import os, random

def select_audio_playlist(audiodir: str, min_n=80, max_n=200, list_file="playlist.txt"):
    files = [f for f in os.listdir(audiodir) if f.lower().endswith(".mp3")]
    n = min(len(files), random.randint(min_n, max_n))
    selected = random.sample(files, n)
    with open(list_file,"w") as f:
        for s in selected:
            f.write(f"file '{os.path.join(audiodir, s)}'\n")
    return list_file, selected
