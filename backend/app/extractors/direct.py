import os
from urllib.parse import urlparse, unquote
import httpx
from app.core.config import settings
from app.core.errors import MediaNotFoundError
from app.extractors.base import BaseExtractor
from app.schemas.media import MediaAnalysisResponse, MediaItem, MediaFormat
from app.utils.mime import (
    KNOWN_VIDEO_EXTS,
    KNOWN_AUDIO_EXTS,
    KNOWN_IMAGE_EXTS,
    get_media_type_from_ext,
    get_media_type_from_mime,
    guess_extension,
    format_bytes,
)
from app.utils.text import extract_domain, clean_title


class DirectMediaExtractor(BaseExtractor):
    """
    Handles URLs that point directly to video, audio, or image files.
    """
    name = "direct"

    def _get_url_extension(self, url: str) -> str:
        try:
            path = urlparse(url).path
            filename = os.path.basename(unquote(path))
            if "." in filename:
                return filename.split(".")[-1].lower()
        except Exception:
            pass
        return ""

    async def can_handle(self, url: str) -> bool:
        ext = self._get_url_extension(url)
        all_exts = KNOWN_VIDEO_EXTS | KNOWN_AUDIO_EXTS | KNOWN_IMAGE_EXTS
        if ext in all_exts:
            return True
        return False

    async def extract(self, url: str) -> MediaAnalysisResponse:
        domain = extract_domain(url)
        parsed = urlparse(url)
        raw_filename = os.path.basename(unquote(parsed.path)) or "direct_media"
        ext = self._get_url_extension(url)
        title = raw_filename

        media_type = get_media_type_from_ext(ext)
        content_length = None
        content_type = None

        # Send HEAD request to verify and get file size
        try:
            async with httpx.AsyncClient(
                timeout=settings.REQUEST_TIMEOUT_SECONDS,
                follow_redirects=True,
                headers={"User-Agent": settings.USER_AGENT}
            ) as client:
                resp = await client.head(url)
                if resp.status_code in [200, 206]:
                    content_type = resp.headers.get("content-type")
                    cl = resp.headers.get("content-length")
                    if cl and cl.isdigit():
                        content_length = int(cl)
                    if not media_type or media_type == "other":
                        media_type = get_media_type_from_mime(content_type)
        except Exception:
            pass

        if not ext and content_type:
            ext = guess_extension(content_type, "bin")

        fmt = MediaFormat(
            format_id="direct",
            format=ext or "bin",
            quality="Original",
            resolution="Original",
            filesize_bytes=content_length,
            filesize=format_bytes(content_length),
            has_video=(media_type == "video"),
            has_audio=(media_type in ["video", "audio"]),
            download_url=url,
            note="Direct media stream"
        )

        item = MediaItem(
            id="item_0",
            title=clean_title(title),
            media_type=media_type if media_type in ["video", "audio", "image"] else "other",
            thumbnail=url if media_type == "image" else None,
            source_url=url,
            direct_url=url,
            formats=[fmt],
            original_filename=raw_filename
        )

        return MediaAnalysisResponse(
            success=True,
            url=url,
            source=domain,
            extractor_name=self.name,
            title=item.title,
            thumbnail=item.thumbnail,
            media_type=item.media_type,
            is_multi=False,
            items_count=1,
            items=[item],
            formats=[fmt]
        )
