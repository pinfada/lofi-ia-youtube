import os, datetime
from celery import Celery
from settings import REDIS_URL, AUDIO_DIR, LOOP_VIDEO, INTRO_VIDEO, OUTRO_VIDEO, DEFAULT_TITLE, DEFAULT_DESCRIPTION, DEFAULT_TAGS
from db import SessionLocal, log_event
from services.music import select_audio_playlist
from services.images import generate_image_16x9
from services.animate import animate_to_loop
from services.thumbnails import render_thumbnail
from services.youtube import upload_video, set_thumbnail
from ffmpeg_utils import concat_audio_from_list, loop_video_to_duration

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

@celery.task(name="pipeline.generate_and_publish")
def generate_and_publish():
    db = SessionLocal()
    try:
        date_tag = datetime.date.today().isoformat()
        # 1) Image
        img_path = f"/data/frame_{date_tag}.png"
        generate_image_16x9("lofi cafe at night, anime style, warm lights, rain, 16:9", img_path)

        # 2) Animation loop (ou utiliser un loop pre-existant)
        loop_path = LOOP_VIDEO  # sinon: animate_to_loop(img_path, "/data/loop.mp4", 6)

        # 3) Playlist audio
        playlist_file, tracks = select_audio_playlist(AUDIO_DIR, 80, 120)

        # 4) Concat audio
        audio_path = "/data/audio.mp3"
        concat_audio_from_list(playlist_file, audio_path)

        # 5) Rendu vidéo
        out_video = f"/data/lofi_{date_tag}.mp4"
        loop_video_to_duration(loop_path, audio_path, out_video, intro=INTRO_VIDEO, outro=OUTRO_VIDEO)

        # 6) Thumbnail
        thumb_path = f"/data/thumb_{date_tag}.jpg"
        render_thumbnail(img_path, DEFAULT_TITLE, thumb_path)

        # 7) Upload YouTube
        video_id = upload_video(out_video, f"{DEFAULT_TITLE} | {date_tag}", DEFAULT_DESCRIPTION, DEFAULT_TAGS)
        set_thumbnail(video_id, thumb_path)

        log_event(db, "pipeline", {"video_id": video_id, "file": out_video, "tracks": tracks}, "ok")
        return {"status": "ok", "video_id": video_id}
    except Exception as e:
        log_event(db, "pipeline", {"error": str(e)}, "error")
        raise
    finally:
        db.close()
