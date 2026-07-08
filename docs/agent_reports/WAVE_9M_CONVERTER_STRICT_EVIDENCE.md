# Wave 9M - Converter Strict Evidence

Date: 2026-07-08

## Scope

Promote `e2e-converter-legacy-save-predictions-web` from hybrid to strict for
its declared migration scope: legacy-save conversion, prediction lowering,
Python oracle rerun, and client-side Web result rendering.

## Files Modified

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/CROSS_LANGUAGE_E2E.md`
- `tests/test_e2e_scenarios.py`

## Tests Run

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `NIRS4ALL_UI_SHIM_ROOT=/tmp/n4a-clean-ui-origin python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-converter-strict run e2e-converter-legacy-save-predictions-web --execute`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-converter-strict evidence --scenario e2e-converter-legacy-save-predictions-web --json`

## Result

- Coverage now reports `strictness_gaps=9`.
- Scenario evidence levels are now `hybrid=9`, `strict=2`.
- The converter scenario verified 6 artifacts with 0 failures:
  `converted-workspace.n4a.json`, `predictions.rt_result.json`,
  `python-open-pipeline.json`, `python-rerun-pipeline.json`,
  `web-results-panels.json`, and `web-results.png`.

## Decisions

- Paper export and repository forced-best-refit remain `not_applicable` for this
  migration lane instead of being counted as strictness debt.
- No legacy `nirs4all-lite` alias is introduced or preserved. The only legacy
  surface here is the explicit migration input handled by `nirs4all-tools`.

## Risks

- This does not claim full ecosystem parity. Five V1 phase cells remain
  `contract`, and nine scenarios remain hybrid.
- The local execution used a clean `/tmp/n4a-clean-ui-origin` checkout for the
  UI shim to avoid touching the concurrent dirty `nirs4all-ui` workspace.
