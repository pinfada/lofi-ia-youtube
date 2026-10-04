#!/usr/bin/env bash
# Generate a few short, valid MP3 tracks (sine tones) for local testing.
# Files filled with zeros are not decodable by ffmpeg and break the pipeline.
set -e
OUT_DIR="${AUDIO_DIR:-./data/MP3_NORMALIZED}"
COUNT="${1:-20}"
mkdir -p "$OUT_DIR"
for i in $(seq 1 "$COUNT"); do
  freq=$((200 + i * 20))
  ffmpeg -loglevel error -y -f lavfi -i "sine=frequency=${freq}:duration=5" \
    -ar 44100 -ac 2 -c:a libmp3lame -b:a 128k "$OUT_DIR/track_$i.mp3"
done
echo "Generated $COUNT tracks in $OUT_DIR"
