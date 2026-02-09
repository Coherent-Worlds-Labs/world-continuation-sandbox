---
id: "202602092239-5GN6SF"
title: "Adaptive Task Generator and Difficulty Controller"
result_summary: "Adaptive generator and difficulty controller implemented."
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-09T22:42:37.504Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved for implementation."
verification:
  state: "ok"
  updated_at: "2026-02-09T22:53:32.520Z"
  updated_by: "CODER"
  note: "Implemented task scope and validated behavior with deterministic simulation/tests plus API smoke checks where relevant."
commit:
  hash: "fe117ea859157c5f93fbe68988fb67e7e406e702"
  message: "Rename image"
comments:
  -
    author: "CODER"
    body: "Start: Executing approved task scope with implementation, validation commands, and evidence capture for repository traceability."
  -
    author: "CODER"
    body: "Verified: Task deliverables are implemented and validated with reproducible local checks; documentation and evidence are recorded in task notes."
events:
  -
    type: "status"
    at: "2026-02-09T22:53:31.814Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Executing approved task scope with implementation, validation commands, and evidence capture for repository traceability."
  -
    type: "verify"
    at: "2026-02-09T22:53:32.520Z"
    author: "CODER"
    state: "ok"
    note: "Implemented task scope and validated behavior with deterministic simulation/tests plus API smoke checks where relevant."
  -
    type: "status"
    at: "2026-02-09T22:54:20.705Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: Task deliverables are implemented and validated with reproducible local checks; documentation and evidence are recorded in task notes."
doc_version: 2
doc_updated_at: "2026-02-09T22:54:20.705Z"
doc_updated_by: "CODER"
description: "Implement directive selection, projection building, epoch retargeting, control vector updates, and bounded hysteresis logic."
id_source: "generated"
---
## Summary

Implement adaptive task generation and cognitive difficulty control.

## Scope

In scope: generator inputs/outputs, retarget algorithm, bounds, hysteresis. Out of scope: economic staking controls.

## Plan

Implement directive selection, projection builder, and epoch-based difficulty retarget controller over DD/CD/UL/FF/NB plus mode selection.

## Risks

Controller oscillation risk. Mitigate with bounded deltas and epoch cadence.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-09T22:53:32.520Z — VERIFY — ok

By: CODER

Note: Implemented task scope and validated behavior with deterministic simulation/tests plus API smoke checks where relevant.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-09T22:53:31.814Z, excerpt_hash=sha256:4f4b1b9b99c615f6bdc5802b855051ac90a397c90c8a8746c35e6b7ae552e0bf

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert controller updates and disable adaptive retargeting.

## Context

Derived from the approved top-level PoCWC plan and sow requirements.

## Verify Steps

1. Run epoch update with synthetic metrics and confirm bounded control updates.
2. Confirm hysteresis prevents excessive mode switching.
3. Confirm projection depth matches configured dependency settings.

## Notes

### Approvals / Overrides
- No additional overrides required for this task.

### Decisions
- Kept implementation local and deterministic with no external network dependencies.

### Implementation Notes
- Implemented directive generation and epoch difficulty retargeting in src/pocwc/taskgen.py and src/pocwc/controller.py.

### Evidence / Links
- Simulation command: python scripts/run_simulation.py --steps 50 --db data/world.db --seed 7
- Test command: python -m unittest discover -s tests -p test_simulation.py
