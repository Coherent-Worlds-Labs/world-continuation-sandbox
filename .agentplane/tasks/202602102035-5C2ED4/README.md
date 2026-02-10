---
id: "202602102035-5C2ED4"
title: "Refactor novelty gate to fact-first formulas"
result_summary: "Fact-first novelty gate shipped"
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T20:38:31.226Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX3 implementation scope and verification contract."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:49:18.553Z"
  updated_by: "CODER"
  note: "Verified: Novelty gate now computes fact-first novelty components and hard fact-repeat constraints; pytest suite passed."
commit:
  hash: "c65286f159b61509b3f01d106d6ec68794a83656"
  message: "✅ WBKPRX backend: implement FIX3 fact-centric progression and escape mode"
comments:
  -
    author: "CODER"
    body: "Start: Refactor novelty gating to use canonical fact-object metrics, including hard repeat checks and explicit novelty components."
  -
    author: "CODER"
    body: "Verified: Novelty gate now uses canonical fact metrics, hard fact-repeat barrier, and phased novelty thresholds; tests are passing."
events:
  -
    type: "status"
    at: "2026-02-10T20:38:54.368Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Refactor novelty gating to use canonical fact-object metrics, including hard repeat checks and explicit novelty components."
  -
    type: "verify"
    at: "2026-02-10T20:49:18.553Z"
    author: "CODER"
    state: "ok"
    note: "Verified: Novelty gate now computes fact-first novelty components and hard fact-repeat constraints; pytest suite passed."
  -
    type: "status"
    at: "2026-02-10T20:50:23.208Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: Novelty gate now uses canonical fact metrics, hard fact-repeat barrier, and phased novelty thresholds; tests are passing."
doc_version: 2
doc_updated_at: "2026-02-10T20:50:23.208Z"
doc_updated_by: "CODER"
description: "Implement sim_fact/novel_fact/novel_type/novel_refs formulas with hard repeat rules and canonicalization."
id_source: "generated"
---
## Summary

Refactor novelty gate to fact-first formulas and hard rules.

## Scope

verifiers novelty logic, canonical fact comparison helpers, and related policy wiring.

## Plan

1. Compute sim_fact/novel_fact over canonical fact text.
2. Add novel_type and novel_refs contributions.
3. Apply hard repeat by sim_fact and conditional scene-repeat rule.
4. Emit detailed novelty component signals for diagnostics and tests.

## Risks

Risk: over-strict thresholds cause false rejects. Mitigation: configurable thresholds in world config and deterministic tests.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:49:18.553Z — VERIFY — ok

By: CODER

Note: Verified: Novelty gate now computes fact-first novelty components and hard fact-repeat constraints; pytest suite passed.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:38:54.368Z, excerpt_hash=sha256:dcf7674118dadfc15d9f75ca49d37f388c690dfca332c373300981ba8a426518

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert verifier formula changes and restore previous novelty gate while retaining diagnostics if needed.

## Context

Implements FIX3 requirement to judge novelty by fact objects, not phrasing.

## Verify Steps

1. Run python -m pytest tests -q.
2. Validate new signals exist in verification outputs.
3. Smoke run with LLM-disabled fallback confirms accepted progression over multiple steps.

## Notes

### Approvals / Overrides
No overrides requested.

### Decisions
Apply FIX3 as fact-centric progression architecture.

### Implementation Notes
Pending implementation.

### Evidence / Links
Pending.
