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

        return Candidate(
            candidate_id=f"{challenge.challenge_id}-cand-{ordinal}",
            challenge_id=challenge.challenge_id,
            prover_id=self.prover_id,
            artifact_x=artifact,
            meta_m=meta,
        )

    def _fallback_bundle(self, challenge: Challenge, strengths: dict[str, float]) -> dict[str, Any]:
        strongest = max(strengths, key=strengths.get)
        scene_templates = [
            "Alice notices another discrepancy in records that should have remained stable.",
            "Alice observes a new contradiction between witness logs and municipal archives.",
            "Alice receives a field report that conflicts with the official timeline.",
            "Alice traces a fresh mismatch across two agencies that should share the same source data.",
        ]
        event_templates = [
            "A courier delivers an annotated map from the old transit office at dawn.",
            "A maintenance team finds a sealed container near the river checkpoint at midnight.",
            "A council aide releases a timestamped memo from the northern district archive.",
            "A volunteer scanner uncovers a mislabeled evidence card in the central depot.",
        ]
        profile = self.world_profile or {}
        scene_templates = list(profile.get("scene_templates", scene_templates)) or scene_templates
        event_templates = list(profile.get("event_templates", event_templates)) or event_templates
        alternatives = list(
            profile.get(
                "alternative_compatibility",
                [
                    "A process-trace explanation preserves uncertainty by attributing confidence to archival workflow noise.",
                    "A social-belief explanation preserves uncertainty by showing group incentives can mimic evidence.",
                ],
            )
        )
        social_effect = str(
            profile.get(
                "social_effect",
                "Communities split between evidence-first and interpretation-first responses, increasing coordination friction.",
            )
        )
        deferred_tension = str(
            profile.get(
                "deferred_tension",
                "The world gains a new unresolved thread: should trust attach to the discovered artifact or to the discovery process?",
            )
        )
        scene = f"{self.rng.choice(scene_templates)} {self.rng.choice(event_templates)}"
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
        return {
            "claims": claims,
            "threads": [
                str(bundle.get("deferred_tension", "")),
                "How social pressure modifies perceived certainty.",
            ],
            "interpretation_strength": strengths,
            "closure_risk_hint": round(max(strengths.values()) - min(strengths.values()), 3),
            "story_bundle": bundle,
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
        system = (
            "You generate PoCWC world continuations. Output valid JSON only. "
            "Do not reveal final truth."
        )
        prompt = (
            "Return JSON with keys: artifact_x (string), bundle (object with keys "
            "scene, surface_confirmation, alternative_compatibility[list], social_effect, deferred_tension). "
            f"Directive: {challenge.directive_type}. Style: {self.style}. "
            f"Projection: {challenge.projection}\n"
            f"Interpretation strengths seed: {strengths}\n"
            f"Language requirement: produce all narrative text in {self.story_language}.\n"
            "Constraints: preserve at least two plausible alternatives and increase semantic tension without closure.\n"
            "Must include one concrete new event for this step (actor + action + place/time cue), and avoid reusing the exact previous scene wording."
        )
        temp = self.llm_temperature + max(0.0, challenge.difficulty.novelty_budget - 0.5) * 0.4
        if challenge.directive_type in {"IntroduceAmbiguousFact", "AgentActionDivergence", "DelayedEffect"}:
            temp += 0.08
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
