# WAVE 9V - R dataset strict numeric gate

Date: 2026-07-08

## Scope

Closed the last strict non-numeric exception for `e2e-r-dataset-io-pipeline-save`.

## Files Modified

- `nirs4all-core/bindings/r/tests/e2e_run_save_pipeline.R`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/nirs4all-core` submodule pointer

## Decisions

- Kept `nirs4all-core` as the canonical aggregate; no legacy public alias was added.
- Made `make test-r-parity` emit `r-parity-ledger.json` for this scenario via the existing `NIRS4ALL_CORE_R_PARITY_LEDGER` hook.
- Added direct numeric assertions for the R portable fixture gate and the real dataset roundtrip/rerun/prediction artifacts.
- Left full parity for a later large batch, per operating guidance.

## Validation

- `python3.11 -m pytest tests/test_e2e_scenarios.py -q`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-r-next run --execute e2e-r-dataset-io-pipeline-save`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-r-next evidence --scenario e2e-r-dataset-io-pipeline-save --json`

Results:

- `128 passed`
- `OK: 11 cross-language E2E scenarios`
- `strict_non_numeric_check_count = 0`
- R scenario evidence verified 11/11 artifacts, failures 0
- `r-parity-ledger.json`: 4 cases, 104 prediction rows, all target/prediction/RMSE/variant deltas within published tolerances

## Risks

- This is targeted evidence, not a full parity sweep.
- R package install still depends on the local R 4.3.3 conda environment and prebuilt `nirs4all-methods` dev-release artifacts.
