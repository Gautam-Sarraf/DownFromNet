import random
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.core.config import settings
from app.core.telemetry import sanitize_proxy_url


class ProxyHealthRecord:
    def __init__(self, raw_url: str):
        self.raw_url = raw_url
        self.sanitized_url = sanitize_proxy_url(raw_url) or raw_url
        self.success_count: int = 0
        self.failure_count: int = 0
        self.consecutive_failures: int = 0
        self.last_success: Optional[datetime] = None
        self.last_failure: Optional[datetime] = None
        self.latency_ms: float = 0.0
        self.cooldown_until: Optional[datetime] = None

    @property
    def is_healthy(self) -> bool:
        if self.cooldown_until and datetime.now(timezone.utc) < self.cooldown_until:
            return False
        return True

    def record_success(self, latency_ms: float = 0.0):
        self.success_count += 1
        self.consecutive_failures = 0
        self.last_success = datetime.now(timezone.utc)
        self.cooldown_until = None
        if latency_ms > 0:
            # Exponential moving average for latency
            if self.latency_ms == 0.0:
                self.latency_ms = latency_ms
            else:
                self.latency_ms = round(self.latency_ms * 0.7 + latency_ms * 0.3, 2)

    def record_failure(self, is_hard_failure: bool = True, cooldown_seconds: int = 60):
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_failure = datetime.now(timezone.utc)

        if is_hard_failure or self.consecutive_failures >= 3:
            penalty = min(300, cooldown_seconds * (2 ** max(0, self.consecutive_failures - 3)))
            self.cooldown_until = datetime.now(timezone.utc) + timedelta(seconds=penalty)


class HealthAwareProxyManager:
    """
    Health-aware proxy pool manager with latency tracking and automatic cooldown.
    Supports formats:
    - http://user:pass@host:port
    - socks5://user:pass@host:port
    - host:port:user:pass
    - user:pass@host:port
    - host:port
    """
    def __init__(self):
        self._proxies: dict[str, ProxyHealthRecord] = {}
        self._load_proxies()

    def _normalize_proxy(self, raw: str) -> Optional[str]:
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            return None

        # Already full URL scheme
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
        loaded_urls: list[str] = []

        if settings.PROXY_URL and settings.PROXY_URL.strip():
            normalized = self._normalize_proxy(settings.PROXY_URL)
            if normalized:
                loaded_urls.append(normalized)

        if settings.PROXY_LIST and settings.PROXY_LIST.strip():
            raw_entries = re.split(r"[\n,;]+", settings.PROXY_LIST)
            for entry in raw_entries:
                normalized = self._normalize_proxy(entry)
                if normalized and normalized not in loaded_urls:
                    loaded_urls.append(normalized)

        # Retain existing records, add new ones
        for url in loaded_urls:
            if url not in self._proxies:
                self._proxies[url] = ProxyHealthRecord(url)

    def get_proxy(self) -> Optional[str]:
        """
        Returns the best healthy proxy using weighted selection (lowest latency & highest success rate).
        """
        if not self._proxies:
            self._load_proxies()

        if not self._proxies:
            return None

        healthy_records = [p for p in self._proxies.values() if p.is_healthy]

        if not healthy_records:
            # If all are in cooldown, reset expired ones or pick the one with oldest cooldown
            now = datetime.utcnow()
            available = [p for p in self._proxies.values() if p.cooldown_until and p.cooldown_until <= now]
            if available:
                healthy_records = available
            else:
                # Pick proxy with earliest cooldown expiration
                healthy_records = sorted(self._proxies.values(), key=lambda p: p.cooldown_until or now)[:2]

        # Prioritize proxies with lowest latency and fewer consecutive failures
        sorted_proxies = sorted(
            healthy_records,
            key=lambda p: (p.consecutive_failures, p.latency_ms if p.latency_ms > 0 else 9999.0)
        )

        # Select from the top 3 best proxies with slight randomization to balance load
        candidates = sorted_proxies[:min(3, len(sorted_proxies))]
        return random.choice(candidates).raw_url

    def get_all_healthy_proxies(self) -> list[str]:
        """Returns list of all currently healthy proxy URLs in priority order."""
        if not self._proxies:
            self._load_proxies()

        if not self._proxies:
            return []

        healthy = [p for p in self._proxies.values() if p.is_healthy]
        if not healthy:
            # Return all if none strictly healthy
            return [p.raw_url for p in self._proxies.values()]

        sorted_healthy = sorted(
            healthy,
            key=lambda p: (p.consecutive_failures, p.latency_ms if p.latency_ms > 0 else 9999.0)
        )
        return [p.raw_url for p in sorted_healthy]

    def report_success(self, proxy_url: Optional[str], latency_ms: float = 0.0):
        if proxy_url and proxy_url in self._proxies:
            self._proxies[proxy_url].record_success(latency_ms)

    def report_failure(self, proxy_url: Optional[str], error: Exception):
        """
        Classifies error before penalizing proxy:
        - Network/timeout/connect errors -> hard proxy failure
        - Platform bot check -> soft proxy failure
        - Video unavailable / private / invalid URL -> NOT a proxy failure
        """
        if not proxy_url or proxy_url not in self._proxies:
            return

        err_str = str(error).lower()

        # Non-proxy failures (content-level issues)
        if any(k in err_str for k in ["unavailable", "removed", "private video", "not a valid", "deleted"]):
            return

        # Hard network errors
        if any(k in err_str for k in ["timed out", "timeout", "connection refused", "connection reset", "proxy error"]):
            self._proxies[proxy_url].record_failure(is_hard_failure=True, cooldown_seconds=90)
            return

        # Soft errors (rate limit / bot check)
        if any(k in err_str for k in ["429", "bot", "too many requests", "sign in"]):
            self._proxies[proxy_url].record_failure(is_hard_failure=False, cooldown_seconds=45)
            return

        # Default soft failure
        self._proxies[proxy_url].record_failure(is_hard_failure=False, cooldown_seconds=30)


proxy_manager = HealthAwareProxyManager()
