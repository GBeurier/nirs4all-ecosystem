# Wave 9N - Web Repository Forced Refit

Date: 2026-07-08

## Scope

Close the `repository_forced_best_refit` contract phase for
`e2e-wasm-open-repo-pipeline-alt-dataset` without touching `nirs4all`,
`nirs4all-studio`, or the dirty concurrent `nirs4all-ui` checkout.

## Files Modified

- `nirs4all-web/studio-lite/tests/fixtures/pipeline-repository/manifest.json`
- `nirs4all-web/studio-lite/tests/fixtures/pipeline-repository/repository-forced-best-refit.n4a.json`
- `nirs4all-web/studio-lite/tests/pipeline-repository-smoke.mjs`
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

## Tests Run

- `node --check tests/pipeline-repository-smoke.mjs`
- `npx vitest run --config vitest.config.ts src/components/pipeline/_helpers.test.ts`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `npm run build`
- `N4A_WEB_PYTHON=python3.11 ARTIFACTS_DIR=/tmp/n4a-e2e-wasm-repo-forced npm run smoke:pipeline-repository`
- `NIRS4ALL_UI_SHIM_ROOT=/tmp/n4a-clean-ui-origin python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-wasm-repo-forced run e2e-wasm-open-repo-pipeline-alt-dataset --execute`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-wasm-repo-forced evidence --scenario e2e-wasm-open-repo-pipeline-alt-dataset --json`

## Result

- `repository_forced_best_refit` is now strict for the Web/WASM repository
  scenario.
- Coverage now reports `v1_contract_phases=4`.
- Verified artifacts: `pipeline-repository-smoke.json`,
  `predict-artifact-smoke.json`, and `web-results.png`.
- The smoke records `repository_forced_best_refit.status=passed`,
  `source_repo=GBeurier/nirs4all-repository`, `force_best_refit=true`,
  descriptor SHA verification, selected pipeline id, recipe SHA verification,
  and dataset id matching.

## Decisions

- The scenario remains `hybrid`: it still uses a deterministic non-demo uploaded
  fixture dataset, not an external provider/catalog dataset.
- The repository forced-refit proof is a checked fixture contract, not a runtime
  call into production `nirs4all` or Studio.
- No `nirs4all-lite` compatibility alias was added or preserved.

## Risks

- One Web/WASM parity check remains `contract` because it is structural
  export/import evidence; numeric Python and source-vs-import comparisons remain
  strict.
- The local execute used `/tmp/n4a-clean-ui-origin` for the UI shim to avoid
  modifying the concurrent `nirs4all-ui` workspace.
