# Wave 4K - Core language gates

Date: 2026-07-02
Coordinator: Codex

## Scope

Refresh local proof for `RC-v1-nirs4all-core` after the RC publication audit.
This wave does not rerun full Python parity and does not change code.

Selected head:

- `nirs4all-lite` worktree `RC-v1-nirs4all-core`
- branch `rc/v1-full-refactor-core`
- commit `29d6d04a5bb0`
- tag `n4a-v1-rc1-2026.07-refactor`

## Gates Run

Rust/Python/WASM aggregate gate:

```bash
make PYTHON=python3.11 test
```

Partial result:

- Rust: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets -- -D warnings`,
  and `cargo test --workspace` passed.
- Rust tests: `8 passed`.
- Python binding tests: `54 run, 1 skipped`.
- The initial full `make test` invocation failed at the WASM step because PATH
  resolved `npm` to Windows (`/mnt/c/Program Files/nodejs/npm`) and because a
  parallel `npm ci` was running. This was an environment invocation problem, not
  a code failure.

WASM rerun with Linux Node 24:

```bash
PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH make PYTHON=python3.11 test-wasm
```

Result:

- npm: `11.13.0`
- node: `v24.16.0`
- JS/WASM tests: `13 passed, 2 skipped`
- TypeScript typecheck passed.
- Skips: local `nirs4all-methods` JS/WASM build is not available.

V1 public surfaces:

```bash
PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH make PYTHON=python3.11 test-v1-surfaces
```

Result:

- Python V1 surface tests: `53 passed`.
- WASM V1 surface tests: `13 passed, 1 skipped`.
- TypeScript typecheck passed.
- R V1 surface gate reported:
  `SKIP/RISK: R V1 public surface not checked: R/Rscript is not installed`.

Strict core parity against selected methods RC build:

```bash
LD_LIBRARY_PATH=/home/delete/nirs4all/_worktrees/RC-v1-methods/build/dev-release/cpp/src:$LD_LIBRARY_PATH \
NIRS4ALL_METHODS_LIB=/home/delete/nirs4all/_worktrees/RC-v1-methods/build/dev-release/cpp/src/libn4m.so.2.0.0 \
NIRS4ALL_METHODS_PYTHONPATH=/home/delete/nirs4all/_worktrees/RC-v1-methods/bindings/python/src \
make PYTHON=python3.11 test-python-parity
```

Result: `1 passed`.

```bash
LD_LIBRARY_PATH=/home/delete/nirs4all/_worktrees/RC-v1-methods/build/dev-release/cpp/src:$LD_LIBRARY_PATH \
NIRS4ALL_METHODS_LIB=/home/delete/nirs4all/_worktrees/RC-v1-methods/build/dev-release/cpp/src/libn4m.so.2.0.0 \
make test-rust-parity
```

Result: `1 passed`.

## Environment Gaps

- `R` and `Rscript` are not installed locally, so R package execution remains an
  environment gate.
- `octave` is not installed locally, so MATLAB/Octave execution remains an
  environment gate.
- The local `nirs4all-methods` JS/WASM package build is not available, so the
  WASM methods execution parity cases remain explicit skips in this local run.

## Decision

Core is stronger than the previous state for RC accounting: Rust, Python, WASM
topology, V1 surfaces, and strict Python/Rust core parity are locally proven on
the selected RC heads. This is not sufficient to claim full language release
completion because R, MATLAB/Octave, and methods-backed JS/WASM execution still
need an environment that can run them.
