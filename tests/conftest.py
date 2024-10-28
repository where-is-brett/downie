# tests/conftest.py
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def sample_video(temp_dir):
    """Create a sample video file for testing."""
    video_path = temp_dir / "sample.mp4"
    # Create a minimal valid MP4 file
    with open(video_path, 'wb') as f:
        f.write(bytes.fromhex('00000018667479706D703432'))
    return video_path

@pytest.fixture
def sample_subtitle(temp_dir):
    """Create a sample SRT subtitle file for testing."""
    subtitle_path = temp_dir / "sample.srt"
    content = """1
00:00:01,000 --> 00:00:04,000
This is a sample subtitle
For testing purposes

2
00:00:05,000 --> 00:00:08,000
Second subtitle entry
Multiple lines
"""
    subtitle_path.write_text(content, encoding='utf-8')
    return subtitle_path

@pytest.fixture
def mock_response():
    """Create a mock video info response."""
    return {
        'title': 'Test Video',
        'duration': 100,
        'upload_date': '20240101',
        'uploader': 'Test Channel',
        'view_count': 1000,
        'like_count': 100,
        'description': 'Test Description',
        'formats': [{
            'format_id': '22',
            'ext': 'mp4',
            'width': 1920,
            'height': 1080,
            'fps': 30,
            'vcodec': 'h264',
            'acodec': 'aac',
            'filesize': 1024*1024
        }]
    }