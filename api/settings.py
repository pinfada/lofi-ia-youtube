import os
from dotenv import load_dotenv
load_dotenv()

MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/data")
AUDIO_DIR = os.getenv("AUDIO_DIR", "/data/MP3_NORMALIZED")
LOOP_VIDEO = os.getenv("LOOP_VIDEO", "/data/loop_seamless.mp4")
INTRO_VIDEO = os.getenv("INTRO_VIDEO", "/app/static/intro.mp4")
OUTRO_VIDEO = os.getenv("OUTRO_VIDEO", "/app/static/outro.mp4")

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
PIKA_API_KEY = os.getenv("PIKA_API_KEY")
MUBERT_API_KEY = os.getenv("MUBERT_API_KEY")

DEFAULT_TITLE = os.getenv("DEFAULT_TITLE")
DEFAULT_DESCRIPTION = os.getenv("DEFAULT_DESCRIPTION")
DEFAULT_TAGS = os.getenv("DEFAULT_TAGS", "").split(",")
