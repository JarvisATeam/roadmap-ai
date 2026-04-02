"""Decision logging utilities."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from roadmap.storage import db


def get_decisions_path() -> Path:
    """Return filesystem path for decisions store."""
    return Path.home() / ".roadmap" / "decisions.json"


def load_decisions() -> List[dict]:
    """Load decisions from disk."""
    path = get_decisions_path()
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return []


def save_decisions(decisions: List[dict]) -> None:
    """Persist decisions to disk."""
    path = get_decisions_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(decisions, indent=2))


def generate_decision_id() -> str:
    """Generate monotonically increasing decision identifier."""
    existing = load_decisions()
    highest = 0
    for decision in existing:
        identifier = decision.get("id", "")
        if identifier.startswith("dec_"):
            try:
                highest = max(highest, int(identifier.split("_", 1)[1]))
            except (ValueError, IndexError):
                continue
    return f"dec_{highest + 1:03d}"


def _match_step(session, identifier: str):
    from roadmap.storage.models import Step

    return (
        session.query(Step)
        .filter(Step.id.like(f"{identifier}%"))
        .first()
    )


def _match_mission(session, identifier: str):
    from roadmap.storage.models import Mission

    return (
        session.query(Mission)
        .filter(Mission.id.like(f"{identifier}%"))
        .first()
    )


def get_step_context(step_id: str) -> dict:
    """Collect context details for a task or mission."""
    context = {
        "step_id": step_id,
        "step_type": "unknown",
    }
    try:
        db.init_db()
    except Exception:
        # Database might already be initialized; ignore errors here.
        pass
    try:
        session = db.get_session()
    except Exception:
        return context

    try:
        step = _match_step(session, step_id)
        if step:
            mission = step.milestone.mission if step.milestone else None
            context.update(
                {
                    "step_type": "task",
                    "mission_id": mission.id if mission else None,
                    "mission_name": mission.title if mission else None,
                    "blockers": [blocker.id for blocker in step.blockers if blocker.status != "resolved"],
                    "blocked_by_count": sum(1 for blocker in step.blockers if blocker.status != "resolved"),
                    "energy": getattr(step, "priority", None),
                    "revenue_weight": getattr(mission, "revenue", None) if mission else None,
                }
            )
            return context
        mission = _match_mission(session, step_id)
        if mission:
            tasks = []
            for milestone in mission.milestones:
                tasks.extend(milestone.steps)
            context.update(
                {
                    "step_type": "mission",
                    "mission_id": mission.id,
                    "mission_name": mission.title,
                    "task_count": len(tasks),
                    "revenue": getattr(mission, "revenue", None),
                }
            )
    finally:
        session.close()
    return context


def add_decision(step_id: str, decision_text: str) -> dict:
    """Record a new decision."""
    decisions = load_decisions()
    decision = {
        "id": generate_decision_id(),
        "step_id": step_id,
        "decision": decision_text,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "context": get_step_context(step_id),
    }
    decisions.append(decision)
    save_decisions(decisions)
    return decision


def get_decision(decision_id: str) -> Optional[dict]:
    """Retrieve single decision by identifier."""
    decisions = load_decisions()
    return next((item for item in decisions if item.get("id") == decision_id), None)


def list_decisions(step_id: Optional[str] = None) -> List[dict]:
    """Return collection of decisions, optionally filtered by step."""
    decisions = load_decisions()
    if step_id:
        return [item for item in decisions if item.get("step_id") == step_id]
    return decisions
