# Quick Start Guide

Get started with Downie's basic features and commands.

## Basic Usage

### Download a Video

```bash
# Basic download (best quality)
downie video download "https://youtube.com/watch?v=example"

# Specify quality
downie video download "https://youtube.com/watch?v=example" -q 1080p

# Specify output directory
downie video download "https://youtube.com/watch?v=example" -o ~/Downloads/videos
```

### Download Subtitles

```bash
# Download English subtitles
downie subtitle download "https://youtube.com/watch?v=example"

# Download multiple languages
downie subtitle download "https://youtube.com/watch?v=example" -l "en,es,fr"

# Convert to SRT format
downie subtitle download "https://youtube.com/watch?v=example" --convert-srt
```

### Process Videos

```bash
# Resize video
downie video download "https://youtube.com/watch?v=example" \
  --process \
  --resize 1920x1080

# Convert HDR to SDR
downie video download "https://youtube.com/watch?v=example" \
  --process \
  --hdr-to-sdr

# Extract audio
downie video download "https://youtube.com/watch?v=example" \
  --extract-audio \
  --audio-format mp3
```

## Command Structure

Downie commands follow this pattern:
```bash
downie <command> [options] URL
downie subtitle <command> [options] URL
```

Common options:
- `-o, --output`: Output directory
- `-q, --quality`: Video quality
- `-f, --format`: Format selection
- `--process`: Enable video processing
- `--verbose`: Show detailed output

## Examples

### Download Playlist
```bash
downie video download "https://youtube.com/playlist?list=example" \
  -o playlist \
  -q 720p
```

### Download with Custom Format
```bash
downie video download "https://youtube.com/watch?v=example" \
  -f "bestvideo[height<=1080]+bestaudio/best"
```

### Process and Convert
```bash
downie video download "https://youtube.com/watch?v=example" \
  --process \
  --resize 1280x720 \
  --fps 30 \
  --video-codec libx264
```

## Next Steps

- Check out the [Configuration Guide](configuration.md) for customizing Downie
- Learn about [Advanced Usage](advanced-usage.md) features
- Read the [API Reference](../api/downloader.md) for programmatic usage