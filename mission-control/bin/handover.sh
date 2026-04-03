#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$ROOT/.." && pwd)"
HANDOFF="$ROOT/HANDOFF.md"
DECISIONS="$ROOT/.ai/memory/decisions.jsonl"

usage() {
  cat <<USAGE
Handover generator.

Usage:
  mc handover                    Print handover report
  mc handover --export <file>    Write report to file
  mc handover --commit           Append to HANDOFF.md, record decision, git push
USAGE
}

ensure_files() {
  mkdir -p "$(dirname "$DECISIONS")"
  touch "$DECISIONS"
  touch "$HANDOFF"
}

generate_report() {
  local ts branch head tag status
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  branch=$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  head=$(git -C "$REPO_ROOT" log --oneline -1 2>/dev/null || echo "unknown")
  tag=$(git -C "$REPO_ROOT" tag --list | tail -1 || echo "none")
  status=$(git -C "$REPO_ROOT" status -sb | head -1)

  cat <<REPORT
## HANDOVER — ${ts}

### Git
- Branch: ${branch}
- HEAD: ${head}
- Tag: ${tag}
- Status: ${status}

### Recent Commits
$(git -C "$REPO_ROOT" log --oneline -10)

### Active Missions
$(ls "$ROOT/.ai/missions/active/" 2>/dev/null | head -10 || echo "(none)")

### Panel Output
$(ls -lh "$REPO_ROOT/panel_output/" 2>/dev/null | tail -10 || echo "(none)")

### Health Highlights
$($ROOT/bin/doctor.sh 2>/dev/null | grep -E "✅|❌|⚠️" | head -15 || echo "(doctor unavailable)")

### Phone Summary
$(cat "$REPO_ROOT/panel_output/phone_summary.txt" 2>/dev/null || echo "(none)")

### Idempotency Log (last 5)
$(tail -5 "$REPO_ROOT/panel_output/dispatch_idempotency.jsonl" 2>/dev/null || echo "(none)")

### Key Files
- scripts/dispatch_runner.sh
- scripts/idempotency.sh
- mission-control/bin/mc.sh
- mission-control/bin/doctor.sh
- roadmap/core/id_resolver.py
- roadmap/core/nta.py
- dispatch_ops.yaml / DISPATCH_RULES.md
REPORT
}

do_commit() {
  ensure_files
  local report
  report=$(generate_report)
  {
    echo
    echo "$report"
  } >> "$HANDOFF"
  python3 - "$DECISIONS" <<'PY'
import json, sys, time
path = sys.argv[1]
entry = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "title": "Handover generated",
    "context": "mc handover --commit"
}
with open(path, "a") as fh:
    fh.write(json.dumps(entry) + "\n")
PY
  git -C "$REPO_ROOT" add "$HANDOFF" "$DECISIONS"
  git -C "$REPO_ROOT" commit -m "docs: handover update"
  git -C "$REPO_ROOT" push
  printf '%s\n' "$report"
}

case "${1:-}" in
  --commit)
    do_commit
    ;;
  --export)
    if [ -z "${2:-}" ]; then
      echo "Missing export path" >&2
      exit 1
    fi
    generate_report > "$2"
    echo "✅ Exported to $2"
    ;;
  -h|--help)
    usage
    ;;
  *)
    generate_report
    ;;
esac
