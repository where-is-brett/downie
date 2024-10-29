# src/downie/models/video.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class VideoMetadata:
    """Video metadata information."""

    title: str
    duration: Optional[float]
    upload_date: Optional[datetime]
    uploader: Optional[str]
    view_count: Optional[int]
    like_count: Optional[int]
    description: Optional[str]
    tags: List[str]
    categories: List[str]
    thumbnail_url: Optional[str]
    webpage_url: str
    extractor: str
    format_id: str
    width: Optional[int]
    height: Optional[int]
    fps: Optional[float]
    vcodec: Optional[str]
    acodec: Optional[str]
    filesize: Optional[int]


@dataclass
class DownloadResult:
    """Download result information."""

    success: bool
    filepath: Optional[Path]
    error: Optional[str]
    metadata: Optional[VideoMetadata]
    download_time: float
    filesize: int
    checksum: Optional[str]
