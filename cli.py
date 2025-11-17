#!/usr/bin/env python3
"""
Admin CLI for LoFi IA YouTube management.

Usage:
    python cli.py user create <username> <email> <password> [--admin]
    python cli.py user list
    python cli.py pipeline run [--async]
    python cli.py pipeline status
    python cli.py cache clear [namespace]
    python cli.py db migrate
    python cli.py db upgrade
    python cli.py stats
"""
import sys
import os
import click
from datetime import datetime

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))


@click.group()
def cli():
    """LoFi IA YouTube Admin CLI."""
    pass


@cli.group()
def user():
    """User management commands."""
    pass


@user.command("create")
@click.argument("username")
@click.argument("email")
@click.argument("password")
@click.option("--admin", is_flag=True, help="Create as admin user")
def create_user(username: str, email: str, password: str, admin: bool):
    """Create a new user."""
    from auth import get_password_hash, fake_users_db

    role = "admin" if admin else "user"
    user_id = str(len(fake_users_db) + 1)

    fake_users_db[username] = {
        "id": user_id,
        "username": username,
        "email": email,
        "role": role,
        "hashed_password": get_password_hash(password),
        "is_active": True,
    }

    click.echo(f"✓ User '{username}' created (role: {role})")


@user.command("list")
def list_users():
    """List all users."""
    from auth import fake_users_db

    click.echo("\nUsers:")
    click.echo("-" * 60)

    for username, user_data in fake_users_db.items():
        click.echo(f"  {user_data['id']:3s} | {username:15s} | {user_data['email']:30s} | {user_data['role']:10s}")

    click.echo(f"\nTotal: {len(fake_users_db)} users")


@cli.group()
def pipeline():
    """Pipeline management commands."""
    pass


@pipeline.command("run")
@click.option("--async", "async_mode", is_flag=True, help="Run asynchronously")
def run_pipeline(async_mode: bool):
    """Run the video generation pipeline."""
    from tasks import generate_and_publish

    click.echo("🎬 Starting pipeline...")

    if async_mode:
        task = generate_and_publish.delay()
        click.echo(f"✓ Pipeline queued (task_id: {task.id})")
    else:
        click.echo("⚠️  Running synchronously (this may take a while)...")
        try:
            result = generate_and_publish()
            click.echo(f"✓ Pipeline completed: {result}")
        except Exception as e:
            click.echo(f"✗ Pipeline failed: {e}", err=True)
            sys.exit(1)


@pipeline.command("status")
def pipeline_status():
    """Check pipeline status from database."""
    from db import SessionLocal
    from sqlalchemy import text

    db = SessionLocal()

    try:
        # Get recent pipeline events
        result = db.execute(
            text("SELECT id, created_at, status, payload FROM events WHERE kind = 'pipeline' ORDER BY id DESC LIMIT 10")
        )
        events = result.fetchall()

        if not events:
            click.echo("No pipeline executions found.")
            return

        click.echo("\nRecent Pipeline Executions:")
        click.echo("-" * 80)

        for event in events:
            payload = event[3] if len(event) > 3 else {}
            status_icon = "✓" if event[2] == "ok" else "✗"
            click.echo(f"{status_icon} [{event[1]}] Status: {event[2]}")

            if payload and isinstance(payload, dict):
                if "video_id" in payload:
                    click.echo(f"   Video ID: {payload['video_id']}")
                if "error" in payload:
                    click.echo(f"   Error: {payload['error']}")

        click.echo(f"\nTotal: {len(events)} recent executions")

    finally:
        db.close()


@cli.group()
def cache():
    """Cache management commands."""
    pass


@cache.command("clear")
@click.argument("namespace", required=False)
def clear_cache(namespace: str = None):
    """Clear cache for a namespace or all caches."""
    from cache import cache as redis_cache

    if namespace:
        deleted = redis_cache.delete_pattern(namespace, "*")
        click.echo(f"✓ Cleared cache for namespace '{namespace}' ({deleted} keys deleted)")
    else:
        # Clear all cache namespaces
        deleted = redis_cache.delete_pattern("cache", "*")
        click.echo(f"✓ Cleared all caches ({deleted} keys deleted)")


@cache.command("stats")
def cache_stats():
    """Show cache statistics."""
    from cache import cache as redis_cache

    if not redis_cache.client:
        click.echo("✗ Redis not available", err=True)
        return

    try:
        info = redis_cache.client.info("stats")

        click.echo("\nRedis Cache Statistics:")
        click.echo("-" * 60)
        click.echo(f"  Total keys: {redis_cache.client.dbsize()}")
        click.echo(f"  Total connections: {info.get('total_connections_received', 'N/A')}")
        click.echo(f"  Total commands: {info.get('total_commands_processed', 'N/A')}")
        click.echo(f"  Keyspace hits: {info.get('keyspace_hits', 'N/A')}")
        click.echo(f"  Keyspace misses: {info.get('keyspace_misses', 'N/A')}")

        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses

        if total > 0:
            hit_rate = (hits / total) * 100
            click.echo(f"  Hit rate: {hit_rate:.2f}%")

    except Exception as e:
        click.echo(f"✗ Error getting cache stats: {e}", err=True)


@cli.group()
def db():
    """Database management commands."""
    pass


@db.command("migrate")
@click.option("-m", "--message", required=True, help="Migration message")
def create_migration(message: str):
    """Create a new database migration."""
    import subprocess

    click.echo(f"Creating migration: {message}")

    try:
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            capture_output=True,
            text=True,
            check=True
        )
        click.echo(result.stdout)
        click.echo("✓ Migration created")
    except subprocess.CalledProcessError as e:
        click.echo(f"✗ Migration failed: {e.stderr}", err=True)
        sys.exit(1)


@db.command("upgrade")
@click.option("--revision", default="head", help="Revision to upgrade to")
def upgrade_db(revision: str):
    """Upgrade database to a revision."""
    import subprocess

    click.echo(f"Upgrading database to {revision}...")

    try:
        result = subprocess.run(
            ["alembic", "upgrade", revision],
            capture_output=True,
            text=True,
            check=True
        )
        click.echo(result.stdout)
        click.echo("✓ Database upgraded")
    except subprocess.CalledProcessError as e:
        click.echo(f"✗ Upgrade failed: {e.stderr}", err=True)
        sys.exit(1)


@db.command("current")
def current_revision():
    """Show current database revision."""
    import subprocess

    try:
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            check=True
        )
        click.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        click.echo(f"✗ Error: {e.stderr}", err=True)
        sys.exit(1)


@cli.command()
def stats():
    """Show system statistics."""
    from db import SessionLocal
    from sqlalchemy import text

    db = SessionLocal()

    try:
        # Get event counts
        result = db.execute(text("SELECT kind, status, COUNT(*) FROM events GROUP BY kind, status"))
        event_stats = result.fetchall()

        # Get video count
        result = db.execute(text("SELECT COUNT(*) FROM videos"))
        video_count = result.fetchone()[0]

        click.echo("\n" + "=" * 60)
        click.echo("System Statistics")
        click.echo("=" * 60)

        click.echo("\nEvents:")
        click.echo("-" * 60)
        for row in event_stats:
            click.echo(f"  {row[0]:15s} | {row[1]:10s} | {row[2]:5d}")

        click.echo(f"\nVideos:")
        click.echo("-" * 60)
        click.echo(f"  Total videos: {video_count}")

        click.echo("\n" + "=" * 60)

    finally:
        db.close()


@cli.command()
def health():
    """Check system health."""
    from db import SessionLocal
    from sqlalchemy import text
    import redis
    from settings import REDIS_URL

    checks = []

    # Check database
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks.append(("Database", "✓ OK", "green"))
    except Exception as e:
        checks.append(("Database", f"✗ Error: {e}", "red"))

    # Check Redis
    try:
        r = redis.from_url(REDIS_URL, socket_connect_timeout=2)
        r.ping()
        checks.append(("Redis", "✓ OK", "green"))
    except Exception as e:
        checks.append(("Redis", f"✗ Error: {e}", "red"))

    click.echo("\n" + "=" * 60)
    click.echo("System Health Check")
    click.echo("=" * 60)

    for name, status, color in checks:
        click.echo(f"  {name:15s}: {status}")

    click.echo("=" * 60 + "\n")

    # Exit with error if any check failed
    if any(status.startswith("✗") for _, status, _ in checks):
        sys.exit(1)


if __name__ == "__main__":
    cli()
