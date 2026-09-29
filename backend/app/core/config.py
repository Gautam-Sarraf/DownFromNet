import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Universal Media Downloader"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    # Allowed CORS Origins
    CORS_ORIGINS: list[str] = ["*"]

    # Storage and retention
    TEMP_STORAGE_DIR: Path = Path("/tmp/universal_media_downloader")
    FILE_RETENTION_MINUTES: int = 30
    CLEANUP_INTERVAL_SECONDS: int = 60

    # Download & Resource Limits
    MAX_FILE_SIZE_BYTES: int = 1024 * 1024 * 500  # 500 MB max download size
    MAX_DOWNLOAD_DURATION_SECONDS: int = 600  # 10 minutes max per task
    MAX_CONCURRENT_DOWNLOADS: int = 10
    REQUEST_TIMEOUT_SECONDS: int = 25

    # Rate Limiting (per client IP)
    RATE_LIMIT_ANALYZE_PER_MINUTE: int = 30
    RATE_LIMIT_DOWNLOAD_PER_MINUTE: int = 15

    # Security / SSRF
    ALLOW_PRIVATE_IPS: bool = False  # Set to True only for internal testing if required
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    # Optional Proxy and YouTube Cookies (for cloud deployments)
    PROXY_URL: str | None = None
    COOKIES_FILE_PATH: str | None = None
    COOKIES_TXT_CONTENT: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure temp storage directory exists
os.makedirs(settings.TEMP_STORAGE_DIR, exist_ok=True)
