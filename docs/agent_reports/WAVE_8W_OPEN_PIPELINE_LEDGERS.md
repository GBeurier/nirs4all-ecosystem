# Wave 8W - Python Open Pipeline Ledgers

Date: 2026-07-07

## Scope

Reduced V1 cross-language E2E debt by promoting honest `python_open_pipeline`
coverage for:

- `e2e-multimodal-python-r-wasm-roundtrip`
- `e2e-multisource-branching-stacking-replay`
- `e2e-pipeline-generation-performance-compare`

The converter scenario remains a real `python_rerun_pipeline` gap because its
legacy fixture preserves already-computed predictions but does not contain the
features/fitted model material required for a true Python rerun.

## Files Modified

- `nirs4all/tests/e2e/test_multimodal_roundtrip.py`
- `nirs4all/tests/e2e/test_multisource_stacking_replay.py`
- `nirs4all/tests/e2e/test_pipeline_generation_performance.py`
- `nirs4all-core/scripts/e2e/run_multisource_stacking_replay.py`
- `nirs4all-web/studio-lite/tests/performance-compare-smoke.mjs`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/CROSS_LANGUAGE_E2E.md`

## Evidence Added

- Multimodal producer writes `multimodal-roundtrip/python-open-ledger.json`
  with scenario id, descriptor hash equality, name equality, source-count
  equality and dataset hash.
- Multisource producer writes `multisource-stacking/python-open-ledger.json`
  with scenario id, replay manifest hash, pipeline hash equality, branch/source
  identity, branch descriptor hash, and reopened manifest scenario identity.
- Performance producer writes `performance-compare/pipeline-candidate.n4a.json`,
  reopens it, and runs both legacy and dag-ml from the reopened descriptor
  derived from the real `generator_zip_paired` pipeline factory. The Web smoke
  copies `python_open_pipeline` into `python-vs-dagml.json`.

## Tests Run

- `cd nirs4all && python3.11 -m py_compile tests/e2e/test_multimodal_roundtrip.py tests/e2e/test_multisource_stacking_replay.py tests/e2e/test_pipeline_generation_performance.py`
- `cd nirs4all && python3.11 -m ruff check tests/e2e/test_multimodal_roundtrip.py tests/e2e/test_multisource_stacking_replay.py tests/e2e/test_pipeline_generation_performance.py`
- `cd nirs4all && PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/e2e/test_multimodal_roundtrip.py::test_generate_oracle --artifacts-dir=/tmp/n4a-e2e-open-batch/multimodal-roundtrip`
- `cd nirs4all && PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/e2e/test_multisource_stacking_replay.py --artifacts-dir=/tmp/n4a-e2e-open-batch/multisource-stacking`
- `cd nirs4all && PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/e2e/test_pipeline_generation_performance.py::test_generate_family --artifacts-dir=/tmp/n4a-e2e-open-batch/performance-compare`
- `cd nirs4all-core && python3.11 -m py_compile scripts/e2e/run_multisource_stacking_replay.py`
- `cd nirs4all-core && python3.11 scripts/e2e/run_multimodal_roundtrip.py --workspace-root /home/delete/nirs4all --artifacts-dir /tmp/n4a-e2e-open-batch/multimodal-roundtrip`
- `cd nirs4all-core && python3.11 scripts/e2e/run_multisource_stacking_replay.py --artifacts-dir /tmp/n4a-e2e-open-batch/multisource-stacking`
- `cd nirs4all-web && node --check studio-lite/tests/performance-compare-smoke.mjs`
- `cd nirs4all-web/studio-lite && npm run build`
- `cd nirs4all-web/studio-lite && ARTIFACTS_DIR=/tmp/n4a-e2e-open-batch/performance-compare npm run smoke:performance-compare`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py validate`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py coverage --json-out /tmp/n4a-e2e-after-open.json --markdown-out /tmp/n4a-e2e-after-open.md`
- `cd nirs4all-ecosystem && python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `cd nirs4all-ecosystem && python3.11 -m pytest -q`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-open-batch evidence --scenario e2e-multimodal-python-r-wasm-roundtrip`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-open-batch evidence --scenario e2e-multisource-branching-stacking-replay`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-open-batch evidence --scenario e2e-pipeline-generation-performance-compare`

## Review

- Agent review confirmed the converter `python_rerun_pipeline` gap must not be
  promoted without a runnable fixture containing spectra/features, targets,
  split ledger and a portable pipeline descriptor.
- Agent review confirmed multimodal and multisource can be promoted once the
  standalone `python-open-ledger.json` artifacts are required.
- Agent review requested that performance use the reopened descriptor for the
  actual legacy/dag-ml runs and that the descriptor come from the registered
  factory rather than hand-coded steps; implemented.
- Agent review requested a multisource reopened-manifest scenario id check;
  implemented and required by the ecosystem evidence verifier.

## Decisions

- `v1_gap_phases` is reduced from 4 to 1.
- `python_open_pipeline` now has `strict=7 contract=2 gap=0 not_applicable=2`.
- The only remaining V1 gap phase is converter `python_rerun_pipeline`.
- `nirs4all` producer changes are on the existing `refactor/L17-pyref` branch,
  not Python production `main`; this preserves the current production hold.

## Risks

- The converter gap is still real and needs a richer fixture before strict
  rerun coverage can be claimed.
- The performance Web smoke consumes a prebuilt/dist app; full Web build was run
  in this wave, but this is still not a full Studio runtime performance gate.
