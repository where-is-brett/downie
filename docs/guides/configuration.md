# Configuration Guide

Downie can be configured using a YAML configuration file and command-line options.

## Configuration File

The default configuration file is located at:
- Linux/macOS: `~/.config/downie/config.yaml`
- Windows: `%APPDATA%\downie\config.yaml`

### Example Configuration

```yaml
download:
  output_dir: ~/Downloads/videos
  max_concurrent_downloads: 3
  default_quality: 1080p
  rate_limit: null
  proxy: null
  verify_ssl: true
  retries: 3

processing:
  video_codec: libx264
  audio_codec: aac
  thumbnail_size: 1280x720
  max_processing_threads: 2
  temp_dir: ~/.cache/downie
  default_format: mp4

subtitles:
  languages: [en]
  download_auto: false
  convert_to_srt: true
  fix_encoding: true
  remove_formatting: false

storage:
  max_temp_size: 10GB
  cleanup_after_days: 7
  min_free_space: 5GB
```

## Configuration Options

### Download Settings

| Option | Description | Default |
|--------|-------------|---------|
| `output_dir` | Default download directory | `~/Downloads/videos` |
| `max_concurrent_downloads` | Maximum simultaneous downloads | 3 |
| `default_quality` | Default video quality | 1080p |
| `rate_limit` | Download speed limit | None |
| `proxy` | Proxy URL | None |
| `verify_ssl` | Verify SSL certificates | True |
| `retries` | Number of retry attempts | 3 |

### Processing Settings

| Option | Description | Default |
|--------|-------------|---------|
| `video_codec` | Default video codec | libx264 |
| `audio_codec` | Default audio codec | aac |
| `thumbnail_size` | Thumbnail resolution | 1280x720 |
| `max_processing_threads` | Maximum processing threads | 2 |
| `temp_dir` | Temporary file directory | ~/.cache/downie |
| `default_format` | Default output format | mp4 |

### Subtitle Settings

| Option | Description | Default |
|--------|-------------|---------|
| `languages` | Default subtitle languages | [en] |
| `download_auto` | Download auto-generated subtitles | False |
| `convert_to_srt` | Convert subtitles to SRT | True |
| `fix_encoding` | Fix subtitle encoding issues | True |
| `remove_formatting` | Remove subtitle formatting | False |

### Storage Settings

| Option | Description | Default |
|--------|-------------|---------|
| `max_temp_size` | Maximum temporary storage | 10GB |
| `cleanup_after_days` | Auto-cleanup after days | 7 |
| `min_free_space` | Minimum required free space | 5GB |

## Environment Variables

You can also configure Downie using environment variables:

```bash
# Download settings
export downie_OUTPUT_DIR=~/Videos
export downie_QUALITY=720p
export downie_PROXY=http://proxy:8080

# Processing settings
export downie_VIDEO_CODEC=libx264
export downie_AUDIO_CODEC=aac

# Subtitle settings
export downie_SUBTITLE_LANGS=en,es
```

## Command-Line Priority

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

## Validating Configuration

```bash
# Validate current configuration
downie config validate

# Show current configuration
downie config show
```

## Best Practices

1. **Start with Defaults**: Begin with the default configuration and modify as needed
2. **Version Control**: Keep your configuration in version control for backup
3. **Environment-Specific**: Use different configurations for different environments
4. **Security**: Never commit sensitive information (like proxy passwords) to version control

## Troubleshooting

### Common Configuration Issues

1. **Invalid YAML Syntax**
   ```
   Error: Invalid YAML syntax in config file
   ```
   Solution: Use a YAML validator to check syntax

2. **Permission Issues**
   ```
   Error: Cannot write to config directory
   ```
   Solution: Check directory permissions

3. **Invalid Values**
   ```
   Error: Invalid value for max_concurrent_downloads
   ```
   Solution: Check value types and ranges in documentation

## Advanced Configuration

### Custom Format Strings

```yaml
download:
  format_strings:
    hd: "bestvideo[height<=1080]+bestaudio/best"
    sd: "bestvideo[height<=720]+bestaudio/best"
    mobile: "bestvideo[height<=480]+bestaudio/best"
```

### Processing Profiles

```yaml
processing:
  profiles:
    mobile:
      resize: 720x480
      fps: 30
      video_codec: libx264
    web:
      resize: 1280x720
      fps: 60
      video_codec: libvpx-vp9
```

### Proxy Configuration

```yaml
download:
  proxy:
    http: http://proxy:8080
    https: https://proxy:8080
    socks5: socks5://proxy:1080
```

## Next Steps

- Learn about [Advanced Usage](advanced-usage.md)
- Check the [API Reference](../api/downloader.md)
- Read about [Contributing](../contributing/development.md)