import enum
from typing import Optional
from app.core.errors import AppError


class YouTubeErrorCode(str, enum.Enum):
    VIDEO_UNAVAILABLE = "VIDEO_UNAVAILABLE"
    PRIVATE_VIDEO = "PRIVATE_VIDEO"
    REGION_RESTRICTED = "REGION_RESTRICTED"
    AGE_RESTRICTED = "AGE_RESTRICTED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    TEMPORARY_NETWORK_ERROR = "TEMPORARY_NETWORK_ERROR"
    FORMAT_UNAVAILABLE = "FORMAT_UNAVAILABLE"
    EXTRACTION_ERROR = "EXTRACTION_ERROR"
    DOWNLOAD_ERROR = "DOWNLOAD_ERROR"
    FFMPEG_ERROR = "FFMPEG_ERROR"
    UNKNOWN = "UNKNOWN"


class YouTubeExtractionError(AppError):
    """Normalized application error for YouTube extraction and download failures."""
    def __init__(
        self,
        code: YouTubeErrorCode,
        message: str,
        status_code: int = 400,
        is_retryable: bool = False,
        details: Optional[dict] = None
    ):
        super().__init__(message=message, status_code=status_code, details=details or {})
        self.code = code
        self.is_retryable = is_retryable


def classify_youtube_error(exc: Exception) -> tuple[YouTubeErrorCode, str, int, bool]:
    """
    Classifies raw exceptions from yt-dlp or network requests into structured application errors.
    Returns: (YouTubeErrorCode, user_friendly_message, status_code, is_retryable)
    """
    err_str = str(exc)
    err_lower = err_str.lower()

    if any(k in err_lower for k in [
        "this video is unavailable",
        "video unavailable",
        "has been removed by the uploader",
        "deleted video",
        "video has been removed",
        "is not a valid video",
        "does not exist"
    ]):
        return (
            YouTubeErrorCode.VIDEO_UNAVAILABLE,
            "This video is unavailable or has been removed from YouTube.",
            404,
            False
        )

    if any(k in err_lower for k in ["private video", "this video is private"]):
        return (
            YouTubeErrorCode.PRIVATE_VIDEO,
            "This video is private and cannot be accessed.",
            403,
            False
        )

    if any(k in err_lower for k in [
        "not made this video available in your country",
        "blocked in your country",
        "georestricted",
        "not available in your region"
    ]):
        return (
            YouTubeErrorCode.REGION_RESTRICTED,
            "This video is restricted in the current server region.",
            403,
            True  # Retryable with a proxy in another country
        )

    if any(k in err_lower for k in ["age-restricted", "sign in to confirm your age"]):
        return (
            YouTubeErrorCode.AGE_RESTRICTED,
            "This video is age-restricted on YouTube and requires authentication.",
            403,
            False
        )

    if any(k in err_lower for k in [
        "sign in to confirm you’re not a bot",
        "sign in to confirm you're not a bot",
        "bot verification",
        "use --cookies",
        "proof of origin"
    ]):
        return (
            YouTubeErrorCode.AUTH_REQUIRED,
            "YouTube requested bot verification for this request. Retrying through alternate routing.",
            403,
            True  # Retryable with clean proxy or cookies
        )

    if any(k in err_lower for k in ["too many requests", "http error 429", "rate limit"]):
        return (
            YouTubeErrorCode.RATE_LIMITED,
            "YouTube rate limit reached. Retrying through secondary proxy.",
            429,
            True
        )

    if any(k in err_lower for k in [
        "timed out",
        "timeout",
        "connection reset",
        "connection refused",
        "unable to connect",
        "network is unreachable",
        "proxy error",
        "502 bad gateway",
        "503 service unavailable",
        "504 gateway timeout"
    ]):
        return (
            YouTubeErrorCode.TEMPORARY_NETWORK_ERROR,
            "Temporary network connection error while communicating with YouTube.",
            503,
            True
        )

    if any(k in err_lower for k in [
        "requested format is not available",
        "no video formats found",
        "format not found"
    ]):
        return (
            YouTubeErrorCode.FORMAT_UNAVAILABLE,
            "The requested video quality or format is not available for this video.",
            404,
            True  # Retryable with fallback format
        )

    if "ffmpeg" in err_lower:
        return (
            YouTubeErrorCode.FFMPEG_ERROR,
            "Media transcoding or remuxing encountered an error.",
            500,
            False
        )

    # General extraction error fallback
    clean_msg = err_str.split("ERROR:")[-1].strip() if "ERROR:" in err_str else "Unable to parse video stream."
    # Scrub any accidental tokens/paths
    if len(clean_msg) > 150:
        clean_msg = clean_msg[:150] + "..."

    return (
        YouTubeErrorCode.EXTRACTION_ERROR,
        f"Media extraction error: {clean_msg}",
        400,
        False
    )
