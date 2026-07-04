# Wave 4BD - IO/Datasets E2E Entrypoint

Date: 2026-07-04

## Scope

Added the first executable step for
`e2e-formats-io-datasets-methods-language-bindings`.

## Files changed

- `nirs4all-io/tests/e2e/conftest.py`
  - Adds the ecosystem-compatible `--artifacts-dir` pytest option.
- `nirs4all-io/tests/e2e/test_formats_io_datasets_methods.py`
  - Adds `test_assemble_reference_datasets`.
  - Uses the sibling `nirs4all-datasets` checkout and real `nirs4all_io`
    dataset-package APIs.
  - Validates two clean local reference datasets:
    `cgl_nir_grain_eigenvector` and `ohpl_beer_nir`.
  - Checks assembled matrices, wavelength headers, targets, metadata/split
    alignment, package manifest counts, and writes `assembled-datasets.json`.
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - The IO step now runs with `PYTHONPATH=src python3.11`, avoiding dependence
    on a local venv while keeping Python >= 3.11.
  - The blocked methods step now declares both `binding-parity.json` and
    `predictions-by-language.json` as produced artifacts.

## Results

- `nirs4all-io`: `PYTHONPATH=src python3.11 -m pytest
  tests/e2e/test_formats_io_datasets_methods.py::test_assemble_reference_datasets
  -q --artifacts-dir=/tmp/n4a-formats-io-methods-main-py311` -> 1 passed.
- `nirs4all-io`: `.venv/bin/python -m pytest
  tests/e2e/test_formats_io_datasets_methods.py::test_assemble_reference_datasets
  -q --artifacts-dir=/tmp/n4a-formats-io-methods-main-venv` -> 1 passed.
- `nirs4all-io`: `ruff check tests/e2e/conftest.py
  tests/e2e/test_formats_io_datasets_methods.py` -> passed.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py run
  e2e-formats-io-datasets-methods-language-bindings --execute --allow-blocked`
  -> IO step passed and wrote `assembled-datasets.json`; final exit code 2
  because the methods parity step is still blocked.

## Decisions

- The IO entrypoint was committed on `nirs4all-io` `main`, not only on the
  pre-existing `refactor/L7-io-dagml-sibling` branch. `origin/main` already had
  the dataset-package APIs needed by the test.
- No skip/xfail was introduced. The scenario remains blocked until the
  `nirs4all-methods` cross-binding script exists and `Rscript` is available.

## Risks

- The test assumes the standard sibling workspace layout:
  `/home/delete/nirs4all/nirs4all-datasets`.
- The methods step still needs a real implementation:
  `nirs4all-methods/scripts/e2e/cross_binding_methods_parity.py`.
