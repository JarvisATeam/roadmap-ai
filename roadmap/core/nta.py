"""Next Task Algorithm (NTA) scoring."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from roadmap.core import blocks, data


def calculate_revenue_weight(task: Dict, missions: List[Dict]) -> float:
    """Return relative revenue weight (0.0 - 1.0)."""
    mission = next((m for m in missions if m["id"] == task.get("mission_id")), None)
    if not mission:
        return 0.5
    revenues = [m.get("revenue", 0) for m in missions]
    max_revenue = max(revenues) if revenues else 0
    if not max_revenue:
        return 0.5
    return mission.get("revenue", 0) / max_revenue


def calculate_urgency(task: Dict) -> float:
    """Calculate urgency multiplier."""
    deadline = task.get("deadline")
    if not deadline:
        return 0.8
    try:
        deadline_dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        now = datetime.now(deadline_dt.tzinfo) if deadline_dt.tzinfo else datetime.now()
        delta_days = (deadline_dt - now).days
    except (ValueError, TypeError):
        return 1.0
    if delta_days <= 0:
        return 2.0
    if delta_days <= 3:
        return 1.5
    if delta_days <= 7:
        return 1.2
    return 1.0


def calculate_energy_match(task: Dict, current_energy: int = 5) -> float:
    """Return energy match factor (0.5 - 1.0)."""
    task_energy = task.get("energy", 3)
    diff = abs(current_energy - task_energy)
    match = 1.0 - (diff * 0.1)
    return max(0.5, min(1.0, match))


def calculate_context_cost(task: Dict, last_task_id: Optional[str] = None) -> float:
    """Return context switching penalty."""
    if not last_task_id:
        return 0.0
    last_task = data.find_task(last_task_id)
    if not last_task:
        return 0.0
    cost = 0.0
    if last_task.get("mission_id") != task.get("mission_id"):
        cost += 0.2
    return min(0.3, cost)


def calculate_risk_penalty(task: Dict) -> float:
    """Return penalty based on blocker depth."""
    blocker_chain = blocks.get_blockers(task["id"])
    depth = len(blocker_chain)
    return min(0.5, depth * 0.1)


def score_task(
    task: Dict,
    missions: List[Dict],
    current_energy: int = 5,
    last_task_id: Optional[str] = None,
) -> Dict:
    """Return score payload for a task."""
    revenue = calculate_revenue_weight(task, missions)
    urgency = calculate_urgency(task)
    energy = calculate_energy_match(task, current_energy)
    context = calculate_context_cost(task, last_task_id)
    risk = calculate_risk_penalty(task)
    score = (revenue * urgency * energy) - context - risk
    return {
        "task_id": task["id"],
        "task_name": task["name"],
        "mission_id": task.get("mission_id"),
        "score": round(score, 3),
        "factors": {
            "revenue_weight": round(revenue, 3),
            "urgency": round(urgency, 3),
            "energy_match": round(energy, 3),
            "context_cost": round(context, 3),
            "risk_penalty": round(risk, 3),
        },
    }


def get_ranked_tasks(
    current_energy: int = 5,
    last_task_id: Optional[str] = None,
    include_blocked: bool = False,
) -> List[Dict]:
    """Return ranked list of available tasks."""
    tasks = data.load_tasks()
    missions = data.load_missions()
    ranked: List[Dict] = []

    for task in tasks:
        if task.get("completed"):
            continue
        blockers_list = blocks.get_blockers(task["id"])
        if blockers_list and not include_blocked:
            continue
        ranked.append(score_task(task, missions, current_energy, last_task_id))

    ranked.sort(key=lambda item: item["score"], reverse=True)
    for index, item in enumerate(ranked, start=1):
        item["rank"] = index
    return ranked


def smart_next(
    current_energy: int = 5,
    last_task_id: Optional[str] = None,
) -> Optional[Dict]:
    """Return the single highest-ranked task."""
    tasks = get_ranked_tasks(current_energy=current_energy, last_task_id=last_task_id)
    return tasks[0] if tasks else None
