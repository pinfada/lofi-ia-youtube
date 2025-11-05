import os, time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube"]

def youtube_client():
    creds = Credentials(None, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token",
                        client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)
    return build("youtube","v3", credentials=creds)

def upload_video(path: str, title: str, description: str, tags: list[str]) -> str:
    yt = youtube_client()
    insert = yt.videos().insert(
        part="snippet,status",
        body={"snippet":{"title":title,"description":description,"tags":tags,"categoryId":"10"},
              "status":{"privacyStatus":"public"}},
        media_body=path
    )
    resp = insert.execute()
    return resp["id"]

def set_thumbnail(video_id: str, thumbnail_path: str):
    yt = youtube_client()
    yt.thumbnails().set(videoId=video_id, media_body=thumbnail_path).execute()
