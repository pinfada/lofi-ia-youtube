import os
from dotenv import load_dotenv
load_dotenv()

MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/data")
AUDIO_DIR = os.getenv("AUDIO_DIR", "/data/MP3_NORMALIZED")
LOOP_VIDEO = os.getenv("LOOP_VIDEO", "/data/loop_seamless.mp4")
INTRO_VIDEO = os.getenv("INTRO_VIDEO", "/app/static/intro.mp4")
OUTRO_VIDEO = os.getenv("OUTRO_VIDEO", "/app/static/outro.mp4")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://lofi:lofi@db:5432/lofi")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
PIKA_API_KEY = os.getenv("PIKA_API_KEY")
MUBERT_API_KEY = os.getenv("MUBERT_API_KEY")

DEFAULT_TITLE = os.getenv("DEFAULT_TITLE") or "Lo-Fi Midnight Café — Beats to Study, Chill & Sleep"
DEFAULT_DESCRIPTION = (
    os.getenv("DEFAULT_DESCRIPTION")
    or "Chill beats for studying, relaxing or sleeping. New mixes regularly."
)
DEFAULT_TAGS = [
    tag.strip()
    for tag in os.getenv("DEFAULT_TAGS", "lofi,study beats,relax,chill,focus,deep work").split(",")
    if tag.strip()
]
