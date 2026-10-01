import asyncio
import os
import urllib.parse
from typing import Optional
import httpx
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from app.core.config import settings
from app.core.cookies import get_cookie_file_path
from app.core.proxy import proxy_manager
from app.core.rate_limit import rate_limiter
from app.core.security import sanitize_filename
from app.core.errors import JobNotFoundError, ProcessingError
from app.schemas.download import (
    DownloadRequest,
    BatchDownloadRequest,
    DownloadJobStatus,
)
from app.services.downloader import download_manager
from app.services.analyzer import analyzer_service

router = APIRouter(tags=["Download"])


@router.get("/download/stream")
async def stream_download(
    request: Request,
    url: str,
    format_id: Optional[str] = "best",
    custom_filename: Optional[str] = None,
    target_format: Optional[str] = None,
    direct_url: Optional[str] = None
):
    """
    Streams media chunks directly into the browser's HTTP response.
    Triggers immediate, native browser download without server-side intermediate storage.
    """
    rate_limiter.check_limit(request, endpoint_type="download")

    safe_name = sanitize_filename(custom_filename or "media_download")
    ext = target_format or "mp4"

    is_platform_url = any(d in url.lower() for d in [
        "youtube", "youtu.be", "vimeo", "reddit", "twitter", "x.com", "tiktok", "instagram",
        "facebook", "fb.watch", "dailymotion", "soundcloud", "twitch", "pinterest", "bilibili"
    ])

    if direct_url and not is_platform_url:
        active_proxy = proxy_manager.get_proxy()
        client = httpx.AsyncClient(
            proxy=active_proxy,
            timeout=settings.MAX_DOWNLOAD_DURATION_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": settings.USER_AGENT}
        )
        try:
            req = client.build_request("GET", direct_url)
            resp = await client.send(req, stream=True)
            if resp.status_code >= 400:
                await resp.aclose()
                await client.aclose()
                raise HTTPException(status_code=resp.status_code, detail="Remote media source unavailable.")

            content_length = resp.headers.get("content-length")
            content_type = resp.headers.get("content-type") or "application/octet-stream"

            async def direct_stream_generator():
                try:
                    async for chunk in resp.aiter_bytes(chunk_size=65536):
                        yield chunk
                finally:
                    await resp.aclose()
                    await client.aclose()

            headers = {
                "Content-Disposition": f'attachment; filename="{safe_name}.{ext}"',
                "Accept-Ranges": "bytes",
            }
            if content_length:
                headers["Content-Length"] = content_length

            return StreamingResponse(
                direct_stream_generator(),
                media_type=content_type,
                headers=headers
            )
        except HTTPException:
            raise
        except Exception as e:
            await client.aclose()
            raise HTTPException(status_code=500, detail=str(e))

    # For YouTube and social platforms: stream live bytes via yt-dlp stdout pipe
    cookie_file = get_cookie_file_path()
    cmd = [
        "yt-dlp",
        "-o", "-",
        "--no-playlist",
        "--quiet",
        "--no-warnings",
        "--user-agent", settings.USER_AGENT
    ]

    if format_id and format_id not in ["best", "direct"]:
        cmd.extend(["-f", f"{format_id}+bestaudio/bestvideo+{format_id}/{format_id}/best"])
    else:
        cmd.extend(["-f", "bestvideo+bestaudio/best/b"])

    if target_format and target_format in ["mp3", "m4a", "wav"]:
        cmd.extend(["-x", "--audio-format", target_format])
        ext = target_format
    else:
        cmd.extend(["--merge-output-format", "mp4"])
        ext = "mp4"

    if cookie_file:
        cmd.extend(["--cookies", str(cookie_file)])

    cmd.append(url)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start stream: {str(e)}")

    async def proc_stream_generator():
        try:
            while True:
                chunk = await proc.stdout.read(65536)
                if not chunk:
                    break
                yield chunk
            await proc.wait()
        except asyncio.CancelledError:
            try:
                proc.kill()
            except Exception:
                pass
            raise
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    headers = {
        "Content-Disposition": f'attachment; filename="{safe_name}.{ext}"',
        "Accept-Ranges": "bytes",
    }

    return StreamingResponse(
        proc_stream_generator(),
        media_type="video/mp4" if ext == "mp4" else "application/octet-stream",
        headers=headers
    )


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
