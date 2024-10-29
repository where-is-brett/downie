import os
import subprocess
import time

import pytest

from downie.core.downloader import VideoDownloader
from downie.core.processor import VideoProcessor
from downie.models.config import DownloadConfig, ProcessingConfig


class TestPerformance:
    @pytest.fixture
    def sample_video(self, temp_dir):  # Add temp_dir as a parameter
        """Create a sample video for testing."""
        video_path = temp_dir / "sample.mp4"

        # Create a test video using ffmpeg
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-f",
                    "lavfi",
                    "-i",
                    "testsrc=duration=1:size=1280x720:rate=30",
                    "-f",
                    "lavfi",
                    "-i",
                    "aevalsrc=0:duration=1",
                    "-c:v",
                    "libx264",
                    "-c:a",
                    "aac",
                    str(video_path),
                ],
                check=True,
                capture_output=True,
            )

            return video_path
        except subprocess.CalledProcessError as e:
            pytest.skip(f"Failed to create test video: {e.stderr.decode()}")

    @pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true",
        reason="Skip download test in GitHub Actions due to bot check",
    )
    def test_download_performance(self, temp_dir):
        """Test download performance."""
        test_url = "https://www.youtube.com/watch?v=bXERzEafjIU"
        config = DownloadConfig(url=test_url, output_path=temp_dir, quality="1080p")

        downloader = VideoDownloader(config)
        start_time = time.time()
        result = downloader.download()
        duration = time.time() - start_time

        assert duration < 300  # Should complete within 5 minutes
        assert result.success

    @pytest.mark.slow
    def test_processing_performance(self, temp_dir, sample_video):
        """Test video processing performance."""
        if not sample_video.exists():
            pytest.skip("Sample video not available")

        config = ProcessingConfig(
            resize="1280x720", fps=30, video_codec="libx264", audio_codec="aac"
        )

        processor = VideoProcessor(config)
        start_time = time.time()
        result = processor.process_video(sample_video)
        duration = time.time() - start_time

        assert duration < 600  # Should complete within 10 minutes
        assert result.exists()
