from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

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
    min_novelty_score: float = 0.30
    hard_similarity_threshold: float = 0.92

    @staticmethod
    def _fact_text(fact: dict[str, Any]) -> str:
        return " | ".join(
            [
                str(fact.get("subject", "")),
                str(fact.get("predicate", "")),
                str(fact.get("object", "")),
                str(fact.get("time_hint", "")),
                str(fact.get("location_hint", "")),
            ]
        ).strip()

    def _normalized_facts(self, candidate: Candidate) -> list[dict[str, Any]]:
        facts = candidate.meta_m.get("novel_facts", [])
        if not isinstance(facts, list):
            return []
        normalized: list[dict[str, Any]] = []
        for item in facts:
            if not isinstance(item, dict):
                continue
            text = self._fact_text(item)
            if not text:
                continue
            normalized.append(item)
        return normalized

    @staticmethod
    def _fact_object_valid(fact: dict[str, Any]) -> tuple[bool, str]:
        required = ["id", "type", "content", "introduced_by", "time", "evidence", "interpretation_affinity", "references"]
        missing = [key for key in required if key not in fact]
        if missing:
            return False, f"missing fields: {', '.join(missing)}"
        if not str(fact.get("id", "")).strip():
            return False, "id is empty"
        if not str(fact.get("type", "")).strip():
            return False, "type is empty"
        content = str(fact.get("content", "")).strip()
        if len(content.split()) < 4:
            return False, "content is too short"
        affinity = fact.get("interpretation_affinity")
        if not isinstance(affinity, dict):
            return False, "interpretation_affinity must be an object"
        refs = fact.get("references")
        if not isinstance(refs, list):
            return False, "references must be a list"
        return True, ""

    def _equivalent_fact(self, fact: dict[str, Any], recent_facts: list[str]) -> bool:
        content = str(fact.get("content", "")).strip()
        ftype = str(fact.get("type", "")).strip()
        ref_text = ",".join(str(x) for x in fact.get("references", []))
        probe = f"{ftype} | {content} | refs:{ref_text}"
        if not probe.strip():
            return False
        max_sim = max((semantic_similarity(probe, prev, self.llm) for prev in recent_facts), default=0.0)
        return max_sim >= 0.93

    def evaluate(self, challenge: Challenge, candidate: Candidate, allow_l3: bool = False) -> VerificationResult:
        _ = allow_l3
        policy = challenge.verifier_policy
        recent_facts = list(policy.get("recent_fact_texts", []))
        recent_narratives = list(policy.get("recent_narratives", []))
        active_anchor_ids = set(str(x) for x in policy.get("active_anchor_ids", []))
        required_min_new_facts = max(0, int(policy.get("required_min_new_facts", 1)))
        max_new_facts_per_step = max(1, int(policy.get("max_new_facts_per_step", 1)))
        dependency_target_depth = max(1, int(policy.get("dependency_target_depth", 4)))
        required_reference_count = max(1, int(policy.get("required_reference_count", 2)))
        enforce_dependency_accumulation = bool(policy.get("enforce_dependency_accumulation", True))
        min_refs_at_height_2 = max(1, int(policy.get("min_refs_height_2", 1)))
        min_refs_at_height_5 = max(1, int(policy.get("min_refs_height_5", 2)))
        current_height = max(1, int(policy.get("current_height", 1)))

        facts = self._normalized_facts(candidate)
        fact_object = candidate.meta_m.get("fact_object", {})
        fact_ok, fact_reason = self._fact_object_valid(fact_object) if isinstance(fact_object, dict) else (False, "fact_object missing")

        unique_new = 0
        named_count = 0
        referenced_anchors: set[str] = set()
        commitment_count = 0

        for item in facts:
            fact_id = str(item.get("fact_id", "")).strip()
            if fact_id:
                named_count += 1
            text = self._fact_text(item)
            max_sim = max((semantic_similarity(text, prev, self.llm) for prev in recent_facts), default=0.0)
            if max_sim < 0.82:
                unique_new += 1
            references = item.get("references", [])
            if isinstance(references, list):
                for ref in references:
                    ref_id = str(ref).strip()
                    if ref_id and ref_id in active_anchor_ids:
                        referenced_anchors.add(ref_id)
            if str(item.get("anchor_type", "")).strip() == "agent_commitment":
                commitment_count += 1

        scene = str(candidate.meta_m.get("story_bundle", {}).get("scene", "")).strip()
        max_scene_similarity = max((semantic_similarity(scene, prev, self.llm) for prev in recent_narratives), default=0.0)
        similarity_threshold = float(policy.get("hard_similarity_threshold", self.hard_similarity_threshold))
        semantic_delta = 1.0 - max_scene_similarity

        llm_novelty = self._llm_novelty_estimate(challenge, candidate, recent_narratives)
        novelty_score = llm_novelty if llm_novelty is not None else semantic_delta
        tension_progress = float(candidate.meta_m.get("tension_progress", 0.5))

        hard_fail = False
        reasons: list[str] = []

        if not fact_ok:
            hard_fail = True
            reasons.append(f"Novelty gate failed: invalid fact_object ({fact_reason})")
        if named_count != len(facts):
            hard_fail = True
            reasons.append("Novelty gate failed: every fact must have a non-empty fact_id")
        if unique_new < required_min_new_facts:
            hard_fail = True
            reasons.append("Novelty gate failed: insufficient new structured facts")
        if unique_new > max_new_facts_per_step:
            hard_fail = True
            reasons.append("Novelty gate failed: too many new facts for one step")
        if novelty_score < self.min_novelty_score:
            hard_fail = True
            reasons.append("Novelty gate failed: semantic delta below threshold")
        if max_scene_similarity > similarity_threshold:
            hard_fail = True
            reasons.append("Novelty gate failed: hard repetition threshold exceeded")
        if not str(candidate.meta_m.get("what_changed_since_previous_step", "")).strip():
            hard_fail = True
            reasons.append("Novelty gate failed: missing explicit change annotation")

        if (
            enforce_dependency_accumulation
            and challenge.difficulty.dependency_depth < dependency_target_depth
            and len(active_anchor_ids) >= required_reference_count
        ):
            if len(referenced_anchors) < required_reference_count:
                hard_fail = True
                reasons.append("Novelty gate failed: insufficient references to prior anchors")

        if challenge.directive_type == "AgentCommitment" and commitment_count < 1:
            hard_fail = True
            reasons.append("Novelty gate failed: AgentCommitment directive requires commitment anchor")
        if self._equivalent_fact(fact_object if isinstance(fact_object, dict) else {}, recent_facts):
            hard_fail = True
            reasons.append("Novelty gate failed: fact is equivalent to an existing anchor")

        required_refs_by_height = 0
        if current_height >= 5:
            required_refs_by_height = min_refs_at_height_5
        elif current_height >= 2:
            required_refs_by_height = min_refs_at_height_2
        if required_refs_by_height > 0 and len(referenced_anchors) < required_refs_by_height and len(active_anchor_ids) >= required_refs_by_height:
            hard_fail = True
            reasons.append("Novelty gate failed: reference accumulation policy violated")

        verdict = Verdict.REJECT if hard_fail else Verdict.ACCEPT
        score = max(0.0, min(1.0, novelty_score))
        progress_gate = 0.0 if hard_fail else 1.0
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
                "new_fact_count": float(int(unique_new)),
                "named_fact_count": float(int(named_count)),
                "reference_count": float(int(len(referenced_anchors))),
                "max_scene_similarity": round(max_scene_similarity, 3),
                "progress_gate": progress_gate,
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
