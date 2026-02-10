from __future__ import annotations

import random
from dataclasses import dataclass

from .domain import Candidate, Challenge, VerificationLevel, VerificationResult, Verdict
from .invariants import evaluate_invariants
from .llm import LLMAdapter
from .semantic import semantic_similarity


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


@dataclass(slots=True)
class NoveltyGateVerifier:
    verifier_id: str
    rng: random.Random
    llm: LLMAdapter | None = None
    min_new_facts: int = 2
    min_novelty_score: float = 0.30

    @staticmethod
    def _fact_text(fact: dict) -> str:
        return " | ".join(
            [
                str(fact.get("subject", "")),
                str(fact.get("predicate", "")),
                str(fact.get("object", "")),
                str(fact.get("time_hint", "")),
                str(fact.get("location_hint", "")),
            ]
        ).strip()

    def evaluate(self, challenge: Challenge, candidate: Candidate, allow_l3: bool = False) -> VerificationResult:
        recent_facts = list(challenge.verifier_policy.get("recent_fact_texts", []))
        recent_narratives = list(challenge.verifier_policy.get("recent_narratives", []))
        facts = candidate.meta_m.get("novel_facts", [])
        if not isinstance(facts, list):
            facts = []

        unique_new = 0
        for item in facts:
            if not isinstance(item, dict):
                continue
            text = self._fact_text(item)
            if not text:
                continue
            max_sim = max((semantic_similarity(text, prev, self.llm) for prev in recent_facts), default=0.0)
            if max_sim < 0.82:
                unique_new += 1

        scene = str(candidate.meta_m.get("story_bundle", {}).get("scene", "")).strip()
        semantic_delta = 1.0 - max((semantic_similarity(scene, prev, self.llm) for prev in recent_narratives), default=0.0)

        llm_novelty = self._llm_novelty_estimate(challenge, candidate, recent_narratives)
        novelty_score = llm_novelty if llm_novelty is not None else semantic_delta
        tension_progress = float(candidate.meta_m.get("tension_progress", 0.5))

        hard_fail = False
        reasons: list[str] = []
        if unique_new < self.min_new_facts:
            hard_fail = True
            reasons.append("Novelty gate failed: insufficient new structured facts")
        if novelty_score < self.min_novelty_score:
            hard_fail = True
            reasons.append("Novelty gate failed: semantic delta below threshold")
        if not str(candidate.meta_m.get("what_changed_since_previous_step", "")).strip():
            hard_fail = True
            reasons.append("Novelty gate failed: missing explicit change annotation")

        verdict = Verdict.REJECT if hard_fail else Verdict.ACCEPT
        score = max(0.0, min(1.0, novelty_score))
        return VerificationResult(
            candidate_id=candidate.candidate_id,
            verifier_id=self.verifier_id,
            level_max_reached=VerificationLevel.L2,
            verdict=verdict,
            score=round(score, 3),
            signals={
                "closure_risk": 0.45,
                "chaos_risk": 0.45,
                "fragility_score": round(max(0.0, 1.0 - novelty_score), 3),
                "novelty_score": round(novelty_score, 3),
                "new_fact_count": float(unique_new),
                "tension_progress": round(tension_progress, 3),
            },
            notes="; ".join(reasons) if reasons else "novelty gate passed",
        )

    def _llm_novelty_estimate(
        self,
        challenge: Challenge,
        candidate: Candidate,
        recent_narratives: list[str],
    ) -> float | None:
        if self.llm is None:
            return None
        system = "You evaluate semantic novelty progression. Return JSON: {novelty_score: float 0..1}."
        prompt = (
            f"Directive: {challenge.directive_type}\n"
            f"Recent narratives: {recent_narratives[-5:]}\n"
            f"Candidate scene: {candidate.meta_m.get('story_bundle', {}).get('scene', '')}\n"
            f"Candidate novel facts: {candidate.meta_m.get('novel_facts', [])}\n"
            "Score novelty considering factual progression, not wording."
        )
        try:
            payload = self.llm.generate_json(system_prompt=system, user_prompt=prompt, temperature=0.0, max_tokens=220)
            return max(0.0, min(1.0, float(payload.get("novelty_score", 0.5))))
        except Exception:  # noqa: BLE001
            return None


def default_verifiers(rng: random.Random, llm: LLMAdapter | None = None) -> list[object]:
    return [
        NoveltyGateVerifier("verifier-novelty", rng, llm),
        Verifier("verifier-a", 0.95, rng, llm),
        Verifier("verifier-b", 1.00, rng, llm),
        Verifier("verifier-c", 1.05, rng, llm),
    ]
