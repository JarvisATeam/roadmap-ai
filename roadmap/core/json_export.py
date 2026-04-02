"""JSON export utilities for roadmap-ai."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional


VERSION = "0.3.0"


def create_envelope(
    command: str,
    data: Any,
    metadata: Optional[Dict] = None
) -> Dict:
    """Create standardized JSON envelope for all commands."""
    envelope = {
        "roadmap_version": VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "command": command,
        "data": data
    }
    if metadata:
        envelope["metadata"] = metadata
    return envelope


def to_json(envelope: Dict, indent: int = 2) -> str:
    """Convert envelope to JSON string."""
    return json.dumps(envelope, indent=indent, default=str)


def get_base_metadata() -> Dict:
    """Get base metadata for exports."""
    from roadmap.storage.db import get_session
    from roadmap.storage.models import Mission, Step

    session = get_session()
    try:
        missions_count = session.query(Mission).count()
        steps_total = session.query(Step).count()
        steps_done = session.query(Step).filter(Step.status == "done").count()
        return {
            "missions_count": missions_count,
            "steps_total": steps_total,
            "steps_completed": steps_done,
            "steps_remaining": steps_total - steps_done
        }
    finally:
        session.close()
