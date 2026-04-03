"""Tests for list-steps command."""

import json
from datetime import datetime, timedelta, timezone

import pytest
from click.testing import CliRunner

from roadmap.cli.main import cli


@pytest.fixture
def runner(tmp_path, monkeypatch):
    db_path = tmp_path / "roadmap-list-steps.db"
    monkeypatch.setenv("ROADMAP_DB_PATH", str(db_path))
    runner = CliRunner()
    init_result = runner.invoke(cli, ["init"])
    assert init_result.exit_code == 0
    return runner


def _create_mission(runner):
    result = runner.invoke(cli, ["add-mission", "List Steps Mission", "--revenue", "1000"])
    assert result.exit_code == 0
    missions_json = runner.invoke(cli, ["list-missions", "--json"])
    data = json.loads(missions_json.output)
    mission = data["missions"][0]
    return mission["id"], mission["mission_code"]


def test_list_steps_json_output(runner):
    mission_id, mission_code = _create_mission(runner)
    due_date = (datetime.now(timezone.utc) + timedelta(days=5)).strftime("%Y-%m-%d")
    runner.invoke(cli, ["add-step", mission_code, "Step A", "--energy", "4"])
    runner.invoke(cli, ["add-step", mission_code, "Step B", "--energy", "2", "--due", due_date])

    result = runner.invoke(cli, ["list-steps", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["count"] == 2
    titles = {s["title"] for s in payload["steps"]}
    assert {"Step A", "Step B"} == titles
    due_entry = next(s for s in payload["steps"] if s["title"] == "Step B")
    assert due_entry["due_date"].startswith(due_date)


def test_list_steps_filters_by_short_mission_id(runner):
    mission_id, mission_code = _create_mission(runner)
    runner.invoke(cli, ["add-step", mission_code, "Only Step"])

    result = runner.invoke(cli, ["list-steps", "--mission", mission_id[:4], "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["count"] == 1
    assert payload["steps"][0]["title"] == "Only Step"
    assert payload["filter_mission"] == mission_id
