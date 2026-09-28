import asyncio
import os
import zipfile
from pathlib import Path
from typing import Optional
from app.core.errors import ProcessingError
from app.core.security import sanitize_filename


class MediaArchiver:
    """
    Creates clean and secure ZIP archives for batch downloads.
    """
    async def create_zip_archive(
        self,
        file_paths: list[tuple[Path, str]],  # (absolute_path, zip_internal_name)
        output_zip_path: Path,
        progress_callback: Optional[callable] = None
    ) -> Path:
        loop = asyncio.get_running_loop()

        def _sync_zip():
            with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                total = len(file_paths)
                for idx, (fpath, internal_name) in enumerate(file_paths):
                    if fpath.exists():
                        safe_name = sanitize_filename(internal_name)
                        zipf.write(fpath, arcname=safe_name)
                    if progress_callback:
                        progress = ((idx + 1) / total) * 100
                        progress_callback(progress)

        try:
            await loop.run_in_executor(None, _sync_zip)
            if not output_zip_path.exists() or output_zip_path.stat().st_size == 0:
                raise ProcessingError("Failed to build ZIP archive.")
            return output_zip_path
        except Exception as e:
            raise ProcessingError(f"Archive error: {str(e)}")


media_archiver = MediaArchiver()
