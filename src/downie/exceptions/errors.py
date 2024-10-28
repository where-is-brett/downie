# src/downie/exceptions/errors.py
class VideoDownloaderError(Exception):
    """Base exception for video downloader."""
    pass

class DownloadError(VideoDownloaderError):
    """Raised when download fails."""
    pass

class ValidationError(VideoDownloaderError):
    """Raised when validation fails."""
    pass

class SubtitleError(VideoDownloaderError):
    """Raised when subtitle processing fails."""
    pass

class ProcessingError(VideoDownloaderError):
    """Raised when video processing fails."""
    pass

class UnsupportedPlatformError(DownloadError):
    """Raised when video platform is not supported."""
    pass