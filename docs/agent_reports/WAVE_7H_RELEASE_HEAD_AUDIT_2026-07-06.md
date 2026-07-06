# Wave 7H - release head audit

Date: 2026-07-06

## Scope

Verify that the ecosystem release contracts and release-facing reports still
match the currently selected or intentionally retained heads, without changing
production `nirs4all` Python or production `nirs4all-studio`.

## Authoritative state

- `nirs4all-ecosystem`: `main` at `72749b5`.
- `aggregation-manifest.n4a.json` remains consistent with the intended topology:
  - aggregate target is `nirs4all-core`;
  - `nirs4all-lite` is legacy compatibility only;
  - `nirs4all-providers` remains an outside-lock optional Python client over
    neutral provider contracts;
  - `nirs4all` Python oracle and `nirs4all-studio` product remain outside the
    aggregation lock.
- `aggregation-lock.n4a.lock.json` is still the authoritative selected-member
  source of truth. Validated via an isolated `checkout-members` workspace, not
  via live `_worktrees`.

Current authoritative lock member heads:

| Member | Repo | Commit | Tag |
| --- | --- | --- | --- |
| `dag_ml` | `dag-ml` | `4238443c` | `n4a-v1-rc8-2026.07-refactor` |
| `dag_ml_data` | `dag-ml-data` | `f8483800` | `n4a-v1-rc8-2026.07-refactor` |
| `lite` | `nirs4all-core` | `5c652e66` | `n4a-v1-rc8-2026.07-refactor` |
| `methods` | `nirs4all-methods` | `115077ae` | `n4a-v1-2026.07-refactor` |
| `formats` | `nirs4all-formats` | `181946f1` | `n4a-v1-2026.07-refactor` |
| `io` | `nirs4all-io` | `1fc6c120` | `n4a-v1-2026.07-refactor` |
| `datasets` | `nirs4all-datasets` | `c46042da` | `n4a-v1-2026.07-refactor` |

## Findings

1. Live `RC-v1-dagml` has advanced to `d7ee3ccd` (`n4a-v1-2026.07-refactor`),
   but that head no longer locksteps with the currently selected `dag-ml-data`
   commit. Regenerating the release lock on that newer `dag-ml` head makes the
   `dagml-pair` equivalence invalid. The lock was therefore left unchanged.
2. Live `RC-v1-dmd` is locally dirty and includes uncommitted reversions from
   `0.2.4` to `0.2.3` in tracked release files. That disk state is not
   authoritative release evidence and must not be used to regenerate the lock.
3. `RC-v1-ui` contains the non-main assets branch
   `codex/ui-assets-brand-system` at `ed0f71c`, documented in
   `WAVE_7F_UI_VISUAL_ASSET_SYSTEM.md`. It is relevant as a reviewable UI-assets
   branch only; it is not a merged `main` product head and is not part of the
   aggregation lock.
4. `public-v1-surface-matrix.n4a.json` still models the held production split
   correctly:
   - Python oracle: repo `nirs4all`, selected RC worktree
     `RC-v1-nirs4all-python`, target repo path `nirs4all-python`.
   - Studio product: repo `nirs4all-studio`, outside the aggregation lock.

Reference heads retained by policy:

- `nirs4all` production checkout: `main` `4b75d8c5`
- selected Python oracle RC worktree: `bf242e48`
- `nirs4all-studio` production checkout: `main` `87b2a9d3`
- selected Studio RC worktree: `15082420`

## Result

No release-contract repin was applied. The only safe authority today is:

- manifest semantics as committed on ecosystem `72749b5`;
- the existing aggregation lock, validated from an isolated selected-root;
- the public V1 surface matrix for outside-lock surfaces;
- the explicit note that live RC worktrees may advance beyond the lock without
  becoming selected heads.

## Validation

- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_release_lock.py checkout-members --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output <tmp>`
- `python3 scripts/n4a_release_lock.py --workspace-root <tmp> validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -p no:cacheprovider`
