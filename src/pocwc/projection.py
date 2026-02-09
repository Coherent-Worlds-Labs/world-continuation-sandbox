from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProjectionBuilder:
    """Build a compact projection from recent state artifacts."""

    def build(self, artifacts: list[str], depth: int) -> str:
        if not artifacts:
            return ""
        tail = artifacts[-max(1, depth):]
        return "\n\n".join(tail)
