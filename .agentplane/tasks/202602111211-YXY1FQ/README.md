---
id: "202602111211-YXY1FQ"
title: "Enforce FIX7 directive and artifact contracts"
result_summary: "Implemented FIX7 directive/artifact contract hardening."
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
  updated_at: "2026-02-11T12:12:30.831Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX7 contract plan."
verification:
  state: "ok"
  updated_at: "2026-02-11T12:19:12.155Z"
  updated_by: "CODER"
  note: "Verified: directive-type contracts and strengthened public_artifact artifact fields are enforced with explicit reason codes/details."
commit:
  hash: "b81ce4fd615610781b6d6a7a2a9ed07895dca298"
  message: "✅ 893HE0 backend: implement FIX7 single-candidate protocol and contracts"
comments:
  -
    author: "CODER"
    body: "Start: Enforcing directive-type and public_artifact contracts with explicit FIX7 reason diagnostics."
  -
    author: "CODER"
    body: "Verified: directive contracts and stronger public_artifact schema fields are enforced with explicit diagnostics."
events:
  -
    type: "status"
    at: "2026-02-11T12:12:39.700Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Enforcing directive-type and public_artifact contracts with explicit FIX7 reason diagnostics."
  -
    type: "verify"
    at: "2026-02-11T12:19:12.155Z"
    author: "CODER"
    state: "ok"
    note: "Verified: directive-type contracts and strengthened public_artifact artifact fields are enforced with explicit reason codes/details."
  -
    type: "status"
    at: "2026-02-11T12:19:48.042Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: directive contracts and stronger public_artifact schema fields are enforced with explicit diagnostics."
doc_version: 2
doc_updated_at: "2026-02-11T12:19:48.042Z"
doc_updated_by: "CODER"
description: "Add directive-type contract gates and strengthen public_artifact schema/specificity requirements with explicit reason codes."
id_source: "generated"
---
## Summary

Enforce directive-type contracts and stronger public_artifact schema.

## Scope

In scope: verifiers/provers/config contract fields and reason codes. Out of scope: external API providers.

## Plan

1) Add directive->expected fact_type mapping policy. 2) Add hard directive contract gate. 3) Require artifact kind/locator/identifier for public_artifact and include identifier in specificity scoring. 4) Log pre/post-normalization fact object details.

## Risks

Risk: stricter contract may reject legacy outputs. Mitigation: canonical normalization plus explicit reason details.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-11T12:19:12.155Z — VERIFY — ok

By: CODER

Note: Verified: directive-type contracts and strengthened public_artifact artifact fields are enforced with explicit reason codes/details.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-11T12:12:39.700Z, excerpt_hash=sha256:6733cbc924ddeb2edbafe91b11f1ea641be2af2fb9d528c459198eefe1db2762

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert contract gate changes and restore previous schema policy.

## Context

FIX7 calls for type-oriented directives and stricter artifact validation.

## Verify Steps

1) $env:PYTHONPATH=src; python -m pytest tests -q`n2) $env:PYTHONPATH=src; python scripts/run_simulation.py --steps 10 --db data/fix7_contract_smoke.db --seed 9

## Notes

### Decisions`n- Directive contracts are protocol-level hard gates.
