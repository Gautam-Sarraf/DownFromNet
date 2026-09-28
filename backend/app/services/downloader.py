import asyncio
from datetime import datetime, timedelta
import os
from pathlib import Path
import re
from typing import Optional, Any
import uuid
import aiofiles
import httpx
import yt_dlp
from app.core.config import settings
from app.core.errors import (
    FileSizeLimitExceededError,
    ProcessingError,
    JobNotFoundError,
    MediaNotFoundError
)
from app.core.security import sanitize_filename, validate_url_security
from app.schemas.download import DownloadJobStatus, DownloadStatus
from app.services.converter import media_converter
from app.services.archiver import media_archiver
from app.utils.mime import format_bytes, guess_extension
from app.utils.text import clean_title


class DownloadJob:
    def __init__(self, job_id: str, original_url: str, custom_name: Optional[str] = None):
        self.job_id = job_id
        self.original_url = original_url
        self.custom_name = custom_name
        self.status: DownloadStatus = "pending"
        self.progress: float = 0.0
        self.message: str = "Download queued"
        self.filename: Optional[str] = None
        self.file_path: Optional[Path] = None
        self.filesize_bytes: Optional[int] = None
        self.filesize_formatted: Optional[str] = None
        self.error: Optional[str] = None
        self.created_at: datetime = datetime.utcnow()
        self.expires_at: Optional[datetime] = datetime.utcnow() + timedelta(minutes=settings.FILE_RETENTION_MINUTES)
        self.is_archive: bool = False
        self.task: Optional[asyncio.Task] = None

    def to_schema(self) -> DownloadJobStatus:
        download_url = f"{settings.API_PREFIX}/download/file/{self.job_id}" if self.status == "completed" else None
        return DownloadJobStatus(
            job_id=self.job_id,
            status=self.status,
            progress=round(self.progress, 1),
            message=self.message,
            filename=self.filename,
            filesize_bytes=self.filesize_bytes,
            filesize_formatted=self.filesize_formatted,
            download_url=download_url,
            error=self.error,
            created_at=self.created_at,
            expires_at=self.expires_at,
            is_archive=self.is_archive
        )


class DownloadManager:
    def __init__(self):
        self.jobs: dict[str, DownloadJob] = {}
        self._lock = asyncio.Lock()

    def get_job(self, job_id: str) -> DownloadJob:
        job = self.jobs.get(job_id)
        if not job:
            raise JobNotFoundError()
        return job

    def get_all_jobs(self) -> list[DownloadJobStatus]:
        return [job.to_schema() for job in self.jobs.values()]

    async def cancel_job(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if not job:
            return False
        if job.task and not job.task.done():
            job.task.cancel()
        job.status = "cancelled"
        job.message = "Download cancelled by user"
        if job.file_path and job.file_path.exists():
            try:
                job.file_path.unlink()
            except Exception:
                pass
        return True

    def create_job(self, url: str, custom_name: Optional[str] = None) -> DownloadJob:
        job_id = str(uuid.uuid4()).replace("-", "")[:12]
        job = DownloadJob(job_id=job_id, original_url=url, custom_name=custom_name)
        self.jobs[job_id] = job
        return job

    async def start_direct_download(
        self,
        job_id: str,
        direct_url: str,
        target_format: Optional[str] = None,
        custom_name: Optional[str] = None
    ):
        job = self.get_job(job_id)
        job.task = asyncio.current_task()

        try:
            job.status = "downloading"
            job.message = "Connecting to source stream..."
            job.progress = 5.0

            safe_name = sanitize_filename(custom_name or "download")
            temp_filename = f"{job_id}_{safe_name}.tmp"
            temp_path = settings.TEMP_STORAGE_DIR / temp_filename

            async with httpx.AsyncClient(
                timeout=settings.MAX_DOWNLOAD_DURATION_SECONDS,
                follow_redirects=True,
                headers={"User-Agent": settings.USER_AGENT}
            ) as client:
                async with client.stream("GET", direct_url) as response:
                    if response.status_code >= 400:
                        raise ProcessingError(f"Source server returned HTTP status {response.status_code}.")

                    content_length = response.headers.get("content-length")
                    total_bytes = int(content_length) if content_length and content_length.isdigit() else None

                    if total_bytes and total_bytes > settings.MAX_FILE_SIZE_BYTES:
                        raise FileSizeLimitExceededError()

                    content_type = response.headers.get("content-type")
                    guessed_ext = guess_extension(content_type, "bin")

                    downloaded_bytes = 0
                    async with aiofiles.open(temp_path, "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=65536):
                            await f.write(chunk)
                            downloaded_bytes += len(chunk)
                            if downloaded_bytes > settings.MAX_FILE_SIZE_BYTES:
                                raise FileSizeLimitExceededError()
                            if total_bytes and total_bytes > 0:
                                job.progress = min(90.0, (downloaded_bytes / total_bytes) * 90.0)
                                job.message = f"Downloading: {format_bytes(downloaded_bytes)} / {format_bytes(total_bytes)}"

            # Download finished, check if format conversion is needed
            current_ext = guessed_ext
            if target_format and target_format.lower() != current_ext:
                job.status = "processing"
                job.message = f"Converting to {target_format.upper()}..."
                job.progress = 92.0
                converted_path = settings.TEMP_STORAGE_DIR / f"{job_id}_{safe_name}.{target_format.lower()}"
                final_path = await media_converter.convert(temp_path, target_format, converted_path)
                if temp_path.exists() and temp_path != final_path:
                    temp_path.unlink()
                final_ext = target_format.lower()
            else:
                final_path = settings.TEMP_STORAGE_DIR / f"{job_id}_{safe_name}.{current_ext}"
                temp_path.rename(final_path)
                final_ext = current_ext

            final_size = final_path.stat().st_size
            job.status = "completed"
            job.progress = 100.0
            job.message = "Ready for download"
            job.file_path = final_path
            job.filename = f"{safe_name}.{final_ext}"
            job.filesize_bytes = final_size
            job.filesize_formatted = format_bytes(final_size)

        except asyncio.CancelledError:
            job.status = "cancelled"
            job.message = "Download cancelled"
            if temp_path.exists():
                temp_path.unlink()
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.message = f"Download failed: {str(e)}"
            if 'temp_path' in locals() and temp_path.exists():
                temp_path.unlink()

    async def start_ytdlp_download(
        self,
        job_id: str,
        url: str,
        format_id: Optional[str] = None,
        target_format: Optional[str] = None,
        custom_name: Optional[str] = None
    ):
        job = self.get_job(job_id)
        job.task = asyncio.current_task()
        loop = asyncio.get_running_loop()

        try:
            job.status = "downloading"
            job.message = "Initializing extractor..."
            job.progress = 5.0

            safe_name = sanitize_filename(custom_name or "media")
            out_template = str(settings.TEMP_STORAGE_DIR / f"{job_id}_{safe_name}.%(ext)s")

            def progress_hook(d):
                if d["status"] == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate")
                    downloaded = d.get("downloaded_bytes", 0)
                    if total and total > 0:
                        percent = (downloaded / total) * 85.0
                        job.progress = min(85.0, percent + 5.0)
                        job.message = f"Downloading: {format_bytes(downloaded)} / {format_bytes(total)}"
                    else:
                        job.progress = min(80.0, job.progress + 2.0)
                        job.message = f"Downloaded {format_bytes(downloaded)}"
                elif d["status"] == "finished":
                    job.status = "processing"
                    job.message = "Processing media stream..."
                    job.progress = 90.0

            # Determine ytdlp format selector & merge format
            postprocessors = []
            merge_format = "mp4"

            if target_format in ["mp3", "m4a", "wav"]:
                fmt_selector = "bestaudio/best"
                postprocessors.append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": target_format,
                    "preferredquality": "192",
                })
            elif format_id and format_id not in ["best", "direct"]:
                # If specific video stream chosen, merge with best audio
                fmt_selector = f"{format_id}+bestaudio/bestvideo+bestaudio/{format_id}/best"
                if target_format in ["mp4", "webm", "mkv"]:
                    merge_format = target_format
            else:
                fmt_selector = "bestvideo+bestaudio/best"
                if target_format in ["mp4", "webm", "mkv"]:
                    merge_format = target_format

            ydl_opts = {
                "format": fmt_selector,
                "outtmpl": out_template,
                "merge_output_format": merge_format,
                "noplaylist": True,
                "progress_hooks": [progress_hook],
                "quiet": True,
                "no_warnings": True,
                "user_agent": settings.USER_AGENT,
                "max_filesize": settings.MAX_FILE_SIZE_BYTES,
                "postprocessors": postprocessors,
            }

            def _sync_download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return info

            info = await loop.run_in_executor(None, _sync_download)

            # Find the generated file in TEMP_STORAGE_DIR
            matching_files = list(settings.TEMP_STORAGE_DIR.glob(f"{job_id}_{safe_name}.*"))
            if not matching_files:
                # Try generic match with job_id
                matching_files = [f for f in settings.TEMP_STORAGE_DIR.glob(f"{job_id}_*") if not f.name.endswith(".tmp")]

            if not matching_files:
                raise ProcessingError("Downloaded file could not be located on disk.")

            final_path = matching_files[0]
            final_size = final_path.stat().st_size
            title = clean_title(info.get("title"), safe_name) if info else safe_name
            ext = final_path.suffix.lstrip(".")

            job.status = "completed"
            job.progress = 100.0
            job.message = "Ready for download"
            job.file_path = final_path
            job.filename = f"{sanitize_filename(title)}.{ext}"
            job.filesize_bytes = final_size
            job.filesize_formatted = format_bytes(final_size)

        except asyncio.CancelledError:
            job.status = "cancelled"
            job.message = "Download cancelled"
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.message = f"Download failed: {str(e)}"

    async def start_batch_download(
        self,
        job_id: str,
        items: list[dict[str, Any]],  # list of {"url": "...", "title": "...", "format": "..."}
        archive_name: str = "media_bundle"
    ):
        job = self.get_job(job_id)
        job.task = asyncio.current_task()
        job.is_archive = True

        try:
            job.status = "downloading"
            job.message = f"Downloading {len(items)} items..."
            job.progress = 5.0

            downloaded_files: list[tuple[Path, str]] = []
            total = len(items)

            async with httpx.AsyncClient(
                timeout=settings.REQUEST_TIMEOUT_SECONDS,
                follow_redirects=True,
                headers={"User-Agent": settings.USER_AGENT}
            ) as client:
                for idx, itm in enumerate(items):
                    item_url = itm.get("url")
                    if not item_url:
                        continue

                    title = itm.get("title") or f"file_{idx+1}"
                    ext = itm.get("format") or "bin"
                    filename = f"{sanitize_filename(title)}.{ext}"
                    temp_file = settings.TEMP_STORAGE_DIR / f"{job_id}_sub_{idx}.{ext}"

                    try:
                        resp = await client.get(item_url)
                        if resp.status_code == 200:
                            async with aiofiles.open(temp_file, "wb") as f:
                                await f.write(resp.content)
                            downloaded_files.append((temp_file, filename))
                    except Exception:
                        pass

                    job.progress = 5.0 + (((idx + 1) / total) * 75.0)
                    job.message = f"Fetched {idx+1}/{total} items..."

            if not downloaded_files:
                raise ProcessingError("Could not retrieve any of the selected files.")

            # Create ZIP archive
            job.status = "processing"
            job.message = "Creating ZIP archive..."
            job.progress = 85.0

            zip_filename = f"{sanitize_filename(archive_name)}.zip"
            zip_path = settings.TEMP_STORAGE_DIR / f"{job_id}_{zip_filename}"

            def update_zip_progress(p):
                job.progress = 85.0 + (p * 0.14)

            await media_archiver.create_zip_archive(downloaded_files, zip_path, update_zip_progress)

            # Cleanup sub temp files
            for fpath, _ in downloaded_files:
                if fpath.exists():
                    fpath.unlink()

            final_size = zip_path.stat().st_size
            job.status = "completed"
            job.progress = 100.0
            job.message = "Archive ready for download"
            job.file_path = zip_path
            job.filename = zip_filename
            job.filesize_bytes = final_size
            job.filesize_formatted = format_bytes(final_size)

        except asyncio.CancelledError:
            job.status = "cancelled"
            job.message = "Batch download cancelled"
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.message = f"Batch archive failed: {str(e)}"


download_manager = DownloadManager()
