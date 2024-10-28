# src/downie/utils/ffmpeg.py
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional
import shutil
import logging

logger = logging.getLogger(__name__)

def validate_ffmpeg_installation() -> bool:
    """Validate FFmpeg installation and capabilities."""
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            check=True
        )
        return True
    except Exception as e:
        logger.error(f"FFmpeg validation failed: {str(e)}")
        return False

def get_video_info(file_path: Path) -> Dict:
    """
    Get video file information using FFprobe.
    
    Args:
        file_path: Path to video file
        
    Returns:
        Dictionary containing video information
        
    Raises:
        ValueError: If FFprobe fails or returns invalid data
    """
    if not file_path.exists():
        raise ValueError(f"File not found: {file_path}")

    try:
        # First check if file is readable
        with open(file_path, 'rb') as f:
            # Read first few bytes to verify it's accessible
            f.read(1024)

        result = subprocess.run([
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(file_path)
        ], capture_output=True, text=True, check=True)

        try:
            info = json.loads(result.stdout)
            if not info or 'streams' not in info:
                raise ValueError("FFprobe returned invalid data")
            return info
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse FFprobe output: {str(e)}")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or "No error message provided"
        raise ValueError(f"FFprobe failed: {error_msg}")
    except Exception as e:
        raise ValueError(f"Failed to get video info: {str(e)}")

def check_codec_support(codec: str) -> bool:
    """
    Check if FFmpeg supports a specific codec.
    
    Args:
        codec: Name of the codec to check
        
    Returns:
        True if codec is supported, False otherwise
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-codecs'],
            capture_output=True,
            text=True,
            check=True
        )
        return codec in result.stdout
    except subprocess.CalledProcessError:
        logger.error(f"Failed to check codec support for {codec}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking codec support: {str(e)}")
        return False

def get_ffmpeg_path() -> Optional[str]:
    """Get the path to FFmpeg executable."""
    return shutil.which('ffmpeg')

def create_test_video(output_path: Path, duration: int = 1, size: str = "1280x720") -> Path:
    """
    Create a test video file for testing purposes.
    
    Args:
        output_path: Where to save the video
        duration: Length of video in seconds
        size: Video dimensions in format "WIDTHxHEIGHT"
    
    Returns:
        Path to created video file
    """
    try:
        subprocess.run([
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'testsrc=duration={duration}:size={size}:rate=30',
            '-f', 'lavfi',
            '-i', f'sine=frequency=1000:duration={duration}',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            str(output_path)
        ], capture_output=True, check=True)
        
        return output_path
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to create test video: {e.stderr}")