from __future__ import annotations

import random
from dataclasses import dataclass

from .domain import Difficulty

DIRECTIVES = [
    "IntroduceAmbiguousFact",
    "AgentActionDivergence",
    "DelayedEffect",
    "FalseConvergence",
    "RetrospectiveReinterpretation",
    "MaintenanceEpoch",
]


@dataclass(slots=True)
class BranchSignals:
    closure_pressure: float
    chaos_pressure: float
    uncertainty: float
    accept_rate: float


class TaskGenerator:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def pick_directive(self, signals: BranchSignals, mode: str) -> str:
        if mode == "maintenance":
            return "MaintenanceEpoch"
        if mode == "diversify":
            return self.rng.choice(
                [
                    "IntroduceAmbiguousFact",
                    "AgentActionDivergence",
                    "DelayedEffect",
                    "RetrospectiveReinterpretation",
                ]
            )
        if signals.closure_pressure > 0.65:
            return self.rng.choice(["AgentActionDivergence", "RetrospectiveReinterpretation"])
        if signals.chaos_pressure > 0.65:
            return "MaintenanceEpoch"
        if signals.accept_rate > 0.8 and signals.uncertainty < 0.25:
            return "FalseConvergence"
        return self.rng.choice(DIRECTIVES)

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
