---
id: "202602100023-8D51RW"
title: "Story Language CLI Control Tracking"
result_summary: "Story language CLI tracking completed."
status: "DONE"
priority: "med"
owner: "ORCHESTRATOR"
depends_on:
  - "[202602100023-MKA4K0]"
tags:
  - "code"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T00:24:11.709Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved for implementation."
verification:
  state: "ok"
  updated_at: "2026-02-10T00:26:07.025Z"
  updated_by: "ORCHESTRATOR"
  note: "Downstream implementation completed and validated."
commit:
  hash: "1ee47922e1481aaec75e54c4a891904202c01ced"
  message: "✅ 23FYSE task: record LLM integration tracking evidence"
comments:
  -
    author: "ORCHESTRATOR"
    body: "Verified: Story language CLI control is implemented and validated."
events:
  -
    type: "verify"
    at: "2026-02-10T00:26:07.025Z"
    author: "ORCHESTRATOR"
    state: "ok"
    note: "Downstream implementation completed and validated."
  -
    type: "status"
    at: "2026-02-10T00:26:07.579Z"
    author: "ORCHESTRATOR"
    from: "TODO"
    to: "DONE"
    note: "Verified: Story language CLI control is implemented and validated."
doc_version: 2
doc_updated_at: "2026-02-10T00:26:07.579Z"
doc_updated_by: "ORCHESTRATOR"
description: "Track implementation of command-line story language selection for generation."
id_source: "generated"
---
## Summary

Track language-selectable story generation from command line.

## Scope

In scope: simulation CLI, config, prover language propagation, docs/tests.

## Plan

1. Add story language parameter to runtime config and CLI. 2. Propagate language into prover generation and LLM prompts. 3. Add tests and docs updates for behavior and fallback.

## Risks

Risk of inconsistent behavior between deterministic and LLM modes.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T00:26:07.025Z — VERIFY — ok

By: ORCHESTRATOR

Note: Downstream implementation completed and validated.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T00:24:11.203Z, excerpt_hash=sha256:f20db21fb9f7bf567aa04aac7583884048f403acede2380356bb567fd440c8d1

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert CLI and prover language propagation changes.

## Verify Steps

1. Run simulation with --story-language set. 2. Validate metadata stores requested language. 3. Run full tests.
