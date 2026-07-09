# WAVE 10BA - Cockpit public shape and E2E gate refresh

Date: 2026-07-09T18:16:56Z

Lane: release/cockpit coordination + lightweight ecosystem gates

## Summary

- Removed the transient `Release bundles` dashboard surface from the public
  cockpit, including the visible `rc` / `production-held` channel chips.
- Removed `release_bundles` from the public cockpit snapshot shape so future
  collects do not republish a hidden dashboard-only field.
- Kept `ops/targets.yaml` release bundle metadata in cockpit as internal
  inventory/coordination data; it is no longer projected to `data/current.json`.
- Revalidated the cross-language E2E contracts and release-lock gates without
  launching the full Python parity suite.

## Repositories touched

- `nirs4all-cockpit`
  - Commit `c216460` (`fix(dashboard): keep bundles out of public snapshot`)
  - Previous related commit `4cd2248` (`fix(dashboard): hide bundle and channel badges`)
- `nirs4all-studio`
  - Commit `0f4ec85` (`fix(ci): satisfy release pin import ordering`)
  - Follow-up to the `nirs4all` `0.10.3` runtime pin.

## Files modified

In `nirs4all-cockpit`:

- `cockpit/model.py`
- `cockpit/reconcile.py`
- `data/current.json`
- `tests/test_targets_topology.py`
- `web/app.js`
- `web/index.html`
- `web/style.css`

In `nirs4all-studio`:

- `tests/test_nirs4all_release_pin.py`
- `recommended-config.json`
- `.github/workflows/release-unified.yml`

## Validation

Cockpit local:

- `.venv/bin/python -m pytest -q` -> 141 passed.
- `.venv/bin/python -m ruff check cockpit tests` -> OK.
- `.venv/bin/python -m cockpit.cli validate-targets ops/targets.yaml` -> OK, 22 packages, 102 targets.
- `python3 scripts/smoke_dashboard_dom.py` -> OK via google-chrome.
- Offline reconcile shape check -> `release_bundles` absent, 22 packages.

Cockpit GitHub:

- `ci` on `c216460` -> success.
- `pages` on `c216460` -> success.
- `version-guard` on `c216460` -> success.
- Public checks: `https://cockpit.nirs4all.org/` contains no
  `release-bundles-block` / `pkg-channel`; public `data/current.json` contains
  no `release_bundles`.

Studio GitHub:

- `CI` on `0f4ec85` -> success.
- `Playwright E2E Tests` on `0f4ec85` -> success, 63 passed.
- `version-guard` on `0f4ec85` -> success.

Ecosystem gates:

- `python3 scripts/n4a_e2e_scenarios.py validate` -> 11 scenarios OK.
- `python3 scripts/n4a_e2e_scenarios.py coverage --require-full-strict` ->
  11/11 ready, strictness gaps 0.
- `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
  -> 11/11 scenarios verified, 71 artifacts, failures 0.
- `python3 scripts/n4a_release_surface_matrix.py validate` -> OK.
- `python3 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  -> OK.
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable`
  -> 7/7 member commits fetchable.
- `python3 scripts/n4a_cutover_gates.py --workspace-root /home/delete/nirs4all validate`
  -> manifest and readiness matrix OK.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py tests/test_release_surface_matrix.py tests/test_gitmodules_topology.py tests/test_cutover_state_gate.py tests/test_release_lock.py`
  -> 163 passed.

## Decisions

- Do not expose release bundle cards or channel capsules in cockpit; keep the
  dashboard to the current matrix/status surface.
- Keep bundle metadata in `ops/targets.yaml` because it is useful coordination
  state, but do not publish it in `data/current.json`.
- Do not run full Python parity in this wave; this pass touched dashboard/schema
  presentation and contract gates, not numerical implementation.

## Remaining risks / blockers

- CRAN submissions/resubmissions remain external/manual for `n4m`, `pls4all`,
  `nirs4allio`, `nirs4alldatasets`, and aggregate `nirs4all`.
- Studio Windows RC install/portable smoke remains a manual Windows-side gate.
- Search Console credentials are still absent from the public cockpit collect
  environment.
- Sentry still reports unresolved Studio issues; they remain a production-hold
  monitoring item.
