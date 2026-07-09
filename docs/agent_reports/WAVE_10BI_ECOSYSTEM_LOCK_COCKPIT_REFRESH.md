# Wave 10BI - Ecosystem Lock and Cockpit Refresh

Date: 2026-07-09

## Scope

Integrated the post-actions public topology batch in `nirs4all-ecosystem` and
kept the cockpit surface aligned with the user's request to remove release
channel additions.

## Files Changed

- `dag-ml`, `dag-ml-data`, `nirs4all-aom`, `nirs4all-benchmarks`,
  `nirs4all-cluster`, `nirs4all-cockpit`, `nirs4all-core`,
  `nirs4all-datasets`, `nirs4all-formats`, `nirs4all-io`,
  `nirs4all-methods`, `nirs4all-org`, `nirs4all-papers`,
  `nirs4all-providers`, `nirs4all-repository`, `nirs4all-studio`,
  `nirs4all-tools`, `nirs4all-ui`, `nirs4all-web`: gitlinks advanced to the
  current public `main` heads.
- `docs/contracts/release/aggregation-lock.n4a.lock.json`: regenerated against
  the current 7-member core train workspace.
- `tests/test_gitmodules_topology.py`: added the already-tracked
  `nirs4all-device` public Pages surface to the topology contract.

## Decisions

- `nirs4all` Python was intentionally not bumped. A mechanical
  `git submodule update --remote` would have rewound the gitlink from the
  selected refactor head to `main`; that would lose current parity/refactor
  evidence from the parent topology.
- `nirs4all-studio` was bumped only as a gitlink to the current public `main`
  head. This does not publish or switch the held production Studio app.
- The cockpit cleanup is kept in the current surface: no `Release bundles`
  panel and no visible channel capsules for `rc` / `production held`.
- The release lock now validates on the live workspace. Its updated member
  heads are post-tag commits, so `exact_tag` is `null` for those entries until
  the next publication/tag batch.

## Validation

- `nirs4all-core`: GitHub `CI` and `version-guard` passed on
  `5f207202124725d749cf3f2a013b57caaa1d0b20`.
- `nirs4all-cockpit`: GitHub `collect` passed on `7a07d6d`, produced
  `68e339b chore(collect): refresh data/current.json`, and `pages` passed on
  `68e339b`.
- `python3 scripts/n4a_release_surface_matrix.py validate` -> OK.
- `python3 scripts/n4a_e2e_scenarios.py validate` -> 11 scenarios OK.
- `python3 scripts/n4a_e2e_scenarios.py coverage --json` -> 11/11 ready,
  full strict coverage.
- `python3 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  -> OK.
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable`
  -> 7/7 fetchable.
- `python3 scripts/n4a_cutover_gates.py validate` -> OK.
- `python3 scripts/n4a_cutover_gates.py readiness --json` -> readiness
  contract loads and reports the current gate matrix.
- `python3 -m pytest -q tests/test_gitmodules_topology.py tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_e2e_scenarios.py tests/test_cutover_state_gate.py tests/test_quality_custom_host_smoke.py tests/test_submodule_repin_plan.py`
  -> 171 passed.

## Parallel Review Notes

- Cockpit read-only review confirmed that `Release bundles` is no longer
  present in code or generated data, visible channel capsules are gone, and the
  manual blockers section remains at the bottom of the page.
- Ecosystem read-only review flagged the `nirs4all` rewind risk; that gitlink
  was excluded from this bump.

## Remaining Risks

- Runtime E2E evidence freshness was not regenerated in this wave:
  `evidence-ledger --check --max-age-seconds 14400` reports the tracked ledger
  stale. This is expected to be rerun after the larger selected-head batch, not
  during this topology/cockpit update.
- Full Python parity was not launched in this wave.
- The post-tag lock heads need a follow-up publication/tag batch if the goal is
  to make every locked member an exact tagged release candidate again.
