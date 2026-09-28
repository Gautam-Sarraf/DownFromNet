import mimetypes
from typing import Optional


COMMON_EXTENSIONS = {
    # Video
    "video/mp4": "mp4",
    "video/webm": "webm",
    "video/quicktime": "mov",
    "video/x-matroska": "mkv",
    "video/x-msvideo": "avi",
    "video/ogg": "ogv",
    # Audio
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/mp4": "m4a",
    "audio/x-m4a": "m4a",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/ogg": "ogg",
    "audio/flac": "flac",
    "audio/aac": "aac",
    # Image
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/svg+xml": "svg",
    "image/bmp": "bmp",
}

KNOWN_VIDEO_EXTS = {"mp4", "webm", "mkv", "mov", "avi", "flv", "wmv", "m4v", "ogv", "3gp", "ts"}
KNOWN_AUDIO_EXTS = {"mp3", "m4a", "wav", "flac", "aac", "ogg", "wma", "opus"}
KNOWN_IMAGE_EXTS = {"jpg", "jpeg", "png", "webp", "gif", "svg", "bmp", "avif", "ico", "tiff"}


def get_media_type_from_ext(ext: str) -> str:
    ext_clean = ext.lower().lstrip(".")
    if ext_clean in KNOWN_VIDEO_EXTS:
        return "video"
    elif ext_clean in KNOWN_AUDIO_EXTS:
        return "audio"
    elif ext_clean in KNOWN_IMAGE_EXTS:
        return "image"
    return "other"


def get_media_type_from_mime(mime_type: Optional[str]) -> str:
    if not mime_type:
        return "other"
    mime = mime_type.lower().split(";")[0].strip()
    if mime.startswith("video/"):
        return "video"
    if mime.startswith("audio/"):
        return "audio"
    if mime.startswith("image/"):
        return "image"
    return "other"


def guess_extension(mime_type: Optional[str], default: str = "bin") -> str:
    if not mime_type:
        return default
    mime = mime_type.lower().split(";")[0].strip()
    if mime in COMMON_EXTENSIONS:
        return COMMON_EXTENSIONS[mime]
    ext = mimetypes.guess_extension(mime)
    if ext:
        return ext.lstrip(".")
    return default


def format_bytes(size_bytes: Optional[int]) -> Optional[str]:
    if size_bytes is None or size_bytes < 0:
        return None
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_idx = 0
    val = float(size_bytes)
    while val >= 1024.0 and unit_idx < len(units) - 1:
        val /= 1024.0
        unit_idx += 1
    return f"{val:.1f} {units[unit_idx]}"


def format_duration(seconds: Optional[float]) -> Optional[str]:
    if seconds is None or seconds < 0:
        return None
    total_secs = int(seconds)
    hours = total_secs // 3600
    minutes = (total_secs % 3600) // 60
    secs = total_secs % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
