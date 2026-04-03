"""Short ID resolver for roadmap-ai.

Resolves short prefixes to full UUIDs by matching against
missions, steps, and decisions in the current state.
"""

from typing import List, Dict


class AmbiguousIDError(Exception):
    """Raised when a short ID matches multiple entries."""
    def __init__(self, prefix: str, matches: List[str]):
        self.prefix = prefix
        self.matches = matches
        super().__init__(
            f"Ambiguous ID prefix '{prefix}' matches {len(matches)} entries: "
            + ", ".join(matches[:5])
        )


class IDNotFoundError(Exception):
    """Raised when a short ID matches nothing."""
    def __init__(self, prefix: str):
        self.prefix = prefix
        super().__init__(f"No match found for ID prefix '{prefix}'")


def resolve_id(prefix: str, candidates: List[str]) -> str:
    """Resolve a short ID prefix to a full UUID.

    Args:
        prefix: Short prefix (e.g., '280198' or '280')
        candidates: List of full UUIDs to match against

    Returns:
        The unique matching full UUID

    Raises:
        IDNotFoundError: No match found
        AmbiguousIDError: Multiple matches found
    """
    prefix = prefix.strip().lower()

    # Exact match first
    for c in candidates:
        if c.lower() == prefix:
            return c

    # Prefix match
    matches = [c for c in candidates if c.lower().startswith(prefix)]

    if len(matches) == 0:
        raise IDNotFoundError(prefix)
    elif len(matches) == 1:
        return matches[0]
    else:
        raise AmbiguousIDError(prefix, matches)


def resolve_mission_id(prefix: str, state: dict) -> str:
    """Resolve a short prefix to a full mission ID."""
    missions = state.get("missions", [])
    candidates = [m.get("id", "") for m in missions if m.get("id")]
    return resolve_id(prefix, candidates)


def resolve_step_id(prefix: str, state: dict, mission_id: str = None) -> str:
    """Resolve a short prefix to a full step/task ID.

    Optionally scope to a specific mission.
    """
    candidates = []
    missions = state.get("missions", [])
    for m in missions:
        if mission_id and m.get("id") != mission_id:
            continue
        for step in m.get("steps", []):
            step_id = step.get("id", "")
            if step_id:
                candidates.append(step_id)
    return resolve_id(prefix, candidates)


def load_state_snapshot() -> Dict:
    """Load current missions/steps for ID resolution."""
    from roadmap.core import data

    missions = data.load_missions()
    steps = data.load_tasks()
    mission_lookup: Dict[str, Dict] = {}
    for mission in missions:
        mission_copy = {**mission, "steps": []}
        mission_lookup[mission["id"]] = mission_copy
    for step in steps:
        mission_id = step.get("mission_id")
        if not mission_id:
            continue
        mission_entry = mission_lookup.get(mission_id)
        if not mission_entry:
            mission_entry = {"id": mission_id, "steps": []}
            mission_lookup[mission_id] = mission_entry
        mission_entry.setdefault("steps", []).append(step)
    return {"missions": list(mission_lookup.values())}
