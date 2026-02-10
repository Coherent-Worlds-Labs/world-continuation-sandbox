---
id: "202602101956-GEV32Q"
title: "Rewrite ontological stagnation metric"
result_summary: "FIX2 constraints delivered and validated."
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T19:58:45.951Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX2 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:08:01.191Z"
  updated_by: "CODER"
  note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
commit:
  hash: "861c9ce98c77a11d5e0a59dfa7a7e6c77ce57d6d"
  message: "✅ YJYT9K backend: implement FIX2 hard fact-object progression constraints"
comments:
  -
    author: "CODER"
    body: "Start: Rewrite ontological stagnation metric using structural world deltas rather than text style."
  -
    author: "CODER"
    body: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
events:
  -
    type: "status"
    at: "2026-02-10T20:00:24.953Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Rewrite ontological stagnation metric using structural world deltas rather than text style."
  -
    type: "verify"
    at: "2026-02-10T20:08:01.191Z"
    author: "CODER"
    state: "ok"
    note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
  -
    type: "status"
    at: "2026-02-10T20:08:37.243Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
doc_version: 2
doc_updated_at: "2026-02-10T20:08:37.243Z"
doc_updated_by: "CODER"
description: "Compute stagnation strictly from structural world-state deltas rather than narrative phrasing."
id_source: "generated"
---
## Summary

Rewrite ontological stagnation to structural-world criteria.

## Scope

Stagnation metric based on fact/type/entity/commitment deltas, not textual similarity.

## Plan

1) Define structural stagnation inputs over rolling window. 2) Compute score from fact-id growth, type diversity, entity/commitment changes. 3) Integrate into controller and diagnostics. 4) Add tests for stagnant vs progressing sequences.

## Risks

Metric oscillation; mitigate with rolling window and thresholds in config.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:08:01.191Z — VERIFY — ok

By: CODER

Note: FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed).

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:00:24.953Z, excerpt_hash=sha256:817cd2c543c73511b81c71322a1c0e1c04c3bf0a0f5ae4926387db23bb7816ff

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert to previous stagnation implementation.

## Context

Derived from sow/FIX2 - factobject.txt to eliminate pseudo-facts and enforce irreversible structural world progression.

## Verify Steps

- Add tests where repetitive text with no structural change yields high stagnation. - Validate progressing structural sequences lower stagnation.

## Notes

### Approvals / Overrides
- Plan approved by user. No overrides requested.

### Decisions
- FIX2 enforces hard structural progression constraints over stylistic quality.

### Implementation Notes
- Pending implementation in this task.

### Evidence / Links
- Source analysis: sow/FIX2 - factobject.txt
