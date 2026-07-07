# Wave 8Y - Multimodal Python Rerun Parity

Date: 2026-07-07

Owner: Codex main agent

## Scope

- Promoted `e2e-multimodal-python-r-wasm-roundtrip` `python_rerun_pipeline` from contract to strict.
- Added a Python reopen/rerun ledger over the persisted multimodal pipeline and dataset.
- Kept `nirs4all-ui` untouched because another agent is actively editing it.

## Files Modified

- `nirs4all/tests/e2e/test_multimodal_roundtrip.py`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/agent_reports/WAVE_8Y_MULTIMODAL_PYTHON_RERUN_PARITY.md`

## Tests Run

- `cd nirs4all && python3.11 -m ruff check tests/e2e/test_multimodal_roundtrip.py`
- `cd nirs4all && PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_multimodal_roundtrip.py::test_generate_oracle --artifacts-dir=/tmp/n4a-multimodal-rerun`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py validate`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `cd nirs4all-ecosystem && python3.11 -m pytest tests/test_e2e_scenarios.py -q`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-multimodal-rerun-evidence run e2e-multimodal-python-r-wasm-roundtrip --execute`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-multimodal-rerun-evidence evidence --scenario e2e-multimodal-python-r-wasm-roundtrip --json`
- `cd nirs4all-ecosystem && python3.11 -m pytest -q`
- `cd nirs4all-core && PYTHONPATH=bindings/python/src python3.11 -m unittest bindings/python/tests/test_release_topology.py bindings/python/tests/test_facade.py`

## Decisions

- The new ledger uses `schema_version=n4a.e2e.python_rerun_pipeline.v1` and verifies pipeline hash, dataset hash, split hash, selected `n_components`, prediction/target shape, finite predictions, prediction delta, target delta, and RMSE delta.
- The remaining multimodal contract phase is still `wasm_web_reuse`, because native Web/Studio multimodal source-structure roundtrip is not implemented by this lane.
- Full parity was not launched; this lane used targeted E2E plus the orchestrated multimodal scenario to avoid running the long global parity gate before a larger batch.

## Risks

- The multimodal scenario still proves the dense fused-matrix proxy, not native multimodal runtime semantics.
- The Python production repo remains on the refactor branch and is not part of the final prod release gate yet.
