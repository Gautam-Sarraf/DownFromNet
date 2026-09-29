import asyncio
from datetime import datetime, timedelta
import os
from pathlib import Path
import re
import time
from typing import Optional, Any
import uuid
import aiofiles
import httpx
import yt_dlp
from app.core.config import settings
from app.core.cookies import get_cookie_file_path
from app.core.errors import (
    FileSizeLimitExceededError,
    ProcessingError,
    JobNotFoundError,
    MediaNotFoundError
)
from app.core.proxy import proxy_manager
from app.core.security import sanitize_filename, validate_url_security
from app.core.telemetry import log_extraction_event, ExtractionTimer, sanitize_proxy_url
from app.core.youtube_config import YouTubeExtractorConfig
from app.core.youtube_errors import classify_youtube_error
from app.schemas.download import DownloadJobStatus, DownloadStatus
from app.services.converter import media_converter
from app.services.archiver import media_archiver
from app.utils.mime import format_bytes, guess_extension
from app.utils.text import clean_title, extract_domain


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
        temp_path: Optional[Path] = None

        try:
            job.status = "downloading"
            job.message = "Connecting to source stream..."
            job.progress = 5.0

            safe_name = sanitize_filename(custom_name or "download")
            temp_filename = f"{job_id}_{safe_name}.tmp"
            temp_path = settings.TEMP_STORAGE_DIR / temp_filename

            active_proxy = proxy_manager.get_proxy()
            async with httpx.AsyncClient(
                proxy=active_proxy,
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
            if temp_path and temp_path.exists():
                temp_path.unlink()
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.message = f"Download failed: {str(e)}"
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

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
        domain = extract_domain(url)
        is_youtube = "youtube" in url.lower() or "youtu.be" in url.lower()
        proxy_used: Optional[str] = None
        video_id: Optional[str] = None

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

            def _sync_download():
                nonlocal proxy_used, video_id
                cookie_file = get_cookie_file_path()
                proxies_to_try = proxy_manager.get_all_healthy_proxies()
                if not proxies_to_try:
                    proxies_to_try = [None]

                last_error = None
                for proxy_candidate in proxies_to_try:
                    t0 = time.perf_counter()
                    proxy_used = proxy_candidate

                    if is_youtube:
                        ydl_opts, _ = YouTubeExtractorConfig.build_download_opts(
                            output_template=out_template,
                            format_id=format_id,
                            target_format=target_format,
                            proxy=proxy_candidate,
                            cookie_file=cookie_file,
                            progress_hook=progress_hook,
                            timeout=30
                        )
                    else:
                        # Non-YouTube platforms (TikTok, Instagram, Twitter, Reddit, etc.)
                        fmt_selector = format_id if format_id and format_id not in ["best", "direct"] else "bestvideo+bestaudio/best"
                        ydl_opts = {
                            "format": fmt_selector,
                            "outtmpl": out_template,
                            "merge_output_format": "mp4",
                            "noplaylist": True,
                            "progress_hooks": [progress_hook],
                            "quiet": True,
                            "no_warnings": True,
                            "user_agent": settings.USER_AGENT,
                            "max_filesize": settings.MAX_FILE_SIZE_BYTES,
                            "socket_timeout": 30,
                        }
                        if cookie_file:
                            ydl_opts["cookiefile"] = cookie_file
                        if proxy_candidate:
                            ydl_opts["proxy"] = proxy_candidate

                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=True)
                            if info:
                                video_id = info.get("id") or info.get("display_id")
                                latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                                proxy_manager.report_success(proxy_candidate, latency_ms)
                                return info
                    except Exception as err:
                        last_error = err
                        proxy_manager.report_failure(proxy_candidate, err)
                        code, _, _, is_retryable = classify_youtube_error(err)
                        if not is_retryable:
                            raise err
                        continue

                if last_error:
                    raise last_error
                raise ProcessingError("Could not initiate download with available endpoints.")

            with ExtractionTimer() as timer:
                info = await loop.run_in_executor(None, _sync_download)

            # Find the generated file in TEMP_STORAGE_DIR
            matching_files = list(settings.TEMP_STORAGE_DIR.glob(f"{job_id}_{safe_name}.*"))
            if not matching_files:
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

            log_extraction_event(
                platform=domain,
                video_id=video_id,
                extractor="ytdlp",
                action="download",
                duration_ms=timer.duration_ms,
                result="success",
                proxy_used=proxy_used,
                format_requested=target_format or format_id,
                file_size_bytes=final_size
            )

        except asyncio.CancelledError:
            job.status = "cancelled"
            job.message = "Download cancelled"
            self._cleanup_partial_files(job_id)
        except Exception as e:
            code, user_msg, _, _ = classify_youtube_error(e)
            job.status = "failed"
            job.error = user_msg
            job.message = f"Download failed: {user_msg}"
            self._cleanup_partial_files(job_id)

            log_extraction_event(
                platform=domain,
                video_id=video_id,
                extractor="ytdlp",
                action="download",
                duration_ms=0.0,
                result="failed",
                proxy_used=proxy_used,
                format_requested=target_format or format_id,
                failure_category=code.value,
                error_message=user_msg
            )

    def _cleanup_partial_files(self, job_id: str):
        """Cleans up any partial or temporary files associated with a job ID."""
        try:
            for p in settings.TEMP_STORAGE_DIR.glob(f"{job_id}_*"):
                if p.exists():
                    p.unlink()
        except Exception:
            pass

    async def start_batch_download(
        self,
        job_id: str,
        items: list[dict[str, Any]],
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
            active_proxy = proxy_manager.get_proxy()

            async with httpx.AsyncClient(
                proxy=active_proxy,
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

            await media_archiver.create_zip(
                files=downloaded_files,
                output_zip_path=zip_path,
                progress_callback=update_zip_progress
            )

            # Cleanup sub files
            for temp_f, _ in downloaded_files:
                if temp_f.exists():
                    try:
                        temp_f.unlink()
                    except Exception:
                        pass

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
            self._cleanup_partial_files(job_id)
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.message = f"Batch archive failed: {str(e)}"
            self._cleanup_partial_files(job_id)


download_manager = DownloadManager()
