#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROADMAP_AI_DIR="${ROADMAP_AI_DIR:-$HOME/roadmap-ai}"
HOOKS_PATH="$(git -C "$ROOT" config core.hooksPath 2>/dev/null || true)"
PLIST_PATH="$HOME/Library/LaunchAgents/com.roadmap-ai.morning-standup.plist"

pass() { echo "✅ $*"; }
warn() { echo "⚠️  $*"; }
fail() { echo "❌ $*"; }

check_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    pass "command available: $cmd"
  else
    fail "missing command: $cmd"
  fi
}

check_file() {
  local path="$1"
  if [ -e "$path" ]; then
    pass "exists: $path"
  else
    fail "missing: $path"
  fi
}

check_exec() {
  local path="$1"
  if [ -x "$path" ]; then
    pass "executable: $path"
  else
    fail "not executable: $path"
  fi
}

echo "=== MISSION CONTROL DOCTOR ==="
echo "root: $ROOT"
echo "roadmap-ai: $ROADMAP_AI_DIR"
echo "os: $(uname -s)"
echo

echo "=== COMMANDS ==="
check_cmd git
check_cmd python3
check_cmd pbcopy || true
echo

echo "=== CORE FILES ==="
check_exec "$ROOT/bin/mc.sh"
check_exec "$ROOT/bin/prompt.sh"
check_exec "$ROOT/bin/doctor.sh"
check_file "$ROOT/docs/SYSTEM_PROMPT_BUILD.md"
check_file "$ROOT/docs/SETUP.md"
check_file "$ROOT/.githooks/pre-commit"
check_exec "$ROOT/scripts/bootstrap_mission_control.sh"
check_exec "$ROOT/scripts/install_launchagent.sh"
echo

echo "=== GIT HOOKS ==="
if [ "$HOOKS_PATH" = ".githooks" ]; then
  pass "core.hooksPath is set to .githooks"
elif [ -n "$HOOKS_PATH" ]; then
  warn "core.hooksPath is set to: $HOOKS_PATH"
else
  warn "core.hooksPath is not set"
fi
echo

echo "=== ROADMAP-AI ==="
if [ -d "$ROADMAP_AI_DIR" ]; then
  pass "roadmap-ai dir exists"
  if [ -x "$ROADMAP_AI_DIR/scripts/test_exports.sh" ]; then
    pass "roadmap-ai export test script is executable"
  else
    warn "roadmap-ai/scripts/test_exports.sh missing or not executable"
  fi
else
  warn "roadmap-ai dir missing: $ROADMAP_AI_DIR"
fi
echo

echo "=== LAUNCHAGENT ==="
if [ "$(uname -s)" = "Darwin" ]; then
  if [ -e "$PLIST_PATH" ]; then
    pass "LaunchAgent plist exists"
    if plutil -lint "$PLIST_PATH" >/dev/null 2>&1; then
      pass "LaunchAgent plist is valid"
    else
      fail "LaunchAgent plist is invalid"
    fi
    if launchctl list | grep -q "com.roadmap-ai.morning-standup"; then
      pass "LaunchAgent is loaded"
    else
      warn "LaunchAgent not loaded"
    fi
  else
    warn "LaunchAgent plist missing"
  fi
else
  warn "LaunchAgent checks skipped: non-macOS"
fi
echo

echo "=== GIT STATUS ==="
git -C "$ROOT" status -sb || true
