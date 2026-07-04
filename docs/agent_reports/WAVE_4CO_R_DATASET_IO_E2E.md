# Wave 4CO - R dataset/io E2E hardening

Date: 2026-07-04

## Scope

Lane G/E: replace the R dataset/io scenario's synthetic-oracle preparation with a real provider/datasets/io bridge feeding the R native pipeline execution.

## Files changed

- `nirs4all-core/scripts/e2e/prepare_r_dataset_io_pipeline.py`
  - Loads `malaria_anopheles_gambiae_sporozoite_nir` through `nirs4all-providers.DatasetProvider`.
  - Delegates catalog access to `nirs4all-datasets` and package materialization to `nirs4all-io`.
  - Writes `dataset-card.json`, `io-spec.n4a.json`, `dataset-package-summary.json`, and `reshaped-dataset.json`.
  - Produces a deterministic 120x96 R-ready subset while preserving selected IO values and recording hashes.
- `nirs4all-core/bindings/r/tests/e2e_dataset_io_pipeline.R`
  - Orchestrates the dataset/io preparation from R and validates the produced neutral artifacts.
  - Writes `r-session-info.json`.
- `nirs4all-core/bindings/r/tests/e2e_run_save_pipeline.R`
  - Requires the new v2 prepared dataset schema.
  - Propagates IO/provenance hashes into workspace and prediction artifacts.
  - Fails on non-finite R/native predictions or targets.
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - Declares `nirs4all-providers` and the new dataset/io evidence artifacts.
  - Corrects the parity wording: fixture parity is covered by `make test-r-parity`; the real dataset run proves provider/datasets/io bridge integrity plus R/native execution output sanity.

## Tests run

- `cd nirs4all-core && python3.11 -m py_compile scripts/e2e/prepare_r_dataset_io_pipeline.py`
- `cd nirs4all-core && python3.11 -m ruff check scripts/e2e/prepare_r_dataset_io_pipeline.py`
- `cd nirs4all-core && python3.11 scripts/e2e/prepare_r_dataset_io_pipeline.py --out /tmp/n4a-r-dataset-io`
- `cd nirs4all-core && PATH=/home/delete/miniconda3/envs/pls4all_r/bin:$PATH Rscript bindings/r/tests/e2e_dataset_io_pipeline.R --out /tmp/n4a-r-dataset-io-r`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py validate`
- `cd nirs4all-ecosystem && python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-r-scenario run e2e-r-dataset-io-pipeline-save --execute`

## Decisions

- Use the real local public dataset `malaria_anopheles_gambiae_sporozoite_nir` because it has canonical bytes, one source, finite targets, and no NA-policy blocker.
- Keep providers as a Python convenience client, but make the e2e evidence neutral: card, IO spec, package summary, hashes, and R-readable payload.
- Do not claim full Python-reference parity for the real dataset until a dedicated Python reference execution path for this exact provider/io payload is available.

## Risks / follow-up

- R native dataset fetching remains contract-backed rather than a standalone R HTTP/fetcher implementation.
- The scenario depends on the local canonical dataset being present; Dataverse-backed acquisition can replace that once the collection is available.
