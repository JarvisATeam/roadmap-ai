#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MC_LOG="$ROOT/.ai/logs/mc.log"
DISPATCH_LOG="$HOME/dispatch.log"
DISPATCH_ERROR_LOG="$HOME/dispatch_error.log"

MODE="mc"
LINES=50
TAIL_MODE=0

print_usage() {
  cat <<USAGE
Usage:
  mc logs [mc|dispatch|errors] [--tail] [--lines N]
Examples:
  mc logs
  mc logs dispatch --lines 20
  mc logs errors --tail
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    mc|dispatch|errors)
      MODE="$1"
      shift
      ;;
    --dispatch)
      MODE="dispatch"
      shift
      ;;
    --errors)
      MODE="errors"
      shift
      ;;
    --tail|-f)
      TAIL_MODE=1
      shift
      ;;
    --lines|-n)
      LINES="$2"
      shift 2
      ;;
    --help|-h)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      print_usage >&2
      exit 1
      ;;
  esac
done


show_file() {
  local file="$1"
  local label="$2"
  if [ ! -f "$file" ]; then
    echo "$label not found: $file"
    return 1
  fi
  if [ "$TAIL_MODE" -eq 1 ]; then
    tail -f "$file"
  else
    tail -n "$LINES" "$file"
  fi
}

case "$MODE" in
  mc)
    show_file "$MC_LOG" "mc.log" || true
    ;;
  dispatch)
    show_file "$DISPATCH_LOG" "dispatch.log" || true
    ;;
  errors)
    show_file "$DISPATCH_ERROR_LOG" "dispatch_error.log" || true
    ;;
  *)
    print_usage >&2
    exit 1
    ;;
esac
