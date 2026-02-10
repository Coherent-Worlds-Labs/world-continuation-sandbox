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
            self.assertGreaterEqual(float(update["step_similarity"]), 0.0)
            self.assertLessEqual(float(update["step_similarity"]), 1.0)
            traces = update["candidate_traces"]
            self.assertGreaterEqual(len(traces), 1)
            for trace in traces:
                self.assertIn("similarity", trace)
                self.assertIn("penalty", trace)

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


if __name__ == "__main__":
    unittest.main()
