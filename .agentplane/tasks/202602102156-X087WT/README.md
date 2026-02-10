---
id: "202602102156-X087WT"
title: "Implement FIX6 fact schema canonicalization"
result_summary: "Implemented FIX6 fact schema canonicalization and consistency checks."
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
  updated_at: "2026-02-10T21:58:35.415Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX6 schema canonicalization plan."
verification:
  state: "ok"
  updated_at: "2026-02-10T22:08:24.726Z"
  updated_by: "CODER"
  note: "Verified: strict fact schema/type checks and fact id/type consistency validation are enforced with canonicalized ids and explicit reject codes. Tests passed."
commit:
  hash: "07d230dd01699a9690f1e637b6993f2cbbcb8d42"
  message: "✅ EJG6RH backend: implement FIX6 gate transparency and protocol diagnostics"
comments:
  -
    author: "CODER"
    body: "Start: Implementing fact schema canonicalization and structural consistency checks for FIX6 candidate handling."
  -
    author: "CODER"
    body: "Verified: fact schema/type/id canonicalization and structural consistency checks are enforced with explicit reject codes."
events:
  -
    type: "status"
    at: "2026-02-10T21:58:47.118Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implementing fact schema canonicalization and structural consistency checks for FIX6 candidate handling."
  -
    type: "verify"
    at: "2026-02-10T22:08:24.726Z"
    author: "CODER"
    state: "ok"
    note: "Verified: strict fact schema/type checks and fact id/type consistency validation are enforced with canonicalized ids and explicit reject codes. Tests passed."
  -
    type: "status"
    at: "2026-02-10T22:09:02.947Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: fact schema/type/id canonicalization and structural consistency checks are enforced with explicit reject codes."
doc_version: 2
doc_updated_at: "2026-02-10T22:09:02.947Z"
doc_updated_by: "CODER"
description: "Enforce strict fact schema/type/id normalization and candidate-level structural consistency handling."
id_source: "generated"
---
## Summary

Enforce strict fact schema canonicalization and structural consistency expectations.

## Scope

In scope: src/pocwc/provers.py, src/pocwc/aggregation.py, src/pocwc/verifiers.py for canonical id/type and structural checks. Out of scope: changing world narrative content.

## Plan

1) Canonicalize fact_id and fact_type before scoring. 2) Enforce public_artifact schema with concrete artifact signal and evidence minimum. 3) Add consistency rejection reason when structural disagreement cannot be normalized.

## Risks

Risk: legacy outputs may fail stricter schema. Mitigation: normalize known variants and keep explicit fallback reason codes.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T22:08:24.726Z — VERIFY — ok

By: CODER

Note: Verified: strict fact schema/type checks and fact id/type consistency validation are enforced with canonicalized ids and explicit reject codes. Tests passed.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T21:58:47.118Z, excerpt_hash=sha256:a1b1b3f798b7196a76bf7cc34d3a28999f6ec025f1c65904e9491a6e75962510

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert schema/canonicalization commit and keep previous normalization if breakage is excessive.

## Context

FIX6 observed mismatched fact_id case and type disagreement across provers.

## Verify Steps

1) python -m pytest tests -q`n2) python scripts/run_simulation.py --steps 8 --db data/fix6_schema_smoke.db --seed 11

## Notes

### Decisions`n- Candidate validity is checked independently before aggregation-level acceptance.
