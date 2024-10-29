import click

from .download import cli as download_cli
from .subtitle import cli as subtitle_cli


@click.group()
def cli():
    """Downie - Advanced video and subtitle downloader

    Downie is a powerful tool for downloading videos and subtitles from various platforms.

    Basic Usage:

      downie video download URL [options]
      downie subtitle download URL [options]

    Examples:

      # Download a video in best quality
      downie video download "https://example.com/video"

      # Download video with specific quality
      downie video download "https://example.com/video" -q 1080p

      # Download English subtitles
      downie subtitle download "https://example.com/video" -l en
    """
    pass


cli.add_command(download_cli, name="video")
cli.add_command(subtitle_cli, name="subtitle")

if __name__ == "__main__":
    cli()
