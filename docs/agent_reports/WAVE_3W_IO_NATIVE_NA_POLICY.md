# Wave 3W - IO Native NA Policy

Date: 2026-07-01

## Scope

Lane G tranche focused on `_worktrees/INT-io`: port the Python MVP NA policy into the Rust IO core and apply it consistently to CSV bytes, facade-decoded frames, and native Parquet reads. Full Python-reference parity was intentionally deferred until a larger batch.

## Commit

- `_worktrees/INT-io` `789c3e5` - `feat(io): apply native NA policy`

## Files Modified

`_worktrees/INT-io`:

- `crates/nirs4all-io-core/src/materialize/assemble.rs`
- `crates/nirs4all-io-core/src/materialize/loaders.rs`
- `crates/nirs4all-io-core/src/materialize/mod.rs`
- `crates/nirs4all-io-core/tests/assemble_in_memory.rs`
- `crates/nirs4all-io/src/materialize/assemble.rs`
- `crates/nirs4all-io/src/materialize/loaders.rs`
- `crates/nirs4all-io/tests/parquet_na.rs`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Euclid the 2nd | IO implementation seed | integrated | Added the first native NA policy skeleton and split Parquet raw decode from public `read_table`; supervisor extended, tested, and committed. |
| Aristotle the 2nd | Python oracle / placement audit | done | Confirmed exact Python MVP `apply_na_policy` semantics and identified the Parquet default-abort trap in `source_payload`. |
| Huygens the 2nd | W3W review | go | Read-only review returned GO; no blocking findings. Residual risk documented for unsupported unselected Parquet columns in raw shared-frame assembly. |

## Decisions

- `nirs4all-io-core::materialize::apply_na_policy` is the pure shared implementation for `auto => abort`, `ignore`, `remove_sample`, `remove_feature`, and `replace`.
- `replace` now covers Python MVP fill methods: `value` with default `0.0`, `mean`, `median`, `forward_fill`, and `backward_fill`.
- Mean/median fill follows Python rules: per-column numeric fill leaves non-numeric NA untouched; global fill computes over numeric columns and fills the whole frame.
- Forward/backward fill follows Python `axis=1` behavior across columns within each row.
- `SourcePayload::Frame` applies `format.columns` and `header_unit` first, then effective NA policy. This keeps Parquet shared-frame assembly source-specific.
- Native Parquet assembly decodes a raw frame without applying default `auto=abort`; source/global params are applied later in the core.

## Tests Run

`_worktrees/INT-io`:

- `cargo test -p nirs4all-io-core materialize::loaders -- --nocapture` -> passed.
- `cargo test -p nirs4all-io-core frame_payload_applies_source_na_policy_after_projection -- --nocapture` -> passed.
- `cargo test -p nirs4all-io parquet -- --nocapture` -> passed.
- `cargo fmt --all --check` -> passed.
- `cargo test -p nirs4all-io-core --no-fail-fast` -> passed.
- `cargo test -p nirs4all-io --no-fail-fast` -> passed.
- `cargo clippy --workspace --all-targets -- -D warnings` -> passed.
- `cargo test --workspace --no-fail-fast` -> passed.
- `cargo build --workspace --no-default-features` -> passed.
- `uv run --python 3.11 --with maturin --with pytest --with numpy --with pandas bash -lc 'maturin develop && pytest -q tests/test_idiomatic.py'` from `bindings/python` -> 9 passed.
- `git diff --check` -> passed.

## Risks / Follow-Ups

- Full Python-reference parity and long dag-ml/native parity were deferred per batch policy.
- Assembly still decodes Parquet shared inputs as raw frames before per-source projection. That preserves W3V shared-input behavior, but `format.columns` cannot yet avoid an unsupported unselected Parquet column during assembly. A later IO micro-lane should consider per-path union projection across all source/variation uses.
- The public `nirs4all` Python/R/WASM surfaces are not changed by this batch; they remain covered by W3P and should stay in final roadmap/release gates.
