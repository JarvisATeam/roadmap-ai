"""Tests for decision logging."""
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from roadmap.cli.main import cli
from roadmap.core.decisions import (
    add_decision,
    get_decision,
    list_decisions,
    get_decisions_path,
)


@pytest.fixture(autouse=True)
def clean_decisions(tmp_path, monkeypatch):
    """Redirect decisions file to a temporary directory."""
    decisions_path = tmp_path / ".roadmap" / "decisions.json"

    def _path_override() -> Path:
        return decisions_path

    monkeypatch.setattr("roadmap.core.decisions.get_decisions_path", _path_override)
    yield decisions_path


class TestDecisionCore:
    """Unit tests for decision helpers."""

    def test_add_decision_increments_ids(self):
        decision = add_decision("task_001", "First decision")
        assert decision["id"] == "dec_001"
        assert decision["step_id"] == "task_001"

        second = add_decision("task_002", "Second decision")
        assert second["id"] == "dec_002"

    def test_get_decision(self):
        add_decision("task_001", "Stored decision")
        result = get_decision("dec_001")
        assert result is not None
        assert result["decision"] == "Stored decision"

    def test_get_decision_missing(self):
        assert get_decision("dec_999") is None

    def test_list_decisions_filter(self):
        add_decision("task_001", "Task decision")
        add_decision("task_002", "Another decision")
        scoped = list_decisions("task_001")
        assert len(scoped) == 1
        assert scoped[0]["step_id"] == "task_001"


class TestDecisionCLI:
    """CLI command coverage."""

    def test_decide_command_text_output(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["decide", "task_001", "Test decision"])
        assert result.exit_code == 0
        assert "Decision logged" in result.output
        assert "dec_001" in result.output

    def test_decide_command_json_output(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["decide", "task_001", "Test decision", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["id"] == "dec_001"

    def test_list_decisions_command(self):
        runner = CliRunner()
        runner.invoke(cli, ["decide", "task_001", "First"])
        runner.invoke(cli, ["decide", "task_002", "Second"])
        result = runner.invoke(cli, ["list-decisions"])
        assert result.exit_code == 0
        assert "dec_001" in result.output
        assert "dec_002" in result.output

    def test_list_decisions_empty(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["list-decisions"])
        assert result.exit_code == 0
        assert "No decisions logged" in result.output

    def test_show_decision_command(self):
        runner = CliRunner()
        runner.invoke(cli, ["decide", "task_001", "Important decision"])
        result = runner.invoke(cli, ["show-decision", "dec_001"])
        assert result.exit_code == 0
        assert "Important decision" in result.output

    def test_show_decision_not_found(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["show-decision", "dec_999"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()
