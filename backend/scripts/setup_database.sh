#!/bin/bash
# Database Setup Script for Flock
#
# Usage:
#   ./scripts/setup_database.sh [--seed]
#
# Options:
#   --seed    Seed the database with Nifty 200 stocks after setup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

echo "========================================"
echo "Flock Database Setup"
echo "========================================"
echo ""

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "Error: Docker daemon is not running"
    exit 1
fi

# Start PostgreSQL container
echo "Step 1: Starting PostgreSQL container..."
cd ..
docker compose up -d db
echo "Waiting for PostgreSQL to be ready..."

# Wait for PostgreSQL to be healthy
for i in {1..30}; do
    if docker exec flock-postgres pg_isready -U flock -d flock_db &> /dev/null; then
        echo "PostgreSQL is ready!"
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

# Check if database is ready
if ! docker exec flock-postgres pg_isready -U flock -d flock_db &> /dev/null; then
    echo "Error: PostgreSQL failed to start"
    exit 1
fi

echo ""
echo "Step 2: Running database migrations..."
cd "$BACKEND_DIR"
python -m scripts.run_migrations

echo ""
echo "Step 3: Initializing database..."
if [[ "$1" == "--seed" ]]; then
    echo "Seeding Nifty 200 stocks..."
    python -m scripts.init_db --seed
else
    echo "Database ready. Use --seed to populate Nifty 200 stocks."
fi

echo ""
echo "========================================"
echo "Database setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Start the backend API: uvicorn app.main:app --reload"
echo "  2. Run the data pipeline: python -m app.pipelines.daily_pipeline"
echo "  3. Open the explorer: http://localhost:8000/explorer.html"
echo ""
