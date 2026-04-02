"""Tests for revenue helpers."""
from roadmap.core import revenue


def test_task_value_missing(monkeypatch):
    monkeypatch.setattr("roadmap.core.revenue.data.find_task", lambda task_id: None)
    result = revenue.task_value("missing")
    assert "error" in result


def test_task_value_base(monkeypatch):
    task = {"id": "t1", "name": "Task", "mission_id": "m1"}
    mission = {"id": "m1", "name": "Mission", "revenue": 1000}
    monkeypatch.setattr("roadmap.core.revenue.data.find_task", lambda task_id: task)
    monkeypatch.setattr("roadmap.core.revenue.data.find_mission", lambda mission_id: mission)
    monkeypatch.setattr(
        "roadmap.core.revenue.data.load_tasks",
        lambda: [{"mission_id": "m1", "completed": False}, {"mission_id": "m1", "completed": True}],
    )
    monkeypatch.setattr("roadmap.core.revenue.blocks.get_blocked_by", lambda task_id: [])
    result = revenue.task_value("t1")
    assert result["base_value"] == 500.0
    assert result["total_value"] >= 500.0


def test_mission_forecast_not_found(monkeypatch):
    monkeypatch.setattr("roadmap.core.revenue.data.find_mission", lambda mission_id: None)
    result = revenue.mission_forecast("missing")
    assert "error" in result
