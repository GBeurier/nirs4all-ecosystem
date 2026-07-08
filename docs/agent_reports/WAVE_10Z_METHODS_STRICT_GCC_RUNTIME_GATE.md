# Wave 10Z - Methods strict GCC runtime gate

Date: 2026-07-09

Lane: F / C, `nirs4all-methods` native runtime used by strict ecosystem E2E.

## Scope

- Reviewed the failing GitHub full E2E runtime-prep step for `nirs4all-methods`.
- Fixed GCC strict diagnostics in AOM result construction without changing ABI or numerical logic.
- Aligned methods documentation index links with the facade-declared `doc_path` values surfaced by Python bindings.
- Repinned `nirs4all-ecosystem` to `nirs4all-methods` `5310ba5b87a87751d2a899eb3eac0aac48c597da`.

## Files changed upstream

- `cpp/src/core/aom_robust_hpo.cpp`
- `cpp/src/core/aom_ridge_blender.cpp`
- `cpp/src/core/aom_operator_pls_stack.cpp`
- `docs/methods/index.md`

## Tests run

- `cmake -S . -B build/ci-local-conda-release -G Ninja -DCMAKE_BUILD_TYPE=Release -DN4M_WARNINGS_AS_ERRORS=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_C_COMPILER=/home/delete/miniconda3/bin/x86_64-conda-linux-gnu-gcc -DCMAKE_CXX_COMPILER=/home/delete/miniconda3/bin/x86_64-conda-linux-gnu-g++ -DCMAKE_Fortran_COMPILER=/home/delete/.local/bin/gfortran`
- `cmake --build build/ci-local-conda-release --target n4m_c --parallel`
- `cmake --build build/ci-local-conda-release --target n4m_tests n4m_internal_tests --parallel`
- `LD_LIBRARY_PATH=/home/delete/miniconda3/lib:$LD_LIBRARY_PATH ctest --test-dir build/ci-local-conda-release --output-on-failure`
- `PYTHONPATH=bindings/python/src N4M_LIB_PATH=build/ci-local-conda-release/cpp/src/libn4m.so python3.11 -m pytest -q bindings/python/tests/test_moment_model_wrappers.py bindings/python/tests/test_aom_moment_facade.py`

## Results

- Native build passed with GCC 15.2.0 and `N4M_WARNINGS_AS_ERRORS=ON`.
- Native CTest passed: `2/2`.
- Python binding/facade tests passed: `110 passed, 1 skipped`.

## Decisions

- Used `vector::swap` for fold-id result transfer after all local uses of the source vector are complete.
- Used `assign(1U, value)` for the single-value intercept vector to avoid GCC initializer-list false positives.
- Updated public method index links to canonical runtime pages (`aom_ridge_*.md`) because facades already declare those docs as authoritative.

## Risks

- Exact local GCC 12 reproduction was unavailable because `gcc-12`/`g++-12` are not installed and passwordless `sudo` is disabled.
- GitHub Actions remains the exact GCC 12 gate; the full strict E2E must be rerun after this repin.
