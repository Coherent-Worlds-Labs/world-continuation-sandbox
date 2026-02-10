---
id: "202602101632-JRQK7C"
title: "Remove remaining world content from source code"
status: "DOING"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T16:33:11.186Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved strict world-content isolation in config."
verification:
  state: "pending"
  updated_at: null
  updated_by: null
  note: null
commit: null
comments:
  -
    author: "CODER"
    body: "Start: removing residual world-content literals from source and enforcing config-only world content loading."
events:
  -
    type: "status"
    at: "2026-02-10T16:39:08.231Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: removing residual world-content literals from source and enforcing config-only world content loading."
doc_version: 2
doc_updated_at: "2026-02-10T16:39:08.238Z"
doc_updated_by: "CODER"
description: "Ensure world narrative/content exists only in config files by removing embedded world defaults and story constants from Python source."
id_source: "generated"
---
## Summary


## Scope

In scope: src/pocwc/world_config.py, src/pocwc/orchestrator.py, src/pocwc/provers.py, tests/doc updates if needed. Out of scope: changing world content itself in config files.

## Plan

1) Refactor world_config loader to read base content from config/world.default.json instead of embedded Python defaults. 2) Remove world-specific fallback literals from orchestrator/prover and use config-driven fields with generic neutral fallbacks only. 3) Run full tests and grep checks to ensure Alice/E0 world strings are not present in source modules. 4) Commit and close task.

## Risks

If config file is missing/corrupt, startup may fail; mitigate with explicit loader errors and clear path requirement.

## Verification


## Rollback Plan

Revert commit if strict config sourcing causes regressions; restore previous loader/default behavior.

## Verify Steps

1) PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" must pass.
2) rg -n "Alice|E0|city archive|Genesis: The City After E0" src/pocwc/world_config.py src/pocwc/orchestrator.py src/pocwc/provers.py should return no matches.
