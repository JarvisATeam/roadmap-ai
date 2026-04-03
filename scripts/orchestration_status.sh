#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUEUE_DIR="$ROOT/orchestration/queue"
OUTPUT="$ROOT/panel_output/orchestration.json"

echo "[INFO] Generating orchestration status..."

# Count tasks by status
PENDING=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"status": "pending"' {} \; 2>/dev/null | wc -l | tr -d ' ')
PROPOSED=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"status": "proposed"' {} \; 2>/dev/null | wc -l | tr -d ' ')
APPROVED=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"status": "approved"' {} \; 2>/dev/null | wc -l | tr -d ' ')
RUNNING=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"status": "running"' {} \; 2>/dev/null | wc -l | tr -d ' ')
BLOCKED=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"status": "blocked"' {} \; 2>/dev/null | wc -l | tr -d ' ')
FAILED=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"status": "failed"' {} \; 2>/dev/null | wc -l | tr -d ' ')
DONE=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"status": "done"' {} \; 2>/dev/null | wc -l | tr -d ' ')

TOTAL=$((PENDING + PROPOSED + APPROVED + RUNNING + BLOCKED + FAILED + DONE))

# Count by agent
GINIE=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"agent_role": "GINIE"' {} \; 2>/dev/null | wc -l | tr -d ' ')
AVA=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"agent_role": "AVA"' {} \; 2>/dev/null | wc -l | tr -d ' ')
CODEX=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"agent_role": "CODEX"' {} \; 2>/dev/null | wc -l | tr -d ' ')
DISPATCH=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"agent_role": "DISPATCH"' {} \; 2>/dev/null | wc -l | tr -d ' ')
HUMAN=$(find "$QUEUE_DIR" -name "task-*.json" -exec grep -l '"agent_role": "HUMAN_ONLY"' {} \; 2>/dev/null | wc -l | tr -d ' ')

# Find last success/failure times
LAST_SUCCESS="never"
LAST_FAILURE="never"
FAILURE_REASON=""

for f in "$QUEUE_DIR"/task-*.json; do
  [ -f "$f" ] || continue
  STATUS=$(python3 -c "import json,sys; print(json.load(open('$f')).get('status',''))" 2>/dev/null || echo "")
  if [ "$STATUS" = "done" ]; then
    LAST_SUCCESS=$(python3 -c "import json; print(json.load(open('$f')).get('completed_at','unknown'))" 2>/dev/null || echo "unknown")
  elif [ "$STATUS" = "failed" ]; then
    LAST_FAILURE=$(python3 -c "import json; print(json.load(open('$f')).get('updated_at','unknown'))" 2>/dev/null || echo "unknown")
    FAILURE_REASON=$(python3 -c "import json; print(json.load(open('$f')).get('error','unknown'))" 2>/dev/null || echo "unknown")
  fi
done

# Generate JSON
cat > "$OUTPUT" <<JSON
{
  "roadmap_version": "0.3.0",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "command": "orchestration-status",
  "data": {
    "queue_depth": {
      "total": $TOTAL,
      "pending": $PENDING,
      "proposed": $PROPOSED,
      "approved": $APPROVED,
      "running": $RUNNING,
      "blocked": $BLOCKED,
      "failed": $FAILED,
      "done": $DONE
    },
    "by_agent": {
      "GINIE": $GINIE,
      "AVA": $AVA,
      "CODEX": $CODEX,
      "DISPATCH": $DISPATCH,
      "HUMAN_ONLY": $HUMAN
    },
    "health": {
      "last_success": "$LAST_SUCCESS",
      "last_failure": "$LAST_FAILURE",
      "failure_reason": "$FAILURE_REASON",
      "blocked_count": $BLOCKED
    }
  },
  "metadata": {
    "queue_location": "orchestration/queue",
    "schema_version": "1.0"
  }
}
JSON

echo "[OK] Orchestration status → $OUTPUT"
cat "$OUTPUT"
