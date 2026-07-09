# WAVE 10AK - strict performance workload

Date: 2026-07-09

## Scope

Fix the remaining strict GitHub artifact failure from run `28990244296`.

## Files changed

- `nirs4all/tests/e2e/test_pipeline_generation_performance.py`
- `nirs4all` submodule pin
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`

## Decision

The best-of-3 timing strategy removed single-sample noise, but the CI workload
was still too small to reliably measure dag-ml's batch benefit: run
`28990244296` measured `legacy_over_dag_ml_ratio=0.959`. The E2E-only
performance candidate now expands the zipped PLS workload to nine generated
variants. The strict checker remains unchanged: it still requires
`performance.verdict == "dag_ml_faster"` and `legacy_over_dag_ml_ratio > 1`.

## Validation

- `nirs4all`: `python3.11 -m py_compile tests/e2e/test_pipeline_generation_performance.py` -> OK.
- `nirs4all`: `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/e2e/test_pipeline_generation_performance.py::test_generate_family --artifacts-dir=/tmp/n4a-perf-debug/amplified` -> passed, `legacy_over_dag_ml_ratio=3.1764`.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-performance-amplified run e2e-pipeline-generation-performance-compare --execute && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-performance-amplified evidence --scenario e2e-pipeline-generation-performance-compare` -> passed.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py run e2e-pipeline-generation-performance-compare --execute && python3.11 scripts/n4a_e2e_scenarios.py evidence --ready-only && python3.11 scripts/n4a_e2e_scenarios.py evidence-ledger --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json` -> `11/11 scenarios verified; artifacts=70 failures=0`.
- `nirs4all-ecosystem`: `python3.11 -m pytest -q` -> 168 passed.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_release_surface_matrix.py validate` -> passed.

## Risks

- The full GitHub strict run still needs to be relaunched after this repin is
  pushed.
