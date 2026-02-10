---
id: "202602102156-EJG6RH"
title: "Implement FIX6 gate refactor and reason codes"
result_summary: "Implemented FIX6 gate refactor and reject diagnostics."
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
  updated_at: "2026-02-10T21:58:35.417Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX6 gate refactor plan."
verification:
  state: "ok"
  updated_at: "2026-02-10T22:08:24.668Z"
  updated_by: "CODER"
  note: "Verified: gate predicates are separated, novelty check is pure, and structured reason codes/details are propagated to traces and decisions. Tests passed and simulation smoke run completed."
commit:
  hash: "07d230dd01699a9690f1e637b6993f2cbbcb8d42"
  message: "✅ EJG6RH backend: implement FIX6 gate transparency and protocol diagnostics"
comments:
  -
    author: "CODER"
    body: "Start: Refactoring verifier gate predicates and adding structured reject diagnostics for FIX6 with step-aware refs policy."
  -
    author: "CODER"
    body: "Verified: FIX6 gate predicates were split and novelty/progress/schema diagnostics are now explicit and machine-readable."
events:
  -
    type: "status"
    at: "2026-02-10T21:58:47.131Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Refactoring verifier gate predicates and adding structured reject diagnostics for FIX6 with step-aware refs policy."
  -
    type: "verify"
    at: "2026-02-10T22:08:24.668Z"
    author: "CODER"
    state: "ok"
    note: "Verified: gate predicates are separated, novelty check is pure, and structured reason codes/details are propagated to traces and decisions. Tests passed and simulation smoke run completed."
  -
    type: "status"
    at: "2026-02-10T22:09:02.936Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: FIX6 gate predicates were split and novelty/progress/schema diagnostics are now explicit and machine-readable."
doc_version: 2
doc_updated_at: "2026-02-10T22:09:02.936Z"
doc_updated_by: "CODER"
description: "Refactor verifier gates into independent predicates, enforce pure novelty check, add structured reason_codes/details, and wire step-aware progress policy."
id_source: "generated"
---
## Summary

Refactor verifier gating into explicit predicates and produce machine-readable reject diagnostics.

## Scope

In scope: src/pocwc/verifiers.py, src/pocwc/orchestrator.py, scripts/run_simulation.py for gate/report wiring. Out of scope: UI redesign.

## Plan

1) Split novelty/progress/schema/evidence/type checks into independent predicates. 2) Make novelty gate compare novelty_total against novelty_min only. 3) Add reason_codes/details payload and propagate to trace and CLI. 4) Implement step-aware refs policy (step1 refs_min=0, step2+ refs_min=1 by config).

## Risks

Risk: stricter gates can reduce acceptance rate. Mitigation: add transparent details and configurable thresholds in world config.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T22:08:24.668Z — VERIFY — ok

By: CODER

Note: Verified: gate predicates are separated, novelty check is pure, and structured reason codes/details are propagated to traces and decisions. Tests passed and simulation smoke run completed.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T21:58:47.131Z, excerpt_hash=sha256:89c33bb61e7a12703cc655d03121c66c23a798d92059608e62ab678fa63c350d

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert FIX6 gate refactor commit and restore previous verifier behavior if regression is detected.

## Context

Based on FIX6 findings: novelty failures are opaque and likely conflated with non-novelty checks.

## Verify Steps

1) python -m pytest tests -q`n2) python scripts/run_simulation.py --steps 8 --db data/fix6_smoke.db --seed 7

## Notes

### Decisions`n- Reject reasons must be explicit and deterministic for every hard fail.
