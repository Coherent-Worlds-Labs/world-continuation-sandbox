from __future__ import annotations

import random
import unittest

from pocwc.aggregation import Aggregator
from pocwc.domain import Candidate, Challenge, Difficulty, VerificationLevel, VerificationResult, Verdict
from pocwc.verifiers import NoveltyGateVerifier


class Fix2ConstraintTests(unittest.TestCase):
    def _challenge(self, **policy_overrides):
        policy = {
            "recent_fact_texts": [
                "public_artifact | City clerk | publishes | a sworn public claim | dawn | north archive wing"
            ],
            "recent_narratives": ["A baseline narrative scene."],
            "active_anchor_ids": ["F_PREV_1", "F_PREV_2"],
            "required_min_new_facts": 1,
            "max_new_facts_per_step": 1,
            "dependency_target_depth": 4,
            "required_reference_count": 1,
            "enforce_dependency_accumulation": True,
            "current_height": 3,
            "hard_similarity_threshold": 0.92,
            "min_refs_height_1": 0,
            "min_refs_height_2": 1,
            "min_refs_height_5": 2,
            "mode": "diversify",
            "min_fact_specificity_score": 3,
            "fact_specificity_required_types": ["public_artifact", "measurement", "institutional_action"],
            "specificity_places": ["archive", "district", "checkpoint", "wing", "desk"],
            "specificity_artifacts": ["document", "map", "record", "registry", "memo", "card"],
            "specificity_banned_terms": ["something", "some", "perhaps", "unknown"],
            "max_same_fact_type_diversify": 2,
            "fact_type_enum": ["public_artifact", "witness", "measurement", "institutional_action", "resource_change", "agent_commitment"],
            "public_artifact_min_evidence": 2,
            "directive_fact_type_contracts": {
                "IntroduceAmbiguousFact": "public_artifact",
                "InstitutionalAction": "institutional_action",
                "AgentCommitment": "agent_commitment",
                "ResourceConstraint": "resource_change",
            },
        }
        policy.update(policy_overrides)
        return Challenge(
            challenge_id="c1",
            branch_id="branch-main",
            parent_state_id="s0",
            projection="projection",
            directive_type="IntroduceAmbiguousFact",
            difficulty=Difficulty(),
            verifier_policy=policy,
        )

    def _candidate(self, **overrides):
        fact = {
            "fact_id": "F_NEW_1",
            "anchor_type": "public_artifact",
            "subject": "City clerk",
            "predicate": "publishes",
            "object": "a timestamped registry copy",
            "time_hint": "midday",
            "location_hint": "north archive wing",
            "evidence_type": "report",
            "falsifiable": True,
            "can_be_reinterpreted": True,
            "references": ["F_PREV_1"],
        }
        fact_object = {
            "id": "F_NEW_1",
            "type": "public_artifact",
            "content": "City clerk publishes a timestamped registry copy in the public ledger.",
            "introduced_by": "City clerk",
            "time": "midday",
            "evidence": ["report from public ledger", "witness transcript in archive registry"],
            "artifact_kind": "record",
            "artifact_locator": "north archive wing",
            "artifact_identifier": "REG-221",
            "interpretation_affinity": {"I1": 0.2, "I2": 0.6, "I3": 0.2},
            "references": ["F_PREV_1"],
        }
        meta = {
            "closure_risk_hint": 0.4,
            "story_bundle": {"scene": "A clearly new scene with concrete development."},
            "novel_facts": [fact],
            "fact_object": fact_object,
            "what_changed_since_previous_step": "A concrete public artifact was published.",
            "tension_progress": 0.6,
        }
        meta.update(overrides)
        return Candidate(
            candidate_id="cand-1",
            challenge_id="c1",
            prover_id="prover-a",
            artifact_x="Artifact with concrete progress.",
            meta_m=meta,
        )

    def test_invalid_fact_object_is_rejected(self):
        verifier = NoveltyGateVerifier("verifier-novelty", random.Random(1), llm=None)
        challenge = self._challenge()
        candidate = self._candidate(fact_object={"id": ""})
        result = verifier.evaluate(challenge, candidate, allow_l3=False)
        self.assertEqual(result.verdict, Verdict.REJECT)
        self.assertIn("FACT_SCHEMA_INVALID", result.signals["reason_codes"])

    def test_reference_policy_rejects_missing_refs(self):
        verifier = NoveltyGateVerifier("verifier-novelty", random.Random(2), llm=None)
        challenge = self._challenge(current_height=5, required_reference_count=2, min_refs_height_5=2)
        fact = self._candidate().meta_m["novel_facts"][0]
        fact["references"] = []
        fact_object = self._candidate().meta_m["fact_object"]
        fact_object["references"] = []
        candidate = self._candidate(novel_facts=[fact], fact_object=fact_object)
        result = verifier.evaluate(challenge, candidate, allow_l3=False)
        self.assertEqual(result.verdict, Verdict.REJECT)
        self.assertIn("PROGRESS_GATE_FAIL", result.signals["reason_codes"])

    def test_equivalent_fact_is_rejected(self):
        verifier = NoveltyGateVerifier("verifier-novelty", random.Random(3), llm=None)
        challenge = self._challenge(
            recent_fact_texts=["public_artifact: City clerk publishes a timestamped registry copy in the public ledger. | report from public ledger ; witness transcript in archive registry"]
        )
        candidate = self._candidate()
        result = verifier.evaluate(challenge, candidate, allow_l3=False)
        self.assertEqual(result.verdict, Verdict.REJECT)
        self.assertIn("FACT_EQUIVALENT", result.signals["reason_codes"])

    def test_fact_type_outside_enum_is_rejected(self):
        verifier = NoveltyGateVerifier("verifier-novelty", random.Random(4), llm=None)
        challenge = self._challenge()
        fact_object = self._candidate().meta_m["fact_object"]
        fact_object["type"] = "unsupported_type"
        candidate = self._candidate(fact_object=fact_object)
        result = verifier.evaluate(challenge, candidate, allow_l3=False)
        self.assertEqual(result.verdict, Verdict.REJECT)
        self.assertIn("TYPE_NOT_IN_ENUM", result.signals["reason_codes"])

    def test_fact_specificity_gate_rejects_vague_content(self):
        verifier = NoveltyGateVerifier("verifier-novelty", random.Random(5), llm=None)
        challenge = self._challenge()
        fact_object = self._candidate().meta_m["fact_object"]
        fact_object["content"] = "Someone maybe found something unknown somewhere."
        fact_object["evidence"] = ["maybe log"]
        candidate = self._candidate(fact_object=fact_object)
        result = verifier.evaluate(challenge, candidate, allow_l3=False)
        self.assertEqual(result.verdict, Verdict.REJECT)
        self.assertIn("FACT_SPECIFICITY_BELOW_MIN", result.signals["reason_codes"])

    def test_public_artifact_requires_artifact_fields(self):
        verifier = NoveltyGateVerifier("verifier-novelty", random.Random(51), llm=None)
        challenge = self._challenge()
        fact_object = self._candidate().meta_m["fact_object"]
        fact_object["artifact_identifier"] = ""
        candidate = self._candidate(fact_object=fact_object)
        result = verifier.evaluate(challenge, candidate, allow_l3=False)
        self.assertEqual(result.verdict, Verdict.REJECT)
        self.assertIn("FACT_SCHEMA_INVALID", result.signals["reason_codes"])

    def test_directive_contract_fail_is_explicit(self):
        verifier = NoveltyGateVerifier("verifier-novelty", random.Random(52), llm=None)
        challenge = self._challenge(directive_fact_type_contracts={"IntroduceAmbiguousFact": "public_artifact"})
        fact_object = self._candidate().meta_m["fact_object"]
        fact_object["type"] = "agent_commitment"
        candidate = self._candidate(fact_object=fact_object)
        result = verifier.evaluate(challenge, candidate, allow_l3=False)
        self.assertEqual(result.verdict, Verdict.REJECT)
        self.assertIn("DIRECTIVE_CONTRACT_FAIL", result.signals["reason_codes"])

    def test_step_one_does_not_require_refs(self):
        verifier = NoveltyGateVerifier("verifier-novelty", random.Random(6), llm=None)
        challenge = self._challenge(
            current_height=1,
            min_refs_height_1=0,
            active_anchor_ids=[],
            recent_fact_texts=[],
            recent_narratives=[],
            min_fact_specificity_score=2,
        )
        fact_object = self._candidate().meta_m["fact_object"]
        fact_object["references"] = []
        candidate = self._candidate(fact_object=fact_object)
        result = verifier.evaluate(challenge, candidate, allow_l3=False)
        self.assertEqual(result.verdict, Verdict.ACCEPT)
        self.assertEqual(result.signals["progress_gate"], 1.0)

    def test_structural_mismatch_is_rejected(self):
        verifier = NoveltyGateVerifier("verifier-novelty", random.Random(7), llm=None)
        challenge = self._challenge()
        fact_object = self._candidate().meta_m["fact_object"]
        fact_object["id"] = "F_NEW_X"
        candidate = self._candidate(fact_object=fact_object)
        result = verifier.evaluate(challenge, candidate, allow_l3=False)
        self.assertEqual(result.verdict, Verdict.REJECT)
        self.assertIn("STRUCTURAL_INCONSISTENCY", result.signals["reason_codes"])

    def test_high_novelty_progress_fail_not_reported_as_novelty_fail(self):
        verifier = NoveltyGateVerifier("verifier-novelty", random.Random(8), llm=None)
        challenge = self._challenge(
            current_height=5,
            min_refs_height_5=2,
            required_reference_count=2,
            active_anchor_ids=["F_PREV_1", "F_PREV_2", "F_PREV_3"],
        )
        fact_object = self._candidate().meta_m["fact_object"]
        fact_object["references"] = []
        fact_object["content"] = "City clerk publishes registry card 221 in north archive wing at 09:30."
        fact_object["evidence"] = ["registry card 221 photographed in archive wing", "two witness logs reference card 221"]
        candidate = self._candidate(fact_object=fact_object)
        result = verifier.evaluate(challenge, candidate, allow_l3=False)
        self.assertEqual(result.verdict, Verdict.REJECT)
        self.assertIn("PROGRESS_GATE_FAIL", result.signals["reason_codes"])
        self.assertNotIn("NOVELTY_BELOW_MIN", result.signals["reason_codes"])

    def test_aggregator_hard_progress_gate(self):
        agg = Aggregator()
        results = [
            VerificationResult("cand-1", "v1", VerificationLevel.L2, Verdict.ACCEPT, 0.9, {"closure_risk": 0.2, "chaos_risk": 0.2, "fragility_score": 0.2}, ""),
            VerificationResult("cand-1", "v2", VerificationLevel.L2, Verdict.ACCEPT, 0.88, {"closure_risk": 0.2, "chaos_risk": 0.2, "fragility_score": 0.2}, ""),
            VerificationResult("cand-1", "v3", VerificationLevel.L2, Verdict.ACCEPT, 0.87, {"closure_risk": 0.2, "chaos_risk": 0.2, "fragility_score": 0.2}, ""),
        ]
        decision = agg.decide(results, novelty_score=0.9, tension_progress=0.8, repetition_penalty=0.0, hard_fail=False, progress_gate=False)
        self.assertEqual(decision.verdict, Verdict.REJECT)
        self.assertIn("progress gate", "; ".join(decision.reasons))


if __name__ == "__main__":
    unittest.main()
