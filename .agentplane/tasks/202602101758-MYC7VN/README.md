---
id: "202602101758-MYC7VN"
title: "Add AgentCommitment directive"
status: "DOING"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T18:04:54.804Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX1 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T18:27:15.730Z"
  updated_by: "CODER"
  note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
commit: null
comments:
  -
    author: "CODER"
    body: "Start: Add AgentCommitment directive with persistent continuity requirements and verifier checks."
events:
  -
    type: "status"
    at: "2026-02-10T18:09:52.313Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Add AgentCommitment directive with persistent continuity requirements and verifier checks."
  -
    type: "verify"
    at: "2026-02-10T18:27:15.730Z"
    author: "CODER"
    state: "ok"
    note: "All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry."
doc_version: 2
doc_updated_at: "2026-02-10T18:27:15.734Z"
doc_updated_by: "CODER"
description: "Introduce persistent public-commitment operator and enforce continuity constraints for downstream steps."
id_source: "generated"
---
## Summary

Add AgentCommitment directive with persistent downstream consequences.

## Scope

Directive definition, generation prompting, persistence semantics, and verifier expectations.

## Plan

1) Add AgentCommitment directive type and selection hooks. 2) Define output contract for commitment actor/claim/public channel. 3) Persist commitment as anchor. 4) Enforce follow-up references in later steps. 5) Add tests for commitment continuity.

## Risks

Commitments may drift if not referenced consistently. Mitigate by making commitments anchor-backed and non-forgettable.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T18:27:15.730Z — VERIFY — ok

By: CODER

Note: All automated checks passed: python -m pytest tests -q (15 passed). Smoke run passed: run_simulation produced integer fact counts, anchor references, and ontological stagnation telemetry.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T18:09:52.313Z, excerpt_hash=sha256:55ac3ff25913a606ecb0f8b95adccd0b8b36fcbade260ab37e5d15957b7c0799

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Remove AgentCommitment directive additions and restore prior directive set.

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

## Verify Steps

- Run unit tests for AgentCommitment generation and persistence semantics. - Run simulation sample and confirm commitments appear and are referenced in subsequent accepted steps.
