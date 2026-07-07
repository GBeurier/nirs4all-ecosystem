# Wave 7Z - Core 0.2.9 Release And Web Sync

Date: 2026-07-07

## Scope

Publish the custom-host capability manifest contract as a versioned
`nirs4all-core` release candidate and propagate the version into
`nirs4all-web`.

## Integrated heads

- `nirs4all-core`: `f0f9869 chore(release): bump core to 0.2.9`
- Tag: `v0.2.9`
- `nirs4all-web`: `9b6b944 chore(web): sync core shim 0.2.9`
- `nirs4all-ecosystem`: submodule pins updated for core and web

## Core version changes

- Rust crate `nirs4all`: `0.2.9`
- npm package `nirs4all`: `0.2.9`
- R package `nirs4all`: `0.2.9`
- Python distribution `nirs4all-core`: `0.2.9`
- Python import surface `nirs4all_lite.__version__`: `0.2.9`

## Tests run

In `nirs4all-core`:

- `scripts/bump_version.sh --check`
- `PYTHONPATH=bindings/python/src python3 -m unittest bindings/python/tests/test_release_topology.py bindings/python/tests/test_cross_language_surface.py bindings/python/tests/test_capability_matrix.py`
  - 42 passed.
- `cargo fmt --all --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace`
  - 10 Rust tests passed.
- Direct WASM gate via Windows Node over WSL path:
  `node --test tests/index.test.js tests/execution.test.js` plus
  `tsc --project tsconfig.typecheck.json`
  - 16 passed.

In `nirs4all-web/studio-lite`:

- `npm run vendor:core`
- `npm run check:core-shim`
- `npx vitest run --config vitest.config.ts src/engine/nirs4all-core.test.ts src/app/custom-app-host.contract.test.ts`
  - 10 passed.
- `npm run typecheck`

## Publication status

- `nirs4all-core` tag `v0.2.9` was pushed. Release workflows are expected to
  publish/attach non-Python artifacts where registry credentials are valid.
- Known risk: the Python `nirs4all-core` PyPI workflow may still require PyPI
  Trusted Publisher configuration; previous `v0.2.8` had failed there.
- `nirs4all-web` Pages deployment is triggered by the web push.

## Risks

- Full strict Python parity was not rerun in this release bump; strict parity was
  kept for the next large parity batch per operator guidance.
- R and MATLAB/Octave local native checks are still unavailable in this WSL
  environment; CI workflows cover those release paths.
