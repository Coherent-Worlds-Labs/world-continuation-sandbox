---
id: "202602111238-CRGGYA"
title: "Implement FIX8 coercion policy and expected type wiring"
result_summary: "Implemented FIX8 coercion and expected type wiring."
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
  updated_at: "2026-02-11T12:40:08.892Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX8 coercion/wiring plan."
verification:
  state: "ok"
  updated_at: "2026-02-11T12:44:56.070Z"
  updated_by: "CODER"
  note: "Verified: controlled coercion policy and expected_fact_type propagation are wired through challenge policy and diagnostics."
commit:
  hash: "f04b7dba28ccb3e56131f29e457b9f37258f3f81"
  message: "✅ 5PC685 backend: implement FIX8 strict fact schema and coercion diagnostics"
comments:
  -
    author: "CODER"
    body: "Start: Implementing controlled coercion policy and expected_fact_type propagation for FIX8."
  -
    author: "CODER"
    body: "Verified: controlled coercion policy and expected_fact_type wiring are active and reported in diagnostics."
events:
  -
    type: "status"
    at: "2026-02-11T12:40:16.176Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implementing controlled coercion policy and expected_fact_type propagation for FIX8."
  -
    type: "verify"
    at: "2026-02-11T12:44:56.070Z"
    author: "CODER"
    state: "ok"
    note: "Verified: controlled coercion policy and expected_fact_type propagation are wired through challenge policy and diagnostics."
  -
    type: "status"
    at: "2026-02-11T12:45:46.595Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: controlled coercion policy and expected_fact_type wiring are active and reported in diagnostics."
doc_version: 2
doc_updated_at: "2026-02-11T12:45:46.595Z"
doc_updated_by: "CODER"
description: "Add controlled coercion policy for malformed fields and guarantee expected_fact_type propagation and enforcement."
id_source: "generated"
---
## Summary

Implement controlled coercion and expected_fact_type propagation.

## Scope

In scope: progression policy wiring + coercion hooks + directive contract enforcement context.

## Plan

1) Add config flags for coercion behavior. 2) Coerce known malformed fields when enabled and log coercions. 3) Guarantee expected_fact_type is always set when contract exists.

## Risks

Risk: over-coercion can hide model errors. Mitigation: make coercion explicit and configurable.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-11T12:44:56.070Z — VERIFY — ok

By: CODER

Note: Verified: controlled coercion policy and expected_fact_type propagation are wired through challenge policy and diagnostics.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-11T12:40:16.176Z, excerpt_hash=sha256:74976391f3cee6291708c832b91752be503d9bf5b16e11ca9fe14b39c32c7c07

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Disable coercion policy and revert wiring changes if side effects appear.

## Context

FIX8 highlighted empty expected_fact_type and malformed fields requiring safe coercion policy.

## Verify Steps

1) $env:PYTHONPATH=src; python -m pytest tests -q`n2) $env:PYTHONPATH=src; python scripts/run_simulation.py --steps 8 --db data/fix8_smoke.db --seed 16

## Notes

### Decisions`n- Coercion is opt-in policy and always logged in diagnostics.
