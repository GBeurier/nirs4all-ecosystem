# Wave 7V — Release Publication And Core/Web Alignment

Date: 2026-07-07

## Scope

- Protected `nirs4all-ui` and `nirs4all-quality`: not modified; another agent owns that work.
- Production-held repos `nirs4all` Python and `nirs4all-studio`: no release switch performed.
- Updated release monitoring, release contracts, and submodule pins for the V1 RC batch.

## Integrated commits

- `nirs4all-core`: `54fcdc5ee2afedf87d94a611725d38fe455fe4bc`, tag/release `v0.2.8`.
- `nirs4all-methods`: `90ccd89a8533018edcd34f5f08b0e2f74f75d419`, tag/release `v1.0.6`.
- `nirs4all-providers`: `12b9f65c7222ad85731f329a9de6c53fd69e06ce`, tag/release `v0.2.6`.
- `nirs4all-web`: `815058670d142d8ce1963a16c5c33ce1d2c1e804`.
- `nirs4all-org`: `3a5ac880052d6bc903b586f27a290d3ffc8fee47`.
- `nirs4all-cockpit`: `dba9fabeef4892dc3e60c7a1888be0786c098929`.

## Publication status

- Core aggregate:
  - npm `nirs4all@0.2.8`: published.
  - crates.io `nirs4all = 0.2.8`: published.
  - GitHub Release `nirs4all-core v0.2.8`: published.
  - R/R-universe target `nirs4all 0.2.8`: visible in cockpit as green.
  - PyPI `nirs4all-core`: still missing; release workflow fails with PyPI Trusted Publisher `invalid-publisher` for `repo:GBeurier/nirs4all-core:environment:pypi`.
- Methods:
  - npm `@nirs4all/methods@1.0.6`: published.
  - PyPI `nirs4all-methods==1.0.6` and `pls4all==1.0.6`: published.
  - R/R-universe `n4m` and `pls4all` 1.0.6: visible in cockpit as green.
  - GitHub Release and source/MATLAB/R/Python/npm/wheels jobs: green.
  - Attempted npm deprecation of old `@nirs4all/methods-wasm <=1.0.5`; npm emitted per-version notices but returned 404 and the registry did not expose a `deprecated` field afterward, so this remains a manual npm ownership action.
- Providers:
  - GitHub Release `nirs4all-providers v0.2.6`: published.
  - GitHub Pages provider site: green.
  - PyPI `nirs4all-providers`: still missing; release workflow fails with PyPI Trusted Publisher `invalid-publisher` for `repo:GBeurier/nirs4all-providers:environment:pypi`.
- Web/org/cockpit:
  - `nirs4all-web` web-ci and Pages green on `8150586`; app remains client-side-only.
  - `nirs4all-org` version guard and Pages green on `3a5ac88`.
  - `nirs4all-cockpit` refreshed `data/current.json` at 2026-07-07T00:27:46Z: `green=86`, `stale=2`, `pending=4`, `missing=7`, `unknown=0`, `excluded=1`.

## Tests and validation

- `nirs4all-core` local:
  - `scripts/bump_version.sh --check`.
  - Python release topology/facade/upstreams/cross-language unit tests: 43 passed.
  - `npm test --prefix bindings/wasm`: 16 passed plus typecheck.
  - `make test-v1-surfaces`: Rust/Python/npm surfaces pass; R and Octave skipped locally because not installed.
- `nirs4all-web` local:
  - `npm run check:core-shim`.
  - Targeted Vitest for core/client-side-only tests: 10 passed.
  - `npm run typecheck`.
  - `git diff --check`.
- `nirs4all-cockpit` local:
  - `n4a-cockpit validate-targets ops/targets.yaml`: OK, 21 packages, 100 targets.
  - `pytest -q`: 112 passed.
  - `ruff check .`: passed.
  - Fixed collection logic so stale coordination tags no longer override a real production tag that covers the manifest version.
- `nirs4all-ecosystem` local before this report:
  - JSON validation for release manifest, lock, and public V1 surface matrix.
  - `pytest -q tests/test_release_lock.py tests/test_e2e_scenarios.py`: 99 passed.
  - `scripts/n4a_release_lock.py checkout-members ... --output /tmp/n4a-selected-lock`, then `scripts/n4a_release_lock.py --workspace-root /tmp/n4a-selected-lock validate ...`: lock validated.

## Decisions

- Canonical JS/WASM methods package is `@nirs4all/methods`; no compatibility alias is kept in the V1 surface matrix.
- Providers V1 surface is limited to datasets and repository. Benchmarks and papers remain in their owning repos/plugins.
- Core remains the canonical aggregate project. Python distribution is `nirs4all-core`; non-Python aggregate publications continue under `nirs4all` where there is no Python namespace conflict.
- `nirs4all-lite` is only a retired old checkout / historical name during
  cutover; no public compatibility alias is kept in the V1 surface matrix.

## Risks and remaining decisions

- PyPI Trusted Publishers for `nirs4all-core` and `nirs4all-providers` must be created manually on PyPI before rerunning the failed release jobs.
- npm deprecation for `@nirs4all/methods-wasm` still needs a token/account with package ownership; current attempt did not persist a registry `deprecated` field.
- Full Python-reference parity was not rerun in this wave, per instruction to reserve it for larger batches.
- `nirs4all-ui` assets/components remain intentionally untouched in this wave because another agent is working there for `nirs4all-quality`.
