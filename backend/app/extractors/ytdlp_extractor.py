import asyncio
from typing import Any, Optional
import yt_dlp
from app.core.config import settings
from app.core.errors import MediaNotFoundError, MediaAccessDeniedError
from app.core.proxy import proxy_manager
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
    Extractor powered by yt-dlp for video platforms and social media.
    """
    name = "ytdlp"

    async def can_handle(self, url: str) -> bool:
        domain = extract_domain(url).lower()
        if any(d in domain for d in SUPPORTED_DOMAINS):
            return True
        return False

    def _get_cookie_file(self) -> Optional[str]:
        if settings.COOKIES_FILE_PATH and Path(settings.COOKIES_FILE_PATH).exists():
            return settings.COOKIES_FILE_PATH
        if settings.COOKIES_TXT_CONTENT and settings.COOKIES_TXT_CONTENT.strip():
            cookie_file = settings.TEMP_STORAGE_DIR / "cookies.txt"
            cookie_file.write_text(settings.COOKIES_TXT_CONTENT.strip(), encoding="utf-8")
            return str(cookie_file)
        return None

    def _sync_extract_info(self, url: str) -> dict[str, Any]:
        cookie_file = self._get_cookie_file()

        # Primary configuration
        ydl_opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
            "user_agent": settings.USER_AGENT,
            "socket_timeout": 12,
            "ignoreerrors": False,
            "no_color": True,
            "format": "bestvideo+bestaudio/best/bv*+ba/b",
            "js_runtimes": {"node": {}},
        }

        if cookie_file:
            ydl_opts["cookiefile"] = cookie_file
        else:
            # If no cookies, try mobile client rotation
            ydl_opts["extractor_args"] = {
                "youtube": {
                    "player_client": ["android", "ios", "web"],
                }
            }

        active_proxy = proxy_manager.get_proxy()
        if active_proxy:
            ydl_opts["proxy"] = active_proxy

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    return info
        except Exception as primary_err:
            # Fallback configuration with lenient format selector
            fallback_opts: dict[str, Any] = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "extract_flat": False,
                "socket_timeout": 12,
                "ignoreerrors": True,
                "no_color": True,
                "format": "best",
                "js_runtimes": {"node": {}},
            }
            if cookie_file:
                fallback_opts["cookiefile"] = cookie_file
            
            # Try a fresh proxy on fallback if available
            fb_proxy = proxy_manager.get_proxy() or active_proxy
            if fb_proxy:
                fallback_opts["proxy"] = fb_proxy

            with yt_dlp.YoutubeDL(fallback_opts) as ydl_fb:
                info = ydl_fb.extract_info(url, download=False)
                if info:
                    return info
            raise primary_err

        return {}

    async def extract(self, url: str) -> MediaAnalysisResponse:
        domain = extract_domain(url)
        loop = asyncio.get_running_loop()

        try:
            info = await loop.run_in_executor(None, self._sync_extract_info, url)
        except yt_dlp.utils.DownloadError as e:
            err_msg = str(e)
            err_lower = err_msg.lower()
            if any(k in err_lower for k in ["private", "login", "authenticate", "forbidden", "403", "bot", "sign in"]):
                raise MediaAccessDeniedError(f"Platform restricted access: {err_msg.split('ERROR:')[-1].strip()}")
            raise MediaNotFoundError(f"Could not extract media metadata: {err_msg.split('ERROR:')[-1].strip()}")
        except Exception as e:
            raise MediaNotFoundError(f"Media extraction failed: {str(e)}")

        if not info:
            raise MediaNotFoundError("No metadata could be parsed from the provided URL.")

        # Check if playlist or single entry
        entries = info.get("entries")
        if entries and isinstance(entries, list) and len(entries) > 0:
            # Multi-item playlist/album
            items: list[MediaItem] = []
            for idx, entry in enumerate(entries[:20]):  # Limit to 20 entries for response sanity
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

            return MediaAnalysisResponse(
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

        # Single entry video/audio
        formats = self._parse_formats(info)
        title = clean_title(info.get("title"), "Media Video")
        duration = info.get("duration")
        thumbnail = info.get("thumbnail")
        media_type = "video" if (info.get("vcodec") != "none" or formats and any(f.has_video for f in formats)) else "audio"

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

        return MediaAnalysisResponse(
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

    def _parse_formats(self, info: dict[str, Any]) -> list[MediaFormat]:
        raw_formats = info.get("formats", [])
        if not raw_formats:
            # Fallback if only single url is provided
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

        # Filter out storyboard / mhtml formats
        valid_formats = [
            f for f in raw_formats
            if f.get("ext") not in ["mhtml", "storyboard"] and not f.get("format_note") == "storyboard"
        ]

        # 1. Best Combined / High Quality Video Formats
        # Sort video formats by height descending
        video_formats = [
            f for f in valid_formats
            if f.get("vcodec") != "none"
        ]
        video_formats.sort(key=lambda x: (x.get("height") or 0, x.get("tbr") or 0), reverse=True)

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
            res_str = f"{f.get('width', '')}x{height}".strip("x") if f.get('width') else f"{height}p"

            # Do not set download_url to m3u8/manifest URLs for platform streams
            raw_url = f.get("url", "")
            is_manifest = ".m3u8" in raw_url or ".mpd" in raw_url or "manifest" in raw_url or f.get("protocol") in ["m3u8", "m3u8_native", "http_dash_segments"]
            download_url = None if is_manifest else raw_url

            parsed.append(
                MediaFormat(
                    format_id=str(f.get("format_id", f"vid_{height}")),
                    format=ext,
                    quality=f"{height}p" if height else "Standard",
                    resolution=res_str,
                    filesize_bytes=size,
                    filesize=format_bytes(size),
                    has_video=True,
                    has_audio=f.get("acodec") != "none",
                    download_url=download_url
                )
            )

        # 2. Audio-only formats (MP3 / M4A)
        audio_formats = [
            f for f in valid_formats
            if f.get("vcodec") == "none" and f.get("acodec") != "none"
        ]
        audio_formats.sort(key=lambda x: (x.get("abr") or 0, x.get("tbr") or 0), reverse=True)

        for f in audio_formats[:3]:  # Top 3 audio options
            abr = int(f.get("abr") or 128)
            ext = f.get("ext", "m4a")
            quality_key = f"audio_{abr}k_{ext}"
            if quality_key in seen_qualities:
                continue
            seen_qualities.add(quality_key)

            size = f.get("filesize") or f.get("filesize_approx")
            raw_url = f.get("url", "")
            is_manifest = ".m3u8" in raw_url or ".mpd" in raw_url or "manifest" in raw_url or f.get("protocol") in ["m3u8", "m3u8_native", "http_dash_segments"]
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
                    note="Audio only stream"
                )
            )

        # 3. If no formats parsed, add a default 'best' option
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
