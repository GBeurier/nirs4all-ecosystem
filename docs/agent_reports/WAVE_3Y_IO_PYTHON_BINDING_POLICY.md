# Wave 3Y - IO Python Binding Native Policy

Date: 2026-07-01

## Scope

Lane E/G public-surface tranche focused on `_worktrees/INT-io`: add Python binding coverage for the native IO behaviors introduced by W3W/W3X. No full Python-reference parity was run.

## Commit

- `_worktrees/INT-io` `b050c2a` - `test(io): cover native policy in python binding`

## Files Modified

`_worktrees/INT-io`:

- `bindings/python/tests/test_idiomatic.py`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Sagan the 2nd | binding surface audit | done | Read-only; confirmed Python is the direct native file-IO binding, R has no load/assemble surface, and WASM needs a later CSV+NA `assembleDataset` smoke. |
| Avicenna the 2nd | W3Y review | go | Read-only review returned GO; confirmed tests exercise public `nio.load` and deterministic inline Parquet fixtures. |

## Decisions

- Added public Python binding tests through `nio.load(..., target="assembled")`.
- Covered CSV native NA replace from the Python surface.
- Covered Parquet native NA replace from the Python surface.
- Covered Parquet projection skipping an unsupported unselected column from the Python surface.
- Kept Parquet fixtures inline as base64 to avoid a runtime/test dependency on `pyarrow`.
- Deferred WASM and R follow-ups: WASM should get a small CSV+NA `assembleDataset` smoke; R remains low risk because v0 exposes spec/infer/validate, not load/assemble.

## Tests Run

`_worktrees/INT-io/bindings/python`:

- `uv run --python 3.11 --with maturin --with pytest --with numpy --with pandas bash -lc 'maturin develop && pytest -q tests/test_idiomatic.py'` -> 12 passed.
- `uv run --python 3.11 --with ruff ruff check tests/test_idiomatic.py` -> passed.

`_worktrees/INT-io`:

- `git diff --check` -> passed.

## Risks / Follow-Ups

- Full Python-reference parity and long dag-ml/native parity were deferred per batch policy.
- Inline Parquet fixtures are deterministic but opaque; keep regeneration rationale in nearby comments if they change.
- Add a later WASM `assembleDataset` CSV+NA smoke and an R spec-marshalling smoke for `params.na` / `format.columns`.
