# Wave 8P - Tools Fallback Assets And R-universe Trigger

Date: 2026-07-07

## Scope

- Published fallback distribution assets for `nirs4all-tools` while PyPI remains
  blocked by Trusted Publisher setup.
- Triggered the `dagmldata` R-universe rebuild path without touching production
  `nirs4all` Python or `nirs4all-studio`.
- Refreshed `nirs4all-cockpit` so the public dashboard reflects the new fallback
  assets and the resolved `nirs4allformats` R-universe action.

## Published Assets

`nirs4all-tools` release `v0.0.4` now carries:

- `nirs4all_tools-0.0.4-py3-none-any.whl`
- `nirs4all_tools-0.0.4.tar.gz`

The artifacts were rebuilt from the exact `v0.0.4` tag
`659cdab0074c847ebd474b6e7badda7bdeb361ad`, not from `main`.

## R-universe

- `GBeurier.r-universe.dev` already had remote commit
  `217f163 chore: pin dagmldata to main branch`.
- Added trigger commit
  `12992a9 chore: trigger dagmldata runiverse rebuild`.
- Live R-universe still reported `dagmldata` `0.2.4` immediately after the
  trigger; this remains pending until the external R-universe build completes.

## Cockpit Changes

- `nirs4all-cockpit`: `d402aa2c432226e7b25ec2deca7e628bf8f22cb1`
- Updated `nirs4all-tools` target reasons to state that GitHub Release fallback
  wheel/sdist assets are available.
- Updated `nirs4all-repository` target reason to reflect its existing
  `v0.1.6` wheel/sdist fallback assets.
- Marked `runiverse-formats-rebuild` done because `nirs4allformats` and
  `nirs4allformats.lite` are green at `0.2.4`.
- Corrected `pypi-publisher-tools.after_done` to rerun `publish.yml` from
  `v0.0.4`, matching the workflow's tag-only publish guard.

## Tests

`nirs4all-tools` assets:

- `python3.11 -m build --outdir /tmp/n4a-tools-v0.0.4-dist /tmp/n4a-tools-v0.0.4-build`
- `python3.11 -m twine check /tmp/n4a-tools-v0.0.4-dist/*`
- `gh release view v0.0.4 --repo GBeurier/nirs4all-tools --json assets`

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

- PyPI still requires Trusted Publisher setup for the missing Python projects.
- CRAN remains manual.
- `dagmldata` R-universe rebuild is triggered but not yet observed green.
- `nirs4all-ui` quality-facing `lab/theme/quali` surfaces remain local and
  unpublished; they were not touched in this wave.
