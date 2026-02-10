from __future__ import annotations

import json
import unittest
from pathlib import Path

from pocwc.orchestrator import SimulationConfig, SimulationEngine


class SimulationTests(unittest.TestCase):
    def test_run_50_steps_and_forks(self) -> None:
        db = Path("data/test_world_a.db")
        if db.exists():
            db.unlink()
        engine = SimulationEngine(SimulationConfig(db_path=db, steps=50, seed=11))
        summary = engine.run(50)

        self.assertGreaterEqual(summary["attempted_challenges"], 50)
        self.assertGreaterEqual(summary["branches"], 2)
        self.assertIn("L0", summary["reject_by_level"])
        self.assertIn("L2", summary["reject_by_level"])

    def test_state_progression(self) -> None:
        db = Path("data/test_world_b.db")
        if db.exists():
            db.unlink()
        engine = SimulationEngine(SimulationConfig(db_path=db, steps=15, seed=21))
        engine.run(15)
        states = engine.store.list_states(branch_id="branch-main")

        heights = [s["height"] for s in states]
        self.assertEqual(heights[0], 0)
        self.assertEqual(heights, sorted(heights))

    def test_controller_epoch_records(self) -> None:
        db = Path("data/test_world_c.db")
        if db.exists():
            db.unlink()
        engine = SimulationEngine(SimulationConfig(db_path=db, steps=12, seed=3, epoch=3))
        engine.run(12)

        epoch = engine.store.latest_epoch()
        self.assertIsNotNone(epoch)
        self.assertIn(epoch["mode"], {"diversify", "consolidate", "maintenance", "false-convergence", "deferred-tension"})

    def test_progress_reports_similarity_and_trace_penalties(self) -> None:
        db = Path("data/test_world_similarity_metrics.db")
        if db.exists():
            db.unlink()
        engine = SimulationEngine(SimulationConfig(db_path=db, steps=4, seed=13))
        updates: list[dict] = []
        engine.run(4, progress_callback=updates.append)

        self.assertGreaterEqual(len(updates), 1)
        for update in updates:
            self.assertIn("step_similarity", update)
            self.assertIn("candidate_traces", update)
            self.assertIn("new_fact_count", update)
            self.assertIn("novel_fact_ratio", update)
            self.assertIn("semantic_delta_score", update)
            self.assertIn("stagnation_streak", update)
            self.assertIn("ontological_stagnation", update)
            self.assertIn("active_anchor_count", update)
            self.assertGreaterEqual(float(update["step_similarity"]), 0.0)
            self.assertLessEqual(float(update["step_similarity"]), 1.0)
            self.assertEqual(int(update["new_fact_count"]), float(update["new_fact_count"]))
            traces = update["candidate_traces"]
            self.assertGreaterEqual(len(traces), 1)
            for trace in traces:
                self.assertIn("similarity", trace)
                self.assertIn("penalty", trace)
                self.assertIn("new_fact_count", trace)
                self.assertIn("progress_gate", trace)
                self.assertIn("novelty_score", trace)
                self.assertEqual(int(trace["new_fact_count"]), float(trace["new_fact_count"]))

    def test_directive_repetition_is_bounded(self) -> None:
        db = Path("data/test_world_directive_repetition.db")
        if db.exists():
            db.unlink()
        engine = SimulationEngine(SimulationConfig(db_path=db, steps=30, seed=4))
        engine.run(30)
        directives = [row["directive_type"] for row in engine.store.list_challenges(branch_id="branch-main")]
        streak = 1
        for idx in range(1, len(directives)):
            if directives[idx] == directives[idx - 1]:
                streak += 1
            else:
                streak = 1
            self.assertLessEqual(streak, 2)

    def test_branch_fact_registry_populates(self) -> None:
        db = Path("data/test_world_fact_registry.db")
        if db.exists():
            db.unlink()
        engine = SimulationEngine(SimulationConfig(db_path=db, steps=3, seed=12))
        engine.run(3)
        facts = engine.store.list_branch_facts("branch-main", limit=50)
        self.assertGreaterEqual(len(facts), 1)
        active_facts = engine.store.list_active_facts("branch-main", limit=50)
        self.assertGreaterEqual(len(active_facts), 1)
        self.assertIn("anchor_type", active_facts[0])
        self.assertIn("references", active_facts[0])
        self.assertIn("introduced_height", active_facts[0])

    def test_custom_world_config_overrides_genesis(self) -> None:
        db = Path("data/test_world_custom_config.db")
        cfg = Path("data/test_world_custom_config.json")
        if db.exists():
            db.unlink()
        if cfg.exists():
            cfg.unlink()

        cfg.write_text(
            json.dumps(
                {
                    "anchor_character": "Morgan",
                    "main_branch_id": "branch-custom",
                    "genesis": {
                        "state_id": "state-custom-0",
                        "story_bundle": {
                            "scene": "Morgan starts from a fragmented harbor city timeline."
                        },
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        engine = SimulationEngine(SimulationConfig(db_path=db, steps=1, seed=5, world_config_path=cfg))
        snap = engine.get_genesis_snapshot()
        self.assertEqual(snap["branch_id"], "branch-custom")
        self.assertEqual(snap["genesis_state_id"], "state-custom-0")
        self.assertIn("Morgan", snap["scene"])

    def test_controller_reports_ontological_stagnation(self) -> None:
        db = Path("data/test_world_controller_ontology.db")
        if db.exists():
            db.unlink()
        engine = SimulationEngine(SimulationConfig(db_path=db, steps=8, seed=6))
        summary = engine.run(8)
        self.assertIn("controller", summary)
        self.assertIn("ontological_stagnation", summary["controller"])


if __name__ == "__main__":
    unittest.main()
