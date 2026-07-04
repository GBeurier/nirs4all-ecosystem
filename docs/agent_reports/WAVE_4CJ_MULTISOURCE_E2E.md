# Wave 4CJ - Multisource Stacking E2E

## Scope

- Closed `e2e-multisource-branching-stacking-replay`.
- Added a Python oracle for a multisource dataset, duplication-branch preprocessing, prediction stacking, and `.n4a` replay artifacts.
- Added a core-side replay validator that consumes the oracle and native `dag-ml` artifacts without reimplementing training logic in `nirs4all-core`.

## Files Modified

- `nirs4all/pipeline/dagml/cli_runner.py`
- `nirs4all/pipeline/dagml_bridge.py`
- `nirs4all/tests/e2e/test_multisource_stacking_replay.py`
- `nirs4all/tests/integration/parity/test_dagml_bridge_spike.py`
- `nirs4all/tests/integration/parity/test_dagml_cli_runner.py`
- `nirs4all-core/scripts/e2e/run_multisource_stacking_replay.py`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`

## Tests

- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m py_compile nirs4all/pipeline/dagml/cli_runner.py nirs4all/pipeline/dagml_bridge.py tests/e2e/test_multisource_stacking_replay.py`
- `ruff check nirs4all/pipeline/dagml/cli_runner.py nirs4all/pipeline/dagml_bridge.py tests/integration/parity/test_dagml_bridge_spike.py tests/integration/parity/test_dagml_cli_runner.py tests/e2e/test_multisource_stacking_replay.py`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/integration/parity/test_dagml_bridge_spike.py::test_vertical_slice_controller_manifests_validate tests/integration/parity/test_dagml_bridge_spike.py::test_multi_source_baseline_builds_data_requirement_plan tests/integration/parity/test_dagml_cli_runner.py::test_multi_source_emission_single_source_unchanged tests/integration/parity/test_dagml_cli_runner.py::test_multi_source_emission_emits_feature_block_set tests/e2e/test_multisource_stacking_replay.py --artifacts-dir=/tmp/n4a-e2e-ms-stack-focused -q`
- `ruff check scripts/e2e/run_multisource_stacking_replay.py`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m py_compile scripts/e2e/run_multisource_stacking_replay.py`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/e2e/run_multisource_stacking_replay.py --artifacts-dir /tmp/n4a-e2e-ms-stack-focused`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py plan --json`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-ms-stack-orchestrated run e2e-multisource-branching-stacking-replay --execute`

## Result Snapshot

- Native `dag-ml` execution stayed active; no fallback warning was accepted.
- Oracle and native values matched within `1e-3`.
- `cv_best_score`: `14.978127212445557`.
- `best_rmse`: `12.818656538179722`.
- Required artifacts were produced:
  - `stacking-replay.n4a.json`
  - `oof-ledger.json`
  - native `manifest.json`
  - native `score_set.json`
  - native `predictions.parquet`
  - core replay `native-replay.json`

## Decisions

- The old richer by-source stacking branch was audited but not integrated. A leakage-safe native implementation diverged from the current legacy Python summary, so it remains a fallback boundary until the legacy semantics are either preserved exactly or intentionally changed with a dedicated parity migration.
- This scenario validates multisource input handling plus native duplication-branch prediction stacking against a direct Python/sklearn oracle. It does not claim full parity for every current legacy by-source stacking variant.

## Risks

- The scenario covers a realistic multisource stacked workflow, but not arbitrary nested by-source controller combinations.
- The core replay validator intentionally validates artifacts and contract shape; numerical training remains owned by `nirs4all` plus `dag-ml`, not duplicated inside `nirs4all-core`.
