import asyncio
import os
import shutil
from pathlib import Path
from typing import Optional
from app.core.errors import ProcessingError


class MediaConverter:
    """
    Safe FFmpeg media conversion service without shell invocation.
    """
    def __init__(self):
        self.ffmpeg_path = shutil.which("ffmpeg")

    def is_available(self) -> bool:
        return self.ffmpeg_path is not None

    async def convert(
        self,
        input_path: Path,
        target_format: str,
        output_path: Optional[Path] = None,
        progress_callback: Optional[callable] = None
    ) -> Path:
        """
        Converts media file at input_path into target_format (e.g. mp3, mp4, webm, jpg, png).
        """
        if not self.is_available():
            raise ProcessingError("FFmpeg is not installed on the system server.")

        target_ext = target_format.lower().lstrip(".")
        input_ext = input_path.suffix.lower().lstrip(".")

        if input_ext == target_ext and output_path is None:
            return input_path

        if output_path is None:
            output_path = input_path.with_suffix(f".{target_ext}")

        # Build secure FFmpeg arguments list
        cmd = [self.ffmpeg_path, "-y", "-i", str(input_path)]

        # Video to Audio conversion (e.g. to MP3 or M4A)
        if target_ext == "mp3":
            cmd.extend(["-vn", "-acodec", "libmp3lame", "-b:a", "192k"])
        elif target_ext == "m4a":
            cmd.extend(["-vn", "-acodec", "aac", "-b:a", "192k"])
        elif target_ext == "wav":
            cmd.extend(["-vn", "-acodec", "pcm_s16le"])
        # Video conversion
        elif target_ext == "mp4":
            cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart"])
        elif target_ext == "webm":
            cmd.extend(["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", "-c:a", "libopus"])
        # Image conversion
        elif target_ext in ["jpg", "jpeg", "png", "webp"]:
            cmd.extend(["-vframes", "1"])
        else:
            # Default copy or standard conversion
            cmd.extend(["-c", "copy"])

        cmd.append(str(output_path))

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)

            if process.returncode != 0:
                err_text = stderr.decode("utf-8", errors="ignore")
                raise ProcessingError(f"FFmpeg conversion failed: {err_text[-200:]}")

            if not output_path.exists() or output_path.stat().st_size == 0:
                raise ProcessingError("Converted output file is empty.")

            return output_path

        except asyncio.TimeoutError:
            raise ProcessingError("Media conversion timed out.")
        except ProcessingError:
            raise
        except Exception as e:
            raise ProcessingError(f"Conversion error: {str(e)}")


media_converter = MediaConverter()
