import asyncio
import time
from typing import Any, Optional
import yt_dlp
from app.core.cache import media_cache
from app.core.config import settings
from app.core.cookies import get_cookie_file_path
from app.core.errors import MediaNotFoundError, MediaAccessDeniedError
from app.core.proxy import proxy_manager
from app.core.telemetry import log_extraction_event, ExtractionTimer, sanitize_proxy_url
from app.core.youtube_config import YouTubeExtractorConfig
from app.core.youtube_errors import classify_youtube_error, YouTubeErrorCode, YouTubeExtractionError
from app.extractors.base import BaseExtractor
from app.schemas.media import MediaAnalysisResponse, MediaItem, MediaFormat
from app.utils.mime import format_bytes, format_duration
from app.utils.text import extract_domain, clean_title


SUPPORTED_DOMAINS = {
    "youtube", "youtu", "vimeo", "reddit", "twitter", "x", "tiktok", "instagram",
    "facebook", "fb", "dailymotion", "soundcloud", "twitch", "pinterest", "tumblr",
    "bilibili", "mixcloud", "bandcamp", "streamable", "vk", "threads"
}


class YtDlpExtractor(BaseExtractor):
    """
    Production-grade extractor powered by yt-dlp for video platforms and social media.
    Features:
    - Dedicated YouTubeExtractorConfig layer
    - In-memory TTL metadata caching
    - Health-aware proxy rotation with latency reporting
    - Structured telemetry without credential leaks
    - Normalized application-level error classification
    """
    name = "ytdlp"

    async def can_handle(self, url: str) -> bool:
        domain = extract_domain(url).lower()
        if any(d in domain for d in SUPPORTED_DOMAINS):
            return True
        return False

    def _sync_extract_info(self, url: str) -> tuple[dict[str, Any], Optional[str]]:
        """
        Synchronously extracts media metadata by trying healthy proxies in prioritized order.
        Returns: (metadata_dict, proxy_used)
        """
        is_youtube = "youtube" in url.lower() or "youtu.be" in url.lower()
        proxies_to_try = proxy_manager.get_all_healthy_proxies()
        if not proxies_to_try:
            proxies_to_try = [None]

        last_error: Optional[Exception] = None
        cookie_file = get_cookie_file_path()

        for proxy_candidate in proxies_to_try:
            t0 = time.perf_counter()

            if is_youtube:
                ydl_opts = YouTubeExtractorConfig.build_analyze_opts(
                    proxy=proxy_candidate,
                    cookie_file=cookie_file,
                    timeout=10
                )
            else:
                # Generic platforms (TikTok, Instagram, Twitter, Reddit, Vimeo, etc.)
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "skip_download": True,
                    "extract_flat": False,
                    "user_agent": settings.USER_AGENT,
                    "socket_timeout": 12,
                    "ignoreerrors": False,
                    "no_color": True,
                }
                if cookie_file:
                    ydl_opts["cookiefile"] = cookie_file
                if proxy_candidate:
                    ydl_opts["proxy"] = proxy_candidate

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                        proxy_manager.report_success(proxy_candidate, latency_ms)
                        return info, proxy_candidate
            except Exception as err:
                last_error = err
                proxy_manager.report_failure(proxy_candidate, err)

                # Check if this error is non-retryable (e.g. video unavailable or private)
                code, _, _, is_retryable = classify_youtube_error(err)
                if not is_retryable:
                    raise err

                # If retryable, continue to next healthy proxy
                continue

        if last_error:
            raise last_error
        return {}, None

    async def extract(self, url: str) -> MediaAnalysisResponse:
        domain = extract_domain(url)

        # 1. Check Metadata Cache first
        cached_result = media_cache.get(url)
        if cached_result:
            return cached_result

        loop = asyncio.get_running_loop()
        proxy_used: Optional[str] = None
        video_id: Optional[str] = None

        with ExtractionTimer() as timer:
            try:
                info, proxy_used = await loop.run_in_executor(None, self._sync_extract_info, url)
            except Exception as e:
                code, user_msg, status_code, _ = classify_youtube_error(e)
                log_extraction_event(
                    platform=domain,
                    video_id=video_id,
                    extractor=self.name,
                    action="analyze",
                    duration_ms=timer.duration_ms,
                    result="failed",
                    proxy_used=proxy_used,
                    failure_category=code.value,
                    error_message=user_msg
                )

                if code in [YouTubeErrorCode.PRIVATE_VIDEO, YouTubeErrorCode.AGE_RESTRICTED, YouTubeErrorCode.AUTH_REQUIRED]:
                    raise MediaAccessDeniedError(user_msg)
                elif code in [YouTubeErrorCode.VIDEO_UNAVAILABLE, YouTubeErrorCode.FORMAT_UNAVAILABLE]:
                    raise MediaNotFoundError(user_msg)
                else:
                    raise YouTubeExtractionError(
                        code=code,
                        message=user_msg,
                        status_code=status_code
                    )

        if not info:
            raise MediaNotFoundError("No metadata could be parsed from the provided URL.")

        video_id = info.get("id") or info.get("display_id")

        # 2. Check if playlist or single entry
        entries = info.get("entries")
        if entries and isinstance(entries, list) and len(entries) > 0:
            # Multi-item playlist/album
            items: list[MediaItem] = []
            for idx, entry in enumerate(entries[:20]):
                if not entry:
                    continue
                item_formats = self._parse_formats(entry)
                item = MediaItem(
                    id=f"item_{idx}",
                    title=clean_title(entry.get("title"), f"Media Part {idx+1}"),
                    media_type="video" if entry.get("vcodec") != "none" else "audio",
                    thumbnail=entry.get("thumbnail"),
                    duration=entry.get("duration"),
                    duration_formatted=format_duration(entry.get("duration")),
                    source_url=entry.get("webpage_url") or url,
                    direct_url=entry.get("url"),
                    formats=item_formats,
                    width=entry.get("width"),
                    height=entry.get("height"),
                )
                items.append(item)

            response = MediaAnalysisResponse(
                success=True,
                url=url,
                source=domain,
                extractor_name=self.name,
                title=clean_title(info.get("title"), f"{domain.capitalize()} Playlist"),
                thumbnail=items[0].thumbnail if items else None,
                media_type="video",
                is_multi=len(items) > 1,
                items_count=len(items),
                items=items,
                formats=items[0].formats if items else []
            )
            media_cache.set(url, response)

            log_extraction_event(
                platform=domain,
                video_id=video_id,
                extractor=self.name,
                action="analyze",
                duration_ms=timer.duration_ms,
                result="success",
                proxy_used=proxy_used,
                extra={"items_count": len(items)}
            )
            return response

        # 3. Single entry video/audio
        formats = self._parse_formats(info)
        title = clean_title(info.get("title"), "Media Video")
        duration = info.get("duration")
        thumbnail = info.get("thumbnail")
        media_type = "video" if (info.get("vcodec") != "none" or (formats and any(f.has_video for f in formats))) else "audio"

        item = MediaItem(
            id="item_0",
            title=title,
            media_type=media_type,
            thumbnail=thumbnail,
            duration=duration,
            duration_formatted=format_duration(duration),
            source_url=url,
            direct_url=info.get("url"),
            formats=formats,
            width=info.get("width"),
            height=info.get("height"),
        )

        response = MediaAnalysisResponse(
            success=True,
            url=url,
            source=domain,
            extractor_name=self.name,
            title=title,
            thumbnail=thumbnail,
            duration=duration,
            duration_formatted=format_duration(duration),
            media_type=media_type,
            is_multi=False,
            items_count=1,
            items=[item],
            formats=formats
        )

        # Store in cache
        media_cache.set(url, response)

        log_extraction_event(
            platform=domain,
            video_id=video_id,
            extractor=self.name,
            action="analyze",
            duration_ms=timer.duration_ms,
            result="success",
            proxy_used=proxy_used,
            extra={"formats_count": len(formats)}
        )
        return response

    def _parse_formats(self, info: dict[str, Any]) -> list[MediaFormat]:
        raw_formats = info.get("formats", [])
        if not raw_formats:
            single_url = info.get("url")
            ext = info.get("ext", "mp4")
            return [
                MediaFormat(
                    format_id="best",
                    format=ext,
                    quality="Standard",
                    resolution=f"{info.get('width', '')}x{info.get('height', '')}".strip("x") or None,
                    filesize_bytes=info.get("filesize") or info.get("filesize_approx"),
                    filesize=format_bytes(info.get("filesize") or info.get("filesize_approx")),
                    has_video=info.get("vcodec") != "none",
                    has_audio=info.get("acodec") != "none",
                    download_url=single_url
                )
            ]

        parsed: list[MediaFormat] = []
        seen_qualities = set()

        valid_formats = [
            f for f in raw_formats
            if f.get("ext") not in ["mhtml", "storyboard"] and f.get("format_note") != "storyboard"
        ]

        # 1. Video Formats (Prefer direct HTTPS DASH over rate-limited m3u8 streams)
        def _format_sort_key(f):
            height = f.get("height") or 0
            protocol = f.get("protocol") or ""
            raw_url = f.get("url") or ""
            is_m3u8 = "m3u8" in protocol or ".m3u8" in raw_url or f.get("format_note") == "HLS"
            return (height, not is_m3u8, f.get("tbr") or 0)

        video_formats = [f for f in valid_formats if f.get("vcodec") != "none"]
        video_formats.sort(key=_format_sort_key, reverse=True)

        quality_labels = {
            2160: "2160p (4K)",
            1440: "1440p (2K)",
            1080: "1080p (FHD)",
            720: "720p (HD)",
            480: "480p (SD)",
            360: "360p",
            240: "240p",
            144: "144p"
        }

        for f in video_formats:
            height = f.get("height")
            ext = f.get("ext", "mp4")
            if not height:
                continue

            quality_key = f"{height}p_{ext}"
            if quality_key in seen_qualities:
                continue
            seen_qualities.add(quality_key)

            size = f.get("filesize") or f.get("filesize_approx")
            res_str = f"{f.get('width', '')}x{height}".strip("x") if f.get("width") else f"{height}p"
            quality_name = quality_labels.get(height, f"{height}p")

            # Platform streams requiring server remux/download
            raw_url = f.get("url", "")
            is_manifest = (
                ".m3u8" in raw_url or ".mpd" in raw_url or "manifest" in raw_url
                or f.get("protocol") in ["m3u8", "m3u8_native", "http_dash_segments"]
            )
            download_url = None if is_manifest else raw_url

            parsed.append(
                MediaFormat(
                    format_id=str(f.get("format_id", f"vid_{height}")),
                    format=ext,
                    quality=quality_name,
                    resolution=res_str,
                    filesize_bytes=size,
                    filesize=format_bytes(size),
                    has_video=True,
                    has_audio=f.get("acodec") != "none",
                    download_url=download_url
                )
            )

        # 2. Audio-only Formats (sorted descending by bitrate)
        audio_formats = [f for f in valid_formats if f.get("vcodec") == "none" and f.get("acodec") != "none"]
        audio_formats.sort(key=lambda x: (x.get("abr") or 0, x.get("tbr") or 0), reverse=True)

        for f in audio_formats[:4]:
            abr = int(f.get("abr") or 128)
            ext = f.get("ext", "m4a")
            quality_key = f"audio_{abr}k_{ext}"
            if quality_key in seen_qualities:
                continue
            seen_qualities.add(quality_key)

            size = f.get("filesize") or f.get("filesize_approx")
            raw_url = f.get("url", "")
            is_manifest = (
                ".m3u8" in raw_url or ".mpd" in raw_url or "manifest" in raw_url
                or f.get("protocol") in ["m3u8", "m3u8_native", "http_dash_segments"]
            )
            download_url = None if is_manifest else raw_url

            parsed.append(
                MediaFormat(
                    format_id=str(f.get("format_id", f"audio_{abr}")),
                    format=ext,
                    quality=f"Audio {abr}kbps",
                    resolution="Audio Only",
                    filesize_bytes=size,
                    filesize=format_bytes(size),
                    has_video=False,
                    has_audio=True,
                    download_url=download_url,
                    note="High quality audio stream"
                )
            )

        # 3. Fallback format if none parsed
        if not parsed:
            parsed.append(
                MediaFormat(
                    format_id="best",
                    format="mp4",
                    quality="Best Available",
                    resolution=None,
                    filesize_bytes=None,
                    filesize=None,
                    has_video=True,
                    has_audio=True
                )
            )

        return parsed
