---
id: "202602101955-AGHV6S"
title: "Define canonical Fact Object schema and prover contract"
result_summary: "FIX2 constraints delivered and validated."
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T19:58:43.668Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved after FIX2 decomposition and verify contract review."
verification:
  state: "ok"
  updated_at: "2026-02-10T20:07:58.123Z"
  updated_by: "CODER"
  note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
commit:
  hash: "861c9ce98c77a11d5e0a59dfa7a7e6c77ce57d6d"
  message: "✅ YJYT9K backend: implement FIX2 hard fact-object progression constraints"
comments:
  -
    author: "CODER"
    body: "Start: Define and enforce canonical Fact Object schema for prover outputs and fallback normalization."
  -
    author: "CODER"
    body: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
events:
  -
    type: "status"
    at: "2026-02-10T20:00:21.932Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Define and enforce canonical Fact Object schema for prover outputs and fallback normalization."
  -
    type: "verify"
    at: "2026-02-10T20:07:58.123Z"
    author: "CODER"
    state: "ok"
    note: "FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed)."
  -
    type: "status"
    at: "2026-02-10T20:08:33.157Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: FIX2 hard progression constraints implemented and validated by automated tests (19 passed)."
doc_version: 2
doc_updated_at: "2026-02-10T20:08:33.157Z"
doc_updated_by: "CODER"
description: "Implement strict atomic fact schema and make prover output compliant with required fact object fields."
id_source: "generated"
---
## Summary

Define canonical atomic Fact Object schema and enforce it in prover outputs.

## Scope

Prover payload contract, schema normalization, and strict field requirements for new facts.

## Plan

1) Define Fact Object schema fields and validation rules. 2) Require prover output to include exactly one atomic fact object when fact directive applies. 3) Normalize fallback and LLM outputs to schema. 4) Persist structured fields for downstream verification.

## Risks

Overly strict schema may reject valid outputs; mitigate with deterministic fallback normalization.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T20:07:58.123Z — VERIFY — ok

By: CODER

Note: FIX2 implemented with hard progress gate, canonical fact object validation, refs policy, hard repetition rejection, equivalence rejection, diagnostics API/UI, and deterministic regressions. Validation: python -m pytest tests -q (19 passed).

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T20:00:21.932Z, excerpt_hash=sha256:bb06b584b386f0223cbedd629977f0fb73e2d95288a103522151ec9876eead02

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert schema-enforcement changes in prover/normalization path.

## Context

Derived from sow/FIX2 - factobject.txt to eliminate pseudo-facts and enforce irreversible structural world progression.

## Verify Steps

- Run tests validating required Fact Object fields. - Run simulation and confirm accepted steps carry schema-compliant fact objects.

## Notes

### Approvals / Overrides
- Plan approved by user. No overrides requested.

### Decisions
- FIX2 enforces hard structural progression constraints over stylistic quality.

### Implementation Notes
- Pending implementation in this task.

### Evidence / Links
- Source analysis: sow/FIX2 - factobject.txt
