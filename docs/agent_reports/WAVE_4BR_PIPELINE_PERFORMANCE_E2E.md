# Wave 4BR - Pipeline Performance E2E

## Scope

- Closed the Python/Web part of `e2e-pipeline-generation-performance-compare` without claiming Studio runtime coverage.
- Added a focused Python legacy-vs-dag-ml benchmark for a canonical generator pipeline.
- Added a client-only Web/WASM runtime smoke that consumes the Python ledger and runs the served SPA to CV results.

## Commits Integrated

- `nirs4all`: `fe79a256 test(e2e): compare pipeline generation runtimes` on `refactor/L17-pyref`; follow-ups `2fabf4b test(e2e): fail performance run on dagml fallback`, `a111cf2e test(e2e): require native dagml result artifacts`, and `7e52be10 test(e2e): harden dagml performance evidence`.
- `nirs4all-web`: `ebedbd1 test(web): add performance comparison smoke`; follow-ups `3338752 test(web): mark studio runtime hold in perf smoke` and `cad394e2 test(web): assert dagml runtime evidence`.
- `nirs4all-ecosystem`: this report and `cross-language-scenarios.n4a.json`.

## Manifest Changes

- `generate-family`
  - Uses `python3.11`.
  - Writes `pipeline-family.json` with legacy Python runtime, dag-ml runtime, selected-prediction parity, and local speed ratio.
- `compare-runtimes`
  - Uses the existing static Web preview smoke runner.
  - Requires `node`, `npm`, and `google-chrome`, with a local runner fallback for the workstation nvm path.
  - Writes `python-vs-dagml.json` and `studio-web-runtime.json`.
  - `studio-web-runtime.json` now reports `passed_web_with_studio_hold` and explicitly marks Studio as `not_executed_prod_hold`; this is evidence, not hidden coverage.
  - The Web ledger now records observed `window.__n4aLastRun` evidence: `dag-ml-wasm + libn4m`, `compiled=true`, `executed=true`, `schedulerFallback=false`, and non-empty CV predictions.

## Tests

- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_pipeline_generation_performance.py::test_generate_family --artifacts-dir=/tmp/n4a-perf-e2e-python -q`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_pipeline_generation_performance.py::test_generate_family --artifacts-dir=/tmp/n4a-perf-e2e-python-nativeartifacts -q`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_pipeline_generation_performance.py::test_generate_family --artifacts-dir=/tmp/n4a-perf-e2e-python-strong -q`
- `python3.11 -m py_compile tests/e2e/conftest.py tests/e2e/test_pipeline_generation_performance.py`
- `python3.11 -m ruff check tests/e2e/test_pipeline_generation_performance.py`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run build`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH ARTIFACTS_DIR=/tmp/n4a-perf-e2e-python npm run smoke:performance-compare`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH node --check tests/performance-compare-smoke.mjs`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH ARTIFACTS_DIR=/tmp/n4a-perf-e2e-python-strong npm run smoke:performance-compare`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-performance-nativeartifacts-4bw run e2e-pipeline-generation-performance-compare --execute`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-performance-strong-4bx run e2e-pipeline-generation-performance-compare --execute`
- `git diff --check`

## Artifacts

- `/tmp/n4a-e2e-performance-strong-4bx/performance-compare/pipeline-family.json`
- `/tmp/n4a-e2e-performance-strong-4bx/performance-compare/python-vs-dagml.json`
- `/tmp/n4a-e2e-performance-strong-4bx/performance-compare/studio-web-runtime.json`

## Result Snapshot

- Python selected-prediction parity: `prediction_abs_max = 0.0`.
- Python selected `best_rmse` parity: `1.7763568394002505e-15`.
- Local Python legacy/dag-ml timing ratio: about `1.76x` faster for dag-ml on this run.
- Web dag-ml/WASM runtime executed `60` CV predictions in about `0.25s` after the Run action.
- Studio runtime status is `not_executed_prod_hold`.
- The Python test now fails if `engine="dag-ml"` falls back to the legacy engine.
- The Python test now also requires native dag-ml result artifacts when `results_path` is requested.
- The Web smoke now fails unless the observed run reports `compiled=true`, `executed=true`, `schedulerFallback=false`, no diagnostics, and a visible `by dag-ml` badge.

## Risks

- This is a focused performance smoke, not the full parity suite.
- Studio runtime comparison is not executed yet because `nirs4all-studio` production release remains held; a dedicated Studio test entrypoint is still required before claiming Studio performance coverage.
