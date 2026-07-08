# WAVE 10Q - R-universe Cockpit Refresh

Date: 2026-07-08

## Scope

Refresh the cockpit public snapshot after R-universe caught up for packages
already released from source:

- `nirs4allformats` from `nirs4all-formats` `0.2.6`
- `dagmldata` from `dag-ml-data` `0.2.8`

## Files Modified

- `nirs4all-cockpit/data/current.json`
- `nirs4all-cockpit/data/manual-actions.json`
- `nirs4all-ecosystem/nirs4all-cockpit`
- `nirs4all-ecosystem/docs/agent_reports/WAVE_10Q_RUNIVERSE_COCKPIT_REFRESH.md`

## Tests And Gates

- R-universe live probe:
  - `https://gbeurier.r-universe.dev/src/contrib/PACKAGES`
  - confirmed `dagmldata Version: 0.2.8`
  - confirmed `nirs4allformats Version: 0.2.6`
- `nirs4all-cockpit`:
  - `python3.11 -m cockpit.cli collect --only nirs4all-formats,dag-ml-data --out /tmp/n4a-cockpit-r-universe-refresh.json`
  - `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
  - `python3.11 -m pytest -q` -> `132 passed`
  - `python3.11 scripts/smoke_dashboard_dom.py` -> `dashboard smoke OK via google-chrome`
  - GitHub Actions for `17626ec`: `ci`, `version-guard`, and Pages succeeded.
- `nirs4all-ecosystem` before this report:
  - `python3.11 scripts/n4a_release_surface_matrix.py validate`
  - `python3.11 scripts/n4a_release_lock.py checkout-members ...`
  - `python3.11 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-release-lock-current-audit validate ...`
  - `python3.11 scripts/n4a_e2e_scenarios.py coverage`
  - `python3.11 scripts/n4a_e2e_scenarios.py evidence`

## Outcome

- Cockpit summary improved from `green=94 stale=3 pending=4 excluded=1` to
  `green=96 stale=1 pending=4 excluded=1`.
- Manual actions improved from `pending=8 resolved=15` to
  `pending=6 resolved=17`.
- Remaining manual actions are now restricted to:
  - Studio Windows RC smoke/build on native Windows.
  - CRAN manual submissions/resubmissions for `n4m`, `pls4all`,
    `nirs4allio`, `nirs4alldatasets`, and the aggregate `nirs4all` R package.

## Risks / Follow-Up

- The remaining CRAN items are manual registry actions; they are not fixed by
  pushing source changes alone.
- Studio production and `nirs4all` Python production remain intentionally held
  until the strict parity/cutover gates are complete.
