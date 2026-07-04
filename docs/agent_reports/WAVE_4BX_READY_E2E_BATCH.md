# Wave 4BX - Ready E2E Batch

## Scope

- Executed all currently ready cross-language E2E scenarios after the Web converter, performance lane, native dag-ml artifact gate, and Web dag-ml runtime evidence gate were integrated.
- Kept full parity deferred; this was the ready-scenario batch gate, not the exhaustive Python-reference parity suite.

## Command

- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-ready-4bx run-ready --execute`

## Result

- Exit code: `2`, expected because three scenarios still have missing entrypoints and remain blocked by design.
- Ready scenarios executed:
  - `e2e-r-dataset-io-pipeline-save`
  - `e2e-wasm-open-repo-pipeline-parity-alt-dataset`
  - `e2e-converter-legacy-save-predictions-web`
  - `e2e-dataset-provider-repository-roundtrip`
  - `e2e-pipeline-generation-performance-compare`
  - `e2e-cluster-dag-rights-client-core`
  - `e2e-formats-io-datasets-methods-language-bindings`
- Still blocked:
  - `e2e-python-reopen-paper-repository-refit`
  - `e2e-multimodal-python-r-wasm-roundtrip`
  - `e2e-multisource-branching-stacking-replay`

## Artifacts Checked

- `/tmp/n4a-e2e-ready-4bx/performance-compare/pipeline-family.json`
- `/tmp/n4a-e2e-ready-4bx/performance-compare/python-vs-dagml.json`
- `/tmp/n4a-e2e-ready-4bx/performance-compare/studio-web-runtime.json`
- `/tmp/n4a-e2e-ready-4bx/legacy-converter/web-results-panels.json`
- `/tmp/n4a-e2e-ready-4bx/formats-io-methods/binding-parity.json`
- `/tmp/n4a-e2e-ready-4bx/formats-io-methods/predictions-by-language.json`
- `/tmp/n4a-e2e-ready-4bx/wasm-repo-alt-dataset/web-results.png`
- `/tmp/n4a-e2e-ready-4bx/legacy-converter/web-results.png`

## Notes

- Performance artifact status: `passed` for Python legacy/dag-ml and `passed_web_with_studio_hold` for Web/Studio runtime, with Studio explicitly `not_executed_prod_hold`.
- The dag-ml performance run now fails on legacy fallback, requires native result artifacts when `results_path` is requested, and the Web smoke verifies observed `dag-ml-wasm + libn4m` execution with `schedulerFallback=false`.
- Non-blocking warnings observed: Polars category deprecations, Web chunk-size warnings, and dependency deprecation warnings in cluster/IO smoke tests.
