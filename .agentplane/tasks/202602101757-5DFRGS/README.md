---
id: "202602101757-5DFRGS"
title: "Implement ontological stagnation metric"
status: "DOING"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T18:04:13.141Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX1 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T18:27:15.053Z"
  updated_by: "CODER"
  note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
commit: null
comments:
  -
    author: "CODER"
    body: "Start: Implement ontological stagnation metric and wire it into runtime decision pressure."
events:
  -
    type: "status"
    at: "2026-02-10T18:09:51.676Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implement ontological stagnation metric and wire it into runtime decision pressure."
  -
    type: "verify"
    at: "2026-02-10T18:27:15.053Z"
    author: "CODER"
    state: "ok"
    note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
doc_version: 2
doc_updated_at: "2026-02-10T18:27:15.055Z"
doc_updated_by: "CODER"
description: "Add world-structure stagnation metric and integrate it into controller/taskgen pressure."
id_source: "generated"
---
## Summary

Implement ontological stagnation metric based on world-structure deltas.

## Scope

Metrics and controller integration for non-lexical stagnation detection.

## Plan

1) Define ontological stagnation inputs: entity growth, anchor growth, agent-structure changes. 2) Compute windowed stagnation score. 3) Integrate score into controller/taskgen pressure. 4) Expose stagnation diagnostics in CLI/API. 5) Add tests for true/false positive scenarios.

## Risks

False positives could force unnecessary mode changes. Mitigate with windowed thresholds and hysteresis.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T18:27:15.053Z — VERIFY — ok

By: CODER

Note: All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T18:09:51.676Z, excerpt_hash=sha256:30c6d3d730b6274482d321221d31939903e33ebc805195d8b871c10c235c8eb6

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert stagnation metric/controller wiring to previous heuristic behavior.

## Verify Steps

- Run tests covering stagnation score transitions across synthetic sequences. - Run simulation and confirm stagnation reacts to structural inactivity, not wording differences alone.

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
