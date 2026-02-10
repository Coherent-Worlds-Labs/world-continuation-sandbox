from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from .domain import Difficulty

DIRECTIVE_CATALOG: dict[str, dict[str, Any]] = {
    "IntroduceAmbiguousFact": {"family": "introduce_fact"},
    "AgentCommitment": {"family": "agent_commitment"},
    "ResourceConstraint": {"family": "resource_constraint"},
    "InformationAsymmetry": {"family": "information_asymmetry"},
    "DelayedConsequence": {"family": "delayed_consequence"},
    "AgentActionDivergence": {"family": "agent_action"},
    "RetrospectiveReinterpretation": {"family": "reinterpretation"},
    "FalseConvergence": {"family": "false_convergence"},
    "MaintenanceEpoch": {"family": "maintenance"},
}

DIRECTIVES = list(DIRECTIVE_CATALOG.keys())


@dataclass(slots=True)
class BranchSignals:
    closure_pressure: float
    chaos_pressure: float
    uncertainty: float
    accept_rate: float


class TaskGenerator:
    def __init__(self, rng: random.Random, policy: dict[str, Any] | None = None) -> None:
        self.rng = rng
        self.policy = policy or {}
        self.max_same_directive_streak = int(self.policy.get("max_same_directive_streak", 2))

    @staticmethod
    def directive_family(directive: str) -> str:
        return str(DIRECTIVE_CATALOG.get(directive, {}).get("family", "other"))

    def _base_pool(self, signals: BranchSignals, mode: str) -> list[str]:
        if mode == "maintenance":
            return ["MaintenanceEpoch", "ResourceConstraint"]
        if mode == "diversify":
            return [
                "IntroduceAmbiguousFact",
                "AgentCommitment",
                "ResourceConstraint",
                "InformationAsymmetry",
                "DelayedConsequence",
                "AgentActionDivergence",
                "RetrospectiveReinterpretation",
            ]
        if signals.closure_pressure > 0.65:
            return ["AgentActionDivergence", "RetrospectiveReinterpretation", "InformationAsymmetry"]
        if signals.chaos_pressure > 0.65:
            return ["MaintenanceEpoch", "ResourceConstraint"]
        if signals.accept_rate > 0.8 and signals.uncertainty < 0.25:
            return ["FalseConvergence", "AgentCommitment"]
        return DIRECTIVES

    def pick_directive(
        self,
        signals: BranchSignals,
        mode: str,
        *,
        recent_directives: list[str] | None = None,
        required_families: list[str] | None = None,
    ) -> str:
        recent = recent_directives or []
        candidates = self._base_pool(signals, mode)
        if not candidates:
            candidates = DIRECTIVES[:]

        if len(recent) >= self.max_same_directive_streak:
            last = recent[-1]
            if all(item == last for item in recent[-self.max_same_directive_streak :]):
                filtered = [item for item in candidates if item != last]
                if filtered:
                    candidates = filtered

        if required_families:
            required = set(required_families)
            family_aligned = [d for d in candidates if self.directive_family(d) in required]
            if family_aligned:
                candidates = family_aligned

        return self.rng.choice(candidates)

    def build_difficulty(self, base: Difficulty, signals: BranchSignals, mode: str = "diversify") -> Difficulty:
        depth = max(1, min(8, base.dependency_depth + (1 if signals.accept_rate > 0.75 else 0)))
        cd = min(1.0, max(0.1, base.constraint_density + (0.1 if signals.closure_pressure > 0.6 else 0.0)))
        ul = min(1.0, max(0.1, base.underspecification_level + (0.1 if signals.accept_rate > 0.8 else 0.0)))
        ff = min(1.0, max(0.1, base.future_fragility + (0.15 if signals.accept_rate > 0.8 else 0.0)))
        nb = min(1.0, max(0.1, base.novelty_budget - (0.15 if signals.chaos_pressure > 0.7 else 0.0)))
        if mode == "diversify":
            cd = min(1.0, max(0.1, cd - 0.06))
            ul = min(1.0, max(0.1, ul + 0.12))
            ff = min(1.0, max(0.1, ff + 0.08))
            nb = min(1.0, max(0.1, nb + 0.18))
        return Difficulty(depth, cd, ul, ff, nb)
