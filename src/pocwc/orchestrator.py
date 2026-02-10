from __future__ import annotations

import random
import re
import hashlib
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
from .semantic import semantic_similarity


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
        self.progression = dict(self.world.get("progression", {}))
        self.taskgen_policy = dict(self.world.get("taskgen_policy", {}))
        self.projection = ProjectionBuilder()
        self.taskgen = TaskGenerator(self.rng, self.taskgen_policy)
        llm_settings = LLMSettings.from_env(
            provider_override=config.llm_provider,
            model_override=config.llm_model,
            base_url_override=config.llm_base_url,
        )
        llm_adapter = create_llm_adapter(llm_settings)
        self.llm_adapter = llm_adapter
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
        self.stagnation_streak = 0
        self.steps_since_new_fact = 0
        self.ontological_stagnation_score = 0.0

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

    def _semantic_similarity(self, a: str, b: str) -> float:
        return semantic_similarity(a, b, self.llm_adapter)

    @staticmethod
    def _fact_object_text(fact_object: Any) -> str:
        if not isinstance(fact_object, dict):
            return ""
        ftype = str(fact_object.get("type", "")).strip()
        content = str(fact_object.get("content", "")).strip()
        evidence = fact_object.get("evidence", [])
        if isinstance(evidence, list):
            evidence_text = " ; ".join(str(x).strip() for x in evidence if str(x).strip())
        else:
            evidence_text = str(evidence).strip()
        return f"{ftype}: {content} | {evidence_text}".strip()

    def _state_fact_text(self, state: dict[str, Any] | None) -> str:
        if not state:
            return ""
        meta = state.get("meta_m", {})
        fact_text = self._fact_object_text(meta.get("fact_object", {}))
        if fact_text:
            return fact_text
        story_bundle = meta.get("story_bundle", {})
        scene = str(story_bundle.get("scene", "")).strip()
        return scene or str(state.get("artifact_x", "")).strip()

    def _progression_int(self, key: str, default: int) -> int:
        try:
            return int(self.progression.get(key, default))
        except (TypeError, ValueError):
            return default

    def _progression_float(self, key: str, default: float) -> float:
        try:
            return float(self.progression.get(key, default))
        except (TypeError, ValueError):
            return default

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

    @staticmethod
    def _fact_text(fact: dict[str, Any]) -> str:
        return " | ".join(
            [
                str(fact.get("subject", "")),
                str(fact.get("predicate", "")),
                str(fact.get("object", "")),
                str(fact.get("time_hint", "")),
                str(fact.get("location_hint", "")),
            ]
        ).strip()

    @staticmethod
    def _fact_hash(text: str) -> str:
        return hashlib.sha1(" ".join(text.lower().split()).encode("utf-8")).hexdigest()

    def _recent_branch_facts(self, branch_id: str, limit: int = 120) -> list[dict[str, Any]]:
        return self.store.list_branch_facts(branch_id, limit=limit)

    def _recent_branch_directives(self, branch_id: str, limit: int = 12) -> list[str]:
        challenges = self.store.list_challenges(branch_id=branch_id)
        return [str(ch.get("directive_type", "")) for ch in challenges[-limit:] if str(ch.get("directive_type", "")).strip()]

    def _required_families(self, recent_directives: list[str]) -> list[str]:
        families_window = self._progression_int("family_window", 6)
        required = list(
            self.progression.get(
                "required_families",
                ["introduce_fact", "agent_commitment", "resource_constraint", "information_asymmetry", "delayed_consequence"],
            )
        )
        seen = {self.taskgen.directive_family(d) for d in recent_directives[-families_window:]}
        return [item for item in required if item not in seen]

    def _active_anchor_ids(self, branch_id: str, limit: int = 300) -> list[str]:
        facts = self.store.list_active_facts(branch_id, limit=limit)
        ids: list[str] = []
        for fact in facts:
            fid = str(fact.get("fact_id", "")).strip()
            if fid and fid not in ids:
                ids.append(fid)
        return ids

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
        anchor = str(self.world.get("anchor_character", "anchor"))
        state_id = str(genesis.get("state_id", "state-0"))
        branch_id = self.main_branch_id
        created_at = self._now()
        interpretation_strength = genesis.get("interpretation_strength", {})
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
                        "",
                    )
                ),
                "meta_m": {
                    "entities": list(genesis.get("entities", [])),
                    "threads": list(genesis.get("threads", [])),
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
                            continuity.get("default_known_entities", [anchor]),
                        )
                    ),
                    "unresolved_tensions": list(
                        story_memory.get(
                            "unresolved_tensions",
                            [],
                        )
                    ),
                    "timeline_highlights": list(
                        story_memory.get(
                            "timeline_highlights",
                            [],
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
                "title": str(story_event.get("title", "Genesis")),
                "scene": str(story_event.get("scene", "")),
                "surface_confirmation": str(story_event.get("surface_confirmation", "")),
                "alternative_compatibility": list(
                    story_event.get(
                        "alternative_compatibility",
                        [],
                    )
                ),
                "social_effect": str(
                    story_event.get("social_effect", "")
                ),
                "deferred_tension": str(
                    story_event.get("deferred_tension", "")
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

    def _build_challenge(self, step: int, branch: dict[str, Any], reject_streak: int = 0) -> Challenge:
        branch_id = branch["branch_id"]
        states = self.store.list_states(branch_id=branch_id)
        artifacts = [s["artifact_x"] for s in states]
        recent_narratives = self._recent_branch_narratives(branch_id, limit=6)
        recent_facts = self._recent_branch_facts(branch_id, limit=160)
        active_anchor_ids = self._active_anchor_ids(branch_id, limit=250)
        recent_directives = self._recent_branch_directives(branch_id, limit=12)
        required_families = self._required_families(recent_directives)
        signals = self._branch_signals(branch)
        directive = self.taskgen.pick_directive(
            signals,
            self.controller_state.mode,
            recent_directives=recent_directives,
            required_families=required_families,
        )
        escape_reject_streak = max(2, self._progression_int("escape_reject_streak", 2))
        forced_directives = list(
            self.progression.get(
                "escape_directive_types",
                ["IntroduceAmbiguousFact", "AgentCommitment", "ResourceConstraint"],
            )
        )
        escape_mode = reject_streak >= escape_reject_streak
        if escape_mode and forced_directives:
            directive = self.rng.choice([str(x) for x in forced_directives if str(x).strip()] or [directive])
        if self.stagnation_streak >= 2:
            directive = self.rng.choice(["AgentCommitment", "ResourceConstraint", "InformationAsymmetry", "DelayedConsequence"])
        max_streak = max(1, int(getattr(self.taskgen, "max_same_directive_streak", 2)))
        if len(recent_directives) >= max_streak:
            tail = recent_directives[-max_streak:]
            if tail and all(item == tail[0] for item in tail) and directive == tail[0]:
                alternatives = [d for d in self.taskgen._base_pool(signals, self.controller_state.mode) if d != directive]  # noqa: SLF001
                if alternatives:
                    directive = self.rng.choice(alternatives)
        difficulty = self.taskgen.build_difficulty(
            self.controller_state.difficulty,
            signals,
            self.controller_state.mode,
        )
        if escape_mode:
            difficulty = Difficulty(
                dependency_depth=difficulty.dependency_depth,
                constraint_density=min(1.0, max(0.1, difficulty.constraint_density + 0.12)),
                underspecification_level=max(0.1, difficulty.underspecification_level - 0.20),
                future_fragility=difficulty.future_fragility,
                novelty_budget=min(1.0, max(0.1, difficulty.novelty_budget + 0.10)),
            )
        projection = self.projection.build(artifacts, difficulty.dependency_depth)
        story_memory = self.store.get_story_memory(branch_id)
        if story_memory:
            projection = (
                f"{projection}\n\nStory continuity summary:\n{story_memory.get('summary', '')}\n"
                f"Unresolved tensions: {', '.join(story_memory.get('continuity', {}).get('unresolved_tensions', []))}"
            )
        if recent_facts:
            projection = (
                f"{projection}\n\nRecent branch facts (avoid rephrasing these as new):\n"
                + "\n".join(
                    f"- {str(f.get('fact_id', '')).strip()} :: {str(f.get('anchor_type', '')).strip()} :: {str(f.get('fact_text', ''))}"
                    for f in recent_facts[:8]
                )
            )
        if active_anchor_ids:
            projection = (
                f"{projection}\n\nAvailable prior fact IDs (use these in refs):\n"
                + ", ".join(active_anchor_ids[-12:])
            )
        if escape_mode:
            projection = (
                f"{projection}\n\nBreak-glass mode:\n"
                "Return strict JSON and force concrete progression. "
                "fact_object.type must be from allowed enum, fact_object.content must describe one concrete event in 1-2 sentences, "
                "and provide at least one explicit reference to a prior fact id when available."
            )
        cadence_window = max(1, self._progression_int("fact_cadence_window", 3))
        required_min_new_facts = 1 if self.steps_since_new_fact >= cadence_window - 1 else 0
        dependency_target_depth = max(1, self._progression_int("dependency_target_depth", 4))
        required_reference_count = max(1, self._progression_int("required_reference_count", 2))
        max_new_facts_per_step = max(1, self._progression_int("max_new_facts_per_step", 1))
        enforce_dependency = difficulty.dependency_depth < dependency_target_depth
        current_height = int(states[-1]["height"]) + 1 if states else 1
        hard_similarity_threshold = self._progression_float("hard_similarity_threshold", 0.92)
        scene_repeat_threshold = self._progression_float("scene_repeat_threshold", 0.97)
        min_refs_height_2 = max(1, self._progression_int("min_refs_height_2", 1))
        min_refs_height_5 = max(1, self._progression_int("min_refs_height_5", 2))
        refs_quality_min_height_2 = self._progression_float("refs_quality_min_height_2", 0.8)
        refs_quality_min_height_5 = self._progression_float("refs_quality_min_height_5", 1.2)
        refs_quality_alpha = self._progression_float("refs_quality_alpha", 0.18)
        novelty_min_early = self._progression_float("novelty_min_early", 0.45)
        novelty_min_mid = self._progression_float("novelty_min_mid", 0.55)
        novelty_min_late = self._progression_float("novelty_min_late", 0.60)
        type_memory_window = self._progression_int("type_memory_window", 7)
        refs_target = self._progression_int("refs_target", 2)
        hard_refs_from_step_2 = bool(self.progression.get("hard_refs_from_step_2", True))
        novelty_phase_early_end = self._progression_int("novelty_phase_early_end", 5)
        novelty_phase_mid_end = self._progression_int("novelty_phase_mid_end", 20)
        sim_fact_max = self._progression_float("sim_fact_max", hard_similarity_threshold)
        cid = f"challenge-{step:04d}-{branch_id}"

        challenge = Challenge(
            challenge_id=cid,
            branch_id=branch_id,
            parent_state_id=branch["head_state_id"],
            projection=projection,
            directive_type=directive,
            difficulty=difficulty,
            verifier_policy={
                "theta": self.controller_state.theta,
                "cascade": "L0-L3",
                "recent_narratives": recent_narratives,
                "recent_fact_texts": [f"{str(f.get('anchor_type', ''))}: {str(f.get('fact_text', ''))}" for f in recent_facts],
                "recent_fact_types": [str(f.get("anchor_type", "")).strip() for f in recent_facts if str(f.get("anchor_type", "")).strip()],
                "fact_height_by_id": {
                    str(f.get("fact_id", "")).strip(): int(f.get("introduced_height", 0))
                    for f in recent_facts
                    if str(f.get("fact_id", "")).strip()
                },
                "active_anchor_ids": active_anchor_ids,
                "last_fact_ids": active_anchor_ids[-12:],
                "recent_directives": recent_directives,
                "required_families": required_families,
                "required_min_new_facts": required_min_new_facts,
                "max_new_facts_per_step": max_new_facts_per_step,
                "dependency_target_depth": dependency_target_depth,
                "required_reference_count": required_reference_count,
                "enforce_dependency_accumulation": enforce_dependency,
                "current_height": current_height,
                "hard_similarity_threshold": hard_similarity_threshold,
                "scene_repeat_threshold": scene_repeat_threshold,
                "min_refs_height_2": min_refs_height_2,
                "min_refs_height_5": min_refs_height_5,
                "refs_quality_min_height_2": refs_quality_min_height_2,
                "refs_quality_min_height_5": refs_quality_min_height_5,
                "refs_quality_alpha": refs_quality_alpha,
                "novelty_min_early": novelty_min_early,
                "novelty_min_mid": novelty_min_mid,
                "novelty_min_late": novelty_min_late,
                "type_memory_window": type_memory_window,
                "refs_target": refs_target,
                "hard_refs_from_step_2": hard_refs_from_step_2,
                "novelty_phase_early_end": novelty_phase_early_end,
                "novelty_phase_mid_end": novelty_phase_mid_end,
                "sim_fact_max": sim_fact_max,
                "stagnation_streak": self.stagnation_streak,
                "escape_mode": escape_mode,
            },
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
        *,
        repetition_penalty: float = 0.0,
        hard_repetition_fail: bool = False,
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
        novelty_scores = [float(r.signals.get("novelty_score", r.score)) for r in results]
        tension_scores = [float(r.signals.get("tension_progress", 0.5)) for r in results]
        novelty_result = next((r for r in results if r.verifier_id == "verifier-novelty"), None)
        hard_fail = any("Novelty gate failed" in (r.notes or "") for r in results) or hard_repetition_fail
        progress_gate = not hard_fail
        decision = self.aggregator.decide(
            results,
            novelty_score=sum(novelty_scores) / max(1, len(novelty_scores)),
            tension_progress=sum(tension_scores) / max(1, len(tension_scores)),
            repetition_penalty=repetition_penalty,
            hard_fail=hard_fail,
            progress_gate=progress_gate,
        )

        novelty_new_fact_count = int(float((novelty_result.signals.get("new_fact_count", 0.0) if novelty_result else 0.0)))
        novelty_reference_count = int(float((novelty_result.signals.get("reference_count", 0.0) if novelty_result else 0.0)))
        novelty_refs_quality = float((novelty_result.signals.get("refs_quality", 0.0) if novelty_result else 0.0))
        novelty_fact_similarity = float((novelty_result.signals.get("max_fact_similarity", 0.0) if novelty_result else 0.0))
        novelty_scene_similarity = float((novelty_result.signals.get("max_scene_similarity", 0.0) if novelty_result else 0.0))
        novelty_fact_delta = float((novelty_result.signals.get("novel_fact", 0.0) if novelty_result else 0.0))
        novelty_type_delta = float((novelty_result.signals.get("novel_type", 0.0) if novelty_result else 0.0))
        novelty_refs_delta = float((novelty_result.signals.get("novel_refs", 0.0) if novelty_result else 0.0))
        signal_means = {
            "closure_risk": round(sum(r.signals["closure_risk"] for r in results) / len(results), 3),
            "chaos_risk": round(sum(r.signals["chaos_risk"] for r in results) / len(results), 3),
            "fragility_score": round(sum(r.signals["fragility_score"] for r in results) / len(results), 3),
            "novelty_score": round(sum(novelty_scores) / max(1, len(novelty_scores)), 3),
            "tension_progress": round(sum(tension_scores) / max(1, len(tension_scores)), 3),
            "new_fact_count": float(novelty_new_fact_count),
            "reference_count": float(novelty_reference_count),
            "refs_quality": round(novelty_refs_quality, 3),
            "max_fact_similarity": round(novelty_fact_similarity, 3),
            "max_scene_similarity": round(novelty_scene_similarity, 3),
            "novel_fact": round(novelty_fact_delta, 3),
            "novel_type": round(novelty_type_delta, 3),
            "novel_refs": round(novelty_refs_delta, 3),
            "progress_gate": 1.0 if progress_gate else 0.0,
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
        self._record_branch_facts(
            branch_id=branch_id,
            state_id=state_id,
            state_height=state_height,
            facts=candidate.meta_m.get("novel_facts", []),
            fact_object=candidate.meta_m.get("fact_object", {}),
        )

        self.runtime.accepted_candidates += 1

    def _record_branch_facts(self, *, branch_id: str, state_id: str, state_height: int, facts: Any, fact_object: Any) -> None:
        existing_ids = {
            str(row.get("fact_id", "")).strip()
            for row in self.store.list_branch_facts(branch_id, limit=3000)
            if str(row.get("fact_id", "")).strip()
        }

        def ensure_unique_fact_id(raw_id: str, index: int) -> str:
            base = raw_id.strip() or f"{state_id}-fact-{index + 1}"
            if base not in existing_ids:
                existing_ids.add(base)
                return base
            candidate = f"{base}::{state_id}"
            suffix = 1
            while candidate in existing_ids:
                suffix += 1
                candidate = f"{base}::{state_id}::{suffix}"
            existing_ids.add(candidate)
            return candidate

        canonical_facts: list[dict[str, Any]] = []
        if isinstance(fact_object, dict) and str(fact_object.get("id", "")).strip():
            evidence_raw = fact_object.get("evidence", "")
            if isinstance(evidence_raw, list):
                evidence_text = " ; ".join(str(x).strip() for x in evidence_raw if str(x).strip())
            else:
                evidence_text = str(evidence_raw).strip()
            canonical_facts.append(
                {
                    "fact_id": str(fact_object.get("id", "")).strip(),
                    "anchor_type": str(fact_object.get("type", "public_artifact")).strip() or "public_artifact",
                    "subject": str(fact_object.get("introduced_by", "")).strip(),
                    "predicate": "introduces",
                    "object": str(fact_object.get("content", "")).strip(),
                    "time_hint": str(fact_object.get("time", "")).strip(),
                    "location_hint": "",
                    "evidence_type": evidence_text,
                    "falsifiable": True,
                    "can_be_reinterpreted": True,
                    "references": list(fact_object.get("references", [])) if isinstance(fact_object.get("references", []), list) else [],
                }
            )
        if isinstance(facts, list):
            for item in facts:
                if isinstance(item, dict):
                    canonical_facts.append(item)
        deduped: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for item in canonical_facts:
            fid = str(item.get("fact_id", "")).strip()
            if not fid or fid in seen_ids:
                continue
            seen_ids.add(fid)
            deduped.append(item)
        canonical_facts = deduped
        if not canonical_facts:
            return
        for index, item in enumerate(canonical_facts):
            if not isinstance(item, dict):
                continue
            unique_fact_id = ensure_unique_fact_id(str(item.get("fact_id", "")), index)
            fact_text = self._fact_text(item)
            if not fact_text:
                continue
            references = item.get("references", [])
            if not isinstance(references, list):
                references = []
            self.store.insert_branch_fact(
                {
                    "branch_id": branch_id,
                    "state_id": state_id,
                    "fact_id": unique_fact_id,
                    "anchor_type": str(item.get("anchor_type", "public_artifact")),
                    "subject": str(item.get("subject", "")),
                    "predicate": str(item.get("predicate", "")),
                    "object": str(item.get("object", "")),
                    "time_hint": str(item.get("time_hint", "")),
                    "location_hint": str(item.get("location_hint", "")),
                    "evidence_type": str(item.get("evidence_type", "")),
                    "falsifiable": 1 if bool(item.get("falsifiable", True)) else 0,
                    "can_be_reinterpreted": 1 if bool(item.get("can_be_reinterpreted", True)) else 0,
                    "references": references,
                    "introduced_height": state_height,
                    "fact_text": fact_text,
                    "fact_hash": self._fact_hash(fact_text),
                    "created_at": self._now(),
                }
            )

    def _update_story_continuity(self, *, branch_id: str, state_id: str, height: int, story_bundle: dict[str, Any]) -> None:
        memory = self.store.get_story_memory(branch_id)
        continuity_cfg = self.world.get("continuity", {})
        anchor = str(self.world.get("anchor_character", "anchor"))
        continuity = memory.get("continuity", {}) if memory else {}
        known_entities = set(
            continuity.get(
                "known_entities",
                continuity_cfg.get("default_known_entities", [anchor]),
            )
        )
        unresolved = list(continuity.get("unresolved_tensions", []))
        highlights = list(continuity.get("timeline_highlights", []))

        scene = str(story_bundle.get("scene", ""))
        social_effect = str(story_bundle.get("social_effect", ""))
        tension = str(story_bundle.get("deferred_tension", ""))
        if anchor in scene:
            known_entities.add(anchor)
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

    def _ontological_stagnation(self, branch_id: str) -> dict[str, Any]:
        window = max(2, self._progression_int("stagnation_window", 6))
        states = self.store.list_states(branch_id=branch_id)
        recent_states = states[-window:]
        if len(recent_states) < 2:
            return {
                "score": 1.0,
                "new_fact_count": 0,
                "entity_growth": 0,
                "agent_structure_change": 0,
                "type_diversity_growth": 0,
                "interpretation_shift": 0.0,
            }
        state_ids = {str(s.get("state_id", "")) for s in recent_states}
        facts = [f for f in self.store.list_branch_facts(branch_id, limit=1000) if str(f.get("state_id", "")) in state_ids]
        new_fact_count = len({str(f.get("fact_id", "")) for f in facts if str(f.get("fact_id", "")).strip()})
        types = {str(f.get("anchor_type", "")).strip() for f in facts if str(f.get("anchor_type", "")).strip()}
        type_diversity_growth = max(0, len(types) - 1)
        first_entities = set(str(x) for x in recent_states[0].get("meta_m", {}).get("entities", []))
        last_entities = set(str(x) for x in recent_states[-1].get("meta_m", {}).get("entities", []))
        entity_growth = max(0, len(last_entities - first_entities))
        agent_structure_change = 1 if any(str(f.get("anchor_type", "")) == "agent_commitment" for f in facts) else 0
        first_weights = recent_states[0].get("meta_m", {}).get("interpretation_strength", {})
        last_weights = recent_states[-1].get("meta_m", {}).get("interpretation_strength", {})
        keys = set(first_weights).union(last_weights)
        interpretation_shift = sum(abs(float(last_weights.get(k, 0.0)) - float(first_weights.get(k, 0.0))) for k in keys)
        components = [
            0.0 if new_fact_count > 0 else 1.0,
            0.0 if entity_growth > 0 else 1.0,
            0.0 if agent_structure_change > 0 else 1.0,
            0.0 if type_diversity_growth > 0 else 1.0,
            0.0 if interpretation_shift >= 0.08 else 1.0,
        ]
        score = sum(components) / len(components)
        return {
            "score": round(score, 3),
            "new_fact_count": int(new_fact_count),
            "entity_growth": int(entity_growth),
            "agent_structure_change": int(agent_structure_change),
            "type_diversity_growth": int(type_diversity_growth),
            "interpretation_shift": round(float(interpretation_shift), 3),
        }

    def run(self, steps: int | None = None, progress_callback: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
        self._seed_genesis()
        total_steps = steps or self.config.steps
        existing_challenges = len(self.store.list_challenges())
        reject_streak = 0

        for offset in range(1, total_steps + 1):
            step = existing_challenges + offset
            branch = self._choose_branch()
            challenge = self._build_challenge(step, branch, reject_streak=reject_streak)
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
            recent_facts = self._recent_branch_facts(branch["branch_id"], limit=120)
            recent_fact_texts = [f"{str(f.get('anchor_type', '')).strip()}: {str(f.get('fact_text', '')).strip()}" for f in recent_facts]

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
                candidate_scene = str(candidate.meta_m.get("story_bundle", {}).get("scene", "")).strip()
                candidate_text = candidate_scene or candidate.artifact_x
                candidate_fact_text = self._fact_object_text(candidate.meta_m.get("fact_object", {}))
                max_fact_similarity = 0.0
                max_scene_similarity = 0.0
                if candidate_fact_text and recent_fact_texts:
                    max_fact_similarity = max(self._semantic_similarity(candidate_fact_text, prev) for prev in recent_fact_texts)
                if recent_narratives:
                    max_scene_similarity = max(self._semantic_similarity(candidate_text, prev) for prev in recent_narratives)
                hard_similarity_threshold = float(challenge.verifier_policy.get("sim_fact_max", 0.92))
                hard_repetition_fail = max_fact_similarity >= hard_similarity_threshold
                novelty_penalty = 0.0
                if max_fact_similarity > 0.80:
                    novelty_penalty = min(0.85, ((max_fact_similarity - 0.80) / 0.20) ** 2 * 0.85)
                verdict, score, signals, levels, reasons = self._evaluate_candidate(
                    challenge,
                    candidate,
                    repetition_penalty=novelty_penalty,
                    hard_repetition_fail=hard_repetition_fail,
                )
                adjusted_score = score
                adjusted_verdict = verdict
                adjusted_reasons = list(reasons)
                if novelty_penalty > 0:
                    adjusted_reasons.append(
                        f"Repetition penalty applied (fact_similarity={max_fact_similarity:.2f}, penalty={novelty_penalty:.3f})"
                    )
                if hard_repetition_fail:
                    adjusted_reasons.append(
                        f"Hard repetition reject (fact_similarity={max_fact_similarity:.2f} >= threshold={hard_similarity_threshold:.2f})"
                    )

                candidate_traces.append(
                    {
                        "prover_id": candidate.prover_id,
                        "candidate_id": candidate.candidate_id,
                        "score": round(adjusted_score, 3),
                        "raw_score": round(score, 3),
                        "similarity": round(max_fact_similarity, 3),
                        "fact_similarity": round(max_fact_similarity, 3),
                        "scene_similarity": round(max_scene_similarity, 3),
                        "penalty": round(novelty_penalty, 3),
                        "new_fact_count": int(signals.get("new_fact_count", 0.0)),
                        "reference_count": int(signals.get("reference_count", 0.0)),
                        "refs_quality": round(float(signals.get("refs_quality", 0.0)), 3),
                        "progress_gate": int(signals.get("progress_gate", 0.0)),
                        "novelty_score": signals.get("novelty_score", 0.0),
                        "novel_fact": signals.get("novel_fact", 0.0),
                        "novel_type": signals.get("novel_type", 0.0),
                        "novel_refs": signals.get("novel_refs", 0.0),
                        "tension_progress": signals.get("tension_progress", 0.0),
                        "verdict": adjusted_verdict.value,
                        "llm_used": bool(candidate.meta_m.get("llm_used", False)),
                        "source": str(candidate.meta_m.get("story_generation_source", "unknown")),
                        "llm_error": str(candidate.meta_m.get("llm_error", "")),
                        "escape_mode": bool(challenge.verifier_policy.get("escape_mode", False)),
                        "fact_id": str(candidate.meta_m.get("fact_object", {}).get("id", "")),
                        "fact_type": str(candidate.meta_m.get("fact_object", {}).get("type", "")),
                        "fact_refs": list(candidate.meta_m.get("fact_object", {}).get("references", []))
                        if isinstance(candidate.meta_m.get("fact_object", {}).get("references", []), list)
                        else [],
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

            new_fact_count_current = int(best_any_meta.get("new_fact_count", 0.0)) if best_any_meta else 0
            if accepted_candidate is not None:
                self._accept_candidate(challenge, accepted_candidate, best_score, best_meta, best_levels)
                self._maybe_create_fork(challenge, accepted_candidate)
                reject_streak = 0
                new_fact_count_current = int(best_meta.get("new_fact_count", 0.0))
            else:
                self.runtime.rejected_candidates += 1
                reject_streak += 1
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

            if new_fact_count_current >= 1:
                self.steps_since_new_fact = 0
            else:
                self.steps_since_new_fact += 1
            ontological = self._ontological_stagnation(branch["branch_id"])
            self.ontological_stagnation_score = float(ontological["score"])
            if self.ontological_stagnation_score >= self._progression_float("stagnation_threshold", 0.66):
                self.stagnation_streak += 1
            else:
                self.stagnation_streak = 0

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
                novelty_score=float(best_meta.get("novelty_score", 0.5)) if best_meta else 0.5,
                stability_score=1.0 - min(1.0, metrics["validator_variance"] * 2.0),
                ontological_stagnation=self.ontological_stagnation_score,
            )
            self.controller_state = self.controller.update(step, self.controller_state, cm)
            self._record_controller_epoch(
                step,
                {
                    **metrics,
                    "debt_trend": cm.debt_trend,
                    "stability": cm.stability_score,
                    "ontological_stagnation": self.ontological_stagnation_score,
                },
            )

            if progress_callback is not None:
                head_state = self.store.get_branch(branch["branch_id"])
                head_id = head_state["head_state_id"] if head_state else None
                head_node = self.store.get_state(head_id) if head_id else None
                artifact = head_node["artifact_x"] if head_node else ""
                story_bundle = (head_node or {}).get("meta_m", {}).get("story_bundle", {}) if head_node else {}
                parent_node = self.store.get_state(head_node.get("parent_state_id")) if head_node and head_node.get("parent_state_id") else None
                current_progress_text = self._state_fact_text(head_node)
                parent_progress_text = self._state_fact_text(parent_node)
                step_similarity = self._semantic_similarity(parent_progress_text, current_progress_text)
                candidate_artifact = best_any_candidate.artifact_x if best_any_candidate is not None else ""
                max_facts = max(1, self._progression_int("max_new_facts_per_step", 1))
                active_anchor_count = len(self._active_anchor_ids(branch["branch_id"], limit=250))
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
                        "new_fact_count": int(new_fact_count_current),
                        "novel_fact_ratio": round(min(1.0, float(new_fact_count_current) / float(max_facts)), 3),
                        "semantic_delta_score": round(float(best_any_meta.get("novelty_score", 0.0)), 3),
                        "stagnation_streak": self.stagnation_streak,
                        "ontological_stagnation": round(self.ontological_stagnation_score, 3),
                        "active_anchor_count": active_anchor_count,
                        "decision_reasons": best_any_reasons,
                        "candidate_traces": candidate_traces,
                        "accepted_via_retry": accepted_via_retry,
                        "reject_streak": reject_streak,
                        "escape_mode": bool(challenge.verifier_policy.get("escape_mode", False)),
                        "projection_fact_ids": list(challenge.verifier_policy.get("last_fact_ids", [])),
                        "scene": story_bundle.get("scene", ""),
                        "deferred_tension": story_bundle.get("deferred_tension", ""),
                    }
                )

        final_metrics = compute_metrics(self.store.list_branches(), self.store.list_verification_results(), self.runtime)
        final_metrics["controller"] = {
            "difficulty": self.controller_state.difficulty.as_dict(),
            "mode": self.controller_state.mode,
            "theta": self.controller_state.theta,
            "ontological_stagnation": round(self.ontological_stagnation_score, 3),
        }
        return final_metrics
