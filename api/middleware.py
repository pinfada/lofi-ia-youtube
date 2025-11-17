"""
Middleware components for the LoFi IA YouTube API.
"""
import time
import redis
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime

from logger import app_logger, log_with_context
from settings import REDIS_URL


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis.

    Implements a sliding window rate limiter to prevent API abuse.
    """

    def __init__(self, app, redis_url: str = None, requests_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            redis_url: Redis connection URL
            requests_per_minute: Maximum requests allowed per minute per IP
        """
        super().__init__(app)
        self.redis_url = redis_url or REDIS_URL
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 60 seconds

        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_available = True
            app_logger.info("Rate limiting enabled with Redis")
        except Exception as e:
            self.redis_available = False
            log_with_context(
                app_logger,
                "warning",
                "Rate limiting disabled - Redis unavailable",
                error=str(e)
            )

    def get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.

        Args:
            request: FastAPI request object

        Returns:
            Client IP address
        """
        # Check for X-Forwarded-For header (when behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response or rate limit error
        """
        # Skip rate limiting if Redis is not available
        if not self.redis_available:
            return await call_next(request)

        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = self.get_client_ip(request)
        key = f"rate_limit:{client_ip}"
        current_time = int(time.time())

        try:
            # Get current request count
            pipe = self.redis_client.pipeline()

            # Remove old entries outside the time window
            pipe.zremrangebyscore(key, 0, current_time - self.window_size)

            # Count requests in current window
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {str(current_time): current_time})

            # Set expiration
            pipe.expire(key, self.window_size)

            results = pipe.execute()
            request_count = results[1]  # Result from zcard

            # Check if rate limit exceeded
            if request_count >= self.requests_per_minute:
                log_with_context(
                    app_logger,
                    "warning",
                    "Rate limit exceeded",
                    client_ip=client_ip,
                    request_count=request_count,
                    limit=self.requests_per_minute,
                    path=request.url.path
                )

                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Please try again later.",
                        "limit": self.requests_per_minute,
                        "window": f"{self.window_size} seconds",
                        "retry_after": self.window_size
                    },
                    headers={
                        "Retry-After": str(self.window_size),
                        "X-RateLimit-Limit": str(self.requests_per_minute),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(current_time + self.window_size)
                    }
                )

            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, self.requests_per_minute - request_count - 1)
            )
            response.headers["X-RateLimit-Reset"] = str(current_time + self.window_size)

            return response

        except Exception as e:
            # If Redis fails, allow request but log error
            log_with_context(
                app_logger,
                "error",
                "Rate limiting error",
                client_ip=client_ip,
                error=str(e)
            )
            return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response details.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response from handler
        """
        # Start timing
        start_time = time.time()

        # Extract request details
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None

        # Log incoming request
        log_with_context(
            app_logger,
            "info",
            "Incoming request",
            method=method,
            path=path,
            client_ip=client_ip,
            query_params=query_params
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            log_with_context(
                app_logger,
                "info",
                "Request completed",
                method=method,
                path=path,
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2),
                client_ip=client_ip
            )

            # Add processing time header
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))

            return response

        except Exception as e:
            # Log errors
            process_time = time.time() - start_time
            log_with_context(
                app_logger,
                "error",
                "Request failed",
                method=method,
                path=path,
                error=str(e),
                process_time_ms=round(process_time * 1000, 2),
                client_ip=client_ip
            )
            raise


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS and security headers middleware.
    """

    def __init__(self, app, allowed_origins: list = None):
        """
        Initialize CORS middleware.

        Args:
            app: FastAPI application
            allowed_origins: List of allowed origins (default: ["*"])
        """
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to response.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response with security headers
        """
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # CORS headers
        origin = request.headers.get("origin")
        if origin and (self.allowed_origins == ["*"] or origin in self.allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        return response
