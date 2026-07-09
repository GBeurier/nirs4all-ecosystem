# WAVE 10AT - Python parity skip audit

Date: 2026-07-09

## Scope

- Re-audit the current `nirs4all` Python reference test state after the recent
  reset and integration batches.
- Remove local runtime skips that could hide missing prediction artifacts.
- Keep the full parity suite deferred until the next large integration batch.

## Agents and review

- Codex explorer `019f46d1-fdf6-7811-a350-98ab5f15b5d1`: read-only
  `nirs4all` Python audit.
  - Finding: parity registry has no active xfails, but a few integration tests
    used runtime skips for missing predictions.
  - Finding: system Python 3.10 is not a valid test interpreter for this repo;
    `.venv/bin/python` is Python 3.11.15 and collects reliably.
- Codex explorer `019f46d2-181f-7623-ad16-3b370f5d03d8`: read-only
  ecosystem/core audit.
  - Finding: cross-language E2E evidence is ready for the current artifact set;
    long runtime execution should remain a batch gate, not a per-commit gate.

## Files changed

- `nirs4all/tests/integration/artifacts/test_artifact_flow.py`
- `nirs4all/tests/integration/pipeline/test_branch_artifacts.py`
- `nirs4all/tests/integration/pipeline/test_merge_prediction_mode.py`
  - Replaced runtime `pytest.skip(...)` guards for missing prediction artifacts
    with explicit assertions.
- `nirs4all/tests/unit/data/loaders/test_parquet_loader.py`
  - Changed the module-level Parquet availability check to accept either
    `pyarrow` or `fastparquet`.

Commit: `d3863ee2 test(parity): harden prediction and parquet skip guards`

## Tests and gates

- `cd nirs4all && .venv/bin/python -m pytest -q tests/integration/artifacts/test_artifact_flow.py tests/integration/pipeline/test_branch_artifacts.py tests/integration/pipeline/test_merge_prediction_mode.py tests/unit/data/loaders/test_parquet_loader.py`
  - 38 passed.
- `cd nirs4all && .venv/bin/python -m pytest -q tests/integration/parity/test_parity_compiles.py tests/integration/parity/test_compatibility_ledger.py`
  - 99 passed.
- `cd nirs4all && .venv/bin/python -m pytest -q tests/regression`
  - 22 passed.
- `cd nirs4all && .venv/bin/ruff check tests/integration/artifacts/test_artifact_flow.py tests/integration/pipeline/test_branch_artifacts.py tests/integration/pipeline/test_merge_prediction_mode.py tests/unit/data/loaders/test_parquet_loader.py`
  - Passed.

## Parity ledger snapshot

- Registered parity capabilities: 95.
- Runnable parity capabilities: 95.
- Non-runnable parity capabilities: 0.
- Non-legacy skip total: 0.
- Strict xfail total: 0.
- Legacy bug xfail: 0.
- Known divergence xfail: 0.
- Expected fallback markers remain documented: 15.

## Remaining risks

- The full Python-reference parity suite was intentionally not run in this
  small hardening batch because it is long; run it after the next large batch.
- Optional dependency skips remain for legitimately absent local toolchains or
  libraries.
- The Parquet test file still skips only when neither supported Parquet engine
  is installed.
