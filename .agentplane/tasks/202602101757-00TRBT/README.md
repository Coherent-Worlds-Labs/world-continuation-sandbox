---
id: "202602101757-00TRBT"
title: "Enforce discrete fact-count contract"
status: "DOING"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T18:04:10.947Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX1 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T18:27:13.106Z"
  updated_by: "CODER"
  note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
commit: null
comments:
  -
    author: "CODER"
    body: "Start: Replace fractional fact telemetry with integer contract and enforce cadence for new facts."
events:
  -
    type: "status"
    at: "2026-02-10T18:09:49.733Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Replace fractional fact telemetry with integer contract and enforce cadence for new facts."
  -
    type: "verify"
    at: "2026-02-10T18:27:13.106Z"
    author: "CODER"
    state: "ok"
    note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
doc_version: 2
doc_updated_at: "2026-02-10T18:27:13.109Z"
doc_updated_by: "CODER"
description: "Remove fractional fact accounting and require integer new_fact_count with cadence guarantees."
id_source: "generated"
---
## Summary

Replace fractional fact accounting with discrete fact-count semantics and cadence guarantees.

## Scope

Verifier/orchestrator telemetry and acceptance contracts for new fact counts.

## Plan

1) Enforce integer new_fact_count in progression signals. 2) Remove any averaging that produces fractional counts. 3) Add cadence rule requiring >=1 new fact at least once per K steps. 4) Update CLI/API output to show integer counts. 5) Add tests for count integrity and cadence.

## Risks

Strict fact-count gating may reject too many candidates initially. Mitigate with calibrated cadence windows and clear errors.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T18:27:13.106Z — VERIFY — ok

By: CODER

Note: All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T18:09:49.733Z, excerpt_hash=sha256:0cc0da06c7f8138ee4f52ac5d4df46d0b781ef131528b2b722d569873115206b

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert discrete-count gating and restore previous counting path if regressions occur.

## Verify Steps

- Run tests ensuring new_fact_count is integer-valued in accepted-step telemetry. - Run simulation and confirm no 0.5 values appear in logs.

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
