#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PLAN_FILE="${1:-plan-v2.json}"
if [ ! -f "$PLAN_FILE" ]; then
  echo "❌ Plan file not found: $PLAN_FILE" >&2
  exit 1
fi
source venv/bin/activate
PLAN_FILE="$PLAN_FILE" python3 - <<'PY'
import json
import os
from pathlib import Path
from roadmap.core.export import ExportEngine

plan_file = os.environ["PLAN_FILE"]
plan = json.loads(Path(plan_file).read_text())
engine = ExportEngine()
result = engine.to_json(plan)
outfile = Path("exports/plan.json")
outfile.write_text(result)
print(f"✅ JSON exported → {outfile} ({len(result)} chars)")
PY
