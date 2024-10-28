# src/downie/config/settings.py
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import os
import logging.config

class Settings:
    """Global application settings."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config_dir = Path.home() / '.config' / 'downie'
        self.config_file = config_file if config_file else self.config_dir / 'config.yaml'
        self.download_dir = Path.home() / 'Downloads' / 'downie'
        self.temp_dir = Path.home() / '.cache' / 'downie'
        self.log_dir = self.config_dir / 'logs'

        # Create necessary directories
        for directory in [self.config_dir, self.download_dir, self.temp_dir, self.log_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Setup logging
        self._setup_logging()

    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            'download': {
                'output_dir': str(self.download_dir),
                'temp_dir': str(self.temp_dir),
                'max_concurrent_downloads': 3,
                'default_quality': '1080p',
                'rate_limit': None,
                'proxy': None
            },
            'processing': {
                'video_codec': 'libx264',
                'audio_codec': 'aac',
                'thumbnail_size': '1280x720',
                'max_processing_threads': 2
            },
            'subtitles': {
                'languages': ['en'],
                'download_auto': False,
                'convert_to_srt': True
            },
            'storage': {
                'max_temp_size': '10GB',
                'cleanup_after_days': 7,
                'min_free_space': '5GB'
            }
        }

        try:
            if self.config_file.exists():
                print(f"Loading config from: {self.config_file}")  # Add path check
                with open(self.config_file) as f:
                    user_config = yaml.safe_load(f)
                    # Deep merge user config with defaults
                    merged_config = self._merge_configs(default_config, user_config or {})
                    print(f"Loaded and merged config: {merged_config}")  # Log loaded config
                    return merged_config
        except Exception as e:
            logging.error(f"Failed to load config: {str(e)}")

        return default_config

    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Deep merge two configuration dictionaries."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        print(f"Merging result: {result}")  # Debug to check merging process
        return result
    
    def _setup_logging(self) -> None:
        """Configure logging."""
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
            },
            'handlers': {
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': str(self.log_dir / 'downie.log'),
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'formatter': 'standard',
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                }
            },
            'loggers': {
                '': {  # Root logger
                    'handlers': ['console', 'file'],
                    'level': 'INFO',
                },
                'downie': {
                    'handlers': ['console', 'file'],
                    'level': 'DEBUG',
                    'propagate': False,
                }
            }
        }
        
        logging.config.dictConfig(logging_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key path."""
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            print(f"Saving config to: {self.config_file}")  # Add path check
            with open(self.config_file, 'w') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False)
            print(f"Config saved: {self.config}")  # Confirm save
        except Exception as e:
            logging.error(f"Failed to save config: {str(e)}")



# Global settings instance
settings = Settings()