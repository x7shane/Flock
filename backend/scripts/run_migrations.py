"""
Run Alembic Migrations.

Usage:
    python -m scripts.run_migrations

This script runs Alembic migrations to set up the database schema.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from alembic import command
from alembic.config import Config


def run_migrations():
    """Run Alembic migrations."""
    # Get the alembic.ini file location
    alembic_ini = Path(__file__).resolve().parent.parent / "alembic.ini"

    if not alembic_ini.exists():
        print(f"Error: alembic.ini not found at {alembic_ini}")
        sys.exit(1)

    # Create Alembic config
    config = Config(str(alembic_ini))

    print("Running Alembic migrations...")
    print(f"Config file: {alembic_ini}")
    print("-" * 50)

    # Run migrations
    command.upgrade(config, "head")

    print("-" * 50)
    print("Migrations completed successfully.")


if __name__ == "__main__":
    run_migrations()
