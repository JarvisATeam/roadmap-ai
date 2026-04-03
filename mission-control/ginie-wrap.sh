#!/usr/bin/env bash
set -euo pipefail

HANDOVER_FILE="${HOME}/.ginie/handover.md"
REPO="${HOME}/GinieSystem"

if [ "$#" -lt 1 ]; then
  echo "bruk: gw \"enkel kommando uten && eller ;\"" >&2
  exit 1
fi

CMD="$1"

if [[ "$CMD" == *"&&"* || "$CMD" == *";"* ]]; then
  echo "gw støtter ikke flere kommandoer samtidig (ingen && eller ;)" >&2
  exit 1
fi

timestamp() {
  date +"%Y-%m-%d %H:%M:%S %Z"
}

OUTPUT="$(
  cd "$REPO"
  $CMD
)"

TAIL_OUTPUT="$(printf '%s\n' "$OUTPUT" | tail -n 5)"

{
  echo ""
  echo "## Handover – $(timestamp)"
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
