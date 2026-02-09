from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
