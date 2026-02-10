---
id: "202602102035-WBKPRX"
title: "Fix step similarity to use fact-centric baseline"
result_summary: "Fact-centric step similarity shipped"
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T20:38:31.188Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX3 implementation scope and verification contract."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:49:18.586Z"
  updated_by: "CODER"
  note: "Verified: Fact-centric step_similarity and candidate similarity diagnostics implemented; validated with pytest and simulation smoke run."
commit:
  hash: "c65286f159b61509b3f01d106d6ec68794a83656"
  message: "✅ WBKPRX backend: implement FIX3 fact-centric progression and escape mode"
comments:
  -
    author: "CODER"
    body: "Start: Implement fact-centric step similarity and remove dependence on static narrative baseline while preserving diagnostics compatibility."
  -
    author: "CODER"
    body: "Verified: Implemented fact-centric step similarity and progression traces; validated with pytest and simulation smoke run evidence."
events:
  -
    type: "status"
    at: "2026-02-10T20:38:54.357Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implement fact-centric step similarity and remove dependence on static narrative baseline while preserving diagnostics compatibility."
  -
    type: "verify"
    at: "2026-02-10T20:49:18.586Z"
    author: "CODER"
    state: "ok"
    note: "Verified: Fact-centric step_similarity and candidate similarity diagnostics implemented; validated with pytest and simulation smoke run."
  -
    type: "status"
    at: "2026-02-10T20:50:23.186Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: Implemented fact-centric step similarity and progression traces; validated with pytest and simulation smoke run evidence."
doc_version: 2
doc_updated_at: "2026-02-10T20:50:23.186Z"
doc_updated_by: "CODER"
description: "Recompute progression similarity from canonical fact payloads rather than static narrative baseline."
id_source: "generated"
---
## Summary

Fix step similarity baseline to compare candidate against accepted factual state.

## Scope

orchestrator progress metrics and any shared helpers used by similarity traces.

## Plan

1. Introduce fact-canonical similarity input for step progression.
2. Replace narrative-baseline step_similarity with fact-centric computation.
3. Keep scene similarity as secondary diagnostic only.
4. Add/adjust tests for expected range and progression behavior.

## Risks

Risk: regressions in UI/CLI metrics expectations. Mitigation: preserve field names and adjust semantics with docs/tests.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:49:18.586Z — VERIFY — ok

By: CODER

Note: Verified: Fact-centric step_similarity and candidate similarity diagnostics implemented; validated with pytest and simulation smoke run.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:38:54.357Z, excerpt_hash=sha256:5509309ccdb3039b9dfad115ef71624037550d500295ed501f9bd528ffe345ee

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert orchestrator similarity changes and restore prior calculation if regressions block release.

## Context

Addresses FIX3 red flag where step_similarity stays 1.0 despite candidate changes.

## Verify Steps

1. Run python -m pytest tests -q.
2. Run python scripts/run_simulation.py --steps 8 --db data/fix3_wbkprx.db --seed 7.
3. Confirm step_similarity changes with fact progression, not static narrative.

## Notes

### Approvals / Overrides
No overrides requested.

### Decisions
Apply FIX3 as fact-centric progression architecture.

### Implementation Notes
Pending implementation.

### Evidence / Links
Pending.
