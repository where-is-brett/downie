# Code Style Guide

This document outlines the coding standards and style guidelines for the Downie project.

## General Principles

1. Readability counts
2. Explicit is better than implicit
3. Simple is better than complex
4. Consistency matters

## Python Style Guidelines

### Code Formatting

We use `black` for code formatting with default settings:

```bash
# Format code
black .

# Check formatting without changes
black . --check
```

### Import Organization

Use `isort` for organizing imports:

```bash
# Sort imports
isort .

# Check import sorting
isort . --check-only
```

Import order should be:
1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
import os
from pathlib import Path
from typing import Dict, List, Optional

import ffmpeg
import yt_dlp
from click import command, option

from downie.core.processor import VideoProcessor
from downie.utils.validation import validate_url
```

### Type Hints

Use type hints for all function arguments and return types:

```python
def process_video(
    self,
    input_path: Path,
    output_format: Optional[str] = None
) -> Path:
    """Process video file."""
    ...

def get_formats(self, url: str) -> List[Dict[str, Any]]:
    """Get available video formats."""
    ...
```

### Documentation Strings

Use Google-style docstrings:

```python
def download_video(self, url: str, quality: str = "best") -> DownloadResult:
    """
    Download video from URL.
    
    Args:
        url: Video URL to download
        quality: Desired video quality (e.g., "720p", "1080p", "best")
        
    Returns:
        DownloadResult containing download status and metadata
        
    Raises:
        DownloadError: If download fails
        ValidationError: If URL is invalid
        
    Example:
        >>> downloader = VideoDownloader(config)
        >>> result = downloader.download_video("https://example.com/video")
        >>> print(result.success)
        True
    """
```

### Variable Naming

```python
# Good variable names
video_path = Path("video.mp4")
download_result = downloader.download()
frame_rate = 30
is_complete = True

# Bad variable names
p = Path("video.mp4")  # Too short
downloadResult = downloader.download()  # Not snake_case
frm_rt = 30  # Unclear abbreviation
```

### Constants

```python
# Constants in all caps
MAX_RETRIES = 3
DEFAULT_QUALITY = "1080p"
SUPPORTED_FORMATS = ["mp4", "webm", "mkv"]
```

### Error Handling

```python
try:
    result = downloader.download(url)
except ValidationError as e:
    logger.error(f"Invalid configuration: {e}")
    raise
except DownloadError as e:
    logger.error(f"Download failed: {e}")
    if retries < MAX_RETRIES:
        return retry_download(url)
    raise
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

### Class Organization

```python
class VideoProcessor:
    """Video processor class."""
    
    def __init__(self, config: ProcessingConfig):
        """Initialize processor."""
        self.config = config
        self._validate_setup()
    
    # Public methods first
    def process_video(self, input_path: Path) -> Path:
        """Process video file."""
        ...
    
    # Protected methods next
    def _validate_setup(self) -> None:
        """Validate processor setup."""
        ...
    
    # Private methods last
    def __parse_format(self, fmt_str: str) -> Dict[str, Any]:
        """Parse format string."""
        ...
```

### Comments and Documentation

```python
# Good comments
# Calculate video duration in seconds
duration = frames / fps

# Bad comments
# Increment x
x += 1
```

## Testing Guidelines

### Test Structure

```python
class TestVideoDownloader:
    """Test video downloader functionality."""
    
    @pytest.fixture
    def downloader(self):
        """Create test downloader instance."""
        config = DownloadConfig(...)
        return VideoDownloader(config)
    
    def test_successful_download(self, downloader):
        """Test successful video download."""
        result = downloader.download(TEST_URL)
        assert result.success
        assert result.filepath.exists()
```

### Test Naming

```python
# Good test names
def test_download_with_valid_url():
    ...

def test_processor_handles_missing_file():
    ...

# Bad test names
def test1():
    ...

def testDownload():
    ...
```

## Logging

```python
import logging

logger = logging.getLogger(__name__)

# Good logging
logger.debug("Processing video: %s", video_path)
logger.info("Download completed in %.2f seconds", duration)
logger.error("Failed to process video: %s", str(error))

# Bad logging
logger.debug(f"Processing video: {video_path}")  # f-strings in logging
logger.info("Starting...")  # Non-informative message
```

## Configuration

```python
# Good configuration
config = {
    'download': {
        'output_dir': '~/Downloads/videos',
        'max_concurrent_downloads': 3,
        'default_quality': '1080p',
    }
}

# Bad configuration
config = {
    'dir': '~/Downloads/videos',  # Unclear key
    'max': 3,  # Ambiguous
    'q': '1080p',  # Too short
}
```

## File Organization

```
src/downie/
├── __init__.py
├── cli/
│   ├── __init__.py
│   ├── download.py
│   └── subtitle.py
├── core/
│   ├── __init__.py
│   ├── downloader.py
│   └── processor.py
├── models/
│   ├── __init__.py
│   └── config.py
└── utils/
    ├── __init__.py
    └── validation.py
```

## Git Commit Messages

```bash
# Good commit messages
git commit -m "Add video processing progress bar"
git commit -m "Fix memory leak in subtitle processor"
git commit -m "Update documentation for new API features"

# Bad commit messages
git commit -m "fix bug"
git commit -m "updates"
git commit -m "WIP"
```

## Pre-commit Hooks

Our pre-commit configuration (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Editor Configuration

### VSCode Settings

```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "files.trimTrailingWhitespace": true
}
```

## Additional Resources

- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [Black Documentation](https://black.readthedocs.io/en/stable/)