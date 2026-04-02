"""Risk prediction helpers for ORION."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from roadmap.core import blocks, data


def get_blocker_chain(task_id: str, max_depth: int = 10) -> List[str]:
    """Return blocker chain for a task."""
    chain = []
    queue = blocks.get_blockers(task_id)
    checked = set()
    while queue and len(chain) < max_depth:
        current = queue.pop(0)
        if current in checked:
            continue
        checked.add(current)
        chain.append(current)
        queue.extend(blocks.get_blockers(current))
    return chain


def blocker_risk(task_id: str) -> float:
    """Calculate blocker risk based on chain depth."""
    chain = get_blocker_chain(task_id)
    unresolved = len(chain)
    risk = (len(chain) * 0.15) + (unresolved * 0.25)
    return min(1.0, risk)


def is_overdue(task: Dict) -> bool:
    """Return True when task deadline passed."""
    deadline = task.get("deadline")
    if not deadline:
        return False
    try:
        deadline_dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        now = datetime.now(deadline_dt.tzinfo) if deadline_dt.tzinfo else datetime.now()
        return deadline_dt < now
    except (ValueError, TypeError):
        return False


def mission_failure_probability(mission_id: str) -> float:
    """Estimate failure probability for a mission."""
    tasks = [t for t in data.load_tasks() if t.get("mission_id") == mission_id and not t.get("completed")]
    if not tasks:
        return 0.0
    blocked = sum(1 for task in tasks if blocks.get_blockers(task["id"]))
    overdue = sum(1 for task in tasks if is_overdue(task))
    total = len(tasks)
    probability = (blocked / total) * 0.4 + (overdue / total) * 0.6
    return min(1.0, probability)


def get_warnings(mission_id: Optional[str] = None) -> List[Dict]:
    """Return collection of warning dicts."""
    warnings: List[Dict] = []
    missions = data.load_missions()
    if mission_id:
        missions = [m for m in missions if m["id"] == mission_id or m["id"].startswith(mission_id)]
    for mission in missions:
        prob = mission_failure_probability(mission["id"])
        if prob > 0.5:
            warnings.append(
                {
                    "type": "high_failure_risk",
                    "mission_id": mission["id"],
                    "mission_name": mission["name"],
                    "message": f"Mission has {prob * 100:.0f}% failure probability",
                    "severity": "critical",
                    "probability": round(prob, 2),
                }
            )
        elif prob > 0.3:
            warnings.append(
                {
                    "type": "elevated_risk",
                    "mission_id": mission["id"],
                    "mission_name": mission["name"],
                    "message": f"Mission has elevated risk ({prob * 100:.0f}%)",
                    "severity": "warning",
                    "probability": round(prob, 2),
                }
            )
        for task in [t for t in data.load_tasks() if t.get("mission_id") == mission["id"]]:
            risk = blocker_risk(task["id"])
            if risk > 0.7:
                warnings.append(
                    {
                        "type": "blocker_cascade",
                        "mission_id": mission["id"],
                        "task_id": task["id"],
                        "task_name": task["name"],
                        "message": "Deep blocker chain detected",
                        "severity": "warning",
                        "risk": round(risk, 2),
                    }
                )
    return warnings


def get_risk_summary(mission_id: Optional[str] = None) -> Dict:
    """Return aggregated risk summary."""
    missions = data.load_missions()
    tasks = data.load_tasks()
    if mission_id:
        missions = [m for m in missions if m["id"] == mission_id or m["id"].startswith(mission_id)]
        tasks = [t for t in tasks if t.get("mission_id") == mission_id or t.get("mission_id", "").startswith(mission_id)]
    blocked_tasks = sum(1 for task in tasks if blocks.get_blockers(task["id"]))
    overdue_tasks = sum(1 for task in tasks if is_overdue(task))
    warnings = get_warnings(mission_id=mission_id)
    return {
        "mission_id": mission_id,
        "missions_analyzed": len(missions),
        "warnings": warnings,
        "blocked_tasks": blocked_tasks,
        "overdue_tasks": overdue_tasks,
        "total_incomplete": len([t for t in tasks if not t.get("completed")]),
        "critical_warnings": len([w for w in warnings if w["severity"] == "critical"]),
        "summary_warnings": len([w for w in warnings if w["severity"] == "warning"]),
    }
