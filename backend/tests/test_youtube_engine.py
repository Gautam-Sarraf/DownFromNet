import pytest
import time
from app.core.cache import MetadataCache
from app.core.proxy import HealthAwareProxyManager
from app.core.telemetry import sanitize_proxy_url, sanitize_url, ExtractionTimer
from app.core.youtube_config import YouTubeExtractorConfig
from app.core.youtube_errors import classify_youtube_error, YouTubeErrorCode
from app.schemas.media import MediaAnalysisResponse


def test_youtube_error_classification():
    # Unavailable
    code, msg, status, retry = classify_youtube_error(Exception("ERROR: [youtube] dQw4w9WgXcQ: This video is unavailable"))
    assert code == YouTubeErrorCode.VIDEO_UNAVAILABLE
    assert status == 404
    assert retry is False

    # Private
    code, msg, status, retry = classify_youtube_error(Exception("ERROR: [youtube] dQw4w9WgXcQ: Private video"))
    assert code == YouTubeErrorCode.PRIVATE_VIDEO
    assert status == 403
    assert retry is False

    # Bot check
    code, msg, status, retry = classify_youtube_error(Exception("ERROR: [youtube] Sign in to confirm you're not a bot"))
    assert code == YouTubeErrorCode.AUTH_REQUIRED
    assert retry is True

    # Rate limit
    code, msg, status, retry = classify_youtube_error(Exception("HTTP Error 429: Too Many Requests"))
    assert code == YouTubeErrorCode.RATE_LIMITED
    assert retry is True

    # Network timeout
    code, msg, status, retry = classify_youtube_error(Exception("Connection timed out"))
    assert code == YouTubeErrorCode.TEMPORARY_NETWORK_ERROR
    assert retry is True


def test_youtube_extractor_config_format_selectors():
    # Audio MP3
    selector, merge = YouTubeExtractorConfig.build_format_selector(target_format="mp3")
    assert selector == "bestaudio/best"
    assert merge == "mp3"

    # Specific video quality (1080p stream 137)
    selector, merge = YouTubeExtractorConfig.build_format_selector(format_id="137", target_format="mp4")
    assert "137+bestaudio" in selector
    assert merge == "mp4"

    # Default video
    selector, merge = YouTubeExtractorConfig.build_format_selector()
    assert "bestvideo+bestaudio" in selector
    assert merge == "mp4"


def test_metadata_cache():
    cache = MetadataCache(ttl_seconds=1)
    dummy_resp = MediaAnalysisResponse(
        success=True,
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        source="youtube",
        extractor_name="ytdlp",
        title="Test Title",
        media_type="video",
        is_multi=False,
        items_count=1,
        items=[],
        formats=[]
    )

    cache.set("https://youtu.be/dQw4w9WgXcQ", dummy_resp)
    # Normalized key lookup
    assert cache.get("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is not None

    # Wait for TTL expiry
    time.sleep(1.1)
    assert cache.get("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is None


from app.core.proxy import HealthAwareProxyManager, ProxyHealthRecord

def test_health_aware_proxy_manager():
    mgr = HealthAwareProxyManager()
    mgr._proxies.clear()
    proxy_url = "http://user:pass@1.2.3.4:8080"
    mgr._proxies[proxy_url] = ProxyHealthRecord(proxy_url)

    mgr.report_success(proxy_url, latency_ms=120.0)
    record = mgr._proxies[proxy_url]
    assert record.success_count == 1
    assert record.is_healthy is True

    # Test non-proxy failure does not penalize proxy
    mgr.report_failure(proxy_url, Exception("This video is unavailable"))
    assert record.failure_count == 0

    # Test network failure penalizes proxy
    mgr.report_failure(proxy_url, Exception("Connection timed out"))
    assert record.failure_count == 1


def test_telemetry_sanitization():
    masked = sanitize_proxy_url("http://myuser:supersecretpassword@192.168.1.5:8080")
    assert "supersecretpassword" not in masked
    assert "myuser" not in masked
    assert "192.168.1.5:8080" in masked

    sanitized_url = sanitize_url("https://example.com/video?sig=secret123&token=abc")
    assert "secret123" not in sanitized_url
