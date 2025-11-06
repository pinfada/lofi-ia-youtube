"""Utility helpers for producing placeholder images.

The production system is expected to call an external provider (OpenAI,
Stability, …) to generate a 16:9 illustration.  For development and for the
unit/integration tests that run in this kata we generate a deterministic image
locally using Pillow so that the rest of the pipeline (animation, thumbnail
rendering, ffmpeg concatenation, …) has real assets to work with.

The helper below keeps the public API identical to the future implementation so
swapping the stub for a real network call will only require replacing the body
of :func:`generate_image_16x9`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

# Default HD size in 16:9 ratio.  The actual APIs usually return at least this
# resolution, so using it here gives ffmpeg enough pixels to work with.
DEFAULT_SIZE: Tuple[int, int] = (1920, 1080)


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _draw_background(draw: ImageDraw.ImageDraw, size: Tuple[int, int]) -> None:
    """Create a simple vertical gradient to avoid a flat looking placeholder."""

    width, height = size
    top_colour = (20, 24, 52)
    bottom_colour = (112, 93, 198)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(top_colour[0] + ratio * (bottom_colour[0] - top_colour[0]))
        g = int(top_colour[1] + ratio * (bottom_colour[1] - top_colour[1]))
        b = int(top_colour[2] + ratio * (bottom_colour[2] - top_colour[2]))
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def _draw_prompt_overlay(draw: ImageDraw.ImageDraw, size: Tuple[int, int], prompt: str) -> None:
    """Add the (truncated) prompt on top of a semi-transparent rectangle."""

    width, height = size
    overlay_height = int(height * 0.22)
    top = height - overlay_height
    draw.rectangle([(0, top), (width, height)], fill=(0, 0, 0, 160))

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=int(height * 0.045))
    except OSError:
        font = ImageFont.load_default()

    text = prompt.strip() or "Lo-Fi Midnight Café"
    max_chars = 120
    if len(text) > max_chars:
        text = text[: max_chars - 1] + "…"

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    position = ((width - text_width) / 2, top + (overlay_height - text_height) / 2)
    draw.text(position, text, fill=(240, 240, 255), font=font)


def _draw_centerpiece(draw: ImageDraw.ImageDraw, size: Tuple[int, int]) -> None:
    width, height = size
    radius = min(width, height) * 0.18
    cx, cy = width * 0.32, height * 0.58
    bbox = [
        (cx - radius, cy - radius),
        (cx + radius, cy + radius),
    ]
    draw.ellipse(bbox, fill=(255, 179, 71, 255))
    inner_radius = radius * 0.5
    draw.ellipse(
        [(cx - inner_radius, cy - inner_radius), (cx + inner_radius, cy + inner_radius)],
        fill=(90, 50, 30, 255),
    )

def generate_image_16x9(prompt: str, out_path: str) -> str:
    """Generate a deterministic placeholder illustration.

    Parameters
    ----------
    prompt:
        Text prompt describing the desired artwork.
    out_path:
        Destination path where the PNG should be stored.
    """

    path = Path(out_path)
    _ensure_parent_dir(path)

    image = Image.new("RGBA", DEFAULT_SIZE)
    draw = ImageDraw.Draw(image, "RGBA")
    _draw_background(draw, DEFAULT_SIZE)
    _draw_centerpiece(draw, DEFAULT_SIZE)
    _draw_prompt_overlay(draw, DEFAULT_SIZE, prompt)

    image.convert("RGB").save(path, format="PNG")
    return str(path)