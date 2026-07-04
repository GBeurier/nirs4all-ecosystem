# Wave 4BN - Ready E2E Batch Execution

## Scope

- Executed the current ready subset of the cross-language E2E manifest after adding `run-ready`.
- Did not run full parity; this was the medium batch gate requested before expensive parity runs.

## Command

- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-ready-4bm run-ready --execute`

## Result

- Exit code: `2`, expected because five scenarios remain blocked.
- Ready scenarios executed and produced declared artifacts:
  - `e2e-r-dataset-io-pipeline-save`
  - `e2e-wasm-open-repo-pipeline-parity-alt-dataset`
  - `e2e-dataset-provider-repository-roundtrip`
  - `e2e-cluster-dag-rights-client-core`
  - `e2e-formats-io-datasets-methods-language-bindings`
- Still blocked:
  - `e2e-python-reopen-paper-repository-refit`
  - `e2e-multimodal-python-r-wasm-roundtrip`
  - `e2e-multisource-branching-stacking-replay`
  - `e2e-converter-legacy-save-predictions-web`
  - `e2e-pipeline-generation-performance-compare`

## Artifact Check

- JSON artifacts under `/tmp/n4a-e2e-ready-4bm` were parsed with `python3.11 -m json.tool`.
- Non-JSON artifacts produced by the run included:
  - `/tmp/n4a-e2e-ready-4bm/wasm-repo-alt-dataset/web-results.png`
  - `/tmp/n4a-e2e-ready-4bm/formats-io-methods/methods-cross-binding-matrix.csv`
  - `/tmp/n4a-e2e-ready-4bm/formats-io-methods/orchestrator.log`
  - `/tmp/n4a-e2e-ready-4bm/formats-io-methods/r-gate-Makevars`

## Risks

- This is not a final green gate while the blocked scenarios remain blocked.
- The Web build emitted existing Vite chunk-size/browser-externalization warnings, but both Web smokes passed without console errors.
