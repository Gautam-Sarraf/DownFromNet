import re
from pathlib import Path
from typing import Optional
from app.core.config import settings


def get_cookie_file_path() -> Optional[str]:
    """
    Parses and sanitizes Netscape cookie content from environment variables or file paths.
    Converts literal escape sequences (\\n, \\t) and space-separated lines into valid Netscape tab format.
    """
    if settings.COOKIES_FILE_PATH and Path(settings.COOKIES_FILE_PATH).exists():
        return settings.COOKIES_FILE_PATH

    if not settings.COOKIES_TXT_CONTENT or not settings.COOKIES_TXT_CONTENT.strip():
        return None

    raw = settings.COOKIES_TXT_CONTENT.strip()

    # Handle escaped string inputs from cloud dashboards (.env / Render)
    if "\\n" in raw:
        raw = raw.replace("\\r\\n", "\n").replace("\\n", "\n")
    if "\\t" in raw:
        raw = raw.replace("\\t", "\t")

    lines = raw.splitlines()
    formatted_lines = [
        "# Netscape HTTP Cookie File",
        "# http://curl.haxx.se/rfc/cookie_spec.html",
        "# This is a generated file!  Do not edit.",
        ""
    ]

    for line in lines:
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue

        # If already tab-separated with 7 fields
        if "\t" in line_str:
            parts = line_str.split("\t")
            if len(parts) >= 7:
                formatted_lines.append("\t".join(parts[:7]))
                continue

        # If space-separated, convert to tab-separated
        parts = re.split(r"\s+", line_str)
        if len(parts) >= 7:
            formatted_lines.append("\t".join(parts[:7]))

    cookie_file = settings.TEMP_STORAGE_DIR / "cookies.txt"
    cookie_file.write_text("\n".join(formatted_lines) + "\n", encoding="utf-8")
    return str(cookie_file)
