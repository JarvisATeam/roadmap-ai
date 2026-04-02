#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${ROADMAP_DB_PATH:-$(pwd)/.roadmap_cli.db}"
export ROADMAP_DB_PATH="$DB_PATH"

echo "======================================"
echo "Phase 1.2 Cleanup Testing"
echo "======================================"

rm -f "$DB_PATH"

python test_db_layer.py

source venv/bin/activate

roadmap init
roadmap add-task "Task 1: High priority" -m "Backend" -p 5 --due 2024-02-15 -t urgent -t backend
roadmap add-task "Task 2: Medium priority" -m "Backend" -p 3 -t backend
roadmap add-task "Task 3: Frontend work" -m "Frontend" -p 4 -t frontend -t ui

roadmap next
roadmap next --all

BLOCK_TARGET=$(sqlite3 "$DB_PATH" "SELECT id FROM steps WHERE status='todo' ORDER BY priority DESC LIMIT 1 OFFSET 1;")
if [[ -n "${BLOCK_TARGET}" ]]; then
  roadmap block "${BLOCK_TARGET:0:8}" "Waiting on reviewer"
  roadmap list-blocks
  BLOCKER_ID=$(sqlite3 "$DB_PATH" "SELECT id FROM blockers ORDER BY created_at DESC LIMIT 1;")
  roadmap unblock "${BLOCKER_ID:0:8}" -n "Reviewer approved"
fi

TASK_ID=$(sqlite3 "$DB_PATH" "SELECT id FROM steps WHERE status='todo' ORDER BY priority DESC LIMIT 1;")
roadmap complete "${TASK_ID:0:8}" -n "Finished during testing"

roadmap status
roadmap status --detailed

if [ -f plan.json ]; then
  roadmap summary
else
  echo "Skipping summary test (no plan.json)"
fi

echo "======================================"
echo "✅ All tests passed!"
echo "======================================"
