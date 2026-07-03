# Wave 4Y - Studio Frontend And Methods/Core WASM Gates

Date: 2026-07-03

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Scope

Wave 4Y closes two remaining local RC gates after the full Python parity and
fetchability follow-up:

- full Studio frontend Vitest on the selected Studio RC head;
- nirs4all-methods JS/WASM build/stage/test plus nirs4all-core strict WASM
  parity against that staged dist.

## Integrated Heads

- `nirs4all-studio`: unchanged at `75f511b`.
- `nirs4all-methods`: unchanged at `a24b06b`; generated JS/WASM artifacts are
  local build outputs, not source commits.
- `nirs4all-core`: moved to `2b0d18a fix(core): resolve methods wasm dist path absolutely`.
- `nirs4all-ecosystem`: aggregation lock regenerated to pin Core `2b0d18a`.

## Tests Run

Studio frontend:

- `PATH=/home/delete/.vscode-server/bin/1b50d58d73426c9171299ec4037d01365d995b78:$PATH node_modules/.bin/vitest run`
- Result: `517 passed` test files, `3709 passed` tests, duration `13.59s`.
- Claude read-only reviewer reran/confirmed the same full frontend gate:
  `517` test files, `3709` tests, `0 failed`, `0 skipped`.
- Scope note: Studio's Vitest include covers `src/**` and `electron/**`. It
  does not execute tests stored inside the vendored `vendor/nirs4all-ui`
  package. Shared UI source behavior remains owned by the `nirs4all-ui` repo
  gate and Studio/Web shim drift checks.

Methods JS/WASM:

- Environment: `source /home/delete/emsdk/emsdk_env.sh`
  - `emcc 5.0.7`
  - Node `v22.16.0`
  - npm `10.9.2`
- `make test-js-wasm`
- Result: passed.
  - Built CMake preset `emscripten` and target `pls4all_wasm`.
  - Staged `bindings/js/dist/index.js`, `bindings/js/dist/n4m.js`,
    `bindings/js/dist/n4m.wasm`.
  - JS smoke/parity tests passed, including native Python `pls4all` parity:
    coefficients, x_mean, y_mean, and predictions `rmse_rel` around `1e-16`.
  - `npm pack --dry-run` produced `nirs4all-methods-wasm-1.0.1.tgz` with
    `dist/index.js`, `dist/index.d.ts`, `dist/n4m.js`, and `dist/n4m.wasm`.

Core WASM strict parity:

- Initial run with `NIRS4ALL_METHODS_ROOT=../RC-v1-methods` exposed a false
  path failure because `npm --prefix bindings/wasm` interpreted the relative
  dist path from `bindings/wasm`.
- Core fix `2b0d18a` makes default `NIRS4ALL_METHODS_JS_DIST` absolute via
  `$(abspath ...)`.
- Re-run:
  - `PATH=/home/delete/emsdk/node/22.16.0_64bit/bin:$PATH make check-wasm-methods-artifact NIRS4ALL_METHODS_ROOT=../RC-v1-methods`
  - `PATH=/home/delete/emsdk/node/22.16.0_64bit/bin:$PATH make test-wasm-parity-strict NIRS4ALL_METHODS_ROOT=../RC-v1-methods`
- Result: strict WASM tests `15 pass`, `0 fail`, `0 skipped`, then TypeScript
  typecheck passed.
- Claude read-only reviewer confirmed the strict gate is not decorative when
  the staged Methods dist is present: the WASM tests load real
  `n4m.js`/`n4m.wasm`, report Methods WASM `1.0.1+abi.2.0.0`, and compare
  native fixture parity at machine-epsilon scale.
- `PYTHONPATH=bindings/python/src python3.11 -m unittest -v bindings/python/tests/test_release_topology.py`:
  `12 tests OK`.
- `git diff --check`: passed.

Ecosystem:

- `python3.11 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees generate ...`: regenerated lock.
- `python3.11 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate ...`: passed.
- `python3.11 scripts/n4a_release_lock.py audit-fetchability ... --fail-on-unfetchable`: `7/7 member commits checked out (0 unfetchable)`.
- `python3.11 scripts/n4a_release_surface_matrix.py validate`: passed.
- `pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py`: `16 passed`.

## Decisions

- Core's strict WASM parity target now tolerates relative `NIRS4ALL_METHODS_ROOT`
  while still requiring a real staged Methods JS/WASM dist.
- The `bindings/wasm/package.json` and `test-wasm` release-surface entries in
  the aggregation lock refer to the Core aggregate npm package `nirs4all`, not
  to the Methods package. Methods JS/WASM is correctly represented as
  `@nirs4all/methods-wasm` under `nirs4all-methods/bindings/js`.
- The Methods JS/WASM dist remains generated release output. It is not committed
  into `nirs4all-methods`; CI/release builds it through the Emscripten preset
  and `bindings/js` package scripts.
- Studio frontend skip accounting is now closed for the selected RC head in the
  local Linux/Node environment.

## Remaining Risks

- R and Octave/MATLAB execution remain external toolchain gates.
- Full non-Python DatasetPackage materialization remains an environment gate.
