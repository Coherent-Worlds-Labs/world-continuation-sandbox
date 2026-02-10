from __future__ import annotations

import argparse
import json
from pathlib import Path

from pocwc.orchestrator import SimulationConfig, SimulationEngine


def _style(label: str, value: str, *, color: str = "36") -> str:
    return f"\033[{color}m{label}\033[0m {value}"


def _render_genesis(snapshot: dict) -> None:
    entities = ", ".join(str(x) for x in snapshot.get("entities", [])) or "-"
    threads = ", ".join(str(x) for x in snapshot.get("threads", [])) or "-"
    interpretation = snapshot.get("interpretation_strength", {})
    interpretation_line = (
        ", ".join(f"{k}={float(v):.2f}" for k, v in interpretation.items()) if interpretation else "-"
    )
    scene = " ".join(str(snapshot.get("scene") or "").split())
    tension = " ".join(str(snapshot.get("deferred_tension") or "").split())
    continuity = " ".join(str(snapshot.get("continuity_summary") or "").split())
    baseline = (
        f"debt={float(snapshot.get('semantic_debt_est', 0.0)):.3f}  "
        f"uncertainty={float(snapshot.get('uncertainty', 0.0)):.3f}"
    )
    pressure = (
        f"closure={float(snapshot.get('closure_pressure', 0.0)):.3f}  "
        f"chaos={float(snapshot.get('chaos_pressure', 0.0)):.3f}"
    )

    print("\n\033[1;36m+-------------------------------- Genesis World State --------------------------------+\033[0m")
    print(
        f"{_style('branch:', str(snapshot.get('branch_id', '-')), color='35')}  "
        f"{_style('state:', str(snapshot.get('genesis_state_id', '-')), color='35')}  "
        f"{_style('height:', str(snapshot.get('height', '-')), color='35')}"
    )
    print(
        f"{_style('baseline:', baseline, color='32')}  "
        f"{_style('pressure:', pressure, color='32')}"
    )
    print(_style("entities:", entities, color="37"))
    print(_style("threads:", threads, color="37"))
    print(_style("interpretations:", interpretation_line, color="33"))
    print(_style("scene:", scene if scene else "-", color="36"))
    print(_style("tension:", tension if tension else "-", color="31"))
    if continuity:
        print(_style("continuity:", continuity, color="34"))
    print("\033[1;36m+-------------------------------------------------------------------------------------+\033[0m")


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
    candidate_artifact = str(update.get("candidate_artifact") or "")
    candidate_score = update.get("candidate_score")
    decision_reasons = update.get("decision_reasons") or []
    accepted_via_retry = bool(update.get("accepted_via_retry"))
    reject_streak = int(update.get("reject_streak") or 0)
    tension = str(update.get("deferred_tension") or "")

    narrative = scene if scene else artifact
    narrative = " ".join(narrative.split())
    candidate_preview = " ".join(candidate_artifact.split())
    tension_preview = " ".join(tension.split())

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
    print(_style("narrative:", narrative if narrative else "(no narrative available)", color="36"))
    if candidate_preview:
        extra = f"score={candidate_score}" if candidate_score is not None else "score=n/a"
        print(_style("candidate:", f"{candidate_preview} ({extra})", color="37"))
    if tension_preview:
        print(_style("tension:", tension_preview, color="31"))
    if decision_reasons:
        print(_style("decision:", "; ".join(str(x) for x in decision_reasons), color="33"))
    if accepted_via_retry:
        print(_style("adaptive:", "accepted via retry threshold relaxation", color="32"))
    elif reject_streak > 0:
        print(_style("adaptive:", f"reject streak={reject_streak}", color="31"))


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
    llm = engine.llm_status
    llm_mode = "enabled" if llm["enabled"] else "disabled"
    print(
        f"{_style('LLM:', llm_mode, color='35')} "
        f"{_style('provider:', str(llm['provider']), color='35')} "
        f"{_style('model:', str(llm['model'] or '-'), color='35')} "
        f"{_style('reason:', str(llm['reason']), color='35')}"
    )
    genesis = engine.get_genesis_snapshot()
    _render_genesis(genesis)
    summary = engine.run(args.steps, progress_callback=_render_progress)
    print("\n\033[1;32m=== Final Summary ===\033[0m")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
