import ipaddress
import re
import socket
from urllib.parse import urlparse
from app.core.config import settings
from app.core.errors import InvalidURLError, SSRFSecurityError


# Dangerous/Private IP networks to block
DISALLOWED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.88.99.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),  # Multicast
    ipaddress.ip_network("240.0.0.0/4"),  # Reserved
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("fc00::/7"),    # Unique local
    ipaddress.ip_network("fe80::/10"),   # Link-local
    ipaddress.ip_network("ff00::/8"),    # Multicast
]


def is_private_or_restricted_ip(ip_str: str) -> bool:
    """Check if an IP address string belongs to a private/restricted network."""
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
            return True
        for net in DISALLOWED_NETWORKS:
            if ip in net:
                return True
        return False
    except ValueError:
        return True


def validate_url_security(url: str) -> str:
    """
    Validates that a URL is well-formed, uses http/https, and does not target
    localhost or internal/private IP networks (SSRF prevention).
    """
    if not url or not isinstance(url, str):
        raise InvalidURLError("A valid URL string is required.")

    cleaned_url = url.strip()
    if not (cleaned_url.startswith("http://") or cleaned_url.startswith("https://")):
        # Auto-prefix http if missing schema or throw
        if cleaned_url.startswith("//"):
            cleaned_url = "https:" + cleaned_url
        elif "://" not in cleaned_url:
            cleaned_url = "https://" + cleaned_url
        else:
            raise InvalidURLError("Only HTTP and HTTPS URLs are supported.")

    try:
        parsed = urlparse(cleaned_url)
    except Exception:
        raise InvalidURLError("Malformed URL format.")

    hostname = parsed.hostname
    if not hostname:
        raise InvalidURLError("URL must contain a valid domain or host.")

    # Check for localhost keywords
    if hostname.lower() in ["localhost", "127.0.0.1", "0.0.0.0", "::1", "local"]:
        if not settings.ALLOW_PRIVATE_IPS:
            raise SSRFSecurityError()

    if not settings.ALLOW_PRIVATE_IPS:
        # Resolve host to IP addresses and check all
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                if is_private_or_restricted_ip(ip_str):
                    raise SSRFSecurityError(f"Target host '{hostname}' resolves to a restricted IP address.")
        except socket.gaierror:
            raise InvalidURLError(f"Unable to resolve host '{hostname}'.")

    return cleaned_url


def sanitize_filename(name: str, max_length: int = 120, default_ext: str = "") -> str:
    """
    Sanitizes a string to be safely used as a filename.
    Removes path traversal patterns (../, null bytes), unsafe filesystem chars,
    and limits length.
    """
    if not name:
        name = "download"

    # Remove null bytes and control chars
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    # Remove path traversal
    name = name.replace("..", "").replace("/", "_").replace("\\", "_")
    # Keep only alphanumeric, dash, underscore, dot, unicode words
    name = re.sub(r'[^\w\s\.\-]', '_', name).strip()
    name = re.sub(r'\s+', '_', name)
    # Collapse multiple consecutive underscores
    name = re.sub(r'_+', '_', name).strip('_')

    if not name or name == ".":
        name = "download"

    # Truncate
    if len(name) > max_length:
        base, ext = name[:max_length-10], name[-8:]
        name = f"{base}_{ext}"

    if default_ext and not name.lower().endswith(f".{default_ext.lstrip('.')}"):
        name = f"{name}.{default_ext.lstrip('.')}"

    return name
