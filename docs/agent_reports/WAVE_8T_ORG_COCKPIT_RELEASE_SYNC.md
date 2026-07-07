# Wave 8T - Org Cockpit Release Sync

Date: 2026-07-07

## Scope

- Kept `nirs4all` Python production and `nirs4all-studio` production held.
- Published only non-held coordination/site/cockpit updates.
- Did not touch `nirs4all-ui` quality-owned paths.
- Treated `/home/delete/nirs4all/_worktrees/nirs4all-ui-assets` as the safe
  UI asset/showcase source while `nirs4all-ui/main` remains dirty for
  quality work.

## Changes

### nirs4all-org

- Published `v1.0.4`.
- Refreshed the public site copy for `nirs4all-tools` from `v0.0.3` to
  `v0.0.4`.
- GitHub Actions on `9dc6119d9fc23b1147af10dbeefa83fedef6c380`:
  `version-guard` passed and Pages deployed.

### nirs4all-cockpit

- Published `v0.1.7` for the code-stat scanner fix.
- Updated the scanner to skip nested Git checkouts, preventing submodule-heavy
  repos from inflating parent repo LOC/test metrics.
- Refreshed cockpit snapshot data for:
  - `nirs4all-ecosystem` at
    `1c0f1f87f8c4fe0ac036a9db8f0acd74d8372090`.
  - `nirs4all-cockpit` release `v0.1.7`.
  - `nirs4all-org` release `v1.0.4`.
- GitHub Actions passed on:
  - `1f4c3b4b94e3ef05d1d976ea87dd7f8e00212109`
    (`ci`, `version-guard`, `pages`).
  - `25468c33836f338a2770659e8dc9d2eda7465cf4`
    (`ci`, `version-guard`, `pages`).
  - `6d35faf50d97a50cdc2e347f4e36373b35fe6759`
    (`ci`, `version-guard`, `pages`).

### nirs4all-ecosystem

- Advanced submodule pins:
  - `nirs4all-org` -> `9dc6119d9fc23b1147af10dbeefa83fedef6c380`.
  - `nirs4all-cockpit` ->
    `6d35faf50d97a50cdc2e347f4e36373b35fe6759`.
- Clarified source documents for the public V1 surface matrix:
  WAVE_8R remains the custom-host/UI asset boundary source, WAVE_8S records
  Studio Windows RC prep, and this report records the Org/Cockpit release sync.

## Validation

- `nirs4all-org`: HTML parser smoke, `package.json` JSON parse, content
  assertions, `git diff --check`.
- `nirs4all-cockpit`: `python3.11 -m cockpit.cli validate-targets
  ops/targets.yaml`, `python3.11 -m pytest -q`, `python3.11 -m ruff check .`,
  `python3.11 scripts/smoke_dashboard_dom.py`.
- `nirs4all-ecosystem`: release surface matrix validation, E2E scenario
  contract validation, targeted pytest, release lock fetchability, and diff
  check.

## Risks

- PyPI/CRAN/R-universe blockers remain external/manual and are tracked in the
  cockpit.
- `nirs4all-ui/main` remains intentionally dirty for `nirs4all-quality`; do not
  publish from it until that work is reconciled.
- Studio Windows native `.exe` artifacts still need to be built and manually
  tested on Windows.
