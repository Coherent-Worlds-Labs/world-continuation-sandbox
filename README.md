![Coherent-World-Continuation Header](docs/assets/header.png)

# PoCWC Prototype: Competing Interpretations World

## Purpose

This repository contains a working prototype of **Proof-of-Coherent-World-Continuation (PoCWC)** for a world model where one foundational event remains unresolved and multiple interpretations compete over time.

The prototype implements:

- Genesis world seeding (`S0`) with at least three interpretations.
- Challenge generation with directive and difficulty vectors.
- Prover pool with multiple candidate strategies.
- Verifier cascade (`L0` to `L3`) and robust aggregation.
- Branch/fork world evolution with persistent state.
- Difficulty controller with epoch retargeting.
- API and web browser for inspecting branches, states, challenges, and candidates.
- Deterministic tests and a DoD-oriented validation harness.

## Project Structure

- `src/pocwc/domain.py`: core types and protocol entities.
- `src/pocwc/store.py`: SQLite persistence and query layer.
- `src/pocwc/orchestrator.py`: simulation loop and branch lifecycle.
- `src/pocwc/taskgen.py`: directive and difficulty generation.
- `src/pocwc/provers.py`: baseline prover strategies.
- `src/pocwc/verifiers.py`: cascade-level verifier logic.
- `src/pocwc/aggregation.py`: robust acceptance aggregation.
- `src/pocwc/controller.py`: epoch-based difficulty retarget controller.
- `src/pocwc/api_server.py`: HTTP API and static UI server.
- `src/pocwc/web/ui/`: world browser frontend.
- `tests/`: deterministic simulation and controller tests.
- `scripts/run_simulation.py`: CLI simulation runner.
- `scripts/run_server.py`: API/UI server runner.

## Quickstart

### 1. Run simulation

```bash
$env:PYTHONPATH="src"
python scripts/run_simulation.py --steps 50 --db data/world.db --seed 7
```

### 2. Run API + UI

```bash
$env:PYTHONPATH="src"
python scripts/run_server.py --db data/world.db --host 127.0.0.1 --port 8080
```

Open `http://127.0.0.1:8080`.

### 3. Run tests

```bash
$env:PYTHONPATH="src"
python -m pytest tests
```

If `pytest` is unavailable in your environment, run:

```bash
$env:PYTHONPATH="src"
python -m unittest discover -s tests -p "test_*.py"
```

## Verification Targets (DoD)

The prototype is considered valid when:

1. Genesis includes at least three interpretations.
2. Simulation can run at least 50 evolution steps.
3. At least one parent state produces two or more accepted branch continuations.
4. Reject-level distribution is available for cascade levels.
5. API/UI expose branches, states, challenges, candidates, and metrics.

## English-Only Repository Rule

All code and repository documentation must remain in English.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
Commercial use requires a separate license.

All contributions are subject to the Contributor License Agreement (CLA).
