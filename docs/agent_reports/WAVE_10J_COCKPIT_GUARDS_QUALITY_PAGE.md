# Wave 10J - Cockpit quality page and version guards

## Scope

- Fixed the cockpit dashboard page roster so `nirs4all-quality` / `quali.nirs4all.org`
  is rendered wherever Pages/GoatCounter ecosystem pages are listed.
- Strengthened the cockpit test from a hardcoded subset to parity between
  `ops/targets.yaml` Pages targets, the canonical Pages URL registry, and the
  dashboard JS roster.
- Refreshed cockpit README/ROADMAP deployment notes to match the actual daily
  collect workflow, shallow sibling checkouts, plain-git snapshot commits, and
  Pages `workflow_run` deployment trigger.
- Added missing `version-guard.yml` workflows to `nirs4all-providers`,
  `nirs4all-tools`, and `nirs4all-ui`.
- Repinned ecosystem gitlinks for `nirs4all-cockpit`, `nirs4all-providers`,
  `nirs4all-tools`, and `nirs4all-ui` to the pushed heads.

## Files Modified

- `nirs4all-cockpit`: `web/app.js`, `tests/test_targets_topology.py`,
  `README.md`, `ROADMAP.md`.
- `nirs4all-providers`: `.github/workflows/version-guard.yml`.
- `nirs4all-tools`: `.github/workflows/version-guard.yml`.
- `nirs4all-ui`: `.github/workflows/version-guard.yml`.
- `nirs4all-ecosystem`: gitlinks for the four repos above and this report.

## Tests Run

- `nirs4all-cockpit`: `n4a-cockpit validate-targets ops/targets.yaml`,
  `pytest -q`, `python3 scripts/smoke_dashboard_dom.py`, `git diff --check`.
- `nirs4all-providers`: local version/tag comparison for `0.2.9 <= v0.2.9`,
  `git diff --check`; GitHub `Providers CI`, `Pages`, and `version-guard` passed.
- `nirs4all-tools`: local version/tag comparison for `0.0.5 <= v0.0.5`,
  `git diff --check`; GitHub `CI` and `version-guard` passed.
- `nirs4all-ui`: local version/tag comparison for `0.1.8 <= v0.1.8`,
  `git diff --check`; GitHub `CI`, `GitHub Pages`, and `version-guard` passed.
- `nirs4all-ui` pre-existing package validation also passed in this wave:
  Node 24 via `nvm`, `npm run ci`, `npm run site:build`.

## Decisions

- The new guards intentionally fail only when the manifest/package version is
  ahead of the latest `v*` tag. Tag-ahead and equal-tag states remain allowed.
- No package version bump or release tag was created for CI/docs-only guard
  changes.
- `nirs4all-quality` uses the explicit GoatCounter path `/quality` and the
  public URL `https://quali.nirs4all.org/`.

## Risks

- `nirs4all-quality` had no observed GoatCounter page in the last committed
  snapshot, so the cockpit will render it as a zero-count page until traffic is
  reported.
- The live cockpit collect command hung once locally during this wave; the
  previous committed snapshot remains valid, and offline cockpit tests/smoke
  passed. A future public cron run should refresh `data/current.json`.
