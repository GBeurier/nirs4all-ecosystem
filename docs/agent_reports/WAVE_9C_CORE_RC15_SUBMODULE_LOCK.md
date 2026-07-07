# Wave 9C - Core RC15 submodule and release-lock repin

Date: 2026-07-08
Owner: Codex

## Scope

Fix the `nirs4all-ecosystem` cross-language E2E CI failure introduced by the
custom app host strict Python rerun ledger. The CI public checkout used the
`nirs4all-core` submodule at `v0.3.0`, which did not contain
`scripts/e2e/run_custom_app_host.py`.

## Files changed

- `nirs4all-core` submodule: `d830879` -> `3ff5bb2`
- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `tests/test_release_lock.py`
- `docs/agent_reports/WAVE_9C_CORE_RC15_SUBMODULE_LOCK.md`

## Decisions

- Created and pushed annotated tag `n4a-v1-rc15-2026.07-refactor` on
  `nirs4all-core@3ff5bb21a23852f708665d9089f33d47b33f5dbf`.
- Updated the core release selection from `v0.3.0` to
  `n4a-v1-rc15-2026.07-refactor`.
- Regenerated the aggregation lock for the new core selection.
- Kept unrelated dirty `nirs4all-io` work out of the lock; it belongs to a
  separate in-progress lane and must not become release evidence here.
- No legacy alias was added or preserved for this fix.

## Tests run

- `N4A_WORKSPACE_ROOT=/home/delete/nirs4all/nirs4all-ecosystem PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py`
  - `125 passed`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_submodule_repin_plan.py tests/test_gitmodules_topology.py`
  - `27 passed`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
  - `OK: 11 cross-language E2E scenarios`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage`
  - `11/11 scenarios; ready=11 blocked=0`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q`
  - `157 passed`
- `python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable --output-json /tmp/n4a-release-fetchability.json`
  - `fetchability: 7/7 member commits checked out (0 unfetchable)`

## Risks

- `nirs4all-io` has unrelated dirty local work in the parent workspace. The
  generated lock initially observed it, then the lock was kept on the previous
  clean `io` state intentionally.
- Full parity was not rerun in this slice; this is a release-lock/submodule
  integration fix after the custom host parity evidence was already generated.
