from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from pocwc.orchestrator import SimulationConfig, SimulationEngine


def _style(label: str, value: str, *, color: str = "36") -> str:
    return f"\033[{color}m{label}\033[0m {value}"


def _render_progress(update: dict) -> None:
    step = int(update["step"])
    total = int(update["total_steps"])
    branch = str(update["branch_id"])
    accepted = int(update["accepted"])
    rejected = int(update["rejected"])
    forks = int(update["forks"])
    debt = float(update["debt"])
    variance = float(update["variance"])
    mode = str(update["mode"])
    theta = float(update["theta"])
    scene = str(update.get("scene") or "")
    artifact = str(update.get("artifact") or "")
    tension = str(update.get("deferred_tension") or "")

    narrative = scene if scene else artifact
    narrative = " ".join(narrative.split())
    narrative_preview = textwrap.shorten(narrative, width=112, placeholder=" ...")
    tension_preview = textwrap.shorten(" ".join(tension.split()), width=88, placeholder=" ...")

    print(
        f"\n\033[1;34m=== Step {step}/{total} ===\033[0m "
        f"{_style('branch:', branch, color='35')} "
        f"{_style('mode:', mode, color='33')} "
        f"{_style('theta:', f'{theta:.2f}', color='33')}"
    )
    print(
        f"{_style('world:', f'debt={debt:.3f}  variance={variance:.4f}  forks={forks}', color='32')} "
        f"{_style('ledger:', f'accepted={accepted} rejected={rejected}', color='32')}"
    )
    print(_style("narrative:", narrative_preview if narrative_preview else "(no narrative available)", color="36"))
    if tension_preview:
        print(_style("tension:", tension_preview, color="31"))


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
    summary = engine.run(args.steps, progress_callback=_render_progress)
    print("\n\033[1;32m=== Final Summary ===\033[0m")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
