# Wave 2Y Release Lock Rebase

Date: 2026-07-01T18:10:00+02:00

## Scope

Follow-up after W2W and W2X. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2Y targets Lane A/E/G release-lock and topology consistency:

- Audit the current selected release heads after the reset and W2W/W2X commits.
- Verify that `nirs4all` Python, R, and WASM release surfaces remain represented.
- Regenerate `docs/contracts/release/aggregation-lock.n4a.lock.json` only if
  current workspace heads are clean enough and the lock generator reads trusted
  tracked metadata.
- Do not run `pyref_oracle_full`.
- Do not merge old W2K/W9x worktrees without audit; many are superseded by
  current repo heads.

## Starting State

- `nirs4all-ecosystem`: `639d3af`
- `_worktrees/INT-nirs4all`: `122ef5d1`
- `_worktrees/INT-studio`: `2fb8df8`
- `nirs4all-lite/main`: `272e07f`
- `nirs4all-methods/main`: `00ca8467`
- `nirs4all-tools/main`: `fd51610`
- `dag-ml`: `a428926` on `refactor/L20-lockstep`
- `dag-ml-data`: `818616e` on `refactor/L20-lockstep`, with a dirty generated
  `_dag_ml_data.abi3.so` preserved and not reverted.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| A | Tesla | read-only ecosystem/release lock | Audit current component heads, dirty blockers, and GO/NO-GO for lock regeneration. |
| A/G | Carson | read-only dag-ml/dag-ml-data | Audit lockstep contracts and whether dirty generated binary blocks release lock. |
| E | Linnaeus | read-only nirs4all-lite | Verify Python/R/WASM topology surfaces and whether current main is the selected release head. |
| A/K | coordinator | ecosystem only if approved | Generate, validate, review, and commit the aggregation lock update. |

## Planned Gates

- Temporary lock generation to `/tmp` for diff/audit before touching tracked lock.
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all validate ...`
- `python3 -m pytest tests/test_release_lock.py tests/test_release_surface_matrix.py -q`
- `python3 scripts/n4a_release_surface_matrix.py validate`

`pyref_oracle_full` is intentionally deferred.

## Audit Results

### Tesla - Release Lock/Pins

Recommendation: NO-GO for regenerating the aggregation lock from the raw
`/home/delete/nirs4all` workspace.

- Checked-in lock validates against `_release_roots/W2L-selected`.
- Raw workspace validation fails because it would capture unintended local state:
  - `dag-ml-data` raw checkout is dirty.
  - raw `nirs4all-io` is `e52eecd`, while the selected lock head is clean
    `refactor/integration-io` at `eae8263`.
- `nirs4all` surfaces remain represented:
  - `nirs4all.python.oracle` in the public V1 matrix, outside aggregation lock.
  - `nirs4all.r.aggregate` via locked `lite`.
  - `nirs4all.browser_wasm.aggregate` via locked `lite`.

### Carson - dag-ml / dag-ml-data

- `dag-ml` is clean at `a428926` on `refactor/L20-lockstep`, same commit as
  `refactor/integration-dagml`.
- `dag-ml-data` is at `818616e` on `refactor/L20-lockstep`, same commit as
  `refactor/integration-dmd`, but has one dirty tracked generated binary:
  `crates/dag-ml-data-py/python/dag_ml_data/_dag_ml_data.abi3.so`.
- Cross-repo contract validation passed both directions.
- The dirty `.so` is not part of the explicit shared-contract lockstep artifact
  set, but it should block any PyPI/wheel release decision until resolved.

### Linnaeus - nirs4all-lite topology

Recommendation: GO for using `nirs4all-lite/main` at `272e07f`.

- `refactor/integration-lite` is stale: it is an ancestor of `main` and lacks
  the post-merge V1 surface/facade gate commits.
- Current `main` includes:
  - Python distribution `nirs4all-lite`, import `nirs4all_lite`.
  - Python additive facades `n4a` and `nirs4all_core`.
  - Rust crate package `nirs4all`.
  - npm/WASM package `nirs4all`.
  - R package `nirs4all`.
- R/Octave runtime checks were not run locally because R/Octave are unavailable.

## Coordinator Decision

Do not regenerate `aggregation-lock.n4a.lock.json` from the raw workspace in
W2Y. The checked-in lock is valid for the selected release root and should stay
unchanged until either:

1. the raw workspace is aligned to the selected heads and clean, or
2. a future release-lock tool accepts an explicit selected-root mapping instead
   of relying on sibling checkout names.

The release-lock blocker is therefore reclassified from "lock content stale" to
"raw workspace does not match selected clean release root".

## Gates Run

- PASS: `python3 -B scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_release_roots/W2L-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- PASS: `python3 -B scripts/n4a_release_surface_matrix.py validate`
- PASS: `python3 -B -m pytest tests/test_release_surface_matrix.py tests/test_release_lock.py tests/test_cutover_state_gate.py -q`
  - 13 passed.

## Remaining Decisions

- Resolve the dirty/generated `dag-ml-data` Python extension before any
  PyPI/wheel release decision.
- Decide whether to promote selected-root symlink construction into a tracked
  release helper or keep it as local coordinator state.
- Keep `refactor/integration-lite` out of future release pin decisions; use
  `nirs4all-lite/main`.
