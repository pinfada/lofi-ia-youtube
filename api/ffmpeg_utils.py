import os
import subprocess
import tempfile

# Every segment is normalised to this format so the concat filter accepts them
# even when intro/outro and the loop were produced with different settings.
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30


def concat_audio_from_list(list_file: str, out_audio: str = "audio.mp3"):
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", out_audio], check=True)
    return out_audio


def probe_duration(filepath: str) -> float:
    res = subprocess.run([
        "ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", filepath
    ], capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def _is_valid_video(path: str) -> bool:
    """Return True if ``path`` exists and ffprobe can read a duration from it."""
    if not path or not os.path.isfile(path):
        return False
    try:
        return probe_duration(path) > 0
    except (subprocess.CalledProcessError, ValueError):
        return False


def _normalize_filter(index: int) -> str:
    return (
        f"[{index}:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
        f"fps={VIDEO_FPS},format=yuv420p[v{index}]"
    )


def loop_video_to_duration(loop_src: str, audio_src: str, output: str, intro: str = None, outro: str = None):
    dur = probe_duration(audio_src)
    # Missing or placeholder intro/outro files are skipped instead of breaking the render.
    intro = intro if _is_valid_video(intro) else None
    outro = outro if _is_valid_video(outro) else None

    if not intro and not outro:
        subprocess.run([
            "ffmpeg","-y","-stream_loop","-1","-i", loop_src, "-i", audio_src,
            "-map","0:v:0","-map","1:a:0","-t", str(dur),
            "-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac", output,
        ], check=True)
        return output

    # The loop fills the time left once intro/outro are accounted for, so the
    # final video matches the audio length and the outro is not cut off.
    extra = (probe_duration(intro) if intro else 0) + (probe_duration(outro) if outro else 0)
    loop_dur = max(dur - extra, 1.0)

    tmp_video_fd, tmp_video = tempfile.mkstemp(suffix=".mp4", prefix="tmp_video_")
    os.close(tmp_video_fd)
    concat_video_fd, concat_video = tempfile.mkstemp(suffix=".mp4", prefix="concat_video_")
    os.close(concat_video_fd)
    try:
        subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", loop_src, "-t", str(loop_dur), "-c:v","libx264","-an", tmp_video], check=True)
        inputs = [p for p in (intro, tmp_video, outro) if p]
        parts = []
        for path in inputs:
            parts += ["-i", path]
        filters = [_normalize_filter(i) for i in range(len(inputs))]
        labels = "".join(f"[v{i}]" for i in range(len(inputs)))
        filters.append(f"{labels}concat=n={len(inputs)}:v=1:a=0[v]")
        fc = ["-filter_complex", ";".join(filters), "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p"]
        subprocess.run(["ffmpeg","-y"] + parts + fc + [concat_video], check=True)
        subprocess.run([
            "ffmpeg","-y","-i",concat_video,"-i", audio_src,
            "-map","0:v:0","-map","1:a:0","-t", str(dur),
            "-c:v","copy","-c:a","aac", output,
        ], check=True)
    finally:
        # Clean up temporary files
        if os.path.exists(tmp_video):
            os.unlink(tmp_video)
        if os.path.exists(concat_video):
            os.unlink(concat_video)
    return output
