from __future__ import annotations

import unittest
from pathlib import Path

from pocwc.domain import VerificationLevel, VerificationResult, Verdict
from pocwc.orchestrator import SimulationConfig, SimulationEngine


class _AlwaysRejectVerifier:
    verifier_id = "verifier-always-reject"

    def evaluate(self, challenge, candidate, allow_l3=False):  # noqa: ANN001
        _ = challenge, candidate, allow_l3
        return VerificationResult(
            candidate_id="stub",
            verifier_id=self.verifier_id,
            level_max_reached=VerificationLevel.L2,
            verdict=Verdict.REJECT,
            score=0.72,
            signals={
                "closure_risk": 0.3,
                "chaos_risk": 0.3,
                "fragility_score": 0.3,
                "novelty_score": 0.72,
                "new_fact_count": 1.0,
                "reference_count": 0.0,
                "progress_gate": 0.0,
                "tension_progress": 0.5,
            },
            notes="Novelty gate failed: forced rejection for test",
        )


class Fix4StateCommitTests(unittest.TestCase):
    def test_no_threshold_relaxation_accept_bypass(self) -> None:
        db = Path("data/test_world_fix4_reject.db")
        if db.exists():
            db.unlink()
        engine = SimulationEngine(SimulationConfig(db_path=db, steps=1, seed=31))
        engine.verifiers = [_AlwaysRejectVerifier(), _AlwaysRejectVerifier(), _AlwaysRejectVerifier()]

        summary = engine.run(1)

        self.assertEqual(summary["attempted_challenges"], 1)
        self.assertEqual(summary["accepted_candidates"], 0)
        self.assertEqual(summary["rejected_candidates"], 1)

    def test_duplicate_fact_id_is_not_rewritten_on_commit(self) -> None:
        db = Path("data/test_world_fix4_fact_ids.db")
        if db.exists():
            db.unlink()
        engine = SimulationEngine(SimulationConfig(db_path=db, steps=1, seed=32))
        engine._seed_genesis()

        repeated_fact = {
            "fact_id": "F_REPEAT",
            "anchor_type": "public_artifact",
            "subject": "Archive auditor",
            "predicate": "publishes",
            "object": "a discrepancy bulletin",
            "time_hint": "dawn",
            "location_hint": "north archive wing",
            "evidence_type": "report",
            "falsifiable": True,
            "can_be_reinterpreted": True,
            "references": [],
        }

        engine._record_branch_facts(
            branch_id="branch-main",
            state_id="state-a",
            state_height=1,
            facts=[repeated_fact],
            fact_object={},
        )
        engine._record_branch_facts(
            branch_id="branch-main",
            state_id="state-b",
            state_height=2,
            facts=[repeated_fact],
            fact_object={},
        )

        active = engine.store.list_active_facts("branch-main", limit=20)
        ids = [str(row.get("fact_id", "")) for row in active]

        self.assertEqual(len(ids), 1)
        self.assertEqual(ids[0], "F_REPEAT")


if __name__ == "__main__":
    unittest.main()
