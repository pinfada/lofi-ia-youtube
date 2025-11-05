#!/usr/bin/env bash
mkdir -p ./data
dd if=/dev/zero of=./data/loop_seamless.mp4 bs=1024 count=64
