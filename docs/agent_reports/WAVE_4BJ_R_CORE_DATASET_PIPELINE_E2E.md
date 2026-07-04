# WAVE 4BJ - R/Core dataset pipeline E2E

Date: 2026-07-04

## Scope

- Converted `e2e-r-dataset-io-pipeline-save` from blocked to executable.
- Added R entrypoints in `nirs4all-core` to prepare a reshaped dataset, install
  strict R parity dependencies, run a portable pipeline, and save workspace,
  pipeline, and prediction artifacts.

## Integrated commit

- `nirs4all-core`: `a5f3c35f4138ddc4d7e563b6784f9b3bd5a84171`
  - `test(r): add dataset pipeline e2e entrypoints`

## Files changed

### nirs4all-core

- `bindings/r/tests/e2e_dataset_io_pipeline.R`
- `bindings/r/tests/e2e_run_save_pipeline.R`

### nirs4all-ecosystem

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

## Tests run

- `Rscript --vanilla -e 'parse("bindings/r/tests/e2e_dataset_io_pipeline.R"); parse("bindings/r/tests/e2e_run_save_pipeline.R")'`
- `python3.11 scripts/n4a_e2e_scenarios.py plan --scenario e2e-r-dataset-io-pipeline-save`
- `python3.11 scripts/n4a_e2e_scenarios.py run e2e-r-dataset-io-pipeline-save --execute`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 -m ruff check scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py`

## Decisions

- The scenario uses the existing portable parity oracle fixture as a stable
  local dataset source until Dataverse datasets are available.
- The run step calls `make test-r-parity` first, so `n4m` is built from the
  pinned `nirs4all-methods` checkout and ABI `>= 2` is enforced.
- Prediction output is JSON (`r-predictions.json`) rather than Parquet because
  the current R core package has no Parquet dependency.

## Risks

- This is a compact local dataset gate, not the future full Dataverse dataset
  bridge.
- It proves the current portable pipeline subset in R; it does not cover every
  operator/controller planned for final V1.
