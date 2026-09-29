import random
import re
from typing import Optional
from app.core.config import settings


class ProxyManager:
    """
    Manages proxy rotation for cloud media scrapers.
    Supports formats:
    - http://user:pass@host:port
    - socks5://user:pass@host:port
    - host:port:user:pass
    - user:pass@host:port
    - host:port
    """
    def __init__(self):
        self._proxies: list[str] = []
        self._load_proxies()

    def _normalize_proxy(self, raw: str) -> Optional[str]:
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            return None

        # Already full URL
        if raw.startswith("http://") or raw.startswith("https://") or raw.startswith("socks5://"):
            return raw

        # format: host:port:user:pass
        parts = raw.split(":")
        if len(parts) == 4:
            host, port, user, password = parts
            return f"http://{user}:{password}@{host}:{port}"

        # format: user:pass@host:port
        if "@" in raw:
            return f"http://{raw}"

        # format: host:port
        if len(parts) == 2:
            host, port = parts
            return f"http://{host}:{port}"

        return f"http://{raw}"

    def _load_proxies(self):
        proxies: list[str] = []

        if settings.PROXY_URL and settings.PROXY_URL.strip():
            normalized = self._normalize_proxy(settings.PROXY_URL)
            if normalized:
                proxies.append(normalized)

        if settings.PROXY_LIST and settings.PROXY_LIST.strip():
            # Split by comma or newline
            raw_entries = re.split(r"[\n,;]+", settings.PROXY_LIST)
            for entry in raw_entries:
                normalized = self._normalize_proxy(entry)
                if normalized and normalized not in proxies:
                    proxies.append(normalized)

        self._proxies = proxies

    def get_proxy(self) -> Optional[str]:
        if not self._proxies:
            self._load_proxies()
        if not self._proxies:
            return None
        return random.choice(self._proxies)

    def get_all_proxies(self) -> list[str]:
        if not self._proxies:
            self._load_proxies()
        return self._proxies


proxy_manager = ProxyManager()
