# WAVE 7Q - RC11 release-lock canonicalization

Date: 2026-07-06
Agent: Codex
Lane: release lock / topology

## Scope

- Published the immutable coordination tag `n4a-v1-rc11-2026.07-refactor` for the seven aggregation-lock members.
- Regenerated the aggregation lock from a clean selected-root so the lock includes the post-RC10 `dag-ml` Python extension freshness fix and `dag-ml-data` R packaging fix.
- Left `nirs4all-ui`, `nirs4all-quality`, `nirs4all`, and `nirs4all-studio` untouched.

## Selected lock heads

| Member | Repo | Commit | Tag |
| --- | --- | --- | --- |
| `dag_ml` | `dag-ml` | `b3f34bf2c3c2` | `n4a-v1-rc11-2026.07-refactor` |
| `dag_ml_data` | `dag-ml-data` | `bfe6431124a4` | `n4a-v1-rc11-2026.07-refactor` |
| `datasets` | `nirs4all-datasets` | `f7b9caa1137b` | `n4a-v1-rc11-2026.07-refactor` |
| `formats` | `nirs4all-formats` | `181946f141ed` | `n4a-v1-rc11-2026.07-refactor` |
| `io` | `nirs4all-io` | `ccf9a7d2f799` | `n4a-v1-rc11-2026.07-refactor` |
| `lite` | `nirs4all-core` | `1708ab0305a8` | `n4a-v1-rc11-2026.07-refactor` |
| `methods` | `nirs4all-methods` | `115077ae4551` | `n4a-v1-rc11-2026.07-refactor` |

## Files changed

- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `tests/test_release_lock.py`

## Validation

- Selected root: `/tmp/n4a-selected-rc11-20260706`
- `python scripts/n4a_release_lock.py --workspace-root /tmp/n4a-selected-rc11-20260706 validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -p no:cacheprovider`
  - Result: `23 passed`
- `python scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output-json /tmp/n4a-fetch-rc11-audit.json --fail-on-unfetchable`
  - Result: `7/7 member commits checked out; 0 unfetchable`
- `git diff --check`

## Notes

- `dag_ml_data` is locked at the RC branch commit `bfe6431`; `main` also contains the same R packaging fix through merge commit `c53ee46` for R-universe.
- The product package versions did not change: `dag-ml` remains `0.2.3`, `dag-ml-data` remains `0.2.4`.
