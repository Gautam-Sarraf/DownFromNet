import shutil
from fastapi import APIRouter
from app.core.config import settings
from app.services.converter import media_converter

router = APIRouter(tags=["Health & System"])


@router.get("/health")
async def health_check():
    total, used, free = shutil.disk_usage(settings.TEMP_STORAGE_DIR)
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ffmpeg_available": media_converter.is_available(),
        "storage_free_mb": round(free / (1024 * 1024), 2),
    }


@router.get("/system/info")
async def system_info():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ffmpeg_available": media_converter.is_available(),
        "max_file_size_mb": settings.MAX_FILE_SIZE_BYTES // (1024 * 1024),
        "file_retention_minutes": settings.FILE_RETENTION_MINUTES,
        "supported_video_formats": ["mp4", "webm", "mkv", "mov"],
        "supported_audio_formats": ["mp3", "m4a", "wav"],
        "supported_image_formats": ["jpg", "png", "webp", "gif"],
    }
