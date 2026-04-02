"""Shared data helpers for ORION modules."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from roadmap.storage import db
from roadmap.storage import models


def _safe_iso(value: Optional[datetime]) -> Optional[str]:
    if not value:
        return None
    return value.isoformat().replace("+00:00", "Z")


def _energy_from_priority(priority: Optional[int]) -> int:
    base = priority if priority is not None else 3
    return max(1, min(10, base))


def load_tasks() -> List[Dict]:
    """Convert Step rows into dictionaries consumable by ORION modules."""
    try:
        db.init_db()
    except Exception:
        pass
    try:
        session = db.get_session()
    except Exception:
        return []
    try:
        steps = session.query(models.Step).all()
        tasks: List[Dict] = []
        for step in steps:
            milestone = step.milestone
            mission = milestone.mission if milestone else None
            tasks.append(
                {
                    "id": step.id,
                    "name": step.description,
                    "mission_id": mission.id if mission else None,
                    "mission_name": mission.title if mission else None,
                    "status": step.status,
                    "priority": step.priority or 0,
                    "energy": _energy_from_priority(step.priority),
                    "deadline": _safe_iso(step.due_date),
                    "completed": step.status == "done",
                    "completed_at": _safe_iso(step.completed_at),
                    "blocked": step.status == "blocked",
                    "blocker_ids": [b.id for b in step.blockers if b.status != "resolved"],
                    "created_at": _safe_iso(step.created_at),
                }
            )
        return tasks
    except Exception:
        return []
    finally:
        try:
            session.close()
        except Exception:
            pass


def load_missions() -> List[Dict]:
    """Return missions as dictionaries."""
    try:
        db.init_db()
    except Exception:
        pass
    try:
        session = db.get_session()
    except Exception:
        return []
    try:
        missions: List[Dict] = []
        for mission in session.query(models.Mission).all():
            task_ids = []
            for milestone in mission.milestones:
                task_ids.extend(step.id for step in milestone.steps)
            missions.append(
                {
                    "id": mission.id,
                    "name": mission.title,
                    "status": mission.status,
                    "revenue": getattr(mission, "revenue", 0) or 0,
                    "task_ids": task_ids,
                }
            )
        return missions
    except Exception:
        return []
    finally:
        try:
            session.close()
        except Exception:
            pass


def find_task(identifier: str) -> Optional[Dict]:
    """Return matching task dictionary using prefix matching."""
    for task in load_tasks():
        if task["id"] == identifier or task["id"].startswith(identifier):
            return task
    return None


def find_mission(identifier: str) -> Optional[Dict]:
    """Return matching mission dictionary using prefix matching."""
    for mission in load_missions():
        if mission["id"] == identifier or mission["id"].startswith(identifier):
            return mission
    return None
