from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


DEFAULT_WORLD_CONFIG_PATH = Path("config/world.default.json")


def _default_world_config() -> dict[str, Any]:
    return {
        "world_id": "alice-competing-interpretations",
        "anchor_character": "Alice",
        "main_branch_id": "branch-main",
        "genesis": {
            "state_id": "state-0",
            "artifact_x": (
                "In Alice's city, a foundational event happened years ago, yet no one can state what truly happened. "
                "Some call it an accident, others an experiment, others a cumulative drift. "
                "Every new fact shifts plausibility, but no interpretation reaches final truth."
            ),
            "entities": ["E0", "Alice", "I1", "I2", "I3"],
            "threads": ["origin ambiguity", "institutional trust", "memory reliability"],
            "interpretation_strength": {"I1": 0.34, "I2": 0.33, "I3": 0.33},
            "story_bundle": {
                "scene": "Alice lives in a city changed by an unnamed event from years ago.",
                "surface_confirmation": "No single interpretation can claim certainty.",
                "alternative_compatibility": [
                    "Some describe the event as an accident hidden by institutions.",
                    "Others describe it as an intentional experiment or a long drift of choices.",
                ],
                "social_effect": "Public discourse fragments into stable but conflicting narratives.",
                "deferred_tension": "Alice remembers life as simpler but cannot prove what changed.",
            },
            "branch_metrics": {
                "semantic_debt_est": 0.5,
                "uncertainty": 0.5,
                "closure_pressure": 0.5,
                "chaos_pressure": 0.5,
            },
            "story_memory": {
                "summary": "Alice's world begins with one unresolved event and three competing interpretations.",
                "known_entities": ["E0", "Alice", "city archive"],
                "unresolved_tensions": [
                    "What happened at E0",
                    "Whether records reflect truth or process noise",
                ],
                "timeline_highlights": [
                    "Genesis uncertainty is stable and no final truth is available.",
                ],
            },
            "story_event": {
                "title": "Genesis: The City After E0",
                "scene": "Alice and the city hold incompatible memories of a foundational event.",
                "surface_confirmation": "No interpretation is final.",
                "alternative_compatibility": [
                    "Accident narrative",
                    "Experiment narrative",
                    "Cumulative drift narrative",
                ],
                "social_effect": "Interpretive camps emerge without resolving the underlying event.",
                "deferred_tension": "Alice cannot map memory certainty to objective evidence.",
            },
        },
        "continuity": {
            "default_known_entities": ["Alice", "E0", "city archive"],
            "summary_template": "{anchor_character} continuity at height {height}: {scene_excerpt}",
        },
        "fallback_generation": {
            "scene_templates": [
                "Alice notices another discrepancy in records that should have remained stable.",
                "Alice observes a new contradiction between witness logs and municipal archives.",
                "Alice receives a field report that conflicts with the official timeline.",
                "Alice traces a fresh mismatch across two agencies that should share the same source data.",
            ],
            "event_templates": [
                "A courier delivers an annotated map from the old transit office at dawn.",
                "A maintenance team finds a sealed container near the river checkpoint at midnight.",
                "A council aide releases a timestamped memo from the northern district archive.",
                "A volunteer scanner uncovers a mislabeled evidence card in the central depot.",
            ],
            "alternative_compatibility": [
                "A process-trace explanation preserves uncertainty by attributing confidence to archival workflow noise.",
                "A social-belief explanation preserves uncertainty by showing group incentives can mimic evidence.",
            ],
            "social_effect": (
                "Communities split between evidence-first and interpretation-first responses, increasing coordination friction."
            ),
            "deferred_tension": (
                "The world gains a new unresolved thread: should trust attach to the discovered artifact or to the discovery process?"
            ),
        },
    }


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_world_config(path: Path | None = None) -> dict[str, Any]:
    base = _default_world_config()
    cfg_path = path or DEFAULT_WORLD_CONFIG_PATH
    if cfg_path.exists():
        payload = json.loads(cfg_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("World config root must be a JSON object")
        merged = _deep_merge(base, payload)
    else:
        merged = base

    # Normalize scalar identity fields.
    merged["world_id"] = str(merged.get("world_id", base["world_id"]))
    merged["anchor_character"] = str(merged.get("anchor_character", base["anchor_character"]))
    merged["main_branch_id"] = str(merged.get("main_branch_id", base["main_branch_id"]))
    return merged
