# Wave 6W - Core Methods Extra

Date: 2026-07-06

## Scope

- Repo: `nirs4all-core`
- Head: `ce32154`
- Lane: Python packaging / release train dependency consistency

## Problem

`nirs4all-core[methods]` installed `nirs4all-methods` and `scikit-learn`, but the Python portable
runner imports both `n4m` and `pls4all.sklearn.PLSRegression`. Since `nirs4all-methods` exposes the
`n4m` package and `pls4all` is a separate distribution, the extra could install successfully while
`run_portable_pipeline()` failed on first use.

## Changes

- Added `pls4all>=1.0.5` to `nirs4all-core[methods]`.
- Raised `nirs4all-methods` minimum from `>=1.0.2` to `>=1.0.5`.
- Added `pls4all>=1.0.5` to `nirs4all-core[all]`.
- Raised optional `nirs4all-datasets` from `>=0.3.3` to `>=0.3.4`.
- Updated installation docs and release-topology tests to prevent regression.

## Validation

From `nirs4all-core`:

- `PYTHONPATH=bindings/python/src python3 -m unittest bindings/python/tests/test_release_topology.py bindings/python/tests/test_upstreams.py bindings/python/tests/test_execution_parity.py -v`
  - 21 tests run, 1 skipped because local native methods bindings were not installed
- `PYTHONPATH=bindings/python/src python3 -m unittest discover -s bindings/python/tests -v`
  - 60 tests run, 1 skipped for the same local native methods binding absence
- `git diff --check`
- `python3.11` TOML validation of the updated extras

## Risk

Low. This is a packaging metadata fix. It does not migrate the runner from `pls4all` to `n4m`, which
would be a separate parity-sensitive runtime change.
