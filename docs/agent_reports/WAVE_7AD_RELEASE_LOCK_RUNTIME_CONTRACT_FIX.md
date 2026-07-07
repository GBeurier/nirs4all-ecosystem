# WAVE 7AD - Release lock runtime contract fix

Date: 2026-07-07

## Scope

- Repository: `nirs4all-ecosystem`
- Lane: release-lock/topology validation after `nirs4all-core` `v0.2.12`
- Constraint: no changes to `nirs4all-ui` or `nirs4all-quality`

## Files modified

- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/agent_reports/WAVE_7AD_RELEASE_LOCK_RUNTIME_CONTRACT_FIX.md`

## Decision

The `v0.2.12` core topology contract intentionally added the
`runtime_contracts` key to `release_topology_manifest()`. The release lock had
the new core commit and package versions, but still carried the previous
topology artifact hashes. The lock was regenerated from the selected-member
checkout to match the exact CI release-lock validation path.

## Tests run

- `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-release-external-0212 generate --manifest docs/contracts/release/aggregation-manifest.n4a.json --output docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-release-external-0212 validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_e2e_scenarios.py`
- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 scripts/n4a_e2e_scenarios.py coverage`

## Result

- Release lock validation now passes against the hermetic selected-member
  checkout.
- E2E scenario board remains `11/11 ready`, with unchanged strictness debt:
  `strictness_gaps=12`, `v1_contract_phases=13`, `v1_gap_phases=31`.

## Risks

- This does not reduce E2E strictness debt; it only fixes the release-lock gate
  for the newly published runtime contract surface.
