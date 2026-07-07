# Wave 8M - Cockpit Snapshot And CI Gate

Date: 2026-07-07

## Scope

- `nirs4all-cockpit`: refreshed the public snapshot after live R-universe
  reported `nirs4allformats` and `nirs4allformats.lite` at 0.2.4.
- `nirs4all-cockpit`: added a real CI gate for `ruff`, `pytest`,
  inventory validation, JavaScript syntax, and headless Chrome dashboard smoke.
- `nirs4all-ecosystem`: submodule pointer updated to the reviewed cockpit head.

## Integrated Head

- `nirs4all-cockpit`: `f8d033fbf7a92707d6af9a78ccddded2c873e697`.

## Files Modified

- `nirs4all-cockpit`
  - `.github/workflows/ci.yml`
  - `scripts/smoke_dashboard_dom.py`
  - `data/current.json`
  - `data/manual-actions.json`
- `nirs4all-ecosystem`
  - `docs/RELEASE_DISTRIBUTION_MATRIX.md`
  - `docs/agent_reports/WAVE_8M_COCKPIT_SNAPSHOT_AND_CI_GATE.md`
  - submodule: `nirs4all-cockpit`

## Results

- Cockpit summary changed from `green=84 stale=5 pending=4 missing=7` to
  `green=86 stale=3 pending=4 missing=7`.
- `nirs4all-formats` rollup is now green in the public snapshot:
  `nirs4allformats=0.2.4` and `nirs4allformats.lite=0.2.4` on R-universe.
- `runiverse-formats-rebuild` resolves automatically in
  `data/manual-actions.json`.
- `nirs4all-ecosystem` source now points at
  `58d6ee2da37060feaef197389cf1e3c3f6c63d5e`, whose GitHub Actions passed.
- The cockpit public site deployed the refreshed data snapshot from
  `387ed375d788b2a1244338f8b367389f68f95c47`; the follow-up CI-only head
  `f8d033f` passed `ci` and `version-guard`.

## Tests

- `nirs4all-cockpit`: `python3.11 -m ruff check .`.
- `nirs4all-cockpit`: `python3.11 -m pytest -q` -> 119 passed.
- `nirs4all-cockpit`: `python3.11 -m cockpit.cli validate-targets
  ops/targets.yaml`.
- `nirs4all-cockpit`: `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH
  node --check web/app.js`.
- `nirs4all-cockpit`: `python3.11 scripts/smoke_dashboard_dom.py`.
- `nirs4all-cockpit`: `git diff --check`.
- GitHub Actions: `nirs4all-cockpit` `ci` and `version-guard` passed on
  `f8d033f`; Pages passed on the data snapshot commit `387ed37`.

## Risks

- PyPI Trusted Publisher blockers remain for seven package surfaces and are
  still visible in the cockpit.
- CRAN and `dagmldata` R-universe rebuild remain manual/external blockers.
- Full Python-reference parity was not run in this cockpit/UI/e2e batch.
