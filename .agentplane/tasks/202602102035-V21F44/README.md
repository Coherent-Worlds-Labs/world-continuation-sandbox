---
id: "202602102035-V21F44"
title: "Add deterministic escape mode for reject streak"
result_summary: "Deterministic escape mode shipped"
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T20:38:39.148Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX3 implementation scope and verification contract."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:49:27.864Z"
  updated_by: "CODER"
  note: "Verified: deterministic escape mode policy added for reject streaks with forced directive set and stricter prompt contract."
commit:
  hash: "c65286f159b61509b3f01d106d6ec68794a83656"
  message: "✅ WBKPRX backend: implement FIX3 fact-centric progression and escape mode"
comments:
  -
    author: "CODER"
    body: "Start: Add deterministic break-glass escape mode for reject streaks with constrained directives and strict response contract."
  -
    author: "CODER"
    body: "Verified: Added deterministic break-glass path for reject streak with forced directives and stricter LLM output contract."
events:
  -
    type: "status"
    at: "2026-02-10T20:39:02.741Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Add deterministic break-glass escape mode for reject streaks with constrained directives and strict response contract."
  -
    type: "verify"
    at: "2026-02-10T20:49:27.864Z"
    author: "CODER"
    state: "ok"
    note: "Verified: deterministic escape mode policy added for reject streaks with forced directive set and stricter prompt contract."
  -
    type: "status"
    at: "2026-02-10T20:50:34.179Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: Added deterministic break-glass path for reject streak with forced directives and stricter LLM output contract."
doc_version: 2
doc_updated_at: "2026-02-10T20:50:34.179Z"
doc_updated_by: "CODER"
description: "Force directive and stricter output contract after repeated rejects to escape local minima."
id_source: "generated"
---
## Summary

Add deterministic break-glass mode on reject streak.

## Scope

taskgen directive selection, orchestration retry strategy, and prover output contract strictness.

## Plan

1. Detect reject streak threshold and activate escape mode.
2. Force directive types from constrained set for concrete progression.
3. Tighten prompt contract for strict JSON fact output under escape mode.
4. Record escape-mode diagnostics in candidate traces.

## Risks

Risk: reduced narrative variety when escape mode overfires. Mitigation: threshold tuning and bounded activation window.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:49:27.864Z — VERIFY — ok

By: CODER

Note: Verified: deterministic escape mode policy added for reject streaks with forced directive set and stricter prompt contract.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:39:02.741Z, excerpt_hash=sha256:0f8f439353fe7bf2e0f4d4ad4003be66429b8440da459b35fcfdae94dbacd933

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Disable escape mode path via config or revert taskgen/orchestrator changes if behavior degrades.

## Context

Implements FIX3 emergency strategy to escape local minima under repeated rejection.

## Verify Steps

1. Run python -m pytest tests -q.
2. Run deterministic simulation seed that previously deadlocked.
3. Confirm escape mode activation and eventual accepted progression.

## Notes

### Approvals / Overrides
No overrides requested.

### Decisions
Apply FIX3 as fact-centric progression architecture.

### Implementation Notes
Pending implementation.

### Evidence / Links
Pending.
