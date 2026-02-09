# Architecture and Operations

## System Overview

The prototype is a single-process simulation system with SQLite persistence and a lightweight HTTP server.

### Components

1. `WorldStore`: persistent storage for branches, states, challenges, candidates, verification results, and controller epochs.
2. `TaskGenerator`: chooses directives and adjusts difficulty from branch signals.
3. `ProverPool`: conservative/aggressive/maintenance candidate generators.
4. `VerifierPool`: cascade-style verification producing verdicts and diagnostics.
5. `Aggregator`: robust acceptance decision from multi-verifier scores.
6. `SimulationEngine`: orchestrates branch selection, challenge flow, acceptance, retries, and forking.
7. `DifficultyController`: epoch retarget mechanism over cognitive difficulty axes.
8. `World Browser`: API routes + static frontend pages.

## Data Model

- `branches`: branch state and pressure metrics.
- `states`: accepted world nodes with artifact and metadata.
- `challenges`: generated tasks with projection and difficulty.
- `candidates`: prover outputs and status.
- `verification_results`: per-verifier cascade outputs.
- `controller_epochs`: historical retarget snapshots.

## Invariants

- No final truth claims.
- No interpretation collapse to one surviving interpretation.
- Local coherence checks on accepted artifacts.
- Path dependence through projection depth.

## Execution Flow

1. Seed `S0` if storage is empty.
2. Select active branch.
3. Build challenge from projection + directive + difficulty.
4. Generate candidates from prover pool.
5. Verify each candidate through cascade.
6. Aggregate scores and accept or reject.
7. Update branch metrics and optionally fork.
8. Recompute metrics and retarget difficulty on epoch boundaries.

## Runbook

### Reset local state

```bash
Remove-Item data/world.db -ErrorAction SilentlyContinue
```

### Run simulation

```bash
$env:PYTHONPATH="src"
python scripts/run_simulation.py --steps 50 --db data/world.db --seed 7
```

### Run API/UI server

```bash
$env:PYTHONPATH="src"
python scripts/run_server.py --db data/world.db --host 127.0.0.1 --port 8080
```

### Validate API

- `GET /api/health`
- `GET /api/overview`
- `GET /api/branches`
- `GET /api/states?branch_id=branch-main`
- `GET /api/challenges`
- `GET /api/candidates/<candidate-id>`
- `GET /api/metrics`

## Known Constraints

- Verification is probabilistic and heuristic.
- L3 is simulated, not a real expensive external reasoning model.
- No distributed consensus networking or cryptoeconomic security.
