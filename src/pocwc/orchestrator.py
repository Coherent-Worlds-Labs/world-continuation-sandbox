from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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


@dataclass(slots=True)
class SimulationConfig:
    db_path: Path = Path("data/world.db")
    seed: int = 7
    steps: int = 50
    epoch: int = 5
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_base_url: str | None = None


class SimulationEngine:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.rng = random.Random(config.seed)
        self.store = WorldStore(config.db_path)
        self.projection = ProjectionBuilder()
        self.taskgen = TaskGenerator(self.rng)
        llm_settings = LLMSettings.from_env(
            provider_override=config.llm_provider,
            model_override=config.llm_model,
            base_url_override=config.llm_base_url,
        )
        llm_adapter = create_llm_adapter(llm_settings)
        self.provers = default_provers(self.rng, llm_adapter)
        self.verifiers = default_verifiers(self.rng, llm_adapter)
        self.aggregator = Aggregator()
        self.controller = DifficultyController(epoch=config.epoch)
        self.controller_state = ControllerState(difficulty=Difficulty())
        self.runtime = RuntimeStats()
        self.debt_history: list[float] = []

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _seed_genesis(self) -> None:
        branches = self.store.list_branches()
        if branches:
            return

        state_id = "state-0"
        branch_id = "branch-main"
        created_at = self._now()
        self.store.insert_state(
            {
                "state_id": state_id,
                "branch_id": branch_id,
                "parent_state_id": None,
                "height": 0,
                "artifact_x": (
                    "In Alice's city, a foundational event happened years ago, yet no one can state what truly happened. "
                    "Some call it an accident, others an experiment, others a cumulative drift. "
                    "Every new fact shifts plausibility, but no interpretation reaches final truth."
                ),
                "meta_m": {
                    "entities": ["E0", "Alice", "I1", "I2", "I3"],
                    "threads": ["origin ambiguity", "institutional trust", "memory reliability"],
                    "interpretation_strength": {"I1": 0.34, "I2": 0.33, "I3": 0.33},
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
                "semantic_debt_est": 0.5,
                "uncertainty": 0.5,
                "closure_pressure": 0.5,
                "chaos_pressure": 0.5,
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
        difficulty = self.taskgen.build_difficulty(self.controller_state.difficulty, signals)
        projection = self.projection.build(artifacts, difficulty.dependency_depth)
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

    def _evaluate_candidate(self, challenge: Challenge, candidate) -> tuple[Verdict, float, dict[str, Any], dict[str, int]]:
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
        return decision.verdict, decision.score, signal_means, decision.level_counts

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

        self.runtime.accepted_candidates += 1

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

    def run(self, steps: int | None = None) -> dict[str, Any]:
        self._seed_genesis()
        total_steps = steps or self.config.steps
        existing_challenges = len(self.store.list_challenges())

        for offset in range(1, total_steps + 1):
            step = existing_challenges + offset
            branch = self._choose_branch()
            challenge = self._build_challenge(step, branch)
            self.runtime.attempted_challenges += 1

            accepted_candidate = None
            best_score = 0.0
            best_meta: dict[str, Any] = {}
            best_levels: dict[str, int] = {}

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
                verdict, score, signals, levels = self._evaluate_candidate(challenge, candidate)
                if verdict == Verdict.ACCEPT and score > best_score:
                    accepted_candidate = candidate
                    best_score = score
                    best_meta = signals
                    best_levels = levels
                self.store.update_candidate_status(candidate.candidate_id, verdict.value)

            if accepted_candidate is not None:
                self._accept_candidate(challenge, accepted_candidate, best_score, best_meta, best_levels)
                self._maybe_create_fork(challenge, accepted_candidate)
            else:
                self.runtime.rejected_candidates += 1
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

        final_metrics = compute_metrics(self.store.list_branches(), self.store.list_verification_results(), self.runtime)
        final_metrics["controller"] = {
            "difficulty": self.controller_state.difficulty.as_dict(),
            "mode": self.controller_state.mode,
            "theta": self.controller_state.theta,
        }
        return final_metrics
