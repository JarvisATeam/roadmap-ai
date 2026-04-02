"""Data helpers backed by the ORM."""

from typing import Dict, List, Optional

from roadmap.storage.db import get_session
from roadmap.storage.models import Milestone, Mission, Step


def _mission_code(mission: Mission) -> str:
    return mission.mission_code or f"M-{mission.id[:8]}"


def load_missions() -> List[Dict]:
    """Return missions with revenue data."""
    session = get_session()
    try:
        missions = session.query(Mission).all()
        return [
            {
                "id": mission.id,
                "mission_code": _mission_code(mission),
                "title": mission.title,
                "status": mission.status,
                "revenue": mission.revenue or 0,
            }
            for mission in missions
        ]
    finally:
        session.close()


def load_tasks() -> List[Dict]:
    """Return steps enriched with mission data."""
    session = get_session()
    try:
        steps = (
            session.query(Step)
            .join(Milestone)
            .join(Mission)
            .all()
        )
        result: List[Dict] = []
        for step in steps:
            mission = step.milestone.mission
            result.append(
                {
                    "id": step.id,
                    "name": step.description,
                    "mission_id": mission.id,
                    "mission_code": _mission_code(mission),
                    "mission_name": mission.title,
                    "energy": step.energy or 3,
                    "priority": step.priority or 3,
                    "status": step.status,
                    "deadline": step.due_date.isoformat() if step.due_date else None,
                    "completed": step.status == "done",
                }
            )
        return result
    finally:
        session.close()


def find_mission(identifier: str) -> Optional[Dict]:
    session = get_session()
    try:
        mission = (
            session.query(Mission)
            .filter(
                (Mission.mission_code == identifier)
                | (Mission.id.like(f"{identifier}%"))
            )
            .first()
        )
        if not mission:
            return None
        return {
            "id": mission.id,
            "mission_code": _mission_code(mission),
            "title": mission.title,
            "revenue": mission.revenue or 0,
        }
    finally:
        session.close()


def find_task(identifier: str) -> Optional[Dict]:
    session = get_session()
    try:
        step = (
            session.query(Step)
            .filter(Step.id.like(f"{identifier}%"))
            .first()
        )
        if not step:
            return None
        mission = step.milestone.mission
        return {
            "id": step.id,
            "name": step.description,
            "mission_id": mission.id,
            "mission_code": _mission_code(mission),
            "mission_name": mission.title,
            "energy": step.energy or 3,
            "priority": step.priority or 3,
            "status": step.status,
        }
    finally:
        session.close()
