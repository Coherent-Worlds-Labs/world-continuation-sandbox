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
    parser.add_argument("--llm-provider", default=None, help="LLM provider (none|openrouter)")
    parser.add_argument("--llm-model", default=None, help="LLM model id for provider")
    parser.add_argument("--llm-base-url", default=None, help="Override provider base URL")
    parser.add_argument("--story-language", default="english", help="Requested story generation language")
    args = parser.parse_args()

    engine = SimulationEngine(
        SimulationConfig(
            db_path=args.db,
            steps=args.steps,
            seed=args.seed,
            llm_provider=args.llm_provider,
            llm_model=args.llm_model,
            llm_base_url=args.llm_base_url,
            story_language=args.story_language,
        )
    )
    summary = engine.run(args.steps)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
