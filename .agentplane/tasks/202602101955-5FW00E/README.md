---
id: "202602101955-5FW00E"
title: "Implement fact equivalence rejection"
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
  updated_at: "2026-02-10T19:58:45.520Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX2 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:08:00.587Z"
  updated_by: "CODER"
  note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
commit:
  hash: "861c9ce98c77a11d5e0a59dfa7a7e6c77ce57d6d"
  message: "✅ YJYT9K backend: implement FIX2 hard fact-object progression constraints"
comments:
  -
    author: "CODER"
    body: "Start: Implement fact equivalence detector and reject semantically duplicate facts as non-progress."
  -
    author: "CODER"
    body: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
events:
  -
    type: "status"
    at: "2026-02-10T20:00:24.361Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implement fact equivalence detector and reject semantically duplicate facts as non-progress."
  -
    type: "verify"
    at: "2026-02-10T20:08:00.587Z"
    author: "CODER"
    state: "ok"
    note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
  -
    type: "status"
    at: "2026-02-10T20:08:36.210Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
doc_version: 2
doc_updated_at: "2026-02-10T20:08:36.210Z"
doc_updated_by: "CODER"
description: "Detect semantically equivalent facts and reject them as non-progressing duplicates."
id_source: "generated"
---
## Summary

Reject semantically equivalent facts as non-progressing duplicates.

## Scope

Fact equivalence detector over type/content/reference features with optional semantic checks.

## Plan

1) Define fact equivalence function over normalized fields. 2) Compare candidate fact to active anchors/history. 3) Reject equivalent facts and record reason. 4) Add optional semantic augmentation when embeddings are available.

## Risks

Equivalence false matches; mitigate with feature-weighted thresholds and deterministic fallback path.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:08:00.587Z — VERIFY — ok

By: CODER

Note: FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed).

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:00:24.361Z, excerpt_hash=sha256:b0710c12d3c4028f5c98e7064189ec5d446c3cb42b71b6314b09f2de8302d4bc

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Disable equivalence rejection and keep only basic novelty checks.

## Context

Derived from sow/FIX2 - factobject.txt to eliminate pseudo-facts and enforce irreversible structural world progression.

## Verify Steps

- Add tests for equivalent/non-equivalent fact pairs. - Confirm equivalent fact attempts are rejected in simulation traces.

## Notes

### Approvals / Overrides
- Plan approved by user. No overrides requested.

### Decisions
- FIX2 enforces hard structural progression constraints over stylistic quality.

### Implementation Notes
- Pending implementation in this task.

### Evidence / Links
- Source analysis: sow/FIX2 - factobject.txt
