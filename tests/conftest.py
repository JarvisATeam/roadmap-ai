import os
import pytest

from roadmap.storage.db import init_db, get_session
from roadmap.storage.models import Mission, Milestone, Step


@pytest.fixture
def initialized_db(tmp_path, monkeypatch):
    db_path = tmp_path / "roadmap.db"
    monkeypatch.setenv("ROADMAP_DB_PATH", str(db_path))
    init_db()
    session = get_session()
    try:
        mission = Mission(title="Pilot Mission", revenue=3000, status="active")
        session.add(mission)
        session.flush()
        mission.mission_code = f"M-{mission.id[:8]}"
        milestone = Milestone(mission_id=mission.id, title="Backlog", order=1)
        session.add(milestone)
        session.flush()
        session.add_all(
            [
                Step(milestone_id=milestone.id, description="Task A", energy=3),
                Step(milestone_id=milestone.id, description="Task B", energy=5),
            ]
        )
        session.commit()
    finally:
        session.close()
    return str(db_path)
