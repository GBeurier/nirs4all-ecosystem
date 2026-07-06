# Wave 7D - RC5 Cross-Language E2E Execution

Date: 2026-07-06

## Scope

- Executed the ready cross-language/platform E2E batch after the RC5 release lock and coordination tags were published.
- This is not the long full-parity sweep; it is the executable ecosystem gate for complex pipelines, multimodal/multisource flows, Web/WASM, R, Python, IO/datasets, repository, papers, converter, cluster, methods, and the custom app host.

## Commands

- `python3 scripts/n4a_e2e_scenarios.py coverage`
- `python3 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-rc5-ready run-ready --execute`
- `python3 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-rc5-ready evidence`

## Results

- Coverage/readiness: `11/11 scenarios; ready=11 blocked=0`
- Languages covered: `python=11`, `r=4`, `javascript_wasm=8`, `web=5`
- Tags covered: `datasets=5`, `io=4`, `multimodal=1`, `multisource=1`, `papers=1`, `parity=10`, `pipeline=11`, `pipeline_generation=2`, `predictions=6`, `repository=3`, `web_results=5`, `workspace_save=6`
- Execution: all 11 ready scenarios completed successfully.
- Evidence verification: `11/11 scenarios verified; artifacts=47 failures=0`

## Scenario Evidence

- `e2e-r-dataset-io-pipeline-save`: 9 artifacts verified.
- `e2e-python-reopen-paper-repository-refit`: 5 artifacts verified.
- `e2e-wasm-open-repo-pipeline-alt-dataset`: 3 artifacts verified.
- `e2e-multimodal-python-r-wasm-roundtrip`: 5 artifacts verified.
- `e2e-multisource-branching-stacking-replay`: 3 artifacts verified.
- `e2e-converter-legacy-save-predictions-web`: 4 artifacts verified.
- `e2e-dataset-provider-repository-roundtrip`: 4 artifacts verified.
- `e2e-pipeline-generation-performance-compare`: 3 artifacts verified.
- `e2e-cluster-dag-rights-client-core`: 4 artifacts verified.
- `e2e-formats-io-datasets-methods-language-bindings`: 3 artifacts verified.
- `e2e-core-ui-custom-app-host`: 4 artifacts verified.

## Notable Gates

- Performance comparison: Python legacy/dag-ml parity passed; `dag_ml_faster` with `legacy_over_dag_ml_ratio=1.7534`.
- Web runtime: dag-ml WASM executed 60 CV predictions in `0.253s`.
- Custom app host: core/UI prediction parity passed with `max_abs_delta=2.786659791809143e-14` under `1e-5`.
- Cluster scheduler: local vs cluster numeric oracle passed with `abs_diff=0.0`.
- Methods binding parity: C++, Python, R, and WASM gates passed; Rust remains an archived binding and is reported as not a current release target.
- Converter/Web results: converted predictions rendered through the Web result components.

## Risks And Limits

- The long full-parity sweep was intentionally not launched in this batch.
- Studio production release remains held; this gate validates Web/WASM and shared UI contracts, not a full Studio production release.
- `nirs4all-core` PyPI, R-universe, and CRAN surfaces remain unresolved as tracked in the cockpit.
- `dag-ml`/`dag-ml-data` Python/npm/R binding registry surfaces remain planned/missing as tracked in the cockpit.
- The methods WASM gate used the local `build/emscripten` artifact because `emcc`/`EMSDK` was unavailable in this environment; the artifact digest was recorded by the gate.
