# ROADMAP — roadmap-ai

Master plan for Python roadmap CLI development.

## Visual Roadmap

```
┌─────────────────────────────────────────────────────────────┐
│                    ROADMAP-AI PHASES                        │
├────────────┬──────────────┬──────────────┬─────────────────┤
│  Phase 1.3 │  Phase 1.4   │   Phase 2.0  │   Phase 3.0     │
│    CORE    │  DECISIONS   │    ORION     │  INTEGRATION    │
│     ✅     │      ✅      │      ✅      │      🔵         │
└────────────┴──────────────┴──────────────┴─────────────────┘
  2d build      3h build      1.5d build      TBD
  b7722e9       [current]     [current]       (planned)
```

## Overview

```
Phase 1.3  Core CLI + blocking        ✅ complete
Phase 1.4  Decision logging           🟡 next
Phase 2.0  ORION intelligence         🟡 planned
Phase 3.0  Dashboard integration      🔵 future
```

---

## Phase 2.5 Pilot — Day 7 Status

- Verdict: **GO WITH FIXES** — ORION recommendation accuracy ~78% on mission `M-e9f70c2e` (€4000).
- Strengths: mission-aware `add-step` workflow with energy tagging feeds ORION scoring end-to-end.
- Gaps before dashboards: deadline capture for urgency, short IDs/prefixes for `roadmap decide`, and batch `list-steps` data.

---

## Phase 1.3 ✅ Complete

**Commit:** `b7722e9`  
**Branch:** `master`  
**Status:** Remote-synced, tests passing

### Delivered

- `roadmap init` — initialize JSON store
- `roadmap add-mission` — create mission with revenue
- `roadmap add-task` — add task to mission with energy cost
- `roadmap block` — set blocking relationships
- `roadmap next` — get next unblocked task
- `roadmap status` — full status display
- `roadmap list-blocks` — show all blockers
- `roadmap complete` — mark task done

### Storage

```
~/.roadmap/
├── missions.json
├── tasks.json
└── blocks.json
```

---

## Phase 1.4 🟡 In Progress — Decision Logging

**Gate:** Phase 1.3 complete ✅  
**Estimate:** 2–3 hours

### Commands

```bash
roadmap decide <step-id> "decision text"
roadmap list-decisions
roadmap show-decision <decision-id>
```

### Storage Addition

```
~/.roadmap/
└── decisions.json
```

### Schema

```json
{
  "id": "dec_001",
  "step_id": "task_001",
  "step_type": "task",
  "decision": "Using SQLite for Phase 3 storage",
  "timestamp": "2025-01-15T14:32:00Z",
  "context": {
    "mission_id": "mission_001",
    "blockers": [],
    "energy": 3
  }
}
```

### Done When

- [ ] All three commands functional
- [ ] `--json` output supported
- [ ] Tests in `tests/test_decisions.py`
- [ ] Committed and pushed

---

## Phase 2.0 ✅ Complete — ORION Intelligence Layer

### Why ORION Matters

Without ORION:
- Pick tasks manually → higher chance of ignoring high-value work
- No early warning → missions fail silently until deadlines pass
- Guess at impact → time spent on low-ROI tasks without realizing it

With ORION:
- `smart next` keeps contributors focused on the most valuable, unblocked task
- `risks` highlights blocker cascades before they derail a mission
- `value` explains cost of delay so trade-offs are explicit
- `forecast` predicts completion probability alongside revenue

Avoiding even one week of wrong-priority work (~€2k–€5k) easily pays for the ORION build effort.

**Gate:** Phase 1.4 complete (or explicit skip)  
**Estimate:** 1–2 days  
**ROI:** €2k–€8k projected

### Core Modules

#### `roadmap/core/nta.py` — Next Task Algorithm

```python
score = (revenue × urgency × energy_match) - context_cost - risk_penalty
```

Factors:
- **revenue**: Mission value weight
- **urgency**: Days until deadline / overdue penalty
- **energy_match**: Current energy vs task requirement
- **context_cost**: Task switching penalty
- **risk_penalty**: Blocker chain depth

#### `roadmap/core/predictor.py` — Risk Prediction

- Blocker chain analysis
- Mission failure probability
- Delay cascade detection
- Early warning signals

#### `roadmap/core/revenue.py` — Value Calculation

- Task value attribution
- Delay cost per day
- Mission ROI projection
- Completion forecast

### CLI Commands

```bash
roadmap smart next              # AI-ranked recommendation
roadmap smart next --json       # Machine-readable

roadmap risks                   # All current risks
roadmap risks --mission m001    # Mission-specific

roadmap value task_001          # Task value breakdown
roadmap value task_001 --json

roadmap forecast mission_001    # Mission completion/ROI forecast
```

### File Structure

```
roadmap/
├── core/
│   ├── nta.py
│   ├── predictor.py
│   └── revenue.py
├── cli/
│   └── smart_commands.py
tests/
├── test_nta.py
├── test_predictor.py
└── test_revenue.py
docs/
└── ORION.md
```

### Done When

- [ ] All four commands functional
- [ ] `--json` output on all
- [ ] >80% test coverage on new modules
- [ ] `docs/ORION.md` complete
- [ ] Committed and pushed

---

## Phase 3.0 🔵 Planned — Dashboard Integration

**Gate:** Phase 2 complete ✅  
**Estimate:** 3–5 days  
**ROI:** €1k–€3k (operator time savings)

### Scope

#### JSON Export Contract

Standardized output format for all commands:

```json
{
  "roadmap_version": "0.2.0",
  "timestamp": "2025-01-15T14:32:00Z",
  "command": "smart next",
  "data": { ... },
  "metadata": {
    "missions_count": 3,
    "tasks_total": 12,
    "tasks_blocked": 2
  }
}
```

#### Dashboard Surface Points

1. **Status Panel**
   - Current mission health (from `roadmap status --json`)
   - Top 3 risks (from `roadmap risks --json`)
   - Next recommended task (from `roadmap smart next --json`)

2. **Forecast Panel**
   - Mission completion probability
   - Expected delivery dates
   - Revenue at risk

3. **Decision Trail**
   - Last 10 decisions with context
   - Filter by mission/task
   - Export to PDF/Markdown

#### Integration with `~/roadmapai`

```bash
# ~/roadmapai wrapper calls roadmap-ai
bin/roadmap_python.sh smart next --json > /tmp/orion_next.json

# Dashboard reads JSON
dashboard/orion_panel.py render /tmp/orion_next.json
```

### Done When

- [ ] All commands have stable `--json` schema
- [ ] `~/roadmapai` can consume output without parsing hacks
- [ ] Dashboard shows at least 3 ORION-powered panels
- [ ] Daily ops report generator works (`roadmap report --daily`)

### Why Phase 3

**Current state:** CLI tools work, but require terminal context-switching.

**Phase 3 state:** Dashboard surfaces ORION intelligence at a glance.

**Value:** Operator sees risks/recommendations without leaving mission-control UI.

### Real Operator Workflow (Pilot)

```bash
# Morning
roadmap smart next
roadmap risks
roadmap list-decisions | tail -5

# During work
roadmap decide <step-id> "Tech: Switching dashboard transport to WebSockets"

# End of day
roadmap forecast M-e9f70c2e
```

**Top commands (7-day pilot):**
1. `roadmap smart next` — 18 uses — prioritization heartbeat.
2. `roadmap decide` — 12 uses — decision logging + ORION feedback.
3. `roadmap add-step` — 9 uses — expanding the mission backlog with energy-tagged work.
4. `roadmap risks` — 7 uses — blocker cascade scan every morning.
5. `roadmap list-decisions` — 5 uses — re-entry context and daily review.

**Validated revenue scale:**
- €500  → hygiene / backup work (docs, small fixes)
- €1000 → normal features / UX polish
- €2000 → integration/API deliverables
- €4000 → launch blockers (dashboard integration tasks)
- €8000 → critical contractual / go-no-go work

**Validated energy scale:**
- 1–2 → quick scripts / status updates between meetings
- 3–4 → normal development / 1–2 hour blocks
- 5–7 → deep integrations / half-day focus
- 8–10 → architecture / refactor / high-risk work (full day)

**Critical dashboard panels (Phase 3 targets):**
1. Smart Next Panel — show `roadmap smart next` with score + factors.
2. Risk Summary Panel — show `roadmap risks --json` (blocked counts, warnings).
3. Forecast Panel — show `roadmap forecast <mission>` (probability, completion date).
4. Recent Decisions Panel — show latest 5 decision entries for context.
5. Mission Progress Panel — show task count + total energy per mission.

**Known gaps before dashboard build:**
- `roadmap decide` needs short ID/prefix support (UUID logging is slow).
- Deadlines/urgency need to flow into `add-step` and ORION scoring.
- Need `roadmap list-steps --mission` (or equivalent) for batch data feeds to the UI.

**Phase 3 readiness:** GO WITH FIXES — build dashboards after the above fixes land.

---

## Migration Guide

### Upgrading from Phase 1.3 to Phase 2.0

Existing data in `~/.roadmap/*.json` remains compatible. To unlock full ORION scoring, ensure revenue and energy are set:

```bash
# Phase 1.3 data (minimal metadata)
roadmap add-mission "Legacy mission"
roadmap add-task mission_001 "Legacy task"

# Phase 2.0 data (revenue + energy aware)
roadmap add-mission "Revenue mission" --revenue 5000
roadmap add-task mission_002 "Energy-aware task" --energy 3
```

**Energy scale guidance**

- 1–2 → quick wins, low cognitive load
- 3–4 → standard engineering tasks
- 5–7 → deep work, multi-hour focus blocks
- 8–10 → research or architecture spikes

**Revenue guidance**

- Use actual contract value when known
- Use opportunity cost for internal initiatives
- If numbers are unknown, keep consistent relative values (e.g., 1k / 3k / 5k)

---

## Stop Rules

1. No Phase 2 work until Phase 1.4 pushed (or explicit skip documented)
2. No status claims without fresh Git Proof Pack
3. No dashboard ORION panels until ORION commands tested

---

## Proof Requirements

Each phase closeout requires:

```bash
git status -sb          # clean
git log --oneline -3    # shows phase commit
git remote -v           # shows origin
git push origin master  # up to date
```
