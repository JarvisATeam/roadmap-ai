#!/usr/bin/env python3
"""Test agent orchestration schemas"""
import json
import jsonschema
from pathlib import Path

SCHEMAS_DIR = Path(__file__).parent / "schemas"

def test_agent_task_schema():
    schema = json.loads((SCHEMAS_DIR / "agent_task.json").read_text())
    
    # Valid task
    valid_task = {
        "task_id": "task-12345678",
        "agent_role": "CODEX",
        "verb": "execute",
        "status": "pending",
        "created_at": "2026-04-03T20:00:00Z"
    }
    jsonschema.validate(valid_task, schema)
    print("✓ agent_task.json: valid task accepted")
    
    # Invalid: unknown status
    try:
        invalid_task = valid_task.copy()
        invalid_task["status"] = "unknown"
        jsonschema.validate(invalid_task, schema)
        assert False, "Should have failed"
    except jsonschema.ValidationError:
        print("✓ agent_task.json: invalid status rejected")

def test_agent_result_schema():
    schema = json.loads((SCHEMAS_DIR / "agent_result.json").read_text())
    
    valid_result = {
        "task_id": "task-12345678",
        "agent_role": "CODEX",
        "status": "done",
        "timestamp": "2026-04-03T20:05:00Z",
        "changed_files": ["main.py"],
        "tests_passed": True,
        "commit_hash": "abc1234"
    }
    jsonschema.validate(valid_result, schema)
    print("✓ agent_result.json: valid result accepted")

def test_agent_decision_schema():
    schema = json.loads((SCHEMAS_DIR / "agent_decision.json").read_text())
    
    valid_decision = {
        "task_id": "task-12345678",
        "decision": "approved",
        "decided_by": "AVA",
        "timestamp": "2026-04-03T20:03:00Z",
        "confidence": 0.95
    }
    jsonschema.validate(valid_decision, schema)
    print("✓ agent_decision.json: valid decision accepted")

def test_agent_handoff_schema():
    schema = json.loads((SCHEMAS_DIR / "agent_handoff.json").read_text())
    
    valid_handoff = {
        "task_id": "task-12345678",
        "from_agent": "GINIE",
        "to_agent": "AVA",
        "timestamp": "2026-04-03T20:01:00Z",
        "acceptance_required": True
    }
    jsonschema.validate(valid_handoff, schema)
    print("✓ agent_handoff.json: valid handoff accepted")

if __name__ == "__main__":
    test_agent_task_schema()
    test_agent_result_schema()
    test_agent_decision_schema()
    test_agent_handoff_schema()
    print("\n✅ All schema tests passed")
