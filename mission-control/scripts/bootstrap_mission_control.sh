#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROADMAP_AI_DIR="${ROADMAP_AI_DIR:-$HOME/roadmap-ai}"
DRY_RUN=0
SKIP_HOOKS=0
SKIP_LAUNCHAGENT=0
OS_NAME="$(uname -s)"

say() {
  echo "[bootstrap] $*"
}

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

require_file() {
  local path="$1"
  if [ ! -e "$path" ]; then
    say "missing required file: $path"
    exit 1
  fi
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    say "missing required command: $cmd"
    exit 1
  fi
}

usage() {
  cat <<USAGE
Usage: ./scripts/bootstrap_mission_control.sh [options]

Options:
  --dry-run           Show actions without making changes
  --skip-hooks        Do not configure git hooks
  --skip-launchagent  Do not run LaunchAgent installer
  -h, --help          Show this help
USAGE
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --dry-run) DRY_RUN=1 ;;
      --skip-hooks) SKIP_HOOKS=1 ;;
      --skip-launchagent) SKIP_LAUNCHAGENT=1 ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        say "unknown option: $1"
        usage
        exit 1
        ;;
    esac
    shift
  done
}

check_base_dependencies() {
  require_cmd git
  require_cmd python3
}

check_hook_dependencies() {
  require_cmd git
}

check_launchagent_dependencies() {
  if [ "$OS_NAME" != "Darwin" ]; then
    say "LaunchAgent installation is only supported on macOS (detected: $OS_NAME)"
    exit 1
  fi
  require_cmd launchctl
  require_cmd plutil
}

configure_hooks() {
  require_file "$ROOT/.githooks/pre-commit"
  if [ ! -d "$ROOT/.git" ]; then
    say "missing .git directory: $ROOT/.git"
    exit 1
  fi
  check_hook_dependencies
  say "configuring versioned git hooks"
  run git -C "$ROOT" config core.hooksPath .githooks
  if [ "$DRY_RUN" -eq 0 ]; then
    say "hooksPath=$(git -C "$ROOT" config core.hooksPath)"
  fi
}

run_launchagent() {
  require_file "$ROOT/scripts/install_launchagent.sh"
  if [ ! -x "$ROOT/scripts/install_launchagent.sh" ]; then
    say "LaunchAgent installer not executable: $ROOT/scripts/install_launchagent.sh"
    exit 1
  fi
  check_launchagent_dependencies
  say "running LaunchAgent installer"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] $ROOT/scripts/install_launchagent.sh"
  else
    "$ROOT/scripts/install_launchagent.sh"
  fi
}

main() {
  parse_args "$@"

  say "root: $ROOT"
  say "roadmap-ai: $ROADMAP_AI_DIR"
  say "os: $OS_NAME"
  say "dry-run=$DRY_RUN skip-hooks=$SKIP_HOOKS skip-launchagent=$SKIP_LAUNCHAGENT"

  check_base_dependencies

  run mkdir -p \
    "$ROOT/.ai/memory" \
    "$ROOT/.ai/missions/active" \
    "$ROOT/bin" \
    "$ROOT/scripts" \
    "$ROOT/docs" \
    "$ROOT/claude-prompts"

  require_file "$ROOT/bin/mc.sh"
  require_file "$ROOT/bin/prompt.sh"
  require_file "$ROOT/docs/SYSTEM_PROMPT_BUILD.md"

  if [ "$SKIP_HOOKS" -eq 0 ]; then
    configure_hooks
  else
    say "skipping git hook configuration"
  fi

  if [ "$SKIP_LAUNCHAGENT" -eq 0 ]; then
    run_launchagent
  else
    say "skipping LaunchAgent installation"
  fi

  say "verifying key files"
  run ls -l \
    "$ROOT/bin/mc.sh" \
    "$ROOT/bin/prompt.sh" \
    "$ROOT/.githooks/pre-commit" \
    "$ROOT/scripts/install_launchagent.sh" \
    "$ROOT/docs/SYSTEM_PROMPT_BUILD.md"

  say "done"
}

main "$@"
