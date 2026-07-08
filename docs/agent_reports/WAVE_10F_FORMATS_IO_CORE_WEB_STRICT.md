# Wave 10F - Formats/IO Core Web Strict Evidence

Date: 2026-07-08

## Scope

Promote only `e2e-formats-io-datasets-methods-language-bindings` from hybrid to strict by adding a real nirs4all-core client-side WASM pipeline import over the assembled formats/IO dataset ledger.

## Files Modified

- `nirs4all-io/tests/e2e/test_formats_io_datasets_methods.py`
  - Adds `web_core_fixture` payloads for single-source and dense-fused multi-source assembled datasets.
- `nirs4all-core/scripts/e2e/run_formats_io_core_web_import.py`
  - Runs the assembled ledger through the `nirs4all` WASM package and compares it against `nirs4all_core` Python on the same dense matrices.
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - Adds the `core-web-import-assembled-ledger` step and `web-core-pipeline-import.json` artifact.
  - Promotes the formats/IO/methods scenario to `strict`.
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
  - Requires the new Web/core artifact and numeric delta checks.
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
  - Updates coverage expectations from `hybrid:3` to `hybrid:2`.

## Validation

- `PYTHONPATH=src python3.11 -m pytest tests/e2e/test_formats_io_datasets_methods.py::test_assemble_reference_datasets --artifacts-dir=/tmp/n4a-formats-io-core-web/formats-io-methods -q`
  - Result: passed.
- `LD_LIBRARY_PATH=/home/delete/nirs4all/nirs4all-methods/build/dev-release/cpp/src:$LD_LIBRARY_PATH PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/e2e/run_formats_io_core_web_import.py --artifacts-dir /tmp/n4a-formats-io-core-web/formats-io-methods`
  - Result: passed; single-source and dense-fused multi-source deltas are 0.
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-formats-io-core-web run --execute e2e-formats-io-datasets-methods-language-bindings`
  - Result: passed.
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-formats-io-core-web evidence --scenario e2e-formats-io-datasets-methods-language-bindings --json`
  - Result: 5 artifacts verified, 0 failures.
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/test_e2e_scenarios.py -q`
  - Result: 129 passed.

## Remaining Risk

The full strict gate still fails intentionally: `non_strict_evidence_levels=hybrid:2`, `strictness_gaps=2`, `v1_contract_phases=1`. Remaining gaps are multimodal Web/Studio/native source-aware runtime evidence and multisource `by_source`/external corpus replay, not formats/IO/methods.
