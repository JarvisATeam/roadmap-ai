#!/bin/bash
# Dashboard panel refresher for roadmap-ai (copy to ~/roadmapai/bin if desired)
set -e

ROADMAP_AI_DIR="${ROADMAP_AI_DIR:-$HOME/roadmap-ai}"
VENV_PATH="${ROADMAP_AI_DIR}/venv"
OUTPUT_DIR="${ROADMAP_PANEL_DIR:-$HOME/roadmapai/data/roadmap}"
mkdir -p "$OUTPUT_DIR"
source "$VENV_PATH/bin/activate"

refresh() {
  local cmd=$1
  shift
  roadmap "$cmd" "$@"
}

case "$1" in
  smart)
    roadmap smart next --json > "$OUTPUT_DIR/smart_next.json"
    ;;
  risks)
    roadmap risks --json > "$OUTPUT_DIR/risks.json"
    ;;
  forecast)
    mission=$2
    if [ -z "$mission" ]; then
      echo "Usage: roadmap_panels.sh forecast <mission-code>"
      exit 1
    fi
    roadmap forecast "$mission" --json > "$OUTPUT_DIR/forecast_${mission}.json"
    ;;
  decisions)
    roadmap list-decisions --limit 10 --json > "$OUTPUT_DIR/decisions.json"
    ;;
  status)
    roadmap status --json > "$OUTPUT_DIR/status.json"
    ;;
  report)
    roadmap report --daily --json > "$OUTPUT_DIR/daily_report.json"
    ;;
  all)
    "$0" smart || true
    "$0" risks || true
    "$0" status || true
    "$0" decisions || true
    "$0" report || true
    ;;
  *)
    echo "Usage: roadmap_panels.sh {smart|risks|forecast|decisions|status|report|all}" >&2
    exit 1
    ;;
esac
