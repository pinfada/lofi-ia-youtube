import subprocess

def concat_audio_from_list(list_file: str, out_audio: str = "audio.mp3"):
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", out_audio], check=True)
    return out_audio

def probe_duration(filepath: str) -> float:
    res = subprocess.run([
        "ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", filepath
    ], capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def loop_video_to_duration(loop_src: str, audio_src: str, output: str, intro: str = None, outro: str = None):
    import math, os, tempfile
    dur = probe_duration(audio_src)
    base_cmd = ["ffmpeg","-y","-stream_loop","-1","-i", loop_src, "-t", str(dur), "-i", audio_src, "-shortest",
                "-c:v","libx264","-c:a","aac", output]
    if not intro and not outro:
        subprocess.run(base_cmd, check=True)
        return output
    # intro/outro concat v:
    tmp_video_fd, tmp_video = tempfile.mkstemp(suffix=".mp4", prefix="tmp_video_")
    os.close(tmp_video_fd)
    concat_video_fd, concat_video = tempfile.mkstemp(suffix=".mp4", prefix="concat_video_")
    os.close(concat_video_fd)
    try:
        subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i", loop_src, "-t", str(dur), "-c:v","libx264","-an", tmp_video], check=True)
        parts = []
        if intro: parts += ["-i", intro]
        parts += ["-i", tmp_video]
        if outro: parts += ["-i", outro]
        fc = []
        n = 0
        if intro: n += 1
        n += 1
        if outro: n += 1
        fc = ["-filter_complex", f"concat=n={n}:v=1:a=0[v]","-map","[v]"]
        subprocess.run(["ffmpeg","-y"] + parts + fc + [concat_video], check=True)
        subprocess.run(["ffmpeg","-y","-i",concat_video,"-i", audio_src,"-shortest","-c:v","libx264","-c:a","aac", output], check=True)
    finally:
        # Clean up temporary files
        if os.path.exists(tmp_video):
            os.unlink(tmp_video)
        if os.path.exists(concat_video):
            os.unlink(concat_video)
    return output
