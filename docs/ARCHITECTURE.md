# Architecture and Operations

## System Overview

The prototype is a single-process simulation system with SQLite persistence and a lightweight HTTP server.

### Components

1. `WorldStore`: persistent storage for branches, states, challenges, candidates, verification results, and controller epochs.
2. `TaskGenerator`: chooses directives, enforces structural operator rotation, and adjusts difficulty from branch signals.
3. `LLM Adapter Layer`: provider-agnostic interface with an OpenRouter client implementation.
4. `ProverPool`: conservative/aggressive/maintenance candidate generators with optional LLM narrative generation.
5. `VerifierPool`: cascade-style verification producing verdicts and diagnostics with optional LLM semantic checks.
5. `Aggregator`: robust acceptance decision from multi-verifier scores.
6. `SimulationEngine`: orchestrates branch selection, challenge flow, acceptance, retries, and forking.
7. `DifficultyController`: epoch retarget mechanism over cognitive difficulty axes.
8. `World Browser`: API routes + static frontend pages.
9. `Narrative Continuity Memory`: branch-scoped summary plus per-state story events.
10. `Anchor Registry`: persistent branch facts/anchors with references and introduced height.
11. `Progress Diagnostics`: exposes fact-object progression signals (`max_fact_similarity`, `refs_quality`, novelty components) through CLI/API/UI.

## Data Model

- `branches`: branch state and pressure metrics.
- `states`: accepted world nodes with artifact and metadata.
- `challenges`: generated tasks with projection and difficulty.
- `candidates`: prover outputs and status.
- `verification_results`: per-verifier cascade outputs.
- `controller_epochs`: historical retarget snapshots.
- `story_memory`: current continuity snapshot for each branch.
- `story_events`: append-only timeline entries derived from accepted story bundles.
- `branch_facts`: persistent world anchors with ids, types, references, and reinterpretability flags.

## Invariants

- No final truth claims.
- No interpretation collapse to one surviving interpretation.
- Local coherence checks on accepted artifacts.
- Path dependence through projection depth.
- English-only generated artifacts for repository-facing outputs.

## Execution Flow

1. Seed `S0` if storage is empty.
2. Select active branch.
3. Build challenge from projection + directive + difficulty.
4. Generate candidates from prover pool.
5. Select one canonical candidate for the step using deterministic screening (schema/contract pass first, then rank).
6. Verify only the selected candidate through cascade (fact-centric novelty gate plus general verifiers).
7. Aggregate scores and accept only when score threshold passes and protocol gates report no hard failures.
7. Update branch metrics and optionally fork.
8. Recompute metrics, including ontological stagnation, and retarget difficulty on epoch boundaries.

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

### Run simulation with OpenRouter

```bash
$env:POCWC_LLM_PROVIDER="openrouter"
$env:OPENROUTER_API_KEY="<your_key>"
$env:OPENROUTER_MODEL="openai/gpt-4o-mini"
$env:PYTHONPATH="src"
python scripts/run_simulation.py --steps 50 --db data/world.db --seed 7 --llm-provider openrouter --llm-model openai/gpt-4o-mini
```

Optional language control:

```bash
$env:PYTHONPATH="src"
python scripts/run_simulation.py --steps 20 --db data/world.db --seed 7 --story-language spanish
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
- `GET /api/story/summary?branch_id=branch-main`
- `GET /api/story?branch_id=branch-main&limit=200`
- `GET /api/facts/active?branch_id=branch-main&limit=200`
- `GET /api/progress/diagnostics?branch_id=branch-main&limit=50`

## Known Constraints

- Verification is probabilistic and heuristic.
- FIX3 progression guardrails are deterministic at gate level: hard fact-repeat reject, reference accumulation policy, and reject-streak escape mode.
- Reject-streak handling no longer lowers acceptance thresholds; progression must pass hard gates.
- FIX5 adds semantic hardening: strict fact-type enum validation, fact-specificity gate, and scene-stagnation breaker (`InstitutionalAction`).
- FIX6 separates protocol gates and emits deterministic diagnostics (`reason_codes` + `reason_details`), including explicit novelty threshold comparisons and step-aware reference requirements.
- `novelty_score` gate is pure (`novelty_score >= novelty_min`), while progress/schema/evidence/consistency failures are reported under their own reason codes.
- FIX7 enforces one-candidate protocol semantics per step, adds directive-type contract gates, and requires explicit artifact fields for `public_artifact`.
- FIX8 adds strict schema validation for `fact_object` with structured field-level errors and optional policy-based coercion for known malformed payloads.
- L3 is simulated, not a real expensive external reasoning model.
- No distributed consensus networking or cryptoeconomic security.
- LLM provider calls require explicit API credentials and network availability; missing credentials trigger deterministic fallback.
