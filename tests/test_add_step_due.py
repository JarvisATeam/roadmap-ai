"""Integration tests for add-step CLI."""

from datetime import date

from click.testing import CliRunner

from roadmap.cli.main import cli
from roadmap.storage.db import get_session
from roadmap.storage.models import Mission, Step


def _get_first_mission():
    session = get_session()
    try:
        return session.query(Mission).first()
    finally:
        session.close()


def _get_first_step():
    session = get_session()
    try:
        return session.query(Step).first()
    finally:
        session.close()


def test_add_step_accepts_due_date(monkeypatch, tmp_path):
    db_path = tmp_path / "roadmap.db"
    monkeypatch.setenv("ROADMAP_DB_PATH", str(db_path))
    runner = CliRunner()

    # Initialize DB and seed mission
    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 0
    result = runner.invoke(cli, ["add-mission", "Deadline Mission", "--revenue", "1000"])
    assert result.exit_code == 0

    mission = _get_first_mission()
    assert mission is not None
    mission_code = mission.mission_code or mission.id[:8]

    due_str = "2030-01-05"
    result = runner.invoke(
        cli,
        ["add-step", mission_code, "Task with deadline", "--due", due_str],
    )
    assert result.exit_code == 0

    step = _get_first_step()
    assert step is not None
    assert step.due_date is not None
    assert step.due_date.date() == date(2030, 1, 5)
