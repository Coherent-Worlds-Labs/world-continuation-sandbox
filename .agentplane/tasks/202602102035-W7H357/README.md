---
id: "202602102035-W7H357"
title: "Implement refs quality and height policy"
result_summary: "Refs quality progression policy shipped"
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T20:38:31.253Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX3 implementation scope and verification contract."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:49:18.560Z"
  updated_by: "CODER"
  note: "Verified: refs_count and refs_quality progression policy enforced by height and exposed in diagnostics; smoke run confirms refs growth."
commit:
  hash: "c65286f159b61509b3f01d106d6ec68794a83656"
  message: "✅ WBKPRX backend: implement FIX3 fact-centric progression and escape mode"
comments:
  -
    author: "CODER"
    body: "Start: Implement refs count and refs quality accumulation policy by height with deterministic thresholds from config."
  -
    author: "CODER"
    body: "Verified: refs_count plus refs_quality policies are enforced by height and surfaced in diagnostics; smoke output confirms accumulation."
events:
  -
    type: "status"
    at: "2026-02-10T20:38:54.412Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implement refs count and refs quality accumulation policy by height with deterministic thresholds from config."
  -
    type: "verify"
    at: "2026-02-10T20:49:18.560Z"
    author: "CODER"
    state: "ok"
    note: "Verified: refs_count and refs_quality progression policy enforced by height and exposed in diagnostics; smoke run confirms refs growth."
  -
    type: "status"
    at: "2026-02-10T20:50:23.290Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: refs_count plus refs_quality policies are enforced by height and surfaced in diagnostics; smoke output confirms accumulation."
doc_version: 2
doc_updated_at: "2026-02-10T20:50:23.290Z"
doc_updated_by: "CODER"
description: "Add refs_count/refs_quality metrics and progressive refs thresholds by state height."
id_source: "generated"
---
## Summary

Implement refs count/quality policy with progression by height.

## Scope

verifier refs evaluation, policy extraction, and config defaults.

## Plan

1. Add refs_count and refs_quality metrics from explicit fact ids.
2. Enforce refs_min by height and optional quality override.
3. Ensure active anchor ids are projected into prompts and diagnostics.
4. Add tests for refs policy edge cases.

## Risks

Risk: refs_quality may overweight stale refs. Mitigation: age-weighted scoring and bounded caps.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:49:18.560Z — VERIFY — ok

By: CODER

Note: Verified: refs_count and refs_quality progression policy enforced by height and exposed in diagnostics; smoke run confirms refs growth.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:38:54.412Z, excerpt_hash=sha256:cb26814fe6081f6c81808ce27ab64bf8fe7ac1878242ae19f57e7e997e8142b4

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert refs policy changes and restore previous min_refs gate if instability appears.

## Context

Addresses FIX3 observation that refs stayed at zero and dependency depth stalled.

## Verify Steps

1. Run python -m pytest tests -q.
2. Run python scripts/run_simulation.py --steps 10 --db data/fix3_refs.db --seed 9.
3. Confirm refs policy thresholds trigger as configured.

## Notes

### Approvals / Overrides
No overrides requested.

### Decisions
Apply FIX3 as fact-centric progression architecture.

### Implementation Notes
Pending implementation.

### Evidence / Links
Pending.
