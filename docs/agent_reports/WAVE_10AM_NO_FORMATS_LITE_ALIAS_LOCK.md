# WAVE 10AM - no formats lite alias in release lock

Date: 2026-07-09

## Scope

Remove the remaining active release-contract reference to the legacy
`nirs4allformatslite` R package alias.

## Files changed

- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`

## Decision

The V1 release policy keeps historical `nirs4all-lite` references only in
audit/history documents and does not maintain public legacy aliases. The
formats release manifest still declared both `nirs4allformats` and
`nirs4allformatslite` under the R surface. The legacy lite alias was removed,
and the aggregation lock was regenerated against the selected lock checkout to
avoid accidentally advancing member commits from the live sibling workspace.

## Validation

- `nirs4all-ecosystem`: `python3.11 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-release-lock-selected generate --manifest docs/contracts/release/aggregation-manifest.n4a.json --output docs/contracts/release/aggregation-lock.n4a.lock.json` -> lock regenerated.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-release-lock-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> passed.
- `nirs4all-ecosystem`: `python3.11 -m pytest -q tests/test_release_surface_matrix.py tests/test_release_lock.py tests/test_submodule_repin_plan.py` -> 25 passed.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_release_surface_matrix.py validate` -> passed.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py validate && python3.11 scripts/n4a_e2e_scenarios.py coverage` -> `11/11 scenarios; ready=11 blocked=0`.

## Risks

- Historical reports still mention old lite decisions by design; the active
  release contracts and cockpit snapshot no longer carry this alias.
