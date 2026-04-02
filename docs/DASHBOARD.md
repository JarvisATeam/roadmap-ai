# Dashboard Integration Guide

Complete guide for integrating roadmap-ai with dashboard systems.

## Overview

roadmap-ai provides standardized JSON exports for 5 core operational panels:

1. **Smart Next** — ORION-recommended next task
2. **Risk Summary** — Blocker analysis and warnings
3. **Mission Progress** — Task completion status
4. **Recent Decisions** — Latest logged decisions
5. **Daily Report** — Aggregated ops summary

All commands support `--json` output with a consistent envelope schema.

---

## JSON Envelope Schema

All JSON exports follow this structure:

```json
{
  "roadmap_version": "0.3.0",
  "timestamp": "2025-04-02T21:22:00Z",
  "command": "smart next",
  "data": {
    // Command-specific payload
  },
  "metadata": {
    "missions_count": 1,
    "steps_total": 6,
    "steps_completed": 2,
    "steps_remaining": 4
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `roadmap_version` | string | roadmap-ai version |
| `timestamp` | ISO8601 | Generation time (UTC) |
| `command` | string | Command that generated this data |
| `data` | object | Command-specific payload |
| `metadata` | object | Global metrics (missions, steps, etc.) |

---

## Panel 1: Smart Next

**Command:**
```bash
roadmap smart next --json
```

**Output:**
```json
{
  "roadmap_version": "0.3.0",
  "timestamp": "2025-04-02T21:22:00Z",
  "command": "smart next",
  "data": {
    "recommendation": {
      "step_id": "abc123...",
      "description": "Design JSON export contract",
      "mission_id": "def456...",
      "score": 0.8,
      "factors": {
        "revenue_weight": 1.0,
        "urgency": 1.0,
        "energy_match": 1.0,
        "context_cost": 0.0,
        "risk_penalty": 0.2
      }
    }
  },
  "metadata": {
    "missions_count": 1,
    "steps_total": 6,
    "steps_completed": 2,
    "steps_remaining": 4,
    "energy_input": 5
  }
}
```

**UI Consumption:**

```javascript
// React example
const SmartNextPanel = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('/data/roadmap/smart_next.json')
      .then(r => r.json())
      .then(setData);
  }, []);
  
  if (!data?.data?.recommendation) return <div>No tasks available</div>;
  
  const rec = data.data.recommendation;
  return (
    <Panel title="🎯 Next Recommended Task">
      <TaskCard 
        description={rec.description}
        score={rec.score}
        factors={rec.factors}
      />
    </Panel>
  );
};
```

**Refresh Strategy:**
- Manual: User-triggered via button
- Auto: On task completion
- Interval: Not recommended (use on-demand)

---

## Panel 2: Risk Summary

**Command:**
```bash
roadmap risks --json
```

**Output:**
```json
{
  "roadmap_version": "0.3.0",
  "command": "risks",
  "data": {
    "missions_analyzed": 1,
    "warnings": [
      {
        "type": "blocker_cascade",
        "mission_id": "...",
        "task_id": "...",
        "message": "Deep blocker chain detected",
        "severity": "warning",
        "risk": 0.8
      }
    ],
    "blocked_steps": 2,
    "overdue_steps": 0,
    "critical_warnings": 0,
    "summary_warnings": 1
  }
}
```

**UI Consumption:**

```python
# Python/Flask example
import json

def get_risk_status():
    with open('data/roadmap/risks.json') as f:
        data = json.load(f)
    
    risks = data['data']
    return {
        'level': 'critical' if risks['critical_warnings'] > 0 else 'warning' if risks['blocked_steps'] > 0 else 'ok',
        'blocked_count': risks['blocked_steps'],
        'warnings': risks['warnings']
    }
```

**Refresh Strategy:**
- Interval: Every 30 minutes
- Trigger: After blocker changes

---

## Panel 3: Mission Progress

**Command:**
```bash
roadmap status --json
```

**Output:**
```json
{
  "command": "status",
  "data": {
    "missions": [
      {
        "id": "...",
        "mission_code": "M-e9f70c2e",
        "title": "Dashboard Integration (Phase 3)",
        "status": "active",
        "revenue": 4000,
        "steps_total": 6,
        "steps_completed": 2,
        "steps_in_progress": 2,
        "steps_blocked": 1,
        "steps_todo": 1
      }
    ],
    "missions_count": 1
  }
}
```

**UI Consumption:**

```html
<!-- HTML/CSS example -->
<div class="mission-panel">
  <h3>📈 Mission Progress</h3>
  <div class="mission" data-mission-code="M-e9f70c2e">
    <h4>Dashboard Integration (Phase 3)</h4>
    <div class="progress-bar">
      <div class="fill" style="width: 33%"></div>
    </div>
    <div class="stats">
      <span>✅ 2 done</span>
      <span>🔄 2 in progress</span>
      <span>🚫 1 blocked</span>
      <span>📋 1 todo</span>
    </div>
  </div>
</div>

<script>
fetch('data/roadmap/status.json')
  .then(r => r.json())
  .then(data => {
    const mission = data.data.missions[0];
    const pct = (mission.steps_completed / mission.steps_total) * 100;
    document.querySelector('.fill').style.width = pct + '%';
  });
</script>
```

**Refresh Strategy:**
- Interval: Every 15 minutes
- Trigger: After task completion/status change

---

... [continue entire file content per specification]
