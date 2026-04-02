#!/bin/bash
# Setup cron job for local panel exports
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REFRESH_INTERVAL="${REFRESH_INTERVAL:-15}"
LOG_DIR="$ROOT_DIR/logs"

printf "\n⏰ Setting up local cron export (every %s min)\n\n" "$REFRESH_INTERVAL"

mkdir -p "$LOG_DIR"

CRON_JOB="*/${REFRESH_INTERVAL} * * * * cd ${ROOT_DIR} && ./scripts/export_panels_local.sh >> ${LOG_DIR}/panel_export.log 2>&1"

if crontab -l 2>/dev/null | grep -q "export_panels_local.sh"; then
    printf "⚠️  Existing export_panels cron job detected. Replace? (y/N): "
    read -r reply
    if [[ ! $reply =~ ^[Yy]$ ]]; then
        printf "Aborted.\n"
        exit 0
    fi
    crontab -l | grep -v "export_panels_local.sh" | crontab -
fi

(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

printf "✅ Cron job installed.\n"
printf "🔍 Monitor: tail -f %s/panel_export.log\n" "$LOG_DIR"
printf "🛑 Remove: crontab -e  (delete export_panels_local line)\n\n"
