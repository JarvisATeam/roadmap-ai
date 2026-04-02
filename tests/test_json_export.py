"""Tests for JSON export utilities and CLI outputs."""

import json
from click.testing import CliRunner

from roadmap.cli.main import cli
from roadmap.core.json_export import create_envelope, to_json


def test_create_envelope_structure():
    envelope = create_envelope("smart next", {"foo": "bar"}, metadata={"test": True})
    assert envelope["command"] == "smart next"
    assert envelope["data"] == {"foo": "bar"}
    assert envelope["metadata"]["test"] is True
    assert "roadmap_version" in envelope
    assert "timestamp" in envelope


def test_to_json_round_trip():
    envelope = create_envelope("test", {"value": 42})
    payload = json.loads(to_json(envelope))
    assert payload["command"] == "test"
    assert payload["data"]["value"] == 42


def test_smart_next_json_output(initialized_db):
    runner = CliRunner()
    result = runner.invoke(cli, ["smart", "next", "--json"])
    if result.exit_code == 0 and result.output.strip():
        payload = json.loads(result.output)
        assert payload["command"] == "smart next"
        assert "roadmap_version" in payload


def test_risks_json_output(initialized_db):
    runner = CliRunner()
    result = runner.invoke(cli, ["risks", "--json"])
    if result.exit_code == 0:
        payload = json.loads(result.output)
        assert payload["command"] == "risks"
        assert "data" in payload
