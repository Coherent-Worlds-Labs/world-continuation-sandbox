---
id: "202602101757-9NRP9V"
title: "Introduce persistent world anchors"
status: "DOING"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T18:04:11.667Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX1 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T18:27:13.775Z"
  updated_by: "CODER"
  note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
commit: null
comments:
  -
    author: "CODER"
    body: "Start: Add persistent world-anchor schema and anchor reference enforcement across accepted steps."
events:
  -
    type: "status"
    at: "2026-02-10T18:09:50.374Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Add persistent world-anchor schema and anchor reference enforcement across accepted steps."
  -
    type: "verify"
    at: "2026-02-10T18:27:13.775Z"
    author: "CODER"
    state: "ok"
    note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
doc_version: 2
doc_updated_at: "2026-02-10T18:27:13.778Z"
doc_updated_by: "CODER"
description: "Add explicit world-anchor schema and generation/verification contracts based on anchor IDs."
id_source: "generated"
---
## Summary

Formalize persistent world anchors and enforce reference-based world evolution.

## Scope

Anchor schema, persistence, prover prompt contract, and verifier reference checks.

## Plan

1) Define world anchor schema with stable IDs and metadata. 2) Persist anchors with non-disappearing lifecycle semantics. 3) Require candidate outputs to reference prior anchors when evolving context. 4) Reject generic rephrasing with no anchor linkage. 5) Add tests for anchor persistence and reference validity.

## Risks

Schema changes can break backward compatibility. Mitigate with additive schema and tolerant reads.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T18:27:13.775Z — VERIFY — ok

By: CODER

Note: All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T18:09:50.374Z, excerpt_hash=sha256:09baa6b161e430030ac377d29452d1830c41ecd020ff913e4081ae26e7caeea9

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert anchor schema additions and related generator/verifier checks.

## Verify Steps

- Run tests for anchor creation, persistence, and retrieval. - Run simulation sample and confirm new steps reference existing anchor IDs.

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
