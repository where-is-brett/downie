# tests/test_subtitle.py
import pytest
from unittest.mock import Mock, patch
import shutil
import pysrt
from downie.core.subtitle import SubtitleDownloader
from downie.models.config import SubtitleConfig
from downie.exceptions.errors import SubtitleError

class TestSubtitleDownloader:
    @pytest.fixture
    def sample_srt(self, temp_dir):
        """Create a sample SRT file."""
        content = """1
00:00:01,000 --> 00:00:04,000
First subtitle
Second line

2
00:00:05,000 --> 00:00:08,000
Second subtitle
"""
        file_path = temp_dir / "test.srt"
        file_path.write_text(content, encoding='utf-8')
        return file_path

    @pytest.fixture
    def sample_vtt(self, temp_dir):
        """Create a sample VTT file."""
        content = """WEBVTT

00:00:01.000 --> 00:00:04.000
First subtitle
Second line

00:00:05.000 --> 00:00:08.000
Second subtitle
"""
        file_path = temp_dir / "test.vtt"
        file_path.write_text(content, encoding='utf-8')
        return file_path

    @pytest.fixture
    def sample_formatted_srt(self, temp_dir):
        """Create a sample SRT file with formatting tags."""
        content = """1
00:00:01,000 --> 00:00:04,000
<b>Bold text</b>
<i>Italic text</i>

2
00:00:05,000 --> 00:00:08,000
{y:i}Styled text{y:i}"""
        file_path = temp_dir / "formatted.srt"
        file_path.write_text(content, encoding='utf-8')
        return file_path

    def test_initialization(self, temp_dir):
        """Test subtitle downloader initialization."""
        config = SubtitleConfig(
            url="https://youtube.com/watch?v=test",
            output_path=temp_dir,
            languages=['en']
        )
        downloader = SubtitleDownloader(config)
        assert downloader.config == config
        assert downloader.output_path.exists()

    @patch('yt_dlp.YoutubeDL')
    def test_subtitle_download(self, mock_ydl, temp_dir):
        """Test basic subtitle download functionality."""
        config = SubtitleConfig(
            url="https://youtube.com/watch?v=test",
            output_path=temp_dir,
            languages=['en'],
            formats=['vtt']  # Start with just VTT since that's what YouTube provides
        )

        mock_instance = Mock()
        mock_instance.extract_info.return_value = {
            'title': 'Test Video',
            'subtitles': {
                'en': [{'url': 'http://example.com/sub.vtt'}]
            }
        }
        # Create a mock subtitle file to simulate download
        subtitle_file = temp_dir / "Test Video.en.vtt"
        subtitle_file.write_text("WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nTest subtitle")
        
        mock_instance.prepare_filename.return_value = str(temp_dir / "Test Video.mp4")
        mock_ydl.return_value.__enter__.return_value = mock_instance

        downloader = SubtitleDownloader(config)
        result = downloader.download()

        assert len(result) > 0
        assert all(f.suffix == '.vtt' or f.suffix == '.srt' for f in result)
    
    def test_encoding_fix(self, temp_dir):
        """Test subtitle encoding fix functionality."""
        # Create UTF-16 encoded content
        content = "Test subtitle content"
        file_path = temp_dir / "test.srt"
        file_path.write_bytes(content.encode('utf-16'))

        config = SubtitleConfig(
            url="https://youtube.com/watch?v=test",
            output_path=temp_dir,
            fix_encoding=True
        )
        downloader = SubtitleDownloader(config)
        downloader._fix_encoding(file_path)

        # Verify content can be read as UTF-8
        content = file_path.read_text(encoding='utf-8')
        assert "Test subtitle content" in content

    def test_format_conversion(self, temp_dir, sample_vtt):
        """Test conversion between subtitle formats."""
        config = SubtitleConfig(
            url="https://youtube.com/watch?v=test",
            output_path=temp_dir,
            convert_to_srt=True
        )
        downloader = SubtitleDownloader(config)

        output_file = downloader._convert_to_srt(sample_vtt)

        assert output_file.suffix == '.srt'
        content = output_file.read_text()
        assert '00:00:01,000' in content
        assert 'First subtitle' in content
        assert 'Second subtitle' in content

    def test_subtitle_merge(self, temp_dir):
        """Test merging multiple subtitle files."""
        # Create test files
        files = []
        for i, lang in enumerate(['en', 'es']):
            content = f"""1
00:00:0{i},000 --> 00:00:0{i+1},000
Subtitle in {lang}"""
            file_path = temp_dir / f"sub_{lang}.srt"
            file_path.write_text(content)
            files.append(file_path)

        config = SubtitleConfig(
            url="https://youtube.com/watch?v=test",
            output_path=temp_dir,
            merge_subtitles=True
        )
        downloader = SubtitleDownloader(config)

        result = downloader._merge_subtitles(files)

        assert result.exists()
        content = result.read_text()
        assert 'Subtitle in en' in content
        assert 'Subtitle in es' in content

    @pytest.mark.parametrize("time_offset", [-1.0, 1.0, 2.5])
    def test_time_adjustment(self, temp_dir, sample_srt, time_offset):
        """Test subtitle timing adjustment with different offsets."""
        config = SubtitleConfig(
            url="https://youtube.com/watch?v=test",
            output_path=temp_dir,
            time_offset=time_offset
        )
        downloader = SubtitleDownloader(config)
        
        # Create a subtitle file with known timing
        test_srt = temp_dir / "test_timing.srt"
        test_content = """1
    00:00:01,000 --> 00:00:04,000
    Test subtitle"""
        test_srt.write_text(test_content, encoding='utf-8')
        
        # Apply time offset
        downloader._adjust_subtitle_timing(test_srt, time_offset)
        
        # Read and verify timing
        subs = pysrt.open(str(test_srt))
        
        # Calculate expected milliseconds
        expected_start_ms = max(0, 1000 + round(time_offset * 1000))  # Original 1 second + offset
        actual_start_ms = (subs[0].start.hours * 3600000 + 
                        subs[0].start.minutes * 60000 + 
                        subs[0].start.seconds * 1000 + 
                        subs[0].start.milliseconds)
        
        # Use small tolerance for floating-point arithmetic
        assert abs(actual_start_ms - expected_start_ms) <= 1, \
            f"Expected {expected_start_ms}ms but got {actual_start_ms}ms"
        
        # Verify end time
        expected_end_ms = max(0, 4000 + round(time_offset * 1000))  # Original 4 seconds + offset
        actual_end_ms = (subs[0].end.hours * 3600000 + 
                        subs[0].end.minutes * 60000 + 
                        subs[0].end.seconds * 1000 + 
                        subs[0].end.milliseconds)
        
        assert abs(actual_end_ms - expected_end_ms) <= 1, \
            f"Expected {expected_end_ms}ms but got {actual_end_ms}ms"
    
    def test_format_removal(self, temp_dir, sample_formatted_srt):
        """Test removal of formatting tags."""
        config = SubtitleConfig(
            url="https://youtube.com/watch?v=test",
            output_path=temp_dir,
            remove_formatting=True
        )
        downloader = SubtitleDownloader(config)

        test_file = temp_dir / "test_formatting.srt"
        shutil.copy(sample_formatted_srt, test_file)
        downloader._remove_formatting(test_file)

        content = test_file.read_text()
        assert '<b>' not in content
        assert '<i>' not in content
        assert '{y:i}' not in content
        assert 'Bold text' in content
        assert 'Italic text' in content
        assert 'Styled text' in content

    @patch('yt_dlp.YoutubeDL')
    def test_language_availability(self, mock_ydl, temp_dir):
        """Test checking available subtitle languages."""
        config = SubtitleConfig(
            url="https://youtube.com/watch?v=test",
            output_path=temp_dir
        )

        mock_instance = Mock()
        mock_instance.extract_info.return_value = {
            'subtitles': {
                'en': [{'url': 'http://example.com/en.vtt'}],
                'es': [{'url': 'http://example.com/es.vtt'}]
            },
            'automatic_captions': {
                'fr': [{'url': 'http://example.com/fr.vtt'}]
            }
        }
        mock_ydl.return_value.__enter__.return_value = mock_instance

        downloader = SubtitleDownloader(config)
        available = downloader.list_available_subtitles()

        assert 'en' in available['manual']
        assert 'es' in available['manual']
        assert 'fr' in available['automatic']

    def test_error_handling(self, temp_dir):
        """Test various error scenarios."""
        # Test with completely invalid URL
        config = SubtitleConfig(
            url="invalid://url",
            output_path=temp_dir
        )
        
        with pytest.raises(SubtitleError, match="Invalid URL format"):
            downloader = SubtitleDownloader(config)
            downloader.download()

        # Test with missing file for encoding fix
        config = SubtitleConfig(
            url="https://www.youtube.com/watch?v=test",
            output_path=temp_dir
        )
        downloader = SubtitleDownloader(config)
        nonexistent_file = temp_dir / "nonexistent.srt"
        with pytest.raises(FileNotFoundError):
            downloader._fix_encoding(nonexistent_file)

        # Test with invalid format
        invalid_vtt = temp_dir / "invalid.vtt"
        invalid_vtt.write_text("Invalid content")
        result = downloader._convert_to_srt(invalid_vtt)
        assert result == invalid_vtt  # Should return original file on error

    @pytest.mark.parametrize("format_list,expected_count", [
        (['srt'], 1),
        (['srt', 'vtt'], 2),
        (['srt', 'vtt', 'ass'], 3)
    ])
    def test_multiple_format_download(self, format_list, expected_count, temp_dir):
        """Test downloading subtitles in multiple formats."""
        config = SubtitleConfig(
            url="https://youtube.com/watch?v=test",
            output_path=temp_dir,
            formats=format_list
        )

        with patch('yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = Mock()
            mock_instance.extract_info.return_value = {
                'title': 'Test Video',
                'subtitles': {'en': [{'url': 'http://example.com/sub.vtt'}]}
            }
            mock_instance.prepare_filename.return_value = str(temp_dir / "Test Video.mp4")
            mock_ydl.return_value.__enter__.return_value = mock_instance

            # Simulate yt-dlp creating the subtitle files
            for fmt in format_list:
                subtitle_file = temp_dir / f"Test Video.en.{fmt}"
                subtitle_content = f"WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nTest subtitle in {fmt}"
                subtitle_file.write_text(subtitle_content)

            downloader = SubtitleDownloader(config)
            result = downloader.download()

            assert len(result) == expected_count
            assert all(f.suffix[1:] in format_list for f in result)
    
    def test_download_with_all_options(self, temp_dir, sample_vtt):
        """Test download with all processing options enabled."""
        config = SubtitleConfig(
            url="https://youtube.com/watch?v=test",
            output_path=temp_dir,
            languages=['en'],
            formats=['vtt', 'srt'],
            fix_encoding=True,
            convert_to_srt=True,
            remove_formatting=True,
            time_offset=1.0
        )

        with patch('yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = Mock()
            mock_instance.extract_info.return_value = {
                'title': 'Test Video',
                'subtitles': {'en': [{'url': 'http://example.com/sub.vtt'}]}
            }
            mock_instance.prepare_filename.return_value = str(temp_dir / "Test Video.mp4")
            mock_ydl.return_value.__enter__.return_value = mock_instance

            downloader = SubtitleDownloader(config)
            result = downloader.download()

            assert len(result) > 0
            assert all(file.suffix == '.srt' for file in result)
            for file in result:
                content = file.read_text()
                assert '<b>' not in content
                assert '{y:i}' not in content