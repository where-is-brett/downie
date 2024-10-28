# src/downie/utils/filesystem.py
import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, List, Generator
import logging

logger = logging.getLogger(__name__)

def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if necessary."""
    path.mkdir(parents=True, exist_ok=True)

def calculate_checksum(file_path: Path, algorithm: str = 'sha256') -> str:
    """Calculate file checksum."""
    hash_func = getattr(hashlib, algorithm)()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
            
    return hash_func.hexdigest()

def get_free_space(path: Path) -> int:
    """Get free space in bytes at given path."""
    return shutil.disk_usage(path).free

def clean_filename(filename: str) -> str:
    """Clean filename of invalid characters."""
    # Replace invalid characters with underscore
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # Limit length
    return filename[:255]

def find_files(
    directory: Path,
    pattern: str = '*',
    recursive: bool = False
) -> Generator[Path, None, None]:
    """Find files matching pattern in directory."""
    if recursive:
        for path in directory.rglob(pattern):
            if path.is_file():
                yield path
    else:
        for path in directory.glob(pattern):
            if path.is_file():
                yield path

def safe_move(src: Path, dst: Path) -> Path:
    """Safely move file, ensuring unique destination."""
    if not dst.parent.exists():
        dst.parent.mkdir(parents=True)
        
    if dst.exists():
        base = dst.parent / dst.stem
        suffix = dst.suffix
        counter = 1
        while dst.exists():
            dst = base.with_name(f"{base.name}_{counter}{suffix}")
            counter += 1
    
    shutil.move(str(src), str(dst))
    return dst

def cleanup_temp_files(directory: Path, pattern: str = '*') -> None:
    """Clean up temporary files in directory."""
    try:
        for file in directory.glob(pattern):
            if file.is_file():
                file.unlink()
    except Exception as e:
        logger.error(f"Failed to cleanup temp files: {str(e)}")

class FileRotator:
    """Rotate old files to maintain disk space."""
    
    def __init__(self, directory: Path, max_size: int, pattern: str = '*'):
        self.directory = directory
        self.max_size = max_size
        self.pattern = pattern
    
    def rotate(self) -> None:
        """Remove oldest files if total size exceeds max_size."""
        total_size = 0
        files = []
        
        # Get all files and their info
        for file in self.directory.glob(self.pattern):
            if file.is_file():
                size = file.stat().st_size
                files.append((file, size, file.stat().st_mtime))
                total_size += size
        
        # Sort by modification time (oldest first)
        files.sort(key=lambda x: x[2])
        
        # Remove oldest files until under max_size
        while total_size > self.max_size and files:
            file, size, _ = files.pop(0)
            try:
                file.unlink()
                total_size -= size
                logger.info(f"Rotated file: {file}")
            except Exception as e:
                logger.error(f"Failed to rotate file {file}: {str(e)}")