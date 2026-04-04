#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ROADMAP-AI QUICKSTART                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [[ ! -f "venv/bin/activate" ]]; then
  echo "❌ Missing Python virtualenv. Run 'python3 -m venv venv' first." >&2
  exit 1
fi

source venv/bin/activate

echo "1. Running health check..."
./scripts/dispatch_runner.sh health | tail -5 || true

echo ""
echo "2. Generating fresh panel data..."
./scripts/dispatch_runner.sh standup >/dev/null 2>&1 || true
python scripts/github_pr_sync.py >/dev/null 2>&1 || true
python scripts/remote_health_monitor.py >/dev/null 2>&1 || true
python scripts/stripe_revenue_sync.py >/dev/null 2>&1 || true
python scripts/orchestration_status.sh >/dev/null 2>&1 || true
echo "✅ All panels updated"
echo ""

echo "3. System status:"
~/roadmap-ai/mission-control/bin/mc.sh status

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              READY TO USE                                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
cat <<'INFO'
Quick commands:
  roadmap smart-next            - Next task recommendation
  mc watch                      - Live monitoring
  ./scripts/open_dashboards.sh  - Interactive dashboards
  ./scripts/demo_walkthrough.sh - Full demo

Dashboards served from http://localhost:8000/dashboard/ (run open_dashboards.sh)
INFO
