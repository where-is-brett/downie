# Testing Guide

This guide covers testing practices and guidelines for the Downie project.

## Testing Framework

We use pytest as our testing framework. All tests are located in the `tests/` directory.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_downloader.py    # Downloader tests
├── test_processor.py     # Processor tests
├── test_subtitle.py      # Subtitle tests
└── test_utils.py         # Utility tests
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_downloader.py

# Run specific test
pytest tests/test_downloader.py::TestDownloader::test_download_success

# Run with coverage
pytest --cov=downie

# Run with verbose output
pytest -v

# Run tests marked as 'slow'
pytest -m slow
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from downie.core.downloader import VideoDownloader
from downie.models.config import DownloadConfig

class TestDownloader:
    """Test video downloader functionality."""
    
    @pytest.fixture
    def downloader(self, tmp_path):
        """Create test downloader instance."""
        config = DownloadConfig(
            url="https://example.com/video",
            output_path=tmp_path
        )
        return VideoDownloader(config)
    
    def test_download_success(self, downloader):
        """Test successful video download."""
        result = downloader.download()
        assert result.success
        assert result.filepath.exists()
        
    def test_download_failure(self, downloader):
        """Test download failure handling."""
        downloader.config.url = "invalid://url"
        with pytest.raises(ValidationError):
            downloader.download()
```

### Fixtures

```python
# In conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_video(tmp_path: Path) -> Path:
    """Create a sample video file for testing."""
    video_path = tmp_path / "test.mp4"
    # Create test video using FFmpeg
    subprocess.run([
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'testsrc=duration=1:size=1280x720:rate=30',
        '-f', 'lavfi',
        '-i', 'aevalsrc=0:duration=1',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        str(video_path)
    ], check=True)
    return video_path

@pytest.fixture
def mock_downloader(mocker):
    """Create a mocked downloader."""
    return mocker.patch('downie.core.downloader.VideoDownloader')
```

### Test Categories

#### Unit Tests

```python
def test_validate_url():
    """Test URL validation."""
    assert validate_url("https://youtube.com/watch?v=123")
    assert not validate_url("invalid://url")
    
def test_parse_size_string():
    """Test size string parsing."""
    assert parse_size_string("1M") == 1024 * 1024
    assert parse_size_string("500K") == 500 * 1024
```

#### Integration Tests

```python
@pytest.mark.integration
def test_download_and_process(downloader, tmp_path):
    """Test full download and process workflow."""
    result = downloader.download()
    assert result.success
    
    processor = VideoProcessor(ProcessingConfig())
    output = processor.process_video(result.filepath)
    assert output.exists()
```

#### Parametrized Tests

```python
@pytest.mark.parametrize("quality,expected", [
    ("720p", 720),
    ("1080p", 1080),
    ("best", None),
])
def test_quality_parsing(quality, expected):
    """Test quality string parsing."""
    assert parse_quality(quality) == expected

@pytest.mark.parametrize("invalid_url", [
    "not_a_url",
    "http://",
    "",
    "ftp://invalid.com",
])
def test_invalid_urls(invalid_url):
    """Test handling of invalid URLs."""
    with pytest.raises(ValidationError):
        validate_url(invalid_url)
```

### Mocking

```python
def test_download_with_mock(mocker):
    """Test download using mocked yt-dlp."""
    mock_ydl = mocker.patch('yt_dlp.YoutubeDL')
    mock_instance = mock_ydl.return_value.__enter__.return_value
    mock_instance.extract_info.return_value = {
        'title': 'Test Video',
        'duration': 100,
    }
    
    downloader = VideoDownloader(config)
    result = downloader.download()
    
    assert result.success
    mock_instance.extract_info.assert_called_once()
```

### Async Tests

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_download():
    """Test asynchronous download."""
    downloader = AsyncDownloader(config)
    result = await downloader.download()
    assert result.success
```

## Test Coverage

```bash
# Generate coverage report
pytest --cov=downie --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=src/downie
    --cov-report=html
    --cov-report=term-missing
markers =
    slow: marks tests as slow
    integration: marks tests that require external services
```

## Testing Best Practices

1. **Test Organization**
   - One test file per module
   - Clear test class/function names
   - Logical test grouping

2. **Testing Patterns**
   - Arrange-Act-Assert pattern
   - Given-When-Then structure
   - Test one thing per test

3. **Fixtures**
   - Keep fixtures focused
   - Use appropriate scope
   - Clean up resources

4. **Mocking**
   - Mock external services
   - Use appropriate mock levels
   - Verify mock calls

5. **Error Testing**
   - Test error conditions
   - Verify error messages
   - Check exception types

## Performance Testing

```python
@pytest.mark.slow
def test_download_performance(downloader):
    """Test download performance."""
    start_time = time.time()
    result = downloader.download()
    duration = time.time() - start_time
    
    assert duration < 300  # Max 5 minutes
    assert result.success
```

## Security Testing

```python
def test_path_traversal():
    """Test path traversal prevention."""
    config = DownloadConfig(
        output_path="../unsafe"
    )
    with pytest.raises(SecurityError):
        VideoDownloader(config)

def test_url_validation():
    """Test URL validation security."""
    with pytest.raises(ValidationError):
        validate_url("file:///etc/passwd")
```

## Test Data

```python
# test_data.py
TEST_VIDEOS = [
    {
        'url': 'https://example.com/video1',
        'title': 'Test Video 1',
        'duration': 100,
    },
    {
        'url': 'https://example.com/video2',
        'title': 'Test Video 2',
        'duration': 200,
    },
]

## Test Data Management

### Sample Data Files
```python
# tests/data/sample_config.yaml
download:
  output_dir: "tests/output"
  quality: "1080p"

# tests/data/test_urls.txt
https://youtube.com/watch?v=test1
https://youtube.com/watch?v=test2

# Usage in tests
def load_test_data():
    """Load test data from files."""
    with open("tests/data/test_urls.txt") as f:
        urls = f.read().splitlines()
    return urls

@pytest.fixture
def test_urls():
    """Fixture for test URLs."""
    return load_test_data()
```

### Test Constants
```python
# tests/constants.py
TEST_URLS = {
    'valid': [
        'https://youtube.com/watch?v=test1',
        'https://vimeo.com/test2',
    ],
    'invalid': [
        'not_a_url',
        'ftp://invalid.com',
    ]
}

TEST_VIDEO_INFO = {
    'title': 'Test Video',
    'duration': 100,
    'formats': [
        {'format_id': '22', 'ext': 'mp4', 'height': 720},
        {'format_id': '18', 'ext': 'mp4', 'height': 360},
    ]
}
```

## Test Documentation

### Docstring Format
```python
def test_download_with_options(self, downloader):
    """
    Test video download with custom options.
    
    This test verifies that:
    1. Custom quality options are respected
    2. Output path is correctly used
    3. Download progress is reported
    4. Metadata is correctly extracted
    
    Test setup:
    - Creates temporary directory
    - Configures downloader with custom options
    
    Expected results:
    - Download completes successfully
    - File is saved to specified location
    - Quality matches requested quality
    """
    result = downloader.download()
    assert result.success
```

## Test Debugging

### Debug Helpers
```python
@pytest.fixture
def debug_logger():
    """Setup debug logging for tests."""
    import logging
    logger = logging.getLogger('downie')
    logger.setLevel(logging.DEBUG)
    return logger

def test_with_debugging(debug_logger):
    """Test with debug logging enabled."""
    debug_logger.debug("Starting test...")
    # Test code here
    debug_logger.debug("Test complete")
```

### Troubleshooting Tests
```python
def test_with_print(capsys):
    """Test with output capture."""
    print("Debug info")
    # Test code here
    captured = capsys.readouterr()
    print(captured.out)  # Debug output

@pytest.mark.skip(reason="Debugging specific issue")
def test_problematic():
    """Temporarily skip problematic test."""
    pass
```

## Continuous Integration

### GitHub Actions Configuration
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Run tests
      run: |
        pytest --cov=downie
```