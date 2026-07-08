# Wave 9K - Core/Repository Release Refresh and Legacy Alias Shutdown

Date: 2026-07-08

## Scope

Refreshed the public release state after `nirs4all-core` `0.3.3`, tightened the
provider-facing wording in `nirs4all-repository`, published a corrected
`nirs4all-repository` `0.1.10`, and updated the public cockpit snapshot.

## Files Modified

- `nirs4all-repository/CHANGELOG.md`
- `nirs4all-repository/README.md`
- `nirs4all-repository/VERSION`
- `nirs4all-repository/catalog/index.json`
- `nirs4all-repository/docs/SPECIFICATION.md`
- `nirs4all-repository/docs/api.md`
- `nirs4all-repository/src/nirs4all_repository/__init__.py`
- `nirs4all-repository/src/nirs4all_repository/_version.py`
- `nirs4all-repository/tests/test_api.py`
- `nirs4all-cockpit/ops/targets.yaml`
- `nirs4all-cockpit/ops/manual-actions.yaml`
- `nirs4all-cockpit/tests/test_targets_topology.py`
- `nirs4all-cockpit/data/current.json`
- `nirs4all-cockpit/data/manual-actions.json`

## Decisions

- `get_pipeline_list()`, `get_pipeline()`, and `get_bundle()` remain public
  functions in `nirs4all-repository`; they are documented as canonical
  provider-facing entry points, not legacy aliases.
- `nirs4all-repository` `0.1.9` was published but superseded immediately because
  its generated catalogue index had not been refreshed. `0.1.10` is the selected
  release candidate and contains the regenerated `catalog/index.json`.
- The old local `nirs4all-lite` checkout had its `core` push remote removed, and
  the GitHub `GBeurier/nirs4all-lite` `release-*` workflows were disabled
  manually. CI/version-guard remain active for audit.
- R-universe sync could not be triggered with the available token
  (`HTTP 403: Resource not accessible by personal access token`), so
  `runiverse-core-rebuild` remains a real manual blocker.

## Tests and Verification

- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_release_surface_matrix.py --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --matrix docs/contracts/release/public-v1-surface-matrix.n4a.json validate`
- `cd nirs4all-repository && python3.11 -m ruff check .`
- `cd nirs4all-repository && python3.11 -m pytest -q`
- `cd nirs4all-repository && python3.11 -m mypy src tests`
- `cd nirs4all-repository && python3.11 -m build --outdir /tmp/n4a-repository-0110-dist`
- `cd nirs4all-cockpit && ruff check .`
- `cd nirs4all-cockpit && pytest -q`
- `cd nirs4all-cockpit && /home/delete/.vscode-server/bin/1b50d58d73426c9171299ec4037d01365d995b78/node --check web/app.js`
- `cd nirs4all-cockpit && python3 scripts/smoke_dashboard_dom.py`

## Published/Green

- `nirs4all-core` `v0.3.3`: GitHub Release, PyPI `nirs4all-core`, npm
  `nirs4all`, crates.io `nirs4all`, MATLAB/Octave archive, and R tarball assets
  are published. R-universe remains stale at `0.3.1`.
- `nirs4all-repository` `v0.1.10`: GitHub Release assets and PyPI
  `nirs4all-repository` `0.1.10` are published; repository CI/docs/Pages/CodeQL
  and version-guard are green.
- `nirs4all-cockpit` `c04f58e`: `ci`, `pages`, and `version-guard` are green.
  The public JSON at `https://cockpit.nirs4all.org/data/current.json` reports
  `nirs4all-core` `0.3.3` and `nirs4all-repository` `0.1.10`.

## Remaining Risks

- R-universe for the core aggregate still needs a manual rebuild.
- CRAN submissions remain manual/pending.
- Dirty concurrent work remains in `nirs4all-ui` and `nirs4all-io`; this wave
  did not modify those worktrees.
