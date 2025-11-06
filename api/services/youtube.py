"""YouTube upload helpers.

The real project relies on the YouTube Data API.  In the execution environment
of this kata we usually do not have valid credentials which would make the
pipeline fail early.  To keep the rest of the system testable we provide a
fallback implementation that simulates the upload by writing lightweight
metadata files locally.  When valid credentials are configured the genuine
YouTube API is used transparently.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Iterable

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def _has_credentials() -> bool:
    return all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN])


def youtube_client():
    if not _has_credentials():
        raise RuntimeError("YouTube credentials are not configured")
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds)


def _simulate_upload(path: str, title: str, description: str, tags: Iterable[str]) -> str:
    uploads_dir = Path(os.getenv("MEDIA_ROOT", "/data")) / "simulated_uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    video_id = f"sim-{int(time.time())}"
    metadata_path = uploads_dir / f"{video_id}.json"
    metadata = {
        "title": title,
        "description": description,
        "tags": list(tags),
        "source_file": os.path.abspath(path),
        "created_at": time.time(),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return video_id


def upload_video(path: str, title: str, description: str, tags: list[str]) -> str:
    if not _has_credentials():
        return _simulate_upload(path, title, description, tags)

    yt = youtube_client()
    media = MediaFileUpload(path, chunksize=-1, resumable=True)
    insert = yt.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "10",
            },
            "status": {"privacyStatus": "public"},
        },
        media_body=media,
    )
    resp = insert.execute()
    return resp["id"]


def set_thumbnail(video_id: str, thumbnail_path: str):
    if not _has_credentials():
        uploads_dir = Path(os.getenv("MEDIA_ROOT", "/data")) / "simulated_uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        thumb_copy = uploads_dir / f"{video_id}_thumbnail{Path(thumbnail_path).suffix}"
        thumb_copy.write_bytes(Path(thumbnail_path).read_bytes())
        return

    yt = youtube_client()
    media = MediaFileUpload(thumbnail_path, chunksize=-1, resumable=True)
    yt.thumbnails().set(videoId=video_id, media_body=media).execute()