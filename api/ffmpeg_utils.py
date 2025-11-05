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
    import math, os
    dur = probe_duration(audio_src)
    base_cmd = ["ffmpeg","-y","-stream_loop","-1","-i", loop_src, "-t", str(dur), "-i", audio_src, "-shortest",
                "-c:v","libx264","-c:a","aac", output]
    if not intro and not outro:
        subprocess.run(base_cmd, check=True)
        return output
    # intro/outro concat v:
    tmp_video = "tmp_video.mp4"
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
    subprocess.run(["ffmpeg","-y"] + parts + fc + ["concat_video.mp4"], check=True)
    subprocess.run(["ffmpeg","-y","-i","concat_video.mp4","-i", audio_src,"-shortest","-c:v","libx264","-c:a","aac", output], check=True)
    return output
