"""
FastAPI application for LoFi IA YouTube automated video generation.
"""
from datetime import datetime
from typing import List
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import redis

from tasks import generate_and_publish
from db import SessionLocal
from models import Event
from schemas import (
    HealthResponse,
    PipelineRunResponse,
    EventResponse,
    ErrorResponse,
)
from settings import REDIS_URL
from logger import app_logger, log_with_context
from middleware import RateLimitMiddleware, RequestLoggingMiddleware, CORSSecurityMiddleware
from metrics import get_metrics
from auth import (
    LoginRequest,
    Token,
    authenticate_user,
    create_tokens,
    get_current_user,
    get_current_active_user,
    require_admin,
    TokenData,
)

# Initialize FastAPI with rich documentation
app = FastAPI(
    title="LoFi IA YouTube API",
    version="1.0.0",
    description="Automated Lo-Fi video generation and YouTube publishing pipeline",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware (order matters - first added is executed last)
app.add_middleware(CORSSecurityMiddleware, allowed_origins=["*"])
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, redis_url=REDIS_URL, requests_per_minute=60)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors with structured response."""
    log_with_context(
        app_logger,
        "warning",
        "Validation error",
        path=str(request.url),
        errors=str(exc.errors()),
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors."""
    log_with_context(
        app_logger,
        "error",
        "Unexpected error",
        path=str(request.url),
        error=str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API and its dependencies (database, Redis)",
    tags=["System"],
)
def health():
    """
    Perform comprehensive health check.

    Verifies connectivity to:
    - PostgreSQL database
    - Redis message broker

    Returns:
        HealthResponse with status of each component
    """
    health_status = {
        "status": "ok",
        "database": "unknown",
        "redis": "unknown",
        "timestamp": datetime.utcnow(),
    }

    # Check database
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "ok"
        app_logger.info("Database health check passed")
    except SQLAlchemyError as e:
        health_status["database"] = "error"
        health_status["status"] = "degraded"
        log_with_context(app_logger, "error", "Database health check failed", error=str(e))

    # Check Redis
    try:
        r = redis.from_url(REDIS_URL, socket_connect_timeout=2)
        r.ping()
        health_status["redis"] = "ok"
        app_logger.info("Redis health check passed")
    except Exception as e:
        health_status["redis"] = "error"
        health_status["status"] = "degraded"
        log_with_context(app_logger, "error", "Redis health check failed", error=str(e))

    return health_status


@app.post(
    "/pipeline/run",
    response_model=PipelineRunResponse,
    summary="Run Video Pipeline",
    description="Trigger the complete video generation and publishing pipeline",
    tags=["Pipeline"],
)
def run_pipeline():
    """
    Trigger the video generation pipeline.

    The pipeline performs the following steps:
    1. Generate AI image (16:9 Lo-Fi café scene)
    2. Create or use animated video loop
    3. Select 80-120 random audio tracks
    4. Concatenate audio files
    5. Render final video with intro/outro
    6. Generate custom thumbnail
    7. Upload to YouTube with metadata

    Returns:
        PipelineRunResponse with Celery task ID and status

    Raises:
        HTTPException: If pipeline cannot be started
    """
    try:
        task = generate_and_publish.delay()
        log_with_context(
            app_logger,
            "info",
            "Pipeline started",
            task_id=str(task.id),
        )
        return {"task_id": task.id, "status": "queued"}
    except Exception as e:
        log_with_context(
            app_logger,
            "error",
            "Failed to start pipeline",
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=f"Failed to start pipeline: {str(e)}")


@app.get(
    "/events",
    response_model=List[EventResponse],
    summary="List Events",
    description="Retrieve recent pipeline execution events",
    tags=["Monitoring"],
)
def list_events(
    limit: int = Query(
        50,
        ge=1,
        le=1000,
        description="Maximum number of events to return",
    )
):
    """
    List recent events from the database.

    Args:
        limit: Maximum number of events to return (1-1000)

    Returns:
        List of event records ordered by creation date (newest first)

    Raises:
        HTTPException: If database query fails
    """
    try:
        db = SessionLocal()
        rows = db.execute(
            text("SELECT id, created_at, kind, status FROM events ORDER BY id DESC LIMIT :lim"),
            {"lim": limit},
        ).fetchall()
        db.close()

        events = [dict(r._mapping) for r in rows]
        log_with_context(
            app_logger,
            "info",
            "Events retrieved",
            count=len(events),
            limit=limit,
        )
        return events

    except SQLAlchemyError as e:
        log_with_context(
            app_logger,
            "error",
            "Failed to retrieve events",
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get(
    "/metrics",
    summary="Prometheus Metrics",
    description="Prometheus metrics endpoint for monitoring",
    tags=["Monitoring"],
    include_in_schema=False,  # Hide from OpenAPI docs
)
def metrics():
    """
    Expose Prometheus metrics.

    Returns:
        Prometheus metrics in text format
    """
    return get_metrics()


@app.post(
    "/auth/login",
    response_model=Token,
    summary="Login",
    description="Authenticate and get JWT tokens",
    tags=["Authentication"],
)
def login(credentials: LoginRequest):
    """
    Authenticate user and return JWT tokens.

    Args:
        credentials: Login credentials (username + password)

    Returns:
        Token with access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        log_with_context(
            app_logger,
            "warning",
            "Failed login attempt",
            username=credentials.username
        )
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = create_tokens(user)
    log_with_context(
        app_logger,
        "info",
        "User logged in",
        username=user.username,
        role=user.role
    )

    return tokens


@app.get(
    "/auth/me",
    response_model=TokenData,
    summary="Get Current User",
    description="Get information about the current authenticated user",
    tags=["Authentication"],
)
async def read_users_me(current_user: TokenData = Depends(get_current_active_user)):
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        TokenData with user information
    """
    return current_user


@app.post(
    "/auth/refresh",
    response_model=Token,
    summary="Refresh Token",
    description="Refresh access token using refresh token",
    tags=["Authentication"],
)
async def refresh_token(current_user: TokenData = Depends(get_current_user)):
    """
    Refresh access token.

    Args:
        current_user: Current user from token

    Returns:
        New token pair
    """
    # In production, validate refresh token type and revocation
    # For now, just create new tokens
    from auth import fake_users_db, UserInDB

    user_dict = fake_users_db.get(current_user.username)
    if not user_dict:
        raise HTTPException(status_code=401, detail="User not found")

    user = UserInDB(**user_dict)
    tokens = create_tokens(user)

    return tokens


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    app_logger.info("LoFi IA YouTube API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    app_logger.info("LoFi IA YouTube API shutting down")
