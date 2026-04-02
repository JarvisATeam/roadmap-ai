"""Revenue and value calculations for ORION."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict

from roadmap.core import blocks, data
from roadmap.core import predictor


def is_on_critical_path(task: Dict) -> bool:
    """Return True when this task unblocks others."""
    return bool(blocks.get_blocked_by(task["id"]))


def count_tasks_blocked_by(task_id: str) -> int:
    """Return number of tasks this task unblocks."""
    return len(blocks.get_blocked_by(task_id))


def task_value(task_id: str) -> Dict:
    """Return value composition for a task."""
    task = data.find_task(task_id)
    if not task:
        return {"error": f"Task {task_id} not found"}
    mission = data.find_mission(task.get("mission_id")) if task.get("mission_id") else None
    mission_revenue = mission.get("revenue", 0) if mission else 0
    mission_tasks = [t for t in data.load_tasks() if t.get("mission_id") == task.get("mission_id")]
    task_count = len(mission_tasks) or 1
    base_value = mission_revenue / task_count if mission_revenue else 0
    critical_bonus = base_value * 0.5 if is_on_critical_path(task) else 0
    unblocks = count_tasks_blocked_by(task["id"])
    unblock_bonus = unblocks * (mission_revenue * 0.05)
    total_value = base_value + critical_bonus + unblock_bonus
    daily_cost = total_value * 0.02
    cascade_multiplier = 1.0 + (unblocks * 0.1)
    return {
        "task_id": task["id"],
        "task_name": task["name"],
        "mission_id": task.get("mission_id"),
        "mission_revenue": mission_revenue,
        "base_value": round(base_value, 2),
        "critical_path": is_on_critical_path(task),
        "critical_bonus": round(critical_bonus, 2),
        "unblocks_count": unblocks,
        "unblock_bonus": round(unblock_bonus, 2),
        "total_value": round(total_value, 2),
        "delay_cost_per_day": round(daily_cost, 2),
        "cascade_multiplier": round(cascade_multiplier, 2),
    }


def delay_cost(task_id: str, days: int = 1) -> Dict:
    """Return delay cost information."""
    value = task_value(task_id)
    if "error" in value:
        return value
    total_cost = value["delay_cost_per_day"] * days * value["cascade_multiplier"]
    return {
        "task_id": task_id,
        "days": days,
        "daily_cost": value["delay_cost_per_day"],
        "cascade_multiplier": value["cascade_multiplier"],
        "total_delay_cost": round(total_cost, 2),
    }


def mission_forecast(mission_id: str) -> Dict:
    """Return mission level forecast information."""
    mission = data.find_mission(mission_id)
    if not mission:
        return {"error": f"Mission {mission_id} not found"}
    tasks = [t for t in data.load_tasks() if t.get("mission_id") == mission["id"]]
    completed = [t for t in tasks if t.get("completed")]
    remaining = [t for t in tasks if not t.get("completed")]
    if completed:
        completion_times = []
        for task in completed:
            timestamp = task.get("completed_at")
            if timestamp:
                try:
                    completion_times.append(datetime.fromisoformat(timestamp.replace("Z", "+00:00")))
                except (ValueError, TypeError):
                    continue
        if completion_times:
            first_complete = min(completion_times)
            now = datetime.now(first_complete.tzinfo) if first_complete.tzinfo else datetime.now()
            days_elapsed = max(1, (now - first_complete).days)
            velocity = len(completed) / days_elapsed
        else:
            velocity = 1.0
    else:
        velocity = 1.0
    days_remaining = (len(remaining) / velocity) if velocity else float("inf")
    expected_completion = None
    if days_remaining != float("inf"):
        expected_completion = (datetime.now() + timedelta(days=days_remaining)).isoformat()
    failure_prob = predictor.mission_failure_probability(mission["id"])
    return {
        "mission_id": mission["id"],
        "mission_name": mission["name"],
        "revenue": mission.get("revenue", 0),
        "completion_probability": round(1.0 - failure_prob, 2),
        "expected_completion": expected_completion,
        "days_remaining": round(days_remaining, 1) if days_remaining != float("inf") else None,
        "velocity": round(velocity, 2),
        "tasks_completed": len(completed),
        "tasks_remaining": len(remaining),
        "tasks_total": len(tasks),
    }
