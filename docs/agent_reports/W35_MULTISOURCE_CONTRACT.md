# W35 report - dag-ml multi-source contract

Summary:
W35 hardened dag-ml's multi-source data contract. Source concatenation now requires explicit feature-axis source metadata, by-source branches are constrained to exactly supported source scopes, and grouped by-source shapes are refused with machine-readable reasons instead of silently running ambiguous semantics.

Code changed:
- Added/propagated `metadata.source_index` through planning/runtime paths.
- Refused implicit source concat when source feature blocks are not declared.
- Documented data contract behavior for multi-source and by-source execution.
- Added runtime tests for the new contract boundaries.

Files touched:
- `crates/dag-ml-core/src/data.rs`
- `crates/dag-ml-core/src/plan.rs`
- `crates/dag-ml-core/src/runtime/merge.rs`
- `crates/dag-ml-core/src/runtime/tests.rs`
- `docs/contracts/README.md`

Commits:
- `dag-ml/refactor/W35-multisource-contract` `a1b9697`
- Integrated into `dag-ml/refactor/integration-dagml` as `35e9e00`

Tests run:
- `cargo fmt --all --check` -> passed.
- `cargo test -p dag-ml-core` -> `439 passed, 2 ignored`.
- `cargo clippy -p dag-ml-core --all-targets -- -D warnings` -> passed.
- Cross-repo `validate_contracts.py` with `DAG_ML_DATA_REPO=/home/delete/nirs4all/_worktrees/INT-dmd` -> passed.

Impact:
Supports future `B-010` multi-source drain by making source-axis assumptions explicit in dag-ml instead of host-only.

Next action:
Consume the stricter contract from nirs4all fallback-drain slices before removing the remaining multi-source fallback cases.

Sync doc updated: yes
