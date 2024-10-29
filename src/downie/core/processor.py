# src/downie/core/processor.py
import logging
from pathlib import Path
from typing import Any, Dict, Tuple

import ffmpeg

from ..exceptions.errors import ProcessingError
from ..models.config import ProcessingConfig
from ..utils.ffmpeg import validate_ffmpeg_installation

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self._validate_setup()

    def _get_video_info(self, file: Path) -> Dict:
        """Extract video information using ffprobe."""
        try:
            info = ffmpeg.probe(str(file))
            # Get the first video stream
            video_stream = next(
                stream for stream in info["streams"] if stream["codec_type"] == "video"
            )

            # Calculate fps from r_frame_rate
            if "r_frame_rate" in video_stream:
                num, den = map(int, video_stream["r_frame_rate"].split("/"))
                video_stream["fps"] = num // den  # Integer division for fps

            return video_stream
        except ffmpeg.Error as e:
            raise ProcessingError(f"Failed to get video info: {e.stderr.decode()}")
        except (KeyError, StopIteration):
            raise ProcessingError("No video stream found in file")

    def _validate_codecs(self) -> bool:
        """Validate video and audio codec support."""
        from ..utils.ffmpeg import check_codec_support

        if self.config.video_codec and not check_codec_support(self.config.video_codec):
            raise ProcessingError(f"Unsupported video codec: {self.config.video_codec}")

        if self.config.audio_codec and not check_codec_support(self.config.audio_codec):
            raise ProcessingError(f"Unsupported audio codec: {self.config.audio_codec}")

        return True

    def _validate_setup(self) -> None:
        """Validate FFmpeg installation and configuration."""
        if not validate_ffmpeg_installation():
            raise ProcessingError("FFmpeg is not installed or not accessible")

    def _validate_crop(self, crop_str: str) -> Tuple[int, int, int, int]:
        """Validate and parse crop parameters."""
        if not crop_str or not isinstance(crop_str, str):
            raise ProcessingError("Invalid crop format")

        parts = crop_str.split(":")
        if len(parts) != 4:
            raise ProcessingError("Invalid crop format")

        try:
            w, h, x, y = map(int, parts)
            return w, h, x, y
        except ValueError:
            raise ProcessingError("Invalid crop values")

    def _validate_resize(self, resize_str: str) -> Tuple[int, int]:
        """Validate and parse resize parameters."""
        if not resize_str or not isinstance(resize_str, str) or "x" not in resize_str:
            raise ProcessingError("Invalid resize format")

        try:
            w, h = map(int, resize_str.split("x"))
            return w, h
        except ValueError:
            raise ProcessingError("Invalid resize values")

    def process_video(self, input_path: Path) -> Path:
        """Process video according to configuration."""
        try:
            if not input_path.exists():
                raise ProcessingError(f"Input file not found: {input_path}")

            output_path = self._get_output_path(input_path)
            stream = ffmpeg.input(str(input_path))

            # Apply filters in sequence
            if self.config.crop:
                # Validate and get crop parameters
                w, h, x, y = self._validate_crop(self.config.crop)
                stream = stream.filter("crop", w, h, x, y)

            if self.config.resize:
                # Validate and get resize parameters
                w, h = self._validate_resize(self.config.resize)
                stream = stream.filter("scale", w, h)

            if self.config.fps:
                stream = stream.filter("fps", fps=self.config.fps)

            if self.config.hdr_to_sdr:
                stream = (
                    stream.filter("zscale", t="linear", npl=100)
                    .filter("format", pix_fmt="gbrp")
                    .filter("zscale", p="bt709")
                    .filter("tonemap", tonemap="hable")
                    .filter("zscale", t="bt709", m="bt709", r="tv")
                )

            # Get output arguments
            output_args = self._get_output_args()

            # Create output stream
            stream = ffmpeg.output(stream, str(output_path), **output_args)

            # Run FFmpeg
            logger.info(f"Processing video: {input_path.name}")
            ffmpeg.run(
                stream, overwrite_output=True, capture_stdout=True, capture_stderr=True
            )

            return output_path

        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if hasattr(e, "stderr") else str(e)
            raise ProcessingError(f"FFmpeg error: {error_msg}")

    def _apply_video_filters(self, stream) -> ffmpeg.Stream:
        """Apply video filters based on configuration."""
        filters = []

        # Crop
        if self.config.crop:
            try:
                w, h, x, y = map(int, self.config.crop.split(":"))
                filters.append(f"crop={w}:{h}:{x}:{y}")
            except ValueError:
                raise ProcessingError("Invalid crop format. Use width:height:x:y")

        # Resize
        if self.config.resize:
            try:
                w, h = map(int, self.config.resize.split("x"))
                filters.append(f"scale={w}:{h}")
            except ValueError:
                raise ProcessingError("Invalid resize format. Use widthxheight")

        # Rotate
        if self.config.rotate:
            if self.config.rotate not in [90, 180, 270]:
                raise ProcessingError("Rotation must be 90, 180, or 270 degrees")
            filters.append(f"rotate={self.config.rotate}")

        # FPS
        if self.config.fps:
            stream = stream.filter("fps", fps=self.config.fps)

        # Stabilization
        if self.config.stabilize:
            filters.extend(
                [
                    "vidstabdetect=shakiness=10:accuracy=15:result=transforms.trf",
                    "vidstabtransform=input=transforms.trf:zoom=1:smoothing=30",
                ]
            )

        # Denoising
        if self.config.denoise:
            filters.append("nlmeans")

        # HDR to SDR conversion
        if self.config.hdr_to_sdr:
            filters.extend(
                [
                    "zscale=t=linear:npl=100",
                    "format=gbrp",
                    "zscale=p=bt709",
                    "tonemap=tonemap=hable",
                    "zscale=t=bt709:m=bt709:r=tv",
                ]
            )

        # Apply all filters
        if filters:
            stream = stream.filter_multi_output(*filters)

        return stream

    def _handle_audio(self, stream) -> ffmpeg.Stream:
        """Handle audio processing based on configuration."""
        if self.config.remove_audio:
            return stream.audio(None)

        if self.config.extract_audio:
            output_args = {
                "acodec": (
                    "copy"
                    if self.config.audio_codec == "copy"
                    else self.config.audio_codec
                )
            }
            if self.config.audio_bitrate:
                output_args["b:a"] = self.config.audio_bitrate
            return stream.output(audio_only=True, **output_args)

        return stream

    def _get_output_args(self) -> Dict[str, Any]:
        """Get FFmpeg output arguments."""
        args = {}

        if self.config.video_codec:
            args["vcodec"] = self.config.video_codec

        if self.config.video_bitrate:
            args["b:v"] = self.config.video_bitrate

        if self.config.audio_bitrate:
            args["b:a"] = self.config.audio_bitrate

        return args

    def _get_output_path(self, input_path: Path) -> Path:
        """Generate output path for processed video."""
        suffix = input_path.suffix
        stem = input_path.stem

        if self.config.extract_audio:
            suffix = f".{self.config.audio_format}"

        output_path = input_path.with_name(f"{stem}_processed{suffix}")

        # Ensure unique filename
        counter = 1
        while output_path.exists():
            output_path = input_path.with_name(f"{stem}_processed_{counter}{suffix}")
            counter += 1

        return output_path
