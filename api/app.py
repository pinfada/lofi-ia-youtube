from fastapi import FastAPI
from tasks import generate_and_publish
from db import SessionLocal
from sqlalchemy import text

app = FastAPI(title="LoFi IA YouTube API", version="1.0.0")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/pipeline/run")
def run_pipeline():
    task = generate_and_publish.delay()
    return {"task_id": task.id, "status": "queued"}

@app.get("/events")
def list_events(limit: int = 50):
    db = SessionLocal()
    rows = db.execute(text("SELECT id, created_at, kind, status FROM events ORDER BY id DESC LIMIT :lim"), {"lim": limit}).fetchall()
    db.close()
    return [dict(r._mapping) for r in rows]
