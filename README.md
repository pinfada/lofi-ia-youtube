# 🎵 LoFi IA YouTube — Automatic Video Generator

Automated system for generating and publishing Lo-Fi music videos to YouTube using AI services.

## 📦 Architecture

- **API**: FastAPI server with REST endpoints
- **Worker**: Celery workers for video pipeline processing
- **Redis**: Message broker for task queue
- **PostgreSQL**: Database for events and video metadata
- **Grafana**: Monitoring dashboard

## 🚀 Quick Start

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your API keys and credentials

3. Start the services:
```bash
make up
```

4. Access services:
- API: http://localhost:8000
- Grafana: http://localhost:3000 (admin/admin)

## 🎬 Usage

### Check API health:
```bash
curl http://localhost:8000/health
```

### Run the video generation pipeline:
```bash
curl -X POST http://localhost:8000/pipeline/run
```

This will:
1. Generate an AI image (16:9 aspect ratio)
2. Use or create an animated video loop
3. Select and concatenate 80-120 random audio tracks
4. Render the final video with intro/outro
5. Generate a custom thumbnail
6. Upload to YouTube with metadata

### Check events:
```bash
curl http://localhost:8000/events
```

### Check specific event count:
```bash
curl http://localhost:8000/events?limit=100
```

## 🛠 Development

### Access containers:
```bash
make api     # API container shell
make worker  # Worker container shell
```

### View logs:
```bash
make logs
```

### Rebuild:
```bash
make rebuild
```

### Development test data:
Generate sample audio files and video loops for testing:
```bash
./scripts/dev_seed_audio.sh    # Creates test MP3 files
./scripts/dev_seed_images.sh   # Creates test video loop
```

## 📁 Project Structure

```
lofi-ia-youtube/
├─ api/                 # FastAPI application
│  ├─ services/        # AI service integrations
│  └─ static/          # Static assets (intro/outro)
├─ worker/             # Celery worker
├─ grafana/            # Monitoring setup
├─ scripts/            # Development utilities
└─ data/               # Generated content (mounted volume)
```

## 🔑 Required API Keys

- OpenAI (image generation)
- Stability AI (alternative image generation)
- Pika (video animation)
- Mubert (music generation)
- YouTube Data API (video upload)

## 🎥 Video Pipeline

The automated pipeline performs the following steps:

1. **Image Generation**: Creates a 16:9 anime-style Lo-Fi café scene using AI
2. **Video Loop**: Uses pre-existing seamless video loop or generates animation
3. **Audio Playlist**: Randomly selects 80-120 tracks from the audio library
4. **Audio Concatenation**: Merges selected tracks into a single audio file
5. **Video Rendering**: Combines video loop with audio, adds intro/outro
6. **Thumbnail Creation**: Generates custom thumbnail with title overlay
7. **YouTube Upload**: Publishes video with metadata and custom thumbnail

Each pipeline execution is logged to the database for monitoring and analytics.

## 📊 Monitoring

Access Grafana at http://localhost:3000 to monitor:
- Pipeline execution events
- Video generation status
- System health

## 📝 License

See LICENSE file for details.
