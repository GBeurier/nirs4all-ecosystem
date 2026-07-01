# W92 - nirs4all-methods Package Surface, Bindings, And Parity Gate

Date: 2026-07-01

## Scope

Worktree: `/home/delete/nirs4all/_worktrees/W92-methods-release-surface`
Branch: `refactor/W92-methods-release-surface`
Base: `nirs4all-methods/main` at `7602eb08`

Audited `nirs4all-methods` package metadata, Python/R binding docs, ABI
snapshots/docs, catalog ABI validation, CI parity gates, and the live
cross-binding Python-reference gate. No public C ABI symbols were renamed.

## Changes

Commit:

- `d077ea5f fix(package): clarify Python release surface`

Changed files:

- `README.md`
- `bindings/python/README.md`
- `bindings/python/pyproject.toml`
- `bindings/python/scripts/make_python_package.py`
- `bindings/python/src/n4m/_impl/compat.py`
- `bindings/python/tests/test_release_surface_metadata.py`

What changed:

- Clarified that `nirs4all-methods` is the install distribution and `n4m` is the
  Python import package / ABI prefix.
- Removed stale public `n4m.sklearn` guidance from the top-level quick start and
  generated `nirs4all-methods` README; ABI 2 full-package examples now use
  `n4m.<role>` imports.
- Updated Python package metadata URLs to the current `nirs4all-methods` repo.
- Documented `N4M_LIB_PATH` as the shared libn4m override for `pls4all`.
- Added a focused package-generator test proving the generated full and slim
  package directories do not confuse the distribution/import split.

## Verification

Passed:

- `python3 -m ruff format --check bindings/python/scripts/make_python_package.py bindings/python/tests/test_release_surface_metadata.py bindings/python/src/n4m/_impl/compat.py`
- `python3 -m ruff check bindings/python/scripts/make_python_package.py bindings/python/tests/test_release_surface_metadata.py bindings/python/src/n4m/_impl/compat.py`
- `python3 -m pytest bindings/python/tests/test_release_surface_metadata.py -q`
- `scripts/bump_version.sh --check`
- `python3 bindings/python/scripts/make_python_package.py --name nirs4all-methods` with generated README inspected, then generated dir removed.
- `make build PRESET=dev-debug` with broken conda `gfortran` hidden from `PATH` so CMake used the repo's no-FITPACK fallback.
- `make test PRESET=dev-debug` with the same toolchain workaround: `2/2` CTest tests passed.
- Linux ABI symbol snapshot diff against `cpp/abi/expected_symbols_linux.txt` using CI-style `@@N4M_2` suffix stripping.
- `readelf -d build/dev-debug/cpp/src/libn4m.so.2.0.0 | grep -E 'SONAME|NEEDED|RPATH|RUNPATH'`: SONAME `libn4m.so.2`; no RPATH/RUNPATH.
- `python3 catalog/scripts/validate.py --strict-abi --check-references`: `702/702` exported symbols covered; reference coverage `209/209`.
- `N4M_LIB_PATH=$PWD/build/dev-debug/cpp/src/libn4m.so.2.0.0 PYTHONPATH=bindings/python/src python3 -m pytest bindings/python/tests/test_release_surface_metadata.py bindings/python/tests/test_sklearn_optional.py bindings/python/tests/test_n4m_context.py -q`: `3 passed`.
- `python3 -m pytest benchmarks/cross_binding/tests/test_ci_parity_gate.py benchmarks/cross_binding/tests/test_parity_comparator.py benchmarks/cross_binding/tests/test_raw_manifest_reconciliation.py -q`: `16 passed, 1 skipped`.
- `make build PRESET=dev-release` with broken conda `gfortran` hidden from `PATH`, for live parity input.
- `BENCH_SKLEARN_N_JOBS=1 PYTHONPATH=$PWD/bindings/python/src:$PWD python3 benchmarks/cross_binding/orchestrator.py --algorithms pls pcr --registry-cells --threads 1 --workers 1 --libn4m-build dev-release --n-runs 1 --canonical-pls4all-only --reference-backends registry --only registry_pls4all ref_python_scikit_learn --timeout 180 --out-csv /tmp/w92_methods_parity.csv --force --flush-each-cell`
  - `pls` n4m binding vs sklearn: `reference_parity_ok=True`, `rmse_rel=9.68e-16`, tolerance `1e-08`.
  - `pcr` n4m binding vs sklearn: `reference_parity_ok=True`, `rmse_rel=1.43e-14`, tolerance `1e-06`.
- `git diff --check`

Failures / retries:

- The first literal `make build PRESET=dev-debug` failed at link because the
  only visible Fortran compiler was `/home/delete/.local/bin/gfortran`, a conda
  wrapper that injected missing absolute system paths `/lib64/libm.so.6` and
  `/lib64/libmvec.so.1`. There is no `/usr/bin/gfortran` on this host. Retrying
  the same make target with `cmake`/`ninja` exposed but that broken Fortran
  wrapper hidden made CMake report `Fortran compiler - NOTFOUND` and use the
  intended pure-C fallback; build and tests then passed.

## Blockers

None for W92. The remaining broad generated method docs still contain many
`n4m.sklearn` references from generated per-method pages, but W92 intentionally
avoided a generated-doc rewrite. The ABI 2 migration guide and package release
surface now state the correct `n4m.<role>` full-package imports.

## Follow-Up Integration

Coordinator integration needed: merge `nirs4all-methods`
`refactor/W92-methods-release-surface` commit `d077ea5f`.

No ABI snapshot, version, or fixture update is required.
