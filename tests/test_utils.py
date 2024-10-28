# tests/test_utils.py
import pytest
from downie.utils import ffmpeg, filesystem
import subprocess

class TestFFmpegUtils:
    @pytest.fixture
    def sample_video(self, temp_dir):
        """Create a valid sample video file for testing."""
        video_path = temp_dir / "sample.mp4"
        
        # Create a 1-second test video using ffmpeg
        subprocess.run([
            'ffmpeg',
            '-f', 'lavfi',  # Use the lavfi input virtual device
            '-i', 'testsrc=duration=1:size=1280x720:rate=30',  # Create test pattern
            '-f', 'lavfi',
            '-i', 'sine=frequency=1000:duration=1',  # Create test audio
            '-c:v', 'libx264',
            '-c:a', 'aac',
            str(video_path)
        ], capture_output=True)
        
        return video_path

    @pytest.mark.utils
    def test_ffmpeg_installation(self):
        """Test FFmpeg installation check."""
        assert ffmpeg.validate_ffmpeg_installation()

    @pytest.mark.utils
    def test_codec_support(self):
        """Test codec support checking."""
        assert ffmpeg.check_codec_support('libx264')
        assert not ffmpeg.check_codec_support('nonexistent_codec')

    @pytest.mark.utils
    def test_video_info(self, sample_video):
        """Test video information extraction."""
        info = ffmpeg.get_video_info(sample_video)
        
        # Verify basic video information
        assert 'streams' in info
        assert 'format' in info
        
        # Find video stream
        video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
        assert video_stream is not None
        assert video_stream['width'] == 1280
        assert video_stream['height'] == 720
        
        # Find audio stream
        audio_stream = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
        assert audio_stream is not None

class TestFilesystemUtils:
    @pytest.mark.utils
    def test_checksum(self, sample_video):
        """Test file checksum calculation."""
        checksum = filesystem.calculate_checksum(sample_video)
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA-256 length

    @pytest.mark.utils
    def test_file_rotation(self, temp_dir):
        """Test file rotation functionality."""
        # Create test files
        for i in range(5):
            (temp_dir / f"file{i}.txt").write_text("x" * 1000)

        rotator = filesystem.FileRotator(temp_dir, max_size=2000)
        rotator.rotate()

        # Should have removed oldest files to get under max_size
        files = list(temp_dir.glob("*.txt"))
        total_size = sum(f.stat().st_size for f in files)
        assert total_size <= 2000

    @pytest.mark.utils
    def test_empty_directory_cleanup(self, temp_dir):
        """Test cleanup with empty directory."""
        rotator = filesystem.FileRotator(temp_dir, max_size=1000)
        rotator.rotate()  # Should not raise any errors
        assert list(temp_dir.glob("*")) == []