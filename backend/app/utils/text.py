import re
from typing import Optional
from urllib.parse import urlparse


def extract_domain(url: str) -> str:
    """Extract human-readable source/domain name from URL."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or "generic"
        # Strip www.
        if hostname.startswith("www."):
            hostname = hostname[4:]
        # Get main domain name (e.g. youtube.com -> youtube)
        parts = hostname.split(".")
        if len(parts) >= 2:
            return parts[-2]
        return hostname
    except Exception:
        return "generic"


def clean_title(title: Optional[str], default: str = "Media File") -> str:
    if not title:
        return default
    # Strip HTML tags
    title = re.sub(r'<[^>]+>', '', title)
    # Strip multiple spaces / line breaks
    title = re.sub(r'\s+', ' ', title).strip()
    return title or default
