from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from .domain import VerificationResult, Verdict


@dataclass(slots=True)
class AggregateDecision:
    verdict: Verdict
    score: float
    reasons: list[str]
    level_counts: dict[str, int]


class Aggregator:
    def __init__(self, reject_quorum: int = 2, accept_threshold: float = 0.57) -> None:
        self.reject_quorum = reject_quorum
        self.accept_threshold = accept_threshold

    def decide(self, results: list[VerificationResult]) -> AggregateDecision:
        if not results:
            return AggregateDecision(Verdict.REJECT, 0.0, ["No verification results"], {})

        scores = sorted(r.score for r in results)
        trimmed = scores[1:-1] if len(scores) > 2 else scores
        aggregate_score = mean(trimmed)

        rejects = [r for r in results if r.verdict == Verdict.REJECT]
        accepts = [r for r in results if r.verdict == Verdict.ACCEPT]

        level_counts: dict[str, int] = {}
        for r in results:
            level_counts[r.level_max_reached.value] = level_counts.get(r.level_max_reached.value, 0) + 1

        reasons: list[str] = []
        if len(rejects) >= self.reject_quorum:
            reasons.append("Reject quorum reached")
            verdict = Verdict.REJECT
        elif aggregate_score >= self.accept_threshold and len(accepts) >= 2:
            reasons.append("Aggregate threshold satisfied")
            verdict = Verdict.ACCEPT
        else:
            reasons.append("Insufficient confidence")
            verdict = Verdict.REJECT

        return AggregateDecision(verdict, round(aggregate_score, 3), reasons, level_counts)
