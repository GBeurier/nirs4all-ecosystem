# Wave 8H - Cockpit Release Status

Date: 2026-07-07

## Scope

- Repository: `nirs4all-cockpit`
- Commit: `c11e0ad` (`chore(snapshot): refresh web and ui heads`)
- Files changed:
  - `data/current.json`
- Ecosystem integration:
  - `nirs4all-cockpit` submodule advanced from `666dedf` to `c11e0ad`
  - `docs/RELEASE_DISTRIBUTION_MATRIX.md` now points at this newer audit

## Decision

Refreshed the public cockpit snapshot for the two release heads that changed
after the previous collect:

- `nirs4all-web`: `da8a3de`
- `nirs4all-ui`: `5ce32e1`

The refresh keeps the real registry state visible. It does not mark PyPI,
CRAN, or R-universe targets green when the public registries still report
missing, pending, or stale artifacts.

## Current Publication State

Confirmed green/public:

- `nirs4all-web`: GitHub Pages deployed from `da8a3de`
- `nirs4all-ui`: npm `0.1.4`, GitHub release `0.1.4`, GitHub Pages green
- `nirs4all-core`: crates.io `nirs4all` `0.2.13`, npm `nirs4all` `0.2.13`,
  R-universe `nirs4all` `0.2.13`, GitHub release `0.2.13`, ReadTheDocs green
- `dag-ml` and `dag-ml-data`: crates/npm releases `0.2.5`, latest CI green

Still blocked or intentionally visible:

- `nirs4all-core`, `nirs4all-providers`, `nirs4all-tools`, `dag-ml`,
  `dag-ml-data`: PyPI publication jobs fail with `invalid-publisher`; PyPI
  Trusted Publisher configuration must be added for each project/environment.
- `nirs4all-core`, `nirs4all-io`, `nirs4all-methods`: CRAN targets remain
  pending.
- `nirs4all-formats`: R-universe targets remain stale; CRAN is intentionally
  excluded by policy.
- `nirs4all-datasets`: CRAN remains stale until the external CRAN release
  catches up.

## Lock And Topology

The aggregation lock is valid when checked against an isolated selected-member
workspace:

- `n4a_release_lock.py checkout-members` -> OK
- `n4a_release_lock.py --workspace-root /tmp/n4a-lock-selected-wave8g validate`
  -> OK
- `n4a_release_lock.py audit-fetchability --fail-on-unfetchable` -> 7/7
  member commits fetchable

Validation against the live `/home/delete/nirs4all` workspace is expected to
fail while the live sibling checkouts carry post-lock heads and unrelated
work-in-progress. The lock remains the release authority until new member
commits are intentionally selected and regenerated.

## Tests

Executed locally:

- `nirs4all-cockpit`: `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
  -> OK
- `nirs4all-cockpit`: `python3.11 -m cockpit.cli status` -> OK
- `nirs4all-cockpit`: `python3.11 -m pytest -q` -> 117 passed
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_release_surface_matrix.py validate`
  -> OK
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py validate`
  -> OK
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py coverage`
  -> 11/11 ready, 0 blocked

## Risks

- The cockpit is accurate, not all-green. The remaining non-green cells are
  real publication-state signals.
- The Web custom-host proof still uses vendored RC packages inside
  `studio-lite`; published-package external-consumer testing remains a useful
  next hardening step.
