---
id: "202602101955-1SM9EH"
title: "Add hard repetition barrier and nonlinear penalty"
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
  updated_at: "2026-02-10T19:58:45.027Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX2 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:07:59.879Z"
  updated_by: "CODER"
  note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
commit:
  hash: "861c9ce98c77a11d5e0a59dfa7a7e6c77ce57d6d"
  message: "✅ YJYT9K backend: implement FIX2 hard fact-object progression constraints"
comments:
  -
    author: "CODER"
    body: "Start: Add hard similarity reject and nonlinear repetition penalty for near-duplicate candidates."
  -
    author: "CODER"
    body: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
events:
  -
    type: "status"
    at: "2026-02-10T20:00:23.792Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Add hard similarity reject and nonlinear repetition penalty for near-duplicate candidates."
  -
    type: "verify"
    at: "2026-02-10T20:07:59.879Z"
    author: "CODER"
    state: "ok"
    note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
  -
    type: "status"
    at: "2026-02-10T20:08:35.356Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
doc_version: 2
doc_updated_at: "2026-02-10T20:08:35.356Z"
doc_updated_by: "CODER"
description: "Reject near-duplicate steps above hard similarity threshold and strengthen high-similarity penalties."
id_source: "generated"
---
## Summary

Add hard similarity barrier and nonlinear repetition penalty.

## Scope

Similarity gating and penalty math used during candidate evaluation.

## Plan

1) Add hard reject when step similarity exceeds configured threshold. 2) Replace linear penalty with nonlinear penalty for high similarity band. 3) Ensure decision reasons report repetition gate activations.

## Risks

False positives may reject legitimate continuation; mitigate with threshold calibration and exemptions only by policy.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:07:59.879Z — VERIFY — ok

By: CODER

Note: FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed).

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:00:23.792Z, excerpt_hash=sha256:80480e7122e3069a09fe48d042088ba174cb460b4ca5b52484ac5667a23341e7

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Restore linear penalty and remove hard similarity cutoff.

## Context

Derived from sow/FIX2 - factobject.txt to eliminate pseudo-facts and enforce irreversible structural world progression.

## Verify Steps

- Add tests where similarity=1.0 guarantees rejection. - Validate smoke run no exact duplicate accepted when gate active.

## Notes

### Approvals / Overrides
- Plan approved by user. No overrides requested.

### Decisions
- FIX2 enforces hard structural progression constraints over stylistic quality.

### Implementation Notes
- Pending implementation in this task.

### Evidence / Links
- Source analysis: sow/FIX2 - factobject.txt
