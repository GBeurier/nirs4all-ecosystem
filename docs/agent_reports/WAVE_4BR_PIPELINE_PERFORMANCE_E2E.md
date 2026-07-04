# Wave 4BR - Pipeline Performance E2E

## Scope

- Closed `e2e-pipeline-generation-performance-compare`.
- Added a focused Python legacy-vs-dag-ml benchmark for a canonical generator pipeline.
- Added a client-only Web/WASM runtime smoke that consumes the Python ledger and runs the served SPA to CV results.

## Commits Integrated

- `nirs4all`: `fe79a256 test(e2e): compare pipeline generation runtimes` on `refactor/L17-pyref`.
- `nirs4all-web`: `ebedbd1 test(web): add performance comparison smoke`.
- `nirs4all-ecosystem`: this report and `cross-language-scenarios.n4a.json`.

## Manifest Changes

- `generate-family`
  - Uses `python3.11`.
  - Writes `pipeline-family.json` with legacy Python runtime, dag-ml runtime, selected-prediction parity, and local speed ratio.
- `compare-runtimes`
  - Uses the existing static Web preview smoke runner.
  - Writes `python-vs-dagml.json` and `studio-web-runtime.json`.
  - `studio-web-runtime.json` explicitly marks Studio as `not_executed_prod_hold`; this is evidence, not hidden coverage.

## Tests

- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_pipeline_generation_performance.py::test_generate_family --artifacts-dir=/tmp/n4a-perf-e2e-python -q`
- `python3.11 -m py_compile tests/e2e/conftest.py tests/e2e/test_pipeline_generation_performance.py`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run build`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH ARTIFACTS_DIR=/tmp/n4a-perf-e2e-python npm run smoke:performance-compare`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-performance-4br run e2e-pipeline-generation-performance-compare --execute`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH node --check tests/performance-compare-smoke.mjs`
- `git diff --check`

## Artifacts

- `/tmp/n4a-e2e-performance-4br/performance-compare/pipeline-family.json`
- `/tmp/n4a-e2e-performance-4br/performance-compare/python-vs-dagml.json`
- `/tmp/n4a-e2e-performance-4br/performance-compare/studio-web-runtime.json`

## Result Snapshot

- Python selected-prediction parity: `prediction_abs_max = 0.0`.
- Python selected `best_rmse` parity: `1.7763568394002505e-15`.
- Local Python legacy/dag-ml timing ratio: about `1.76x` faster for dag-ml on this run.
- Web dag-ml/WASM runtime reached CV Scores in about `0.25s` after the Run action.

## Risks

- This is a focused performance smoke, not the full parity suite.
- Studio runtime comparison is not executed yet because `nirs4all-studio` production release remains held; a dedicated Studio test entrypoint is still required before claiming Studio performance coverage.
