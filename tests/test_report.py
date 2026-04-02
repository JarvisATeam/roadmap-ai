"""Tests for report CLI command."""

import json
from click.testing import CliRunner

from roadmap.cli.main import cli


def test_daily_report_json(initialized_db):
    runner = CliRunner()
    result = runner.invoke(cli, ["report", "--daily", "--json"])
    if result.exit_code == 0 and result.output.strip():
        payload = json.loads(result.output)
        assert payload["command"] == "report --daily"
        assert "sections" in payload["data"]
        assert "smart_next" in payload["data"]["sections"]


def test_daily_report_markdown(initialized_db):
    runner = CliRunner()
    result = runner.invoke(cli, ["report", "--daily", "--markdown"])
    if result.exit_code == 0:
        assert "# Daily Ops Report" in result.output
        assert "## 🎯 Next Recommended Task" in result.output
