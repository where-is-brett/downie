# Downloader API Reference

The `VideoDownloader` class is the main interface for downloading videos.

## VideoDownloader

```python
from downie.core.downloader import VideoDownloader
from downie.models.config import DownloadConfig
```

### Basic Usage

```python
config = DownloadConfig(
    url="https://youtube.com/watch?v=example",
    output_path="downloads",
    quality="1080p"
)
downloader = VideoDownloader(config)
result = downloader.download()

if result.success:
    print(f"Downloaded to: {result.filepath}")
    print(f"File size: {result.filesize} bytes")
    print(f"Download time: {result.download_time}s")
```

### Class Reference

#### VideoDownloader

```python
class VideoDownloader:
    """Video downloader with advanced configuration options."""
    
    def __init__(self, config: DownloadConfig):
        """
        Initialize the downloader.
        
        Args:
            config: DownloadConfig instance with download settings
        """
        
    def download(self, url: Optional[str] = None) -> DownloadResult:
        """
        Download video from URL.
        
        Args:
            url: Optional URL override. If not provided, uses config URL
            
        Returns:
            DownloadResult containing download status and metadata
            
        Raises:
            DownloadError: If download fails
            ValidationError: If URL is invalid
        """
        
    def get_formats(self, url: str) -> List[Dict[str, Any]]:
        """
        Get available formats for video.
        
        Args:
            url: Video URL
            
        Returns:
            List of format dictionaries with quality info
        """
        
    def get_info(self, url: str) -> VideoMetadata:
        """
        Get video metadata without downloading.
        
        Args:
            url: Video URL
            
        Returns:
            VideoMetadata object with video information
        """
```

### Configuration

#### DownloadConfig

```python
@dataclass
class DownloadConfig:
    """Download configuration settings."""
    
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
```

### Return Types

#### DownloadResult

```python
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
```

#### VideoMetadata

```python
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
```

### Examples

#### Basic Download

```python
from downie.core.downloader import VideoDownloader
from downie.models.config import DownloadConfig
from pathlib import Path

# Configure download
config = DownloadConfig(
    url="https://youtube.com/watch?v=example",
    output_path=Path("downloads"),
    quality="1080p"
)

# Initialize downloader
downloader = VideoDownloader(config)

# Perform download
result = downloader.download()

# Handle result
if result.success:
    print(f"Downloaded: {result.filepath}")
    print(f"Size: {result.filesize / 1024 / 1024:.1f}MB")
    print(f"Time: {result.download_time:.1f}s")
else:
    print(f"Download failed: {result.error}")
```

#### Format Selection

```python
# Get available formats
formats = downloader.get_formats("https://youtube.com/watch?v=example")

# Print format information
for fmt in formats:
    print(f"ID: {fmt['format_id']}")
    print(f"Quality: {fmt.get('height', 'N/A')}p")
    print(f"Codecs: {fmt.get('vcodec', 'N/A')}, {fmt.get('acodec', 'N/A')}")
    print(f"Filesize: {fmt.get('filesize', 0) / 1024 / 1024:.1f}MB")
    print("---")

# Download specific format
config = DownloadConfig(
    url="https://youtube.com/watch?v=example",
    output_path=Path("downloads"),
    format_id="137+140"  # 1080p video + audio
)
```

#### Error Handling

```python
try:
    result = downloader.download()
    if not result.success:
        print(f"Download failed: {result.error}")
except ValidationError as e:
    print(f"Invalid configuration: {e}")
except DownloadError as e:
    print(f"Download error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Event Handling

```python
# Progress callback
def progress_callback(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        print(f"Downloading: {percent} at {speed}")

# Configure with callback
config = DownloadConfig(
    url="https://youtube.com/watch?v=example",
    output_path=Path("downloads")
)
downloader = VideoDownloader(config)
downloader._progress_hook = progress_callback
```

### Best Practices

1. **Error Handling**
   - Always check `result.success` and handle errors
   - Use specific exception types for better error handling
   - Implement retries for transient failures

2. **Resource Management**
   - Close/cleanup resources in error cases
   - Use context managers when appropriate
   - Monitor disk space and bandwidth usage

3. **Configuration**
   - Validate URLs before downloading
   - Use appropriate quality settings for your needs
   - Consider rate limiting for batch downloads

4. **Performance**
   - Use batch mode for multiple downloads
   - Implement progress monitoring for long downloads
   - Consider using proxy rotation for large batches

5. **Security**
   - Validate output paths
   - Handle credentials securely
   - Use SSL verification unless absolutely necessary to disable

### See Also

- [Processor API](processor.md)
- [Subtitle API](subtitle.md)
- [Configuration Guide](../guides/configuration.md)