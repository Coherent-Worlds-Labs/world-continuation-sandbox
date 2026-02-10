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

    def decide(
        self,
        results: list[VerificationResult],
        *,
        novelty_score: float = 0.5,
        tension_progress: float = 0.5,
        repetition_penalty: float = 0.0,
        hard_fail: bool = False,
        progress_gate: bool = True,
    ) -> AggregateDecision:
        if not results:
            return AggregateDecision(Verdict.REJECT, 0.0, ["No verification results"], {})

        scores = sorted(r.score for r in results)
        trimmed = scores[1:-1] if len(scores) > 2 else scores
        aggregate_score = mean(trimmed)
        composite_score = (
            aggregate_score * 0.50
            + novelty_score * 0.30
            + tension_progress * 0.20
            - repetition_penalty * 0.25
        )
        composite_score = max(0.0, min(1.0, composite_score))

        rejects = [r for r in results if r.verdict == Verdict.REJECT]
        accepts = [r for r in results if r.verdict == Verdict.ACCEPT]

        level_counts: dict[str, int] = {}
        for r in results:
            level_counts[r.level_max_reached.value] = level_counts.get(r.level_max_reached.value, 0) + 1

        reasons: list[str] = []
        if hard_fail:
            reasons.append("Hard fail: novelty gate")
            verdict = Verdict.REJECT
        elif not progress_gate:
            reasons.append("Hard fail: progress gate")
            verdict = Verdict.REJECT
        elif len(rejects) >= self.reject_quorum:
            reasons.append("Reject quorum reached")
            verdict = Verdict.REJECT
        elif composite_score >= self.accept_threshold and len(accepts) >= 2:
            reasons.append("Composite threshold satisfied")
            verdict = Verdict.ACCEPT
        else:
            reasons.append("Insufficient confidence")
            verdict = Verdict.REJECT

        return AggregateDecision(verdict, round(composite_score, 3), reasons, level_counts)
