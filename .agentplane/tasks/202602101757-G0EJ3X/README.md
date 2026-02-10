---
id: "202602101757-G0EJ3X"
title: "Enforce structural operator progression policy"
result_summary: "FIX1 anti-treadmill controls implemented and validated."
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T18:04:10.278Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX1 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T18:27:12.265Z"
  updated_by: "CODER"
  note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
commit:
  hash: "71aea9c3368cc0525fd40e2fbe8dce946c970686"
  message: "✅ D0C9NA backend: implement FIX1 anti-treadmill progression stack"
comments:
  -
    author: "CODER"
    body: "Start: Implement directive family rotation policy and anti-repeat constraints to block treadmill directive reuse."
  -
    author: "CODER"
    body: "Verified: Implemented structural anti-treadmill controls and validated by automated tests plus simulation smoke run."
events:
  -
    type: "status"
    at: "2026-02-10T18:09:49.093Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implement directive family rotation policy and anti-repeat constraints to block treadmill directive reuse."
  -
    type: "verify"
    at: "2026-02-10T18:27:12.265Z"
    author: "CODER"
    state: "ok"
    note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
  -
    type: "status"
    at: "2026-02-10T18:29:29.418Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: Implemented structural anti-treadmill controls and validated by automated tests plus simulation smoke run."
doc_version: 2
doc_updated_at: "2026-02-10T18:29:29.418Z"
doc_updated_by: "CODER"
description: "Implement directive family rotation and anti-repeat constraints to prevent semantic treadmill behavior."
id_source: "generated"
---
## Summary

Add structural operator progression logic that enforces directive variety and anti-repeat constraints.

## Scope

Task generation and orchestration policy for directive selection and repetition control.

## Plan

1) Define directive families and rotation policy. 2) Enforce no more than two consecutive identical directive types. 3) Integrate policy with mode-aware selection. 4) Emit diagnostics for applied policy decisions. 5) Add tests for repetition constraints.

## Risks

Over-constraining directives may reduce acceptance rate. Mitigate by using configurable thresholds and adaptive fallback.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T18:27:12.265Z — VERIFY — ok

By: CODER

Note: All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T18:09:49.093Z, excerpt_hash=sha256:51bdda399ea5c6db780f43cf9376dcc732a20b0f94410f29eedc8ac913229305

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert directive-rotation policy changes and restore previous task generation behavior.

## Verify Steps

- Run unit tests covering directive rotation and anti-repeat behavior. - Run simulation smoke test to confirm no directive repeats >2 times consecutively in sample run.

## Context

Derived from sow/FIX1 - threadmill analysis after plan approval. Objective: eliminate semantic treadmill by enforcing world-structure progression.

## Notes

### Approvals / Overrides
- Plan approved by user. No overrides requested.

### Decisions
- Prioritize structural world progression over wording diversity.

### Implementation Notes
- Pending implementation in this task.

### Evidence / Links
- Source analysis: sow/FIX1 - threadmill.txt
