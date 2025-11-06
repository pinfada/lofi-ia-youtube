import random
from pathlib import Path
from typing import Iterable


class AudioSelectionError(RuntimeError):
    """Raised when a playlist cannot be generated from the provided directory."""


def _list_mp3_files(directory: Path) -> list[Path]:
    if not directory.exists():
        raise AudioSelectionError(f"Audio directory '{directory}' does not exist")
    files = sorted(p for p in directory.iterdir() if p.suffix.lower() == ".mp3")
    if not files:
        raise AudioSelectionError(f"Audio directory '{directory}' does not contain any MP3 file")
    return files


def _choose_tracks(files: Iterable[Path], min_n: int, max_n: int) -> list[Path]:
    files = list(files)
    if min_n < 1:
        raise ValueError("min_n must be positive")
    if max_n < min_n:
        raise ValueError("max_n must be greater or equal to min_n")

    desired = random.randint(min_n, max_n)
    count = min(len(files), desired)
    return random.sample(files, count)


def select_audio_playlist(
    audiodir: str,
    min_n: int = 80,
    max_n: int = 200,
    list_file: str | None = None,
) -> tuple[str, list[str]]:
    """Generate a ffmpeg compatible playlist file.

    Parameters
    ----------
    audiodir:
        Directory containing MP3 files.
    min_n / max_n:
        Desired track count bounds.  The function gracefully falls back to the
        amount of available files when the library is small.
    list_file:
        Destination path for the temporary playlist file.  The default is a
        relative path in the current working directory.
    """

    directory = Path(audiodir)
    tracks = _choose_tracks(_list_mp3_files(directory), min_n, max_n)

    if list_file is None:
        playlist_path = directory / "playlist.txt"
    else:
        playlist_path = Path(list_file)
    playlist_path.parent.mkdir(parents=True, exist_ok=True)
    with playlist_path.open("w", encoding="utf-8") as fh:
        for track in tracks:
            fh.write(f"file '{track.as_posix()}'\n")

    return str(playlist_path), [track.name for track in tracks]