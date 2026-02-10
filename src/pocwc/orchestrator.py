from __future__ import annotations

import random
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .aggregation import Aggregator
from .controller import ControllerMetrics, ControllerState, DifficultyController
from .debt import debt_trend, estimate_semantic_debt
from .domain import Challenge, Difficulty, Verdict
from .metrics import RuntimeStats, compute_metrics
from .projection import ProjectionBuilder
from .provers import default_provers
from .llm import LLMSettings, create_llm_adapter
from .store import WorldStore
from .taskgen import BranchSignals, TaskGenerator
from .verifiers import default_verifiers
from .world_config import DEFAULT_WORLD_CONFIG_PATH, load_world_config


@dataclass(slots=True)
class SimulationConfig:
    db_path: Path = Path("data/world.db")
    seed: int = 7
    steps: int = 50
    epoch: int = 5
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_base_url: str | None = None
    llm_temperature: float = 0.55
    llm_top_p: float = 0.92
    story_language: str = "english"
    world_config_path: Path = DEFAULT_WORLD_CONFIG_PATH


class SimulationEngine:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.rng = random.Random(config.seed)
        self.store = WorldStore(config.db_path)
        self.world = load_world_config(config.world_config_path)
        self.main_branch_id = str(self.world.get("main_branch_id", "branch-main"))
        self.projection = ProjectionBuilder()
        self.taskgen = TaskGenerator(self.rng)
        llm_settings = LLMSettings.from_env(
            provider_override=config.llm_provider,
            model_override=config.llm_model,
            base_url_override=config.llm_base_url,
        )
        llm_adapter = create_llm_adapter(llm_settings)
        if llm_adapter is not None:
            llm_reason = "ready"
        elif llm_settings.provider == "none":
            llm_reason = "provider=none"
        elif not llm_settings.model:
            llm_reason = "missing model"
        elif not llm_settings.api_key:
            llm_reason = "missing OPENROUTER_API_KEY"
        else:
            llm_reason = "adapter initialization failed"
        self.llm_status = {
            "enabled": llm_adapter is not None,
            "provider": llm_settings.provider,
            "model": llm_settings.model,
            "reason": llm_reason,
        }
        self.provers = default_provers(
            self.rng,
            llm_adapter,
            config.story_language,
            config.llm_temperature,
            config.llm_top_p,
            self.world.get("fallback_generation", {}),
        )
        self.verifiers = default_verifiers(self.rng, llm_adapter)
        self.aggregator = Aggregator()
        self.controller = DifficultyController(epoch=config.epoch)
        self.controller_state = ControllerState(difficulty=Difficulty())
        self.runtime = RuntimeStats()
        self.debt_history: list[float] = []

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return set(re.findall(r"[a-zA-Zа-яА-Я0-9]+", text.lower()))

    @classmethod
    def _text_similarity(cls, a: str, b: str) -> float:
        aa = cls._tokenize(a)
        bb = cls._tokenize(b)
        if not aa or not bb:
            return 0.0
        return len(aa.intersection(bb)) / max(1, len(aa.union(bb)))

    def _recent_branch_narratives(self, branch_id: str, limit: int = 5) -> list[str]:
        states = self.store.list_states(branch_id=branch_id)
        recent = states[-limit:]
        narratives: list[str] = []
        for state in recent:
            bundle = state.get("meta_m", {}).get("story_bundle", {})
            scene = str(bundle.get("scene", "")).strip()
            artifact = str(state.get("artifact_x", "")).strip()
            narratives.append(scene or artifact)
        return narratives

    def get_genesis_snapshot(self) -> dict[str, Any]:
        self._seed_genesis()
        genesis_cfg = self.world.get("genesis", {})
        genesis_state_id = str(genesis_cfg.get("state_id", "state-0"))
        branch = self.store.get_branch(self.main_branch_id)
        state = self.store.get_state(genesis_state_id)
        memory = self.store.get_story_memory(self.main_branch_id)

        if branch is None or state is None:
            raise RuntimeError("Genesis state is unavailable")

        meta_m = state.get("meta_m", {})
        story_bundle = meta_m.get("story_bundle", {})
        return {
            "branch_id": branch["branch_id"],
            "head_state_id": branch["head_state_id"],
            "genesis_state_id": state["state_id"],
            "height": state["height"],
            "semantic_debt_est": branch["semantic_debt_est"],
            "uncertainty": branch["uncertainty"],
            "closure_pressure": branch["closure_pressure"],
            "chaos_pressure": branch["chaos_pressure"],
            "entities": meta_m.get("entities", []),
            "threads": meta_m.get("threads", []),
            "interpretation_strength": meta_m.get("interpretation_strength", {}),
            "scene": story_bundle.get("scene", ""),
            "deferred_tension": story_bundle.get("deferred_tension", ""),
            "continuity_summary": (memory or {}).get("summary", ""),
        }

    def _seed_genesis(self) -> None:
        branches = self.store.list_branches()
        if branches:
            return

        genesis = self.world.get("genesis", {})
        continuity = self.world.get("continuity", {})
        anchor = str(self.world.get("anchor_character", "Alice"))
        state_id = str(genesis.get("state_id", "state-0"))
        branch_id = self.main_branch_id
        created_at = self._now()
        interpretation_strength = genesis.get("interpretation_strength", {"I1": 0.34, "I2": 0.33, "I3": 0.33})
        branch_metrics = genesis.get(
            "branch_metrics",
            {"semantic_debt_est": 0.5, "uncertainty": 0.5, "closure_pressure": 0.5, "chaos_pressure": 0.5},
        )
        story_bundle = genesis.get("story_bundle", {})
        story_memory = genesis.get("story_memory", {})
        story_event = genesis.get("story_event", {})
        self.store.insert_state(
            {
                "state_id": state_id,
                "branch_id": branch_id,
                "parent_state_id": None,
                "height": 0,
                "artifact_x": str(
                    genesis.get(
                        "artifact_x",
                        (
                            "In Alice's city, a foundational event happened years ago, yet no one can state what truly happened. "
                            "Some call it an accident, others an experiment, others a cumulative drift. "
                            "Every new fact shifts plausibility, but no interpretation reaches final truth."
                        ),
                    )
                ),
                "meta_m": {
                    "entities": list(genesis.get("entities", ["E0", anchor, "I1", "I2", "I3"])),
                    "threads": list(genesis.get("threads", ["origin ambiguity", "institutional trust", "memory reliability"])),
                    "interpretation_strength": interpretation_strength,
                    "story_bundle": story_bundle,
                },
                "challenge_ref": None,
                "acceptance_summary": {"score": 1.0, "reasons": ["genesis"]},
                "created_at": created_at,
            }
        )
        self.store.upsert_branch(
            {
                "branch_id": branch_id,
                "head_state_id": state_id,
                "created_at": created_at,
                "status": "active",
                "semantic_debt_est": float(branch_metrics.get("semantic_debt_est", 0.5)),
                "uncertainty": float(branch_metrics.get("uncertainty", 0.5)),
                "closure_pressure": float(branch_metrics.get("closure_pressure", 0.5)),
                "chaos_pressure": float(branch_metrics.get("chaos_pressure", 0.5)),
            }
        )
        self.store.upsert_story_memory(
            {
                "branch_id": branch_id,
                "summary": str(story_memory.get("summary", f"{anchor}'s world begins with unresolved competing interpretations.")),
                "continuity": {
                    "anchor_character": anchor,
                    "known_entities": list(
                        story_memory.get(
                            "known_entities",
                            continuity.get("default_known_entities", ["E0", anchor, "city archive"]),
                        )
                    ),
                    "unresolved_tensions": list(
                        story_memory.get(
                            "unresolved_tensions",
                            ["What happened at E0", "Whether records reflect truth or process noise"],
                        )
                    ),
                    "timeline_highlights": list(
                        story_memory.get(
                            "timeline_highlights",
                            ["Genesis uncertainty is stable and no final truth is available."],
                        )
                    ),
                },
                "updated_at": created_at,
            }
        )
        self.store.insert_story_event(
            {
                "branch_id": branch_id,
                "state_id": state_id,
                "height": 0,
                "title": str(story_event.get("title", "Genesis: The City After E0")),
                "scene": str(story_event.get("scene", f"{anchor} and the city hold incompatible memories of a foundational event.")),
                "surface_confirmation": str(story_event.get("surface_confirmation", "No interpretation is final.")),
                "alternative_compatibility": list(
                    story_event.get(
                        "alternative_compatibility",
                        ["Accident narrative", "Experiment narrative", "Cumulative drift narrative"],
                    )
                ),
                "social_effect": str(
                    story_event.get("social_effect", "Interpretive camps emerge without resolving the underlying event.")
                ),
                "deferred_tension": str(
                    story_event.get("deferred_tension", f"{anchor} cannot map memory certainty to objective evidence.")
                ),
                "created_at": created_at,
            }
        )

    def _choose_branch(self) -> dict[str, Any]:
        active = [b for b in self.store.list_branches() if b["status"] == "active"]
        if not active:
            stalled = [b for b in self.store.list_branches() if b["status"] == "stalled"]
            if not stalled:
                raise RuntimeError("No active branch available")
            resurrect = self.rng.choice(stalled)
            resurrect["status"] = "active"
            self.store.upsert_branch(resurrect)
            return resurrect
        return self.rng.choice(active)

    def _branch_signals(self, branch: dict[str, Any]) -> BranchSignals:
        return BranchSignals(
            closure_pressure=float(branch["closure_pressure"]),
            chaos_pressure=float(branch["chaos_pressure"]),
            uncertainty=float(branch["uncertainty"]),
            accept_rate=self.runtime.accepted_candidates / max(1, self.runtime.attempted_challenges),
        )

    def _record_controller_epoch(self, step: int, metrics: dict[str, Any]) -> None:
        self.store.insert_controller_epoch(
            {
                "step": step,
                "difficulty": self.controller_state.difficulty.as_dict(),
                "mode": self.controller_state.mode,
                "theta": self.controller_state.theta,
                "metrics": metrics,
                "created_at": self._now(),
            }
        )

    def _build_challenge(self, step: int, branch: dict[str, Any]) -> Challenge:
        states = self.store.list_states(branch_id=branch["branch_id"])
        artifacts = [s["artifact_x"] for s in states]
        signals = self._branch_signals(branch)
        directive = self.taskgen.pick_directive(signals, self.controller_state.mode)
        difficulty = self.taskgen.build_difficulty(
            self.controller_state.difficulty,
            signals,
            self.controller_state.mode,
        )
        projection = self.projection.build(artifacts, difficulty.dependency_depth)
        story_memory = self.store.get_story_memory(branch["branch_id"])
        if story_memory:
            projection = (
                f"{projection}\n\nStory continuity summary:\n{story_memory.get('summary', '')}\n"
                f"Unresolved tensions: {', '.join(story_memory.get('continuity', {}).get('unresolved_tensions', []))}"
            )
        cid = f"challenge-{step:04d}-{branch['branch_id']}"

        challenge = Challenge(
            challenge_id=cid,
            branch_id=branch["branch_id"],
            parent_state_id=branch["head_state_id"],
            projection=projection,
            directive_type=directive,
            difficulty=difficulty,
            verifier_policy={"theta": self.controller_state.theta, "cascade": "L0-L3"},
        )

        self.store.insert_challenge(
            {
                "challenge_id": challenge.challenge_id,
                "branch_id": challenge.branch_id,
                "parent_state_id": challenge.parent_state_id,
                "projection": challenge.projection,
                "directive_type": challenge.directive_type,
                "difficulty_params": challenge.difficulty.as_dict(),
                "verifier_policy": challenge.verifier_policy,
                "created_at": self._now(),
            }
        )
        return challenge

    def _evaluate_candidate(
        self,
        challenge: Challenge,
        candidate,
    ) -> tuple[Verdict, float, dict[str, Any], dict[str, int], list[str]]:
        results = [v.evaluate(challenge, candidate, allow_l3=True) for v in self.verifiers]
        for result in results:
            self.store.insert_verification_result(
                {
                    "candidate_id": result.candidate_id,
                    "verifier_id": result.verifier_id,
                    "level_max_reached": result.level_max_reached.value,
                    "verdict": result.verdict.value,
                    "score": result.score,
                    "signals": result.signals,
                    "notes": result.notes,
                    "created_at": self._now(),
                }
            )
        decision = self.aggregator.decide(results)

        signal_means = {
            "closure_risk": round(sum(r.signals["closure_risk"] for r in results) / len(results), 3),
            "chaos_risk": round(sum(r.signals["chaos_risk"] for r in results) / len(results), 3),
            "fragility_score": round(sum(r.signals["fragility_score"] for r in results) / len(results), 3),
        }
        return decision.verdict, decision.score, signal_means, decision.level_counts, decision.reasons

    def _accept_candidate(self, challenge: Challenge, candidate, score: float, signals: dict[str, float], level_counts: dict[str, int]) -> None:
        parent = self.store.get_state(challenge.parent_state_id)
        if parent is None:
            raise RuntimeError("Parent state not found")

        branch_id = challenge.branch_id
        branch = self.store.get_branch(branch_id)
        if branch is None:
            raise RuntimeError("Branch not found")

        state_height = int(parent["height"]) + 1
        state_id = f"state-{challenge.challenge_id}-{candidate.prover_id[-4:]}"

        debt = estimate_semantic_debt(
            candidate.meta_m["interpretation_strength"],
            signals["fragility_score"],
            branch["uncertainty"],
        )
        self.debt_history.append(debt)

        self.store.insert_state(
            {
                "state_id": state_id,
                "branch_id": branch_id,
                "parent_state_id": challenge.parent_state_id,
                "height": state_height,
                "artifact_x": candidate.artifact_x,
                "meta_m": candidate.meta_m,
                "challenge_ref": challenge.challenge_id,
                "acceptance_summary": {
                    "score": score,
                    "reasons": ["aggregate pass"],
                    "level_counts": level_counts,
                },
                "created_at": self._now(),
            }
        )

        closure_pressure = signals["closure_risk"]
        chaos_pressure = signals["chaos_risk"]
        uncertainty = abs(closure_pressure - chaos_pressure)

        self.store.upsert_branch(
            {
                "branch_id": branch_id,
                "head_state_id": state_id,
                "created_at": branch["created_at"],
                "status": "active",
                "semantic_debt_est": debt,
                "uncertainty": round(uncertainty, 3),
                "closure_pressure": closure_pressure,
                "chaos_pressure": chaos_pressure,
            }
        )
        self._update_story_continuity(
            branch_id=branch_id,
            state_id=state_id,
            height=state_height,
            story_bundle=candidate.meta_m.get("story_bundle", {}),
        )

        self.runtime.accepted_candidates += 1

    def _update_story_continuity(self, *, branch_id: str, state_id: str, height: int, story_bundle: dict[str, Any]) -> None:
        memory = self.store.get_story_memory(branch_id)
        continuity_cfg = self.world.get("continuity", {})
        anchor = str(self.world.get("anchor_character", "Alice"))
        continuity = memory.get("continuity", {}) if memory else {}
        known_entities = set(
            continuity.get(
                "known_entities",
                continuity_cfg.get("default_known_entities", ["E0", anchor, "city archive"]),
            )
        )
        unresolved = list(continuity.get("unresolved_tensions", []))
        highlights = list(continuity.get("timeline_highlights", []))

        scene = str(story_bundle.get("scene", ""))
        social_effect = str(story_bundle.get("social_effect", ""))
        tension = str(story_bundle.get("deferred_tension", ""))
        if anchor in scene:
            known_entities.add(anchor)
        if "archive" in scene.lower():
            known_entities.add("city archive")
        if tension:
            unresolved.append(tension)
        if scene:
            highlights.append(f"H{height}: {scene}")

        unresolved = unresolved[-12:]
        highlights = highlights[-20:]
        summary_template = str(
            continuity_cfg.get("summary_template", "{anchor_character} continuity at height {height}: {scene_excerpt}")
        )
        summary = summary_template.format(
            anchor_character=anchor,
            height=height,
            scene_excerpt=scene[:120] if scene else "state accepted with unresolved interpretations",
        )

        self.store.upsert_story_memory(
            {
                "branch_id": branch_id,
                "summary": summary,
                "continuity": {
                    "anchor_character": anchor,
                    "known_entities": sorted(known_entities),
                    "unresolved_tensions": unresolved,
                    "timeline_highlights": highlights,
                },
                "updated_at": self._now(),
            }
        )
        self.store.insert_story_event(
            {
                "branch_id": branch_id,
                "state_id": state_id,
                "height": height,
                "title": f"Story step {height}",
                "scene": scene or "No explicit scene provided.",
                "surface_confirmation": str(story_bundle.get("surface_confirmation", "")),
                "alternative_compatibility": story_bundle.get("alternative_compatibility", []),
                "social_effect": social_effect,
                "deferred_tension": tension,
                "created_at": self._now(),
            }
        )

    def _maybe_create_fork(self, challenge: Challenge, accepted_candidate) -> None:
        if self.runtime.forks_created >= 2:
            return
        if self.rng.random() > 0.12:
            return

        parent_branch = self.store.get_branch(challenge.branch_id)
        if parent_branch is None:
            return

        new_branch_id = f"branch-fork-{self.runtime.forks_created + 1}"
        self.store.upsert_branch(
            {
                "branch_id": new_branch_id,
                "head_state_id": challenge.parent_state_id,
                "created_at": self._now(),
                "status": "active",
                "semantic_debt_est": parent_branch["semantic_debt_est"],
                "uncertainty": parent_branch["uncertainty"],
                "closure_pressure": parent_branch["closure_pressure"],
                "chaos_pressure": parent_branch["chaos_pressure"],
            }
        )

        # Add one accepted state on the fork from the same parent.
        fork_state_id = f"state-fork-{challenge.challenge_id}-{self.runtime.forks_created + 1}-{accepted_candidate.prover_id[-4:]}"
        self.store.insert_state(
            {
                "state_id": fork_state_id,
                "branch_id": new_branch_id,
                "parent_state_id": challenge.parent_state_id,
                "height": self.store.get_state(challenge.parent_state_id)["height"] + 1,
                "artifact_x": accepted_candidate.artifact_x + " Fork continuation accepted from shared parent.",
                "meta_m": accepted_candidate.meta_m,
                "challenge_ref": challenge.challenge_id,
                "acceptance_summary": {"score": 0.61, "reasons": ["fork branch accepted"]},
                "created_at": self._now(),
            }
        )
        self.store.upsert_branch(
            {
                "branch_id": new_branch_id,
                "head_state_id": fork_state_id,
                "created_at": self._now(),
                "status": "active",
                "semantic_debt_est": parent_branch["semantic_debt_est"],
                "uncertainty": parent_branch["uncertainty"],
                "closure_pressure": parent_branch["closure_pressure"],
                "chaos_pressure": parent_branch["chaos_pressure"],
            }
        )
        self.runtime.forks_created += 1

    def run(self, steps: int | None = None, progress_callback: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
        self._seed_genesis()
        total_steps = steps or self.config.steps
        existing_challenges = len(self.store.list_challenges())
        reject_streak = 0
        previous_progress_narrative = ""

        for offset in range(1, total_steps + 1):
            step = existing_challenges + offset
            branch = self._choose_branch()
            challenge = self._build_challenge(step, branch)
            self.runtime.attempted_challenges += 1

            accepted_candidate = None
            best_score = 0.0
            best_meta: dict[str, Any] = {}
            best_levels: dict[str, int] = {}
            best_any_candidate = None
            best_any_score = -1.0
            best_any_meta: dict[str, Any] = {}
            best_any_levels: dict[str, int] = {}
            best_any_reasons: list[str] = []
            accepted_via_retry = False
            candidate_traces: list[dict[str, Any]] = []
            recent_narratives = self._recent_branch_narratives(branch["branch_id"], limit=6)

            for index, prover in enumerate(self.provers, start=1):
                candidate = prover.generate(challenge, index)
                self.store.insert_candidate(
                    {
                        "candidate_id": candidate.candidate_id,
                        "challenge_id": candidate.challenge_id,
                        "prover_id": candidate.prover_id,
                        "artifact_x": candidate.artifact_x,
                        "meta_m": candidate.meta_m,
                        "status": "pending",
                        "created_at": self._now(),
                    }
                )
                verdict, score, signals, levels, reasons = self._evaluate_candidate(challenge, candidate)
                candidate_scene = str(candidate.meta_m.get("story_bundle", {}).get("scene", "")).strip()
                candidate_text = candidate_scene or candidate.artifact_x
                max_similarity = 0.0
                if recent_narratives:
                    max_similarity = max(self._text_similarity(candidate_text, prev) for prev in recent_narratives)
                novelty_penalty = max(0.0, (max_similarity - 0.62) * 0.35)
                adjusted_score = max(0.0, score - novelty_penalty)
                adjusted_verdict = verdict
                adjusted_reasons = list(reasons)
                if novelty_penalty > 0:
                    adjusted_reasons.append(
                        f"Repetition penalty applied (similarity={max_similarity:.2f}, penalty={novelty_penalty:.3f})"
                    )
                if adjusted_verdict == Verdict.ACCEPT and adjusted_score < self.aggregator.accept_threshold:
                    adjusted_verdict = Verdict.REJECT
                    adjusted_reasons.append("Repetition penalty lowered confidence below acceptance threshold")

                candidate_traces.append(
                    {
                        "prover_id": candidate.prover_id,
                        "candidate_id": candidate.candidate_id,
                        "score": round(adjusted_score, 3),
                        "raw_score": round(score, 3),
                        "similarity": round(max_similarity, 3),
                        "penalty": round(novelty_penalty, 3),
                        "verdict": adjusted_verdict.value,
                        "llm_used": bool(candidate.meta_m.get("llm_used", False)),
                        "source": str(candidate.meta_m.get("story_generation_source", "unknown")),
                        "llm_error": str(candidate.meta_m.get("llm_error", "")),
                    }
                )
                if adjusted_score > best_any_score:
                    best_any_candidate = candidate
                    best_any_score = adjusted_score
                    best_any_meta = signals
                    best_any_levels = levels
                    best_any_reasons = adjusted_reasons
                if adjusted_verdict == Verdict.ACCEPT and adjusted_score > best_score:
                    accepted_candidate = candidate
                    best_score = adjusted_score
                    best_meta = signals
                    best_levels = levels
                self.store.update_candidate_status(candidate.candidate_id, adjusted_verdict.value)

            if accepted_candidate is not None:
                self._accept_candidate(challenge, accepted_candidate, best_score, best_meta, best_levels)
                self._maybe_create_fork(challenge, accepted_candidate)
                reject_streak = 0
            else:
                self.runtime.rejected_candidates += 1
                reject_streak += 1
                # Adaptive retry: after consecutive rejects, accept the strongest candidate near threshold.
                adaptive_threshold = max(0.45, self.controller_state.theta - 0.08)
                if best_any_candidate is not None and reject_streak >= 2 and best_any_score >= adaptive_threshold:
                    self._accept_candidate(challenge, best_any_candidate, best_any_score, best_any_meta, best_any_levels)
                    self._maybe_create_fork(challenge, best_any_candidate)
                    self.runtime.rejected_candidates = max(0, self.runtime.rejected_candidates - 1)
                    reject_streak = 0
                    accepted_via_retry = True
                stale = self.store.get_branch(branch["branch_id"])
                if stale is not None:
                    self.store.upsert_branch(
                        {
                            "branch_id": stale["branch_id"],
                            "head_state_id": stale["head_state_id"],
                            "created_at": stale["created_at"],
                            "status": "stalled" if self.rng.random() < 0.15 else "active",
                            "semantic_debt_est": stale["semantic_debt_est"],
                            "uncertainty": stale["uncertainty"],
                            "closure_pressure": stale["closure_pressure"],
                            "chaos_pressure": stale["chaos_pressure"],
                        }
                    )

            verif = self.store.list_verification_results()
            branches = self.store.list_branches()
            metrics = compute_metrics(branches, verif, self.runtime)
            cm = ControllerMetrics(
                block_interval=1.0,
                accept_rate=metrics["accept_rate"],
                fork_rate=metrics["fork_rate"],
                validator_variance=metrics["validator_variance"],
                debt_level=metrics["semantic_debt_est"],
                debt_trend=debt_trend(self.debt_history),
                novelty_score=0.5 + self.rng.uniform(-0.1, 0.1),
                stability_score=1.0 - min(1.0, metrics["validator_variance"] * 2.0),
            )
            self.controller_state = self.controller.update(step, self.controller_state, cm)
            self._record_controller_epoch(step, {**metrics, "debt_trend": cm.debt_trend, "stability": cm.stability_score})

            if progress_callback is not None:
                head_state = self.store.get_branch(branch["branch_id"])
                head_id = head_state["head_state_id"] if head_state else None
                head_node = self.store.get_state(head_id) if head_id else None
                artifact = head_node["artifact_x"] if head_node else ""
                story_bundle = (head_node or {}).get("meta_m", {}).get("story_bundle", {}) if head_node else {}
                current_narrative = str(story_bundle.get("scene", "") or artifact)
                step_similarity = self._text_similarity(previous_progress_narrative, current_narrative)
                previous_progress_narrative = current_narrative
                candidate_artifact = best_any_candidate.artifact_x if best_any_candidate is not None else ""
                progress_callback(
                    {
                        "step": step,
                        "total_steps": total_steps,
                        "branch_id": branch["branch_id"],
                        "accepted": self.runtime.accepted_candidates,
                        "rejected": self.runtime.rejected_candidates,
                        "forks": self.runtime.forks_created,
                        "debt": metrics["semantic_debt_est"],
                        "variance": metrics["validator_variance"],
                        "mode": self.controller_state.mode,
                        "theta": self.controller_state.theta,
                        "artifact": artifact,
                        "candidate_artifact": candidate_artifact,
                        "candidate_score": round(best_any_score, 3) if best_any_score >= 0 else None,
                        "step_similarity": round(step_similarity, 3),
                        "decision_reasons": best_any_reasons,
                        "candidate_traces": candidate_traces,
                        "accepted_via_retry": accepted_via_retry,
                        "reject_streak": reject_streak,
                        "scene": story_bundle.get("scene", ""),
                        "deferred_tension": story_bundle.get("deferred_tension", ""),
                    }
                )

        final_metrics = compute_metrics(self.store.list_branches(), self.store.list_verification_results(), self.runtime)
        final_metrics["controller"] = {
            "difficulty": self.controller_state.difficulty.as_dict(),
            "mode": self.controller_state.mode,
            "theta": self.controller_state.theta,
        }
        return final_metrics
