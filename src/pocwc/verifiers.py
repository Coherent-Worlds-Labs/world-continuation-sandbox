from __future__ import annotations

import random
from dataclasses import dataclass

from .domain import Candidate, Challenge, VerificationLevel, VerificationResult, Verdict
from .invariants import evaluate_invariants


@dataclass(slots=True)
class Verifier:
    verifier_id: str
    sensitivity: float
    rng: random.Random

    def evaluate(self, challenge: Challenge, candidate: Candidate, allow_l3: bool = False) -> VerificationResult:
        failures = evaluate_invariants(candidate.artifact_x, candidate.meta_m)
        if failures:
            return VerificationResult(
                candidate_id=candidate.candidate_id,
                verifier_id=self.verifier_id,
                level_max_reached=VerificationLevel.L0,
                verdict=Verdict.REJECT,
                score=0.0,
                signals={"closure_risk": 1.0, "chaos_risk": 0.0, "fragility_score": 0.9},
                notes="; ".join(failures),
            )

        closure_risk = float(candidate.meta_m.get("closure_risk_hint", 0.5))
        chaos_risk = max(0.0, min(1.0, challenge.difficulty.underspecification_level * 0.5 + self.rng.uniform(-0.1, 0.1)))
        fragility = max(0.0, min(1.0, challenge.difficulty.future_fragility * 0.7 + closure_risk * 0.3))

        base = 1.0 - (0.45 * closure_risk + 0.35 * chaos_risk + 0.20 * fragility)
        score = max(0.0, min(1.0, base - self.sensitivity * 0.08 + self.rng.uniform(-0.05, 0.05)))

        if score >= 0.58:
            verdict = Verdict.ACCEPT
            level = VerificationLevel.L2
        elif score >= 0.45:
            verdict = Verdict.ESCALATE if allow_l3 else Verdict.REJECT
            level = VerificationLevel.L2
            if allow_l3:
                l3_adjust = self.rng.uniform(-0.08, 0.10)
                score = max(0.0, min(1.0, score + l3_adjust))
                verdict = Verdict.ACCEPT if score >= 0.55 else Verdict.REJECT
                level = VerificationLevel.L3
        else:
            verdict = Verdict.REJECT
            level = VerificationLevel.L2

        return VerificationResult(
            candidate_id=candidate.candidate_id,
            verifier_id=self.verifier_id,
            level_max_reached=level,
            verdict=verdict,
            score=round(score, 3),
            signals={
                "closure_risk": round(closure_risk, 3),
                "chaos_risk": round(chaos_risk, 3),
                "fragility_score": round(fragility, 3),
            },
            notes=f"evaluated at {level.value}",
        )


def default_verifiers(rng: random.Random) -> list[Verifier]:
    return [
        Verifier("verifier-a", 0.95, rng),
        Verifier("verifier-b", 1.00, rng),
        Verifier("verifier-c", 1.05, rng),
    ]
