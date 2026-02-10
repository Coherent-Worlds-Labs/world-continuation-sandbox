---
id: "202602100046-DGJDA7"
title: "Implement simulation output hotfix and adaptive retry"
status: "DOING"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T00:47:33.524Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved implementation scope: p1/p2/p4, excluding deterministic fallback localization."
verification:
  state: "ok"
  updated_at: "2026-02-10T00:48:56.793Z"
  updated_by: "TESTER"
  note: "Unit tests passed with PYTHONPATH=src; simulation smoke run confirms LLM status reason visibility, decision diagnostics, adaptive retry fields, and no formatter-level text truncation in console stream."
commit: null
comments:
  -
    author: "CODER"
    body: "Start: executing approved hotfix for stream diagnostics, adaptive retry acceptance, and full untruncated narrative output."
events:
  -
    type: "status"
    at: "2026-02-10T00:47:39.223Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: executing approved hotfix for stream diagnostics, adaptive retry acceptance, and full untruncated narrative output."
  -
    type: "verify"
    at: "2026-02-10T00:48:56.793Z"
    author: "TESTER"
    state: "ok"
    note: "Unit tests passed with PYTHONPATH=src; simulation smoke run confirms LLM status reason visibility, decision diagnostics, adaptive retry fields, and no formatter-level text truncation in console stream."
doc_version: 2
doc_updated_at: "2026-02-10T00:49:19.309Z"
doc_updated_by: "TESTER"
description: "Apply user-requested fixes: remove output truncation, surface LLM enablement reason, print candidate/decision diagnostics, and add adaptive acceptance after reject streak (excluding deterministic language fallback localization)."
id_source: "generated"
---
## Summary

Fix simulation stream usability: no truncation, explicit LLM mode diagnostics, richer decision telemetry, and adaptive retry acceptance to reduce repeated static output.

## Scope

In scope: src/pocwc/orchestrator.py and scripts/run_simulation.py for diagnostics/retry/output rendering. Out of scope: deterministic fallback localization and external provider tuning.

## Plan

1) Extend orchestrator progress payload with explicit LLM status and decision diagnostics. 2) Add adaptive retry acceptance when reject streak reaches 2 with bounded relaxed threshold. 3) Update run_simulation renderer to print full text without truncation and include adaptive/LLM status lines. 4) Run unit tests and smoke simulation command to validate behavior.

## Risks

Adaptive acceptance may allow lower-quality candidates in prolonged reject streaks; mitigated with bounded relaxed threshold. Additional console output may be verbose for long runs.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T00:48:56.793Z — VERIFY — ok

By: TESTER

Note: Unit tests passed with PYTHONPATH=src; simulation smoke run confirms LLM status reason visibility, decision diagnostics, adaptive retry fields, and no formatter-level text truncation in console stream.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T00:47:39.223Z, excerpt_hash=sha256:79777ac98f35cf7307a6b6866f522360eae9242fdde0230bd47ef289072dc3f4

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert commit linked to this task via agentplane revert workflow or git revert on the task commit hash, restoring previous orchestrator and CLI renderer behavior.

## Context

User observed English output despite --story-language russian and repeated lines across steps. Root cause for language mismatch in observed run is disabled LLM due missing OpenRouter API key; deterministic fallback remains English by current scope decision.

## Verify Steps

1) python -m unittest discover -s tests -p "test_*.py" must pass.
2) python scripts/run_simulation.py --steps 6 --db data/world_debug_stream.db --seed 8 --llm-provider openrouter --llm-model openai/gpt-4o-mini --story-language russian must print LLM status line with reason when key missing, show decision reasons, and print full narrative/tension/candidate text without formatter truncation.
