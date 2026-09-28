from typing import Optional, Literal
from pydantic import BaseModel, Field


MediaType = Literal["video", "audio", "image", "document", "other"]


class MediaFormat(BaseModel):
    format_id: str = Field(description="Unique format identifier (e.g. '137', 'mp4-1080p', 'direct')")
    format: str = Field(description="Container or extension name (e.g. 'mp4', 'webm', 'mp3', 'jpg')")
    quality: str = Field(default="Standard", description="Quality label (e.g. '1080p', '720p', '320kbps', 'Original')")
    resolution: Optional[str] = Field(default=None, description="Resolution if applicable (e.g. '1920x1080')")
    filesize_bytes: Optional[int] = Field(default=None, description="Filesize in bytes if known")
    filesize: Optional[str] = Field(default=None, description="Human readable filesize (e.g. '45.2 MB')")
    has_video: bool = True
    has_audio: bool = True
    download_url: Optional[str] = None
    note: Optional[str] = None


class MediaItem(BaseModel):
    id: str = Field(description="Identifier within this extraction result (e.g. 'item_0', 'img_1')")
    title: str = Field(default="Media Download")
    media_type: MediaType = "video"
    thumbnail: Optional[str] = None
    duration: Optional[float] = Field(default=None, description="Duration in seconds")
    duration_formatted: Optional[str] = Field(default=None, description="Duration as mm:ss or hh:mm:ss")
    source_url: str
    direct_url: Optional[str] = None
    formats: list[MediaFormat] = Field(default_factory=list)
    width: Optional[int] = None
    height: Optional[int] = None
    original_filename: Optional[str] = None


class AnalyzeRequest(BaseModel):
    url: str = Field(description="Public URL to inspect and extract media from")


class MediaAnalysisResponse(BaseModel):
    success: bool = True
    url: str
    source: str = Field(description="Domain or platform name (e.g. 'youtube', 'instagram', 'generic')")
    extractor_name: str
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[float] = None
    duration_formatted: Optional[str] = None
    media_type: MediaType = "video"
    is_multi: bool = False
    items_count: int = 1
    items: list[MediaItem] = Field(default_factory=list)
    formats: list[MediaFormat] = Field(default_factory=list)
    notice: Optional[str] = "Only download content you have permission to download. Respect copyright and platform terms."
