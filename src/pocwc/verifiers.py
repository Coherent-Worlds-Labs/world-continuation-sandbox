from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, ClassVar

from .domain import Candidate, Challenge, VerificationLevel, VerificationResult, Verdict
from .invariants import evaluate_invariants
from .llm import LLMAdapter
from .semantic import semantic_similarity
from .fact_schema import validate_and_normalize_fact_object


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
    allowed_fact_types: ClassVar[tuple[str, ...]] = (
        "public_artifact",
        "witness",
        "measurement",
        "institutional_action",
        "resource_change",
        "agent_commitment",
    )

    @staticmethod
    def _canonical_fact_id(raw: Any) -> str:
        return str(raw or "").strip().upper()

    @staticmethod
    def _canonical_fact_type(raw: Any, allowed_types: set[str]) -> str:
        text = str(raw or "").strip().lower()
        mapping = {
            "fact": "public_artifact",
            "new_fact": "public_artifact",
            "artifact": "public_artifact",
            "publicartifact": "public_artifact",
            "measurement": "measurement",
            "institution action": "institutional_action",
            "resource change": "resource_change",
            "agent commitment": "agent_commitment",
        }
        normalized = mapping.get(text, text.replace(" ", "_"))
        return normalized if normalized in allowed_types else ""

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
        fact_type = str(fact.get("type", "")).strip()
        if not fact_type:
            return False, "type is empty"
        if fact_type not in NoveltyGateVerifier.allowed_fact_types:
            return False, "type is outside allowed enum"
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

    @staticmethod
    def _fact_specificity_score(
        content: str,
        evidence_items: list[str],
        places: list[str],
        artifact_terms: list[str],
        banned_terms: list[str],
        artifact_identifier: str,
    ) -> int:
        text = content.lower()
        score = 0
        if any(ch.isdigit() for ch in content):
            score += 1
        if any(place.lower() in text for place in places):
            score += 1
        if any(term.lower() in text for term in artifact_terms):
            score += 1
        if len(evidence_items) >= 2:
            score += 1
        if artifact_identifier and any(ch.isdigit() for ch in artifact_identifier):
            score += 1
        if 80 <= len(content) <= 280:
            score += 1
        if any(term.lower() in text for term in banned_terms):
            score -= 1
        return score

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
        min_refs_at_height_1 = max(0, int(policy.get("min_refs_height_1", 0)))
        hard_refs_from_step_2 = bool(policy.get("hard_refs_from_step_2", True))
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
        mode = str(policy.get("mode", "diversify")).strip().lower()
        max_same_fact_type_diversify = max(1, int(policy.get("max_same_fact_type_diversify", 2)))
        early_phase_end = max(1, int(policy.get("novelty_phase_early_end", 5)))
        mid_phase_end = max(early_phase_end + 1, int(policy.get("novelty_phase_mid_end", 20)))
        current_height = max(1, int(policy.get("current_height", 1)))
        specificity_min = max(0, int(policy.get("min_fact_specificity_score", 3)))
        specificity_types = {
            str(x).strip()
            for x in policy.get("fact_specificity_required_types", ["public_artifact", "measurement", "institutional_action"])
            if str(x).strip()
        }
        places = [str(x).strip() for x in policy.get("specificity_places", []) if str(x).strip()]
        artifact_terms = [str(x).strip() for x in policy.get("specificity_artifacts", []) if str(x).strip()]
        banned_terms = [str(x).strip() for x in policy.get("specificity_banned_terms", []) if str(x).strip()]
        allowed_types = {
            str(x).strip()
            for x in policy.get("fact_type_enum", list(self.allowed_fact_types))
            if str(x).strip()
        } or set(self.allowed_fact_types)
        public_artifact_min_evidence = max(1, int(policy.get("public_artifact_min_evidence", 2)))
        directive_contracts = policy.get("directive_fact_type_contracts", {})
        expected_fact_type = str(policy.get("expected_fact_type", "")).strip()
        if isinstance(directive_contracts, dict):
            expected_fact_type = expected_fact_type or str(directive_contracts.get(challenge.directive_type, "")).strip()

        raw_fact_object = candidate.meta_m.get("fact_object", {})
        schema_result = validate_and_normalize_fact_object(
            raw_fact_object,
            policy,
            expected_fact_type=expected_fact_type,
            allow_coercion=bool(policy.get("allow_fact_object_coercion", False)),
        )
        fact_object = dict(schema_result.normalized)
        if isinstance(candidate.meta_m, dict):
            candidate.meta_m["fact_object"] = fact_object
        fact_ok, fact_reason = self._fact_object_valid(fact_object) if not schema_result.errors else (False, "schema validation failed")

        canonical_fact = self._canonical_fact_text_from_object(fact_object if isinstance(fact_object, dict) else {})
        sim_fact = max((semantic_similarity(canonical_fact, prev, self.llm) for prev in recent_fact_texts), default=0.0)
        novel_fact = max(0.0, min(1.0, 1.0 - sim_fact))

        raw_fact_type = str((fact_object or {}).get("type", "")).strip() if isinstance(fact_object, dict) else ""
        fact_type = self._canonical_fact_type(raw_fact_type, allowed_types)
        fact_id = self._canonical_fact_id((fact_object or {}).get("id", "")) if isinstance(fact_object, dict) else ""
        last_types = recent_fact_types[-type_memory_window:] if recent_fact_types else []
        novel_type = 1.0 if fact_type and fact_type not in last_types else 0.0

        references = []
        if isinstance(fact_object, dict) and isinstance(fact_object.get("references"), list):
            references = [str(x).strip() for x in fact_object.get("references", []) if str(x).strip()]
        evidence = fact_object.get("evidence", []) if isinstance(fact_object, dict) else []
        if isinstance(evidence, list):
            evidence_items = [str(x).strip() for x in evidence if str(x).strip()]
        else:
            evidence_items = [str(evidence).strip()] if str(evidence).strip() else []
        fact_content = str((fact_object or {}).get("content", "")).strip() if isinstance(fact_object, dict) else ""
        artifact_identifier = str((fact_object or {}).get("artifact_identifier", "")).strip() if isinstance(fact_object, dict) else ""
        fact_specificity_score = self._fact_specificity_score(
            fact_content,
            evidence_items,
            places,
            artifact_terms,
            banned_terms,
            artifact_identifier,
        )
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
        reason_codes: list[str] = []

        def fail(code: str, message: str) -> None:
            nonlocal hard_fail
            hard_fail = True
            reason_codes.append(code)
            reasons.append(message)

        # Structural consistency: fact_object and novel_facts[0] must agree after canonicalization.
        novel_facts = candidate.meta_m.get("novel_facts", [])
        if isinstance(novel_facts, list) and novel_facts and isinstance(novel_facts[0], dict):
            nf = novel_facts[0]
            nf_id = self._canonical_fact_id(nf.get("fact_id", ""))
            nf_type = self._canonical_fact_type(nf.get("anchor_type", ""), allowed_types)
            if nf_id and fact_id and nf_id != fact_id:
                fail("STRUCTURAL_INCONSISTENCY", "fact id mismatch between fact_object and novel_facts")
            if nf_type and fact_type and nf_type != fact_type:
                fail("STRUCTURAL_INCONSISTENCY", "fact type mismatch between fact_object and novel_facts")

        if not fact_ok:
            fail("FACT_SCHEMA_INVALID", f"invalid fact_object ({fact_reason})")
        if schema_result.errors:
            fail("FACT_SCHEMA_INVALID", "strict schema validation failed")
        if not fact_type:
            fail("TYPE_NOT_IN_ENUM", "fact_object.type is outside allowed enum")
        if expected_fact_type and fact_type and fact_type != expected_fact_type:
            fail("DIRECTIVE_CONTRACT_FAIL", f"directive {challenge.directive_type} expects fact_type={expected_fact_type}")
        if fact_type in specificity_types and fact_specificity_score < specificity_min:
            fail("FACT_SPECIFICITY_BELOW_MIN", "fact specificity is below minimum")
        if fact_type == "public_artifact":
            artifact_kind = str((fact_object or {}).get("artifact_kind", "")).strip() if isinstance(fact_object, dict) else ""
            artifact_locator = str((fact_object or {}).get("artifact_locator", "")).strip() if isinstance(fact_object, dict) else ""
            artifact_identifier = str((fact_object or {}).get("artifact_identifier", "")).strip() if isinstance(fact_object, dict) else ""
            artifact_hit = any(term.lower() in fact_content.lower() for term in artifact_terms) or any(
                term.lower() in " ".join(evidence_items).lower() for term in artifact_terms
            )
            if not artifact_hit:
                fail("FACT_SCHEMA_INVALID", "public_artifact is missing a concrete artifact/object signal")
            if not artifact_kind or not artifact_locator or not artifact_identifier:
                fail("FACT_SCHEMA_INVALID", "public_artifact requires artifact_kind/artifact_locator/artifact_identifier")
            if len(evidence_items) < public_artifact_min_evidence:
                fail("EVIDENCE_TOO_WEAK", "public_artifact requires stronger evidence cardinality")
        if mode == "diversify":
            same_tail = 0
            for item in reversed(last_types):
                if item == fact_type:
                    same_tail += 1
                else:
                    break
            if same_tail >= max_same_fact_type_diversify:
                fail("TYPE_STREAK_EXCEEDED", "repeated fact type exceeds diversify streak limit")
        if unique_new > max_new_facts_per_step:
            fail("TOO_MANY_NEW_FACTS", "too many new facts for one step")
        novelty_threshold = max(self.min_novelty_score, novelty_min)
        novelty_gate = novelty_score >= novelty_threshold
        if not novelty_gate:
            fail("NOVELTY_BELOW_MIN", "novelty below phase threshold")
        if sim_fact > hard_fact_similarity_threshold:
            fail("FACT_REPETITION", "hard fact repetition threshold exceeded")
        if max_scene_similarity > scene_repeat_threshold and unique_new == 0:
            fail("SCENE_STAGNATION", "scene repeats without a new fact")
        if not str(candidate.meta_m.get("what_changed_since_previous_step", "")).strip():
            fail("MISSING_CHANGE_ANNOTATION", "missing explicit change annotation")

        refs_min = 0
        refs_quality_min = 0.0
        if current_height >= 5:
            refs_min = min_refs_at_height_5
            refs_quality_min = refs_quality_min_height_5
        elif current_height >= 2:
            refs_min = min_refs_at_height_2
            refs_quality_min = refs_quality_min_height_2
        else:
            refs_min = min_refs_at_height_1
        if hard_refs_from_step_2 and current_height >= 2:
            refs_min = max(1, refs_min)
        refs_gate = True
        if (refs_count < refs_min) and (refs_quality < refs_quality_min) and len(active_anchor_ids) >= max(1, refs_min):
            refs_gate = False
            fail("PROGRESS_GATE_FAIL", "reference accumulation policy violated")

        if (
            enforce_dependency_accumulation
            and challenge.difficulty.dependency_depth < dependency_target_depth
            and len(active_anchor_ids) >= required_reference_count
            and refs_count < required_reference_count
        ):
            refs_gate = False
            fail("PROGRESS_GATE_FAIL", "insufficient references to prior anchors")

        if challenge.directive_type == "AgentCommitment" and commitment_count < 1:
            fail("DIRECTIVE_CONTRACT_FAIL", "AgentCommitment directive requires commitment anchor")
        if self._equivalent_fact(fact_object if isinstance(fact_object, dict) else {}, recent_fact_texts):
            fail("FACT_EQUIVALENT", "fact is equivalent to an existing anchor")

        progress_gate = refs_gate
        schema_gate = 0.0 if any(code in {"FACT_SCHEMA_INVALID", "TYPE_NOT_IN_ENUM", "EVIDENCE_TOO_WEAK", "STRUCTURAL_INCONSISTENCY"} for code in reason_codes) else 1.0
        evidence_gate = 0.0 if "EVIDENCE_TOO_WEAK" in reason_codes else 1.0
        consistency_gate = 0.0 if "STRUCTURAL_INCONSISTENCY" in reason_codes else 1.0

        verdict = Verdict.REJECT if hard_fail else Verdict.ACCEPT
        score = max(0.0, min(1.0, novelty_score))
        reason_codes = list(dict.fromkeys(reason_codes))
        reason_details = {
            "novelty_total": round(novelty_score, 3),
            "novelty_metric_compared": "novelty_score",
            "novelty_min": round(novelty_threshold, 3),
            "refs_min": int(refs_min),
            "refs_count": int(refs_count),
            "refs_quality": round(float(refs_quality), 3),
            "refs_quality_min": round(float(refs_quality_min), 3),
            "fact_specificity_score": int(fact_specificity_score),
            "fact_specificity_min": int(specificity_min),
            "fact_type": fact_type,
            "expected_fact_type": expected_fact_type,
            "fact_id": fact_id,
            "evidence_count": len(evidence_items),
            "artifact_identifier": artifact_identifier,
            "current_height": current_height,
            "schema_errors": list(schema_result.errors),
            "coercions": list(schema_result.coercions),
        }
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
                "novelty_min_threshold": round(novelty_threshold, 3),
                "fact_specificity_score": float(fact_specificity_score),
                "novelty_gate": 1.0 if novelty_gate else 0.0,
                "progress_gate": 1.0 if progress_gate else 0.0,
                "schema_gate": schema_gate,
                "evidence_gate": evidence_gate,
                "consistency_gate": consistency_gate,
                "tension_progress": round(tension_progress, 3),
                "reason_codes": reason_codes,
                "reason_details": reason_details,
            },
            notes=("reject: " + ", ".join(reason_codes) + " | " + "; ".join(reasons)) if reasons else "novelty gate passed",
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
