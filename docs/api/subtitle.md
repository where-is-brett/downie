# Subtitle API Reference

The `SubtitleDownloader` class manages subtitle downloading and processing operations.

## SubtitleDownloader

```python
from downie.core.subtitle import SubtitleDownloader
from downie.models.config import SubtitleConfig
```

### Basic Usage

```python
config = SubtitleConfig(
    url="https://youtube.com/watch?v=example",
    output_path="subtitles",
    languages=["en", "es"]
)
downloader = SubtitleDownloader(config)
subtitle_files = downloader.download()
```

### Class Reference

#### SubtitleDownloader

```python
class SubtitleDownloader:
    """Subtitle downloader and processor."""
    
    def __init__(self, config: SubtitleConfig):
        """
        Initialize the subtitle downloader.
        
        Args:
            config: SubtitleConfig instance with subtitle settings
        """
        
    def download(self) -> List[Path]:
        """
        Download subtitles according to configuration.
        
        Returns:
            List of paths to downloaded subtitle files
            
        Raises:
            SubtitleError: If download fails
        """
        
    def list_available_subtitles(self) -> Dict[str, List[str]]:
        """
        List all available subtitles for a video.
        
        Returns:
            Dictionary mapping subtitle types to language codes
        """
        
    def _convert_to_srt(self, file: Path) -> Path:
        """
        Convert subtitle file to SRT format.
        
        Args:
            file: Input subtitle file
            
        Returns:
            Path to converted file
        """
        
    def _fix_encoding(self, file: Path) -> None:
        """
        Fix subtitle file encoding.
        
        Args:
            file: Subtitle file to fix
        """
        
    def _remove_formatting(self, file: Path) -> None:
        """
        Remove formatting tags from subtitles.
        
        Args:
            file: Subtitle file to process
        """
        
    def _merge_subtitles(self, files: List[Path]) -> Path:
        """
        Merge multiple subtitle files.
        
        Args:
            files: List of subtitle files to merge
            
        Returns:
            Path to merged subtitle file
        """
```

### Configuration

#### SubtitleConfig

```python
@dataclass
class SubtitleConfig:
    """Subtitle configuration."""
    
    url: str
    output_path: Path
    languages: List[str] = field(default_factory=lambda: ['en'])
    formats: List[str] = field(default_factory=lambda: ['srt'])
    auto_generated: bool = False
    convert_to_srt: bool = False
    fix_encoding: bool = True
    remove_formatting: bool = False
    merge_subtitles: bool = False
    time_offset: float = 0.0
```

### Examples

#### Basic Subtitle Download

```python
from downie.core.subtitle import SubtitleDownloader
from downie.models.config import SubtitleConfig
from pathlib import Path

# Configure subtitle download
config = SubtitleConfig(
    url="https://youtube.com/watch?v=example",
    output_path=Path("subtitles"),
    languages=["en", "es", "fr"]
)

# Initialize downloader
downloader = SubtitleDownloader(config)

# Check available subtitles
available = downloader.list_available_subtitles()
print("Available subtitles:", available)

# Download subtitles
try:
    subtitle_files = downloader.download()
    print(f"Downloaded {len(subtitle_files)} subtitle files:")
    for file in subtitle_files:
        print(f"- {file}")
except SubtitleError as e:
    print(f"Download failed: {e}")
```

#### Advanced Subtitle Processing

```python
# Download and process subtitles
config = SubtitleConfig(
    url="https://youtube.com/watch?v=example",
    output_path=Path("subtitles"),
    languages=["en"],
    convert_to_srt=True,
    fix_encoding=True,
    remove_formatting=True,
    time_offset=-2.5  # Adjust timing by -2.5 seconds
)

downloader = SubtitleDownloader(config)
subtitle_files = downloader.download()
```

#### Merging Multiple Language Subtitles

```python
config = SubtitleConfig(
    url="https://youtube.com/watch?v=example",
    output_path=Path("subtitles"),
    languages=["en", "es"],
    convert_to_srt=True,
    merge_subtitles=True
)

downloader = SubtitleDownloader(config)
merged_file = downloader.download()[0]  # Returns list with single merged file
```

### Working with Subtitle Files

```python
import pysrt

# Load SRT file
subs = pysrt.open('subtitles.srt')

# Adjust timing
for sub in subs:
    sub.start.hours += 1
    sub.end.hours += 1

# Save modified subtitles
subs.save('adjusted.srt')
```

### Error Handling

```python
from downie.exceptions.errors import SubtitleError

try:
    subtitle_files = downloader.download()
except SubtitleError as e:
    if "No subtitles found" in str(e):
        print("No subtitles available for this video")
    elif "Invalid URL" in str(e):
        print("Invalid video URL provided")
    else:
        print(f"Subtitle download failed: {e}")
```

### Best Practices

1. **Language Handling**
   - Check available languages before downloading
   - Use ISO 639-1 language codes
   - Handle missing language gracefully

2. **File Management**
   - Clean up temporary files
   - Use appropriate file extensions
   - Handle encoding issues properly

3. **Format Conversion**
   - Validate format compatibility
   - Preserve timing information
   - Handle formatting tags appropriately

4. **Quality Control**
   - Verify subtitle synchronization
   - Check character encoding
   - Validate merged subtitles

### Subtitle Format Support

The following subtitle formats are supported:

| Format | Extension | Description |
|--------|-----------|-------------|
| SubRip | .srt | Most common format, text-based |
| WebVTT | .vtt | Web-native format |
| ASS/SSA | .ass | Advanced SubStation Alpha |
| TTML | .ttml | Timed Text Markup Language |

### See Also

- [Downloader API](downloader.md)
- [Advanced Usage Guide](../guides/advanced-usage.md)
- [Configuration Guide](../guides/configuration.md)