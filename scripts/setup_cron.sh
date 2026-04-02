#!/bin/bash
# Setup cron job for roadmap panels in ~/roadmapai
set -e

ROADMAPAI_DIR="${ROADMAPAI_DIR:-$HOME/roadmapai}"
REFRESH_INTERVAL="${REFRESH_INTERVAL:-15}"

printf "\n⏰ Setting up cron refresh for %s (every %s min)\n\n" "$ROADMAPAI_DIR" "$REFRESH_INTERVAL"

if [ ! -x "$ROADMAPAI_DIR/bin/roadmap_panels.sh" ]; then
    printf "❌ Wrapper script not found at %s/bin/roadmap_panels.sh\n" "$ROADMAPAI_DIR"
    printf "   Run scripts/deploy_to_roadmapai.sh first.\n"
    exit 1
fi

mkdir -p "$ROADMAPAI_DIR/logs"

CRON_JOB="*/${REFRESH_INTERVAL} * * * * cd ${ROADMAPAI_DIR} && bin/roadmap_panels.sh all >> logs/panel_refresh.log 2>&1"

if crontab -l 2>/dev/null | grep -q "roadmap_panels.sh"; then
    printf "⚠️  Existing roadmap_panels cron job detected:\n"
    crontab -l | grep "roadmap_panels.sh"
    printf "\nReplace existing job? (y/N): "
    read -r reply
    if [[ ! $reply =~ ^[Yy]$ ]]; then
        printf "Aborted.\n"
        exit 0
    fi
    crontab -l | grep -v "roadmap_panels.sh" | crontab -
fi

(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

printf "✅ Cron job installed.\n"
printf "🔍 Monitor: tail -f %s/logs/panel_refresh.log\n" "$ROADMAPAI_DIR"
printf "🛑 Remove: crontab -e  (delete roadmap_panels line)\n\n"
