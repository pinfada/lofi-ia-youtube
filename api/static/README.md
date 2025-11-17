# Static Assets

This directory contains static assets used in video generation.

## Files

- **intro.mp4** - Intro video (3 seconds) displayed at the start of each video
- **outro.mp4** - Outro video (3 seconds) displayed at the end of each video
- **templates/thumbnail_template.png** - Base template for thumbnail generation

## Generating Assets

The assets can be generated using the provided script:

### Option 1: Inside Docker Container (Recommended)
```bash
# Start the containers
make up

# Generate assets inside the API container
docker compose exec api bash /app/scripts/generate_static_assets.sh
```

### Option 2: Local Generation (requires FFmpeg)
```bash
# Requires FFmpeg to be installed locally
bash scripts/generate_static_assets.sh
```

### Option 3: Python Script (requires Pillow and FFmpeg)
```bash
# Requires: pip install Pillow ffmpeg-python
python3 scripts/generate_static_assets.py
```

## Customization

You can customize the assets by:

1. **Edit the generation scripts** to change text, colors, durations, etc.
2. **Replace with custom files** - just ensure they match these specifications:
   - `intro.mp4` / `outro.mp4`: 1920x1080, MP4, H.264 codec
   - `thumbnail_template.png`: 1280x720, PNG format

## File Specifications

| File | Format | Resolution | Duration | Size (approx) |
|------|--------|------------|----------|---------------|
| intro.mp4 | MP4/H.264 | 1920x1080 | 3s | ~500KB |
| outro.mp4 | MP4/H.264 | 1920x1080 | 3s | ~500KB |
| thumbnail_template.png | PNG | 1280x720 | N/A | ~200KB |

## Development

During development, placeholder files are used. Generate the real assets before running the pipeline in production.

The pipeline will still work with placeholder files, but the intro/outro videos will not display correctly in the final output.
