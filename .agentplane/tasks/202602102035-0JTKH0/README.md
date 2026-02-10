---
id: "202602102035-0JTKH0"
title: "Expose fact-centric diagnostics in CLI and API"
result_summary: "Diagnostics surface updated"
status: "DONE"
priority: "med"
owner: "CODER"
depends_on: []
tags:
  - "frontend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T20:38:39.132Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX3 implementation scope and verification contract."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:49:28.109Z"
  updated_by: "CODER"
  note: "Verified: API and CLI expose FIX3 diagnostics (fact similarities, novelty components, refs_quality, escape mode)."
commit:
  hash: "c65286f159b61509b3f01d106d6ec68794a83656"
  message: "✅ WBKPRX backend: implement FIX3 fact-centric progression and escape mode"
comments:
  -
    author: "CODER"
    body: "Start: Expose fact-centric progression diagnostics in API and CLI trace outputs for operator visibility."
  -
    author: "CODER"
    body: "Verified: Added FIX3 diagnostics fields to CLI and API payloads including novelty components, refs_quality, and escape state."
events:
  -
    type: "status"
    at: "2026-02-10T20:39:02.755Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Expose fact-centric progression diagnostics in API and CLI trace outputs for operator visibility."
  -
    type: "verify"
    at: "2026-02-10T20:49:28.109Z"
    author: "CODER"
    state: "ok"
    note: "Verified: API and CLI expose FIX3 diagnostics (fact similarities, novelty components, refs_quality, escape mode)."
  -
    type: "status"
    at: "2026-02-10T20:50:34.179Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: Added FIX3 diagnostics fields to CLI and API payloads including novelty components, refs_quality, and escape state."
doc_version: 2
doc_updated_at: "2026-02-10T20:50:34.179Z"
doc_updated_by: "CODER"
description: "Surface fact_object, novelty components, refs quality, and gate reasons in progress outputs."
id_source: "generated"
---
## Summary

Expose FIX3 diagnostics in API/CLI/UI outputs.

## Scope

api_server diagnostics payload and scripts/run_simulation.py trace rendering.

## Plan

1. Add novelty component fields and fact-centric similarity diagnostics.
2. Surface gate reasons and fact_object summary in API response.
3. Print concise progress diagnostics in CLI stream.
4. Keep output readable and stable for operators.

## Risks

Risk: noisy console output. Mitigation: compact formatting and stable keys.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:49:28.109Z — VERIFY — ok

By: CODER

Note: Verified: API and CLI expose FIX3 diagnostics (fact similarities, novelty components, refs_quality, escape mode).

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:39:02.755Z, excerpt_hash=sha256:7e729b3d38928fb56d6a855c347a3b208e62852b709f2e30a2ff7609e25fbd21

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert diagnostics field additions if they break consumer expectations.

## Context

Needed for visibility into why candidates pass/fail under FIX3 gates.

## Verify Steps

1. Run python -m pytest tests -q.
2. Run simulation and inspect CLI trace fields.
3. Query diagnostics API and verify new fields are present.

## Notes

### Approvals / Overrides
No overrides requested.

### Decisions
Apply FIX3 as fact-centric progression architecture.

### Implementation Notes
Pending implementation.

### Evidence / Links
Pending.
