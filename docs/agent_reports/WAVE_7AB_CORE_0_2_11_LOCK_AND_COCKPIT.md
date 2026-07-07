# Wave 7AB - Core 0.2.11 Lock And Cockpit

Date: 2026-07-07

## Scope

Close the `nirs4all-core` micro-release train after the `0.2.9` custom-host
release exposed two release hygiene gaps: the root Cargo lockfile was not
version-checked, and the changelog/package-lock state lagged behind published
artifacts.

## Integrated heads

- `nirs4all-core`: `615a154 chore(release): bump core to 0.2.11`
- Tag: `v0.2.11`
- `nirs4all-web`: `20039fe chore(web): sync core shim 0.2.11`
- `nirs4all-cockpit`: `6e85be5 chore(targets): track core 0.2.11 release`

## Files changed

In `nirs4all-core`:

- `CHANGELOG.md`
- `Cargo.lock`
- all core binding version manifests
- `scripts/bump_version.sh`

In `nirs4all-web`:

- `studio-lite/vendor/nirs4all/package.json`
- `studio-lite/package-lock.json`

In `nirs4all-cockpit`:

- `data/current.json`
- `ops/targets.yaml`
- `ops/manual-actions.yaml`
- `tests/test_targets_topology.py`

In `nirs4all-ecosystem`:

- `nirs4all-core`, `nirs4all-web`, `nirs4all-cockpit` submodule pins
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- this report

## Tests run

In `nirs4all-core`:

- `scripts/bump_version.sh --check`
- `PYTHONPATH=bindings/python/src python3 -m unittest bindings/python/tests/test_release_topology.py bindings/python/tests/test_cross_language_surface.py bindings/python/tests/test_capability_matrix.py`
  - 42 passed.
- `cargo fmt --all --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace`
  - 10 Rust tests passed.
- PowerShell/Windows Node over WSL path:
  `node --test tests/index.test.js tests/execution.test.js` plus
  `node node_modules/typescript/bin/tsc --project tsconfig.typecheck.json`
  - 16 Node tests passed, typecheck passed.

In `nirs4all-web/studio-lite`:

- `npm run vendor:core`
- `npm install --package-lock-only --ignore-scripts`
- `npm run check:core-shim`
- `npx vitest run --config vitest.config.ts src/engine/nirs4all-core.test.ts src/app/custom-app-host.contract.test.ts`
  - 10 passed.
- `npm run typecheck`

In `nirs4all-cockpit`:

- `.venv/bin/python -m pytest -q`
  - 113 passed.
- `.venv/bin/n4a-cockpit validate-targets ops/targets.yaml`
  - 21 packages, 100 targets.
- `.venv/bin/ruff check .`

In `nirs4all-ecosystem`:

- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_e2e_scenarios.py`
  - 109 passed.
- `python3 scripts/n4a_e2e_scenarios.py validate`
  - 11 scenarios valid.
- `python3 scripts/n4a_e2e_scenarios.py coverage`
  - 11/11 ready; remaining debt unchanged.

## Publication status

- `nirs4all-core` `v0.2.11`: `CI`, `release-crates`, `release-source`,
  `release-npm`, `release-r`, and `release-matlab` passed.
- Registry/release checks:
  - crates.io reports `nirs4all = 0.2.11`;
  - npm reports `nirs4all@0.2.11`;
  - GitHub Release `v0.2.11` contains source archives, CycloneDX SBOM,
    `SHA256SUMS`, `nirs4all_0.2.11.tar.gz`, and
    `nirs4all-matlab-octave-0.2.11.zip`.
- `nirs4all-web` `version-guard`, `web-ci`, and GitHub Pages passed on
  `20039fe`.
- `nirs4all-cockpit` `version-guard` and Pages passed on `6e85be5`.

## Decisions

- Published `0.2.11` rather than rewriting `0.2.10`, because `v0.2.10` had
  already been pushed publicly.
- Added `Cargo.lock` validation to `scripts/bump_version.sh` so version drift
  in the tracked Rust lockfile becomes a release-blocking check.
- Updated the web npm lockfile for the vendored core package; this was not
  covered by `sync-core-shim`.
- Reopened `runiverse-core-rebuild` as `todo`: R-universe still serves
  `nirs4all 0.2.8`, despite the `0.2.11` R tarball being attached to the
  GitHub Release.
- Patched only the `lite`/`nirs4all-core` member in the aggregation lock. A
  full regeneration against `_worktrees` would have downgraded unrelated
  selected members, so it was rejected.

## Risks

- PyPI `nirs4all-core` remains blocked externally by Trusted Publisher
  `invalid-publisher`; PyPI still returns 404.
- R-universe remains stale at `0.2.8`; the cockpit marks this explicitly.
- Custom-host parity is not yet strict and uniform across all runtimes:
  WASM has the strongest serialized-model/predict surface, while R/Rust/MATLAB
  currently validate execution/capability surfaces without the same reusable
  model contract.
- The GitGuardian signal for `nirs4all-cluster` appears remediated in the
  current tree, but any historically exposed real credential must still be
  treated as compromised and rotated outside this repo.
