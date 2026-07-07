# Wave 7AL - Core lock naming

Date: 2026-07-07
Agent: Codex
Lane: release-lock / topology / core naming

## Scope

Normalize the active release-lock vocabulary from `lite` to `core` now that
`nirs4all-core` is the canonical aggregate repo. This wave still recorded the
then-open compatibility-alias question; later waves 7AV/7AW superseded that
decision and removed any public `nirs4all-lite` alias from the V1 RC target.

No files in `nirs4all-ui` or `nirs4all-quality` were modified.

## Files modified

- `README.md`
- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/contracts/release/public-v1-surface-matrix.n4a.json`
- `docs/contracts/cutover/drop-gates.n4a.json`
- `docs/contracts/cutover/readiness-matrix.n4a.json`
- `tests/test_release_lock.py`
- `tests/test_cutover_state_gate.py`
- `tests/test_release_surface_matrix.py`

## Decisions

- Renamed the aggregation member key from `lite` to `core`.
- Renamed the V1 aggregate cutover gate from `lite_v1_surfaces` to
  `core_v1_surfaces`.
- Renamed the readiness blocker from `LITE-V1-SURFACE-001` to
  `CORE-V1-SURFACE-001`.
- At the time of this wave, `nirs4all-lite` was still present in
  `repo_aliases`, `legacy_distribution`, and topology evidence while the
  cutover policy was being decided. This was superseded by the no-legacy-alias
  lock: the current V1 RC topology does not keep a public `nirs4all-lite`
  release alias.
- Did not regenerate the whole lock from dirty/current local worktrees; only the
  manifest digest, member key, and derived gate names were changed.

## Tests run

- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_cutover_gates.py validate --gate core_v1_surfaces`
- `python3 -m pytest -q tests/test_release_lock.py tests/test_cutover_state_gate.py tests/test_release_surface_matrix.py tests/test_gitmodules_topology.py`
  - Result: `25 passed`
- JSON syntax validation for the modified contract files with `python3 -m json.tool`
- `git diff --check`
- Clean selected-member lock validation:
  - `python3 scripts/n4a_release_lock.py checkout-members --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output /tmp/n4a-lock-selected-core-1783401972`
  - `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-selected-core-1783401972 validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - Result: validated `docs/contracts/release/aggregation-lock.n4a.lock.json`

## Risks and follow-ups

- Direct validation against `../_worktrees` currently fails because the selected
  live worktrees are not a clean representation of the lock. In particular,
  `RC-v1-dmd` is dirty and some local worktrees have advanced beyond the pinned
  lock commits. Use clean selected-member checkout validation until the next
  intentional repin.
- `studio-lite` paths in web e2e contracts are product-internal names and were
  not changed by this release-lock naming pass.
