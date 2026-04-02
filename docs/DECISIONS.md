# Decision Log — roadmap-ai

Decisions recorded via `roadmap decide` for audit trail and ORION input.

## Usage

```bash
# Log a decision
roadmap decide task_001 "Using retry logic instead of fail-fast"

# List all decisions
roadmap list-decisions

# Show specific decision
roadmap show-decision dec_001
```

## When to Log Decisions

**Log it when:**
- ✅ You choose one technical approach over another and need future context
- ✅ You accept or mitigate a risk ("Shipping without load testing, monitor instead")
- ✅ Scope or priority shifts ("Dropping real-time sync from MVP")
- ✅ A blocker requires a workaround or parallel track

**Skip it when:**
- ❌ You simply completed a task (use `roadmap complete` instead)
- ❌ The choice is obvious and has no alternatives
- ❌ It's a temporary reminder better suited for project notes

If you'd want to remember *why* in six months, log it.

## Schema

```json
{
  "id": "dec_001",
  "step_id": "task_001",
  "step_type": "task",
  "decision": "Using retry logic instead of fail-fast",
  "timestamp": "2025-01-15T14:32:00Z",
  "context": {
    "mission_id": "mission_001",
    "mission_name": "Launch ORION intelligence layer",
    "blockers": ["task_000"],
    "blocked_by_count": 1,
    "energy": 3,
    "revenue_weight": 5000
  }
}
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique decision ID (`dec_XXX`) |
| `step_id` | string | Task or mission this decision applies to |
| `step_type` | string | `"task"` or `"mission"` |
| `decision` | string | The decision text |
| `timestamp` | ISO8601 | When decision was logged |
| `context` | object | Snapshot of relevant state at decision time |

## Storage

```
~/.roadmap/decisions.json
```

## ORION Integration

Decisions feed into ORION predictor:
- Decision patterns inform risk scoring
- Historical decisions improve task value estimation
- Context snapshots enable decision replay

---

## Decision Review Workflow

### Weekly Review

```bash
# See all decisions from last 7 days
roadmap list-decisions | grep "2025-01-"

# Filter by specific mission
roadmap list-decisions --json | jq '.decisions[] | select(.context.mission_id == "mission_001")'

# Export for retrospective
roadmap list-decisions --json > decisions_week_02.json
```

### Debugging Failed Missions

When a mission fails or gets delayed:

```bash
# 1. Find all decisions for that mission
roadmap list-decisions --json | \
  jq '.decisions[] | select(.context.mission_id == "mission_003")'

# 2. Review decision timeline
roadmap show-decision dec_015
roadmap show-decision dec_018
roadmap show-decision dec_022

# 3. Identify pattern
# Example: "We kept deferring task_007 due to blockers"
# → Next time: resolve blockers earlier
```

### Decision Templates

**Technical choice:**
```bash
roadmap decide task_001 "Tech: Using Postgres over MongoDB because [reason]"
```

**Scope change:**
```bash
roadmap decide mission_002 "Scope: Dropping real-time sync from MVP to hit deadline"
```

**Risk acceptance:**
```bash
roadmap decide task_005 "Risk: Shipping without load test, will monitor in prod"
```

**Blocker resolution:**
```bash
roadmap decide task_003 "Blocked: Waiting on API access, building mock in parallel"
```

Using consistent prefixes (`Tech:`, `Scope:`, `Risk:`, `Blocked:`) makes decisions searchable:

```bash
roadmap list-decisions | grep "Risk:"
```

---

## Example Output

**Terminal**

```bash
$ roadmap list-decisions
Decisions (2):

  dec_001 | task_001
    Using retry logic instead of fail-fast
    @ 2025-01-15T14:32:00Z

  dec_002 | mission_001
    Prioritizing ORION over decision logging
    @ 2025-01-15T15:00:00Z
```

**JSON**

```bash
$ roadmap list-decisions --json
{
  "decisions": [
    {
      "id": "dec_001",
      "step_id": "task_001",
      "decision": "Using retry logic instead of fail-fast",
      "timestamp": "2025-01-15T14:32:00Z"
    },
    {
      "id": "dec_002",
      "step_id": "mission_001",
      "decision": "Prioritizing ORION over decision logging",
      "timestamp": "2025-01-15T15:00:00Z"
    }
  ],
  "count": 2
}
```
