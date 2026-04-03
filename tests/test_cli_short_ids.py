"""CLI coverage for short ID resolver."""

import json

import pytest
from click.testing import CliRunner

from roadmap.cli.main import cli


@pytest.fixture
def resolver_state():
    return {
        "missions": [
            {
                "id": "mission-9999-alpha",
                "steps": [
                    {"id": "task-alpha-1111"},
                    {"id": "task-beta-2222"},
                ],
            }
        ]
    }


class TestValueCommandResolver:
    def test_value_command_short_id(self, monkeypatch, resolver_state):
        monkeypatch.setattr(
            "roadmap.cli.smart_commands._load_state_for_cli",
            lambda: resolver_state,
        )
        captured = {}

        def fake_task_value(step_id):
            captured["id"] = step_id
            return {
                "task_id": step_id,
                "task_name": "Alpha",
                "mission_id": "mission-9999-alpha",
                "mission_revenue": 1000,
                "base_value": 100,
                "critical_path": False,
                "critical_bonus": 0,
                "unblocks_count": 0,
                "unblock_bonus": 0,
                "total_value": 100,
                "delay_cost_per_day": 5,
                "cascade_multiplier": 1.0,
            }

        monkeypatch.setattr("roadmap.cli.smart_commands.revenue.task_value", fake_task_value)
        runner = CliRunner()
        result = runner.invoke(cli, ["value", "task-alpha"])
        assert result.exit_code == 0
        assert captured["id"] == "task-alpha-1111"
        assert "task-alpha-1111" in result.output


class TestForecastCommandResolver:
    def test_forecast_command_short_id_json(self, monkeypatch, resolver_state):
        monkeypatch.setattr(
            "roadmap.cli.smart_commands._load_state_for_cli",
            lambda: resolver_state,
        )
        captured = {}

        def fake_forecast(mission_id):
            captured["id"] = mission_id
            return {
                "mission_id": mission_id,
                "mission_name": "Alpha Mission",
                "revenue": 1000,
                "completion_probability": 0.9,
                "expected_completion": "2024-04-01",
                "days_remaining": 5,
                "velocity": 1.2,
                "tasks_completed": 3,
                "tasks_remaining": 2,
                "tasks_total": 5,
            }

        monkeypatch.setattr("roadmap.cli.smart_commands.revenue.mission_forecast", fake_forecast)
        runner = CliRunner()
        result = runner.invoke(cli, ["forecast", "mission-9999", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert captured["id"] == "mission-9999-alpha"
        assert payload["metadata"]["filter_mission"] == "mission-9999-alpha"
