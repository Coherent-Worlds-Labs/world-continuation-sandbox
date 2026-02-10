---
id: "202602102136-2ZYGS9"
title: "Implement FIX5 fact specificity and type enforcement"
result_summary: "Implemented FIX5 semantic progression hardening."
risk_level: "med"
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T21:37:40.181Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX5 implementation plan."
verification:
  state: "ok"
  updated_at: "2026-02-10T21:47:03.152Z"
  updated_by: "CODER"
  note: "Verified: FIX5 implemented with strict fact type enum, fact specificity hard gate, InstitutionalAction directive support, and scene stagnation breaker wiring. pytest 25/25 passed and 12-step smoke run completed."
commit:
  hash: "8542421a6d11de1bcc8ef960fc1bfba4b708f695"
  message: "✅ 2ZYGS9 backend: implement FIX5 semantic progression hardening"
comments:
  -
    author: "CODER"
    body: "Start: Implement FIX5 strict fact typing, specificity gates, and scene stagnation breaker behavior with tests."
  -
    author: "CODER"
    body: "Verified: FIX5 implemented and validated (strict fact type enum, specificity gate, stagnation breaker, tests)."
events:
  -
    type: "status"
    at: "2026-02-10T21:37:40.291Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implement FIX5 strict fact typing, specificity gates, and scene stagnation breaker behavior with tests."
  -
    type: "verify"
    at: "2026-02-10T21:47:03.152Z"
    author: "CODER"
    state: "ok"
    note: "Verified: FIX5 implemented with strict fact type enum, fact specificity hard gate, InstitutionalAction directive support, and scene stagnation breaker wiring. pytest 25/25 passed and 12-step smoke run completed."
  -
    type: "status"
    at: "2026-02-10T21:48:41.666Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: FIX5 implemented and validated (strict fact type enum, specificity gate, stagnation breaker, tests)."
doc_version: 2
doc_updated_at: "2026-02-10T21:48:41.666Z"
doc_updated_by: "CODER"
description: "Add strict fact type enum/normalization, fact specificity score hard gate, diversify type streak constraint, and scene stagnation breaker directive policy."
id_source: "generated"
---
## Summary

FIX5 implementation for semantic progression quality and anti-stagnation.

## Scope

In-scope: taskgen/orchestrator/provers/verifiers/config/tests/docs updates.

## Plan

1. Add strict fact-type enum and normalization.
2. Add fact-specificity hard gate and banned-vague checks.
3. Add institutional-action directive and scene stagnation trigger.
4. Add diversify type-streak rule and prompt constraints.
5. Validate with pytest and smoke simulation.

## Risks

Risk: stricter gates may lower acceptance; mitigated by targeted stagnation breaker instead of threshold relaxation.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T21:47:03.152Z — VERIFY — ok

By: CODER

Note: Verified: FIX5 implemented with strict fact type enum, fact specificity hard gate, InstitutionalAction directive support, and scene stagnation breaker wiring. pytest 25/25 passed and 12-step smoke run completed.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T21:37:40.291Z, excerpt_hash=sha256:ca4f850e6f0a12bcf84dc379cd17720ae6b1f91f8dc56819849ce46576d074ce

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert FIX5 commit and rerun tests if acceptance collapses or regressions appear.

## Context

FIX5 requires concrete fact impact, strict fact-type handling, and scene stagnation escape logic.

## Verify Steps

1. python -m pytest tests -q
2. python scripts/run_simulation.py --steps 12 --db data/fix5_smoke.db --seed 10
3. Confirm fact_type no longer falls to generic placeholders and scene stagnation breaker activates.

## Notes

### Approvals / Overrides
No overrides.

### Decisions
Prioritize semantic quality over permissive acceptance.

### Implementation Notes
Pending.

### Evidence / Links
Pending.
