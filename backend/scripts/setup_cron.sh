#!/usr/bin/env bash
# =============================================================================
#  Flock — Install Daily Cron Job
#
#  Schedules daily_pipeline.sh to run at 4:00 PM IST (Mon–Fri).
#  NSE/BSE closes at 3:30 PM IST — we wait 30 min for data to settle.
#
#  IST = UTC+5:30  →  4:00 PM IST = 10:30 AM UTC
#  Cron format: 30 10 * * 1-5  (Mon=1, Fri=5)
#
#  Usage: bash setup_cron.sh
#         bash setup_cron.sh --remove   (to uninstall)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_SCRIPT="$SCRIPT_DIR/daily_pipeline.sh"
LOG_DIR="$(dirname "$SCRIPT_DIR")/logs"
CRON_LOG="$LOG_DIR/cron_runner.log"
CRON_TAG="# flock-daily-pipeline"

# ── Ensure script is executable ───────────────────────────────────────────────
chmod +x "$PIPELINE_SCRIPT"
mkdir -p "$LOG_DIR"

# ── Handle --remove flag ──────────────────────────────────────────────────────
if [[ "${1:-}" == "--remove" ]]; then
    echo "Removing Flock daily cron job..."
    crontab -l 2>/dev/null | grep -v "$CRON_TAG" | crontab -
    echo "✅ Cron job removed."
    exit 0
fi

# ── Cron expression ──────────────────────────────────────────────────────────
# 4:00 PM IST = 10:30 UTC | Mon-Fri only
CRON_EXPR="30 10 * * 1-5"
CRON_LINE="$CRON_EXPR TZ=Asia/Kolkata bash $PIPELINE_SCRIPT >> $CRON_LOG 2>&1 $CRON_TAG"

# ── Install (idempotent — won't duplicate) ────────────────────────────────────
echo "Installing Flock daily pipeline cron job..."

# Remove any existing flock cron entry first
EXISTING=$(crontab -l 2>/dev/null | grep -v "$CRON_TAG" || true)
echo "$EXISTING" | { cat; echo "$CRON_LINE"; } | crontab -

echo ""
echo "✅ Cron job installed!"
echo ""
echo "  Schedule : Every weekday (Mon–Fri) at 4:00 PM IST"
echo "  Script   : $PIPELINE_SCRIPT"
echo "  Log      : $CRON_LOG"
echo "  Raw cron : $CRON_EXPR  [TZ=Asia/Kolkata]"
echo ""
echo "  Current crontab:"
echo "  ─────────────────────────────────────────────────"
crontab -l
echo "  ─────────────────────────────────────────────────"
echo ""
echo "  To verify cron is working, run a test:"
echo "    bash $PIPELINE_SCRIPT"
echo ""
echo "  To remove this cron job later:"
echo "    bash $SCRIPT_DIR/setup_cron.sh --remove"
