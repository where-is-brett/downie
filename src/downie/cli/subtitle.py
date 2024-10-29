# src/downie/cli/subtitle.py
from pathlib import Path

import click

from ..core.subtitle import SubtitleDownloader
from ..logging.logger import get_logger
from ..models.config import SubtitleConfig

logger = get_logger(__name__)


@click.group()
def cli():
    """Subtitle downloading commands

    Download subtitles from supported platforms with options for
    language selection, format conversion, and processing.

    Basic Usage:
      downie subtitle download URL [options]

    Example:
      downie subtitle download "https://example.com/video" -l en,es
    """
    pass


@cli.command()
@click.argument("url")
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default="subtitles",
    help="Output directory for subtitles",
)
@click.option("-l", "--languages", default="en", help="Comma-separated language codes")
@click.option("--formats", default="srt", help="Comma-separated subtitle formats")
@click.option(
    "--auto-generated/--no-auto-generated",
    default=True,
    help="Include auto-generated subtitles",
)
@click.option(
    "--convert-srt/--no-convert-srt",
    default=True,
    help="Convert all subtitles to SRT format",
)
@click.option(
    "--fix-encoding/--no-fix-encoding",
    default=True,
    help="Fix subtitle encoding issues",
)
@click.option("--merge/--no-merge", default=False, help="Merge all subtitle files")
def download(url, **kwargs):
    """Download subtitles from URL

    Arguments:
        URL  The video URL to download subtitles from

    Language Options:
        -l, --languages    Comma-separated language codes (default: en)
        --auto-generated   Include auto-generated subtitles

    Output Options:
        -o, --output      Output directory (default: subtitles)
        --formats         Comma-separated subtitle formats (default: srt)

    Processing Options:
        --convert-srt     Convert all subtitles to SRT format
        --fix-encoding    Fix subtitle encoding issues
        --merge          Merge all subtitle files into one

    Examples:
        # Download English subtitles
        downie subtitle download "https://example.com/video"

        # Download multiple languages
        downie subtitle download "https://example.com/video" -l "en,es,fr"

        # Download and convert to SRT
        downie subtitle download "https://example.com/video" --convert-srt
    """
    try:
        config = SubtitleConfig(
            url=url,
            output_path=Path(kwargs.pop("output")),
            languages=kwargs.pop("languages").split(","),
            formats=kwargs.pop("formats").split(","),
            auto_generated=kwargs.pop("auto_generated", True),
            convert_to_srt=kwargs.pop("convert_srt"),
            fix_encoding=kwargs.pop("fix_encoding", True),
            merge_subtitles=kwargs.pop("merge", False),
        )

        downloader = SubtitleDownloader(config)
        subtitle_files = downloader.download()

        if subtitle_files:
            click.echo(
                click.style(
                    f"Successfully downloaded {len(subtitle_files)} subtitle files:",
                    fg="green",
                )
            )
            for file in subtitle_files:
                click.echo(f"- {file}")
        else:
            click.echo(click.style("No subtitle files were downloaded.", fg="yellow"))

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
        raise click.Abort()
