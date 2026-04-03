#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INTERVAL="${1:-5}"

while [ $# -gt 0 ]; do
  case "$1" in
    --interval|-i)
      INTERVAL="$2"
      shift 2
      ;;
    [0-9]*)
      INTERVAL="$1"
      shift
      ;;
    --help|-h)
      echo "Usage: mc watch [--interval N]" >&2
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

echo "Starting watch mode (interval: ${INTERVAL}s)"
echo "Press Ctrl+C to exit"

while true; do
  clear
  echo "=== MISSION CONTROL WATCH $(date +%H:%M:%S) ==="
  echo
  echo "--- STATUS ---"
  "$ROOT/bin/mc.sh" status 2>/dev/null | head -15
  echo
  echo "--- LOGS (mc.log) ---"
  tail -8 "$ROOT/.ai/logs/mc.log" 2>/dev/null || echo "(no logs yet)"
  echo
  echo "--- ACTIVE MISSIONS ---"
  ls "$ROOT/.ai/missions/active/" 2>/dev/null | head -5 || echo "(none)"
  echo
  echo "--- GIT ---"
  git -C "$ROOT" log --oneline -3 2>/dev/null || true
  git -C "$ROOT" status -sb 2>/dev/null | head -5 || true
  echo
  echo "Refreshing in ${INTERVAL}s (Ctrl+C to exit)"
  sleep "$INTERVAL"
done
