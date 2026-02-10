---
id: "202602100023-MKA4K0"
title: "Add --story-language CLI Wiring"
result_summary: "Story language selection is available via CLI and propagated to generation metadata."
status: "DONE"
priority: "med"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T00:24:15.521Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved for implementation."
verification:
  state: "ok"
  updated_at: "2026-02-10T00:26:05.228Z"
  updated_by: "CODER"
  note: "Implementation validated by tests and language propagation smoke checks."
commit:
  hash: "1ee47922e1481aaec75e54c4a891904202c01ced"
  message: "✅ 23FYSE task: record LLM integration tracking evidence"
comments:
  -
    author: "CODER"
    body: "Start: Implementing CLI story language selection with runtime propagation and validation coverage."
  -
    author: "CODER"
    body: "Verified: Story language CLI argument and propagation path are implemented and tested."
events:
  -
    type: "status"
    at: "2026-02-10T00:26:04.704Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Implementing CLI story language selection with runtime propagation and validation coverage."
  -
    type: "verify"
    at: "2026-02-10T00:26:05.228Z"
    author: "CODER"
    state: "ok"
    note: "Implementation validated by tests and language propagation smoke checks."
  -
    type: "status"
    at: "2026-02-10T00:26:05.794Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: Story language CLI argument and propagation path are implemented and tested."
doc_version: 2
doc_updated_at: "2026-02-10T00:26:05.794Z"
doc_updated_by: "CODER"
description: "Add runtime story language selection through simulation CLI and propagate to prover/LLM generation."
id_source: "generated"
---
## Summary

Implement story language CLI parameter and propagation path.

## Scope

CLI arg, config field, prover language handling, tests/docs.

## Plan

Implement --story-language in scripts/run_simulation.py and SimulationConfig, pass to default_provers and LLM prompt, and add tests/docs.

## Risks

Language selection may only affect LLM path when no translation fallback exists.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T00:26:05.228Z — VERIFY — ok

By: CODER

Note: Implementation validated by tests and language propagation smoke checks.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T00:26:04.704Z, excerpt_hash=sha256:b82b038a113fa40308e8942a8c93b9183cfa20ddfbdb58442412fd01e709c87d

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert task-specific files.

## Verify Steps

1. Run simulation with --story-language spanish. 2. Confirm metadata language field. 3. Run unittests.

## Notes

### Approvals / Overrides
- User requested story language CLI control.

### Decisions
- Language choice is propagated through config and prover metadata; multilingual high-fidelity generation remains strongest in LLM mode.

### Implementation Notes
- Added --story-language in CLI and SimulationConfig; wired into prover/LLM prompt.

### Evidence / Links
- python -m unittest discover -s tests -p test_*.py
- python scripts/run_simulation.py --steps 3 --db data/world_lang_check.db --seed 7 --story-language spanish
