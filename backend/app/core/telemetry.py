import logging
import re
import time
from typing import Optional, Any
from app.core.config import settings

logger = logging.getLogger("downfromnet.telemetry")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [TELEMETRY] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)


def sanitize_proxy_url(proxy_url: Optional[str]) -> Optional[str]:
    """
    Masks credentials in proxy URL for safe logging.
    e.g. 'http://user:password@198.23.243.226:6361' -> 'http://***:***@198.23.243.226:6361'
    """
    if not proxy_url:
        return None
    return re.sub(r"://([^:@]+):([^@]+)@", r"://***:***@", proxy_url)


def sanitize_url(url: Optional[str]) -> Optional[str]:
    """
    Removes sensitive query parameters (e.g. tokens, sig, lsig, sapisid) from URLs before logging.
    """
    if not url:
        return None
    # Remove query string if it contains signature/token keys
    if any(k in url.lower() for k in ["sig=", "token=", "session=", "auth="]):
        return url.split("?")[0] + "?[REDACTED_PARAMS]"
    return url


class ExtractionTimer:
    """Context timer to measure duration in milliseconds."""
    def __init__(self):
        self.start_time = 0.0
        self.duration_ms = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = round((time.perf_counter() - self.start_time) * 1000, 2)


def log_extraction_event(
    platform: str,
    video_id: Optional[str],
    extractor: str,
    action: str,  # 'analyze' or 'download'
    duration_ms: float,
    result: str,  # 'success' or 'failed'
    proxy_used: Optional[str] = None,
    format_requested: Optional[str] = None,
    file_size_bytes: Optional[int] = None,
    failure_category: Optional[str] = None,
    error_message: Optional[str] = None,
    extra: Optional[dict[str, Any]] = None
):
    """
    Emits structured telemetry without logging sensitive tokens, passwords, or cookies.
    """
    event_data = {
        "platform": platform,
        "video_id": video_id or "unknown",
        "extractor": extractor,
        "action": action,
        "duration_ms": duration_ms,
        "result": result,
        "proxy": sanitize_proxy_url(proxy_used) if proxy_used else "direct",
    }

    if format_requested:
        event_data["format"] = format_requested
    if file_size_bytes is not None:
        event_data["file_size_bytes"] = file_size_bytes
    if failure_category:
        event_data["failure_category"] = failure_category
    if error_message:
        event_data["error"] = error_message[:120]
    if extra:
        event_data.update(extra)

    log_line = " ".join(f"{k}={v}" for k, v in event_data.items())
    if result == "success":
        logger.info(log_line)
    else:
        logger.warning(log_line)
