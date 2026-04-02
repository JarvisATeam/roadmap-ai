# ORION Intelligence Layer — Specification

ORION provides intelligent task prioritization, risk prediction, and revenue forecasting for roadmap-ai.

## Pilot Status

- Phase 2.5 production pilot verdict: **GO WITH FIXES** — ORION delivered ~78% correct recommendations.
- Strength: revenue × energy scoring works on real mission `M-e9f70c2e` (€4000, 5 steps).
- Gap: no deadline/urgency input yet, so overdue tasks are treated the same as normal ones.

## Components

```
┌─────────────────────────────────────────────┐
│                   ORION                      │
├─────────────┬─────────────┬─────────────────┤
│    NTA      │  Predictor  │    Revenue      │
│  (scoring)  │   (risk)    │   (value)       │
└─────────────┴─────────────┴─────────────────┘
        ↓             ↓              ↓
   smart next      risks      value/forecast
```

---

## NTA — Next Task Algorithm

**File:** `roadmap/core/nta.py`

### Formula

```
score = (revenue × urgency × energy_match) - context_cost - risk_penalty
```

**Plain English**

```
Task score = How valuable × How urgent × How good a fit
             minus switching cost
             minus blocker risk
```

**Example**

```
Task A (critical API)
- Revenue weight: 1.0 (highest mission value)
- Urgency: 1.5 (due in 2 days)
- Energy match: 1.0 (needs 5 energy, you have 5)
- Context cost: 0.0 (same mission as last task)
- Risk penalty: 0.0 (no blockers)
Score: (1.0 × 1.5 × 1.0) - 0 - 0 = 1.5

Task B (docs update)
- Revenue weight: 0.1
- Urgency: 0.8 (no deadline)
- Energy match: 0.6 (needs 1 energy, you have 5)
- Context cost: 0.2 (mission switch)
- Risk penalty: 0.2 (two blockers)
Score: (0.1 × 0.8 × 0.6) - 0.2 - 0.2 = -0.35

→ ORION picks Task A.
```

### Factors

#### Revenue Weight (0.0 – 1.0)
```python
revenue_weight = mission.revenue / max_revenue_in_roadmap
```

#### Urgency (0.0 – 2.0)
```python
if task.deadline:
    days_until = (deadline - now).days
    if days_until <= 0:
        urgency = 2.0  # overdue
    elif days_until <= 3:
        urgency = 1.5  # critical
    elif days_until <= 7:
        urgency = 1.2  # soon
    else:
        urgency = 1.0  # normal
else:
    urgency = 0.8  # no deadline = lower priority
```

#### Energy Match (0.5 – 1.0)
```python
energy_diff = abs(current_energy - task.energy)
energy_match = 1.0 - (energy_diff * 0.1)
energy_match = max(0.5, energy_match)
```

#### Context Cost (0.0 – 0.3)
```python
if last_task.mission_id == task.mission_id:
    context_cost = 0.0  # same mission, no switch
else:
    context_cost = 0.2  # mission switch penalty

if last_task.type == task.type:
    context_cost -= 0.05  # similar work bonus
```

#### Risk Penalty (0.0 – 0.5)
```python
blocker_depth = count_blocker_chain(task)
risk_penalty = min(0.5, blocker_depth * 0.1)
```

### Output

```json
{
  "task_id": "task_001",
  "task_name": "Build NTA scoring module",
  "score": 0.847,
  "factors": {
    "revenue_weight": 1.0,
    "urgency": 1.2,
    "energy_match": 0.9,
    "context_cost": 0.0,
    "risk_penalty": 0.1
  },
  "rank": 1
}
```

---

## Predictor — Risk Analysis

**File:** `roadmap/core/predictor.py`

### Blocker Risk

```python
def blocker_risk(task):
    chain = get_blocker_chain(task)
    depth = len(chain)
    unresolved = sum(1 for t in chain if not t.completed)
    
    risk = (depth * 0.15) + (unresolved * 0.25)
    return min(1.0, risk)
```

### Mission Failure Probability

```python
def mission_failure_prob(mission):
    tasks = get_tasks(mission)
    blocked_count = sum(1 for t in tasks if is_blocked(t))
    overdue_count = sum(1 for t in tasks if is_overdue(t))
    
    prob = (blocked_count / len(tasks)) * 0.4
    prob += (overdue_count / len(tasks)) * 0.6
    
    return min(1.0, prob)
```

### Early Warning

```python
def get_warnings(mission):
    warnings = []
    
    if mission_failure_prob(mission) > 0.5:
        warnings.append({
            "type": "high_failure_risk",
            "message": f"Mission {mission.id} has >50% failure probability",
            "severity": "critical"
        })
    
    for task in get_tasks(mission):
        if blocker_risk(task) > 0.7:
            warnings.append({
                "type": "blocker_cascade",
                "message": f"Task {task.id} has deep blocker chain",
                "severity": "warning"
            })
    
    return warnings
```

### Output

```json
{
  "mission_id": "mission_001",
  "failure_probability": 0.23,
  "warnings": [
    {
      "type": "blocker_cascade",
      "task_id": "task_003",
      "message": "Deep blocker chain detected",
      "severity": "warning"
    }
  ],
  "blocked_tasks": 2,
  "overdue_tasks": 0
}
```

---

## Revenue — Value Calculation

**File:** `roadmap/core/revenue.py`

### Task Value

```python
def task_value(task, mission):
    task_count = len(get_tasks(mission))
    base_value = mission.revenue / task_count
    
    # Critical path bonus
    if is_on_critical_path(task):
        base_value *= 1.5
    
    # Blocker bonus (unblocks others)
    unblocks = count_tasks_blocked_by(task)
    base_value += unblocks * (mission.revenue * 0.05)
    
    return base_value
```

### Delay Cost

```python
def delay_cost(task, days=1):
    value = task_value(task, task.mission)
    daily_cost = value * 0.02  # 2% per day
    
    # Cascade multiplier
    blocked_tasks = get_tasks_blocked_by(task)
    cascade = 1.0 + (len(blocked_tasks) * 0.1)
    
    return daily_cost * days * cascade
```

### Mission Forecast

```python
def forecast(mission):
    tasks = get_tasks(mission)
    completed = [t for t in tasks if t.completed]
    remaining = [t for t in tasks if not t.completed]
    
    if not completed:
        velocity = 1.0  # default: 1 task/day
    else:
        # Calculate actual velocity from history
        first_complete = min(t.completed_at for t in completed)
        days_elapsed = (now - first_complete).days or 1
        velocity = len(completed) / days_elapsed
    
    days_remaining = len(remaining) / velocity
    expected_completion = now + timedelta(days=days_remaining)
    
    return {
        "mission_id": mission.id,
        "revenue": mission.revenue,
        "completion_probability": 1.0 - mission_failure_prob(mission),
        "expected_completion": expected_completion.isoformat(),
        "days_remaining": days_remaining,
        "velocity": velocity,
        "tasks_completed": len(completed),
        "tasks_remaining": len(remaining)
    }
```

### Output

```json
{
  "mission_id": "mission_001",
  "revenue": 5000,
  "completion_probability": 0.77,
  "expected_completion": "2025-01-22T00:00:00Z",
  "days_remaining": 7,
  "velocity": 1.2,
  "tasks_completed": 3,
  "tasks_remaining": 5
}
```

---

## CLI Commands

### `roadmap smart next`

```bash
$ roadmap smart next
╭─────────────────────────────────────────────╮
│ RECOMMENDED NEXT TASK                       │
├─────────────────────────────────────────────┤
│ task_001: Build NTA scoring module          │
│ Score: 0.847                                │
│ Mission: Launch ORION (€5000)               │
│                                             │
│ Why this task:                              │
│ • Highest revenue mission                   │
│ • No blockers                               │
│ • Good energy match                         │
╰─────────────────────────────────────────────╯
```

**No available tasks**

```bash
$ roadmap smart next
No available tasks.

# Resolve blockers or add tasks
$ roadmap list-blocks
$ roadmap add-task mission_001 "New task" --energy 3
```

**JSON**

```bash
$ roadmap smart next --json
{
  "task_id": "task_001",
  "task_name": "Build NTA scoring module",
  "mission_id": "mission_001",
  "score": 0.847,
  "factors": {
    "revenue_weight": 1.0,
    "urgency": 1.2,
    "energy_match": 0.9,
    "context_cost": 0.0,
    "risk_penalty": 0.1
  },
  "rank": 1
}
```

### `roadmap risks`

```bash
$ roadmap risks
╭─────────────────────────────────────────────╮
│ RISK ANALYSIS                               │
├─────────────────────────────────────────────┤
│ Mission: Launch ORION                       │
│ Failure probability: 23%                    │
│                                             │
│ Warnings:                                   │
│ ⚠ task_003 has deep blocker chain          │
│                                             │
│ Blocked tasks: 2                            │
│ Overdue tasks: 0                            │
╰─────────────────────────────────────────────╯
```

### `roadmap value <task-id>`

```bash
$ roadmap value task_001
╭─────────────────────────────────────────────╮
│ TASK VALUE: task_001                        │
├─────────────────────────────────────────────┤
│ Base value: €625                            │
│ Critical path bonus: +€312                  │
│ Unblock bonus: +€250 (unblocks 2 tasks)     │
│ Total value: €1187                          │
│                                             │
│ Delay cost: €24/day                         │
│ Cascade multiplier: 1.2x                    │
╰─────────────────────────────────────────────╯
```

### `roadmap forecast <mission-id>`

```bash
$ roadmap forecast mission_001
╭─────────────────────────────────────────────╮
│ MISSION FORECAST: Launch ORION              │
├─────────────────────────────────────────────┤
│ Revenue: €5000                              │
│ Completion probability: 77%                 │
│ Expected completion: 2025-01-22             │
│ Days remaining: 7                           │
│                                             │
│ Progress: ████████░░░░ 3/8 tasks            │
│ Velocity: 1.2 tasks/day                     │
╰─────────────────────────────────────────────╯
```

---

## Common Patterns

### Daily Standup Workflow

```bash
# 1. Check mission health
roadmap risks

# 2. Review yesterday's decisions
roadmap list-decisions | tail -5

# 3. Get today's recommendation
roadmap smart next

# 4. Check forecast if blocked
roadmap forecast mission_001
```

### Task Selection Strategy

**Scenario 1: High energy, clear calendar**
```bash
roadmap smart next --energy 8
# → ORION recommends deep work (energy 7-9)
```

**Scenario 2: Fragmented time, low energy**
```bash
roadmap smart next --energy 2
# → ORION recommends quick wins (energy 1-3)
```

**Scenario 3: Mission at risk**
```bash
roadmap risks --mission mission_001
roadmap value task_003  # Check blocker impact
roadmap decide task_003 "Prioritizing to unblock critical path"
```

### When ORION Disagrees With You

**ORION says:** `task_005` (low score)  
**You want:** `task_002` (high score, but blocked)

```bash
# Debug the scoring
roadmap value task_002
# → Shows it's blocked by 2 tasks

# Check blocker chain
roadmap list-blocks --task task_002
# → Reveals deep dependency

# Either: resolve blockers first
roadmap complete task_001
roadmap smart next  # task_002 now unblocked

# Or: log why you're overriding
roadmap decide task_002 "Overriding ORION: external deadline forces this"
```

### Tuning ORION Over Time

**Week 1:** Use default revenue/energy
```bash
roadmap add-mission "Test project" --revenue 1000
```

**Week 2:** Check forecast accuracy
```bash
roadmap forecast mission_001
# Expected: 2025-01-20
# Actual: 2025-01-22 (2 days late)
```

**Week 3:** Adjust revenue if ORION consistently over/under-prioritizes
```bash
# If ORION under-prioritized this mission:
# Increase revenue weight for similar missions
roadmap add-mission "Similar project" --revenue 1500  # was 1000
```

**Week 4:** You now have calibrated revenue scale for your work type
```bash
# Your personal scale:
# €500 = quick fixes
# €1000 = standard features
# €2000 = critical path work
# €5000 = launch blockers
```

---

## Calibration Guide

ORION is only as strong as the inputs you provide. Check these dials whenever recommendations feel off.

### Revenue Calibration

Start with relative sizing:

```bash
roadmap add-mission "Baseline" --revenue 1000
roadmap add-mission "Small fix" --revenue 200
roadmap add-mission "Major launch" --revenue 5000
```

Every couple of weeks, compare `roadmap forecast` results to real progress and nudge the revenue weights up or down.

### Energy Calibration

- 1–2 → quick wins, can multitask
- 3–4 → normal engineering work
- 5–7 → deep work requiring long focus blocks
- 8–10 → research/architecture, major uncertainty

Add +1 for junior contributors or +2 for unfamiliar technology.

### Urgency Tuning

Deadlines directly influence urgency. If tasks never appear urgent, add or tighten due dates:

```bash
roadmap add-task mission_001 "Comms plan" --energy 3 --deadline 2025-01-20
```

### When Scores Look Wrong

```bash
roadmap value task_001      # Inspect value and delay cost
roadmap list-blocks         # Clear stale blockers
roadmap status --json | jq '.missions[].revenue'
```

---

## Real Operator Workflow (Pilot)

```bash
# Morning loop
roadmap smart next
roadmap risks
roadmap list-decisions | tail -5

# During work
roadmap decide <step-id> "Tech: Switching dashboard transport to WebSockets"

# End of day
roadmap forecast M-e9f70c2e
```

**Top production commands (7 days):**
1. `roadmap smart next` — 18 uses — prioritization heartbeat.
2. `roadmap decide` — 12 uses — logging decisions + ORION feedback.
3. `roadmap add-step` — 9 uses — adding energy-tagged tasks to missions.
4. `roadmap risks` — 7 uses — blocker cascade scan.
5. `roadmap list-decisions` — 5 uses — re-entry context.

**Validated revenue scale:**
- €500  → hygiene / backup work (docs, small fixes)
- €1000 → normal features / UX polish
- €2000 → integration/API deliverables
- €4000 → launch blockers (dashboard integration tasks)
- €8000 → critical contractual / go-no-go work

**Validated energy scale:**
- 1–2 → quick scripts / status updates between meetings
- 3–4 → normal development / 1–2 hour blocks
- 5–7 → deep integrations or code work / half-day focus
- 8–10 → architecture / refactor / high-risk work / full-day

## Critical Dashboard Panels (Phase 3 Targets)

1. **Smart Next Panel** — show `roadmap smart next` with score + factors — so operators instantly know next action.
2. **Risk Summary Panel** — show `roadmap risks --json` (blocked counts + warnings) — early warning on cascades.
3. **Forecast Panel** — show `roadmap forecast <mission>` (probability, completion date) — stakeholder-facing delivery state.
4. **Recent Decisions Panel** — show latest 5 `roadmap decide` entries — quick context when switching operators.
5. **Mission Progress Panel** — show task count + total energy per mission — visualizes momentum and workload.

## Known Gaps Before Dashboard Build

- `roadmap decide` still expects full UUIDs; needs short ID/prefix support for fast logging.
- ORION urgency ignores deadlines; need due-date capture in `add-step` and scoring.
- Need a `roadmap list-steps --mission` (or similar) command to feed dashboards with batch task data.

## Phase 3 Readiness

- **Status:** GO WITH FIXES.
- **Reason:** CLI + ORION are production-usable, but dashboards must wait for short IDs, deadline support, and mission task listing.

---

## Testing

```bash
pytest tests/test_nta.py -v
pytest tests/test_predictor.py -v
pytest tests/test_revenue.py -v
```

### Coverage Target

- `nta.py`: >90%
- `predictor.py`: >80%
- `revenue.py`: >80%
