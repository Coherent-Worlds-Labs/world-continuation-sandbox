from __future__ import annotations

import random
from dataclasses import dataclass

from .domain import Candidate, Challenge, VerificationLevel, VerificationResult, Verdict
from .invariants import evaluate_invariants
from .llm import LLMAdapter


@dataclass(slots=True)
class Verifier:
    verifier_id: str
    sensitivity: float
    rng: random.Random
    llm: LLMAdapter | None = None

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

        if self.llm is not None:
            llm_signals = self._llm_semantic_signals(challenge, candidate)
            if llm_signals is not None:
                closure_risk = (closure_risk + llm_signals["closure_risk"]) / 2
                chaos_risk = (chaos_risk + llm_signals["chaos_risk"]) / 2
                fragility = (fragility + llm_signals["fragility_score"]) / 2

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

    def _llm_semantic_signals(self, challenge: Challenge, candidate: Candidate) -> dict[str, float] | None:
        system = (
            "You evaluate narrative coherence in PoCWC. Return JSON only with closure_risk, chaos_risk, fragility_score in [0,1]."
        )
        prompt = (
            f"Directive: {challenge.directive_type}\n"
            f"Projection: {challenge.projection}\n"
            f"Candidate artifact: {candidate.artifact_x}\n"
            "Evaluate risks: closure_risk (premature finality), chaos_risk (incoherent drift), fragility_score (single-point narrative support)."
        )
        try:
            payload = self.llm.generate_json(system_prompt=system, user_prompt=prompt, temperature=0.0, max_tokens=280)
        except Exception:  # noqa: BLE001
            return None
        if not isinstance(payload, dict):
            return None
        try:
            return {
                "closure_risk": max(0.0, min(1.0, float(payload.get("closure_risk", 0.5)))),
                "chaos_risk": max(0.0, min(1.0, float(payload.get("chaos_risk", 0.5)))),
                "fragility_score": max(0.0, min(1.0, float(payload.get("fragility_score", 0.5)))),
            }
        except (TypeError, ValueError):
            return None


def default_verifiers(rng: random.Random, llm: LLMAdapter | None = None) -> list[Verifier]:
    return [
        Verifier("verifier-a", 0.95, rng, llm),
        Verifier("verifier-b", 1.00, rng, llm),
        Verifier("verifier-c", 1.05, rng, llm),
    ]
