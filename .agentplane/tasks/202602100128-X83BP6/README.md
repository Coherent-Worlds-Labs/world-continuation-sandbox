---
id: "202602100128-X83BP6"
title: "Increase narrative diversity and similarity observability"
status: "DOING"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T01:29:37.962Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved full diversity improvement package."
verification:
  state: "ok"
  updated_at: "2026-02-10T01:33:53.216Z"
  updated_by: "TESTER"
  note: "Unit tests pass (11). Smoke run shows step_similarity output plus per-candidate similarity/penalty traces, repetition penalty reasons, and diversify-friendly fallback variation with concrete event elements."
commit: null
comments:
  -
    author: "CODER"
    body: "Start: implementing anti-repetition penalties, stronger diversify mode, concrete-event constraints, and step similarity telemetry."
events:
  -
    type: "status"
    at: "2026-02-10T01:33:00.205Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: implementing anti-repetition penalties, stronger diversify mode, concrete-event constraints, and step similarity telemetry."
  -
    type: "verify"
    at: "2026-02-10T01:33:53.216Z"
    author: "TESTER"
    state: "ok"
    note: "Unit tests pass (11). Smoke run shows step_similarity output plus per-candidate similarity/penalty traces, repetition penalty reasons, and diversify-friendly fallback variation with concrete event elements."
doc_version: 2
doc_updated_at: "2026-02-10T01:33:53.218Z"
doc_updated_by: "TESTER"
description: "Implement anti-repetition penalties, stronger diversify behavior, richer generation constraints, and step-to-step similarity telemetry in CLI output."
id_source: "generated"
---
## Summary

Reduce repetitive step content and expose explicit similarity telemetry in runtime output.

## Scope

In scope: src/pocwc/orchestrator.py, src/pocwc/provers.py, src/pocwc/controller.py, src/pocwc/taskgen.py, scripts/run_simulation.py, README.md, tests. Out of scope: UI web redesign and external model/provider changes.

## Plan

1) Add novelty similarity scoring utilities and repetition penalty in candidate evaluation path. 2) Strengthen diversify mode behavior in controller/task generator and couple with sampling boost. 3) Tighten LLM prompt constraints to force one concrete new event per step. 4) Expose per-step similarity metrics in progress callback and CLI renderer. 5) Update tests and README, run full unit tests plus smoke run.

## Risks

Aggressive novelty pressure can reduce coherence if over-tuned; mitigated by bounded penalties and fallback behavior.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T01:33:53.216Z — VERIFY — ok

By: TESTER

Note: Unit tests pass (11). Smoke run shows step_similarity output plus per-candidate similarity/penalty traces, repetition penalty reasons, and diversify-friendly fallback variation with concrete event elements.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T01:33:00.205Z, excerpt_hash=sha256:8361089c72a91cf5fd695791698bc03467c723f9e0a3621d0d7de95cfeb64780

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert the task commit if novelty tuning causes unacceptable coherence regression.

## Verify Steps

1) PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" must pass.
2) PYTHONPATH=src python scripts/run_simulation.py --steps 3 --db data/world_similarity_debug.db --seed 8 --llm-temperature 0.75 --llm-top-p 0.92 must print step similarity metrics and per-candidate similarity penalties/reasons when overlap is high.
