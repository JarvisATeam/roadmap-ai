# roadmap-ai

Python CLI for mission-driven task management with intelligent prioritization.

## Install

```bash
cd ~/roadmap-ai
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Quick Start

```bash
# Initialize roadmap
roadmap init

# Add a mission with revenue target
roadmap add-mission "Launch ORION intelligence layer" --revenue 5000

# Add tasks to mission
roadmap add-task mission_001 "Build NTA scoring module" --energy 3
roadmap add-task mission_001 "Build predictor module" --energy 4
roadmap add-task mission_001 "Wire CLI commands" --energy 2

# Set blockers
roadmap block task_002 --blocked-by task_001

# Get next recommended task
roadmap next

# View full status
roadmap status
```

## Real-World Example

```bash
# Start a new project
roadmap init

# Define the mission
roadmap add-mission "Launch MVP dashboard" --revenue 8000

# Break it into tasks
roadmap add-task mission_001 "Design data schema" --energy 3
roadmap add-task mission_001 "Build API endpoints" --energy 5
roadmap add-task mission_001 "Wire frontend" --energy 4
roadmap add-task mission_001 "Deploy to production" --energy 2

# Set dependencies
roadmap block task_003 --blocked-by task_002  # Frontend needs API
roadmap block task_002 --blocked-by task_001  # API needs schema
roadmap block task_004 --blocked-by task_003  # Deploy needs frontend

# Get ORION recommendation
roadmap smart next
# → Recommends task_001 (highest value, unblocked)

# Work on it and log decision
roadmap decide task_001 "Using PostgreSQL for reliability"
roadmap complete task_001

# Check mission health
roadmap risks
roadmap forecast mission_001

# Get next task
roadmap smart next
# → Now recommends task_002
```

### What to do next

1. **Explore ORION:** Try `roadmap risks` and `roadmap forecast mission_001`
2. **Check intelligence:** Run `roadmap value task_001` to see task value breakdown
3. **Review decisions:** Use `roadmap list-decisions` to see your logged choices
4. **Export data:** Add `--json` to any command for machine-readable output

See [docs/ORION.md](docs/ORION.md) for full intelligence layer documentation.

## Commands

### Core (Phase 1.3 ✅)

| Command | Description | Example |
|---------|-------------|---------|
| `roadmap init` | Initialize roadmap in current directory | `roadmap init` |
| `roadmap add-mission <name>` | Create mission with optional `--revenue` | `roadmap add-mission "Launch MVP" --revenue 5000` |
| `roadmap add-task <mission-id> <name>` | Add task with optional `--energy` | `roadmap add-task mission_001 "Build API" --energy 4` |
| `roadmap block <task-id> --blocked-by <id>` | Set blocking relationship | `roadmap block task_002 --blocked-by task_001` |
| `roadmap next` | Show next available task | `roadmap next` |
| `roadmap status` | Show full roadmap status | `roadmap status --json` |
| `roadmap list-blocks` | Show all blocking relationships | `roadmap list-blocks` |
| `roadmap complete <task-id>` | Mark task done | `roadmap complete task_001` |

### Decision Logging (Phase 1.4)

| Command | Description | Example |
|---------|-------------|---------|
| `roadmap decide <step-id> "<text>"` | Log decision for task/mission | `roadmap decide task_001 "Using Postgres"` |
| `roadmap list-decisions` | Show all logged decisions | `roadmap list-decisions --json` |
| `roadmap show-decision <id>` | Show single decision with context | `roadmap show-decision dec_001` |

### ORION Intelligence (Phase 2)

| Command | Description | Example |
|---------|-------------|---------|
| `roadmap smart next` | AI-ranked next task with scoring | `roadmap smart next --energy 6` |
| `roadmap risks` | Show blocker risks and failure outlook | `roadmap risks --mission mission_001` |
| `roadmap value <task-id>` | Show task value + delay cost | `roadmap value task_003 --json` |
| `roadmap forecast <mission-id>` | Show mission ROI forecast | `roadmap forecast mission_001` |

All commands support `--json` for machine-readable output.

### Status & Reporting (Phase 3 ✅)

| Command | Description | Example |
|---------|-------------|---------|
| `roadmap status` | Show mission/step status | `roadmap status --json` |
| `roadmap report --daily` | Generate ops report | `roadmap report --daily --markdown` |

All commands support `--json` for machine-readable output.

> **📊 Dashboard Integration:** See [docs/DASHBOARD.md](docs/DASHBOARD.md) for JSON schemas and UI integration examples.

## Dashboard Deployment & Validation

### Automated Deployment

```bash
# Prefer remote deployment (falls back automatically)
./scripts/deploy_to_roadmapai.sh

# Set up auto-refresh every 15 minutes
./scripts/setup_cron.sh        # tries ~/roadmapai
./scripts/setup_cron_local.sh  # use if exporting locally to panel_output/
```

### Local Export (Fallback)

```bash
./scripts/export_panels_local.sh
ls -lh panel_output/
```

### Validation (CI/CD Friendly)

```bash
roadmap validate panel_output/smart_next.json
roadmap validate-all panel_output/ --strict  # exits 1 on failure
```

See [docs/DASHBOARD.md](docs/DASHBOARD.md) for full deployment, cron, and validation workflows.


| Command | Description | Example |
|---------|-------------|---------|
| `roadmap smart next` | AI-ranked next task with scoring | `roadmap smart next --energy 6` |
| `roadmap risks` | Show blocker risks and failure outlook | `roadmap risks --mission mission_001` |
| `roadmap value <task-id>` | Show task value + delay cost | `roadmap value task_003 --json` |
| `roadmap forecast <mission-id>` | Show mission ROI forecast | `roadmap forecast mission_001` |

> **📘 Deep dive:** See [docs/ORION.md](docs/ORION.md) for scoring formulas, calibration guide, and usage patterns.

All commands support `--json` for machine-readable output.

## Project Status

- **Phase 1.3**: Core CLI — ✅ complete (`b7722e9`)
- **Phase 1.4**: Decision logging — 🟡 in progress
- **Phase 2.0**: ORION intelligence — 🟡 planned

### Pilot Status (Day 7)

- Phase 2.5 production pilot: **GO WITH FIXES** (ORION ~78% accurate, ready for dashboards once small fixes land)
- ORION working set: mission `M-e9f70c2e` (€4000) with 5 energy-tagged tasks
- Main gap: deadlines/urgency not yet captured, so overdue tasks are treated equal

## Documentation

- [ROADMAP.md](docs/ROADMAP.md) — Full project plan
- [DECISIONS.md](docs/DECISIONS.md) — Decision log format
- [ORION.md](docs/ORION.md) — Intelligence layer specification

## Daily Workflow (Production Use)

```bash
# Morning standup
roadmap smart next
roadmap risks
roadmap list-decisions | tail -5

# During work
roadmap decide <step-id> "Tech: Switching to WebSockets for dashboard latency"

# End of day
roadmap forecast M-e9f70c2e
```

Top commands from pilot (7 days):
- `roadmap smart next` — 18 uses — primary prioritization loop
- `roadmap decide` — 12 uses — decisions + ORION feedback
- `roadmap add-step` — 9 uses — queueing mission work

> Tip: When adding a step, capture its deadline for ORION with `roadmap add-step M-XXXX "Task" --energy 3 --due 2024-04-05`. Due dates directly influence the urgency factor used by `roadmap smart next`.
- `roadmap risks` — 7 uses — blocker cascade detection
- `roadmap list-decisions` — 5 uses — re-entry context

## Troubleshooting

### `roadmap: command not found`

```bash
# Activate the virtual environment first
source venv/bin/activate
pip install -e .
```

### `smart next` says "No available tasks"

All tasks are either completed or blocked. Check:

```bash
roadmap list-blocks
roadmap status
```

### ORION commands return empty results

Ensure missions have revenue and tasks include energy:

```bash
roadmap add-mission "Mission" --revenue 5000
roadmap add-task mission_001 "Task" --energy 3
```

### Tests fail with import errors

```bash
pip install -e .
pytest tests/ -v
```

## Calibrated Scales (Pilot)

**Revenue (what operators actually used):**
- €500  → hygiene / backup work (docs, small fixes)
- €1000 → normal features / UX polish
- €2000 → important integrations / APIs
- €4000 → launch blockers (dashboard integration)
- €8000 → critical contractual deliverables / go-no-go work

**Energy (self-reported effort):**
- 1–2 → quick scripts / status updates between meetings
- 3–4 → standard development (1–2 hour blocks)
- 5–7 → deep code or integrations (half-day focus)
- 8–10 → architecture / refactor / high-risk work (full-day uninterrupted)

## License

MIT
