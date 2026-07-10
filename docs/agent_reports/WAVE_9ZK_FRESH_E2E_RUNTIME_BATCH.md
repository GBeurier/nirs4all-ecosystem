# Wave 9ZK - Fresh cross-language E2E runtime batch

Date: 2026-07-10

## Scope

- Refreshed runtime evidence for every ready cross-language E2E scenario.
- Covered Python/R/WASM/Web, datasets/IO, repository, papers, converter, predictions, cluster, multimodal and multisource workflows.
- Did not run the long full Python reference parity batch; this wave refreshes the orchestrated E2E evidence layer.

## Commands run

- `python3 scripts/n4a_e2e_scenarios.py run-ready --execute`
- `GITHUB_TOKEN="$(gh auth token)" python3 scripts/n4a_e2e_scenarios.py run --execute e2e-formats-io-datasets-methods-language-bindings`
- `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --max-age-seconds 14400`
- `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`

## Result

- Fresh runtime evidence: `11/11 scenarios verified; artifacts=71 failures=0`.
- The committed ledger check remains green: `11/11 scenarios verified; artifacts=71 failures=0`.
- The regenerated ledger had no tracked diff after verification.

## Scenario coverage refreshed

- `e2e-r-dataset-io-pipeline-save`
- `e2e-python-reopen-paper-repository-refit`
- `e2e-wasm-open-repo-pipeline-alt-dataset`
- `e2e-multimodal-python-r-wasm-roundtrip`
- `e2e-multisource-branching-stacking-replay`
- `e2e-converter-legacy-save-predictions-web`
- `e2e-dataset-provider-repository-roundtrip`
- `e2e-pipeline-generation-performance-compare`
- `e2e-cluster-dag-rights-client-core`
- `e2e-formats-io-datasets-methods-language-bindings`
- `e2e-core-ui-custom-app-host`

## Notable observations

- The first `run-ready --execute` pass completed the scenario work but stopped late in the MATLAB/Octave release-gate verifier because the GitHub API was rate-limited for anonymous requests.
- The repo-local `github_token` file did not authenticate this request; the verifier succeeded when rerun with the active `gh auth token`.
- Vite emitted the existing chunk-size and `node:module` browser externalization warnings during Web/WASM builds; no Web smoke failed.

## Risks / follow-up

- The fresh evidence is filesystem-local runtime evidence under `.n4a-e2e-artifacts/`; it is intentionally not committed.
- The full Python-reference parity batch remains the next heavier gate before claiming final non-regression.
