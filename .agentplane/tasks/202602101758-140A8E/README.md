---
id: "202602101758-140A8E"
title: "Story UI: active facts and anchors panel"
result_summary: "FIX1 anti-treadmill controls implemented and validated."
status: "DONE"
priority: "med"
owner: "CODER"
depends_on: []
tags:
  - "frontend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T18:04:14.683Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX1 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T18:27:16.354Z"
  updated_by: "CODER"
  note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
commit:
  hash: "71aea9c3368cc0525fd40e2fbe8dce946c970686"
  message: "✅ D0C9NA backend: implement FIX1 anti-treadmill progression stack"
comments:
  -
    author: "CODER"
    body: "Start: Expose active facts/anchors in API and Story View UI for world-state visibility."
  -
    author: "CODER"
    body: "Verified: Implemented structural anti-treadmill controls and validated by automated tests plus simulation smoke run."
events:
  -
    type: "status"
    at: "2026-02-10T18:09:53.039Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Expose active facts/anchors in API and Story View UI for world-state visibility."
  -
    type: "verify"
    at: "2026-02-10T18:27:16.354Z"
    author: "CODER"
    state: "ok"
    note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
  -
    type: "status"
    at: "2026-02-10T18:29:33.760Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: Implemented structural anti-treadmill controls and validated by automated tests plus simulation smoke run."
doc_version: 2
doc_updated_at: "2026-02-10T18:29:33.760Z"
doc_updated_by: "CODER"
description: "Expose and render active facts/anchors in API and UI to visualize world-state accumulation."
id_source: "generated"
---
## Summary

Expose active facts and anchors in API/UI for explicit world-state observability.

## Scope

API endpoint additions and Story View panel updates in frontend.

## Plan

1) Add API route(s) for active facts/anchors by branch. 2) Include key metadata: id, type, introduced step, status, references. 3) Add Story View panel for active facts. 4) Keep UI responsive for desktop and mobile layout. 5) Add lightweight tests/manual checklist.

## Risks

UI clutter may reduce readability. Mitigate with compact fact cards and branch filtering.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T18:27:16.354Z — VERIFY — ok

By: CODER

Note: All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T18:09:53.039Z, excerpt_hash=sha256:f7e8dcc230efc04be41f138c3a5cd4bfac75e66d8fb41af8fd8a78cf64b12b61

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert API endpoint and UI panel changes.

## Verify Steps

- Validate API responses for active facts on populated DB. - Verify UI renders active facts list and updates with branch selection.

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
