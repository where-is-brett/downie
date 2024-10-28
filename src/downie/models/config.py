# src/downie/models/config.py
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path

@dataclass
class ProcessingConfig:
    """Video processing configuration."""
    crop: Optional[str] = None
    resize: Optional[str] = None
    rotate: Optional[int] = None
    fps: Optional[int] = None
    video_codec: str = 'libx264'
    audio_codec: str = 'aac'
    video_bitrate: Optional[str] = None
    audio_bitrate: Optional[str] = None
    remove_audio: bool = False
    extract_audio: bool = False
    audio_format: str = 'mp3'
    stabilize: bool = False
    denoise: bool = False
    hdr_to_sdr: bool = False

    def __post_init__(self):
        """Validate configuration values."""
        # No validation in post_init, moved to processor methods
        pass

@dataclass
class DownloadConfig:
    """Download configuration."""
    url: str
    output_path: Path
    quality: str = 'best'
    format_id: Optional[str] = None
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    proxy: Optional[str] = None
    limit_speed: Optional[str] = None
    geo_bypass: bool = False
    cookies_file: Optional[Path] = None
    username: Optional[str] = None
    password: Optional[str] = None
    max_downloads: Optional[int] = None
    batch_mode: bool = False
    verify_ssl: bool = True
    retries: int = 3
    rate_limit: Optional[str] = None

    def __post_init__(self):
        """Convert string paths to Path objects and validate configuration."""
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)
        if isinstance(self.cookies_file, str):
            self.cookies_file = Path(self.cookies_file)
        
        # Validate quality setting
        if self.quality != 'best' and not self.quality.endswith('p'):
            self.quality = f"{self.quality}p"
        
        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)

@dataclass
class SubtitleConfig:
    """Subtitle configuration."""
    url: str
    output_path: Path
    languages: List[str] = field(default_factory=lambda: ['en'])
    formats: List[str] = field(default_factory=lambda: ['vtt', 'srt'])  # Default to both formats
    auto_generated: bool = False
    convert_to_srt: bool = True  # Default to True
    fix_encoding: bool = True
    remove_formatting: bool = False
    merge_subtitles: bool = False
    time_offset: float = 0.0

    def __post_init__(self):
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

