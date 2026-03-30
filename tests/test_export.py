"""Tests for ExportEngine."""
import json
import tempfile
from pathlib import Path
from datetime import date

import pytest

from roadmap.core.export import ExportEngine


@pytest.fixture
def sample_plan():
    return {
        "plan_id": "test-plan-001",
        "project": "TestProject",
        "generated": "2025-01-15",
        "milestones": [
            {
                "id": "M1",
                "title": "MVP Release",
                "target_date": "2025-03-01",
                "status": "on_track",
                "tasks": [
                    {"id": "T1", "title": "Build API", "owner": "alice", "status": "done"},
                    {"id": "T2", "title": "Build UI", "owner": "bob", "status": "in_progress"}
                ]
            },
            {
                "id": "M2",
                "title": "Beta Launch",
                "target_date": "2025-06-01",
                "status": "at_risk",
                "tasks": [
                    {"id": "T3", "title": "Testing", "owner": "carol", "status": "not_started"}
                ]
            }
        ]
    }


@pytest.fixture
def engine():
    return ExportEngine()


class TestMarkdownExport:
    def test_export_markdown_returns_string(self, engine, sample_plan):
        result = engine.to_markdown(sample_plan)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_export_markdown_contains_project_name(self, engine, sample_plan):
        result = engine.to_markdown(sample_plan)
        assert "TestProject" in result

    def test_export_markdown_contains_milestones(self, engine, sample_plan):
        result = engine.to_markdown(sample_plan)
        assert "MVP Release" in result
        assert "Beta Launch" in result

    def test_export_markdown_contains_tasks(self, engine, sample_plan):
        result = engine.to_markdown(sample_plan)
        assert "Build API" in result
        assert "Build UI" in result

    def test_export_markdown_contains_status(self, engine, sample_plan):
        result = engine.to_markdown(sample_plan)
        assert "on_track" in result or "✅" in result or "On Track" in result

    def test_export_markdown_to_file(self, engine, sample_plan):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "plan.md"
            engine.to_markdown(sample_plan, output_path=filepath)
            assert filepath.exists()
            content = filepath.read_text()
            assert "TestProject" in content


class TestJSONExport:
    def test_export_json_returns_string(self, engine, sample_plan):
        result = engine.to_json(sample_plan)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["plan_id"] == "test-plan-001"

    def test_export_json_roundtrip(self, engine, sample_plan):
        result = engine.to_json(sample_plan)
        parsed = json.loads(result)
        assert parsed == sample_plan

    def test_export_json_to_file(self, engine, sample_plan):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "plan.json"
            engine.to_json(sample_plan, output_path=filepath)
            assert filepath.exists()
            parsed = json.loads(filepath.read_text())
            assert parsed["project"] == "TestProject"

    def test_export_json_pretty(self, engine, sample_plan):
        result = engine.to_json(sample_plan, pretty=True)
        assert "\n" in result
        assert "  " in result


class TestCSVExport:
    def test_export_csv_returns_string(self, engine, sample_plan):
        result = engine.to_csv(sample_plan)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_export_csv_has_header(self, engine, sample_plan):
        result = engine.to_csv(sample_plan)
        first_line = result.strip().split("\n")[0]
        assert "milestone" in first_line.lower() or "task" in first_line.lower()

    def test_export_csv_has_data_rows(self, engine, sample_plan):
        result = engine.to_csv(sample_plan)
        lines = result.strip().split("\n")
        assert len(lines) >= 4  # header + 3 tasks

    def test_export_csv_to_file(self, engine, sample_plan):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "plan.csv"
            engine.to_csv(sample_plan, output_path=filepath)
            assert filepath.exists()
            content = filepath.read_text()
            lines = content.strip().split("\n")
            assert len(lines) >= 4


class TestSummaryExport:
    def test_summary_contains_counts(self, engine, sample_plan):
        result = engine.summary(sample_plan)
        assert isinstance(result, dict)
        assert result["total_milestones"] == 2
        assert result["total_tasks"] == 3

    def test_summary_contains_status_breakdown(self, engine, sample_plan):
        result = engine.summary(sample_plan)
        assert "task_status" in result
        assert result["task_status"]["done"] == 1
        assert result["task_status"]["in_progress"] == 1
        assert result["task_status"]["not_started"] == 1


class TestEdgeCases:
    def test_empty_plan(self, engine):
        empty = {"plan_id": "empty", "project": "Empty", "milestones": []}
        md = engine.to_markdown(empty)
        assert "Empty" in md
        csv = engine.to_csv(empty)
        assert isinstance(csv, str)

    def test_milestone_without_tasks(self, engine):
        plan = {
            "plan_id": "no-tasks",
            "project": "NoTasks",
            "milestones": [
                {"id": "M1", "title": "Solo", "target_date": "2025-01-01", "status": "on_track", "tasks": []}
            ]
        }
        result = engine.to_markdown(plan)
        assert "Solo" in result

    def test_missing_optional_fields(self, engine):
        plan = {
            "plan_id": "minimal",
            "project": "Minimal",
            "milestones": [
                {"id": "M1", "title": "Basic", "tasks": [
                    {"id": "T1", "title": "Task1"}
                ]}
            ]
        }
        result = engine.to_markdown(plan)
        assert "Basic" in result
