# tests/test_cli.py
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from downie.cli import download, subtitle

class TestCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_downloader(self):
        with patch('downie.cli.download.VideoDownloader') as mock:
            instance = Mock()
            instance.download.return_value = Mock(
                success=True,
                filepath="test.mp4",
                download_time=1.5,
                filesize=1024*1024
            )
            mock.return_value = instance
            yield mock

    @pytest.fixture
    def mock_subtitle_downloader(self):
        with patch('downie.cli.subtitle.SubtitleDownloader') as mock:
            instance = Mock()
            instance.download.return_value = [
                Mock(name="subtitle1.srt"),
                Mock(name="subtitle2.srt")
            ]
            mock.return_value = instance
            yield mock

    @pytest.mark.cli
    def test_download_command(self, runner, mock_downloader):
        """Test basic download command."""
        result = runner.invoke(download.download, 
            ['https://youtube.com/watch?v=bXERzEafjIU'])
        assert result.exit_code == 0
        mock_downloader.assert_called_once()

    @pytest.mark.cli
    def test_subtitle_command(self, runner, mock_subtitle_downloader):
        """Test subtitle download command."""
        result = runner.invoke(subtitle.download, 
            ['https://youtube.com/watch?v=bXERzEafjIU'])
        assert result.exit_code == 0
        mock_subtitle_downloader.assert_called_once()

    @pytest.mark.cli
    @pytest.mark.parametrize("option,value", [
        ('--quality', '1080p'),
        ('--format', '22'),
        ('--proxy', 'http://proxy:8080'),
        ('--limit-speed', '1M'),
    ])
    def test_download_options(self, runner, mock_downloader, option, value):
        """Test various download command options."""
        result = runner.invoke(download.download, 
            ['https://youtube.com/watch?v=bXERzEafjIU', option, value])
        assert result.exit_code == 0
        mock_downloader.assert_called_once()