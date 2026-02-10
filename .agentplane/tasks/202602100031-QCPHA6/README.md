---
id: "202602100031-QCPHA6"
title: "Add live progress renderer to run_simulation"
result_summary: "Simulation CLI now streams per-step world and narrative output."
status: "DONE"
priority: "med"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T00:32:15.038Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved for implementation."
verification:
  state: "ok"
  updated_at: "2026-02-10T00:33:42.321Z"
  updated_by: "CODER"
  note: "Output stream and tests validated successfully."
commit:
  hash: "a98644e289991dff0d1db85a475b7be6ed827e84"
  message: "✅ 8D51RW task: record story language tracking evidence"
comments:
  -
    author: "CODER"
    body: "Start: Implementing live simulation stream output with progress callback and styled console rendering."
  -
    author: "CODER"
    body: "Verified: Live progress renderer is implemented and validated with test and smoke runs."
events:
  -
    type: "status"
    at: "2026-02-10T00:33:41.777Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implementing live simulation stream output with progress callback and styled console rendering."
  -
    type: "verify"
    at: "2026-02-10T00:33:42.321Z"
    author: "CODER"
    state: "ok"
    note: "Output stream and tests validated successfully."
  -
    type: "status"
    at: "2026-02-10T00:33:42.880Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: Live progress renderer is implemented and validated with test and smoke runs."
doc_version: 2
doc_updated_at: "2026-02-10T00:33:42.880Z"
doc_updated_by: "CODER"
description: "Emit per-step progress lines showing current step, world health, and latest narrative preview in a readable streaming format."
id_source: "generated"
---
## Summary

Implement live simulation progress console stream.

## Scope

orchestrator callback + CLI rendering only.

## Plan

Add optional progress callback to SimulationEngine.run and implement a styled live renderer in scripts/run_simulation.py.

## Risks

Potential terminal incompatibility with ANSI formatting.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T00:33:42.321Z — VERIFY — ok

By: CODER

Note: Output stream and tests validated successfully.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T00:33:41.777Z, excerpt_hash=sha256:83be2cd536ddc1ff436de4c7b2db5df056bfd062a4edca775543bc9dce435aa3

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert run_simulation and orchestrator run signature changes.

## Verify Steps

1. Run simulation with 5 steps. 2. Verify step-by-step output includes step number, branch state, and narrative snippet. 3. Verify final summary JSON is printed.

## Notes

### Approvals / Overrides
- User requested live streaming progress output in CLI.

### Decisions
- Added optional progress callback in run loop and ANSI-styled rendering in run_simulation.

### Implementation Notes
- Per-step output includes step, branch, mode/theta, debt/variance, ledger, narrative preview, and deferred tension.

### Evidence / Links
- python -m unittest discover -s tests -p test_*.py
- python scripts/run_simulation.py --steps 5 --db data/world_live_stream.db --seed 7 --story-language english
