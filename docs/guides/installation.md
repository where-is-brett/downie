# Installation Guide

This guide will help you install Downie and its dependencies on your system.

## System Requirements

- Python 3.8 or higher
- FFmpeg
- 500MB free disk space
- Internet connection for downloading

## Installing FFmpeg

FFmpeg is required for video processing capabilities. Install it for your operating system:

### macOS

Using Homebrew:
```bash
brew install ffmpeg
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows

1. Download FFmpeg from the [official website](https://ffmpeg.org/download.html)
2. Extract the archive
3. Add the FFmpeg `bin` directory to your system PATH

## Installing Downie

### Using pip (Recommended)

```bash
pip install downie
```

### From Source

```bash
# Clone the repository
git clone https://github.com/where-is-brett/downie.git
cd downie

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Verifying Installation

Check if everything is installed correctly:

```bash
# Check FFmpeg
ffmpeg -version

# Check Downie
downie --version
```

## Optional Dependencies

### For Development
```bash
pip install -e ".[dev]"
```

### For Documentation
```bash
pip install -e ".[docs]"
```

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade downie
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   ```
   Error: FFmpeg is not installed or not accessible
   ```
   Solution: Add FFmpeg to your system PATH or reinstall FFmpeg

2. **Python version mismatch**
   ```
   Error: Python 3.8 or higher is required
   ```
   Solution: Update Python to a supported version

3. **Permission errors**
   ```
   Error: Permission denied
   ```
   Solution: Use `sudo pip install` (Linux/macOS) or run as administrator (Windows)

For more issues, check our [GitHub Issues](https://github.com/where-is-brett/downie/issues).