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
    step_similarity = float(update.get("step_similarity") or 0.0)
    new_fact_count = int(update.get("new_fact_count") or 0)
    novel_fact_ratio = float(update.get("novel_fact_ratio") or 0.0)
    semantic_delta_score = float(update.get("semantic_delta_score") or 0.0)
    stagnation_streak = int(update.get("stagnation_streak") or 0)
    ontological_stagnation = float(update.get("ontological_stagnation") or 0.0)
    active_anchor_count = int(update.get("active_anchor_count") or 0)
    decision_reasons = update.get("decision_reasons") or []
    accepted_via_retry = bool(update.get("accepted_via_retry"))
    reject_streak = int(update.get("reject_streak") or 0)
    escape_mode = bool(update.get("escape_mode"))
    candidate_traces = update.get("candidate_traces") or []
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
        f"{_style('ledger:', f'accepted={accepted} rejected={rejected}', color='32')} "
        f"{_style('step_similarity:', f'{step_similarity:.3f}', color='34')}"
    )
    print(
        f"{_style('novelty:', f'new_fact_count={new_fact_count}  novel_fact_ratio={novel_fact_ratio:.3f}  semantic_delta={semantic_delta_score:.3f}', color='92')} "
        f"{_style('stagnation:', str(stagnation_streak), color='91')} "
        f"{_style('ontological:', f'{ontological_stagnation:.3f}', color='95')} "
        f"{_style('anchors:', str(active_anchor_count), color='96')}"
    )
    print(_style("narrative:", narrative if narrative else "(no narrative available)", color="36"))
    if candidate_preview:
        extra = f"score={candidate_score}" if candidate_score is not None else "score=n/a"
        print(_style("candidate:", f"{candidate_preview} ({extra})", color="37"))
    if tension_preview:
        print(_style("tension:", tension_preview, color="31"))
    if decision_reasons:
        print(_style("decision:", "; ".join(str(x) for x in decision_reasons), color="33"))
    if candidate_traces:
        for trace in candidate_traces:
            print(
                _style(
                    "trace:",
                    (
                        f"{trace.get('prover_id')} "
                        f"verdict={trace.get('verdict')} score={trace.get('score')} raw={trace.get('raw_score')} "
                        f"sim={trace.get('similarity')} scene_sim={trace.get('scene_similarity')} penalty={trace.get('penalty')} "
                        f"new_facts={trace.get('new_fact_count')} refs={trace.get('reference_count')} refs_q={trace.get('refs_quality')} progress_gate={trace.get('progress_gate')} "
                        f"novelty={trace.get('novelty_score')} (fact={trace.get('novel_fact')},type={trace.get('novel_type')},refs={trace.get('novel_refs')}) "
                        f"tension_prog={trace.get('tension_progress')} escape={trace.get('escape_mode')} "
                        f"llm_used={trace.get('llm_used')} source={trace.get('source')}"
                        + (f" error={trace.get('llm_error')}" if trace.get("llm_error") else "")
                    ),
                    color="90",
                )
            )
    if accepted_via_retry:
        print(_style("adaptive:", "accepted via retry threshold relaxation", color="32"))
    elif reject_streak > 0:
        print(_style("adaptive:", f"reject streak={reject_streak}", color="31"))
    if escape_mode:
        print(_style("mode:", "escape mode active (forced concrete progression)", color="93"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PoCWC simulation")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--db", type=Path, default=Path("data/world.db"))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--llm-provider", default=None, help="LLM provider (none|openrouter)")
    parser.add_argument("--llm-model", default=None, help="LLM model id for provider")
    parser.add_argument("--llm-base-url", default=None, help="Override provider base URL")
    parser.add_argument("--llm-temperature", type=float, default=0.75, help="LLM sampling temperature")
    parser.add_argument("--llm-top-p", type=float, default=0.92, help="LLM nucleus sampling top-p")
    parser.add_argument("--world-config", type=Path, default=Path("config/world.default.json"), help="Path to world configuration JSON")
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
            llm_temperature=args.llm_temperature,
            llm_top_p=args.llm_top_p,
            story_language=args.story_language,
            world_config_path=args.world_config,
        )
    )
    llm = engine.llm_status
    llm_mode = "enabled" if llm["enabled"] else "disabled"
    print(
        f"{_style('LLM:', llm_mode, color='35')} "
        f"{_style('provider:', str(llm['provider']), color='35')} "
        f"{_style('model:', str(llm['model'] or '-'), color='35')} "
        f"{_style('temperature:', f'{args.llm_temperature:.2f}', color='35')} "
        f"{_style('top_p:', f'{args.llm_top_p:.2f}', color='35')} "
        f"{_style('reason:', str(llm['reason']), color='35')}"
    )
    genesis = engine.get_genesis_snapshot()
    _render_genesis(genesis)
    summary = engine.run(args.steps, progress_callback=_render_progress)
    print("\n\033[1;32m=== Final Summary ===\033[0m")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
