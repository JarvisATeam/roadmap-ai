#!/usr/bin/env bash
set -euo pipefail

# Agent Router — Routes tasks to correct agent role
# Usage: ./agent_router.sh <task_file>

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCHEMAS="$ROOT/orchestration/schemas"
QUEUE="$ROOT/orchestration/queue"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <task_file>" >&2
  exit 1
fi

TASK_FILE="$1"

if [ ! -f "$TASK_FILE" ]; then
  echo "Error: Task file not found: $TASK_FILE" >&2
  exit 1
fi

# Validate against schema
if ! python3 -c "
import json, jsonschema, sys
schema = json.load(open('$SCHEMAS/agent_task.json'))
task = json.load(open('$TASK_FILE'))
try:
    jsonschema.validate(task, schema)
    print('✓ Task valid')
except jsonschema.ValidationError as e:
    print(f'✗ Validation error: {e.message}', file=sys.stderr)
    sys.exit(1)
" 2>&1; then
  echo "Error: Task validation failed" >&2
  exit 1
fi

# Extract agent role
AGENT_ROLE=$(python3 -c "import json; print(json.load(open('$TASK_FILE'))['agent_role'])")
TASK_ID=$(python3 -c "import json; print(json.load(open('$TASK_FILE'))['task_id'])")

echo "Routing task $TASK_ID to agent: $AGENT_ROLE"

# Route based on role
case "$AGENT_ROLE" in
  GINIE)
    echo "→ GINIE: propose/ideate"
    ;;
  AVA)
    echo "→ AVA: validate/approve"
    ;;
  CODEX)
    echo "→ CODEX: execute/code"
    ;;
  DISPATCH)
    echo "→ DISPATCH: orchestrate"
    ;;
  HUMAN_ONLY)
    echo "→ HUMAN_ONLY: blocked for human review"
    exit 2
    ;;
  *)
    echo "Error: Unknown agent role: $AGENT_ROLE" >&2
    exit 1
    ;;
esac

echo "✓ Task routed successfully"
