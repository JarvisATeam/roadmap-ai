#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROMPTS_DIR="$ROOT/claude-prompts"

copy_and_clipboard() {
  local mode_label="$1"
  local file_path="$2"
  local block
  block=$(printf "# MODUS: %s\n# Lim inn dette som system-prompt i Claude\n---\n%s\n" "$mode_label" "$(cat "$file_path")")
  printf "%s\n" "$block"
  if command -v pbcopy >/dev/null 2>&1; then
    printf "%s" "$block" | pbcopy
    echo "[copied to clipboard]"
  else
    echo "[pbcopy not available — install pbtool]" >&2
  fi
}

show_list(){
  cat <<LIST
Tilgjengelige moduser:
  auto     (alias: build)     — Autonom bygging
  plan     (alias: architect) — Planlegging/arkitektur
  dream    (alias: memory)    — Minnekonsolidering
  security (alias: guard)     — Sikkerhetsmonitor del 1
  security2                   — Sikkerhetsmonitor del 2
  list                        — Denne oversikten

Bruk: ./bin/prompt.sh <modus>
LIST
}

MODE="${1:-list}"

# Resolve aliases
case "$MODE" in
  build)     MODE="auto" ;;
  architect) MODE="plan" ;;
  memory)    MODE="dream" ;;
  guard)     MODE="security" ;;
esac

case "$MODE" in
  list)
    show_list
    ;;
  auto)
    copy_and_clipboard "auto (bygging)" "$PROMPTS_DIR/system-prompt-auto-mode.md"
    ;;
  plan)
    copy_and_clipboard "plan (arkitektur)" "$PROMPTS_DIR/agent-prompt-plan-mode-enhanced.md"
    ;;
  dream)
    copy_and_clipboard "dream (minnekonsolidering)" "$PROMPTS_DIR/agent-prompt-dream-memory-consolidation.md"
    ;;
  security)
    copy_and_clipboard "security (sikkerhetsmonitor del 1)" "$PROMPTS_DIR/agent-prompt-security-monitor-for-autonomous-agent-actions-first-part.md"
    ;;
  security2)
    copy_and_clipboard "security2 (sikkerhetsmonitor del 2)" "$PROMPTS_DIR/agent-prompt-security-monitor-for-autonomous-agent-actions-second-part.md"
    ;;
  *)
    echo "Ukjent modus: $MODE"
    show_list
    exit 1
    ;;
esac
