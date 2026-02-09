from __future__ import annotations

from statistics import mean


def estimate_semantic_debt(interpretation_strength: dict[str, float], fragility: float, uncertainty: float) -> float:
    """Return a bounded semantic debt proxy in [0, 1]."""
    if not interpretation_strength:
        return 0.5

    values = list(interpretation_strength.values())
    spread = max(values) - min(values)
    coexistence = 1.0 - spread
    raw = 0.45 * coexistence + 0.35 * fragility + 0.20 * uncertainty
    return max(0.0, min(1.0, raw))


def debt_trend(history: list[float]) -> float:
    if len(history) < 2:
        return 0.0
    return history[-1] - mean(history[:-1])
