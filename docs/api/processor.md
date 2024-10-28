# Processor API Reference

The `VideoProcessor` class handles video processing operations like resizing, cropping, and format conversion.

## VideoProcessor

```python
from downie.core.processor import VideoProcessor
from downie.models.config import ProcessingConfig
```

### Basic Usage

```python
config = ProcessingConfig(
    resize="1920x1080",
    fps=30,
    video_codec="libx264"
)
processor = VideoProcessor(config)
output_path = processor.process_video(input_path)
```

### Class Reference

#### VideoProcessor

```python
class VideoProcessor:
    """Video processor with advanced processing capabilities."""
    
    def __init__(self, config: ProcessingConfig):
        """
        Initialize the processor.
        
        Args:
            config: ProcessingConfig instance with processing settings
        """
        
    def process_video(self, input_path: Path) -> Path:
        """
        Process video according to configuration.
        
        Args:
            input_path: Path to input video file
            
        Returns:
            Path to processed video file
            
        Raises:
            ProcessingError: If processing fails
        """
        
    def _validate_codecs(self) -> bool:
        """
        Validate video and audio codec support.
        
        Returns:
            True if codecs are supported
            
        Raises:
            ProcessingError: If codecs are not supported
        """
        
    def _get_video_info(self, file: Path) -> Dict:
        """
        Get video file information.
        
        Args:
            file: Video file path
            
        Returns:
            Dictionary with video metadata
        """
```

### Configuration

#### ProcessingConfig

```python
@dataclass
class ProcessingConfig:
    """Video processing configuration."""
    
    crop: Optional[str] = None  # format: "width:height:x:y"
    resize: Optional[str] = None  # format: "widthxheight"
    rotate: Optional[int] = None  # degrees: 90, 180, 270
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
```

### Examples

#### Basic Processing

```python
from downie.core.processor import VideoProcessor
from downie.models.config import ProcessingConfig
from pathlib import Path

# Configure processing
config = ProcessingConfig(
    resize="1920x1080",
    fps=30,
    video_codec="libx264",
    audio_codec="aac"
)

# Initialize processor
processor = VideoProcessor(config)

# Process video
try:
    output_path = processor.process_video(Path("input.mp4"))
    print(f"Processed video saved to: {output_path}")
except ProcessingError as e:
    print(f"Processing failed: {e}")
```

#### HDR to SDR Conversion

```python
config = ProcessingConfig(
    hdr_to_sdr=True,
    video_codec="libx264",
    video_bitrate="5M"
)

processor = VideoProcessor(config)
output_path = processor.process_video(input_path)
```

#### Video Stabilization

```python
config = ProcessingConfig(
    stabilize=True,
    video_codec="libx264",
    fps=30
)

processor = VideoProcessor(config)
output_path = processor.process_video(input_path)
```

### Best Practices

1. **Performance**
   - Monitor system resources during processing
   - Use appropriate codec settings for your needs
   - Consider hardware acceleration when available

2. **Quality Control**
   - Validate input files before processing
   - Check output quality after processing
   - Use appropriate bitrates for target quality

3. **Error Handling**
   - Handle codec validation errors
   - Check disk space before processing
   - Implement cleanup on failure

### See Also

- [Downloader API](downloader.md)
- [Advanced Usage Guide](../guides/advanced-usage.md)