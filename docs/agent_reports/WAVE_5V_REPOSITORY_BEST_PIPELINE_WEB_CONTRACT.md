# WAVE 5V - Repository Best-Pipeline Web Contract

Date: 2026-07-04

## Scope

- Closed the `wasm_web_reuse` gap for `e2e-python-reopen-paper-repository-refit` at contract level.
- Added a Web/WASM consumer for the real `repository-best-pipeline.json` wrapper produced by the Python + Papers lane.
- Kept the scenario `hybrid`: the Web step executes the imported handoff on an alternative uploadable fixture, not yet on the original Python 130x2151 dataset.

## Files Modified

- `nirs4all-web/studio-lite/src/components/pipeline/_helpers.ts`
- `nirs4all-web/studio-lite/src/components/pipeline/_helpers.test.ts`
- `nirs4all-web/studio-lite/tests/repository-best-pipeline-smoke.mjs`
- `nirs4all-web/studio-lite/package.json`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`

## Validation

- `cd nirs4all-web/studio-lite && npx vitest run --config vitest.config.ts src/components/pipeline/_helpers.test.ts` -> 19 passed.
- `cd nirs4all-web/studio-lite && npm run typecheck` -> passed.
- `cd nirs4all-web/studio-lite && npm run build` -> passed.
- `cd nirs4all-web/studio-lite && npm run check:ui-shim` -> passed.
- `cd nirs4all-web/studio-lite && npm run smoke:shared-ui-contract` -> 2 passed.
- `cd nirs4all-web/studio-lite && N4A_WEB_PYTHON=python3.11 N4A_REPOSITORY_EVIDENCE=../.../repository-best-pipeline.json ARTIFACTS_DIR=../.../python-paper-repository npm run smoke:repository-best-pipeline` -> passed.
- `cd nirs4all-ecosystem && python3 scripts/n4a_e2e_scenarios.py validate` -> OK, 10 scenarios.
- `cd nirs4all-ecosystem && python3 -m pytest -q tests/test_e2e_scenarios.py` -> 41 passed.

Smoke evidence:

- `.n4a-e2e-artifacts/python-paper-repository/web-repository-best-pipeline.json`
- `.n4a-e2e-artifacts/python-paper-repository/repository-best-pipeline-web-results.png`
- Status: `passed`
- Runtime: `dag-ml-wasm + libn4m`
- Prediction rows: 20
- Python oracle max absolute delta: `9.85878045867139e-13`

## Decisions

- `wasm_web_reuse` is now `contract`, not `strict`.
- The Web import path accepts the supported repository handoff subset: `StandardNormalVariate` + `PLSRegression`.
- The smoke still uses Python only as a test oracle; the Web app remains client-side only and verifies no backend API calls.

## Risks / Follow-Up

- Promote to `strict` only after the original Python scenario dataset is exported as a browser-uploadable artifact and Web/WASM reruns that exact data.
- Unsupported repository handoff classes fail fast instead of being silently dropped.
- Separate follow-up remains open for the `lite -> core` cross-repo state lock and PyPI/core/providers cockpit consistency.
