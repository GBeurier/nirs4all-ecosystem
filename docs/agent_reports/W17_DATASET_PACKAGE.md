# W17 - DatasetPackage Bridge

Status: salvaged after max-turns, verified, and committed.

## Scope

W17 added the Rust-side target-agnostic `DatasetPackage` v2 bridge in
`nirs4all-io`, without replacing the existing `AssembledDataset` or
`to_dag_ml_data` path.

## Changes

- Added `nirs4all_io::core::materialize::package` with:
  - `DatasetPackage`;
  - typed payload blocks;
  - payload manifest entries with SHA-256 `content_hash`;
  - manifest root hashing;
  - inline vs URI-backed payload descriptors;
  - explicit row-position fallback diagnostics.
- Re-exported package types from `materialize::mod`.
- Added `sha2` dependency to `nirs4all-io-core`.
- Derived `PartialEq` for `Cell`, `Column`, and `Frame` to support package
  round-trip assertions.
- Added `nirs4all-io-dagml::to_dataset_package()` as the package companion to
  `to_dag_ml_data()`.

## Verification

From `_worktrees/W17-io-dataset-package`:

```bash
cargo fmt --all --check
cargo test -p nirs4all-io-core materialize::package --lib
cargo test -p nirs4all-io-dagml to_dataset_package --lib
cargo test -p nirs4all-io-core --lib
cargo test -p nirs4all-io-dagml --lib
cargo clippy -p nirs4all-io-core -p nirs4all-io-dagml --all-targets -- -D warnings
cargo test --workspace
```

Results:

- `DatasetPackage` focused tests: `10 passed`.
- Core lib: `93 passed`.
- Dagml bridge lib: `5 passed`.
- Clippy targeted: clean.
- Workspace test suite: passed.

## Commit

`0a06943 feat(io): add typed dataset package bridge`
