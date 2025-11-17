# 🚀 Guide de Déploiement - Lo-Fi IA YouTube

Ce guide détaille les différentes méthodes de déploiement du projet Lo-Fi IA YouTube.

## 📋 Table des Matières

- [Prérequis](#prérequis)
- [Déploiement Local (Développement)](#déploiement-local-développement)
- [Déploiement Docker (Production)](#déploiement-docker-production)
- [Déploiement sur Cloud](#déploiement-sur-cloud)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

---

## Prérequis

### Logiciels Requis

- **Docker** ≥ 24.0
- **Docker Compose** ≥ 2.20
- **Git** ≥ 2.30
- **Python** 3.11+ (pour développement local)
- **FFmpeg** (installé automatiquement dans les conteneurs)

### API Keys Requises

1. **OpenAI** - https://platform.openai.com/api-keys
2. **Stability AI** (optionnel) - https://platform.stability.ai/
3. **Pika Labs** (optionnel) - https://pika.art/
4. **YouTube Data API** - https://console.cloud.google.com/
5. **Mubert** (optionnel) - https://mubert.com/

---

## Déploiement Local (Développement)

### 1. Cloner le Projet

```bash
git clone https://github.com/pinfada/lofi-ia-youtube.git
cd lofi-ia-youtube
```

### 2. Configuration

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer avec vos clés API
nano .env
```

### 3. Lancer les Services

```bash
# Démarrer tous les services
make up

# Ou avec docker compose directement
docker compose up -d
```

### 4. Initialiser la Base de Données

```bash
# Exécuter les migrations
docker compose exec api bash
psql -h db -U lofi -d lofi -f /app/migrations.sql
exit
```

### 5. Générer les Assets Statiques

```bash
# Dans le conteneur API
docker compose exec api bash /app/scripts/generate_static_assets.sh
```

### 6. Tester l'Installation

```bash
# Health check
curl http://localhost:8000/health

# Documentation API
open http://localhost:8000/docs

# Grafana
open http://localhost:3000
# Login: admin / admin
```

### 7. Lancer le Pipeline

```bash
# Déclencher une génération de vidéo
curl -X POST http://localhost:8000/pipeline/run
```

---

## Déploiement Docker (Production)

### Architecture Production

```
┌─────────────────┐
│  Load Balancer  │ (Nginx/Traefik)
│   (Port 80/443) │
└────────┬────────┘
         │
    ┌────┴────┐
    │   API   │ (x2+ instances)
    │ FastAPI │
    └────┬────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │  Redis  │ Postgres │  Worker  │
    │ (Cache) │   (DB)   │ (Celery) │
    └─────────┴──────────┴──────────┘
```

### 1. Configuration Production

Créer `.env.production`:

```bash
# Production environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=30

# Database (utiliser des credentials sécurisés)
DATABASE_URL=postgresql+psycopg2://lofi:STRONG_PASSWORD@db:5432/lofi

# Redis
REDIS_URL=redis://:REDIS_PASSWORD@redis:6379/0

# API Keys (vos vraies clés)
OPENAI_API_KEY=sk-...
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
YOUTUBE_REFRESH_TOKEN=...

# Storage
MEDIA_ROOT=/data
AUDIO_DIR=/data/MP3_NORMALIZED
LOOP_VIDEO=/data/loop_seamless.mp4

# SEO
DEFAULT_TITLE=Lo-Fi Midnight Café — Beats to Study, Chill & Sleep
DEFAULT_DESCRIPTION=Chill beats for studying, relaxing or sleeping.
DEFAULT_TAGS=lofi,study beats,relax,chill,focus,deep work
```

### 2. Docker Compose Production

Créer `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    restart: always
    env_file:
      - .env.production
    volumes:
      - ./data:/data
    depends_on:
      - db
      - redis
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  worker:
    build:
      context: ./worker
      dockerfile: Dockerfile
    restart: always
    env_file:
      - .env.production
    volumes:
      - ./api:/app
      - ./data:/data
    depends_on:
      - db
      - redis
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '4.0'
          memory: 4G

  db:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_USER: lofi
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: lofi
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api

  grafana:
    image: grafana/grafana:11.1.0
    restart: always
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
      GF_INSTALL_PLUGINS: grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  grafana_data:
```

### 3. Configuration Nginx

Créer `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        least_conn;
        server api:8000 max_fails=3 fail_timeout=30s;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect to HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;

        # API endpoints
        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Metrics endpoint (restrict access)
        location /metrics {
            allow 10.0.0.0/8;  # Internal network
            deny all;
            proxy_pass http://api;
        }
    }
}
```

### 4. Déployer en Production

```bash
# Build et démarrage
docker compose -f docker-compose.prod.yml up -d --build

# Vérifier les logs
docker compose -f docker-compose.prod.yml logs -f

# Vérifier le health check
curl https://your-domain.com/health
```

---

## Déploiement sur Cloud

### AWS (ECS + RDS + ElastiCache)

1. **Infrastructure as Code** (Terraform)

```hcl
# main.tf
resource "aws_ecs_cluster" "lofi" {
  name = "lofi-ia-youtube"
}

resource "aws_db_instance" "postgres" {
  engine         = "postgres"
  engine_version = "16.0"
  instance_class = "db.t3.medium"
  allocated_storage = 20
  # ... autres configs
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id      = "lofi-redis"
  engine          = "redis"
  node_type       = "cache.t3.micro"
  num_cache_nodes = 1
}
```

2. **Déployer**

```bash
terraform init
terraform plan
terraform apply
```

### Google Cloud (Cloud Run + Cloud SQL)

```bash
# Build et push l'image
gcloud builds submit --tag gcr.io/PROJECT_ID/lofi-api

# Déployer sur Cloud Run
gcloud run deploy lofi-api \
  --image gcr.io/PROJECT_ID/lofi-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=... \
  --allow-unauthenticated
```

### DigitalOcean (App Platform)

1. Connecter le repo GitHub
2. Configurer les variables d'environnement
3. Déployer automatiquement

---

## Configuration

### Variables d'Environnement Critiques

| Variable | Description | Requis | Défaut |
|----------|-------------|--------|--------|
| `ENVIRONMENT` | Environment (development/production) | Oui | development |
| `DATABASE_URL` | PostgreSQL connection URL | Oui | - |
| `REDIS_URL` | Redis connection URL | Oui | - |
| `OPENAI_API_KEY` | OpenAI API key | Oui | - |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth client ID | Oui | - |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Rate limit | Non | 60 |

### Secrets Management

**Option 1: Docker Secrets**

```bash
echo "sk-your-api-key" | docker secret create openai_key -
```

**Option 2: AWS Secrets Manager**

```bash
aws secretsmanager create-secret \
  --name lofi/openai-key \
  --secret-string "sk-your-api-key"
```

**Option 3: HashiCorp Vault**

```bash
vault kv put secret/lofi openai_key="sk-your-api-key"
```

---

## Monitoring

### Métriques Prometheus

Accéder aux métriques:

```bash
curl http://localhost:8000/metrics
```

Métriques disponibles:
- `http_requests_total` - Total requests
- `http_request_duration_seconds` - Request latency
- `pipeline_runs_total` - Pipeline executions
- `youtube_uploads_total` - YouTube uploads
- `rate_limit_hits_total` - Rate limit violations

### Dashboards Grafana

Importer le dashboard pré-configuré:

1. Accéder à Grafana (http://localhost:3000)
2. Import → Load dashboard
3. Sélectionner `grafana/provisioning/dashboards/dashboard.json`

### Alertes

Configurer des alertes pour:
- Taux d'erreur > 5%
- Latence moyenne > 1s
- Échec de pipeline
- Espace disque < 10%

---

## Maintenance

### Sauvegardes

**Base de données:**

```bash
# Backup
docker compose exec db pg_dump -U lofi lofi > backup_$(date +%Y%m%d).sql

# Restore
cat backup.sql | docker compose exec -T db psql -U lofi lofi
```

**Volumes:**

```bash
# Backup volumes
docker run --rm -v lofi_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data
```

### Mise à Jour

```bash
# Pull les dernières modifications
git pull origin main

# Rebuild et redémarrage
docker compose down
docker compose up -d --build

# Appliquer les migrations
docker compose exec api python manage.py migrate
```

### Rotation des Logs

Configurer logrotate:

```bash
/var/log/lofi/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

---

## Troubleshooting

### Problèmes Courants

**1. L'API ne démarre pas**

```bash
# Vérifier les logs
docker compose logs api

# Vérifier les variables d'environnement
docker compose exec api env | grep DATABASE_URL
```

**2. Pipeline échoue**

```bash
# Vérifier les logs du worker
docker compose logs worker

# Vérifier Celery
docker compose exec worker celery -A tasks inspect active
```

**3. Problèmes de connexion DB**

```bash
# Tester la connexion
docker compose exec api psql $DATABASE_URL

# Vérifier que la DB est initialisée
docker compose exec db psql -U lofi -d lofi -c "\dt"
```

**4. Rate limiting trop restrictif**

```bash
# Ajuster dans .env
RATE_LIMIT_REQUESTS_PER_MINUTE=120

# Redémarrer l'API
docker compose restart api
```

### Commandes Utiles

```bash
# Voir tous les conteneurs
docker compose ps

# Logs en temps réel
docker compose logs -f --tail=100

# Accéder à un conteneur
docker compose exec api bash

# Nettoyer les ressources
docker compose down -v
docker system prune -a

# Vérifier l'utilisation des ressources
docker stats
```

### Logs et Debugging

**Augmenter le niveau de log:**

```bash
# Dans .env
LOG_LEVEL=DEBUG

# Redémarrer
docker compose restart api worker
```

**Analyser les logs:**

```bash
# Filtrer les erreurs
docker compose logs api | grep ERROR

# Exporter les logs
docker compose logs --no-color > logs_$(date +%Y%m%d).txt
```

---

## Checklist de Déploiement

### Pré-déploiement

- [ ] Toutes les API keys sont configurées
- [ ] Les tests passent (`pytest`)
- [ ] Les migrations DB sont prêtes
- [ ] Les assets statiques sont générés
- [ ] Le fichier .env.production est configuré
- [ ] Les sauvegardes sont configurées

### Déploiement

- [ ] Build des images Docker
- [ ] Démarrage des services
- [ ] Vérification du health check
- [ ] Exécution des migrations
- [ ] Test du pipeline
- [ ] Configuration du monitoring

### Post-déploiement

- [ ] Monitoring actif (Grafana)
- [ ] Alertes configurées
- [ ] Logs centralisés
- [ ] Documentation à jour
- [ ] Équipe informée

---

## Support

Pour toute question ou problème:

1. Consulter la [documentation](/README.md)
2. Vérifier les [issues GitHub](https://github.com/pinfada/lofi-ia-youtube/issues)
3. Créer une nouvelle issue avec:
   - Version du projet
   - Logs d'erreur
   - Configuration (sans les secrets!)
   - Étapes pour reproduire

---

## Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
