# Wave 9R - Provider Repository Dataset Gate

Date: 2026-07-08

## Scope

Strengthen `e2e-dataset-provider-repository-roundtrip` so the strict Python/WASM
prediction gate runs on the dataset materialized by the provider step, not on a
core-local synthetic fallback.

## Changes

- `nirs4all-providers` now emits a deterministic 40 x 28 NIRS CSV fixture from
  the provider E2E and records the executable dataset plus CSV/JSON hashes in
  `provider-resolution.json`.
- `nirs4all-core` now requires `dataset.execution_dataset` from the provider
  resolution artifact and fails if it is absent, malformed, or hash-mismatched.
- `nirs4all-ecosystem` artifact requirements now verify provider dataset kind,
  dimensions, hash continuity, IO summary hash, and strict Python/WASM targets,
  RMSE, predictions, and `predictPortablePipeline` roundtrip deltas.

## Tests

- `python3.11 -m pytest -q tests/e2e/test_dataset_provider_repository_roundtrip.py --artifacts-dir=/tmp/n4a-provider-roundtrip-next`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m unittest discover -s tests -p 'test_consume_repository_descriptor.py' -v`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-provider-repository-strict-dataset run --execute e2e-dataset-provider-repository-roundtrip`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-provider-repository-strict-dataset evidence --scenario e2e-dataset-provider-repository-roundtrip --json`

## Evidence

- Real scenario evidence verified 4 artifacts with `failed_count=0`.
- Provider dataset: `kind=provider_materialized_csv_nirs_matrix`, `rows=40`,
  `cols=28`.
- Strict Python/WASM comparison: `targets_abs_max=0.0`,
  `prediction_abs_max=0.0`, `rmse_abs_max=0.0`,
  `predict_roundtrip_abs_max=0.0`.

## Remaining Risk

The scenario remains `hybrid` because the same repository descriptor is still
not executed through an R surface here. R remains covered by separate
core/methods gates until that binding can execute the full preprocessing and
splitter surface.
