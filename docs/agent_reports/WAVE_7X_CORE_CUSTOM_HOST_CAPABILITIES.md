# Wave 7X - Core Custom Host Capabilities

Date: 2026-07-07

## Scope

Expose an inspect-only V1 capability manifest from `nirs4all-core` so custom
hosts can combine `nirs4all-core` runtimes with `nirs4all-ui` without
duplicating portable pipeline eligibility rules.

## Integrated head

- `nirs4all-core`: `12d48fe feat(capabilities): expose custom host manifests`
- `nirs4all-ecosystem`: submodule pin updated to `12d48fe`

## Files changed in core

- Python: `bindings/python/src/nirs4all_lite/_capabilities.py`,
  `__init__.py`, `_topology.py`, facade/capability tests.
- JavaScript/WASM: `bindings/wasm/src/index.js`, `index.d.ts`,
  `tests/index.test.js`, `README.md`.
- R: `bindings/r/R/capabilities.R`, `NAMESPACE`,
  `tests/surface.R`, `man/nirs4all_capabilities.Rd`.
- Rust: `bindings/rust/nirs4all/src/lib.rs`.
- MATLAB/Octave: `+nirs4all/capabilityManifest.m`,
  `controllerCapabilities.m`, `runtimeSurfaces.m`, `tests/smoke.m`.
- Contract/docs: `compat/capabilities.toml`, `docs/CAPABILITIES.md`.

## Decisions

- The manifest schema is `nirs4all-core.capabilities.v1`.
- Stable controller IDs:
  `split.kennard_stone`, `preprocess.snv`, `preprocess.savgol`,
  `model.pls_regression`, `pipeline.portable_methods`.
- Parameters intentionally match the executable parser today:
  `test_size`; no SNV parameters; Savitzky-Golay
  `window_length/polyorder/deriv/mode/cval`; PLS `n_components/_range_`.
- The manifest is inspect-only. Execution still delegates through the portable
  methods pipeline and `nirs4all-methods`.
- `nirs4all-ui` and `nirs4all-quality` were not touched because another agent is
  actively working there.

## Tests run

- `PYTHONPATH=bindings/python/src python3 -m unittest discover -s bindings/python/tests`
  - 69 passed-equivalent outcomes: 68 passed, 1 skipped.
  - Skip: strict Python execution parity because `nirs4all-methods` Python
    bindings are not installed in this local environment.
- `PYTHONPATH=bindings/python/src python3 -m unittest ...test_release_topology.py ...test_capability_matrix.py`
  - 65 passed, 0 skipped.
- `node --test tests/*.test.js` plus `tsc --project tsconfig.typecheck.json`
  from `bindings/wasm`
  - 17 passed, 0 skipped.
- `cargo fmt --all --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace`
  - 10 Rust tests passed, including Rust oracle parity through the available
    methods library.
- `git diff --check`
  - clean.

## Not run

- R V1 surface / R CMD check: local `R`/`Rscript` are not installed.
- MATLAB/Octave smoke/parity: local `octave` is not installed.
- Full Python strict parity: intentionally deferred to the next large parity
  batch and blocked locally by the missing Python `nirs4all-methods` binding.

## Risks

- Web/studio-lite still vendors a shim and does not yet consume
  `capabilityManifest()`. The core-side contract is now present for a later
  non-conflicting web integration.
- R and MATLAB/Octave manifest functions are statically covered by Python source
  tests, but their native smoke tests need a host with R/Octave installed.
