# Wave 8Q - Core Providers Fallback Assets

Date: 2026-07-07

## Scope

- Published Python wheel/sdist fallback assets to GitHub Releases for
  `nirs4all-core` and `nirs4all-providers` while PyPI Trusted Publisher setup
  remains external.
- Refreshed `nirs4all-core` release checksums to include the newly attached
  Python artifacts.
- Updated `nirs4all-cockpit` and this ecosystem pointer; production-held
  `nirs4all` Python and `nirs4all-studio` were not released.

## Published Assets

`nirs4all-core` release `v0.2.13`, rebuilt from tag commit
`38f536350b2f40cdc1ca52fa28e431af2cb3e4e9`:

- `nirs4all_core-0.2.13-py3-none-any.whl`
- `nirs4all_core-0.2.13.tar.gz`
- `SHA256SUMS` regenerated to include source/SBOM, MATLAB/Octave, R tarball,
  and Python fallback assets.

`nirs4all-providers` release `v0.2.7`, rebuilt from tag commit
`d22431478ff31ac00ab2b6318becbb1666875c43`:

- `nirs4all_providers-0.2.7-py3-none-any.whl`
- `nirs4all_providers-0.2.7.tar.gz`

## Cockpit Changes

- `nirs4all-cockpit`: `23f1468d2e9bf41f8b215b6860f3d63eac81f8c7`
- Updated `nirs4all-core` PyPI and GitHub Release target reasons to state that
  `v0.2.13` carries Python wheel/sdist fallback assets.
- Kept PyPI targets missing; the fallback assets do not replace Trusted
  Publisher setup or real PyPI publication.
- Added topology assertions so the cockpit cannot regress to saying core Python
  wheel/sdist assets are absent.

## Tests

Asset builds:

- `python3.11 -m build --outdir /tmp/n4a-core-v0.2.13-dist /tmp/n4a-core-v0.2.13-build/bindings/python`
- `python3.11 -m build --outdir /tmp/n4a-providers-v0.2.7-dist /tmp/n4a-providers-v0.2.7-build`
- `python3.11 -m twine check /tmp/n4a-core-v0.2.13-dist/* /tmp/n4a-providers-v0.2.7-dist/*`
- `gh release view v0.2.13 --repo GBeurier/nirs4all-core --json assets`
- `gh release view v0.2.7 --repo GBeurier/nirs4all-providers --json assets`

`nirs4all-cockpit`:

- `ruff check .`
- `pytest -q` (`119 passed`)
- `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
- `python3.11 -m cockpit.cli summarize data/current.json`
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH node --check web/app.js`
- `python3.11 scripts/smoke_dashboard_dom.py`
- `git diff --check`

`nirs4all-ecosystem`:

- `python3.11 scripts/n4a_release_surface_matrix.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable`
- `git diff --check`

## Remaining Risks

- PyPI Trusted Publisher setup is still required for real PyPI publication.
- CRAN remains manual.
- `dagmldata` R-universe rebuild was triggered in Wave 8P but was still pending
  at last check.
- `nirs4all-ui` quality-facing `lab/theme/quali` surfaces remain local and
  unpublished; they were not touched in this wave.
