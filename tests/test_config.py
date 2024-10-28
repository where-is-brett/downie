# tests/test_config.py
import pytest
import yaml
from downie.config.settings import Settings

class TestSettings:
    @pytest.fixture
    def sample_config(self, temp_dir):
        config = {
            'download': {
                'output_dir': str(temp_dir),
                'max_concurrent_downloads': 3
            }
        }
        config_file = temp_dir / 'config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        return config_file

    @pytest.mark.config
    def test_load_config(self, sample_config):
        """Test configuration loading."""
        settings = Settings()
        settings.config_file = sample_config
        config = settings._load_config()
        assert config['download']['max_concurrent_downloads'] == 3
        
    @pytest.mark.config
    def test_default_values(self):
        """Test default configuration values."""
        settings = Settings()
        assert settings.get('download.default_quality') == '1080p'

    def test_config_override(self, sample_config):
        """Test configuration override."""
        settings = Settings(config_file=sample_config)
        settings.config['download']['max_concurrent_downloads'] = 5
        print(f"Before saving: {settings.config['download']['max_concurrent_downloads']}")  # Log before saving
        settings.save()

        # Reload and verify
        new_settings = Settings(config_file=sample_config)
        print(f"After loading: {new_settings.get('download.max_concurrent_downloads')}")  # Log after loading
        assert new_settings.get('download.max_concurrent_downloads') == 5

