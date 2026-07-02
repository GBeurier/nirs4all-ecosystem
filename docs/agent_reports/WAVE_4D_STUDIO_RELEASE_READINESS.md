# Wave 4D - Studio shared UI adoption and release readiness refresh

Date: 2026-07-02  
Coordinator: Codex

## Scope

Follow-up to Wave 4C and the Claude release/naming audit. No full Python parity
rerun in this small batch.

## Published code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all-studio` | `rc/v1-full-refactor` | `8141e2eddb2d` / `n4a-v1-rc1-2026.07-refactor` | `src/components/runtime/RuntimeEngineBadge.tsx` |
| `nirs4all-ecosystem` | `rc/v1-full-refactor` | this report commit | `docs/contracts/cutover/readiness-matrix.n4a.json`, this report |

Studio change:

- `RuntimeEngineBadge` now imports `RuntimeEngineBadge` from
  `nirs4all-ui/components` and supplies the Studio-specific status view,
  icon, classes, and title.
- This closes the concrete adoption gap where Studio consumed shared
  `score`/`runtime` helpers but kept a fully local runtime badge component.

Release readiness change:

- `LOCK-REL-001` in `docs/contracts/cutover/readiness-matrix.n4a.json` moved
  from `blocked` to `ready`.
- The previous missing-contract text said 6/7 selected members were not
  fetchable. That was stale after RC publication.

## Tests and gates

Studio:

- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm run test:frontend -- src/components/runtime/RuntimeComponents.test.tsx` -> `3 passed`.
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm run lint:tsc` -> clean.
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npx eslint src/components/runtime/RuntimeEngineBadge.tsx` -> clean.

Ecosystem:

- `python3 -m json.tool docs/contracts/cutover/readiness-matrix.n4a.json` -> valid JSON.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all` -> manifest and readiness matrix OK.
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> valid.
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable` -> `7/7 member commits checked out`.
- `python3 -m pytest tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -q` -> `20 passed`.

## Release/naming audit outcome

Claude read-only release audit confirmed:

- `RC-v1-nirs4all-core` is the renamed `nirs4all-lite` aggregate worktree, not
  the Python modelling library.
- `RC-v1-nirs4all-python` is the Python `nirs4all` library and remains the
  reference oracle.
- No hard PyPI naming collision exists: Python library keeps `nirs4all`; the
  aggregate uses `nirs4all-core` for PyPI and `nirs4all` on non-Python package
  surfaces.
- The release lock is fetchable when checked against peeled tag/commit refs.
- `nirs4all-ui` remains the main release-surface gap: it exists, is pushed, and
  is consumed by Studio/Web, but it is not yet in the release surface matrix,
  aggregation lock, cockpit, or org site.

The audit also flagged these remaining non-code release tasks:

- Decide whether `n4a-v1-rc1-*` tags are merely RC markers or should trigger
  package publication workflows. Current workflows do not uniformly publish from
  that tag pattern.
- Bump package versions to a coherent RC scheme before actual registry
  publication.
- Reconcile public org/cockpit wording for `nirs4all-core` vs
  production-current `nirs4all-lite`.
- Decide whether MATLAB/Octave is required for this RC or should be marked
  non-required until it is tracked in cockpit/org.
- Align the R aggregate license metadata before R publication.

## Remaining gaps

- Full Python parity should be rerun only after the next large integration
  batch.
- `nirs4all-ui` still needs a release decision: either add it to matrix/lock/
  cockpit/org as a package surface, or explicitly mark it out of the RC.
- Web client-only proof still needs the hardening noted in Wave 4C for remote
  `<link>` and font/preconnect resources.
