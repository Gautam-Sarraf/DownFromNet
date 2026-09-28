import json
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import httpx
from app.core.config import settings
from app.core.errors import MediaNotFoundError, MediaAccessDeniedError
from app.extractors.base import BaseExtractor
from app.schemas.media import MediaAnalysisResponse, MediaItem, MediaFormat
from app.utils.mime import (
    get_media_type_from_ext,
    get_media_type_from_mime,
    guess_extension,
    format_bytes,
)
from app.utils.text import extract_domain, clean_title


# Discard common icon / tiny tracking image patterns
IGNORE_IMAGE_PATTERNS = [
    r'icon', r'favicon', r'avatar', r'badge', r'logo_small',
    r'1x1', r'pixel', r'spacer', r'tracker', r'analytics', r'button'
]


class GenericHtmlExtractor(BaseExtractor):
    """
    Generic webpage parser that extracts OpenGraph, Twitter cards, JSON-LD,
    HTML5 video/audio tags, and image galleries from any public website.
    """
    name = "generic_html"

    async def can_handle(self, url: str) -> bool:
        # Fallback extractor that can handle any web URL
        return True

    async def extract(self, url: str) -> MediaAnalysisResponse:
        domain = extract_domain(url)

        try:
            async with httpx.AsyncClient(
                timeout=settings.REQUEST_TIMEOUT_SECONDS,
                follow_redirects=True,
                headers={
                    "User-Agent": settings.USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                }
            ) as client:
                resp = await client.get(url)
                if resp.status_code == 403:
                    raise MediaAccessDeniedError()
                elif resp.status_code >= 400:
                    raise MediaNotFoundError(f"Webpage returned status {resp.status_code}.")
                html_text = resp.text
                final_url = str(resp.url)
        except (MediaAccessDeniedError, MediaNotFoundError):
            raise
        except Exception as e:
            raise MediaNotFoundError(f"Failed to fetch webpage: {str(e)}")

        soup = BeautifulSoup(html_text, "html.parser")

        # 1. Page Title & Meta
        page_title = None
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            page_title = og_title["content"].strip()
        elif soup.title and soup.title.string:
            page_title = soup.title.string.strip()
        page_title = clean_title(page_title, f"{domain.capitalize()} Webpage Media")

        # Primary thumbnail / OpenGraph image
        og_image = soup.find("meta", property="og:image") or soup.find("meta", property="og:image:url")
        tw_image = soup.find("meta", attrs={"name": "twitter:image"}) or soup.find("meta", property="twitter:image")
        hero_thumbnail = None
        if og_image and og_image.get("content"):
            hero_thumbnail = urljoin(final_url, og_image["content"].strip())
        elif tw_image and tw_image.get("content"):
            hero_thumbnail = urljoin(final_url, tw_image["content"].strip())

        detected_items: list[MediaItem] = []
        seen_media_urls = set()

        # Helper to register an item
        def add_item(media_url: str, m_type: str, item_title: str, thumb: str = None, width: int = None, height: int = None):
            abs_url = urljoin(final_url, media_url.strip())
            if not abs_url.startswith("http://") and not abs_url.startswith("https://"):
                return
            if abs_url in seen_media_urls:
                return
            seen_media_urls.add(abs_url)

            # Determine extension
            path = urlparse(abs_url).path
            ext = path.split(".")[-1].lower() if "." in path else ""
            if not ext or len(ext) > 5:
                ext = "mp4" if m_type == "video" else ("mp3" if m_type == "audio" else "jpg")

            fmt = MediaFormat(
                format_id=f"fmt_{len(detected_items)}",
                format=ext,
                quality="Original",
                resolution=f"{width}x{height}".strip("x") if width and height else "Web Quality",
                filesize_bytes=None,
                filesize=None,
                has_video=(m_type == "video"),
                has_audio=(m_type in ["video", "audio"]),
                download_url=abs_url,
                note="Extracted from webpage"
            )

            detected_items.append(
                MediaItem(
                    id=f"item_{len(detected_items)}",
                    title=item_title,
                    media_type=m_type,
                    thumbnail=thumb or (abs_url if m_type == "image" else hero_thumbnail),
                    source_url=final_url,
                    direct_url=abs_url,
                    formats=[fmt],
                    width=width,
                    height=height
                )
            )

        # 2. Check OpenGraph / Twitter Video
        og_video = soup.find("meta", property="og:video") or soup.find("meta", property="og:video:url") or soup.find("meta", property="og:video:secure_url")
        if og_video and og_video.get("content"):
            add_item(og_video["content"], "video", f"{page_title} - Video", thumb=hero_thumbnail)

        # 3. Check JSON-LD Structured Data
        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
                items_to_check = data if isinstance(data, list) else [data]
                for node in items_to_check:
                    if not isinstance(node, dict):
                        continue
                    schema_type = node.get("@type", "")
                    if schema_type in ["VideoObject", "MusicVideoObject"] and node.get("contentUrl"):
                        add_item(
                            node["contentUrl"],
                            "video",
                            node.get("name") or page_title,
                            thumb=node.get("thumbnailUrl") or hero_thumbnail
                        )
                    elif schema_type in ["ImageObject"] and node.get("contentUrl"):
                        add_item(
                            node["contentUrl"],
                            "image",
                            node.get("name") or f"{page_title} Image",
                            thumb=node["contentUrl"]
                        )
            except Exception:
                continue

        # 4. Check HTML5 <video> & <source> tags
        for video_tag in soup.find_all("video"):
            v_src = video_tag.get("src")
            v_poster = video_tag.get("poster")
            if v_poster:
                v_poster = urljoin(final_url, v_poster)
            if v_src:
                add_item(v_src, "video", f"{page_title} - Video", thumb=v_poster or hero_thumbnail)
            for source in video_tag.find_all("source"):
                s_src = source.get("src")
                if s_src:
                    add_item(s_src, "video", f"{page_title} - Video Stream", thumb=v_poster or hero_thumbnail)

        # 5. Check HTML5 <audio> & <source> tags
        for audio_tag in soup.find_all("audio"):
            a_src = audio_tag.get("src")
            if a_src:
                add_item(a_src, "audio", f"{page_title} - Audio", thumb=hero_thumbnail)
            for source in audio_tag.find_all("source"):
                s_src = source.get("src")
                if s_src:
                    add_item(s_src, "audio", f"{page_title} - Audio Stream", thumb=hero_thumbnail)

        # 6. Check Images (OpenGraph image + high quality <img> elements)
        if hero_thumbnail:
            add_item(hero_thumbnail, "image", f"{page_title} - Featured Image", thumb=hero_thumbnail)

        for img in soup.find_all("img"):
            # Inspect sources
            src = img.get("src") or img.get("data-src") or img.get("data-original") or img.get("data-high-res-src")
            srcset = img.get("srcset") or img.get("data-srcset")

            # Extract best candidate from srcset if available
            if srcset:
                candidates = srcset.split(",")
                if candidates:
                    # Last candidate usually has highest resolution (e.g. "image-1200w.jpg 1200w")
                    best_cand = candidates[-1].strip().split()[0]
                    if best_cand:
                        src = best_cand

            if not src or src.startswith("data:"):
                continue

            # Skip tiny icons / trackers
            src_lower = src.lower()
            if any(re.search(pat, src_lower) for pat in IGNORE_IMAGE_PATTERNS):
                continue

            img_title = img.get("alt") or img.get("title") or f"{page_title} Image #{len(detected_items)+1}"
            width_attr = img.get("width")
            height_attr = img.get("height")
            w = int(width_attr) if width_attr and width_attr.isdigit() else None
            h = int(height_attr) if height_attr and height_attr.isdigit() else None

            # Skip if explicitly very small (e.g. < 60px)
            if (w and w < 60) or (h and h < 60):
                continue

            add_item(src, "image", clean_title(img_title), thumb=urljoin(final_url, src), width=w, height=h)

            if len(detected_items) >= 40:  # Cap at 40 media items
                break

        if not detected_items:
            raise MediaNotFoundError("No downloadable images, videos, or audio files found on this page.")

        # Determine dominant media type
        has_videos = any(i.media_type == "video" for i in detected_items)
        has_audio = any(i.media_type == "audio" for i in detected_items)
        dominant_type = "video" if has_videos else ("audio" if has_audio else "image")

        return MediaAnalysisResponse(
            success=True,
            url=final_url,
            source=domain,
            extractor_name=self.name,
            title=page_title,
            thumbnail=hero_thumbnail or (detected_items[0].thumbnail if detected_items else None),
            media_type=dominant_type,
            is_multi=len(detected_items) > 1,
            items_count=len(detected_items),
            items=detected_items,
            formats=detected_items[0].formats if detected_items else []
        )
