from __future__ import annotations

import math
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
    def _canonical_fact_text_from_object(fact: dict[str, Any]) -> str:
        ftype = str(fact.get("type", "")).strip()
        content = str(fact.get("content", "")).strip()
        evidence = fact.get("evidence", [])
        if isinstance(evidence, list):
            evidence_text = " ; ".join(str(x).strip() for x in evidence if str(x).strip())
        else:
            evidence_text = str(evidence).strip()
        return f"{ftype}: {content} | {evidence_text}".strip()

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
        if not str(fact.get("introduced_by", "")).strip():
            return False, "introduced_by is empty"
        content = str(fact.get("content", "")).strip()
        if len(content.split()) < 4:
            return False, "content is too short"

        affinity = fact.get("interpretation_affinity")
        if not isinstance(affinity, dict) or not affinity:
            return False, "interpretation_affinity must be an object"
        affinity_values: list[float] = []
        for _, val in affinity.items():
            try:
                affinity_values.append(float(val))
            except (TypeError, ValueError):
                return False, "interpretation_affinity contains non-numeric values"
        total = sum(affinity_values)
        if abs(total - 1.0) > 0.08:
            return False, "interpretation_affinity must sum to 1"

        evidence = fact.get("evidence")
        if isinstance(evidence, list):
            evidence_items = [str(x).strip() for x in evidence if str(x).strip()]
        else:
            evidence_items = [str(evidence).strip()] if str(evidence).strip() else []
        if not evidence_items:
            return False, "evidence is empty"

        refs = fact.get("references")
        if not isinstance(refs, list):
            return False, "references must be a list"
        return True, ""

    def _equivalent_fact(self, fact: dict[str, Any], recent_facts: list[str]) -> bool:
        probe = self._canonical_fact_text_from_object(fact)
        if not probe.strip():
            return False
        max_sim = max((semantic_similarity(probe, prev, self.llm) for prev in recent_facts), default=0.0)
        return max_sim >= 0.93

    def evaluate(self, challenge: Challenge, candidate: Candidate, allow_l3: bool = False) -> VerificationResult:
        _ = allow_l3
        policy = challenge.verifier_policy

        recent_fact_texts = [str(x).strip() for x in policy.get("recent_fact_texts", []) if str(x).strip()]
        recent_fact_types = [str(x).strip() for x in policy.get("recent_fact_types", []) if str(x).strip()]
        fact_height_by_id_raw = policy.get("fact_height_by_id", {})
        fact_height_by_id = (
            {str(k): int(v) for k, v in fact_height_by_id_raw.items()} if isinstance(fact_height_by_id_raw, dict) else {}
        )
        recent_narratives = [str(x).strip() for x in policy.get("recent_narratives", []) if str(x).strip()]
        active_anchor_ids = set(str(x).strip() for x in policy.get("active_anchor_ids", []) if str(x).strip())

        max_new_facts_per_step = max(1, int(policy.get("max_new_facts_per_step", 1)))
        dependency_target_depth = max(1, int(policy.get("dependency_target_depth", 4)))
        required_reference_count = max(1, int(policy.get("required_reference_count", 2)))
        enforce_dependency_accumulation = bool(policy.get("enforce_dependency_accumulation", True))
        min_refs_at_height_2 = max(0, int(policy.get("min_refs_height_2", 1)))
        min_refs_at_height_5 = max(0, int(policy.get("min_refs_height_5", 2)))
        refs_quality_min_height_2 = max(0.0, float(policy.get("refs_quality_min_height_2", 0.8)))
        refs_quality_min_height_5 = max(0.0, float(policy.get("refs_quality_min_height_5", 1.2)))
        refs_quality_alpha = max(0.01, float(policy.get("refs_quality_alpha", 0.18)))
        novelty_min_early = max(0.0, min(1.0, float(policy.get("novelty_min_early", 0.45))))
        novelty_min_mid = max(0.0, min(1.0, float(policy.get("novelty_min_mid", 0.55))))
        novelty_min_late = max(0.0, min(1.0, float(policy.get("novelty_min_late", 0.60))))
        type_memory_window = max(1, int(policy.get("type_memory_window", 7)))
        hard_fact_similarity_threshold = max(0.0, min(1.0, float(policy.get("sim_fact_max", self.hard_similarity_threshold))))
        scene_repeat_threshold = max(0.0, min(1.0, float(policy.get("scene_repeat_threshold", 0.97))))
        refs_target = max(1, int(policy.get("refs_target", 2)))
        early_phase_end = max(1, int(policy.get("novelty_phase_early_end", 5)))
        mid_phase_end = max(early_phase_end + 1, int(policy.get("novelty_phase_mid_end", 20)))
        current_height = max(1, int(policy.get("current_height", 1)))

        fact_object = candidate.meta_m.get("fact_object", {})
        fact_ok, fact_reason = self._fact_object_valid(fact_object) if isinstance(fact_object, dict) else (False, "fact_object missing")

        canonical_fact = self._canonical_fact_text_from_object(fact_object if isinstance(fact_object, dict) else {})
        sim_fact = max((semantic_similarity(canonical_fact, prev, self.llm) for prev in recent_fact_texts), default=0.0)
        novel_fact = max(0.0, min(1.0, 1.0 - sim_fact))

        fact_type = str((fact_object or {}).get("type", "")).strip() if isinstance(fact_object, dict) else ""
        last_types = recent_fact_types[-type_memory_window:] if recent_fact_types else []
        novel_type = 1.0 if fact_type and fact_type not in last_types else 0.0

        references = []
        if isinstance(fact_object, dict) and isinstance(fact_object.get("references"), list):
            references = [str(x).strip() for x in fact_object.get("references", []) if str(x).strip()]
        valid_references = [r for r in dict.fromkeys(references) if r in active_anchor_ids]
        refs_count = len(valid_references)
        refs_quality = 0.0
        for ref_id in valid_references:
            ref_height = fact_height_by_id.get(ref_id, current_height)
            age = max(0, current_height - int(ref_height))
            refs_quality += math.exp(-refs_quality_alpha * age)
        refs_quality = min(2.0, refs_quality)
        novel_refs = min(1.0, float(refs_count) / float(refs_target))

        novelty_structural = 0.65 * novel_fact + 0.15 * novel_type + 0.20 * novel_refs
        novelty_min = novelty_min_late
        if current_height < early_phase_end:
            novelty_min = novelty_min_early
        elif current_height < mid_phase_end:
            novelty_min = novelty_min_mid

        scene = str(candidate.meta_m.get("story_bundle", {}).get("scene", "")).strip()
        max_scene_similarity = max((semantic_similarity(scene, prev, self.llm) for prev in recent_narratives), default=0.0)

        llm_novelty = self._llm_novelty_estimate(challenge, candidate, recent_narratives)
        novelty_score = novelty_structural
        if llm_novelty is not None:
            novelty_score = 0.8 * novelty_structural + 0.2 * llm_novelty

        named_count = 1 if isinstance(fact_object, dict) and str(fact_object.get("id", "")).strip() else 0
        unique_new = 1 if named_count and sim_fact < hard_fact_similarity_threshold else 0
        commitment_count = 1 if fact_type == "agent_commitment" else 0
        tension_progress = float(candidate.meta_m.get("tension_progress", 0.5))

        hard_fail = False
        reasons: list[str] = []

        if not fact_ok:
            hard_fail = True
            reasons.append(f"Novelty gate failed: invalid fact_object ({fact_reason})")
        if unique_new > max_new_facts_per_step:
            hard_fail = True
            reasons.append("Novelty gate failed: too many new facts for one step")
        if novelty_score < max(self.min_novelty_score, novelty_min):
            hard_fail = True
            reasons.append("Novelty gate failed: novelty below phase threshold")
        if sim_fact > hard_fact_similarity_threshold:
            hard_fail = True
            reasons.append("Novelty gate failed: hard fact repetition threshold exceeded")
        if max_scene_similarity > scene_repeat_threshold and unique_new == 0:
            hard_fail = True
            reasons.append("Novelty gate failed: scene repeats without a new fact")
        if not str(candidate.meta_m.get("what_changed_since_previous_step", "")).strip():
            hard_fail = True
            reasons.append("Novelty gate failed: missing explicit change annotation")

        refs_min = 0
        refs_quality_min = 0.0
        if current_height >= 5:
            refs_min = min_refs_at_height_5
            refs_quality_min = refs_quality_min_height_5
        elif current_height >= 2:
            refs_min = min_refs_at_height_2
            refs_quality_min = refs_quality_min_height_2
        if (refs_count < refs_min) and (refs_quality < refs_quality_min) and len(active_anchor_ids) >= max(1, refs_min):
            hard_fail = True
            reasons.append("Novelty gate failed: reference accumulation policy violated")

        if (
            enforce_dependency_accumulation
            and challenge.difficulty.dependency_depth < dependency_target_depth
            and len(active_anchor_ids) >= required_reference_count
            and refs_count < required_reference_count
        ):
            hard_fail = True
            reasons.append("Novelty gate failed: insufficient references to prior anchors")

        if challenge.directive_type == "AgentCommitment" and commitment_count < 1:
            hard_fail = True
            reasons.append("Novelty gate failed: AgentCommitment directive requires commitment anchor")
        if self._equivalent_fact(fact_object if isinstance(fact_object, dict) else {}, recent_fact_texts):
            hard_fail = True
            reasons.append("Novelty gate failed: fact is equivalent to an existing anchor")

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
                "reference_count": float(int(refs_count)),
                "refs_quality": round(float(refs_quality), 3),
                "max_scene_similarity": round(max_scene_similarity, 3),
                "max_fact_similarity": round(sim_fact, 3),
                "novel_fact": round(novel_fact, 3),
                "novel_type": round(novel_type, 3),
                "novel_refs": round(novel_refs, 3),
                "novelty_min_threshold": round(max(self.min_novelty_score, novelty_min), 3),
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
            f"Candidate fact object: {candidate.meta_m.get('fact_object', {})}\n"
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
