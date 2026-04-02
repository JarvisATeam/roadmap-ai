"""Tests for risk predictor."""
from roadmap.core import predictor


def test_blocker_risk(monkeypatch):
    monkeypatch.setattr("roadmap.core.predictor.blocks.get_blockers", lambda task_id: ["b1", "b2"])
    risk = predictor.blocker_risk("task_001")
    assert 0 < risk <= 1.0


def test_mission_failure_probability(monkeypatch):
    monkeypatch.setattr(
        "roadmap.core.predictor.data.load_tasks",
        lambda: [
            {"id": "t1", "mission_id": "m1", "completed": False, "deadline": None},
            {"id": "t2", "mission_id": "m1", "completed": False, "deadline": None},
        ],
    )
    monkeypatch.setattr("roadmap.core.predictor.blocks.get_blockers", lambda task_id: [])
    prob = predictor.mission_failure_probability("m1")
    assert prob == 0.0


def test_get_risk_summary_structure(monkeypatch):
    monkeypatch.setattr(
        "roadmap.core.predictor.data.load_missions",
        lambda: [{"id": "m1", "name": "Mission", "revenue": 0}],
    )
    monkeypatch.setattr(
        "roadmap.core.predictor.data.load_tasks",
        lambda: [{"id": "t1", "mission_id": "m1", "completed": False, "deadline": None}],
    )
    monkeypatch.setattr("roadmap.core.predictor.blocks.get_blockers", lambda task_id: [])
    summary = predictor.get_risk_summary()
    assert "warnings" in summary
    assert "blocked_tasks" in summary
