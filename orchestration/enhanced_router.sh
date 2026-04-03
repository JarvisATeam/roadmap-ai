#!/usr/bin/env bash
set -euo pipefail

# Enhanced Agent Router with Queue Integration
# Usage: ./enhanced_router.sh <task_id>

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUEUE="$ROOT/orchestration/queue"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <task_id>" >&2
  exit 1
fi

TASK_ID="$1"
TASK_FILE="$QUEUE/$TASK_ID.json"

if [ ! -f "$TASK_FILE" ]; then
  echo "Error: Task not found: $TASK_ID" >&2
  exit 1
fi

# Extract fields
AGENT_ROLE=$(python3 -c "import json; print(json.load(open('$TASK_FILE'))['agent_role'])")
VERB=$(python3 -c "import json; print(json.load(open('$TASK_FILE'))['verb'])")
STATUS=$(python3 -c "import json; print(json.load(open('$TASK_FILE'))['status'])")

echo "=== Routing Task ==="
echo "Task ID: $TASK_ID"
echo "Agent: $AGENT_ROLE"
echo "Verb: $VERB"
echo "Status: $STATUS"
echo ""

# Route based on agent + rules
case "$AGENT_ROLE" in
  GINIE)
    if [ "$VERB" = "propose" ]; then
      echo "→ GINIE: Generate proposal"
      echo "  Next: Queue for AVA validation"
    else
      echo "✗ Unknown GINIE verb: $VERB" >&2
      exit 1
    fi
    ;;
  
  AVA)
    if [ "$VERB" = "validate" ] || [ "$VERB" = "approve" ]; then
      echo "→ AVA: Validate/approve proposal"
      echo "  Outcomes: approved → CODEX | rejected → HUMAN | revise → GINIE"
    else
      echo "✗ Unknown AVA verb: $VERB" >&2
      exit 1
    fi
    ;;
  
  CODEX)
    if [ "$VERB" = "execute" ]; then
      if [ "$STATUS" != "approved" ]; then
        echo "✗ BLOCKED: CODEX requires approved status, got: $STATUS" >&2
        python3 "$ROOT/orchestration/queue_manager.py" <<PY
from queue_manager import QueueManager
qm = QueueManager()
qm.update_status("$TASK_ID", "blocked", blocked_reason="Missing approval - status=$STATUS")
PY
        exit 2
      fi
      echo "→ CODEX: Execute approved task"
      echo "  Must produce: changed_files, tests_passed, commit_hash, git_status"
    else
      echo "✗ Unknown CODEX verb: $VERB" >&2
      exit 1
    fi
    ;;
  
  DISPATCH)
    echo "→ DISPATCH: Orchestrate workflow"
    ;;
  
  HUMAN_ONLY)
    echo "→ HUMAN_ONLY: Blocked for manual review"
    python3 "$ROOT/orchestration/queue_manager.py" <<PY
from queue_manager import QueueManager
qm = QueueManager()
qm.update_status("$TASK_ID", "blocked", blocked_reason="Requires human intervention")
PY
    exit 2
    ;;
  
  *)
    echo "✗ Unknown agent role: $AGENT_ROLE" >&2
    python3 "$ROOT/orchestration/queue_manager.py" <<PY
from queue_manager import QueueManager
qm = QueueManager()
qm.update_status("$TASK_ID", "blocked", blocked_reason="Unknown agent role: $AGENT_ROLE")
PY
    exit 1
    ;;
esac

echo ""
echo "✓ Routing complete"
