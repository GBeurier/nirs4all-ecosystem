# Wave 3V - IO Native Parquet Bridge

Date: 2026-07-01

## Scope

Lane G tranche focused on `_worktrees/INT-io`: add native Parquet loading to the Rust facade and expose it through the pyo3 Python binding. No `nirs4all-formats` routing was added for canonical dataset Parquet, and no full Python-reference parity was run.

## Commit

- `_worktrees/INT-io` `734acd3` - `feat(io): load parquet in native facade`

## Files Modified

`_worktrees/INT-io`:

- `Cargo.lock`
- `bindings/python/Cargo.lock`
- `bindings/python/python/nirs4all_io/__init__.py`
- `bindings/python/tests/test_idiomatic.py`
- `crates/nirs4all-io-core/src/materialize/assemble.rs`
- `crates/nirs4all-io-core/src/materialize/frame.rs`
- `crates/nirs4all-io-core/src/materialize/package.rs`
- `crates/nirs4all-io/Cargo.toml`
- `crates/nirs4all-io/src/materialize/assemble.rs`
- `crates/nirs4all-io/src/materialize/loaders.rs`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Parfit the 2nd | IO implementation | integrated | Added Parquet/Arrow loader, removed pyo3 Parquet guard, added binding test seed. Supervisor completed the integration and tests. |
| Fermat the 2nd | datasets bridge audit | done | Confirmed canonical datasets use generated Parquet under ignored `canonical/`; recommended synthetic `canonical_dataset` smoke and warned not to route canonical Parquet through `nirs4all-formats`. |
| Rawls the 2nd | W3V review | fixed/go | Found a blocker in shared Parquet input caching with per-source params. Supervisor fixed it with per-use `Frame` param application and a regression test; re-review returned GO. |

## Decisions

- `nirs4all-io` facade now owns native `.parquet` / `.pq` loading via Arrow/Parquet, with `snap` and `zstd` enabled for datasets canonical Parquet.
- `nirs4all-io-core` remains filesystem-free. The facade may pre-decode a Parquet table into `SourcePayload::Frame`; the core applies `format.columns` and `header_unit` per source/variation use.
- `Cell::Bool` was added so bool columns are not downgraded to strings.
- The pyo3 `load()` surface no longer blocks Parquet inputs before native materialization.
- The first-review blocker is covered by `shared_parquet_path_applies_format_columns_per_source`.

## Tests Run

`_worktrees/INT-io`:

- `cargo test -p nirs4all-io shared_parquet_path_applies_format_columns_per_source --no-fail-fast` -> passed.
- `cargo test -p nirs4all-io --no-fail-fast` -> passed.
- `cargo test -p nirs4all-io-core --no-fail-fast` -> passed.
- `cargo test --workspace --no-fail-fast` -> passed.
- `cargo clippy --workspace --all-targets -- -D warnings` -> passed.
- `cargo build --workspace --no-default-features` -> passed.
- `uv run --python 3.11 --with maturin --with pytest --with numpy --with pandas bash -lc 'maturin develop && pytest -q tests/test_idiomatic.py'` from `bindings/python` -> 9 passed.
- `ruff check bindings/python/tests/test_idiomatic.py bindings/python/python/nirs4all_io/__init__.py` -> passed.
- `cargo fmt --all --check` -> passed.
- `git diff --check` -> passed.
- Cross-repo smoke: synthetic `nirs4all-datasets` canonical dataset with zstd Parquet -> `nirs4all_io.load(ds, target="assembled")` -> passed.

## Risks / Follow-Ups

- Rust loader NA policy remains broader IO work; W3V tests avoid treating Parquet null default handling as a new parity guarantee.
- Parquet support is intentionally scoped to scalar bool/int/float/string/null columns. Unsupported Arrow/Parquet logical types fail explicitly.
- Full Python-reference parity and long dag-ml/native parity were deferred per batch policy.
