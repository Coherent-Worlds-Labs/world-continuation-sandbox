from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Any


@dataclass(slots=True)
class RuntimeStats:
    attempted_challenges: int = 0
    accepted_candidates: int = 0
    rejected_candidates: int = 0
    forks_created: int = 0


def compute_metrics(
    branches: list[dict[str, Any]],
    verification_results: list[dict[str, Any]],
    runtime: RuntimeStats,
) -> dict[str, Any]:
    reject_by_level: dict[str, int] = {"L0": 0, "L1": 0, "L2": 0, "L3": 0}
    scores: list[float] = []
    for row in verification_results:
        scores.append(float(row["score"]))
        if row["verdict"] == "reject":
            lvl = str(row["level_max_reached"])
            reject_by_level[lvl] = reject_by_level.get(lvl, 0) + 1

    branch_debt = [float(b["semantic_debt_est"]) for b in branches] or [0.0]
    accept_rate = runtime.accepted_candidates / max(1, runtime.attempted_challenges)
    fork_rate = runtime.forks_created / max(1, runtime.accepted_candidates)

    variance = pstdev(scores) if len(scores) > 1 else 0.0

    return {
        "accept_rate": round(accept_rate, 3),
        "fork_rate": round(fork_rate, 3),
        "reject_by_level": reject_by_level,
        "validator_variance": round(variance, 4),
        "semantic_debt_est": round(mean(branch_debt), 3),
        "branches": len(branches),
        "attempted_challenges": runtime.attempted_challenges,
        "accepted_candidates": runtime.accepted_candidates,
        "rejected_candidates": runtime.rejected_candidates,
    }
