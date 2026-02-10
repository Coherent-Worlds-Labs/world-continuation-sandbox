---
id: "202602101955-5Y76H1"
title: "Enforce reference accumulation policy"
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
  updated_at: "2026-02-10T19:58:44.553Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX2 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:07:59.300Z"
  updated_by: "CODER"
  note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
commit:
  hash: "861c9ce98c77a11d5e0a59dfa7a7e6c77ce57d6d"
  message: "✅ YJYT9K backend: implement FIX2 hard fact-object progression constraints"
comments:
  -
    author: "CODER"
    body: "Start: Implement strict reference accumulation thresholds over step/dependency depth."
  -
    author: "CODER"
    body: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
events:
  -
    type: "status"
    at: "2026-02-10T20:00:23.138Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implement strict reference accumulation thresholds over step/dependency depth."
  -
    type: "verify"
    at: "2026-02-10T20:07:59.300Z"
    author: "CODER"
    state: "ok"
    note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
  -
    type: "status"
    at: "2026-02-10T20:08:34.626Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
doc_version: 2
doc_updated_at: "2026-02-10T20:08:34.626Z"
doc_updated_by: "CODER"
description: "Require minimum anchor references by step/depth and reject non-referential continuations."
id_source: "generated"
---
## Summary

Enforce minimum anchor-reference accumulation over time.

## Scope

Reference policy thresholds by step/depth and hard reject when refs are below required minimum.

## Plan

1) Define refs thresholds (n>=2 => refs>=1, n>=5 => refs>=2). 2) Integrate thresholds into verifier policy. 3) Reject candidates violating refs policy. 4) Emit refs diagnostics in traces/UI.

## Risks

Early steps may fail without available anchors; mitigate with warm-up thresholds.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:07:59.300Z — VERIFY — ok

By: CODER

Note: FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed).

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:00:23.138Z, excerpt_hash=sha256:a249c250e84a5175e4fd130960aa7b868097b7033253b4e26bd4e4f4c224f531

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert strict reference thresholds to previous soft behavior.

## Context

Derived from sow/FIX2 - factobject.txt to eliminate pseudo-facts and enforce irreversible structural world progression.

## Verify Steps

- Add tests for refs threshold enforcement at different heights. - Confirm runtime trace reports refs and rejects missing references.

## Notes

### Approvals / Overrides
- Plan approved by user. No overrides requested.

### Decisions
- FIX2 enforces hard structural progression constraints over stylistic quality.

### Implementation Notes
- Pending implementation in this task.

### Evidence / Links
- Source analysis: sow/FIX2 - factobject.txt
