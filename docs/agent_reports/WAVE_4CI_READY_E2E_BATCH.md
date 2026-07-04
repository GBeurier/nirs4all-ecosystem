# Wave 4CI - Ready E2E Batch

## Scope

- Executed all currently ready cross-language E2E scenarios after the multimodal lane was integrated.
- Kept full parity deferred; this was the ready-scenario batch gate, not the exhaustive Python-reference parity suite.

## Command

- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-ready-4ci run-ready --execute`

## Result

- Exit code: `2`, expected because one scenario still has missing entrypoints/runtime coverage and remains blocked by design.
- Ready scenarios executed:
  - `e2e-r-dataset-io-pipeline-save`
  - `e2e-python-reopen-paper-repository-refit`
  - `e2e-wasm-open-repo-pipeline-parity-alt-dataset`
  - `e2e-multimodal-python-r-wasm-roundtrip`
  - `e2e-converter-legacy-save-predictions-web`
  - `e2e-dataset-provider-repository-roundtrip`
  - `e2e-pipeline-generation-performance-compare`
  - `e2e-cluster-dag-rights-client-core`
  - `e2e-formats-io-datasets-methods-language-bindings`
- Still blocked:
  - `e2e-multisource-branching-stacking-replay`

## Artifacts Checked

- `/tmp/n4a-e2e-ready-4ci/python-paper-repository/reopened-result.json`
- `/tmp/n4a-e2e-ready-4ci/python-paper-repository/repository-best-pipeline.json`
- `/tmp/n4a-e2e-ready-4ci/python-paper-repository/paper-export.zip`
- `/tmp/n4a-e2e-ready-4ci/multimodal-roundtrip/core-roundtrip-evidence.json`
- `/tmp/n4a-e2e-ready-4ci/performance-compare/pipeline-family.json`
- `/tmp/n4a-e2e-ready-4ci/performance-compare/python-vs-dagml.json`
- `/tmp/n4a-e2e-ready-4ci/performance-compare/studio-web-runtime.json`
- `/tmp/n4a-e2e-ready-4ci/legacy-converter/web-results-panels.json`
- `/tmp/n4a-e2e-ready-4ci/formats-io-methods/binding-parity.json`
- `/tmp/n4a-e2e-ready-4ci/formats-io-methods/predictions-by-language.json`
- `/tmp/n4a-e2e-ready-4ci/wasm-repo-alt-dataset/web-results.png`
- `/tmp/n4a-e2e-ready-4ci/legacy-converter/web-results.png`

## Result Snapshot

- Python paper/repository artifact status: `passed`, with Python git head `ce08bd3d58ef`, zero-delta legacy vs dag-ml best/final predictions, and zero-delta reopened `.n4a` bundle predictions.
- Multimodal artifact status: `passed` for Python core, R, and JavaScript/WASM; max prediction delta was `8.881784197001252e-16` at tolerance `1e-8`.
- Performance artifact status: `passed`; Python legacy `2.9031906677410007s`, dag-ml `1.6272722887806594s`, ratio `1.784084131314254`, verdict `dag_ml_faster`.
- Web performance smoke executed `60` CV predictions in `0.255s`.
- Converted-predictions Web smoke rendered `4` client-side result panels with no console errors.
- Methods binding parity status: `pass` for C++/Python/R/WASM current targets; archived Rust remains recorded as non-release-target archive evidence, not a current binding gate.

## Notes

- The runner still returns non-zero while any scenario is blocked. This is intentional: `run-ready` cannot be used as a fake green until multisource/stacking replay has real entrypoints.
- Non-blocking warnings observed: Web chunk-size warnings, Polars category deprecations, and dependency deprecation warnings in cluster/IO smoke tests.
- The next real blocker is implementing `nirs4all/tests/e2e/test_multisource_stacking_replay.py` and `nirs4all-core/scripts/e2e/run_multisource_stacking_replay.py`; the old ignored Rust placeholder was removed from the contract.
