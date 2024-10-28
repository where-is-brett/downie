# src/downie/core/subtitle.py
from pathlib import Path
import chardet
import re
from typing import Dict, List
from ..models.config import SubtitleConfig
from ..exceptions.errors import SubtitleError
import yt_dlp
import logging

logger = logging.getLogger(__name__)


class SubtitleDownloader:
    def __init__(self, config: SubtitleConfig):
        self.config = config
        self._validate_config()
        self.output_path = config.output_path
        self.output_path.mkdir(parents=True, exist_ok=True)

    def _validate_config(self) -> None:
        """Validate configuration."""
        if not self.config.url:
            raise SubtitleError("URL cannot be empty")

        # Basic URL validation
        url_pattern = r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)/\S+"
        if not re.match(url_pattern, self.config.url):
            raise SubtitleError("Invalid URL format")

    def _fix_encoding(self, file: Path) -> None:
        """Fix subtitle file encoding."""
        if not file.exists():
            logger.error(f"File not found: {file}")
            raise FileNotFoundError(f"File not found: {file}")
            
        try:
            raw_data = file.read_bytes()
            detected = chardet.detect(raw_data)
            if not detected['encoding']:
                raise SubtitleError(f"Could not detect encoding for {file}")
                
            current_encoding = detected['encoding'] if detected['confidence'] > 0.7 else 'utf-8'
            
            content = raw_data.decode(current_encoding)
            file.write_text(content, encoding='utf-8')
            logger.info(f"Fixed encoding for {file.name}")
        except Exception as e:
            logger.error(f"Failed to fix encoding for {file.name}: {str(e)}")
            raise

    def _adjust_subtitle_timing(self, file: Path, offset: float) -> None:
        """
        Adjust subtitle timing by offset seconds.
        
        Args:
            file: Path to subtitle file
            offset: Time offset in seconds (can be negative)
        """
        try:
            import pysrt
            subs = pysrt.open(str(file))
            
            # Convert offset to exact milliseconds
            offset_ms = round(offset * 1000)  # Round to nearest millisecond
            
            for sub in subs:
                # Calculate total milliseconds
                start_ms = (sub.start.hours * 3600000 + 
                        sub.start.minutes * 60000 + 
                        sub.start.seconds * 1000 + 
                        sub.start.milliseconds)
                end_ms = (sub.end.hours * 3600000 + 
                        sub.end.minutes * 60000 + 
                        sub.end.seconds * 1000 + 
                        sub.end.milliseconds)
                
                # Apply offset
                new_start_ms = max(0, start_ms + offset_ms)
                new_end_ms = max(0, end_ms + offset_ms)
                
                # Convert milliseconds back to hours, minutes, seconds, milliseconds
                start_hours = new_start_ms // 3600000
                start_remainder = new_start_ms % 3600000
                start_minutes = start_remainder // 60000
                start_remainder %= 60000
                start_seconds = start_remainder // 1000
                start_milliseconds = start_remainder % 1000
                
                end_hours = new_end_ms // 3600000
                end_remainder = new_end_ms % 3600000
                end_minutes = end_remainder // 60000
                end_remainder %= 60000
                end_seconds = end_remainder // 1000
                end_milliseconds = end_remainder % 1000
                
                # Create new SubRipTime objects
                sub.start = pysrt.SubRipTime(
                    hours=int(start_hours),
                    minutes=int(start_minutes),
                    seconds=int(start_seconds),
                    milliseconds=int(start_milliseconds)
                )
                sub.end = pysrt.SubRipTime(
                    hours=int(end_hours),
                    minutes=int(end_minutes),
                    seconds=int(end_seconds),
                    milliseconds=int(end_milliseconds)
                )
            
            # Save with Unix-style line endings for consistency
            subs.save(str(file), encoding='utf-8')
            logger.info(f"Adjusted timing for {file} by {offset} seconds")
            
        except Exception as e:
            logger.error(f"Failed to adjust timing for {file}: {str(e)}")
            raise SubtitleError(f"Failed to adjust timing: {str(e)}")

    def download(self) -> List[Path]:
        """Download subtitles according to configuration."""
        try:
            downloaded_files = []
            opts = self._get_ydl_opts()
            logger.debug(f"Using yt-dlp options: {opts}")

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.config.url, download=True)
                title = info.get('title', '').replace('/', '_')
                logger.debug(f"Video title: {title}")
                
                # First check for existing files in all requested formats
                for lang in self.config.languages:
                    for fmt in self.config.formats:
                        pattern = f"*.{lang}.{fmt}"
                        logger.debug(f"Searching for pattern: {pattern}")
                        for file in self.output_path.glob(pattern):
                            logger.debug(f"Found file: {file}")
                            if file.exists():
                                if self.config.fix_encoding:
                                    self._fix_encoding(file)
                                
                                if self.config.convert_to_srt and file.suffix == '.vtt':
                                    new_file = self._convert_to_srt(file)
                                    if new_file != file:
                                        file.unlink()
                                        file = new_file
                                        logger.debug(f"Converted to SRT: {new_file}")
                                
                                if self.config.remove_formatting:
                                    self._remove_formatting(file)
                                
                                downloaded_files.append(file)
                                logger.debug(f"Added file to results: {file}")
                
                # Handle case when VTT was downloaded but SRT was requested
                if 'srt' in self.config.formats and not any(f.suffix == '.srt' for f in downloaded_files):
                    vtt_files = list(self.output_path.glob("*.vtt"))
                    for vtt_file in vtt_files:
                        srt_file = self._convert_to_srt(vtt_file)
                        if srt_file not in downloaded_files:
                            downloaded_files.append(srt_file)
                            logger.debug(f"Added converted SRT file: {srt_file}")
                
                if self.config.merge_subtitles and len(downloaded_files) > 1:
                    merged_file = self._merge_subtitles(downloaded_files)
                    return [merged_file]
                
                logger.debug(f"Final downloaded files: {downloaded_files}")
                return downloaded_files
                
        except Exception as e:
            logger.error(f"Failed to download subtitles: {str(e)}")
            logger.exception(e)
            raise SubtitleError(f"Failed to download subtitles: {str(e)}")
        
    def _get_ydl_opts(self) -> Dict:
        """Get yt-dlp options for subtitle download."""
        return {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': self.config.auto_generated,
            'subtitleslangs': self.config.languages,
            'subtitlesformat': 'vtt' if 'vtt' in self.config.formats else 'srt',  # Prefer vtt since YouTube provides it
            'outtmpl': str(self.output_path / '%(title)s.%(ext)s'),
            'verbose': True
        }
    
    def _convert_to_srt(self, file: Path) -> Path:
        """Convert subtitle file to SRT format."""
        try:
            if file.suffix == '.srt':
                return file
                
            srt_file = file.with_suffix('.srt')
            logger.debug(f"Converting {file} to {srt_file}")
            
            if file.suffix == '.vtt':
                content = file.read_text(encoding='utf-8')
                
                if 'WEBVTT' in content:
                    lines = content.split('\n')
                    srt_lines = []
                    counter = 1
                    skip_webvtt_header = True
                    
                    for line in lines:
                        if skip_webvtt_header:
                            if line.strip() == '':
                                skip_webvtt_header = False
                            continue
                        
                        if '-->' in line:
                            # Convert VTT timestamp format to SRT format
                            line = line.replace('.', ',')
                            srt_lines.append(str(counter))
                            srt_lines.append(line)
                            counter += 1
                        else:
                            srt_lines.append(line)
                    
                    srt_file.write_text('\n'.join(srt_lines), encoding='utf-8')
                    logger.info(f"Converted {file} to SRT format")
                    return srt_file
            
            logger.warning(f"Could not convert {file} to SRT, returning original file")
            return file
            
        except Exception as e:
            logger.error(f"Failed to convert {file} to SRT: {str(e)}")
            return file

    def list_available_subtitles(self) -> Dict[str, List[str]]:
        """List all available subtitles for a video."""
        try:
            with yt_dlp.YoutubeDL({
                'skip_download': True,
                'quiet': True
            }) as ydl:
                info = ydl.extract_info(self.config.url, download=False)
                available = {
                    'manual': [],
                    'automatic': []
                }

                if 'subtitles' in info:
                    available['manual'] = list(info['subtitles'].keys())

                if 'automatic_captions' in info:
                    available['automatic'] = list(info['automatic_captions'].keys())

                return available

        except Exception as e:
            raise SubtitleError(f"Failed to list subtitles: {str(e)}")

    def _remove_formatting(self, file: Path) -> None:
        """Remove formatting tags."""
        try:
            content = file.read_text(encoding="utf-8")
            # Remove HTML tags
            content = re.sub(r"<[^>]+>", "", content)
            # Remove SSA/ASS style tags
            content = re.sub(r"\{[^}]+\}", "", content)
            file.write_text(content, encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to remove formatting from {file}: {str(e)}")

    def _merge_subtitles(self, files: List[Path]) -> Path:
        """Merge multiple subtitle files."""
        try:
            merged_file = self.output_path / "merged_subtitles.srt"
            with open(merged_file, "w", encoding="utf-8") as outfile:
                for i, file in enumerate(files, 1):
                    content = file.read_text(encoding="utf-8")
                    outfile.write(content)
                    if not content.endswith("\n\n"):
                        outfile.write("\n\n")
            return merged_file
        except Exception as e:
            logger.error(f"Failed to merge subtitles: {str(e)}")
            raise SubtitleError(f"Failed to merge subtitles: {str(e)}")
