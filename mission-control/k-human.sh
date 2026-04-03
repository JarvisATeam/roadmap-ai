#!/usr/bin/env bash
set -euo pipefail

HANDOVER_FILE="${HOME}/.ginie/handover.md"
REPO="${HOME}/GinieSystem"

if [ "$#" -lt 2 ]; then
  echo "bruk: k-human <task_id> <approve|reject> [kommentar...]" >&2
  exit 1
fi

TASK_ID="$1"
DECISION="$2"
shift 2
COMMENT="${*:-}"

if [ "$DECISION" != "approve" ] && [ "$DECISION" != "reject" ]; then
  echo "DECISION må være approve eller reject" >&2
  exit 1
fi

timestamp() {
  date +"%Y-%m-%d %H:%M:%S %Z"
}

CMD="./tools/kadens/k godkjenn ${TASK_ID} HUMAN_ONLY"

OUTPUT="$(
  cd "$REPO"
  eval "$CMD"
)"

TAIL_OUTPUT="$(printf '%s\n' "$OUTPUT" | tail -n 5)"

{
  echo ""
  echo "## HUMAN_ONLY review – $(timestamp)"
  echo ""
  echo "Task: ${TASK_ID}"
  echo "Decision: ${DECISION}"
  if [ -n "$COMMENT" ]; then
    echo "Comment: ${COMMENT}"
  fi
  echo ""
  echo "Kommando:"
  echo ""
  echo "    $CMD"
  echo ""
  echo "Output (siste 5 linjer):"
  echo '```'
  echo "$TAIL_OUTPUT"
  echo '```'
} >> "$HANDOVER_FILE"

printf '%s\n' "$OUTPUT" | pbcopy
printf '%s\n' "$TAIL_OUTPUT"
