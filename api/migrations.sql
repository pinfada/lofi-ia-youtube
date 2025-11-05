CREATE TABLE IF NOT EXISTS events (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  kind TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ok',
  payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS videos (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  title TEXT,
  description TEXT,
  tags TEXT[],
  duration_sec INTEGER,
  file_path TEXT,
  youtube_video_id TEXT,
  status TEXT NOT NULL DEFAULT 'pending'
);
