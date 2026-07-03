# WAVE 4AW - Cascade version bumps and release lock refresh

Date: 2026-07-03

Scope: release cascade after the V1 refactor batch, excluding production-sensitive
`nirs4all` Python and `nirs4all-studio` main. `nirs4all-drafts` and
`nirs4all-lab` were not touched.

## Integrated heads

| Repo | Selected head | Version / tag |
| --- | --- | --- |
| `dag-ml` | `7e9a881d0939` | `0.2.2`, `n4a-v1-2026.07-refactor` |
| `dag-ml-data` | `22157227e2a8` | `0.2.3`, `n4a-v1-2026.07-refactor` |
| `nirs4all-formats` | `181946f141ed` | `0.2.1`, final tag moved from stale head |
| `nirs4all-io` | `4a5bef22c117` | `0.1.5` |
| `nirs4all-datasets` | `c46042dabe29` | `0.3.2` |
| `nirs4all-methods` | `115077ae4551` | `1.0.1`, final tag moved from stale head |
| `nirs4all-core` | `19e69417ad89` | `0.2.2`, canonical aggregate target |
| `nirs4all-web` | `5f7ee6823ae` | vendored `nirs4all-core` WASM shim `0.2.2` |
| `nirs4all-cockpit` | `234b2ed` | public snapshot updated |
| `nirs4all-org` | `05666f5` | public site updated |

Additional final tags were added on the selected RC heads for `nirs4all-tools`,
`nirs4all-ui`, `nirs4all-cluster`, and `nirs4all-papers`.

## Files changed in ecosystem

- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/contracts/release/public-v1-surface-matrix.n4a.json`
- `tests/test_release_lock.py`

## Validation

Ecosystem:

- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees generate ...`
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate ...`
- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all`
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -p no:cacheprovider` -> 22 passed

Sibling gates run during the cascade:

- `nirs4all-core`: `cargo test --workspace`; Python unittest discovery; WASM npm tests with Linux Node; version check.
- `nirs4all-web`: `check:lite-shim`, `typecheck`, 134 Vitest tests, catalog validation, `build`, `build:single`.
- `nirs4all-cockpit`: target validation, 87 tests, Ruff.
- `nirs4all-org`: HTML parser smoke and diff check.

Full Python-reference parity was not rerun in this step by instruction; it should
be run after this large batch as the next heavy gate.

## Decisions and risks

- `nirs4all-core` is now the canonical RC repo/package target in the release
  manifest and public surface matrix. `nirs4all-lite` remains a legacy/current
  artifact alias during cutover.
- A dirty staged rollback in `RC-v1-dmd` was removed because it reverted the
  published `dag-ml-data` `0.2.3` head back to `0.2.2` and corrupted the lock
  evidence.
- Public registry state is not forced green: cockpit still marks stale/missing
  targets where PyPI/npm/crates/GitHub Releases have not caught up.
- Web remains client-side-only; Node/npm are build-time tooling only.
- `nirs4all` Python and `nirs4all-studio` main were not released in this batch.
