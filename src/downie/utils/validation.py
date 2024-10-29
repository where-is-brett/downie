# src/downie/utils/validation.py
import re
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Validate if string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_output_path(path: str) -> Optional[str]:
    """Validate output path."""
    if not path:
        return "Output path cannot be empty"
    if len(path) > 255:
        return "Output path too long"
    if not re.match(r"^[\w\-. /\\]+$", path):
        return "Output path contains invalid characters"
    return None


def validate_format_id(format_id: str) -> Optional[str]:
    """Validate format ID."""
    if not re.match(r"^[\w\-+]+$", format_id):
        return "Invalid format ID"
    return None
