---
id: "202602111211-893HE0"
title: "Refactor orchestrator to one-candidate verification flow"
result_summary: "Implemented FIX7 orchestration flow refactor."
risk_level: "med"
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-11T12:12:30.828Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX7 flow refactor plan."
verification:
  state: "ok"
  updated_at: "2026-02-11T12:19:12.163Z"
  updated_by: "CODER"
  note: "Verified: orchestrator now selects one canonical candidate per step and runs verifier cascade only for that candidate; cross-prover hard-fail coupling removed."
commit:
  hash: "b81ce4fd615610781b6d6a7a2a9ed07895dca298"
  message: "✅ 893HE0 backend: implement FIX7 single-candidate protocol and contracts"
comments:
  -
    author: "CODER"
    body: "Start: Refactoring simulation flow to select one canonical candidate per step and verify only that candidate."
  -
    author: "CODER"
    body: "Verified: one-candidate-per-step protocol is implemented; only selected candidate is verified and committed for each step."
events:
  -
    type: "status"
    at: "2026-02-11T12:12:39.571Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Refactoring simulation flow to select one canonical candidate per step and verify only that candidate."
  -
    type: "verify"
    at: "2026-02-11T12:19:12.163Z"
    author: "CODER"
    state: "ok"
    note: "Verified: orchestrator now selects one canonical candidate per step and runs verifier cascade only for that candidate; cross-prover hard-fail coupling removed."
  -
    type: "status"
    at: "2026-02-11T12:19:48.106Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: one-candidate-per-step protocol is implemented; only selected candidate is verified and committed for each step."
doc_version: 2
doc_updated_at: "2026-02-11T12:19:48.106Z"
doc_updated_by: "CODER"
description: "Select a single canonical candidate per step and run verifier cascade only for that candidate; remove cross-prover hard-fail coupling."
id_source: "generated"
---
## Summary

Implement one-candidate-per-step verification protocol in orchestrator.

## Scope

In scope: orchestrator/aggregation flow and candidate selection diagnostics. Out of scope: UI redesign.

## Plan

1) Generate N candidates. 2) Prefilter candidates by local schema validity signals. 3) Select canonical candidate*. 4) Run verifier cascade only on candidate*. 5) Preserve traces for observability.

## Risks

Risk: changed acceptance rate. Mitigation: keep deterministic selection rules and preserve reason diagnostics.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-11T12:19:12.163Z — VERIFY — ok

By: CODER

Note: Verified: orchestrator now selects one canonical candidate per step and runs verifier cascade only for that candidate; cross-prover hard-fail coupling removed.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-11T12:12:39.571Z, excerpt_hash=sha256:47b32ded95fb17c3fa2c4c3c70fefae247b1bd6e45078ed3be9db88df3f5a766

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert flow refactor commit and restore previous loop behavior.

## Context

FIX7 identified rejection ambiguity caused by cross-prover hard-fail coupling.

## Verify Steps

1) $env:PYTHONPATH=src; python -m pytest tests -q`n2) $env:PYTHONPATH=src; python scripts/run_simulation.py --steps 10 --db data/fix7_flow_smoke.db --seed 5

## Notes

### Decisions`n- Acceptance decision must reference one canonical candidate per step.
