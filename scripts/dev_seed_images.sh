#!/usr/bin/env bash
# Generate a short, valid seamless loop video for local testing.
# A zero-filled file would be picked up by the pipeline and make ffmpeg fail.
set -e
OUT_FILE="${LOOP_VIDEO:-./data/loop_seamless.mp4}"
mkdir -p "$(dirname "$OUT_FILE")"
ffmpeg -loglevel error -y -f lavfi -i "testsrc2=size=1920x1080:rate=30:duration=6" \
  -c:v libx264 -pix_fmt yuv420p -an "$OUT_FILE"
echo "Generated loop video $OUT_FILE"
