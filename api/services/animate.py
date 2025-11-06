"""Simple local animation helper used during development.

The real project is supposed to call Pika Labs (or a similar provider) to
generate a looping animation based on a still image.  In our development
environment we approximate that behaviour by creating a short mp4 from the
provided still using ffmpeg.  The function keeps the same signature as the
future integration so swapping it for a real API call later is
straight-forward.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def animate_to_loop(image_path: str, out_video: str, seconds: int = 6) -> str:
    """Create a short MP4 clip from ``image_path``.

    The clip is generated with ffmpeg by looping the still image and applying a
    gentle zoom-in effect.  Although simplistic, it is sufficient for testing
    the downstream ffmpeg pipeline.
    """

    target = Path(out_video)
    target.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        image_path,
        "-vf",
        "scale=1920:1080,zoompan=z='min(zoom+0.0015,1.1)':d=180:s=1920x1080:fps=30",
        "-t",
        str(max(1, seconds)),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-an",
        str(target),
    ]

    subprocess.run(cmd, check=True)
    return str(target)