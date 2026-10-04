from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from settings import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def log_event(db, kind: str, payload: dict, status: str = "ok"):
    import json
    db.execute(
        text("INSERT INTO events(kind, payload, status) VALUES (:k, CAST(:p AS JSONB), :s)"),
        {"k": kind, "p": json.dumps(payload, default=str), "s": status},
    )
    db.commit()
