# Wave 6D — release/cockpit/e2e status

Generated: 2026-07-06T08:28:51Z

## Scope

This report consolidates the post-reset, post-release state for the V1 refactor
wave after the non-prod release batch. The full Python `nirs4all` package and
`nirs4all-studio` production line remain intentionally outside the release
switch, except for test/RC artifacts handled separately.

## Released or refreshed

- `nirs4all-providers` `v0.2.4`
  - GitHub Release: published.
  - Pages/CI: green.
  - PyPI: blocked by Trusted Publisher `invalid-publisher`; package remains
    missing from PyPI.
- `nirs4all-datasets` `v0.3.4`
  - GitHub Release and release workflows: green.
  - Python, npm/WASM, crates, R, MATLAB/source, CI, ABI, Pages: green.
  - Cockpit still sees R-universe at `0.3.3` and CRAN at `0.2.0`; this is a
    registry propagation/upstream CRAN lag, not a local release failure.
- `nirs4all-cluster` `v0.1.3`
  - PyPI/ReadTheDocs: green.
  - GitGuardian alert reviewed: current HEAD contains token-shape guards and no
    live credential in the audited code path.
- `nirs4all-repository` `v0.1.5`
  - `v0.1.4` was superseded immediately after catalog index drift.
  - GitHub Release, CI, docs, Pages, CodeQL: green.
  - PyPI: blocked by Trusted Publisher `invalid-publisher`; package remains
    missing from PyPI.
- `nirs4all-cockpit` `v0.1.6`
  - Release tag pushed.
  - Manual collect run `28777846523`: green.
  - Pages run `28778039420`: green.
  - Local validation: `n4a-cockpit validate-targets` green with 21 packages and
    100 targets.
- `nirs4all-ui` `v0.1.3`
  - GitHub Release, npm, CI, Pages: green.
  - Showcase page expanded for reusable component inspection.
- `nirs4all-web` `v0.1.3`
  - GitHub Release, web CI, version guard, Pages: green after rerun.
  - Still client-side only; `node_modules` are build/development dependencies,
    not a deployed backend.
- `nirs4all-org` `v1.0.2`
  - GitHub Release and Pages: green.
  - Public version badges/descriptions refreshed for the release wave.
- `nirs4all-core` `v0.2.4`
  - Repository `nirs4all-core` is the canonical portable aggregate.
  - Rust crate `nirs4all`, npm package `nirs4all`, R-universe package
    `nirs4all`, MATLAB/source, GitHub Release, CI: green.
  - Python distribution `nirs4all-core`: blocked by PyPI Trusted Publisher /
    project registration. `pip index versions nirs4all-core` returns no
    matching distribution.
- `nirs4all-tools` `v0.0.2`
  - GitHub Release and CI: green.
  - PyPI: missing; workflow uses Trusted Publishing and publish attempts require
    PyPI-side authorization.
- `nirs4all-benchmarks` `v0.1.3`
  - GitHub Release, CI, Pages, ReadTheDocs: green.
  - PyPI: missing; workflow uses Trusted Publishing and publish attempts require
    PyPI-side authorization.

## Cockpit snapshot

`n4a-cockpit summarize` after the 2026-07-06 collect:

- green: 81
- stale: 3
- pending: 5
- missing: 10
- broken: 0
- unknown: 1

Important non-green items are not hidden:

- PyPI Trusted Publisher missing/unauthorized for `nirs4all-core`,
  `nirs4all-providers`, `nirs4all-repository`, `nirs4all-tools`, and
  `nirs4all-benchmarks`.
- CRAN entries remain pending for packages that are intentionally not CRAN-ready
  or awaiting registry publication.
- `dag-ml` and `dag-ml-data` Python/npm targets remain planned, not published.
- `nirs4all-datasets` R-universe/CRAN lag remains visible.

## Cross-language e2e state

The ecosystem now contains 10 complex cross-language scenarios in
`scripts/n4a_e2e_scenarios.py` and `docs/CROSS_LANGUAGE_E2E.md`.

Validation run:

- `python3 scripts/n4a_e2e_scenarios.py coverage --json`
  - scenario count: 10
  - ready: 10
  - blocked: 0
  - languages covered: Python, R, JavaScript/WASM, web, native, Rust
  - repos covered include `nirs4all`, `nirs4all-core`, `nirs4all-web`,
    `nirs4all-ui`, `nirs4all-datasets`, `nirs4all-io`,
    `nirs4all-repository`, `nirs4all-providers`, `nirs4all-methods`,
    `dag-ml`, `dag-ml-data`, `nirs4all-tools`, `nirs4all-papers`, and
    `nirs4all-cluster`.

Prior verification after scenario implementation:

- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 -m pytest -q tests/test_e2e_scenarios.py` => 68 passed
- `python3 -m pytest -q` => 92 passed
- `python3 -m ruff check scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py`

The scenario meter is ready, not a full execution gate yet. A fresh local
`evidence` invocation against an empty artifacts directory correctly failed
because it verifies required post-run artifacts; it does not generate them.

## Decisions

- Keep `nirs4all` Python and `nirs4all-studio` production untouched for now.
- Treat `nirs4all-core` as canonical and `nirs4all-lite` as a legacy
  compatibility/redirect surface only.
- Do not remove missing PyPI targets from the cockpit to obtain artificial
  green status.
- Do not mark e2e evidence as complete until the actual scenario artifacts are
  generated and verified.

## Remaining blockers

1. Configure PyPI Trusted Publishers, or provide a PyPI API token, for the
   missing Python distributions:
   - `nirs4all-core`
   - `nirs4all-providers`
   - `nirs4all-repository`
   - `nirs4all-tools`
   - `nirs4all-benchmarks`
2. Run the heavy full parity/e2e evidence batch after the current release batch
   is accepted as the correct target state.
3. Keep the cockpit showing missing/stale entries until the corresponding
   registry state is genuinely fixed.
