from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


DEFAULT_WORLD_CONFIG_PATH = Path("config/world.default.json")


def _read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"World config root must be a JSON object: {path}")
    return payload


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_world_config(path: Path | None = None) -> dict[str, Any]:
    if not DEFAULT_WORLD_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Default world config not found: {DEFAULT_WORLD_CONFIG_PATH}")

    base = _read_json_object(DEFAULT_WORLD_CONFIG_PATH)
    cfg_path = path or DEFAULT_WORLD_CONFIG_PATH
    if cfg_path == DEFAULT_WORLD_CONFIG_PATH:
        merged = base
    else:
        if not cfg_path.exists():
            raise FileNotFoundError(f"World config not found: {cfg_path}")
        override = _read_json_object(cfg_path)
        merged = _deep_merge(base, override)

    # Basic identity normalization; world content remains in JSON files.
    merged["world_id"] = str(merged.get("world_id", "world"))
    merged["anchor_character"] = str(merged.get("anchor_character", "anchor"))
    merged["main_branch_id"] = str(merged.get("main_branch_id", "branch-main"))
    return merged
