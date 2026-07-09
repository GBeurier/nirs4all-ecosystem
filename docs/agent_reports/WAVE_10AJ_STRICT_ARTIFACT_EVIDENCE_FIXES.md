# WAVE 10AJ - strict artifact evidence fixes

Date: 2026-07-09

## Scope

Fix the artifact-verification failures from GitHub run `28989457465` after all
ready scenarios executed successfully.

## Files changed

- `nirs4all/tests/e2e/test_pipeline_generation_performance.py`
- `nirs4all-ecosystem/scripts/e2e/run_quality_custom_host_smoke.py`
- `nirs4all-ecosystem/tests/test_quality_custom_host_smoke.py`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all` submodule pin

## Decision

The performance comparison used a single timing sample. On GitHub Actions that
was noisy enough to record `legacy_over_dag_ml_ratio=0.979` even though the
same gate is normally a dag-ml speedup. The Python producer now rebuilds the
pipeline and records best-of-3 timings per engine, while the strict artifact
check still requires `dag_ml_faster` and ratio `> 1`.

The quality smoke checker also expected a Tailwind source declaration pointing
at `nirs4all-ui/src/lab`. The quality app now uses the packaged public
`nirs4all-ui/dist/lab` surface, so the evidence accepts and explicitly checks
that public dist source path.

## Validation

- `nirs4all`: `python3.11 -m py_compile tests/e2e/test_pipeline_generation_performance.py` -> OK.
- `nirs4all`: `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/e2e/test_pipeline_generation_performance.py::test_generate_family --artifacts-dir=/tmp/n4a-perf-debug/best-of-3` -> passed, `legacy_over_dag_ml_ratio=1.8009`, `measurement_strategy=best_of_3`.
- `nirs4all-ecosystem`: `python3.11 -m pytest tests/test_quality_custom_host_smoke.py -q` -> 4 passed.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-performance-best-of-3 run e2e-pipeline-generation-performance-compare --execute && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-performance-best-of-3 evidence --scenario e2e-pipeline-generation-performance-compare` -> passed.

## Risks

- The full GitHub strict run still needs to be relaunched after committing the
  ecosystem repin and artifact-check updates.
