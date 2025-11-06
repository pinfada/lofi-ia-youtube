"""Thumbnail generation helpers used for development and testing."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _load_base_image(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    if image.width < 1280 or image.height < 720:
        image = image.resize((1280, 720))
    return image


def _draw_text(image: Image.Image, title: str) -> None:
    draw = ImageDraw.Draw(image)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    bar_height = int(image.height * 0.28)
    overlay_draw.rectangle(
        [(0, image.height - bar_height), (image.width, image.height)],
        fill=(16, 16, 30, 200),
    )

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=int(image.height * 0.09))
    except OSError:
        font = ImageFont.load_default()

    text = title.strip() or "Lo-Fi Midnight Café"
    max_chars = 60
    if len(text) > max_chars:
        text = text[: max_chars - 1] + "…"

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    position = ((image.width - text_width) / 2, image.height - bar_height + (bar_height - text_height) / 2)
    overlay_draw.text(position, text, font=font, fill=(245, 238, 219, 255))

    blurred = overlay.filter(ImageFilter.GaussianBlur(radius=4))
    image.paste(blurred, (0, 0), blurred)


def render_thumbnail(base_image: str, title: str, out_path: str) -> str:
    """Create a simple thumbnail derived from the generated illustration."""

    base_path = Path(base_image)
    output_path = Path(out_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = _load_base_image(base_path)
    _draw_text(image, title)
    image.save(output_path, format="JPEG", quality=90)
    return str(output_path)