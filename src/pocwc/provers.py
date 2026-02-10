from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Any

from .domain import Candidate, Challenge
from .llm import LLMAdapter


@dataclass(slots=True)
class Prover:
    prover_id: str
    style: str
    rng: random.Random
    llm: LLMAdapter | None = None
    story_language: str = "english"
    llm_temperature: float = 0.35
    llm_top_p: float = 1.0
    world_profile: dict[str, Any] | None = None

    @staticmethod
    def _fact_object_from_legacy_fact(fact: dict[str, Any], strongest: str) -> dict[str, Any]:
        return {
            "id": str(fact.get("fact_id", "")).strip(),
            "type": str(fact.get("anchor_type", "public_artifact")).strip() or "public_artifact",
            "content": (
                f"{str(fact.get('subject', '')).strip()} "
                f"{str(fact.get('predicate', '')).strip()} "
                f"{str(fact.get('object', '')).strip()}"
            ).strip(),
            "introduced_by": str(fact.get("subject", "")).strip(),
            "time": str(fact.get("time_hint", "")).strip(),
            "evidence": [str(fact.get("evidence_type", "")).strip()] if str(fact.get("evidence_type", "")).strip() else [],
            "interpretation_affinity": {
                "I1": 0.2 if strongest != "I1" else 0.6,
                "I2": 0.2 if strongest != "I2" else 0.6,
                "I3": 0.2 if strongest != "I3" else 0.6,
            },
            "references": list(fact.get("references", [])) if isinstance(fact.get("references", []), list) else [],
        }

    @staticmethod
    def _ensure_fact_object(bundle: dict[str, Any], strongest: str) -> None:
        fact_obj = bundle.get("fact_object")
        if isinstance(fact_obj, dict) and str(fact_obj.get("id", "")).strip():
            return
        facts = bundle.get("novel_facts", [])
        if isinstance(facts, list) and facts and isinstance(facts[0], dict):
            bundle["fact_object"] = Prover._fact_object_from_legacy_fact(facts[0], strongest)

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

        bundle = self._fallback_bundle(challenge, strengths)
        artifact = self._bundle_to_artifact(bundle)
        meta = self._bundle_to_meta(bundle, strengths)
        meta["story_language_requested"] = self.story_language
        meta["story_generation_source"] = "fallback"
        meta["llm_used"] = False

        if self.llm is not None:
            llm_payload, llm_error = self._generate_with_llm(challenge, strengths)
            if llm_error:
                meta["llm_error"] = llm_error
            if llm_payload is not None:
                llm_bundle = llm_payload.get("bundle", bundle)
                bundle = llm_bundle if isinstance(llm_bundle, dict) else bundle
                novel_facts = llm_payload.get("novel_facts")
                if isinstance(novel_facts, list):
                    bundle["novel_facts"] = novel_facts
                fact_object = llm_payload.get("fact_object")
                if isinstance(fact_object, dict):
                    bundle["fact_object"] = fact_object
                bundle["what_changed_since_previous_step"] = str(
                    llm_payload.get("what_changed_since_previous_step", bundle.get("what_changed_since_previous_step", ""))
                )
                bundle["why_not_rephrase"] = str(llm_payload.get("why_not_rephrase", bundle.get("why_not_rephrase", "")))
                try:
                    bundle["tension_progress"] = float(llm_payload.get("tension_progress", bundle.get("tension_progress", 0.5)))
                except (TypeError, ValueError):
                    bundle["tension_progress"] = float(bundle.get("tension_progress", 0.5))
                llm_artifact = str(llm_payload.get("artifact_x", "")).strip()
                rebuilt_artifact = self._bundle_to_artifact(bundle)
                if self._is_informative_artifact(llm_artifact):
                    artifact = llm_artifact
                    source = "llm"
                elif self._is_informative_artifact(rebuilt_artifact):
                    artifact = rebuilt_artifact
                    source = "llm_bundle_rebuilt"
                    meta["llm_artifact_rejected"] = "placeholder_or_too_short"
                else:
                    source = "fallback"
                    meta["llm_artifact_rejected"] = "placeholder_or_too_short"
                meta = self._bundle_to_meta(bundle, strengths)
                meta["story_language_requested"] = self.story_language
                meta["story_generation_source"] = source
                meta["llm_used"] = source.startswith("llm")
                if llm_error:
                    meta["llm_error"] = llm_error
        self._ensure_fact_object(bundle, max(strengths, key=strengths.get))
        if isinstance(bundle.get("fact_object"), dict):
            meta["fact_object"] = bundle["fact_object"]

        return Candidate(
            candidate_id=f"{challenge.challenge_id}-cand-{ordinal}",
            challenge_id=challenge.challenge_id,
            prover_id=self.prover_id,
            artifact_x=artifact,
            meta_m=meta,
        )

    def _fallback_bundle(self, challenge: Challenge, strengths: dict[str, float]) -> dict[str, Any]:
        strongest = max(strengths, key=strengths.get)
        profile = self.world_profile or {}
        scene_templates = list(profile.get("scene_templates", []))
        event_templates = list(profile.get("event_templates", []))
        alternatives = list(profile.get("alternative_compatibility", []))
        social_effect = str(profile.get("social_effect", ""))
        deferred_tension = str(profile.get("deferred_tension", ""))
        if scene_templates and event_templates:
            scene = f"{self.rng.choice(scene_templates)} {self.rng.choice(event_templates)}"
        elif scene_templates:
            scene = self.rng.choice(scene_templates)
        else:
            scene = f"A new event is observed under directive {challenge.directive_type}."
        if not alternatives:
            alternatives = ["At least one competing interpretation remains plausible."]
        if not social_effect:
            social_effect = "Public coordination shifts while interpretation certainty remains unresolved."
        if not deferred_tension:
            deferred_tension = "The accepted update preserves unresolved interpretive tension."

        fact_subject_pool = list(profile.get("fact_subjects", [])) or ["Observer", "Council", "Archive", "Courier"]
        fact_location_pool = list(profile.get("fact_locations", [])) or ["north district", "river checkpoint", "central depot"]
        fact_time_pool = list(profile.get("fact_time_hints", [])) or ["dawn", "midnight", "late evening"]
        fact_predicates = list(profile.get("fact_predicates", [])) or ["reported", "released", "discovered", "reclassified"]
        fact_objects = list(profile.get("fact_objects", [])) or ["a document", "an artifact", "a log discrepancy", "a sealed record"]

        active_anchor_ids = [str(x) for x in challenge.verifier_policy.get("active_anchor_ids", []) if str(x).strip()]
        last_fact_ids = [str(x) for x in challenge.verifier_policy.get("last_fact_ids", []) if str(x).strip()]
        anchor_pool = last_fact_ids or active_anchor_ids
        max_refs = int(challenge.verifier_policy.get("required_reference_count", 2))
        references = anchor_pool[-max_refs:] if anchor_pool else []
        if anchor_pool and not references:
            references = [anchor_pool[-1]]
        if challenge.verifier_policy.get("escape_mode") and active_anchor_ids and not references:
            references = [active_anchor_ids[-1]]

        anchor_type = "public_artifact"
        if challenge.directive_type == "AgentCommitment":
            anchor_type = "agent_commitment"

        primary_fact = {
            "fact_id": f"{challenge.challenge_id}-f1-{self.prover_id[-4:]}",
            "anchor_type": anchor_type,
            "subject": self.rng.choice(fact_subject_pool),
            "predicate": self.rng.choice(fact_predicates),
            "object": self.rng.choice(fact_objects),
            "time_hint": self.rng.choice(fact_time_pool),
            "location_hint": self.rng.choice(fact_location_pool),
            "evidence_type": "report",
            "falsifiable": True,
            "can_be_reinterpreted": True,
            "references": references,
        }
        if anchor_type == "agent_commitment":
            primary_fact["predicate"] = "commits_publicly"
            primary_fact["object"] = f"a verifiable claim aligned with interpretation {strongest}"

        fact_object = {
            "id": primary_fact["fact_id"],
            "type": anchor_type,
            "content": f"{primary_fact['subject']} {primary_fact['predicate']} {primary_fact['object']}",
            "introduced_by": primary_fact["subject"],
            "time": primary_fact["time_hint"],
            "evidence": [f"{primary_fact['evidence_type']} observed at {primary_fact['location_hint']}"],
            "interpretation_affinity": {
                "I1": 0.2 if strongest != "I1" else 0.6,
                "I2": 0.2 if strongest != "I2" else 0.6,
                "I3": 0.2 if strongest != "I3" else 0.6,
            },
            "references": references,
        }

        return {
            "scene": (
                f"{scene} Witnesses agree on the event itself but differ on where and when the key artifact was discovered. "
                f"Directive pressure: {challenge.directive_type}."
            ),
            "surface_confirmation": (
                f"The immediate public reaction frames the discrepancy as confirmation of interpretation {strongest}."
            ),
            "alternative_compatibility": alternatives[:4],
            "social_effect": social_effect,
            "deferred_tension": deferred_tension,
            "novel_facts": [primary_fact],
            "fact_object": fact_object,
            "what_changed_since_previous_step": f"A new anchor-backed fact was introduced under {challenge.directive_type}.",
            "why_not_rephrase": "The new step adds a uniquely identified anchor and explicit references to prior anchors.",
            "tension_progress": round(min(1.0, 0.45 + self.rng.uniform(0.05, 0.3)), 3),
        }

    @staticmethod
    def _bundle_to_artifact(bundle: dict[str, Any]) -> str:
        alternatives = bundle.get("alternative_compatibility", [])
        alt_lines = "\n".join(f"- {item}" for item in alternatives[:2])
        return (
            f"Scene: {bundle.get('scene', '')}\n\n"
            f"Surface confirmation: {bundle.get('surface_confirmation', '')}\n\n"
            f"Alternative compatibility:\n{alt_lines}\n\n"
            f"Social effect: {bundle.get('social_effect', '')}\n\n"
            f"Deferred tension: {bundle.get('deferred_tension', '')}"
        )

    @staticmethod
    def _bundle_to_meta(bundle: dict[str, Any], strengths: dict[str, float]) -> dict[str, Any]:
        claims = [
            "The observed development appears convergent at first glance.",
            "Competing interpretations remain plausible under deeper reading.",
        ]
        alternatives = bundle.get("alternative_compatibility", [])
        if isinstance(alternatives, list):
            claims.extend(str(item) for item in alternatives[:2])
        facts = bundle.get("novel_facts", []) if isinstance(bundle.get("novel_facts", []), list) else []
        entities = sorted(
            {
                str(f.get("subject", "")).strip()
                for f in facts
                if isinstance(f, dict) and str(f.get("subject", "")).strip()
            }
        )
        return {
            "claims": claims,
            "threads": [
                str(bundle.get("deferred_tension", "")),
                "How social pressure modifies perceived certainty.",
            ],
            "entities": entities,
            "interpretation_strength": strengths,
            "closure_risk_hint": round(max(strengths.values()) - min(strengths.values()), 3),
            "story_bundle": bundle,
            "novel_facts": facts,
            "fact_object": bundle.get("fact_object", {}),
            "what_changed_since_previous_step": str(bundle.get("what_changed_since_previous_step", "")),
            "why_not_rephrase": str(bundle.get("why_not_rephrase", "")),
            "tension_progress": float(bundle.get("tension_progress", 0.5)),
        }

    @staticmethod
    def _is_informative_artifact(text: str) -> bool:
        normalized = " ".join(text.split())
        if len(normalized) < 80:
            return False
        if len(normalized.split()) < 12:
            return False
        lowered = normalized.lower()
        placeholder_pattern = re.compile(
            r"^(artifact[\s_\-]*x|артефакт[\s_\-]*х|артефакт[\s_\-]*x|placeholder|tbd|todo|n/?a)$"
        )
        if placeholder_pattern.match(lowered):
            return False
        if lowered in {"artifact_x", "артефакт_х", "артефакт_x"}:
            return False
        return True

    def _generate_with_llm(self, challenge: Challenge, strengths: dict[str, float]) -> tuple[dict[str, Any] | None, str | None]:
        escape_mode = bool(challenge.verifier_policy.get("escape_mode", False))
        system = (
            "You generate PoCWC world continuations. Output valid JSON only. "
            "Do not reveal final truth."
        )
        prompt = (
            "Return JSON with keys: artifact_x (string), bundle (object with keys "
            "scene, surface_confirmation, alternative_compatibility[list], social_effect, deferred_tension), "
            "fact_object (object with id,type,content,introduced_by,time,evidence[list],interpretation_affinity,references), "
            "novel_facts (list with exactly one object containing fact_id,anchor_type,subject,predicate,object,time_hint,location_hint,evidence_type,falsifiable,can_be_reinterpreted,references[list]), "
            "what_changed_since_previous_step (string), why_not_rephrase (string), tension_progress (float 0..1). "
            f"Directive: {challenge.directive_type}. Style: {self.style}. "
            f"Projection: {challenge.projection}\n"
            f"Interpretation strengths seed: {strengths}\n"
            f"Language requirement: produce all narrative text in {self.story_language}.\n"
            "Constraints: preserve at least two plausible alternatives and increase semantic tension without closure. "
            "Use one clearly named new fact only. Include references to prior anchor IDs when available. "
            f"Available prior fact IDs: {challenge.verifier_policy.get('last_fact_ids', [])}\n"
            "For AgentCommitment directive, set anchor_type=agent_commitment and produce a public commitment statement."
        )
        if escape_mode:
            prompt += (
                " Escape mode is active: return strict concrete output. "
                "fact_object.content must be 1-2 concrete sentences, avoid atmospheric abstractions, "
                "include at least one observable consequence in fact_object.evidence, "
                "and if prior anchors are available include at least one reference id."
            )
        temp = self.llm_temperature + max(0.0, challenge.difficulty.novelty_budget - 0.5) * 0.4
        if challenge.directive_type in {
            "IntroduceAmbiguousFact",
            "AgentActionDivergence",
            "DelayedConsequence",
            "AgentCommitment",
        }:
            temp += 0.08
        if escape_mode:
            temp = min(temp, 0.55)
        try:
            payload = self.llm.generate_json(
                system_prompt=system,
                user_prompt=prompt,
                temperature=max(0.0, min(1.2, temp)),
                top_p=self.llm_top_p,
                max_tokens=1000,
            )
        except Exception:  # noqa: BLE001
            return None, "llm_request_failed"
        if not isinstance(payload, dict):
            return None, "llm_payload_not_object"
        return payload, None


def default_provers(
    rng: random.Random,
    llm: LLMAdapter | None = None,
    story_language: str = "english",
    llm_temperature: float = 0.35,
    llm_top_p: float = 1.0,
    world_profile: dict[str, Any] | None = None,
) -> list[Prover]:
    return [
        Prover("prover-conservative", "conservative", rng, llm, story_language, llm_temperature, llm_top_p, world_profile),
        Prover("prover-aggressive", "aggressive", rng, llm, story_language, llm_temperature, llm_top_p, world_profile),
        Prover("prover-maintenance", "maintenance", rng, llm, story_language, llm_temperature, llm_top_p, world_profile),
    ]
