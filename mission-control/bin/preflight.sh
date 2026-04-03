#!/usr/bin/env bash
set -euo pipefail

MC_ROOT="$HOME/mission-control"
ROADMAP_ROOT="$HOME/roadmap-ai"
ROADMAP_VENV="$ROADMAP_ROOT/venv"

PASS_COUNT=0
FAIL_COUNT=0

function check() {
  local label="$1"
  shift
  if "$@"; then
    echo "✅ $label"
    PASS_COUNT=$((PASS_COUNT+1))
  else
    echo "❌ $label"
    FAIL_COUNT=$((FAIL_COUNT+1))
  fi
}

check "Mission Control repo" test -d "$MC_ROOT/.git"
check "Build workflow doc" test -f "$MC_ROOT/docs/BUILD_WORKFLOW_v2.md"
check "System prompt doc" test -f "$MC_ROOT/docs/SYSTEM_PROMPT_BUILD.md"
check "Dashboard schema" test -f "$MC_ROOT/docs/dashboard_schema.json"
check "Roadmap repo" test -d "$ROADMAP_ROOT/.git"
check "Roadmap venv" test -f "$ROADMAP_VENV/bin/activate"

check "Roadmap CLI" bash -c "source '$ROADMAP_VENV/bin/activate' && command -v roadmap >/dev/null && roadmap --help >/dev/null"

echo "---"
echo "PASS: $PASS_COUNT"
echo "FAIL: $FAIL_COUNT"

[[ $FAIL_COUNT -eq 0 ]]
