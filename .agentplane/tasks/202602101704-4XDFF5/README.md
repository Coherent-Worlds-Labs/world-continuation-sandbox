---
id: "202602101704-4XDFF5"
title: "Implement novelty-gated semantic progression for story steps"
result_summary: "Novelty-gated progression implemented"
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T17:04:46.354Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved full novelty-gated progression implementation."
verification:
  state: "ok"
  updated_at: "2026-02-10T17:14:15.432Z"
  updated_by: "TESTER"
  note: "Unit tests pass (13). Runtime smoke shows novelty metrics and novelty-aware rejection reasons in decision/trace output."
commit:
  hash: "aa7ef15d5d9678ff42e8ed0d0a09687cbcfcd973"
  message: "✅ 4XDFF5 backend: add novelty gate and fact progression controls"
comments:
  -
    author: "INTEGRATOR"
    body: "Verified: structured novel facts, branch fact registry, novelty gate hard-fail checks, multi-objective aggregation, anti-stagnation control, and runtime novelty metrics are implemented and validated via tests/smoke output."
events:
  -
    type: "verify"
    at: "2026-02-10T17:14:15.432Z"
    author: "TESTER"
    state: "ok"
    note: "Unit tests pass (13). Runtime smoke shows novelty metrics and novelty-aware rejection reasons in decision/trace output."
  -
    type: "status"
    at: "2026-02-10T17:16:10.316Z"
    author: "INTEGRATOR"
    from: "TODO"
    to: "DONE"
    note: "Verified: structured novel facts, branch fact registry, novelty gate hard-fail checks, multi-objective aggregation, anti-stagnation control, and runtime novelty metrics are implemented and validated via tests/smoke output."
doc_version: 2
doc_updated_at: "2026-02-10T17:16:10.316Z"
doc_updated_by: "INTEGRATOR"
description: "Add fact registry, novelty contract, novelty verifier gate, multi-objective aggregation, anti-stagnation control, and runtime novelty metrics to block paraphrase-only progress."
id_source: "generated"
---
## Summary

Introduce novelty-gated progression so paraphrase-only candidates are rejected even when structurally coherent.

## Scope

In scope: store schema, prover payload schema, novelty verifier, aggregator scoring, orchestrator anti-stagnation policy, and CLI observability metrics. Out of scope: external performer integration.

## Plan

1) Add branch fact registry persistence and ingestion from accepted candidates. 2) Extend prover output contract with structured novel facts and delta annotations. 3) Add NoveltyGate verifier and hard-fail rules for low novelty. 4) Upgrade aggregator to multi-objective scoring with novelty/tension/repetition terms. 5) Add anti-stagnation policy and challenge-mode forcing in orchestrator. 6) Expose novelty metrics in runtime progress stream and docs. 7) Verify with tests and smoke run.

## Risks

Stronger novelty gating can reduce accept rate and increase retries; mitigated by adaptive anti-stagnation controller and explicit diagnostics.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T17:14:15.432Z — VERIFY — ok

By: TESTER

Note: Unit tests pass (13). Runtime smoke shows novelty metrics and novelty-aware rejection reasons in decision/trace output.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T17:04:39.053Z, excerpt_hash=sha256:5bb572f2004d75d6aecc16659a41a21a24e1192c3b7c65c4a64d9eeaabbabaca

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert commit if novelty gate over-rejects and blocks baseline simulation stability.

## Verify Steps

1) PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" must pass.
2) PYTHONPATH=src python scripts/run_simulation.py --steps 5 --db data/world_novelty_gate.db --seed 8 must print novelty metrics (new_fact_count, novel_fact_ratio, semantic_delta, stagnation_streak) and reject repeated paraphrase candidates with novelty-related reasons.
