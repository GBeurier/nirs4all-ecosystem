# Wave 4CV — Provider Repository Execution Parity

Date: 2026-07-04

## Scope

- Lane C / G / J: provider to repository to core E2E evidence.
- Repos changed: `nirs4all-core`, `nirs4all-ecosystem`.
- Production hold respected: no change to `nirs4all` Python production or `nirs4all-studio`.

## Changes Integrated

- `nirs4all-core@a853894`
  - `scripts/e2e/consume_repository_descriptor.py`
    - The `cross-language-consumption.json` artifact now has top-level `status: passed`.
    - Added deterministic synthetic NIRS execution data.
    - Executes the repository pipeline through Python and JavaScript/WASM binding surfaces.
    - Requires both runtime surfaces; missing Python or WASM now fails the gate.
    - Compares split, preprocessing, targets, RMSE, prediction vectors, and `predictPortablePipeline` roundtrip within `1e-10`.
  - `tests/test_consume_repository_descriptor.py`
    - Adds unit coverage for successful execution evidence, drift detection, and required Python/WASM runtime surfaces.
- `nirs4all-ecosystem`
  - `nirs4all-core` gitlink moved to `a853894`.
  - `e2e-dataset-provider-repository-roundtrip` upgraded from `contract_smoke` to `hybrid`.

## Verification

From `nirs4all-core`:

- `python3.11 -m py_compile scripts/e2e/consume_repository_descriptor.py tests/test_consume_repository_descriptor.py`
- `PYTHONPATH=bindings/python/src python3.11 -m unittest discover -s tests -p 'test_consume_repository_descriptor.py'` — 3 passed.
- Repository descriptor smoke with `portable_methods_pipeline.json` — Python + WASM strict comparison passed.
- `PYTHONPATH=bindings/python/src:/home/delete/nirs4all/nirs4all-methods/bindings/python/src python3.11 -m unittest bindings.python.tests.test_pipeline_contract bindings.python.tests.test_execution_parity` — 8 passed.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm test --prefix bindings/wasm` — 15 passed.
- `python3.11 -m ruff check scripts/e2e/consume_repository_descriptor.py tests/test_consume_repository_descriptor.py` — OK.

## Remaining Gaps

- The strict execution proof uses deterministic synthetic NIRS data, not the provider-materialized catalog dataset.
- R remains covered by separate core/methods gates and is not part of this provider repository roundtrip.
