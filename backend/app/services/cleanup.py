import asyncio
from datetime import datetime, timedelta
import os
import time
from pathlib import Path
from app.core.config import settings
from app.services.downloader import download_manager


class CleanupService:
    def __init__(self):
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    async def _cleanup_loop(self):
        while self._running:
            try:
                await self.perform_cleanup()
            except Exception:
                pass
            await asyncio.sleep(settings.CLEANUP_INTERVAL_SECONDS)

    async def perform_cleanup(self):
        now = time.time()
        retention_secs = settings.FILE_RETENTION_MINUTES * 60
        storage_dir = settings.TEMP_STORAGE_DIR

        # 1. Clean disk files
        if storage_dir.exists():
            for file_path in storage_dir.iterdir():
                if file_path.is_file():
                    try:
                        mtime = file_path.stat().st_mtime
                        if now - mtime > retention_secs:
                            file_path.unlink()
                    except Exception:
                        pass

        # 2. Clean in-memory jobs older than retention
        cutoff_time = datetime.utcnow() - timedelta(minutes=settings.FILE_RETENTION_MINUTES)
        stale_keys = [
            jid for jid, job in download_manager.jobs.items()
            if job.created_at < cutoff_time and job.status in ["completed", "failed", "cancelled"]
        ]
        for key in stale_keys:
            download_manager.jobs.pop(key, None)


cleanup_service = CleanupService()
