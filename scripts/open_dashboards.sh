#!/usr/bin/env bash
set -euo pipefail

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           ROADMAP-AI DASHBOARD LAUNCHER                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

PORT=8000
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Starting webserver on port $PORT..."
cd "$ROOT"

if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
  echo "⚠️  Port $PORT already in use. Kill existing server? (y/N)"
  read -r KILL
  if [[ "$KILL" =~ ^[Yy]$ ]]; then
    lsof -ti:$PORT | xargs kill -9
    sleep 1
  else
    echo "Using existing server..."
  fi
fi

if ! lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
  python3 -m http.server $PORT >/dev/null 2>&1 &
  SERVER_PID=$!
  echo "✅ Server started (PID: $SERVER_PID)"
  sleep 1
fi

BASE_URL="http://localhost:$PORT/dashboard"

echo ""
echo "Available dashboards:"
echo ""
echo "  1. Smart Next       - Next task recommendation"
echo "  2. Risk Summary     - Overdue & blocked tasks"
echo "  3. Progress         - Mission completion status"
echo "  4. Decisions        - Recent decisions log"
echo "  5. Forecast         - Mission timeline projection"
echo "  6. Orchestration    - Agent queue status"
echo "  7. PR Lane          - GitHub pull requests"
echo "  8. Remote Health    - Tailscale node monitoring"
echo "  9. Revenue          - Stripe revenue tracking"
echo ""
echo "  0. Open ALL panels"
echo "  q. Quit"
echo ""

while true; do
  read -p "Select dashboard (0-9, q): " choice
  case $choice in
    1) open "$BASE_URL/smart_next.html" ;;
    2) open "$BASE_URL/risk_summary.html" ;;
    3) open "$BASE_URL/progress.html" ;;
    4) open "$BASE_URL/decisions.html" ;;
    5) open "$BASE_URL/forecast.html" ;;
    6) open "$BASE_URL/orchestration.html" ;;
    7) open "$BASE_URL/pr_lane.html" ;;
    8) open "$BASE_URL/remote_health.html" ;;
    9) open "$BASE_URL/revenue.html" ;;
    0)
      echo "Opening all dashboards..."
      for panel in smart_next risk_summary progress decisions forecast orchestration pr_lane remote_health revenue; do
        open "$BASE_URL/${panel}.html"
        sleep 0.4
      done
      ;;
    q|Q)
      echo "Stopping server..."
      if [ -n "${SERVER_PID:-}" ]; then
        kill $SERVER_PID 2>/dev/null || true
      fi
      exit 0
      ;;
    *)
      echo "Invalid choice. Try again."
      ;;
  esac
done
