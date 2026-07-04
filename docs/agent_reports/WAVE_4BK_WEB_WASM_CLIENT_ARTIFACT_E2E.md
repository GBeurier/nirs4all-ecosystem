# WAVE 4BK - Web/WASM client artifact E2E

Date: 2026-07-04

## Scope

- Replaced non-existent Web/WASM `tests/e2e/*.spec.ts` references with real
  client-side smoke entrypoints in `nirs4all-web/studio-lite`.
- Converted `e2e-wasm-open-repo-pipeline-parity-alt-dataset` from blocked to
  executable as a browser-only artifact smoke.

## Integrated commit

- `nirs4all-web`: `a315cf8a34250240ec8e2bbaf8443265e784959c`
  - `test(web): add client artifact smoke entries`

## Files changed

### nirs4all-web

- `studio-lite/package.json`
- `studio-lite/tests/n4a-roundtrip-smoke.mjs`
- `studio-lite/tests/pipeline-repository-smoke.mjs`

### nirs4all-ecosystem

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`

## Tests run

- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run build`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH ARTIFACTS_DIR=/tmp/n4a-web-smoke npm run smoke:artifacts`
- `python3.11 scripts/n4a_e2e_scenarios.py run e2e-wasm-open-repo-pipeline-parity-alt-dataset --execute`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`

## Decisions

- Reused existing `.mjs` smoke architecture and `scripts/run-smokes.mjs`.
- Added artifact output only when `ARTIFACTS_DIR` is set:
  - `predict-artifact-smoke.json`
  - `pipeline-repository-smoke.json`
  - `web-results.png`
- The scenario wording was narrowed: this gate proves client-only artifact
  export/import/execution, not Python-vs-WASM numerical parity.

## Risks

- The smoke depends on stable visible labels in the Web UI.
- Vite still emits existing warnings about `node:module` externalization and
  large chunks; those warnings predate this gate and did not block the smoke.
