# tests/test_processor.py
import subprocess
from unittest.mock import Mock, patch

import pytest

from downie.core.processor import VideoProcessor
from downie.exceptions.errors import ProcessingError
from downie.models.config import ProcessingConfig


class TestVideoProcessor:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test environment."""
        self.temp_dir = tmp_path

    @pytest.fixture
    def sample_video(self):
        """Create a sample video for testing."""
        video_path = self.temp_dir / "test.mp4"

        # Create a test video using ffmpeg
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

    @pytest.fixture
    def sample_processing_config(self):
        return ProcessingConfig(
            crop="1280:720:0:0",
            resize="1280x720",
            fps=30,
            video_codec="libx264",
            audio_codec="aac",
        )

    def test_initialization(self, sample_processing_config):
        """Test processor initialization."""
        processor = VideoProcessor(sample_processing_config)
        assert processor.config == sample_processing_config

    @patch("ffmpeg.probe")
    def test_video_info_extraction(self, mock_probe, temp_dir, sample_video):
        """Test extraction of video information."""
        mock_probe.return_value = {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "r_frame_rate": "30/1",
                }
            ]
        }

        processor = VideoProcessor(ProcessingConfig())
        info = processor._get_video_info(sample_video)

        assert info["width"] == 1920
        assert info["height"] == 1080
        assert info["fps"] == 30

    @pytest.mark.parametrize(
        "crop_value,expected_error",
        [
            ("invalid", "Invalid crop format"),
            ("1280:720", "Invalid crop format"),
            ("1280:720:0", "Invalid crop format"),
            ("abc:def:0:0", "Invalid crop values"),
        ],
    )
    def test_invalid_crop_values(self, crop_value, expected_error):
        """Test handling of invalid crop values."""
        config = ProcessingConfig()  # Create base config first
        processor = VideoProcessor(config)

        with pytest.raises(ProcessingError, match=expected_error):
            processor._validate_crop(crop_value)

    @pytest.mark.parametrize(
        "resize_value,expected_error",
        [
            ("invalid", "Invalid resize format"),
            ("1280", "Invalid resize format"),
            (
                "axb",
                "Invalid resize values",
            ),  # Changed from abc:def to axb to match format
        ],
    )
    def test_invalid_resize_values(self, resize_value, expected_error):
        """Test handling of invalid resize values."""
        config = ProcessingConfig()
        processor = VideoProcessor(config)

        with pytest.raises(ProcessingError, match=expected_error):
            processor._validate_resize(resize_value)

    def test_processing_chain(self, sample_video):
        """Test multiple processing operations in sequence."""
        config = ProcessingConfig(
            crop="1280:720:0:0", resize="640x360", fps=30, rotate=90
        )
        processor = VideoProcessor(config)

        mock_stream = Mock()
        with patch("ffmpeg.input", return_value=mock_stream) as mock_input, patch(
            "ffmpeg.output"
        ) as mock_output, patch("ffmpeg.run") as mock_run:

            # Setup mock chain
            mock_stream.filter.return_value = mock_stream
            mock_output.return_value = mock_stream

            output = processor.process_video(sample_video)

            # Verify filter chain
            crop_call = mock_stream.filter.call_args_list[0]
            assert crop_call[0][0] == "crop"
            assert crop_call[0][1:] == (1280, 720, 0, 0)

            scale_call = mock_stream.filter.call_args_list[1]
            assert scale_call[0][0] == "scale"
            assert scale_call[0][1:] == (640, 360)

            fps_call = mock_stream.filter.call_args_list[2]
            assert fps_call[0][0] == "fps"
            assert fps_call[1] == {"fps": 30}

    def test_hdr_to_sdr_conversion(self, sample_video):
        """Test HDR to SDR conversion settings."""
        config = ProcessingConfig(hdr_to_sdr=True)
        processor = VideoProcessor(config)

        mock_stream = Mock()
        with patch("ffmpeg.input", return_value=mock_stream) as mock_input, patch(
            "ffmpeg.output"
        ) as mock_output, patch("ffmpeg.run") as mock_run:

            # Setup mock chain
            mock_stream.filter.return_value = mock_stream
            mock_output.return_value = mock_stream

            processor.process_video(sample_video)

            # Verify HDR to SDR filter chain
            filter_calls = mock_stream.filter.call_args_list

            # Test each filter call individually
            assert filter_calls[0][0][0] == "zscale"
            assert filter_calls[0][1] == {"t": "linear", "npl": 100}

            assert filter_calls[1][0][0] == "format"
            assert filter_calls[1][1] == {"pix_fmt": "gbrp"}

            assert filter_calls[2][0][0] == "zscale"
            assert filter_calls[2][1] == {"p": "bt709"}

    @patch("downie.utils.ffmpeg.check_codec_support")
    def test_codec_validation(self, mock_check_codec, temp_dir):
        """Test validation of video and audio codecs."""
        mock_check_codec.side_effect = lambda x: x in ["libx264", "aac"]

        # Valid codecs
        config = ProcessingConfig(video_codec="libx264", audio_codec="aac")
        processor = VideoProcessor(config)
        assert processor._validate_codecs()

        # Invalid video codec
        config = ProcessingConfig(video_codec="invalid", audio_codec="aac")
        processor = VideoProcessor(config)
        with pytest.raises(ProcessingError, match="Unsupported video codec"):
            processor._validate_codecs()

    def test_output_filename_generation(self, temp_dir):
        """Test generation of output filenames."""
        processor = VideoProcessor(ProcessingConfig())

        # Test basic filename
        input_path = temp_dir / "test.mp4"
        output_path = processor._get_output_path(input_path)
        assert output_path.name == "test_processed.mp4"

        # Test when file exists
        output_path.touch()
        new_output_path = processor._get_output_path(input_path)
        assert new_output_path.name == "test_processed_1.mp4"
