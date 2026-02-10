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
- Narrative Continuity Memory with branch-scoped story summary and timeline events.
- Story View in UI for reading the evolving Alice-world timeline.
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

Set requested story language:

```bash
$env:PYTHONPATH="src"
python scripts/run_simulation.py --steps 50 --db data/world.db --seed 7 --story-language spanish
```

Optional LLM mode (OpenRouter):

```bash
$env:POCWC_LLM_PROVIDER="openrouter"
$env:OPENROUTER_API_KEY="<your_key>"
$env:OPENROUTER_MODEL="openai/gpt-4o-mini"
$env:PYTHONPATH="src"
python scripts/run_simulation.py --steps 50 --db data/world.db --seed 7 --llm-provider openrouter --llm-model openai/gpt-4o-mini
```

Control LLM sampling from CLI:

```bash
$env:PYTHONPATH="src"
python scripts/run_simulation.py --steps 50 --db data/world.db --seed 7 --llm-provider openrouter --llm-model openai/gpt-4o-mini --llm-temperature 0.55 --llm-top-p 0.92
```

Runtime stream notes:

- The CLI prints per-candidate traces with `llm_used=true|false`, source (`llm`, `llm_bundle_rebuilt`, or `fallback`), verdict, and score.
- The stream also shows `step_similarity` and per-candidate novelty diagnostics (`sim`, `penalty`, `raw`, adjusted `score`) to make repetition visible.
- Placeholder-like `artifact_x` values (for example `artifact_x`, `артефакт_Х`, `TBD`) are rejected; the engine falls back to a rebuilt or deterministic artifact text.
- Diversify mode now pushes stronger novelty pressure: directives are biased toward non-maintenance events, prompt constraints require one concrete new event per step, and high overlap candidates receive a bounded repetition penalty.

### 2. Run API + UI

```bash
$env:PYTHONPATH="src"
python scripts/run_server.py --db data/world.db --host 127.0.0.1 --port 8080
```

Open `http://127.0.0.1:8080`.

Story View usage:

- In the UI, open the `Story View` panel.
- Keep `branch-main` (or enter another branch id).
- Click `Load Story` to fetch continuity summary and timeline events.

Story API endpoints:

- `GET /api/story/summary?branch_id=branch-main`
- `GET /api/story?branch_id=branch-main&limit=200`

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

## LLM Provider Configuration

The runtime supports provider-agnostic LLM integration with a built-in OpenRouter adapter.

- `POCWC_LLM_PROVIDER`: `none` or `openrouter` (default: `none`)
- `OPENROUTER_API_KEY`: required for OpenRouter mode
- `OPENROUTER_MODEL`: model identifier (for example `openai/gpt-4o-mini`)
- `OPENROUTER_BASE_URL`: optional override (default: `https://openrouter.ai/api/v1`)
- `POCWC_LLM_TIMEOUT`: optional timeout in seconds (default: `30`)

If key/model/provider are incomplete, the system automatically falls back to deterministic non-LLM generation and verification.
In deterministic fallback mode, language selection metadata is stored, while high-fidelity multilingual generation is available through the LLM path.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
Commercial use requires a separate license.

All contributions are subject to the Contributor License Agreement (CLA).
