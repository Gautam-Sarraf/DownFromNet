import asyncio
import os
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from app.core.rate_limit import rate_limiter
from app.core.errors import JobNotFoundError, ProcessingError
from app.schemas.download import (
    DownloadRequest,
    BatchDownloadRequest,
    DownloadJobStatus,
)
from app.services.downloader import download_manager
from app.services.analyzer import analyzer_service

router = APIRouter(tags=["Download"])


@router.post("/download", response_model=DownloadJobStatus)
async def initiate_download(request: Request, body: DownloadRequest, background_tasks: BackgroundTasks):
    rate_limiter.check_limit(request, endpoint_type="download")

    # Create job
    job = download_manager.create_job(url=body.url, custom_name=body.custom_filename)

    # Determine download strategy
    is_platform_url = any(d in body.url.lower() for d in [
        "youtube", "youtu.be", "vimeo", "reddit", "twitter", "x.com", "tiktok", "instagram",
        "facebook", "fb.watch", "dailymotion", "soundcloud", "twitch", "pinterest", "bilibili"
    ])

    is_manifest = bool(body.direct_url and any(k in body.direct_url.lower() for k in [".m3u8", ".mpd", "manifest", "googlevideo"]))

    if body.direct_url and not is_platform_url and not is_manifest:
        # We already have a direct standalone media file URL (static image/video)
        background_tasks.add_task(
            download_manager.start_direct_download,
            job_id=job.job_id,
            direct_url=body.direct_url,
            target_format=body.target_format,
            custom_name=body.custom_filename
        )
    else:
        # Video platform or complex streaming link -> yt-dlp + FFmpeg
        background_tasks.add_task(
            download_manager.start_ytdlp_download,
            job_id=job.job_id,
            url=body.url,
            format_id=body.format_id,
            target_format=body.target_format,
            custom_name=body.custom_filename
        )

    return job.to_schema()


@router.post("/download/batch", response_model=DownloadJobStatus)
async def initiate_batch_download(request: Request, body: BatchDownloadRequest, background_tasks: BackgroundTasks):
    rate_limiter.check_limit(request, endpoint_type="download")

    # Re-analyze URL to get full items list
    analysis = await analyzer_service.analyze_url(body.url)
    selected_items = []

    for itm in analysis.items:
        if itm.id in body.item_ids:
            dl_url = itm.direct_url or (itm.formats[0].download_url if itm.formats else None)
            if dl_url:
                fmt = body.target_format or (itm.formats[0].format if itm.formats else "jpg")
                selected_items.append({
                    "url": dl_url,
                    "title": itm.title,
                    "format": fmt
                })

    if not selected_items:
        raise HTTPException(status_code=400, detail="None of the selected item IDs could be resolved for download.")

    job = download_manager.create_job(url=body.url, custom_name=body.archive_name)

    background_tasks.add_task(
        download_manager.start_batch_download,
        job_id=job.job_id,
        items=selected_items,
        archive_name=body.archive_name or "media_bundle"
    )

    return job.to_schema()


@router.get("/download/{job_id}/status", response_model=DownloadJobStatus)
async def get_download_status(job_id: str):
    job = download_manager.get_job(job_id)
    return job.to_schema()


@router.get("/download/file/{job_id}")
async def download_file(job_id: str):
    job = download_manager.get_job(job_id)
    if job.status != "completed" or not job.file_path or not job.file_path.exists():
        raise HTTPException(status_code=404, detail="File is not ready or has expired.")

    safe_filename = job.filename or "media_download"
    return FileResponse(
        path=str(job.file_path),
        filename=safe_filename,
        media_type="application/octet-stream"
    )


@router.delete("/download/{job_id}")
async def cancel_download(job_id: str):
    cancelled = await download_manager.cancel_job(job_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {"success": True, "message": "Download task cancelled and purged."}


@router.get("/history", response_model=list[DownloadJobStatus])
async def get_download_history():
    return download_manager.get_all_jobs()
