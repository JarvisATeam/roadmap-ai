"""Tests for short ID resolver."""

import pytest
from roadmap.core.id_resolver import (
    resolve_id,
    resolve_mission_id,
    resolve_step_id,
    AmbiguousIDError,
    IDNotFoundError,
)


SAMPLE_IDS = [
    "280198d6-6e65-4f92-8fba-fd5af85dfc2c",
    "69ef1c88-ec77-4a97-b819-fb02f812e6ac",
    "a1b2c3d4-0000-0000-0000-000000000001",
    "a1b2c3d4-0000-0000-0000-000000000002",
]

SAMPLE_STATE = {
    "missions": [
        {
            "id": "69ef1c88-ec77-4a97-b819-fb02f812e6ac",
            "steps": [
                {"id": "280198d6-6e65-4f92-8fba-fd5af85dfc2c"},
                {"id": "a1b2c3d4-0000-0000-0000-000000000001"},
            ],
        },
        {
            "id": "bbbb1111-0000-0000-0000-000000000000",
            "steps": [
                {"id": "a1b2c3d4-0000-0000-0000-000000000002"},
            ],
        },
    ]
}


class TestResolveId:
    def test_exact_match(self):
        result = resolve_id("280198d6-6e65-4f92-8fba-fd5af85dfc2c", SAMPLE_IDS)
        assert result == "280198d6-6e65-4f92-8fba-fd5af85dfc2c"

    def test_short_prefix_unique(self):
        result = resolve_id("2801", SAMPLE_IDS)
        assert result == "280198d6-6e65-4f92-8fba-fd5af85dfc2c"

    def test_short_prefix_single_char(self):
        result = resolve_id("6", SAMPLE_IDS)
        assert result == "69ef1c88-ec77-4a97-b819-fb02f812e6ac"

    def test_ambiguous_prefix(self):
        with pytest.raises(AmbiguousIDError) as exc:
            resolve_id("a1b2", SAMPLE_IDS)
        assert len(exc.value.matches) == 2

    def test_no_match(self):
        with pytest.raises(IDNotFoundError):
            resolve_id("zzz", SAMPLE_IDS)

    def test_case_insensitive(self):
        result = resolve_id("2801", SAMPLE_IDS)
        assert result == "280198d6-6e65-4f92-8fba-fd5af85dfc2c"

    def test_empty_candidates(self):
        with pytest.raises(IDNotFoundError):
            resolve_id("abc", [])


class TestResolveMissionId:
    def test_resolve_mission(self):
        result = resolve_mission_id("69ef", SAMPLE_STATE)
        assert result == "69ef1c88-ec77-4a97-b819-fb02f812e6ac"

    def test_mission_not_found(self):
        with pytest.raises(IDNotFoundError):
            resolve_mission_id("zzz", SAMPLE_STATE)


class TestResolveStepId:
    def test_resolve_step(self):
        result = resolve_step_id("2801", SAMPLE_STATE)
        assert result == "280198d6-6e65-4f92-8fba-fd5af85dfc2c"

    def test_resolve_step_scoped(self):
        result = resolve_step_id(
            "a1b2c3d4-0000-0000-0000-000000000002",
            SAMPLE_STATE,
            mission_id="bbbb1111-0000-0000-0000-000000000000",
        )
        assert result == "a1b2c3d4-0000-0000-0000-000000000002"

    def test_step_ambiguous_across_missions(self):
        with pytest.raises(AmbiguousIDError):
            resolve_step_id("a1b2", SAMPLE_STATE)
