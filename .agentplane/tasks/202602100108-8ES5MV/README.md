---
id: "202602100108-8ES5MV"
title: "Implement LLM trace, artifact guardrail, and CLI sampling args"
status: "DOING"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T01:10:02.378Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved implementation for all 3 requested points."
verification:
  state: "ok"
  updated_at: "2026-02-10T01:11:05.876Z"
  updated_by: "TESTER"
  note: "All tests pass (10). Smoke run confirms --llm-temperature/--llm-top-p rendering and per-candidate trace lines with llm_used/source; artifact guardrail test for placeholder artifact_x added and passing."
commit: null
comments:
  -
    author: "CODER"
    body: "Start: implementing llm trace telemetry, artifact placeholder guardrail, and configurable llm sampling arguments."
events:
  -
    type: "status"
    at: "2026-02-10T01:10:09.595Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: implementing llm trace telemetry, artifact placeholder guardrail, and configurable llm sampling arguments."
  -
    type: "verify"
    at: "2026-02-10T01:11:05.876Z"
    author: "TESTER"
    state: "ok"
    note: "All tests pass (10). Smoke run confirms --llm-temperature/--llm-top-p rendering and per-candidate trace lines with llm_used/source; artifact guardrail test for placeholder artifact_x added and passing."
doc_version: 2
doc_updated_at: "2026-02-10T01:11:05.878Z"
doc_updated_by: "TESTER"
description: "Add per-candidate llm_used trace output, reject placeholder artifact_x values from LLM responses, and expose --llm-temperature/--llm-top-p in CLI and adapter path."
id_source: "generated"
---
## Summary

Implement three runtime improvements: per-candidate llm usage trace, strict placeholder artifact rejection, and configurable LLM sampling from CLI.

## Scope

In scope: src/pocwc/llm.py, src/pocwc/provers.py, src/pocwc/orchestrator.py, scripts/run_simulation.py, tests/test_llm_integration.py, README.md. Out of scope: provider retries and multilingual deterministic fallback localization.

## Plan

1) Extend LLM adapter contract with top_p and propagate sampling params from CLI through SimulationConfig to Prover.
2) Add artifact guardrail in Prover to reject placeholder/short artifact_x and rebuild from bundle or fallback.
3) Emit per-candidate trace metadata (llm_used/source/error/verdict/score) via orchestrator progress payload and print in run_simulation stream.
4) Add targeted test for placeholder artifact rejection and update README usage examples.

## Risks

Stricter artifact validation may reject some compact but valid outputs; mitigated by allowing rebuilt artifacts from LLM bundle before fallback.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T01:11:05.876Z — VERIFY — ok

By: TESTER

Note: All tests pass (10). Smoke run confirms --llm-temperature/--llm-top-p rendering and per-candidate trace lines with llm_used/source; artifact guardrail test for placeholder artifact_x added and passing.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T01:10:09.595Z, excerpt_hash=sha256:db628986e83fdeab78683bac0a1a7339d585274eb30d7b54794a67ea585b62c0

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert the implementation commit to restore previous LLM sampling defaults and artifact acceptance behavior.

## Context

User requested all three proposed fixes after diagnosing mixed-language first step and repeated low-information candidates.

## Verify Steps

1) PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" must pass.
2) PYTHONPATH=src python scripts/run_simulation.py --steps 2 --db data/world_trace_args.db --seed 7 --llm-temperature 0.55 --llm-top-p 0.92 must print LLM temperature/top_p and per-candidate trace lines with llm_used/source.
