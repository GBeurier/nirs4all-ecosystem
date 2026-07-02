# RC-L Methods / Bindings Report

Date: 2026-07-02
Worktree: `/home/delete/nirs4all/_worktrees/RC-v1-methods`
Branch: `rc/v1-full-refactor`

## Scope audited

- Native ABI surface: `cpp/include/n4m/*.h`, `cpp/src/c_api/`, `cpp/tests/`
- Python bindings: full `bindings/python/src/n4m`, slim `bindings/python/src/pls4all`, packaging scripts/tests
- JS/WASM binding: `bindings/js/src`, `bindings/js/test`
- R bindings: `bindings/r/n4m`, `bindings/r/pls4all`
- MATLAB binding: `bindings/matlab/+pls4all`, `bindings/matlab/mex`, `bindings/matlab/test`
- Rust: only `bindings/_archive/rust/pls4all` is present, so this remains archival rather than an active RC surface

## Concrete changes

Added direct pytest coverage for the installed-wheel smoke script:

- `bindings/python/tests/test_installed_nirs4all_methods_smoke.py`

What it locks down:

- `discover_lib()` returns the first ABI-compatible `libn4m` candidate from local build outputs
- `discover_lib()` reports incompatible candidates with actionable diagnostics
- `_install_and_run()` scrubs host `PYTHONPATH` and `N4M_LIB_PATH` / `PLS4ALL_LIB_PATH` overrides before running the smoke child process

This closes a release-surface gap around `bindings/python/scripts/smoke_installed_nirs4all_methods.py`, which previously had no direct tests.

## Files modified

- `/home/delete/nirs4all/_worktrees/RC-v1-methods/bindings/python/tests/test_installed_nirs4all_methods_smoke.py`

## Tests run

Passed:

- `python3 -m pytest bindings/python/tests/test_installed_nirs4all_methods_smoke.py bindings/python/tests/test_binding_readme_abi_claims.py bindings/python/tests/test_release_surface_metadata.py -q`
  - Result: `8 passed in 0.05s`

Build attempted:

- `cmake --preset dev-release`
  - Result: configured successfully
- `cmake --build --preset dev-release --parallel 4`
  - Result: failed at link step for `cpp/src/libn4m.so.2.0.0`
  - Failure:
    - `/usr/bin/ld: cannot find /lib64/libm.so.6: No such file or directory`
    - `/usr/bin/ld: cannot find /lib64/libmvec.so.1: No such file or directory`

Coordinator follow-up:

- `cmake -S . -B build/rc-conda-release -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/home/delete/miniconda3/bin/x86_64-conda-linux-gnu-gcc -DCMAKE_CXX_COMPILER=/home/delete/miniconda3/bin/x86_64-conda-linux-gnu-g++ -DCMAKE_Fortran_COMPILER=/home/delete/miniconda3/bin/x86_64-conda-linux-gnu-gfortran && cmake --build build/rc-conda-release --parallel 4`
  - Result: passed.
- `LD_LIBRARY_PATH=/home/delete/miniconda3/lib:${LD_LIBRARY_PATH:-} ctest --test-dir build/rc-conda-release --output-on-failure -j4`
  - Result: `100% tests passed, 0 tests failed out of 2`.
- Diagnosis: the `dev-release` cache selected system `gcc/g++` with the
  Miniconda `gfortran`, producing a mixed toolchain link that asks `/usr/bin/ld`
  for `/lib64/libm.so.6` and `/lib64/libmvec.so.1`. A coherent conda toolchain
  links and runs the native tests in this environment.

Not run in this environment:

- JS/WASM tests: `node` unavailable
- R tests: `R` unavailable
- MATLAB/Octave tests: `octave` unavailable
- Installed-wheel smoke end to end: still not run as a wheel install, but the
  native library can be built and tested with a coherent conda toolchain as
  shown above.

## Decisions

- Preferred a focused release-surface test addition over speculative binding refactors.
- Treated Rust as archival-only because the repo surface is under `bindings/_archive/rust`, not an active binding directory.
- Did not patch presets in this lane because the `dev-release` failure is
  host/toolchain selection, not a repo-local defect exposed by the test change.
  The final RC should either document the coherent conda invocation or add a
  dedicated preset if methods is released from this WSL environment.

## Risks and open questions

- The Python installed-wheel smoke path is now unit-covered, but end-to-end release validation still depends on a successful native `libn4m` build in the execution environment.
- The local environment currently lacks `node`, `R`, and `octave`, so JS/R/MATLAB parity surfaces were audited structurally but not executed here.
- The `dev-release` link failure should be rechecked in the intended RC build environment before using this workspace as release evidence.

## Remaining gaps

- Re-run `bindings/python/scripts/smoke_installed_nirs4all_methods.py` once `libn4m` links successfully.
- Run the normal per-binding gates in a provisioned environment:
  - Python: broader `bindings/python/tests`
  - JS/WASM: `bindings/js/test/run_smoke.mjs` and related entrypoints
  - R: `bindings/r/*/tests/testthat.R`
  - MATLAB/Octave: `bindings/matlab/test/test_parity.m`
- Follow-up full parity is still needed after any integrated native/binding batch.
