"""
Prometheus metrics for monitoring the LoFi IA YouTube application.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from functools import wraps
import time


# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    ['method', 'endpoint']
)

# Pipeline metrics
pipeline_runs_total = Counter(
    'pipeline_runs_total',
    'Total number of pipeline executions',
    ['status']
)

pipeline_duration_seconds = Histogram(
    'pipeline_duration_seconds',
    'Pipeline execution duration in seconds',
    buckets=[30, 60, 120, 300, 600, 1800, 3600]  # 30s to 1h
)

pipeline_steps_duration_seconds = Histogram(
    'pipeline_steps_duration_seconds',
    'Duration of individual pipeline steps',
    ['step_name'],
    buckets=[1, 5, 10, 30, 60, 120, 300]  # 1s to 5min
)

# Video generation metrics
videos_generated_total = Counter(
    'videos_generated_total',
    'Total number of videos generated',
    ['status']
)

video_duration_seconds = Gauge(
    'video_duration_seconds',
    'Duration of the last generated video in seconds'
)

video_file_size_bytes = Gauge(
    'video_file_size_bytes',
    'Size of the last generated video in bytes'
)

# YouTube upload metrics
youtube_uploads_total = Counter(
    'youtube_uploads_total',
    'Total number of YouTube uploads',
    ['status']
)

youtube_upload_duration_seconds = Histogram(
    'youtube_upload_duration_seconds',
    'YouTube upload duration in seconds',
    buckets=[10, 30, 60, 120, 300, 600, 1800]  # 10s to 30min
)

# Database metrics
db_queries_total = Counter(
    'db_queries_total',
    'Total number of database queries',
    ['query_type', 'status']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

# Redis metrics
redis_operations_total = Counter(
    'redis_operations_total',
    'Total number of Redis operations',
    ['operation', 'status']
)

redis_operation_duration_seconds = Histogram(
    'redis_operation_duration_seconds',
    'Redis operation duration in seconds',
    ['operation']
)

# Celery metrics
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total number of Celery tasks',
    ['task_name', 'status']
)

celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name'],
    buckets=[30, 60, 300, 600, 1800, 3600, 7200]  # 30s to 2h
)

# Error metrics
errors_total = Counter(
    'errors_total',
    'Total number of errors',
    ['error_type', 'endpoint']
)

# Rate limiting metrics
rate_limit_hits_total = Counter(
    'rate_limit_hits_total',
    'Total number of rate limit hits',
    ['endpoint']
)


def track_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    """
    Track HTTP request metrics.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        status_code: HTTP status code
        duration: Request duration in seconds
    """
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status_code=status_code
    ).inc()

    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)


def track_pipeline_step(step_name: str, duration: float):
    """
    Track individual pipeline step duration.

    Args:
        step_name: Name of the pipeline step
        duration: Step duration in seconds
    """
    pipeline_steps_duration_seconds.labels(
        step_name=step_name
    ).observe(duration)


def track_error(error_type: str, endpoint: str):
    """
    Track error occurrence.

    Args:
        error_type: Type/class of error
        endpoint: Endpoint where error occurred
    """
    errors_total.labels(
        error_type=error_type,
        endpoint=endpoint
    ).inc()


def timer_metric(metric_histogram, labels: dict = None):
    """
    Decorator to time function execution and record to histogram.

    Args:
        metric_histogram: Prometheus Histogram metric
        labels: Optional labels for the metric

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric_histogram.labels(**labels).observe(duration)
                else:
                    metric_histogram.observe(duration)
        return wrapper
    return decorator


def get_metrics() -> Response:
    """
    Generate Prometheus metrics response.

    Returns:
        Response with Prometheus metrics in text format
    """
    metrics_output = generate_latest()
    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST
    )
