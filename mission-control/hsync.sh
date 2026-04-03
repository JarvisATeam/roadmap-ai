#!/usr/bin/env bash
set -euo pipefail

NOTE="${1:-}"

HANDOVER_FILE="${HOME}/.ginie/handover.md"
REPO="${HOME}/GinieSystem"

timestamp() {
  date +"%Y-%m-%d %H:%M:%S %Z"
}

{
  echo ""
  echo "## Handover – $(timestamp)"
  if [ -n "$NOTE" ]; then
    echo ""
    echo "Note: $NOTE"
  fi
  echo ""
  echo "### Modus A"
  echo '```'
  (cd "$REPO" && python3 tools/aimigo/modus_a.py)
  echo '```'
  echo ""
  echo "### git status --short"
  echo '```'
  (cd "$REPO" && git status --short)
  echo '```'
} >> "$HANDOVER_FILE"
