# Wave 5T - Cockpit rollup and parallel agent audits

Date: 2026-07-04

## Parallel Audits Integrated

### UI / Web / Studio (`Halley`)

- `nirs4all-web` really consumes `nirs4all-ui` through `studio-lite/vendor/nirs4all-ui` and imports shared UI/runtime helpers.
- `nirs4all-studio` depends on `nirs4all-ui`, but production code currently consumes only bridge helpers (`score`, `runtime` view models), not the reusable component set.
- Studio must therefore stay out of prod release as planned; component migration remains real work before claiming Studio/Web full UI unification.

### Core / Lite / Providers / Cockpit (`Plato`)

- `nirs4all-core` release artifacts and non-PyPI publications are present, but PyPI is blocked by missing Trusted Publisher setup.
- `nirs4all-lite` remains a legacy checkout and PyPI alias still stale until `nirs4all-core` is published on PyPI.
- `nirs4all-providers` GitHub release/site are present, but PyPI is blocked by the same Trusted Publisher class of error.
- Cockpit had a semantic defect: package rollup could stay `green` while a tracked PyPI target was `missing`.

## Cockpit Fixes Pushed

Repository: `nirs4all-cockpit`

- `482cf48 fix(status): roll up worst tracked target`
  - Aligns Python rollup with dashboard rank: `broken > missing > stale > pending > unknown > green`.
  - Adds regression tests for `green + missing -> missing`, `green + pending -> pending`, `stale`/`broken` precedence, and excluded-only behavior.
  - Updates README rollup documentation to include `pending`.
- `9046fcc chore(actions): close resolved manual release tasks`
  - Marks already auto-resolved manual actions as `done`: npm automation token, `pls4all` PyPI publisher, `nirs4all-io` PyPI publisher, R-universe core rebuild, crates verified email.
  - Keeps true PyPI Trusted Publisher blockers open.
- `5660e0a chore(collect): refresh data/current.json`
  - Regenerates `data/current.json` after the rollup fix.

## Verification

- `nirs4all-cockpit`: `.venv/bin/pytest -q` (`101 passed`)
- `nirs4all-cockpit`: `.venv/bin/pytest -q tests/test_reconcile.py tests/test_targets_topology.py tests/test_stats.py` (`37 passed`)
- `nirs4all-cockpit`: `.venv/bin/ruff check .`
- `nirs4all-cockpit`: `n4a-cockpit validate-targets ops/targets.yaml`
- `nirs4all-cockpit`: `collect` workflow success (`28710379777`)
- `nirs4all-cockpit`: `pages` workflow success after rerun (`28710461036`)

## Current Cockpit Interpretation

The target summary is still target-level:

- `green=82`
- `stale=3`
- `pending=5`
- `missing=10`
- `broken=0`
- `unknown=0`

Package rollups now expose blockers instead of hiding them:

- `pending`: `nirs4all-methods`, `nirs4all-formats`, `nirs4all-io`
- `stale`: `nirs4all-datasets`
- `missing`: `nirs4all-providers`, `nirs4all-tools`, `nirs4all-core`, `dag-ml`, `dag-ml-data`, `nirs4all-benchmarks`, `nirs4all-repository`

## Remaining External Blockers

- PyPI Trusted Publishers still need to be created for `nirs4all-core`, `nirs4all-providers`, `nirs4all-tools`, `nirs4all-benchmarks`, and `nirs4all-repository`.
- `nirs4all-lite` final alias publication should wait until `nirs4all-core` exists on PyPI.
- `nirs4alldatasets` R-universe is still stale on the public API; local fixes are pushed but external rebuild/sync has not caught up.

## Decisions

- Do not claim full Studio/Web UI convergence yet: Web is using `nirs4all-ui`; Studio is only partially bridged.
- Do not run full parity for this batch; changes were cockpit/E2E contract hardening, not runtime implementation.
