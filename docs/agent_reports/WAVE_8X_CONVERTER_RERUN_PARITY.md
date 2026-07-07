# Wave 8X - Converter Python Rerun Parity

Date: 2026-07-07

## Scope

- Close the last V1 E2E gap phase:
  `e2e-converter-legacy-save-predictions-web.python_rerun_pipeline`.
- Keep the proof honest: Python must run the current `nirs4all` reference,
  not synthesize a passing JSON.
- Leave `nirs4all-ui` untouched because another agent is editing it.

## Files Modified

- `nirs4all-tools`
  - `tests/e2e/test_legacy_save_predictions_web.py`
  - `tests/fixtures/legacy/old_workspace_mixed/run_predictions.json`
  - `tests/fixtures/legacy/old_workspace_mixed/runs/run-2024-legacy/pipeline-pls/manifest.yaml`
  - `tests/fixtures/legacy/old_workspace_mixed/rerunnable_pipeline.n4a.json`
  - `tests/test_real_golden_fixtures.py`
- `nirs4all-ecosystem`
  - `docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - `scripts/n4a_e2e_scenarios.py`
  - `tests/test_e2e_scenarios.py`
  - `docs/agent_reports/WAVE_8X_CONVERTER_RERUN_PARITY.md`

## Decisions

- Replaced the converter fixture's non-rerunnable target vector with a tiny
  deterministic PLS fixture whose lowered predictions can be reproduced by
  `nirs4all.run`.
- Added `python-rerun-pipeline.json` as real evidence produced by the tools
  E2E test after reopening converted metadata and rerunning through the local
  Python `nirs4all` checkout.
- Promoted `python_rerun_pipeline` for the converter scenario from `gap` to
  `strict`; ecosystem coverage now reports `v1_gap_phases=0`.
- Kept `papers_export` and `repository_forced_best_refit` outside this
  converter scenario; those are covered by the dedicated papers/repository
  lane.

## Validation

- `nirs4all-tools`: `PYTHONPATH=/home/delete/nirs4all/nirs4all PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_legacy_save_predictions_web.py --artifacts-dir=/tmp/n4a-legacy-converter-test`
- `nirs4all-tools`: `python3.11 -m pytest -q`
- `nirs4all-tools`: `python3.11 -m ruff check tests/e2e/test_legacy_save_predictions_web.py tests/test_real_golden_fixtures.py`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `nirs4all-ecosystem`: `python3.11 -m pytest -q`
- `nirs4all-web`: `npm run smoke:shared-ui-contract && npm run build && ARTIFACTS_DIR=/tmp/n4a-legacy-evidence/legacy-converter npm run smoke:converted-predictions`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-legacy-evidence evidence --scenario e2e-converter-legacy-save-predictions-web --json`

## Risks

- The full ecosystem runner still fails the Web step locally at
  `npm run check:ui-shim` because `nirs4all-ui` is dirty/behind from another
  agent's work. The Web rendering smoke passes when that drift guard is
  bypassed; no `nirs4all-ui` files were changed in this wave.
- The fixture is intentionally small and deterministic. It proves the
  converter/rerun contract, not broad model coverage.
