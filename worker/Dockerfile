FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1
# Le worker monte le code de /api en volume (docker-compose)
CMD ["celery", "-A", "tasks", "worker", "--loglevel=INFO"]
