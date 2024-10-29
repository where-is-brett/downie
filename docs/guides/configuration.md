# Configuration Guide

Downie can be configured using a YAML configuration file and command-line options. It provides both video downloading and subtitle management capabilities.

## Configuration File

The default configuration file is located at:
- Linux/macOS: `~/.config/downie/config.yaml`
- Windows: `%APPDATA%\downie\config.yaml`

### Example Configuration

```yaml
video:
  output_dir: ~/Downloads/videos
  quality: best
  format_id: null
  proxy: null
  limit_speed: null
  username: null
  password: null
  cookies_file: null
  
processing:
  crop: null
  resize: null
  rotate: null
  fps: null
  remove_audio: false
  extract_audio: false
  audio_format: mp3
  video_codec: libx264
  audio_codec: aac
  video_bitrate: null
  audio_bitrate: null

subtitles:
  output_dir: ~/Downloads/subtitles
  languages: [en]
  formats: [srt]
  auto_generated: false
  convert_to_srt: true
  fix_encoding: true
  merge_subtitles: false
```

## Configuration Options

### Video Download Settings

| Option | Description | Default |
|--------|-------------|---------|
| `output_dir` | Download directory for videos | ~/Downloads/videos |
| `quality` | Video quality (e.g., 720p, 1080p, best) | best |
| `format_id` | Specific format ID to download | None |
| `proxy` | Proxy URL | None |
| `limit_speed` | Download speed limit (e.g., 1M, 500K) | None |
| `username` | Account username | None |
| `password` | Account password | None |
| `cookies_file` | Path to cookies file | None |

### Video Processing Settings

| Option | Description | Default |
|--------|-------------|---------|
| `crop` | Crop video (width:height:x:y) | None |
| `resize` | Resize video (widthxheight) | None |
| `rotate` | Rotate video (degrees) | None |
| `fps` | Target FPS | None |
| `remove_audio` | Remove audio track | False |
| `extract_audio` | Extract audio only | False |
| `audio_format` | Audio format for extraction | mp3 |
| `video_codec` | Video codec (e.g., libx264, libx265) | libx264 |
| `audio_codec` | Audio codec (e.g., aac, mp3) | aac |
| `video_bitrate` | Video bitrate (e.g., 5M) | None |
| `audio_bitrate` | Audio bitrate (e.g., 192k) | None |

### Subtitle Settings

| Option | Description | Default |
|--------|-------------|---------|
| `output_dir` | Download directory for subtitles | ~/Downloads/subtitles |
| `languages` | Subtitle languages to download | [en] |
| `formats` | Subtitle formats to download | [srt] |
| `auto_generated` | Include auto-generated subtitles | False |
| `convert_to_srt` | Convert subtitles to SRT | True |
| `fix_encoding` | Fix subtitle encoding issues | True |
| `merge_subtitles` | Merge all subtitle files into one | False |


## Environment Variables

You can also configure Downie using environment variables:

```bash
# Video download settings
export downie_OUTPUT_DIR=~/Videos
export downie_QUALITY=720p
export downie_PROXY=http://proxy:8080
export downie_LIMIT_SPEED=1M

# Processing settings
export downie_VIDEO_CODEC=libx264
export downie_AUDIO_CODEC=aac
export downie_AUDIO_FORMAT=mp3

# Subtitle settings
export downie_SUBTITLE_DIR=~/Subtitles
export downie_SUBTITLE_LANGS=en,es
export downie_SUBTITLE_FORMATS=srt,vtt
export downie_MERGE_SUBTITLES=true
```

## Configuration Priority

Configuration priority (highest to lowest):
1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values

## Creating a Configuration File

```bash
# Create config directory
mkdir -p ~/.config/downie

# Create default config
downie config init
```

## Best Practices

1. **Start with Defaults**: Begin with the default configuration and modify as needed
2. **Version Control**: Keep your configuration in version control for backup
3. **Environment-Specific**: Use different configurations for different environments
4. **Security**: Never commit sensitive information (like passwords) to version control

## Troubleshooting

### Common Configuration Issues

1. **Invalid URL**
   ```
   Error: Invalid URL: [url]
   ```
   Solution: Check if the URL is properly formatted and supported

2. **Permission Issues**
   ```
   Error: Cannot write to output directory
   ```
   Solution: Check directory permissions

3. **Download Failures**
   ```
   Error: Download failed
   ```
   Solution: Check network connection and try with --proxy if behind firewall

4. **Processing Errors**
   ```
   Error: Processing failed
   ```
   Solution: Verify ffmpeg installation and processing options

## Next Steps

- Learn about [Advanced Usage](advanced-usage.md)
- Check the [API Reference](../api/downloader.md)
- Read about [Contributing](../contributing/development.md)