"""Helpers for blocker relationships used by ORION."""
from __future__ import annotations

from typing import List

from roadmap.storage import db, models


def _match_step(session, identifier: str):
    return (
        session.query(models.Step)
        .filter(models.Step.id.like(f"{identifier}%"))
        .first()
    )


def get_blockers(step_id: str) -> List[str]:
    """Return list of unresolved blocker identifiers for a task."""
    try:
        db.init_db()
    except Exception:
        pass
    try:
        session = db.get_session()
    except Exception:
        return []
    try:
        step = _match_step(session, step_id)
        if not step:
            return []
        return [blocker.id for blocker in step.blockers if blocker.status != "resolved"]
    except Exception:
        return []
    finally:
        try:
            session.close()
        except Exception:
            pass


def get_blocked_by(step_id: str) -> List[str]:
    """Return identifiers of tasks that depend on the given step."""
    # Dependency relationships between tasks are not explicitly modelled yet.
    # Return an empty list so downstream calculations can handle gracefully.
    return []
