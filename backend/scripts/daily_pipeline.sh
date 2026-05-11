#!/usr/bin/env bash
# =============================================================================
#  Flock — Daily Data Pipeline
#  Runs after NSE/BSE market close (3:30 PM IST) every Mon–Fri.
#
#  Schedule: 4:00 PM IST (10:30 UTC) — Mon to Fri
#  Cron:     30 10 * * 1-5
#
#  Logs:     backend/logs/pipeline_YYYY-MM-DD.log
#            backend/logs/pipeline_latest.log  (always the most recent)
#  Retention: 30 days
# =============================================================================

set -euo pipefail

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
FLOCK_DIR="$(dirname "$BACKEND_DIR")"
VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"
LOG_DIR="$BACKEND_DIR/logs"
DATE=$(date +"%Y-%m-%d")
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S IST")
LOG_FILE="$LOG_DIR/pipeline_${DATE}.log"
LATEST_LOG="$LOG_DIR/pipeline_latest.log"

# ── Setup logs directory ──────────────────────────────────────────────────────
mkdir -p "$LOG_DIR"

# ── Redirect all output to log ───────────────────────────────────────────────
exec > >(tee -a "$LOG_FILE") 2>&1

echo ""
echo "============================================================"
echo "  FLOCK DAILY PIPELINE — $TIMESTAMP"
echo "============================================================"

# ── Step 1: Ensure Docker is running ─────────────────────────────────────────
echo ""
echo "[PRE-CHECK] Docker container status..."
if ! docker ps --format '{{.Names}}' | grep -q "^flock-postgres$"; then
    echo "  ⚠️  flock-postgres is not running. Attempting to start..."
    docker compose -f "$FLOCK_DIR/docker-compose.yml" up -d db
    echo "  Waiting 15s for DB to become healthy..."
    sleep 15

    if ! docker ps --format '{{.Names}}' | grep -q "^flock-postgres$"; then
        echo "  ❌ Failed to start flock-postgres. Aborting pipeline."
        exit 1
    fi
fi
echo "  ✅ flock-postgres is running"

# ── Step 2: Verify Python venv exists ────────────────────────────────────────
echo ""
echo "[PRE-CHECK] Python virtual environment..."
if [ ! -f "$VENV_PYTHON" ]; then
    echo "  ❌ venv not found at $VENV_PYTHON. Aborting."
    exit 1
fi
echo "  ✅ venv OK → $VENV_PYTHON"

# ── Step 3: Run the pipeline ──────────────────────────────────────────────────
echo ""
echo "[PIPELINE] Starting full data fetch (Nifty 200)..."
cd "$BACKEND_DIR"
"$VENV_PYTHON" -m scripts.run_pipeline

# ── Step 4: Update symlink to latest log ─────────────────────────────────────
ln -sf "$LOG_FILE" "$LATEST_LOG"

# ── Step 5: Rotate logs older than 30 days ───────────────────────────────────
echo ""
echo "[CLEANUP] Removing logs older than 30 days..."
find "$LOG_DIR" -name "pipeline_*.log" -mtime +30 -delete
REMAINING=$(find "$LOG_DIR" -name "pipeline_*.log" | wc -l)
echo "  ✅ Log rotation done. $REMAINING log file(s) retained."

echo ""
echo "============================================================"
echo "  PIPELINE FINISHED — $(date +"%Y-%m-%d %H:%M:%S IST")"
echo "============================================================"
echo ""
