# 🚀 ROADMAP-AI QUICKSTART

## First Time Setup

```bash
cd ~/roadmap-ai
source venv/bin/activate
./scripts/quickstart.sh
```

## Daily Use

### Morning Routine

```bash
./scripts/dispatch_runner.sh standup
```

### Interactive Demo

```bash
./scripts/demo_walkthrough.sh
```

### Open Dashboards

```bash
./scripts/open_dashboards.sh
```

## Common Commands

```bash
roadmap smart-next         # Next task
roadmap add-mission ...    # Create mission
roadmap add-step ...       # Add task
mc status                  # Overview
mc watch                   # Live monitoring
mc doctor                  # Diagnostics
```

## Panel Sources

All dashboards read from `panel_output/*.json` (smart_next, risks, progress, decisions, forecast, orchestration, pr_lane, remote_health, revenue).

## Integrations

```bash
python scripts/github_pr_sync.py
python scripts/remote_health_monitor.py
python scripts/stripe_revenue_sync.py
```

## Need Help?

```bash
roadmap --help
mc help
cat docs/README.md
```
