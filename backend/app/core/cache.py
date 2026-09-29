import time
from typing import Optional
from app.schemas.media import MediaAnalysisResponse


class MetadataCache:
    """
    In-memory TTL cache for media analysis results.
    Prevents repeated expensive network scraping when the same URL is analyzed.
    """
    def __init__(self, ttl_seconds: int = 600, max_size: int = 500):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: dict[str, tuple[float, MediaAnalysisResponse]] = {}

    def _normalize_key(self, url: str) -> str:
        # Strip tracking params (si=, utm_=, etc.) for clean caching
        url_clean = url.strip()
        if "youtu" in url_clean:
            # Normalize youtu.be / youtube.com links to canonical form
            if "youtu.be/" in url_clean:
                vid_id = url_clean.split("youtu.be/")[-1].split("?")[0].split("/")[0]
                return f"youtube:{vid_id}"
            elif "v=" in url_clean:
                try:
                    vid_id = url_clean.split("v=")[1].split("&")[0]
                    return f"youtube:{vid_id}"
                except IndexError:
                    pass
        return url_clean

    def get(self, url: str) -> Optional[MediaAnalysisResponse]:
        key = self._normalize_key(url)
        if key in self._cache:
            timestamp, response = self._cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                return response
            else:
                del self._cache[key]
        return None

    def set(self, url: str, response: MediaAnalysisResponse):
        # Evict oldest entries if capacity reached
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            del self._cache[oldest_key]

        key = self._normalize_key(url)
        self._cache[key] = (time.time(), response)

    def clear(self):
        self._cache.clear()


media_cache = MetadataCache(ttl_seconds=600)  # 10 minutes cache TTL
