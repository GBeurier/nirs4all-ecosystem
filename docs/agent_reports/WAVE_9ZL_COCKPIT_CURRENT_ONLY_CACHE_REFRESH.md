# Wave 9ZL - Cockpit current-only cache refresh

## Scope

User-facing cockpit cleanup follow-up: make sure the published dashboard serves
the current-only surface without the transient Release bundles panel or channel
capsules.

## Files changed

- `nirs4all-cockpit/web/index.html`
  - bumped `style.css`, `icons.js`, and `app.js` query strings from
    `20260710-current-only` to `20260710-current-only-2` to invalidate any stale
    browser asset cache.
- `nirs4all-ecosystem/nirs4all-cockpit`
  - updated submodule pointer to `984565a`.

## Tests and checks

- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q \
  tests/test_targets_topology.py::test_inventory_has_no_release_bundles_or_display_channels \
  tests/test_targets_topology.py::test_public_snapshot_has_no_channel_display_metadata \
  tests/test_targets_topology.py::test_dashboard_keeps_release_matrix_without_bundle_or_channel_chips`
  - result: `3 passed`
- Public `https://cockpit.nirs4all.org/` now references
  `20260710-current-only-2`.
- Public HTML/JS/CSS/JSON checks found no `Release bundles`, `production held`,
  `pkg-channel`, `release_bundles`, or `channel` display metadata.
- GitHub workflows on `nirs4all-cockpit@984565a`:
  - `ci`: success
  - `version-guard`: success
  - `pages`: success
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/test_gitmodules_topology.py tests/test_release_surface_matrix.py tests/test_release_lock.py`
  - result: `24 passed`
- `python3 scripts/n4a_release_surface_matrix.py validate`
  - result: `validated docs/contracts/release/public-v1-surface-matrix.n4a.json`
- `python3 scripts/n4a_release_lock.py checkout-members ... --output /tmp/n4a-lock-selected.fRkI6P`
  followed by `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-selected.fRkI6P validate ...`
  - result: `validated docs/contracts/release/aggregation-lock.n4a.lock.json`

## Decisions

- No status/data model change was needed. The local and public cockpit surface
  already had the bundle/channel UI removed; this wave only forces fresh assets
  and records the published commit in the ecosystem lock.

## Risks

- Users with a pinned old HTML document may need a hard refresh once; the new
  asset query string prevents stale JS/CSS after the HTML reloads.
- Direct lock validation against `/home/delete/nirs4all` remains unsuitable while
  the live sibling workspace contains non-lock heads; selected-member validation
  is the authoritative gate for this check.
