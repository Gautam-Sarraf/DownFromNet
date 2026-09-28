from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


DownloadStatus = Literal["pending", "downloading", "processing", "completed", "failed", "cancelled"]


class DownloadRequest(BaseModel):
    url: str = Field(description="URL that was analyzed")
    media_item_id: Optional[str] = Field(default=None, description="Specific media item id if multi-item")
    format_id: Optional[str] = Field(default=None, description="Selected format id")
    target_format: Optional[str] = Field(default=None, description="Optional target format to convert into (e.g. mp3, mp4, jpg)")
    quality: Optional[str] = Field(default=None, description="Selected quality label")
    direct_url: Optional[str] = Field(default=None, description="Direct URL if already resolved")
    custom_filename: Optional[str] = Field(default=None, description="Custom base filename without extension")


class BatchDownloadRequest(BaseModel):
    url: str = Field(description="URL that was analyzed")
    item_ids: list[str] = Field(min_length=1, description="List of item IDs to package into ZIP archive")
    archive_name: Optional[str] = Field(default="media_bundle", description="Name for the resulting ZIP file")
    target_format: Optional[str] = Field(default=None, description="Optional uniform conversion format")


class DownloadJobStatus(BaseModel):
    job_id: str
    status: DownloadStatus = "pending"
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage completed")
    message: str = "Download initiated"
    filename: Optional[str] = None
    filesize_bytes: Optional[int] = None
    filesize_formatted: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_archive: bool = False
