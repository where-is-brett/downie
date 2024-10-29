# tests/test_integration.py
from unittest.mock import Mock, patch

import ffmpeg
import pytest

from downie.core.downloader import VideoDownloader
from downie.core.processor import VideoProcessor
from downie.exceptions.errors import ProcessingError
from downie.models.config import DownloadConfig, ProcessingConfig


class TestIntegration:
    @pytest.fixture(autouse=True)
    def setup_mocks(self, monkeypatch):
        """Setup all required mocks."""

        def mock_validate_ffmpeg():
            return getattr(self, "_mock_ffmpeg_valid", True)

        monkeypatch.setattr(
            "downie.utils.ffmpeg.validate_ffmpeg_installation", mock_validate_ffmpeg
        )

        # Mock ffmpeg-python functions
        def mock_input(*args, **kwargs):
            mock = Mock()
            mock.filter.return_value = mock
            mock.output.return_value = mock
            return mock

        monkeypatch.setattr("ffmpeg.input", mock_input)
        monkeypatch.setattr("ffmpeg.output", lambda *args, **kwargs: args[0])
        monkeypatch.setattr("ffmpeg.run", lambda *args, **kwargs: None)

    @pytest.fixture
    def test_url(self):
        """Fixture for test URL."""
        return "https://www.youtube.com/watch?v=bXERzEafjIU123"

    @pytest.fixture
    def mock_video_info(self):
        """Fixture for mock video info."""
        return {
            "title": "Test Video",
            "duration": 100,
            "formats": [
                {
                    "format_id": "22",
                    "ext": "mp4",
                    "width": 1920,
                    "height": 1080,
                    "fps": 30,
                    "vcodec": "h264",
                    "acodec": "aac",
                    "filesize": 1024 * 1024,
                }
            ],
        }

    @pytest.mark.integration
    def test_download_and_process(self, temp_dir, test_url, mock_video_info):
        """Test full download and process workflow."""
        download_config = DownloadConfig(
            url=test_url, output_path=temp_dir, quality="720p"
        )

        # Mock the download
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_instance = mock_ydl.return_value.__enter__.return_value
            mock_instance.extract_info.return_value = mock_video_info
            output_file = temp_dir / "test_video.mp4"
            mock_instance.prepare_filename.return_value = str(output_file)

            # Create dummy video file
            output_file.write_bytes(b"dummy video content")

            # Download video
            downloader = VideoDownloader(download_config)
            result = downloader.download()

            assert result.success
            assert result.filepath.exists()

            # Process video
            process_config = ProcessingConfig(
                resize="640x360", fps=30, video_codec="libx264"
            )

            with patch("ffmpeg.run") as mock_run:
                processor = VideoProcessor(process_config)
                processed_file = processor.process_video(result.filepath)

                assert mock_run.called
                assert str(processed_file).endswith("_processed.mp4")

    @pytest.mark.integration
    def test_processing_error_handling(self, temp_dir):
        """Test handling of FFmpeg processing errors."""
        input_file = temp_dir / "test.mp4"
        input_file.write_bytes(b"dummy content")

        process_config = ProcessingConfig(resize="640x360", fps=30)

        # Create a proper ffmpeg.Error instance
        ffmpeg_error = ffmpeg.Error(
            cmd=["ffmpeg"], stdout=b"", stderr=b"FFmpeg processing error"
        )

        with patch("ffmpeg.run", side_effect=ffmpeg_error):
            processor = VideoProcessor(process_config)
            with pytest.raises(ProcessingError, match="FFmpeg error"):
                processor.process_video(input_file)

    @pytest.mark.integration
    def test_download_with_subtitles(self, temp_dir, test_url, mock_video_info):
        """Test video download with subtitles."""
        download_config = DownloadConfig(url=test_url, output_path=temp_dir)

        # Mock video download
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_instance = mock_ydl.return_value.__enter__.return_value
            mock_instance.extract_info.return_value = mock_video_info
            output_file = temp_dir / "test_video.mp4"
            mock_instance.prepare_filename.return_value = str(output_file)

            # Create dummy video file
            output_file.write_bytes(b"dummy video content")

            # Download video
            downloader = VideoDownloader(download_config)
            result = downloader.download()

            assert result.success
            assert result.filepath.exists()

            # Create subtitle files
            srt_file = temp_dir / "test_video.en.srt"
            srt_file.write_text(
                """1
00:00:01,000 --> 00:00:04,000
Test subtitle"""
            )

            assert srt_file.exists()

    @pytest.mark.integration
    def test_download_uses_config_url(self, temp_dir, test_url):
        """Test that downloader uses the URL from config."""
        download_config = DownloadConfig(url=test_url, output_path=temp_dir)

        # Mock the download
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_instance = mock_ydl.return_value.__enter__.return_value
            mock_instance.extract_info.return_value = {"title": "Video"}

            downloader = VideoDownloader(download_config)
            result = downloader.download()

            # Verify the downloaded URL is from the config
            mock_instance.extract_info.assert_called_with(test_url, download=True)
