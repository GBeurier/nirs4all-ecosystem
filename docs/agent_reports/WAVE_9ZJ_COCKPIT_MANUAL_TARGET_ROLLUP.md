# Wave 9ZJ - Cockpit manual-target rollup cleanup

Date: 2026-07-10

## Scope

- Removed the remaining top-level `pending`/`stale` noise caused by human-only CRAN submissions.
- Kept those CRAN targets visible in the cockpit matrix and actionable in the manual-actions block at the bottom.
- Updated the ecosystem submodule pin for `nirs4all-cockpit`.

## Files / repos changed

- `nirs4all-cockpit`
  - Commit: `ff703ab fix(dashboard): keep manual targets out of rollup`
  - Snapshot commit: `4d5a9d2 chore(collect): refresh data/current.json`
  - Added explicit target state `manual`.
  - Marked human-only CRAN targets as manual:
    - `n4m`
    - `pls4all`
    - `nirs4allio`
    - `nirs4alldatasets`
    - `nirs4all`
  - Excluded manual targets from package rollup and summary counts while preserving their probed target status and registry links.
- `nirs4all-ecosystem`
  - Updated `nirs4all-cockpit` submodule to `4d5a9d2`.
  - Added this coordination report.

## Validation

- `nirs4all-cockpit`
  - `.venv/bin/ruff check .`
  - `.venv/bin/python -m pytest -q`: 144 passed.
  - `.venv/bin/python -m cockpit.cli validate-targets ops/targets.yaml`
  - GitHub `ci`: success on `ff703ab`.
  - GitHub `version-guard`: success on `ff703ab`.
  - GitHub `collect`: success, produced `4d5a9d2`.
  - GitHub `pages`: success on `4d5a9d2`.
- Public cockpit check:
  - `summary`: `green=97`, `stale=0`, `pending=0`, `missing=0`, `broken=0`, `unknown=0`, `excluded=1`.
  - `nirs4all-methods`, `nirs4all-io`, `nirs4all-core`, and `nirs4all-datasets` now roll up green.
  - The corresponding CRAN targets remain visible as `manual=true` with their live `pending`/`stale` target statuses.
  - `Release bundles`, `production held`, `held outside`, `bundle.channel`, and `pkg-channel` remain absent.

## Decisions

- Used a first-class inventory state instead of string-matching CRAN reasons.
- Did not hide CRAN state. Manual targets remain in `data/current.json` so the matrix and manual-action board preserve auditability.
- Did not run long full parity gates; this wave is cockpit status/visibility scoped.

## Risks / follow-up

- Manual CRAN submissions are still real human actions. They no longer degrade the main cockpit rollup, but they remain unresolved in the bottom manual-actions board until accepted/published.
