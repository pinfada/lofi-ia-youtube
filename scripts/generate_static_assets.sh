#!/bin/bash
# Generate basic static assets using FFmpeg only
# This script creates simple placeholder assets for development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STATIC_DIR="$PROJECT_ROOT/api/static"
TEMPLATES_DIR="$STATIC_DIR/templates"

# Ensure directories exist
mkdir -p "$STATIC_DIR"
mkdir -p "$TEMPLATES_DIR"

echo "============================================================"
echo "Generating Static Assets with FFmpeg"
echo "============================================================"

# Generate intro video (3 seconds, black with white text)
echo "Creating intro video: $STATIC_DIR/intro.mp4"
ffmpeg -f lavfi -i color=c=black:s=1920x1080:d=3 \
    -vf "drawtext=text='Lo-Fi IA YouTube':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,fade=t=in:st=0:d=1" \
    -pix_fmt yuv420p -t 3 -y "$STATIC_DIR/intro.mp4" 2>/dev/null

echo "✓ Intro video created (3s)"

# Generate outro video (3 seconds, black with white text)
echo "Creating outro video: $STATIC_DIR/outro.mp4"
ffmpeg -f lavfi -i color=c=black:s=1920x1080:d=3 \
    -vf "drawtext=text='Subscribe for more Lo-Fi beats!':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,fade=t=out:st=2:d=1" \
    -pix_fmt yuv420p -t 3 -y "$STATIC_DIR/outro.mp4" 2>/dev/null

echo "✓ Outro video created (3s)"

# Generate thumbnail template using FFmpeg (PNG output)
echo "Creating thumbnail template: $TEMPLATES_DIR/thumbnail_template.png"
ffmpeg -f lavfi -i "color=c=0x1e1e50:s=1280x720:d=1" \
    -vf "drawbox=x=10:y=10:w=1260:h=700:color=white:t=3,drawtext=text='Lo-Fi Beats':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,drawtext=text='Study • Relax • Sleep':fontsize=24:fontcolor=0xc8c8ff:x=(w-text_w)/2:y=(h-text_h)/2+20:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" \
    -frames:v 1 -y "$TEMPLATES_DIR/thumbnail_template.png" 2>/dev/null

echo "✓ Thumbnail template created (1280x720)"

echo "============================================================"
echo "✓ All static assets generated successfully!"
echo "============================================================"
echo ""
echo "Generated files:"
echo "  - $STATIC_DIR/intro.mp4"
echo "  - $STATIC_DIR/outro.mp4"
echo "  - $TEMPLATES_DIR/thumbnail_template.png"
echo ""
echo "Note: To regenerate with better quality, run inside Docker container:"
echo "  docker compose exec api bash /app/scripts/generate_static_assets.sh"
