#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/.ai/logs"
LOG_FILE="$LOG_DIR/mc.log"

mkdir -p "$LOG_DIR"

usage() {
  cat <<USAGE
Mission Control

Usage:
  ./bin/mc.sh run
  ./bin/mc.sh status
  ./bin/mc.sh doctor
  ./bin/mc.sh init [--dry-run] [--skip-hooks] [--skip-launchagent]
  ./bin/mc.sh bootstrap [--dry-run] [--skip-hooks] [--skip-launchagent]
  ./bin/mc.sh prompt <mode>
  ./bin/mc.sh selftest
  ./bin/mc.sh logs [mc|dispatch|errors] [--tail] [--lines N]
  ./bin/mc.sh snapshot [--export <file>] [--import <file>] [--compare <file1> <file2>]
  ./bin/mc.sh help

Commands:
  run        Run preflight + dashboard workflow
  status     Show concise environment and setup status
  doctor     Run full diagnostics
  init       Run bootstrap, then self-test
  bootstrap  Run mission-control bootstrap installer
  prompt     Print/copy prompt for a given mode
  selftest   Run mission-control self-test
  snapshot   Show/export/import combined state snapshot
  logs       View mission-control or dispatch logs
  archive    Move mission to archive
  restore    Restore mission from archive
  list       List missions (archived)
  help       Show this help
USAGE
}

run_main() {
  {
    echo "=== MISSION CONTROL ==="
    date
    echo "ROOT=$ROOT"
    echo

    echo "=== PREFLIGHT ==="
    if [ -x "$ROOT/bin/preflight.sh" ]; then
      "$ROOT/bin/preflight.sh"
    else
      echo "preflight.sh not found or not executable"
    fi
    echo

    echo "=== DASHBOARD ==="
    if [ -x "$ROOT/scripts/dashboard.sh" ]; then
      "$ROOT/scripts/dashboard.sh"
    else
      echo "dashboard.sh not found or not executable"
    fi
    echo

    echo "=== GIT ==="
    git -C "$ROOT" status -sb || true
    echo
    HEAD_SHA="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
    echo "HEAD=$HEAD_SHA"
    echo "=== DONE ==="
    echo
    echo "================================================"
    echo "  ANBEFALT PROMPT"
    echo "================================================"
    MISSION_FILE="$(ls "$ROOT/.ai/missions/active/" 2>/dev/null | head -1 || true)"
    if [ -n "${MISSION_FILE:-}" ]; then
      echo "  Aktiv mission: $MISSION_FILE"
      echo "  Anbefalt:  ./bin/prompt.sh build"
      echo "  Kopier:    ./bin/prompt.sh build | pbcopy"
    else
      echo "  Ingen aktiv mission"
      echo "  Start med: ./bin/prompt.sh plan"
    fi
    echo "================================================"
  } | tee -a "$LOG_FILE"
}

run_status() {
  local HOOKS_PATH
  HOOKS_PATH="$(git -C "$ROOT" config core.hooksPath 2>/dev/null || true)"
  local PLIST_PATH="$HOME/Library/LaunchAgents/com.roadmap-ai.morning-standup.plist"

  echo "=== MISSION CONTROL STATUS ==="
  echo "root: $ROOT"
  echo "git: $(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
  echo "hooksPath: ${HOOKS_PATH:-<unset>}"

  if [ -x "$ROOT/bin/doctor.sh" ]; then
    echo "doctor: OK"
  else
    echo "doctor: MISSING"
  fi

  if [ -x "$ROOT/scripts/bootstrap_mission_control.sh" ]; then
    echo "bootstrap: OK"
  else
    echo "bootstrap: MISSING"
  fi

  if [ -x "$ROOT/scripts/selftest_mission_control.sh" ]; then
    echo "selftest: OK"
  else
    echo "selftest: MISSING"
  fi

  if [ -e "$ROOT/.githooks/pre-commit" ]; then
    echo "versioned-hook: OK"
  else
    echo "versioned-hook: MISSING"
  fi

  if [ "$(uname -s)" = "Darwin" ]; then
    if [ -e "$PLIST_PATH" ]; then
      echo "launchagent: INSTALLED"
      if launchctl list | grep -q "com.roadmap-ai.morning-standup"; then
        echo "launchagent-loaded: YES"
      else
        echo "launchagent-loaded: NO"
      fi
    else
      echo "launchagent: NOT INSTALLED"
    fi
  else
    echo "launchagent: SKIPPED (non-macOS)"
  fi

  echo
  git -C "$ROOT" status -sb || true
}


run_snapshot() {
  local mode="${1:-}"
  local filepath="${2:-}"
  local filepath2="${3:-}"

  case "$mode" in
    --export)
      if [ -z "$filepath" ]; then
        echo "Usage: mc snapshot --export <filepath>" >&2
        exit 1
      fi
      {
        echo "=== SNAPSHOT ==="
        echo "timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        echo "root: $ROOT"
        echo "exported_by: $(whoami)@$(hostname)"
        echo
        echo "=== STATUS ==="
        run_status
        echo
        echo "=== ACTIVE MISSION ==="
        ls "$ROOT/.ai/missions/active/" 2>/dev/null | head -5 || echo "no active missions"
        echo
        echo "=== RECENT COMMITS ==="
        git -C "$ROOT" log --oneline -10 || true
        echo
        echo "=== DOCTOR SUMMARY ==="
        "$ROOT/bin/doctor.sh" | sed -n '1,60p'
      } > "$filepath"
      echo "✅ Snapshot exported to: $filepath"
      ;;
    --import)
      if [ -z "$filepath" ]; then
        echo "Usage: mc snapshot --import <filepath>" >&2
        exit 1
      fi
      if [ ! -f "$filepath" ]; then
        echo "Error: file not found: $filepath" >&2
        exit 1
      fi
      echo "=== IMPORTED SNAPSHOT ==="
      cat "$filepath"
      echo
      echo "✅ Snapshot imported from: $filepath"
      ;;
    --compare|--diff)
      if [ -z "$filepath" ] || [ -z "$filepath2" ]; then
        echo "Usage: mc snapshot --compare <file1> <file2>" >&2
        exit 1
      fi
      if [ ! -f "$filepath" ]; then
        echo "Error: file not found: $filepath" >&2
        exit 1
      fi
      if [ ! -f "$filepath2" ]; then
        echo "Error: file not found: $filepath2" >&2
        exit 1
      fi
      echo "=== SNAPSHOT COMPARISON ==="
      echo "Comparing:"
      echo "  A: $filepath"
      echo "  B: $filepath2"
      echo
      if diff -q "$filepath" "$filepath2" >/dev/null 2>&1; then
        echo "✅ Snapshots are identical"
      else
        echo "=== DIFFERENCES ==="
        diff -u "$filepath" "$filepath2" || true
        echo
        echo "✅ Comparison complete"
      fi
      ;;
    *)
      echo "=== SNAPSHOT ==="
      echo "timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
      echo "root: $ROOT"
      echo
      echo "=== STATUS ==="
      run_status
      echo
      echo "=== ACTIVE MISSION ==="
      ls "$ROOT/.ai/missions/active/" 2>/dev/null | head -5 || echo "no active missions"
      echo
      echo "=== RECENT COMMITS ==="
      git -C "$ROOT" log --oneline -5 || true
      echo
      echo "=== DOCTOR SUMMARY (first 40 lines) ==="
      "$ROOT/bin/doctor.sh" | sed -n '1,40p'
      ;;
  esac
}

run_init() {
  "$ROOT/scripts/bootstrap_mission_control.sh" "$@"
  "$ROOT/scripts/selftest_mission_control.sh"
}

cmd="${1:-run}"

case "$cmd" in
  run)
    shift
    run_main "$@"
    ;;
  status)
    shift
    run_status "$@"
    ;;
  snapshot)
    shift
    run_snapshot "$@"
    ;;
  doctor)
    shift
    exec "$ROOT/bin/doctor.sh" "$@"
    ;;
  init)
    shift
    run_init "$@"
    ;;
  bootstrap)
    shift
    exec "$ROOT/scripts/bootstrap_mission_control.sh" "$@"
    ;;
  prompt)
    shift
    exec "$ROOT/bin/prompt.sh" "$@"
    ;;
  archive)
    shift
    exec "$ROOT/bin/archive.sh" archive "$@"
    ;;
  restore)
    shift
    exec "$ROOT/bin/archive.sh" restore "$@"
    ;;
  list)
    shift
    exec "$ROOT/bin/archive.sh" list "$@"
    ;;
  new)
    shift
    exec "$ROOT/bin/new.sh" "$@"
    ;;
  watch)
    shift
    exec "$ROOT/bin/watch.sh" "$@"
    ;;
  logs)
    shift
    exec "$ROOT/bin/logs.sh" "$@"
    ;;
  selftest)
    shift
    exec "$ROOT/scripts/selftest_mission_control.sh" "$@"
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    echo
    usage
    exit 1
    ;;
esac
