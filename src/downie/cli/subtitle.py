# src/downie/cli/subtitle.py
import click
from pathlib import Path
from ..models.config import SubtitleConfig
from ..core.subtitle import SubtitleDownloader
from ..logging.logger import get_logger

logger = get_logger(__name__)

@click.group()
def cli():
    """Subtitle Downloader CLI"""
    pass

@cli.command()
@click.argument('url')
@click.option('-o', '--output', type=click.Path(), default='subtitles',
              help='Output directory for subtitles')
@click.option('-l', '--languages', default='en',
              help='Comma-separated language codes')
@click.option('--formats', default='srt',
              help='Comma-separated subtitle formats')
@click.option('--auto-generated/--no-auto-generated', default=False,
              help='Include auto-generated subtitles')
@click.option('--convert-srt/--no-convert-srt', default=True,
              help='Convert all subtitles to SRT format')
@click.option('--fix-encoding/--no-fix-encoding', default=True,
              help='Fix subtitle encoding issues')
@click.option('--merge/--no-merge', default=False,
              help='Merge all subtitle files')
def download(url, **kwargs):
    """Download subtitles from URL"""
    try:
        config = SubtitleConfig(
            url=url,
            output_path=Path(kwargs.pop('output')),
            languages=kwargs.pop('languages').split(','),
            formats=kwargs.pop('formats').split(','),
            convert_to_srt=kwargs.pop('convert_srt'),
            fix_encoding=kwargs.pop('fix_encoding', True),
            merge_subtitles=kwargs.pop('merge', False)
        )

        downloader = SubtitleDownloader(config)
        subtitle_files = downloader.download()

        if subtitle_files:
            click.echo(click.style(
                f"Successfully downloaded {len(subtitle_files)} subtitle files:",
                fg='green'
            ))
            for file in subtitle_files:
                click.echo(f"- {file}")
        else:
            click.echo(click.style(
                "No subtitle files were downloaded.",
                fg='yellow'
            ))

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'))
        raise click.Abort()
    
def main():
    cli()