# Wave 6R - Release Cockpit Audit

Date: 2026-07-06

## Scope

- Repos: `nirs4all-cockpit`, `nirs4all-ecosystem`, release matrix
- Mode: read-only audit

## Snapshot

The audited cockpit snapshot was generated at `2026-07-06T11:53:18Z` and reported:

- `green = 80`
- `stale = 5`
- `missing = 14`
- `excluded = 1`

## Main Blockers

- `nirs4all-core`: GitHub release/crates/npm OK at `0.2.5`; PyPI `nirs4all-core` is still missing
  because the release workflow hits `invalid-publisher`. R-universe is stale.
- `nirs4all-providers`: GitHub release and Pages OK; PyPI missing with `invalid-publisher`.
- `nirs4all-tools`: GitHub release assets exist; PyPI missing with `invalid-publisher`.
- `nirs4all-benchmarks`: GitHub release/Pages/RTD OK; PyPI missing with `invalid-publisher`.
- `nirs4all-repository`: GitHub release/Pages/RTD OK; PyPI missing with `invalid-publisher`.
- `dag-ml` and `dag-ml-data`: some planned PyPI/npm/R surfaces are absent by design; cockpit
  may be stale if the active checkout does not include the latest tags.
- `nirs4all-methods`: PyPI/npm OK at `1.0.5`; R-universe/CRAN are stale or absent.

## Cascade Debt

- `nirs4all-web/studio-lite/package-lock.json` still needs to match vendored `nirs4all=0.2.5` and
  `nirs4all-ui=0.1.4`.
- `nirs4all-studio/package-lock.json` still needs to match local `nirs4all-ui=0.1.4`.
- `nirs4all-providers` extras should align with the current release train:
  - `nirs4all-repository>=0.1.6`
  - `nirs4all-benchmarks>=0.1.4`
  - `nirs4all-papers>=0.2.3`
  - `nirs4all-io>=0.1.6`
- The release lock should be checked with the isolated checkout-members workflow before changing
  protected lock files.

## Validation Commands Recommended

- `n4a-cockpit validate-targets ops/targets.yaml`
- `n4a-cockpit summarize data/current.json`
- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_e2e_scenarios.py`

## Decision

Keep PyPI/publisher blockers visible rather than treating GitHub release assets as full publication.
Fix local cascade lockfiles and extras first; publisher claims still require external registry
configuration.
