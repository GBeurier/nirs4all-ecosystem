# Wave 3X - IO Parquet Projection Cache

Date: 2026-07-01

## Scope

Lane G tranche focused on `_worktrees/INT-io`: close the W3W residual risk where native assembly decoded an entire shared Parquet frame before per-source projection. Full Python-reference parity was intentionally deferred.

## Commit

- `_worktrees/INT-io` `9bb4e4a` - `feat(io): project parquet source cache`

## Files Modified

`_worktrees/INT-io`:

- `crates/nirs4all-io/src/materialize/assemble.rs`
- `crates/nirs4all-io/src/materialize/loaders.rs`
- `crates/nirs4all-io/tests/parquet_na.rs`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Mendel the 2nd | IO implementation | integrated | Added per-physical-path Parquet projection union and focused tests; supervisor added extra global/null fallback coverage and committed. |
| Lovelace the 2nd | source/variation projection audit | done | Read-only; confirmed source and variation params must mirror core `effective_params` order and fallback to full read when any use has no explicit columns. |
| Chandrasekhar the 2nd | W3X review | go | Read-only review returned GO; no blocking findings. Recommended extra global/null coverage, added before commit. |

## Decisions

- Native assembly now computes Parquet projection requirements by canonical physical path.
- If every use of a Parquet path has explicit `format.columns`, the facade decodes the stable first-seen union.
- If any use has no `format.columns` or explicit `columns: null`, the facade keeps the previous full-frame decode behavior.
- Source projections use `effective_params(spec.params, source.params)`.
- Variation projections use the same source-effective params, then overlay `variation.params`, matching the core load path.
- The raw Parquet frame reader accepts optional projected columns and still does not apply source NA policy; source/global params remain applied later in the shared core.

## Tests Run

`_worktrees/INT-io`:

- `cargo fmt --all --check` -> passed.
- `cargo test -p nirs4all-io --test parquet_na -- --nocapture` -> passed.
- `cargo test -p nirs4all-io shared_parquet_path_applies_format_columns_per_source -- --nocapture` -> passed.
- `cargo test -p nirs4all-io reads_parquet_projected_columns_in_requested_order -- --nocapture` -> passed.
- `cargo test -p nirs4all-io --no-fail-fast` -> passed.
- `cargo clippy -p nirs4all-io --all-targets -- -D warnings` -> passed.
- `git diff --check` -> passed.

## Risks / Follow-Ups

- Full Python-reference parity and long dag-ml/native parity were deferred per batch policy.
- Source payload de-duplication remains name-based as before, while projection is keyed by canonical physical path. The reviewer judged this low risk; a future cleanup can unify these keys if needed.
- This is an IO facade-only change; public `nirs4all` R/Python/WASM final gates remain in scope via W3P and final release validation.
