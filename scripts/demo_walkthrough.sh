#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f "venv/bin/activate" ]]; then
  echo "❌ Missing Python virtualenv (expected venv/)." >&2
  echo "Run 'python3 -m venv venv && source venv/bin/activate && pip install -e .'" >&2
  exit 1
fi

source "venv/bin/activate"

for bin in roadmap mc jq; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "❌ Missing dependency: $bin" >&2
    exit 1
  fi
done

log_section() {
  echo
  echo "============================================================"
  echo " $1"
  echo "============================================================"
  echo
}

run_cmd() {
  local description="$1"
  shift
  echo "▶ $description"
  echo "\$ $*"
  "$@"
  echo
}

timestamp="$(date -u +"%Y%m%d-%H%M%S")"
mission_title="Demo Flow ${timestamp}"

due_in_days() {
  python - "$1" <<'PY'
import datetime
import sys
days = int(sys.argv[1])
print((datetime.date.today() + datetime.timedelta(days=days)).isoformat())
PY
}

log_section "1. Refresh canonical data"
run_cmd "Dispatch standup (regenerates panel_output/*)" ./scripts/dispatch_runner.sh standup

log_section "2. Create a demo mission"
mission_json="$(roadmap add-mission "$mission_title" --description "Interactive walkthrough mission" --revenue 5000 --json)"
mission_code="$(echo "$mission_json" | jq -r '.mission_code')"
echo "Created mission: $mission_code ($mission_title)"
echo

log_section "3. Add demo steps"
due1="$(due_in_days 2)"
due2="$(due_in_days 5)"
due3="$(due_in_days 7)"
run_cmd "Add research step" roadmap add-step "$mission_code" "Research integration points" --due "$due1" --energy 4
run_cmd "Add implementation step" roadmap add-step "$mission_code" "Implement primary flow" --due "$due2" --energy 6
run_cmd "Add QA step" roadmap add-step "$mission_code" "QA + validation" --due "$due3" --energy 5

log_section "4. Inspect mission context"
run_cmd "List steps for $mission_code" roadmap list-steps --mission "$mission_code"
run_cmd "Smart next recommendation" roadmap smart-next --json
run_cmd "Risk snapshot for mission" roadmap risks --mission "$mission_code" --json
run_cmd "Forecast mission timeline" roadmap forecast "$mission_code"

log_section "5. Finish one step and re-check"
first_step_prefix="$(roadmap list-steps --mission "$mission_code" --json | jq -r '.data.steps[0].id[:8]')"
run_cmd "Complete first step" roadmap complete "$first_step_prefix" --notes "Demo walkthrough"
run_cmd "Steps after completion" roadmap list-steps --mission "$mission_code"

log_section "6. Mission Control overview"
run_cmd "Mission Control status" mc status
run_cmd "Generate handover snippet" mc handover

log_section "Demo complete"
cat <<SUMMARY
Mission code : $mission_code
Mission title: $mission_title
Steps demoed : Research, Implement, QA
You can inspect dashboards via:
  python3 -m http.server 8000 &
  open http://localhost:8000/dashboard/index.html

Clean up demo data anytime with:
  roadmap archive $mission_code
SUMMARY
