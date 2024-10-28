# tests/test_downloader.py
import pytest
from unittest.mock import Mock, patch
from downie.core.downloader import VideoDownloader
from downie.models.config import DownloadConfig
from downie.exceptions.errors import ValidationError

class TestVideoDownloader:
    @pytest.fixture
    def valid_url(self):
        return "https://www.youtube.com/watch?v=bXERzEafjIU"

    def test_initialization_with_custom_settings(self, temp_dir, valid_url):
        """Test downloader initialization with custom settings."""
        config = DownloadConfig(
            url=valid_url,
            output_path=temp_dir,
            quality="720p",
            format_id="22",
            proxy="http://proxy:8080",
            limit_speed="1M"
        )
        downloader = VideoDownloader(config)
        assert downloader.config.quality == "720p"
        assert downloader.ydl_opts['ratelimit'] == 1024 * 1024  # 1M in bytes

    @pytest.mark.parametrize("url", [
        "not_a_url",
        "http://",
        "",
        "ftp://invalid.com",
        "https://examplecomvideo"  
    ])
    def test_invalid_urls(self, temp_dir, url):
        """Test handling of invalid URLs."""
        config = DownloadConfig(url=url, output_path=temp_dir)
        with pytest.raises(ValidationError):
            VideoDownloader(config)

    @patch('yt_dlp.YoutubeDL')
    def test_successful_download(self, mock_ydl, temp_dir, valid_url, mock_response):
        """Test successful video download."""
        config = DownloadConfig(
            url=valid_url,
            output_path=temp_dir
        )
        
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = mock_response
        output_file = temp_dir / "test_video.mp4"
        mock_ydl_instance.prepare_filename.return_value = str(output_file)
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

        # Create the output file to simulate successful download
        output_file.touch()

        downloader = VideoDownloader(config)
        result = downloader.download()

        assert result.success
        assert result.metadata.title == "Test Video"
        assert result.filepath == output_file

    @patch('yt_dlp.YoutubeDL')
    def test_download_with_rate_limit(self, mock_ydl, temp_dir, valid_url):
        """Test download with rate limiting."""
        config = DownloadConfig(
            url=valid_url,
            output_path=temp_dir,
            limit_speed="1M"
        )
        downloader = VideoDownloader(config)
        assert downloader.ydl_opts['ratelimit'] == 1024 * 1024  # 1M in bytes

    @patch('yt_dlp.YoutubeDL')
    def test_retry_mechanism(self, mock_ydl, temp_dir, valid_url, mock_response):
        """Test download retry mechanism."""
        config = DownloadConfig(
            url=valid_url,
            output_path=temp_dir,
            retries=3
        )
        downloader = VideoDownloader(config)
        
        mock_instance = Mock()
        mock_instance.extract_info.side_effect = [
            Exception("First try"),
            mock_response  # Succeeds on second try
        ]
        mock_ydl.return_value.__enter__.return_value = mock_instance
        output_file = temp_dir / "test_video.mp4"
        mock_instance.prepare_filename.return_value = str(output_file)
        output_file.touch()  # Create the file to simulate successful download
        
        result = downloader.download()
        assert result.success

    @pytest.mark.parametrize("limit,expected", [
        ("1M", 1024 * 1024),        # 1M = 1,048,576 bytes
        ("500K", 500 * 1024),       # 500K = 512,000 bytes
        ("1.5M", int(1.5 * 1024 * 1024)),  # 1.5M = 1,572,864 bytes
        ("2G", 2 * 1024 * 1024 * 1024),    # 2G = 2,147,483,648 bytes
    ])
    def test_rate_limit_parsing(self, temp_dir, valid_url, limit, expected):
        """Test parsing of rate limit values."""
        config = DownloadConfig(
            url=valid_url,
            output_path=temp_dir,
            limit_speed=limit
        )
        downloader = VideoDownloader(config)
        assert downloader.ydl_opts['ratelimit'] == expected, f"Failed for {limit}"

    @pytest.mark.parametrize("invalid_limit", [
        "1X",       # Invalid unit
        "M",        # Missing number
        "1.2.3M",   # Invalid number format
        "-1M",      # Negative value
        "very fast" # Invalid format
    ])
    def test_invalid_rate_limits(self, temp_dir, valid_url, invalid_limit):
        """Test handling of invalid rate limit values."""
        config = DownloadConfig(
            url=valid_url,
            output_path=temp_dir,
            limit_speed=invalid_limit
        )
        with pytest.raises(ValidationError):
            VideoDownloader(config)