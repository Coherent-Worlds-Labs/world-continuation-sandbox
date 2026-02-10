from __future__ import annotations

from dataclasses import dataclass, field

from .domain import Difficulty

MODES = ["diversify", "consolidate", "maintenance", "false-convergence", "deferred-tension"]


@dataclass(slots=True)
class ControllerMetrics:
    block_interval: float
    accept_rate: float
    fork_rate: float
    validator_variance: float
    debt_level: float
    debt_trend: float
    novelty_score: float
    stability_score: float
    ontological_stagnation: float


@dataclass(slots=True)
class ControllerState:
    difficulty: Difficulty = field(default_factory=Difficulty)
    mode: str = "diversify"
    theta: float = 0.57


class DifficultyController:
    def __init__(self, epoch: int = 5, delta_max: float = 0.15) -> None:
        self.epoch = epoch
        self.delta_max = delta_max

    @staticmethod
    def _clip(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))

    def update(self, step: int, state: ControllerState, metrics: ControllerMetrics) -> ControllerState:
        if step == 0 or step % self.epoch != 0:
            return state

        d = state.difficulty
        debt_low = metrics.debt_level < 0.38
        debt_high = metrics.debt_level > 0.72

        dd = d.dependency_depth
        cd = d.constraint_density
        ul = d.underspecification_level
        ff = d.future_fragility
        nb = d.novelty_budget

        if debt_low:
            dd += 1
            ul += 0.08
            ff += 0.06
        if debt_high:
            ul -= 0.08
            nb -= 0.07
            ff -= 0.06

        if metrics.fork_rate > 0.45:
            nb -= 0.05
            ul -= 0.05
        if metrics.validator_variance < 0.02:
            ul += 0.06
        if metrics.stability_score < 0.45:
            nb -= 0.06
            cd -= 0.04
        if metrics.novelty_score < 0.45:
            nb += 0.12
            ul += 0.08
        if metrics.ontological_stagnation > 0.66:
            dd += 1
            nb += 0.10
            ul += 0.06

        next_difficulty = Difficulty(
            dependency_depth=max(1, min(8, int(dd))),
            constraint_density=self._clip(cd, 0.1, 1.0),
            underspecification_level=self._clip(ul, 0.1, 1.0),
            future_fragility=self._clip(ff, 0.1, 1.0),
            novelty_budget=self._clip(nb, 0.1, 1.0),
        )

        # Hysteresis for mode selection.
        mode = state.mode
        if debt_high and metrics.stability_score < 0.50:
            mode = "maintenance"
        elif debt_low and metrics.accept_rate > 0.88 and metrics.validator_variance < 0.03:
            mode = "false-convergence"
        elif metrics.fork_rate > 0.40:
            mode = "consolidate"
        elif metrics.ontological_stagnation > 0.66:
            mode = "diversify"
        elif metrics.novelty_score < 0.55 or metrics.accept_rate > 0.75:
            mode = "diversify"
        else:
            mode = "diversify"

        theta = state.theta
        if metrics.accept_rate > 0.90:
            theta += 0.015
        elif metrics.accept_rate < 0.45:
            theta -= 0.02
        if mode == "diversify":
            theta -= 0.01

        theta = self._clip(theta, 0.50, 0.70)

        return ControllerState(next_difficulty, mode, round(theta, 3))
