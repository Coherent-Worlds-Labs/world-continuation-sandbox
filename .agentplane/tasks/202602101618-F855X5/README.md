---
id: "202602101618-F855X5"
title: "Externalize world-specific settings into world config"
status: "DOING"
priority: "high"
owner: "CODER"
depends_on: []
tags:
  - "backend"
verify: []
plan_approval:
  state: "approved"
  updated_at: "2026-02-10T16:19:30.580Z"
  updated_by: "ORCHESTRATOR"
  note: "Approved world-config externalization refactor."
verification:
  state: "ok"
  updated_at: "2026-02-10T16:24:35.479Z"
  updated_by: "TESTER"
  note: "Verified: tests and smoke runs passed for world-config externalization."
commit: null
comments:
  -
    author: "CODER"
    body: "Start: moving world-specific setup from code into external config and wiring runtime loaders/CLI arguments."
events:
  -
    type: "status"
    at: "2026-02-10T16:24:04.576Z"
    author: "CODER"
    from: "TODO"
    to: "DOING"
    note: "Start: moving world-specific setup from code into external config and wiring runtime loaders/CLI arguments."
  -
    type: "verify"
    at: "2026-02-10T16:24:24.376Z"
    author: "TESTER"
    state: "ok"
    note: "Unit tests pass (12), simulation smoke with --world-config passes, and run_server startup smoke confirms config path wiring without load errors."
  -
    type: "verify"
    at: "2026-02-10T16:24:35.479Z"
    author: "TESTER"
    state: "ok"
    note: "Verified: tests and smoke runs passed for world-config externalization."
doc_version: 2
doc_updated_at: "2026-02-10T16:24:35.481Z"
doc_updated_by: "TESTER"
description: "Move world-specific constants (genesis state, continuity defaults, fallback narrative templates) from code into a single external configuration file and wire runtime loading."
id_source: "generated"
---
## Summary

Centralize world-specific settings into one external config file and remove hardcoded world constants from runtime code.

## Scope


## Plan

1) Add canonical world config file under config/ and implement loader with defaults/validation. 2) Refactor orchestrator genesis + continuity defaults and prover fallback templates to use loaded world config. 3) Add optional --world-config argument to scripts/run_simulation.py and scripts/run_server.py and propagate to SimulationConfig. 4) Add/adjust tests to verify config-driven behavior. 5) Update README and run full tests + smoke command.

## Risks

Config/schema mismatch could break startup; mitigate with strict loader defaults and fallback-safe normalization.

## Verification

### Plan

### Results

<!-- BEGIN VERIFICATION RESULTS -->
#### 2026-02-10T16:24:24.376Z — VERIFY — ok

By: TESTER

Note: Unit tests pass (12), simulation smoke with --world-config passes, and run_server startup smoke confirms config path wiring without load errors.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T16:24:04.582Z, excerpt_hash=sha256:842f1cc68d83aae36e6ff0670076c2b187f7bf499ce90882373e665e12101b7b

#### 2026-02-10T16:24:35.479Z — VERIFY — ok

By: TESTER

Note: Verified: tests and smoke runs passed for world-config externalization.

VerifyStepsRef: doc_version=2, doc_updated_at=2026-02-10T16:24:24.387Z, excerpt_hash=sha256:842f1cc68d83aae36e6ff0670076c2b187f7bf499ce90882373e665e12101b7b

<!-- END VERIFICATION RESULTS -->

## Rollback Plan

Revert the task commit to restore previous hardcoded world defaults if config wiring causes regressions.

## Verify Steps

1) PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py" must pass.
2) PYTHONPATH=src python scripts/run_simulation.py --steps 1 --db data/world_config_smoke.db --seed 7 must print Genesis World State and execute step stream successfully.
3) PYTHONPATH=src python scripts/run_server.py --db data/world_config_server.db --host 127.0.0.1 --port 8099 --world-config config/world.default.json must start without config load errors (smoke startup).
