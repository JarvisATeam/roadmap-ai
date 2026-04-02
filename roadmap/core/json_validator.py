"""JSON schema validation helpers for roadmap exports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from roadmap.core.json_export import VERSION

ENVELOPE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["roadmap_version", "timestamp", "command", "data"],
    "properties": {
        "roadmap_version": {"type": "string"},
        "timestamp": {"type": "string"},
        "command": {"type": "string"},
        "data": {"type": ["object", "null"]},
        "metadata": {"type": "object"},
    },
}

SMART_NEXT_SCHEMA = {
    **ENVELOPE_SCHEMA,
    "properties": {
        **ENVELOPE_SCHEMA["properties"],
        "data": {
            "type": "object",
            "properties": {
                "recommendation": {
                    "type": ["object", "null"],
                    "properties": {
                        "step_id": {"type": "string"},
                        "description": {"type": "string"},
                        "score": {"type": "number"},
                        "factors": {
                            "type": "object",
                            "properties": {
                                "revenue_weight": {"type": "number"},
                                "urgency": {"type": "number"},
                                "energy_match": {"type": "number"},
                                "context_cost": {"type": "number"},
                                "risk_penalty": {"type": "number"},
                            },
                        },
                    },
                }
            },
        },
    },
}

RISKS_SCHEMA = {
    **ENVELOPE_SCHEMA,
    "properties": {
        **ENVELOPE_SCHEMA["properties"],
        "data": {
            "type": "object",
            "properties": {
                "missions_analyzed": {"type": "integer"},
                "warnings": {"type": "array"},
                "blocked_steps": {"type": "integer"},
                "overdue_steps": {"type": "integer"},
                "critical_warnings": {"type": "integer"},
            },
        },
    },
}

STATUS_SCHEMA = {
    **ENVELOPE_SCHEMA,
    "properties": {
        **ENVELOPE_SCHEMA["properties"],
        "data": {
            "type": "object",
            "properties": {
                "missions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "mission_code": {"type": "string"},
                            "title": {"type": "string"},
                            "revenue": {"type": ["integer", "null"]},
                            "steps_total": {"type": "integer"},
                            "steps_completed": {"type": "integer"},
                        },
                    },
                },
                "missions_count": {"type": "integer"},
            },
        },
    },
}

SCHEMAS = {
    "envelope": ENVELOPE_SCHEMA,
    "smart next": SMART_NEXT_SCHEMA,
    "risks": RISKS_SCHEMA,
    "status": STATUS_SCHEMA,
}


def _basic_validate(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    for field in schema.get("required", []):
        if field not in data:
            return False, f"Missing required field: {field}"
    for field, spec in schema.get("properties", {}).items():
        if field not in data:
            continue
        expected = spec.get("type")
        value = data[field]
        if expected == "string" and not isinstance(value, str):
            return False, f"Field '{field}' must be string"
        if expected == "object" and not isinstance(value, dict):
            return False, f"Field '{field}' must be object"
        if expected == "array" and not isinstance(value, list):
            return False, f"Field '{field}' must be array"
        if expected == "integer" and not isinstance(value, int):
            return False, f"Field '{field}' must be integer"
        if expected == "number" and not isinstance(value, (int, float)):
            return False, f"Field '{field}' must be number"
    return True, None


def validate_json(data: Dict[str, Any], schema_name: str = "envelope") -> Tuple[bool, Optional[str]]:
    schema = SCHEMAS.get(schema_name, ENVELOPE_SCHEMA)
    try:
        from jsonschema import ValidationError, validate  # type: ignore
    except ImportError:
        return _basic_validate(data, schema)

    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as exc:  # pragma: no cover - handled in fallback
        return False, exc.message


def validate_json_file(path: Path, schema_name: str = "envelope") -> Tuple[bool, Optional[str]]:
    try:
        with path.open("r") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return False, f"File not found: {path}"
    except json.JSONDecodeError as exc:
        return False, f"Invalid JSON: {exc}"
    return validate_json(data, schema_name)


def auto_schema_for_file(path: Path) -> str:
    try:
        with path.open("r") as fh:
            data = json.load(fh)
    except Exception:
        return "envelope"
    return data.get("command") if data.get("command") in SCHEMAS else "envelope"
