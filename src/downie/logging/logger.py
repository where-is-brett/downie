# src/downie/logging/logger.py
import logging
import sys
from pathlib import Path
from typing import Optional


def get_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create formatters
        console_formatter = logging.Formatter("%(message)s")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler if log_file is specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

    return logger
