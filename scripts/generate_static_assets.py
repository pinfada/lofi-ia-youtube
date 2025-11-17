#!/usr/bin/env python3
"""
Generate basic static assets (intro/outro videos and thumbnail template).
This script creates simple placeholder assets using FFmpeg and Pillow.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Add api directory to path to import ffmpeg_utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

try:
    import ffmpeg
except ImportError:
    print("Error: ffmpeg-python not installed. Run: pip install ffmpeg-python")
    sys.exit(1)


def create_intro_video(output_path: str, duration: int = 3):
    """
    Create a simple intro video with fade-in effect.

    Args:
        output_path: Path to save the intro video
        duration: Duration in seconds
    """
    print(f"Creating intro video: {output_path}")

    # Create a black video with "Lo-Fi IA YouTube" text
    (
        ffmpeg
        .input(f'color=c=black:s=1920x1080:d={duration}', f='lavfi')
        .drawtext(
            text='Lo-Fi IA YouTube',
            fontsize=72,
            fontcolor='white',
            x='(w-text_w)/2',
            y='(h-text_h)/2',
            fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        )
        .filter('fade', type='in', duration=1)
        .output(output_path, pix_fmt='yuv420p', t=duration)
        .overwrite_output()
        .run(quiet=True)
    )
    print(f"✓ Intro video created ({duration}s)")


def create_outro_video(output_path: str, duration: int = 3):
    """
    Create a simple outro video with fade-out effect.

    Args:
        output_path: Path to save the outro video
        duration: Duration in seconds
    """
    print(f"Creating outro video: {output_path}")

    # Create a black video with "Subscribe for more!" text
    (
        ffmpeg
        .input(f'color=c=black:s=1920x1080:d={duration}', f='lavfi')
        .drawtext(
            text='Subscribe for more Lo-Fi beats!',
            fontsize=56,
            fontcolor='white',
            x='(w-text_w)/2',
            y='(h-text_h)/2',
            fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        )
        .filter('fade', type='out', start_time=duration-1, duration=1)
        .output(output_path, pix_fmt='yuv420p', t=duration)
        .overwrite_output()
        .run(quiet=True)
    )
    print(f"✓ Outro video created ({duration}s)")


def create_thumbnail_template(output_path: str):
    """
    Create a basic thumbnail template image.

    Args:
        output_path: Path to save the thumbnail template
    """
    print(f"Creating thumbnail template: {output_path}")

    # Create 1280x720 image with gradient background
    width, height = 1280, 720
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Draw gradient background (dark blue to purple)
    for y in range(height):
        r = int(30 + (80 - 30) * y / height)
        g = int(30 + (50 - 30) * y / height)
        b = int(80 + (120 - 80) * y / height)
        draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

    # Add decorative elements
    # Draw semi-transparent overlay
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
    img.paste(overlay, (0, 0), overlay)

    # Add border
    border_width = 10
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=(255, 255, 255),
        width=3
    )

    # Add placeholder text in center
    try:
        # Try to use a nice font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
        small_font = font

    text = "Lo-Fi Beats"
    subtitle = "Study • Relax • Sleep"

    # Calculate text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2 - 40

    # Draw text with shadow
    shadow_offset = 3
    draw.text((text_x + shadow_offset, text_y + shadow_offset), text, fill=(0, 0, 0), font=font)
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

    # Draw subtitle
    bbox2 = draw.textbbox((0, 0), subtitle, font=small_font)
    sub_width = bbox2[2] - bbox2[0]
    sub_x = (width - sub_width) // 2
    sub_y = text_y + text_height + 20

    draw.text((sub_x + 2, sub_y + 2), subtitle, fill=(0, 0, 0), font=small_font)
    draw.text((sub_x, sub_y), subtitle, fill=(200, 200, 255), font=small_font)

    # Save the image
    img.save(output_path, 'PNG', quality=95)
    print(f"✓ Thumbnail template created (1280x720)")


def main():
    """Generate all static assets."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    static_dir = os.path.join(project_root, "api", "static")
    templates_dir = os.path.join(static_dir, "templates")

    # Ensure directories exist
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)

    print("=" * 60)
    print("Generating Static Assets")
    print("=" * 60)

    # Generate intro video
    intro_path = os.path.join(static_dir, "intro.mp4")
    create_intro_video(intro_path, duration=3)

    # Generate outro video
    outro_path = os.path.join(static_dir, "outro.mp4")
    create_outro_video(outro_path, duration=3)

    # Generate thumbnail template
    template_path = os.path.join(templates_dir, "thumbnail_template.png")
    create_thumbnail_template(template_path)

    print("=" * 60)
    print("✓ All static assets generated successfully!")
    print("=" * 60)
    print(f"\nGenerated files:")
    print(f"  - {intro_path}")
    print(f"  - {outro_path}")
    print(f"  - {template_path}")


if __name__ == "__main__":
    main()
