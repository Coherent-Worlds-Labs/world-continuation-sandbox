from __future__ import annotations

import re
from typing import Iterable

BANNED_FINAL_TRUTH_PATTERNS = (
    r"final\s+truth",
    r"ultimate\s+proof",
    r"case\s+closed",
    r"revealed\s+what\s+really\s+happened",
)


def check_no_final_truth(text: str) -> tuple[bool, str]:
    lowered = text.lower()
    for pattern in BANNED_FINAL_TRUTH_PATTERNS:
        if re.search(pattern, lowered):
            return False, "Final-truth claim detected"
    return True, ""


def check_non_collapse(meta: dict) -> tuple[bool, str]:
    strengths = meta.get("interpretation_strength", {})
    if not strengths:
        return False, "Missing interpretation strengths"

    positive = [v for v in strengths.values() if float(v) > 0.05]
    if len(positive) < 2:
        return False, "Interpretation collapse detected"
    return True, ""


def check_coherence(text: str, meta: dict) -> tuple[bool, str]:
    claims: Iterable[str] = meta.get("claims", [])
    if len(set(claims)) != len(list(claims)):
        return False, "Duplicate contradictory claims"
    if "contradiction:" in text.lower():
        return False, "Explicit contradiction marker detected"
    return True, ""


def evaluate_invariants(text: str, meta: dict) -> list[str]:
    failures: list[str] = []
    for check in (check_no_final_truth,):
        ok, reason = check(text)
        if not ok:
            failures.append(reason)

    for check in (check_non_collapse, check_coherence):
        ok, reason = check(meta=meta, text=text) if check is check_coherence else check(meta)
        if not ok:
            failures.append(reason)

    return failures
