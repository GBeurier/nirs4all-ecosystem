# Wave 9G - Multisource Native Vector Parity

Date: 2026-07-08

Owner: Codex coordinator

Parallel review:

- Claude Opus/max read-only audit identified the missing native vector path: `nirs4all` did not pass stacking `outcome["results"]` and `identity` into `_scores_to_run_result`.

Scope:

- `nirs4all/nirs4all/pipeline/dagml/run_paths.py`
- `nirs4all/tests/e2e/test_multisource_stacking_replay.py`
- `nirs4all-core/scripts/e2e/run_multisource_stacking_replay.py`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/CROSS_LANGUAGE_E2E.md`

Changes:

- Threaded stacking `outcome["results"]` and `identity` into the dag-ml result projection so native MetaModel final/test rows carry per-sample arrays.
- Added an E2E assertion that native `MetaModel_Ridge` final/test predictions match the Python oracle by sample id.
- Added `prediction_tolerance` to the Python multisource OOF ledger.
- Added `prediction_vector_parity` to `native-replay.json`.
- Promoted the multisource native prediction-table parity check from contract to strict numeric evidence.

Tests:

- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/e2e/test_multisource_stacking_replay.py`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/e2e/test_multisource_stacking_replay.py --artifacts-dir=/tmp/n4a-e2e-artifacts/multisource-stacking`
- `python3.11 scripts/e2e/run_multisource_stacking_replay.py --artifacts-dir /tmp/n4a-e2e-artifacts/multisource-stacking`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-artifacts evidence --scenario e2e-multisource-branching-stacking-replay --json-out /tmp/n4a-multisource-evidence.json`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/integration/parity/test_dagml_native_results.py tests/integration/parity/test_dagml_native_export_model.py`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests` in `nirs4all-core`

Evidence:

- Generated `prediction_vector_parity`: `compared_rows=59`, `max_abs_delta=6.716849298982197e-14`, `target_max_abs_delta=0.0`, `tolerance=1e-08`, `within_tolerance=true`.

Decisions:

- Kept the scenario `hybrid`: strict vector parity now covers the deterministic duplication-branch stacking fixture, while by_source legacy stacking and broader external multisource catalog corpora remain out of this scenario.
- Did not publish the Python `nirs4all` package; this is source/test work only for now.

Risks:

- The ecosystem contract now requires the new `native-replay.json` fields, so selected release locks must point to the updated `nirs4all` and `nirs4all-core` heads before runtime execution.
