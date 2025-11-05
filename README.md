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

### Run the video generation pipeline:
```bash
curl -X POST http://localhost:8000/pipeline/run
```

### Check events:
```bash
curl http://localhost:8000/events
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

## 📊 Monitoring

Access Grafana at http://localhost:3000 to monitor:
- Pipeline execution events
- Video generation status
- System health

## 📝 License

See LICENSE file for details.
