"""
Unit tests for pipeline helpers (DB logging, playlist, thumbnails, ffmpeg rendering).
"""
import shutil
import subprocess

import pytest

requires_ffmpeg = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg/ffprobe not installed",
)


@pytest.mark.unit
def test_log_event_binds_payload_parameter():
    """The payload must be a real bind parameter (':p::jsonb' silently was not)."""
    from unittest.mock import MagicMock

    from db import log_event

    db = MagicMock()
    log_event(db, "pipeline", {"video_id": "abc"}, "ok")

    statement, params = db.execute.call_args[0]
    assert set(statement.compile().params) == {"k", "p", "s"}
    assert params["p"] == '{"video_id": "abc"}'
    db.commit.assert_called_once()


@pytest.mark.unit
def test_settings_have_usable_defaults():
    import settings

    assert settings.DATABASE_URL
    assert settings.REDIS_URL
    assert settings.DEFAULT_TITLE
    assert settings.DEFAULT_DESCRIPTION
    assert "" not in settings.DEFAULT_TAGS


@pytest.mark.unit
def test_playlist_escapes_single_quotes(tmp_path):
    from services.music import select_audio_playlist

    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    (audio_dir / "it's chill.mp3").write_bytes(b"")
    playlist = tmp_path / "playlist.txt"

    path, tracks = select_audio_playlist(str(audio_dir), 1, 1, str(playlist))

    assert tracks == ["it's chill.mp3"]
    content = (tmp_path / "playlist.txt").read_text(encoding="utf-8")
    assert content == f"file '{(audio_dir / 'it').as_posix()}'\\''s chill.mp3'\n"


@pytest.mark.unit
def test_thumbnail_is_youtube_sized(tmp_path):
    from PIL import Image

    from services.images import generate_image_16x9
    from services.thumbnails import render_thumbnail

    frame = generate_image_16x9("lofi cafe", str(tmp_path / "frame.png"))
    thumb = render_thumbnail(frame, "A very long title " * 5, str(tmp_path / "thumb.jpg"))

    assert Image.open(thumb).size == (1280, 720)


def _make_video(path, seconds, size="640x360", rate=25):
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi",
         "-i", f"testsrc2=size={size}:rate={rate}:duration={seconds}",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)],
        check=True,
    )
    return str(path)


def _make_audio(path, seconds):
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi",
         "-i", f"sine=frequency=440:duration={seconds}", "-c:a", "libmp3lame", str(path)],
        check=True,
    )
    return str(path)


@pytest.mark.unit
@requires_ffmpeg
def test_render_with_mismatched_intro_outro(tmp_path):
    """Intro/outro with another resolution/fps must not break the concat, nor be cut off."""
    from ffmpeg_utils import loop_video_to_duration, probe_duration

    loop = _make_video(tmp_path / "loop.mp4", 2)
    intro = _make_video(tmp_path / "intro.mp4", 1, size="1920x1080", rate=30)
    outro = _make_video(tmp_path / "outro.mp4", 1, size="1280x720", rate=24)
    audio = _make_audio(tmp_path / "audio.mp3", 6)
    out = str(tmp_path / "out.mp4")

    loop_video_to_duration(loop, audio, out, intro=intro, outro=outro)

    assert probe_duration(out) == pytest.approx(probe_duration(audio), abs=0.3)


@pytest.mark.unit
@requires_ffmpeg
def test_render_skips_invalid_intro(tmp_path):
    from ffmpeg_utils import loop_video_to_duration, probe_duration

    loop = _make_video(tmp_path / "loop.mp4", 2)
    audio = _make_audio(tmp_path / "audio.mp3", 3)
    placeholder = tmp_path / "intro.mp4"
    placeholder.write_text("Placeholder")
    out = str(tmp_path / "out.mp4")

    loop_video_to_duration(loop, audio, out, intro=str(placeholder), outro=str(tmp_path / "missing.mp4"))

    assert probe_duration(out) == pytest.approx(3, abs=0.3)
