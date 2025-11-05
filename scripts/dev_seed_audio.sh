#!/usr/bin/env bash
mkdir -p ./data/MP3_NORMALIZED
# Copie ou génère quelques mp3 fictifs pour tests (placeholders vides ici)
for i in {1..20}; do dd if=/dev/zero of=./data/MP3_NORMALIZED/track_$i.mp3 bs=1024 count=16; done
