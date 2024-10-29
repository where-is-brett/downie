# Downie: Advanced Video and Subtitle Downloader

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/downie/badge/?version=latest)](https://downie.readthedocs.io/en/latest/?badge=latest)

Downie is a powerful, feature-rich video and subtitle downloader with advanced processing capabilities.

## Features

- Download videos from multiple platforms (YouTube, Vimeo, etc.)
- Process videos (resize, crop, HDR to SDR conversion)
- Download and process subtitles
- Batch processing support
- Configurable settings

## Quick Start

### Installation

```bash
# Install ffmpeg first
# On macOS:
brew install ffmpeg

# On Ubuntu/Debian:
sudo apt install ffmpeg

# Install downie
pip install downie
```

### Basic Usage

```bash
# Download video
downie video download "https://youtube.com/watch?v=example"

# Download with processing
downie video download "https://youtube.com/watch?v=example" --process --resize 1080p

# Download subtitles
downie subtitle download "https://youtube.com/watch?v=example" -l en,es
```

## Documentation

Full documentation is available at [downie.readthedocs.io](https://downie.readthedocs.io/), including:

- [Installation Guide](https://downie.readthedocs.io/en/latest/guides/installation/)
- [Quick Start Guide](https://downie.readthedocs.io/en/latest/guides/quickstart/)
- [Advanced Usage](https://downie.readthedocs.io/en/latest/guides/advanced-usage/)
- [API Reference](https://downie.readthedocs.io/en/latest/api/)
- [Contributing Guide](https://downie.readthedocs.io/en/latest/contributing/)

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and contribute to the project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the core downloading functionality
- [FFmpeg](https://ffmpeg.org/) for video processing capabilities