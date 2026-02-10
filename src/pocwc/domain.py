from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BranchStatus(str, Enum):
    ACTIVE = "active"
    STALLED = "stalled"
    ARCHIVED = "archived"


class Verdict(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    ESCALATE = "escalate"


class VerificationLevel(str, Enum):
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


@dataclass(slots=True)
class Difficulty:
    dependency_depth: int = 2
    constraint_density: float = 0.5
    underspecification_level: float = 0.5
    future_fragility: float = 0.5
    novelty_budget: float = 0.5

    def as_dict(self) -> dict[str, Any]:
        return {
            "dependency_depth": self.dependency_depth,
            "constraint_density": self.constraint_density,
            "underspecification_level": self.underspecification_level,
            "future_fragility": self.future_fragility,
            "novelty_budget": self.novelty_budget,
        }


@dataclass(slots=True)
class Challenge:
    challenge_id: str
    branch_id: str
    parent_state_id: str
    projection: str
    directive_type: str
    difficulty: Difficulty
    verifier_policy: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Candidate:
    candidate_id: str
    challenge_id: str
    prover_id: str
    artifact_x: str
    meta_m: dict[str, Any]


@dataclass(slots=True)
class VerificationResult:
    candidate_id: str
    verifier_id: str
    level_max_reached: VerificationLevel
    verdict: Verdict
    score: float
    signals: dict[str, Any]
    notes: str = ""
