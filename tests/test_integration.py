"""
Integration tests for LoFi IA YouTube application.

These tests require actual database and Redis connections.
Run with: pytest -m integration
"""
import pytest
import os
from datetime import datetime
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
import redis


@pytest.fixture
def db_session():
    """
    Create a test database session.

    Yields:
        SQLAlchemy session for testing
    """
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://lofi:lofi@db:5432/lofi")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def redis_client():
    """
    Create a Redis client for testing.

    Yields:
        Redis client instance
    """
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    client = redis.from_url(redis_url)

    yield client

    # Cleanup test keys
    test_keys = client.keys("test:*")
    if test_keys:
        client.delete(*test_keys)


@pytest.mark.integration
def test_database_connection(db_session):
    """Test that database connection works."""
    result = db_session.execute(text("SELECT 1 as value"))
    row = result.fetchone()
    assert row[0] == 1


@pytest.mark.integration
def test_events_table_exists(db_session):
    """Test that events table exists and is accessible."""
    result = db_session.execute(
        text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'events')")
    )
    exists = result.fetchone()[0]
    assert exists is True


@pytest.mark.integration
def test_videos_table_exists(db_session):
    """Test that videos table exists and is accessible."""
    result = db_session.execute(
        text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'videos')")
    )
    exists = result.fetchone()[0]
    assert exists is True


@pytest.mark.integration
def test_insert_event(db_session):
    """Test inserting an event into the database."""
    db_session.execute(
        text(
            "INSERT INTO events (kind, status, payload) VALUES (:kind, :status, :payload)"
        ),
        {
            "kind": "test_integration",
            "status": "ok",
            "payload": '{"test": true, "timestamp": "2024-01-01T00:00:00Z"}'
        }
    )
    db_session.commit()

    # Verify insertion
    result = db_session.execute(
        text("SELECT COUNT(*) FROM events WHERE kind = 'test_integration'")
    )
    count = result.fetchone()[0]
    assert count >= 1

    # Cleanup
    db_session.execute(text("DELETE FROM events WHERE kind = 'test_integration'"))
    db_session.commit()


@pytest.mark.integration
def test_query_events(db_session):
    """Test querying events from the database."""
    # Insert test event
    db_session.execute(
        text(
            "INSERT INTO events (kind, status, payload) VALUES (:kind, :status, :payload)"
        ),
        {
            "kind": "test_query",
            "status": "ok",
            "payload": '{"action": "query_test"}'
        }
    )
    db_session.commit()

    # Query
    result = db_session.execute(
        text("SELECT id, kind, status, payload FROM events WHERE kind = 'test_query' LIMIT 1")
    )
    row = result.fetchone()

    assert row is not None
    assert row[1] == "test_query"  # kind
    assert row[2] == "ok"  # status

    # Cleanup
    db_session.execute(text("DELETE FROM events WHERE kind = 'test_query'"))
    db_session.commit()


@pytest.mark.integration
def test_redis_connection(redis_client):
    """Test that Redis connection works."""
    assert redis_client.ping() is True


@pytest.mark.integration
def test_redis_set_get(redis_client):
    """Test Redis SET and GET operations."""
    key = "test:simple_key"
    value = "test_value"

    # Set value
    redis_client.set(key, value)

    # Get value
    result = redis_client.get(key)
    assert result.decode('utf-8') == value

    # Cleanup
    redis_client.delete(key)


@pytest.mark.integration
def test_redis_expiration(redis_client):
    """Test Redis key expiration."""
    key = "test:expiring_key"
    value = "temporary_value"

    # Set with 1 second expiration
    redis_client.setex(key, 1, value)

    # Verify it exists
    assert redis_client.exists(key) == 1

    # Check TTL
    ttl = redis_client.ttl(key)
    assert ttl > 0 and ttl <= 1


@pytest.mark.integration
def test_redis_hash(redis_client):
    """Test Redis hash operations."""
    key = "test:hash_key"

    # Set hash fields
    redis_client.hset(key, "field1", "value1")
    redis_client.hset(key, "field2", "value2")

    # Get hash fields
    assert redis_client.hget(key, "field1").decode('utf-8') == "value1"
    assert redis_client.hget(key, "field2").decode('utf-8') == "value2"

    # Get all hash fields
    all_fields = redis_client.hgetall(key)
    assert len(all_fields) == 2

    # Cleanup
    redis_client.delete(key)


@pytest.mark.integration
def test_health_endpoint_with_real_services(client):
    """Test /health endpoint with real database and Redis connections."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # With real services running, all should be ok
    assert data["status"] in ["ok", "degraded"]
    assert data["database"] in ["ok", "error"]
    assert data["redis"] in ["ok", "error"]

    # At least one service should be working
    assert data["database"] == "ok" or data["redis"] == "ok"


@pytest.mark.integration
@pytest.mark.slow
def test_full_event_lifecycle(db_session):
    """Test complete event lifecycle: create, read, update, delete."""
    # Create
    db_session.execute(
        text(
            "INSERT INTO events (kind, status, payload) VALUES (:kind, :status, :payload) RETURNING id"
        ),
        {
            "kind": "test_lifecycle",
            "status": "pending",
            "payload": '{"step": 1}'
        }
    )
    db_session.commit()

    # Read
    result = db_session.execute(
        text("SELECT id, status FROM events WHERE kind = 'test_lifecycle'")
    )
    row = result.fetchone()
    event_id = row[0]
    assert row[1] == "pending"

    # Update
    db_session.execute(
        text("UPDATE events SET status = 'ok' WHERE id = :id"),
        {"id": event_id}
    )
    db_session.commit()

    # Verify update
    result = db_session.execute(
        text("SELECT status FROM events WHERE id = :id"),
        {"id": event_id}
    )
    assert result.fetchone()[0] == "ok"

    # Delete
    db_session.execute(
        text("DELETE FROM events WHERE id = :id"),
        {"id": event_id}
    )
    db_session.commit()

    # Verify deletion
    result = db_session.execute(
        text("SELECT COUNT(*) FROM events WHERE id = :id"),
        {"id": event_id}
    )
    assert result.fetchone()[0] == 0
