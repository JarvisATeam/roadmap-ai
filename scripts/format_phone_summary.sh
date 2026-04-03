#!/usr/bin/env bash
set -euo pipefail
PANEL_DIR="${1:-panel_output}"
python3 - "$PANEL_DIR" <<'PY'
import json, sys
from pathlib import Path
from datetime import datetime, timezone
panel_dir = Path(sys.argv[1])

def safe_load(name):
    path = panel_dir / name
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return None
    return None

smart = safe_load('smart_next.json')
risks = safe_load('risks.json')
health = safe_load('health_status.json')
decisions = safe_load('decisions.json')

lines = []
lines.append('📋 STANDUP {}'.format(datetime.now(timezone.utc).strftime('%H:%MZ')))
lines.append('')
if health:
    data = health.get('data', {})
    checks = data.get('checks_passed', '?')
    total = data.get('checks_total', '?')
    emoji = '✅' if checks == total else '⚠️'
    lines.append(f"{emoji} Health: {checks}/{total}")
else:
    lines.append('❓ Health: unknown')
if smart:
    rec = smart.get('data', {}).get('recommendation', {}) or {}
    task = (rec.get('task_name') or 'No task')[:40]
    score = rec.get('score', 0)
    urgency = rec.get('factors', {}).get('urgency', 0)
    lines.append(f"🎯 Next: {task}")
    lines.append(f"   Score {score:.1f} | Urgency {urgency:.1f}x")
else:
    lines.append('🎯 Next: none')
if risks:
    data = risks.get('data', {})
    overdue = data.get('overdue_tasks', 0)
    blocked = data.get('blocked_tasks', 0)
    if overdue or blocked:
        lines.append(f"🔴 Risk: {overdue} overdue / {blocked} blocked")
    else:
        lines.append('🟢 Risk: clear')
else:
    lines.append('❓ Risk: unknown')
if decisions:
    count = decisions.get('data', {}).get('count', 0)
    lines.append(f"📝 Decisions logged: {count}")
summary = '\n'.join(lines)
(panel_dir / 'phone_summary.txt').write_text(summary + '\n')
print(summary)
PY
