# Wave 8O - Cockpit RC14 Final Refresh And UI Quality Boundary

Date: 2026-07-07

## Scope

- Refreshed `nirs4all-cockpit` after the RC14 prerelease/filter fixes so the
  public dashboard points at the latest selected non-production heads.
- Kept `nirs4all` Python and `nirs4all-studio` outside the release push.
- Rechecked the `nirs4all-ui`/`nirs4all-quality` boundary before any further UI
  edits.

## Integrated Heads

- `nirs4all-cockpit`: `be1d4488d32896b1a631e719bfd0354d5d730dd2`
- `nirs4all-core`: cockpit source commit refreshed to
  `e31a24825fd369810e2b66f6425df457cb38e8d6`
- `nirs4all-providers`: cockpit source commit refreshed to
  `bb85204b00f572e0254bd0b5acbc528dab262b1c`
- `nirs4all-ecosystem`: cockpit source commit refreshed to
  `a55db3b346b92f6aab3c7f8618d01ad1ba6d5e21`

## Files Modified

- `nirs4all-cockpit/data/current.json`
- `nirs4all-cockpit/data/manual-actions.json`
- `nirs4all-cockpit/ops/targets.yaml`
- `nirs4all-ecosystem/nirs4all-cockpit` submodule pointer
- `nirs4all-ecosystem/docs/RELEASE_DISTRIBUTION_MATRIX.md`
- `nirs4all-ecosystem/docs/agent_reports/WAVE_8O_COCKPIT_RC14_FINAL_REFRESH_AND_UI_QUALITY_BOUNDARY.md`

## Decisions

- Corrected the cockpit core `coordination_tag` from the non-existent
  `n4a-v1-rc16-2026.07-refactor` to the published RC14 prerelease tag.
- Treated RC14 as a coordination prerelease, while keeping the stable package
  publication facts (`nirs4all-core` 0.2.13, `nirs4all-providers` 0.2.7,
  `nirs4all-ui` 0.1.6) as the registry truth.
- Preserved the visible PyPI/CRAN blockers instead of converting them into
  artificial green states.
- Did not touch the `nirs4all-ui` paths currently consumed by `nirs4all-quality`:
  `src/lab/**`, `assets/theme.css`, and `assets/brand/{nirs4all,quali}/**`.

## Tests

`nirs4all-cockpit`:

- `ruff check .`
- `pytest -q` (`119 passed`)
- `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
- `python3.11 -m cockpit.cli summarize data/current.json`
- `python3.11 -m cockpit.cli admin actions --json-out /tmp/n4a-manual-actions-check.json`
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH node --check web/app.js`
- `python3.11 scripts/smoke_dashboard_dom.py`
- `git diff --check`

`nirs4all-ecosystem`:

- `python3.11 scripts/n4a_release_surface_matrix.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable`
- `git diff --check`

## Review Notes

- The cockpit now shows `nirs4all-providers` `publish.yml` as the RC14
  prerelease skip, not the stale July 4 failure.
- The cockpit now shows the core release workflows: Python publish still failed
  on the real PyPI Trusted Publisher blocker; crates, npm, and R release
  workflows succeeded.
- `nirs4all-ui@0.1.6` remains a published visual-system surface, but
  `nirs4all-quality` still depends on local, unpublished UI files. The next UI
  integration should publish or explicitly migrate `lab`, `theme.css`, and the
  `quali` brand assets as a stable contract before switching quality to a
  package dependency.

## Remaining Risks

- PyPI Trusted Publisher setup is still required for `nirs4all-core`,
  `nirs4all-providers`, and the other missing PyPI targets listed in the
  cockpit.
- CRAN targets remain manual/pending.
- The `nirs4all-ui` quality-facing surface is not yet reproducible from the
  published package.
- Full Python-reference parity was intentionally not rerun in this wave.
