# Wave 3Z - IO WASM Binding Native Policy

Date: 2026-07-01

## Scope

Lane E/G public-surface tranche focused on `_worktrees/INT-io`: add WASM binding smoke coverage for the native/core NA policy through `assembleDataset`. No full parity was run.

## Commit

- `_worktrees/INT-io` `4ff1cb6` - `test(io): cover native policy in wasm binding`

## Files Modified

`_worktrees/INT-io`:

- `bindings/wasm/Cargo.lock`
- `bindings/wasm/tests/idiomatic_smoke.mjs`
- `bindings/wasm/tests/node_smoke.cjs`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Descartes the 2nd | W3Z review | go | Confirmed the raw and idiomatic JS smokes exercise `assembleDataset` CSV bytes with NA replacement; confirmed the WASM lock refresh is consistent with core `sha2` and version `0.1.3`. |

## Decisions

- Added raw CommonJS WASM smoke coverage for CSV bytes + `na.replace.value`.
- Added idiomatic ESM wrapper smoke coverage for the same object-spec path.
- Kept the coverage smoke-level: alternate NA policies, joins, metadata/y roles and full parity remain covered by Rust/Python gates or deferred.
- Kept the `bindings/wasm/Cargo.lock` refresh because the build updated it from stale `0.1.1` package entries to current `0.1.3` and included the core `sha2` dependency.

## Tests Run

`_worktrees/INT-io`:

- `wasm-pack build bindings/wasm --target nodejs --out-dir pkg` -> passed.
- `"/mnt/c/Program Files/nodejs/node.exe" bindings/wasm/tests/node_smoke.cjs` -> passed.
- `"/mnt/c/Program Files/nodejs/node.exe" bindings/wasm/tests/idiomatic_smoke.mjs` -> passed.
- `git diff --check` -> passed.

Reviewer also ran:

- `cargo metadata --manifest-path bindings/wasm/Cargo.toml --locked --format-version 1` -> passed.

## Risks / Follow-Ups

- Full Python-reference parity and long dag-ml/native parity were deferred per batch policy.
- Coverage is intentionally smoke-level for public WASM; broader NA policy matrix stays in Rust core/facade tests.
- R remains a follow-up for a small spec-marshalling smoke around `params.na` / `format.columns`; no R load/assemble surface exists in v0.
