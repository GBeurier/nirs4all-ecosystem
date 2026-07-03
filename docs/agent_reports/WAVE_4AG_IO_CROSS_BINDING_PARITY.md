# Wave 4AG - IO Cross-Binding Parity Gate

Date: 2026-07-03

Scope:

- `nirs4all-io` selected RC worktree: `_worktrees/RC-v1-io`
- Branch: `rc/v1-full-refactor`
- Head: `26963d5`
- Tag: `n4a-v1-rc1-2026.07-refactor`

Files changed:

- `tests/cross_binding/verify.sh`
- `.github/workflows/cross-binding.yml`
- `docs/STATUS.md`

Decision:

- The cross-binding gate now includes the Python pyo3 `_native.to_spec` leg
  when `maturin` and Python >=3.11 are available.
- The gate remains availability-aware for optional bindings, but the present
  Linux RC host proved CLI and Python byte identity.
- This closes the immediate IO evidence gap that the Python binding existed but
  was not part of the cross-binding parity script.

Local gates:

- `bash -n tests/cross_binding/verify.sh && bash tests/cross_binding/verify.sh`
  -> `ALL 2 bindings agree byte-for-byte: cli python`.
- `cargo fmt --all --check && cargo clippy --workspace --all-targets -- -D warnings`
  -> passed.
- `cargo test --workspace`
  -> passed across Rust, C ABI, CLI, core, dag-ml and doctest targets.

GitHub gates on pushed head `26963d5`:

- `version-guard`: success.
- `version-sync`: success.
- `CI`: success.
- `R binding`: success.
- `Octave binding`: success.
- `WASM binding`: success.
- `Python binding`: success.
- `dag-ml-data conformance`: success.
- `ABI Surface`: success.
- `Cross-binding parity`: success.

Risks:

- The local cross-binding run proved CLI/Python because WASM/R were not part of
  that host invocation. GitHub separately proved the binding jobs.
- Broader non-Python dataset materialization remains owned by IO/datasets bridge
  contracts and later host matrices.
