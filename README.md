# 🎵 LoFi IA YouTube — Automatic Video Generator

[![CI/CD Pipeline](https://github.com/pinfada/lofi-ia-youtube/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/pinfada/lofi-ia-youtube/actions)
[![Tests](https://img.shields.io/badge/tests-34%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-~80%25-green)](tests/)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Automated system for generating and publishing Lo-Fi music videos to YouTube using AI services. Built with FastAPI, Celery, Docker, and comprehensive monitoring.

---

## ✨ Features

### Core Functionality
- 🤖 **AI-Powered Generation**: Automated image and video creation using OpenAI/Stability AI
- 🎬 **Complete Pipeline**: From audio selection to YouTube upload
- 📊 **Real-time Monitoring**: Grafana dashboards + Prometheus metrics
- 🔒 **Production Ready**: Rate limiting, logging, error handling
- ✅ **Fully Tested**: 34+ tests with ~80% coverage
- 🚀 **CI/CD Pipeline**: GitHub Actions with automated testing

### Technical Features
- 🛡️ **Rate Limiting**: Redis-based sliding window (configurable)
- 📝 **Structured Logging**: JSON formatted logs with context
- 📈 **Metrics**: Prometheus metrics for all operations
- 🔐 **Validated Config**: Pydantic-based configuration validation
- 🏥 **Health Checks**: DB and Redis connectivity monitoring
- 🔄 **Auto-scaling**: Docker Compose with replica support

---

## 📦 Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│            FastAPI Application              │
│  ┌─────────┬──────────┬──────────────────┐ │
│  │  Rate   │ Request  │   CORS/Security  │ │
│  │ Limiter │  Logger  │    Middleware    │ │
│  └─────────┴──────────┴──────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │   API Endpoints (/health, /metrics) │   │
│  │   ORM Models + Pydantic Validation  │   │
│  └─────────────────────────────────────┘   │
└──────────────┬─────────────┬────────────────┘
               │             │
       ┌───────┴─────┐   ┌──┴────────┐
       │  PostgreSQL │   │   Redis   │
       │  (Events +  │   │  (Cache + │
       │   Videos)   │   │   Queue)  │
       └─────────────┘   └───┬───────┘
                             │
                    ┌────────┴────────┐
                    │  Celery Worker  │
                    │   (Pipeline)    │
                    └─────────────────┘
                             │
                    ┌────────┴────────┐
                    │   Monitoring    │
                    │ Grafana + Prom  │
                    └─────────────────┘
```

**Components:**
- **API**: FastAPI server with REST endpoints + middleware
- **Worker**: Celery workers for async video pipeline
- **Redis**: Message broker + rate limiting cache
- **PostgreSQL**: Persistent storage (events, videos)
- **Grafana**: Visualization dashboards
- **Prometheus**: Metrics collection and alerting

---

## 🚀 Quick Start

### Prerequisites

- Docker ≥ 24.0
- Docker Compose ≥ 2.20
- API keys (OpenAI, YouTube, etc.)

### 1. Clone & Configure

```bash
# Clone repository
git clone https://github.com/pinfada/lofi-ia-youtube.git
cd lofi-ia-youtube

# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### 2. Start Services

```bash
# Development mode
make up

# Or with docker compose directly
docker compose up -d

# Production mode
docker compose -f docker-compose.prod.yml up -d
```

### 3. Initialize Database

```bash
# Migrations run automatically on first start
# Or manually:
docker compose exec db psql -U lofi -d lofi -f /docker-entrypoint-initdb.d/01-init.sql
```

### 4. Generate Static Assets

```bash
# Inside Docker container (recommended)
docker compose exec api bash /app/scripts/generate_static_assets.sh

# Or with Python locally
python3 scripts/generate_static_assets.py
```

### 5. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| API Docs | http://localhost:8000/docs | - |
| API Health | http://localhost:8000/health | - |
| Metrics | http://localhost:8000/metrics | - |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |

---

## 🎬 Usage

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "database": "ok",
  "redis": "ok",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Run Video Pipeline

```bash
curl -X POST http://localhost:8000/pipeline/run
```

**Response:**
```json
{
  "task_id": "abc-123-def-456",
  "status": "queued"
}
```

**Pipeline Steps:**
1. 🎨 Generate AI image (16:9 Lo-Fi café scene)
2. 🎞️ Create or use animated video loop
3. 🎵 Select 80-120 random audio tracks
4. 🔊 Concatenate audio files
5. 🎬 Render final video with intro/outro
6. 🖼️ Generate custom thumbnail
7. 📤 Upload to YouTube with metadata

### List Events

```bash
# Default: 50 events
curl http://localhost:8000/events

# Custom limit (1-1000)
curl http://localhost:8000/events?limit=100
```

### View Metrics

```bash
# Prometheus format
curl http://localhost:8000/metrics
```

**Available Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `pipeline_runs_total` - Pipeline executions
- `youtube_uploads_total` - YouTube uploads
- `rate_limit_hits_total` - Rate limit violations
- `errors_total` - Error occurrences

---

## 🧪 Testing

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Or inside Docker
docker compose exec api pytest
```

### Test Categories

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests (requires DB/Redis)
pytest -m integration

# Smoke tests
pytest -m smoke

# With coverage report
pytest --cov=api --cov-report=html
open htmlcov/index.html
```

### Test Statistics

- **Total Tests**: 34
- **Unit Tests**: 24
- **Integration Tests**: 10
- **Coverage**: ~80%
- **Files Tested**: `api/`, `models.py`, `schemas.py`

---

## 🛠 Development

### Project Structure

```
lofi-ia-youtube/
├── api/                    # FastAPI application
│   ├── app.py             # Main FastAPI app (236 lines)
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic validation schemas
│   ├── config.py          # Validated configuration
│   ├── middleware.py      # Rate limiting, logging, CORS
│   ├── metrics.py         # Prometheus metrics
│   ├── logger.py          # Structured logging
│   ├── db.py              # Database connection
│   ├── tasks.py           # Celery tasks
│   ├── services/          # AI service integrations
│   │   ├── images.py      # Image generation
│   │   ├── music.py       # Audio selection
│   │   ├── animate.py     # Video animation
│   │   ├── thumbnails.py  # Thumbnail rendering
│   │   └── youtube.py     # YouTube upload
│   └── static/            # Static assets (intro/outro)
├── worker/                # Celery worker
├── tests/                 # Test suite (34 tests)
│   ├── test_api.py        # API endpoint tests
│   ├── test_models.py     # ORM model tests
│   ├── test_schemas.py    # Schema validation tests
│   └── test_integration.py # Integration tests
├── grafana/               # Monitoring dashboards
├── prometheus/            # Metrics configuration
├── scripts/               # Utility scripts
│   ├── generate_static_assets.py
│   └── generate_static_assets.sh
├── .github/workflows/     # CI/CD pipelines
│   └── ci.yml             # GitHub Actions
├── docker-compose.yml     # Development setup
├── docker-compose.prod.yml # Production setup
├── pytest.ini             # Test configuration
├── IMPROVEMENTS.md        # Detailed improvements doc
├── DEPLOYMENT.md          # Deployment guide
└── README.md              # This file
```

### Access Containers

```bash
# API container
make api
# or: docker compose exec api bash

# Worker container
make worker
# or: docker compose exec worker bash

# Database
docker compose exec db psql -U lofi -d lofi
```

### View Logs

```bash
# All services
make logs

# Specific service
docker compose logs -f api
docker compose logs -f worker

# Filter errors
docker compose logs api | grep ERROR
```

### Development Commands

```bash
# Rebuild containers
make rebuild

# Clean everything
make down
docker system prune -a

# Generate test data
./scripts/dev_seed_audio.sh
./scripts/dev_seed_images.sh

# Run tests
pytest -v

# Check code style
black --check api tests
flake8 api
isort --check api tests
```

---

## 📊 Monitoring & Observability

### Grafana Dashboards

Access Grafana at **http://localhost:3000** (admin/admin)

**Pre-configured Dashboards:**
- Pipeline execution timeline
- Video generation metrics
- API performance (latency, throughput)
- Error rates and types
- System resources (CPU, memory, disk)

### Prometheus Metrics

Access Prometheus at **http://localhost:9090**

**Key Metrics:**
- Request rates by endpoint
- P50/P95/P99 latency percentiles
- Pipeline success/failure rates
- YouTube upload durations
- Database query performance
- Redis operation latency

### Structured Logging

All logs are JSON-formatted with:
- Timestamp
- Log level
- Logger name
- Message
- Additional context (user_id, task_id, etc.)

**Example:**
```
timestamp=2024-01-01T12:00:00Z level=INFO logger=lofi_ia_youtube message="Pipeline started" task_id=abc-123 client_ip=192.168.1.1
```

---

## 🔧 Configuration

### Environment Variables

See [.env.example](.env.example) for all available options.

**Critical Variables:**

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ENVIRONMENT` | Environment (development/production) | No | development |
| `DATABASE_URL` | PostgreSQL connection URL | Yes | - |
| `REDIS_URL` | Redis connection URL | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes* | - |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth client ID | Yes* | - |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Rate limit per IP | No | 60 |
| `LOG_LEVEL` | Logging level | No | INFO |

*Required for full functionality; graceful fallbacks in development

### Configuration Validation

The application uses Pydantic for configuration validation:

```python
from config import get_settings

settings = get_settings()

# Validated at startup
# Invalid values raise clear errors
# Type-safe access: settings.database_url
```

---

## 🚀 Deployment

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

**Quick Production Start:**

```bash
# 1. Create production env file
cp .env.example .env.production

# 2. Configure production values
nano .env.production

# 3. Deploy
docker compose -f docker-compose.prod.yml up -d --build

# 4. Verify
curl https://your-domain.com/health
```

### Cloud Platforms

- **AWS**: ECS + RDS + ElastiCache
- **Google Cloud**: Cloud Run + Cloud SQL
- **DigitalOcean**: App Platform
- **Azure**: Container Instances + Azure Database

See [DEPLOYMENT.md](DEPLOYMENT.md) for platform-specific guides.

---

## 🔐 Security

### Security Features

- ✅ **Rate Limiting**: Per-IP sliding window (default: 60 req/min)
- ✅ **CORS Protection**: Configurable allowed origins
- ✅ **Security Headers**: HSTS, X-Frame-Options, CSP
- ✅ **Input Validation**: Pydantic schemas on all endpoints
- ✅ **SQL Injection Prevention**: ORM-based queries
- ✅ **XSS Protection**: Response sanitization
- ✅ **Secrets Management**: Environment variables only

### Best Practices

1. **Never commit secrets** - Use `.env` files (gitignored)
2. **Rotate API keys** regularly
3. **Use strong passwords** for DB/Redis/Grafana
4. **Enable HTTPS** in production (see Nginx config)
5. **Limit /metrics** endpoint to internal network
6. **Monitor for anomalies** in Grafana

---

## 📝 API Documentation

### Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Endpoints

| Method | Endpoint | Description | Rate Limited |
|--------|----------|-------------|--------------|
| GET | `/health` | Health check | ❌ |
| GET | `/metrics` | Prometheus metrics | ❌ |
| GET | `/events` | List events | ✅ |
| POST | `/pipeline/run` | Trigger pipeline | ✅ |

### Rate Limiting

Default: **60 requests/minute per IP**

**Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Reset time (Unix timestamp)

**Response (429 Too Many Requests):**
```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "limit": 60,
  "window": "60 seconds",
  "retry_after": 60
}
```

---

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### Code Quality

- **Tests**: Add tests for new features
- **Coverage**: Maintain >80% coverage
- **Style**: Follow PEP 8 (use `black` + `flake8`)
- **Documentation**: Update docs for API changes

---

## 📚 Documentation

- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Detailed list of all improvements
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[tests/README.md](tests/README.md)** - Testing guide
- **[api/static/README.md](api/static/README.md)** - Static assets guide

---

## 📊 Metrics & Stats

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **API Code** | 22 lines | 260 lines | +1082% |
| **Test Coverage** | 0% | ~80% | +80% |
| **Tests** | 0 | 34 | ∞ |
| **Python Files** | 10 | 20 | +100% |
| **Documentation** | Basic | Complete | ✅ |

---

## 🔑 Required API Keys

1. **OpenAI** - https://platform.openai.com/api-keys
2. **Stability AI** (optional) - https://platform.stability.ai/
3. **Pika Labs** (optional) - https://pika.art/
4. **Mubert** (optional) - https://mubert.com/
5. **YouTube Data API** - https://console.cloud.google.com/

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

Copyright © 2025 pinfada

---

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Celery for distributed task queue
- Docker for containerization
- Prometheus & Grafana for monitoring
- All open-source contributors

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/pinfada/lofi-ia-youtube/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pinfada/lofi-ia-youtube/discussions)
- **Documentation**: See docs above

---

**Built with ❤️ by pinfada**
