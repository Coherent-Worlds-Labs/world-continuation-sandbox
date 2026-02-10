---
id: "202602101956-0E4AN8"
title: "Expose progress diagnostics in API and Story UI"
result_summary: "FIX2 constraints delivered and validated."
status: "DONE"
priority: "med"
owner: "CODER"
depends_on: []
tags:
  - "frontend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T19:58:46.405Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX2 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:08:01.724Z"
  updated_by: "CODER"
  note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
commit:
  hash: "861c9ce98c77a11d5e0a59dfa7a7e6c77ce57d6d"
  message: "✅ YJYT9K backend: implement FIX2 hard fact-object progression constraints"
comments:
  -
    author: "CODER"
    body: "Start: Expose FIX2 progress diagnostics in API and Story View UI with fact/ref/reject visibility."
  -
    author: "CODER"
    body: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
events:
  -
    type: "status"
    at: "2026-02-10T20:00:25.507Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Expose FIX2 progress diagnostics in API and Story View UI with fact/ref/reject visibility."
  -
    type: "verify"
    at: "2026-02-10T20:08:01.724Z"
    author: "CODER"
    state: "ok"
    note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
  -
    type: "status"
    at: "2026-02-10T20:08:38.226Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
doc_version: 2
doc_updated_at: "2026-02-10T20:08:38.226Z"
doc_updated_by: "CODER"
description: "Add API/UI diagnostics for fact objects, refs, and progress-gate accept/reject reasons."
id_source: "generated"
---
## Summary

Expose FIX2 progress diagnostics in API and Story View UI.

## Scope

API routes and UI rendering for Fact Objects, refs, and progress gate reasons.

## Plan

1) Add API payload fields for progress-gate diagnostics. 2) Add Story View panels for current fact object, refs, and reject reasons. 3) Keep rendering lightweight and readable.

## Risks

UI noise; mitigate with concise formatting and filters.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:08:01.724Z — VERIFY — ok

By: CODER

Note: FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed).

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:00:25.507Z, excerpt_hash=sha256:26313f2a7891a3915db272f7188e6a8f406adeb8c15439189a966407b75f9f72

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert diagnostic endpoints/panels.

## Context

Derived from sow/FIX2 - factobject.txt to eliminate pseudo-facts and enforce irreversible structural world progression.

## Verify Steps

- Verify API returns expected diagnostic fields. - Verify UI renders fact objects/refs/reasons for selected branch.

## Notes

### Approvals / Overrides
- Plan approved by user. No overrides requested.

### Decisions
- FIX2 enforces hard structural progression constraints over stylistic quality.

### Implementation Notes
- Pending implementation in this task.

### Evidence / Links
- Source analysis: sow/FIX2 - factobject.txt
