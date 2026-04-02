"""Tests for Next Task Algorithm."""
import pytest

from roadmap.core import nta


@pytest.fixture
def missions():
    return [
        {"id": "m1", "revenue": 5000},
        {"id": "m2", "revenue": 2500},
    ]


@pytest.fixture
def tasks():
    return [
        {
            "id": "t1",
            "name": "Build scoring",
            "mission_id": "m1",
            "energy": 5,
            "deadline": "2099-01-10T00:00:00Z",
            "completed": False,
        },
        {
            "id": "t2",
            "name": "Write docs",
            "mission_id": "m2",
            "energy": 3,
            "deadline": "2099-01-15T00:00:00Z",
            "completed": False,
        },
    ]


class TestScoringHelpers:
    def test_revenue_weight(self, missions):
        task = {"mission_id": "m1"}
        assert nta.calculate_revenue_weight(task, missions) == 1.0

    def test_urgency_without_deadline(self):
        assert nta.calculate_urgency({}) == 0.8

    def test_energy_match(self):
        task = {"energy": 5}
        assert nta.calculate_energy_match(task, current_energy=5) == 1.0


class TestRanking:
    def test_score_task_contains_expected_fields(self, missions):
        task = {"id": "t1", "name": "Task", "mission_id": "m1", "energy": 3}
        result = nta.score_task(task, missions)
        assert result["task_id"] == "t1"
        assert "score" in result
        assert "factors" in result

    def test_get_ranked_tasks(self, monkeypatch, tasks, missions):
        monkeypatch.setattr("roadmap.core.nta.data.load_tasks", lambda: tasks)
        monkeypatch.setattr("roadmap.core.nta.data.load_missions", lambda: missions)
        monkeypatch.setattr("roadmap.core.nta.blocks.get_blockers", lambda _task_id: [])
        ranked = nta.get_ranked_tasks()
        assert len(ranked) == 2
        assert ranked[0]["rank"] == 1

    def test_smart_next_returns_best_task(self, monkeypatch, tasks, missions):
        monkeypatch.setattr("roadmap.core.nta.data.load_tasks", lambda: tasks)
        monkeypatch.setattr("roadmap.core.nta.data.load_missions", lambda: missions)
        monkeypatch.setattr("roadmap.core.nta.blocks.get_blockers", lambda _task_id: [])
        result = nta.smart_next()
        assert result is not None
        assert result["task_id"] in {"t1", "t2"}
