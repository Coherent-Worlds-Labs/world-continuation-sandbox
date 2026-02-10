from __future__ import annotations

import random
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

        bundle = self._fallback_bundle(strengths)
        artifact = self._bundle_to_artifact(bundle)
        meta = self._bundle_to_meta(bundle, strengths)
        meta["story_language_requested"] = self.story_language

        if self.llm is not None:
            llm_payload = self._generate_with_llm(challenge, strengths)
            if llm_payload is not None:
                artifact = str(llm_payload.get("artifact_x", artifact))
                llm_bundle = llm_payload.get("bundle", bundle)
                bundle = llm_bundle if isinstance(llm_bundle, dict) else bundle
                meta = self._bundle_to_meta(bundle, strengths)
                meta["story_language_requested"] = self.story_language

        return Candidate(
            candidate_id=f"{challenge.challenge_id}-cand-{ordinal}",
            challenge_id=challenge.challenge_id,
            prover_id=self.prover_id,
            artifact_x=artifact,
            meta_m=meta,
        )

    @staticmethod
    def _fallback_bundle(strengths: dict[str, float]) -> dict[str, Any]:
        strongest = max(strengths, key=strengths.get)
        return {
            "scene": (
                "Alice notices another discrepancy in records that should have remained stable. "
                "Witnesses agree on the event itself but differ on where and when the key artifact was discovered."
            ),
            "surface_confirmation": (
                f"The immediate public reaction frames the discrepancy as confirmation of interpretation {strongest}."
            ),
            "alternative_compatibility": [
                "A process-trace explanation preserves uncertainty by attributing confidence to archival workflow noise.",
                "A social-belief explanation preserves uncertainty by showing group incentives can mimic evidence.",
            ],
            "social_effect": (
                "Communities split between evidence-first and interpretation-first responses, increasing coordination friction."
            ),
            "deferred_tension": (
                "The world gains a new unresolved thread: should trust attach to the discovered artifact or to the discovery process?"
            ),
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

    def _generate_with_llm(self, challenge: Challenge, strengths: dict[str, float]) -> dict[str, Any] | None:
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
            "Constraints: preserve at least two plausible alternatives and increase semantic tension without closure."
        )
        try:
            payload = self.llm.generate_json(system_prompt=system, user_prompt=prompt, temperature=0.35, max_tokens=1000)
        except Exception:  # noqa: BLE001
            return None
        return payload if isinstance(payload, dict) else None


def default_provers(rng: random.Random, llm: LLMAdapter | None = None, story_language: str = "english") -> list[Prover]:
    return [
        Prover("prover-conservative", "conservative", rng, llm, story_language),
        Prover("prover-aggressive", "aggressive", rng, llm, story_language),
        Prover("prover-maintenance", "maintenance", rng, llm, story_language),
    ]
