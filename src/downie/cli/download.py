# src/downie/cli/download.py
from pathlib import Path

import click

from downie.exceptions.errors import UnsupportedPlatformError

from ..core.downloader import VideoDownloader
from ..logging.logger import get_logger
from ..models.config import DownloadConfig, ProcessingConfig
from ..utils.validation import validate_url

logger = get_logger(__name__)


@click.group()
def cli():
    """Video downloading commands

    Download videos from supported platforms with various options for quality,
    format, and processing.

    Basic Usage:
      downie video download URL [options]

    Example:
      downie video download "https://example.com/video" -q 1080p -o ~/Downloads
    """
    pass


@cli.command()
@click.argument("url")
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default="downloads",
    help="Output directory for downloaded files",
)
@click.option(
    "-q", "--quality", default="best", help="Video quality (e.g., 720p, 1080p, best)"
)
@click.option("-f", "--format", "format_id", help="Specific format ID to download")
@click.option("--proxy", help="Proxy URL")
@click.option("--limit-speed", help="Download speed limit (e.g., 1M, 500K)")
@click.option("--username", help="Account username")
@click.option("--password", help="Account password")
@click.option(
    "--cookies_file", type=click.Path(exists=True), help="Path to cookies file"
)
@click.option("--process/--no-process", default=False, help="Enable video processing")
@click.option("--crop", help="Crop video (width:height:x:y)")
@click.option("--resize", help="Resize video (widthxheight)")
@click.option("--rotate", type=int, help="Rotate video (degrees)")
@click.option("--fps", type=int, help="Target FPS")
@click.option("--remove-audio/--keep-audio", default=False, help="Remove audio track")
@click.option(
    "--extract-audio/--no-extract-audio", default=False, help="Extract audio only"
)
@click.option("--audio-format", default="mp3", help="Audio format for extraction")
@click.option("--video-codec", help="Video codec (e.g., libx264, libx265)")
@click.option("--audio-codec", help="Audio codec (e.g., aac, mp3)")
@click.option("--video-bitrate", help="Video bitrate (e.g., 5M)")
@click.option("--audio-bitrate", help="Audio bitrate (e.g., 192k)")
def download(url, **kwargs):
    """Download video from URL

    Arguments:
        URL  The video URL to download from

    Quality Options:
        -q, --quality    Video quality (720p, 1080p, best)
        -f, --format     Specific format ID to download

    Output Options:
        -o, --output     Output directory (default: downloads)

    Processing Options:
        --process        Enable video processing
        --resize        Resize video (widthxheight)
        --crop          Crop video (width:height:x:y)
        --rotate        Rotate video (degrees)
        --fps           Target FPS

    Network Options:
        --proxy         Proxy URL
        --limit-speed   Download speed limit (e.g., 1M, 500K)

    Authentication:
        --username      Account username
        --password      Account password
        --cookies_file  Path to cookies file

    Audio Options:
        --extract-audio  Extract audio only
        --audio-format   Audio format for extraction (default: mp3)
        --audio-codec    Audio codec (e.g., aac, mp3)
        --audio-bitrate  Audio bitrate (e.g., 192k)
        --remove-audio   Remove audio track

    Video Options:
        --video-codec    Video codec (e.g., libx264, libx265)
        --video-bitrate  Video bitrate (e.g., 5M)

    Examples:
        # Download in best quality
        downie video download "https://example.com/video"

        # Download 1080p to specific directory
        downie video download "https://example.com/video" -q 1080p -o ~/Downloads

        # Download and process video
        downie video download "https://example.com/video" --process --resize 1280x720

        # Extract audio only
        downie video download "https://example.com/video" --extract-audio
    """
    try:
        if not validate_url(url):
            raise click.BadParameter(f"Invalid URL: {url}")

        # Prepare ProcessingConfig if processing is enabled
        process_enabled = kwargs.pop("process", False)
        processing_config = None
        if process_enabled:
            processing_config = ProcessingConfig(
                crop=kwargs.pop("crop", None),
                resize=kwargs.pop("resize", None),
                rotate=kwargs.pop("rotate", None),
                fps=kwargs.pop("fps", None),
                remove_audio=kwargs.pop("remove_audio", False),
                extract_audio=kwargs.pop("extract_audio", False),
                audio_format=kwargs.pop("audio_format", "mp3"),
                video_codec=kwargs.pop("video_codec", "libx264"),
                audio_codec=kwargs.pop("audio_codec", "aac"),
                video_bitrate=kwargs.pop("video_bitrate", None),
                audio_bitrate=kwargs.pop("audio_bitrate", None),
            )

        # Prepare main config
        config = DownloadConfig(
            url=url,
            output_path=Path(kwargs.pop("output", "downloads")),
            quality=kwargs.pop("quality", "best"),
            format_id=kwargs.pop("format_id", None),
            processing=processing_config,
            proxy=kwargs.pop("proxy", None),
            limit_speed=kwargs.pop("limit_speed", None),
            username=kwargs.pop("username", None),
            password=kwargs.pop("password", None),
            cookies_file=kwargs.pop("cookies_file", None),
        )

        # Initialize and run downloader
        downloader = VideoDownloader(config)
        result = downloader.download()

        if result.success:
            # If processing is enabled, process the video
            if process_enabled and processing_config:
                from ..core.processor import VideoProcessor

                click.echo("Processing video...")
                processor = VideoProcessor(processing_config)
                processed_path = processor.process_video(result.filepath)
                click.echo(
                    click.style(f"Processing successful: {processed_path}", fg="green")
                )
                # Update result filepath to processed file
                result.filepath = processed_path

            click.echo(
                click.style(f"Download successful: {result.filepath}", fg="green")
            )
            click.echo(f"Download time: {result.download_time:.1f}s")
            click.echo(f"File size: {result.filesize / 1024 / 1024:.1f}MB")
        else:
            if isinstance(result.error, UnsupportedPlatformError):
                click.echo(
                    click.style(
                        f"Unsupported platform: {result.error}",
                        fg="yellow",  # Use yellow for unsupported rather than red for error
                    )
                )
            else:
                click.echo(click.style(f"Download failed: {result.error}", fg="red"))

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
        raise click.Abort()
