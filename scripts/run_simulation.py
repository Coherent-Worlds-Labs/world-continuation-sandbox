from __future__ import annotations

import argparse
import json
from pathlib import Path

from pocwc.orchestrator import SimulationConfig, SimulationEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PoCWC simulation")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--db", type=Path, default=Path("data/world.db"))
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    engine = SimulationEngine(SimulationConfig(db_path=args.db, steps=args.steps, seed=args.seed))
    summary = engine.run(args.steps)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
