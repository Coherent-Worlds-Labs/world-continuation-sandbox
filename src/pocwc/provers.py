from __future__ import annotations

import random
from dataclasses import dataclass

from .domain import Candidate, Challenge


@dataclass(slots=True)
class Prover:
    prover_id: str
    style: str
    rng: random.Random

    def generate(self, challenge: Challenge, ordinal: int) -> Candidate:
        base_strength = {
            "I1": round(0.34 + self.rng.uniform(-0.08, 0.08), 3),
            "I2": round(0.33 + self.rng.uniform(-0.08, 0.08), 3),
            "I3": round(0.33 + self.rng.uniform(-0.08, 0.08), 3),
        }
        if self.style == "conservative":
            base_strength["I1"] += 0.04
        elif self.style == "aggressive":
            base_strength["I1"] += 0.12
            base_strength["I2"] -= 0.04
        elif self.style == "maintenance":
            base_strength = {k: round(v * 0.98, 3) for k, v in base_strength.items()}

        total = sum(base_strength.values())
        strengths = {k: round(v / total, 3) for k, v in base_strength.items()}

        artifact = (
            f"Directive: {challenge.directive_type}. "
            f"A new event shifts public interpretation while preserving unresolved alternatives. "
            f"Projection depth: {challenge.difficulty.dependency_depth}. "
            f"Candidate emphasis profile: {self.style}."
        )

        meta = {
            "claims": [
                "The event appears to support one interpretation on the surface.",
                "Alternative explanations remain plausible under deeper analysis.",
            ],
            "threads": [
                "How archival trust should be weighted against process uncertainty.",
                "Whether social consensus can diverge from semantic coherence.",
            ],
            "interpretation_strength": strengths,
            "closure_risk_hint": round(max(strengths.values()) - min(strengths.values()), 3),
        }

        return Candidate(
            candidate_id=f"{challenge.challenge_id}-cand-{ordinal}",
            challenge_id=challenge.challenge_id,
            prover_id=self.prover_id,
            artifact_x=artifact,
            meta_m=meta,
        )


def default_provers(rng: random.Random) -> list[Prover]:
    return [
        Prover("prover-conservative", "conservative", rng),
        Prover("prover-aggressive", "aggressive", rng),
        Prover("prover-maintenance", "maintenance", rng),
    ]
