# Wave 7AC - Runtime Contracts 0.2.12

## Scope

Clarify the custom-app host contract after the `nirs4all-core` capability
manifest work: portable pipeline execution remains parity-validated across the
aggregate surfaces, while standalone serialized selected-model prediction is
explicitly advertised only for JavaScript/WASM through `predictPortablePipeline`.

## Commits

- `nirs4all-core`: `563d334 feat(capabilities): expose runtime contracts`
- Tag: `v0.2.12`
- `nirs4all-web`: `c98f5f6 feat(studio-lite): assert core runtime contracts`
- `nirs4all-cockpit`: `98581d6 chore(targets): track core 0.2.12 release`
- `nirs4all-ecosystem`: `a5cfb59 test(e2e): require custom host runtime contracts`

## Files Modified

- Core capability manifests and binding surfaces:
  `compat/capabilities.toml`, Python `_capabilities.py`, WASM `src/index.js`
  and `src/index.d.ts`, R `capabilities.R`, Rust `lib.rs`, MATLAB/Octave
  `runtimeContracts.m`.
- Web vendored core shim and custom-host contract tests under
  `nirs4all-web/studio-lite`.
- Ecosystem E2E custom-host manifest and docs.
- Cockpit target/status files for the `0.2.12` train.

## Tests Run

- `nirs4all-core`: `scripts/bump_version.sh --check`
- `nirs4all-core`: `make test`
- `nirs4all-core`: `make test-v1-surfaces`
- `nirs4all-web/studio-lite`: `npm run check:core-shim`
- `nirs4all-web/studio-lite`: `npx vitest run --config vitest.config.ts src/engine/nirs4all-core.test.ts src/app/custom-app-host.contract.test.ts`
- `nirs4all-web/studio-lite`: `npm run typecheck`
- `nirs4all-ecosystem`: `python3 -m pytest -q tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py validate`
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py coverage`
- `nirs4all-cockpit`: `.venv/bin/python -m pytest -q`
- `nirs4all-cockpit`: `.venv/bin/n4a-cockpit validate-targets ops/targets.yaml`
- `nirs4all-cockpit`: `.venv/bin/ruff check .`

## Publication Status

- crates.io: `nirs4all = 0.2.12`
- npm: `nirs4all@0.2.12`
- GitHub Release `v0.2.12`: source archives, CycloneDX SBOM, `SHA256SUMS`,
  R source tarball, and MATLAB/Octave zip are attached.
- PyPI `nirs4all-core`: still blocked by Trusted Publisher
  `invalid-publisher` on `release-python.yml`, environment `pypi`.

## Decisions

- `controllers[].runtime` continues to describe portable pipeline execution.
- Hosts must read `runtime_contracts` / `runtimeContracts` for replay-predict
  capability. Only `javascript_wasm` currently sets serialized-model prediction
  to true.
- No full parity suite was launched in this batch; the change was contract and
  release-surface scoped.

## Risks

- R and Octave were unavailable locally; `make test-v1-surfaces` recorded those
  as SKIP/RISK while CI release workflows for R and MATLAB/Octave passed.
- PyPI publication needs the external Trusted Publisher configuration before
  rerunning `release-python`.
