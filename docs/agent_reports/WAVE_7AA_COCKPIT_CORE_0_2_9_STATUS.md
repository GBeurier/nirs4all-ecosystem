# Wave 7AA - Cockpit Core 0.2.9 Status

Date: 2026-07-07

## Scope

Refresh the public cockpit inventory after the `nirs4all-core` `v0.2.9`
release and pin the ecosystem cockpit submodule to the reviewed head.

## Integrated heads

- `nirs4all-cockpit`: `e05c777 docs(targets): clarify core r-universe rebuild state`
- Included upstream cockpit refresh: `6fc7c94 chore(collect): refresh data/current.json`
- Included cockpit status update: `b1964d1 chore(targets): track core 0.2.9 release`

## Files changed

In `nirs4all-cockpit`:

- `data/current.json`
- `ops/targets.yaml`
- `ops/manual-actions.yaml`
- `tests/test_targets_topology.py`

In `nirs4all-ecosystem`:

- `nirs4all-cockpit` submodule pin
- `docs/agent_reports/WAVE_7Z_CORE_0_2_9_RELEASE_AND_WEB_SYNC.md`
- `docs/agent_reports/WAVE_7AA_COCKPIT_CORE_0_2_9_STATUS.md`

## Tests run

In `nirs4all-cockpit`:

- `.venv/bin/python -m pytest -q`
  - 113 passed.
- `.venv/bin/python -m pytest -q tests/test_targets_topology.py`
  - 16 passed after the R-universe wording review.
- `.venv/bin/n4a-cockpit validate-targets ops/targets.yaml`
  - 21 packages, 100 targets.
- `.venv/bin/ruff check .`
  - passed.
- `python3 -m json.tool data/current.json >/dev/null`
  - passed.

## Review

- Claude Code read-only review inspected cockpit target/version alignment.
- It reached the turn limit before a final report, but identified one useful
  wording risk: R-universe could be read as already aligned to `0.2.9`.
  The cockpit target reason now states that R-universe remains dependent on a
  manual rebuild while the public snapshot marks it stale at `0.2.8`.

## Decisions

- Keep PyPI `nirs4all-core` as `missing`: the `release-python` workflow failed
  with `invalid-publisher` on `v0.2.9`, and PyPI still returns 404.
- Mark crates.io, npm, and GitHub Release as published at `0.2.9`.
- Keep R-universe as stale at `0.2.8` until the manual rebuild catches up.
- Preserve the production-held status for `nirs4all` Python and Studio.

## Risks

- PyPI publication requires external Trusted Publisher configuration or an
  alternate token-based publication path.
- R-universe still needs a successful rebuild before the cockpit can mark it
  green for `0.2.9`.
