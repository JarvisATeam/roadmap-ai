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

> **📘 Deep dive:** See [docs/ORION.md](docs/ORION.md) for scoring formulas, calibration guide, and usage patterns.

All commands support `--json` for machine-readable output.

## Project Status

- **Phase 1.3**: Core CLI — ✅ complete (`b7722e9`)
- **Phase 1.4**: Decision logging — 🟡 in progress
- **Phase 2.0**: ORION intelligence — 🟡 planned

## Documentation

- [ROADMAP.md](docs/ROADMAP.md) — Full project plan
- [DECISIONS.md](docs/DECISIONS.md) — Decision log format
- [ORION.md](docs/ORION.md) — Intelligence layer specification

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

## License

MIT
