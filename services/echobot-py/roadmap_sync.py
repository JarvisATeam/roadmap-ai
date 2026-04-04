from __future__ import annotations
import json
import sys
from typing import Any

def to_mission_payload(lead: dict[str, Any]) -> dict[str, Any]:
    company = lead.get("companyName") or lead.get("company_name") or "Unknown company"
    problem = lead.get("hypothesis") or lead.get("problemSummary") or "Validate opportunity and prepare operator follow-up"
    return {
        "missionTitle": f"Echobot follow-up: {company}",
        "origin": "echobot",
        "proofDefinition": {
            "description": problem,
            "requiredArtifacts": ["Lead review notes", "Proof of contact", "Commercial follow-up plan"],
        },
        "operatorNotes": lead.get("draftBody") or lead.get("notes") or "",
        "nextActions": [
            f"Review lead context for {company}",
            "Confirm scope and commercial fit",
            "Send or refine offer",
            "Track reply/payment and update operator state",
        ],
        "metadata": {"lead": lead},
    }

if __name__ == "__main__":
    incoming = json.loads(sys.stdin.read() or "{}")
    print(json.dumps(to_mission_payload(incoming), ensure_ascii=False))
