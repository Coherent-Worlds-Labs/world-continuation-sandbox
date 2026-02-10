---
id: "202602102110-AQ5BD6"
title: "Implement FIX4 state commit and anti-bypass hardening"
result_summary: "FIX4 core hardening shipped"
status: "DONE"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T21:10:56.144Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved FIX4 implementation plan."
verification:
  state: "ok"
  updated_at: "2026-02-10T21:11:19.967Z"
  updated_by: "CODER"
  note: "Verified: FIX4 implemented. Full test suite passes (22/22) and smoke simulation shows projection_fact_ids, nonzero refs from step2, and anchor growth diagnostics."
commit:
  hash: "3ef07aef69b657d8ce152a581f11a776bb8bfb0d"
  message: "✅ AQ5BD6 backend: implement FIX4 state-evolution and anti-bypass hardening"
comments:
  -
    author: "CODER"
    body: "Start: Apply FIX4 state-evolution and anti-bypass hardening, add diagnostics, and validate with regression tests and smoke simulation."
  -
    author: "CODER"
    body: "Verified: Enforced atomic state fact commits with unique ids, removed threshold-relax acceptance bypass, added prior-fact projection contract and hard refs-from-step2 checks, plus FIX4 regression tests."
events:
  -
    type: "status"
    at: "2026-02-10T21:11:07.958Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: Apply FIX4 state-evolution and anti-bypass hardening, add diagnostics, and validate with regression tests and smoke simulation."
  -
    type: "verify"
    at: "2026-02-10T21:11:19.967Z"
    author: "CODER"
    state: "ok"
    note: "Verified: FIX4 implemented. Full test suite passes (22/22) and smoke simulation shows projection_fact_ids, nonzero refs from step2, and anchor growth diagnostics."
  -
    type: "status"
    at: "2026-02-10T21:11:45.951Z"
    author: "CODER"
    from: "DOING"
    to: "DONE"
    note: "Verified: Enforced atomic state fact commits with unique ids, removed threshold-relax acceptance bypass, added prior-fact projection contract and hard refs-from-step2 checks, plus FIX4 regression tests."
doc_version: 2
doc_updated_at: "2026-02-10T21:11:45.951Z"
doc_updated_by: "CODER"
description: "Apply FIX4: unique fact IDs on commit, explicit last_fact_ids projection, hard refs from step2, remove threshold-relax acceptance bypass, add tests and diagnostics."
id_source: "generated"
---
## Summary

Implement FIX4 improvements from sow/FIX4.txt with auditable verification.

## Scope

In-scope: orchestrator, verifiers, provers, simulation CLI, config, tests, docs.

## Plan

1. Enforce state-commit invariants and remove acceptance bypass.
2. Propagate prior fact ids into projection and references contract.
3. Tighten verifier refs gate from step 2.
4. Add diagnostics and regression tests.
5. Run pytest and smoke simulation.

## Risks

Risk: stricter gating may reduce accept-rate; mitigated by deterministic escape mode rather than threshold relaxation.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T21:11:19.967Z — VERIFY — ok

By: CODER

Note: Verified: FIX4 implemented. Full test suite passes (22/22) and smoke simulation shows projection_fact_ids, nonzero refs from step2, and anchor growth diagnostics.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T21:11:07.958Z, excerpt_hash=sha256:fc1ac6f3a47436f8c7fdfc569f3cbe1e9375e4f2533948d1186861a22954b809

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert FIX4 commit if regressions are detected, then re-run test suite.

## Context

Fix4 identifies state-evolution bugs (anchor growth/refs), metric inconsistency, and acceptance bypass risk.

## Verify Steps

1. python -m pytest tests -q
2. python scripts/run_simulation.py --steps 8 --db data/fix4_smoke.db --seed 10
3. Confirm projection_fact_ids, fact refs, and anchor growth appear in log.

## Notes

### Approvals / Overrides
No overrides.

### Decisions
Use hard progression constraints; do not relax acceptance thresholds.

### Implementation Notes
To be filled at finish.

### Evidence / Links
To be filled at verify/finish.
