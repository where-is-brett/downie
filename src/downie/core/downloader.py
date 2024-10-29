# src/downie/core/downloader.py
import re
import time
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

import yt_dlp

from ..exceptions.errors import DownloadError, UnsupportedPlatformError, ValidationError
from ..logging.logger import get_logger
from ..models.config import DownloadConfig
from ..models.video import DownloadResult, VideoMetadata
from ..utils.filesystem import calculate_checksum

logger = get_logger(__name__)


class VideoDownloader:
    def __init__(self, config: DownloadConfig):
        self.config = config
        self._validate_url(self.config.url)
        self.ydl_opts = self._prepare_ydl_opts()

    def _validate_url(self, url: str) -> None:
        """Validate URL format."""
        if not url or not isinstance(url, str):
            raise ValidationError("URL cannot be empty")

        try:
            result = urlparse(url)
            if not all(
                [
                    result.scheme in ("http", "https"),
                    result.netloc,  # Must have a domain
                    result.path
                    or result.query
                    or result.fragment,  # Ensures URL has path, query, or fragment
                    len(url) <= 2083,  # Common URL length limit
                ]
            ):
                raise ValidationError(f"Invalid URL format: {url}")
        except Exception:
            raise ValidationError(f"Invalid URL format: {url}")

    def _parse_size_string(self, size_str: str) -> int:
        """Parse size string with units (e.g., '1M', '500K') to bytes."""
        units = {"K": 1024, "M": 1024 * 1024, "G": 1024 * 1024 * 1024}

        # Remove whitespace and convert to uppercase for consistency
        size_str = size_str.strip().upper()

        # Parse value and unit
        match = re.match(r"^([\d.]+)([KMG])?$", size_str)
        if not match:
            raise ValidationError(f"Invalid size format: {size_str}")

        value, unit = match.groups()
        try:
            value = float(value)
        except ValueError:
            raise ValidationError(f"Invalid numeric value: {value}")

        # Convert to bytes
        return int(value * (units.get(unit, 1) if unit else 1))

    def _prepare_ydl_opts(self) -> Dict:
        """Prepare yt-dlp options from configuration."""
        # Handle quality setting
        if self.config.quality == "best":
            format_spec = "bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4][vcodec^=avc]/best"
        else:
            # Extract numeric height from quality string (e.g., '1080p' -> '1080')
            height = self.config.quality.rstrip("p")
            format_spec = f"bestvideo[height<={height}][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4][vcodec^=avc]/best"

        opts = {
            "format": self.config.format_id or format_spec,
            "outtmpl": str(self.config.output_path / "%(title)s.%(ext)s"),
            "retries": getattr(self.config, "retries", 3),
            "quiet": False,
            "progress_hooks": [self._progress_hook],
            "merge_output_format": "mp4",
        }

        if self.config.proxy:
            opts["proxy"] = self.config.proxy

        if self.config.limit_speed:
            try:
                opts["ratelimit"] = self._parse_size_string(self.config.limit_speed)
            except ValidationError as e:
                raise ValidationError(f"Invalid rate limit: {str(e)}")

        return opts

    def _parse_quality(self, quality: str) -> str:
        """Parse quality string to determine video resolution limit."""
        if isinstance(quality, str):
            match = re.match(r"(\d+)", quality)
            if match:
                return match.group(1)  # Extracts the numeric part, like 720 from "720p"
        return "best"  # Default to "best" if no resolution is specified

    def download(self) -> DownloadResult:
        """Download video from URL."""
        url = self.config.url
        start_time = time.time()
        last_error = None

        for attempt in range(self.config.retries):
            try:
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    try:
                        # Get info and download in one call
                        info = ydl.extract_info(url, download=True)
                    except yt_dlp.utils.UnsupportedError:
                        raise UnsupportedPlatformError(
                            f"Platform not supported for URL: {url}"
                        )
                    except yt_dlp.utils.DownloadError as e:
                        if "Unsupported URL" in str(e):
                            raise UnsupportedPlatformError(
                                f"Platform not supported for URL: {url}"
                            )
                        raise

                    filename = ydl.prepare_filename(info)
                    filepath = Path(filename)

                    if not filepath.exists():
                        raise DownloadError(
                            f"Download completed but file not found: {filepath}"
                        )

                    metadata = self._extract_metadata(info)
                    filesize = filepath.stat().st_size
                    checksum = calculate_checksum(filepath)

                    return DownloadResult(
                        success=True,
                        filepath=filepath,
                        error=None,
                        metadata=metadata,
                        download_time=time.time() - start_time,
                        filesize=filesize,
                        checksum=checksum,
                    )

            except UnsupportedPlatformError as e:
                # Don't retry for unsupported platforms
                logger.warning(str(e))
                return DownloadResult(
                    success=False,
                    filepath=None,
                    error=str(e),
                    metadata=None,
                    download_time=time.time() - start_time,
                    filesize=0,
                    checksum=None,
                )

            except Exception as e:
                last_error = str(e)
                logger.error(f"Download attempt {attempt + 1} failed: {last_error}")

                if attempt < self.config.retries - 1:
                    sleep_time = 2**attempt  # Exponential backoff
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)

        # If we get here, all retries failed
        return DownloadResult(
            success=False,
            filepath=None,
            error=last_error,
            metadata=None,
            download_time=time.time() - start_time,
            filesize=0,
            checksum=None,
        )

    def _extract_metadata(self, info: Dict) -> VideoMetadata:
        """Extract metadata from downloaded video info."""
        return VideoMetadata(
            title=info.get("title", ""),
            duration=info.get("duration"),
            upload_date=info.get("upload_date"),
            uploader=info.get("uploader"),
            view_count=info.get("view_count"),
            like_count=info.get("like_count"),
            description=info.get("description"),
            tags=info.get("tags", []),
            categories=info.get("categories", []),
            thumbnail_url=info.get("thumbnail"),
            webpage_url=info.get("webpage_url", ""),
            extractor=info.get("extractor", ""),
            format_id=info.get("format_id", ""),
            width=info.get("width"),
            height=info.get("height"),
            fps=info.get("fps"),
            vcodec=info.get("vcodec"),
            acodec=info.get("acodec"),
            filesize=info.get("filesize"),
        )

    def _progress_hook(self, d: Dict) -> None:
        """Handle download progress updates."""
        if d["status"] == "downloading":
            if "total_bytes" in d:
                percentage = (d["downloaded_bytes"] / d["total_bytes"]) * 100
                print(f"\rDownload progress: {percentage:.1f}%", end="")
            else:
                print(
                    f"\rDownloaded: {d['downloaded_bytes'] / (1024*1024):.1f}MB", end=""
                )
        elif d["status"] == "finished":
            print("\nDownload completed, processing file...")
