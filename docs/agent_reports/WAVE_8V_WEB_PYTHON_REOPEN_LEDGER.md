# Wave 8V - Web repository Python reopen/rerun ledger

## Scope

Reduced true V1 E2E debt for `e2e-wasm-open-repo-pipeline-alt-dataset` by making
the existing Web/WASM repository smoke emit strict Python reopen and rerun
evidence for the same repository descriptor, uploaded dataset fixture, and
dag-ml fold ledger.

## Files modified

- `nirs4all-web/studio-lite/tests/pipeline-repository-smoke.mjs`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/CROSS_LANGUAGE_E2E.md`

## Agent reviews

- Hume the 2nd reviewed the Web smoke diff. Finding: no blocker; requested
  byte-based descriptor hashing to avoid CRLF/text encoding mismatch. Fixed.
- Nietzsche the 2nd reviewed the ecosystem contract diff. Findings: producer
  needed to land with the contract, artifact requirements needed dataset/fold
  hash equality, and the step needed `python3.11` as an explicit tool. Fixed.

## Decisions

- Promoted `python_open_pipeline` and `python_rerun_pipeline` for the Web/WASM
  repository scenario from `gap` to `strict`.
- Added `equals_path` artifact validation so strict evidence can compare fields
  within an artifact instead of accepting arbitrary non-empty hashes.
- Kept `web.nirs4all.org` client-side-only: Python is still only an external
  smoke-test oracle; the browser probe continues to assert no Python bridge,
  no Node process, and no backend API calls in the page.

## Tests run

- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH node --check studio-lite/tests/pipeline-repository-smoke.mjs`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run build`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH N4A_WEB_PYTHON=python3.11 ARTIFACTS_DIR=/tmp/n4a-web-e2e-ledger-v2/wasm-repo-alt-dataset npm run smoke:pipeline-repository`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH ARTIFACTS_DIR=/tmp/n4a-web-e2e-ledger-v2/wasm-repo-alt-dataset npm run smoke:predict-artifact`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json-out /tmp/n4a-e2e-web-python-ledger-v2.json --markdown-out /tmp/n4a-e2e-web-python-ledger-v2.md`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-web-e2e-ledger-v2 evidence --scenario e2e-wasm-open-repo-pipeline-alt-dataset`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `python3.11 -m pytest -q`
- `git diff --check` in `nirs4all-web` and `nirs4all-ecosystem`

## Result

Coverage debt now reports `v1_gap_phases=4` instead of `6`. Remaining true gaps:

- `e2e-converter-legacy-save-predictions-web`: `python_rerun_pipeline`
- `e2e-multimodal-python-r-wasm-roundtrip`: `python_open_pipeline`
- `e2e-multisource-branching-stacking-replay`: `python_open_pipeline`
- `e2e-pipeline-generation-performance-compare`: `python_open_pipeline`

## Risks

- The strict Python evidence covers the deterministic repository fixture and
  non-demo uploaded CSV dataset, not a live external provider/catalog dataset.
  That remaining limitation stays in `strictness_gaps`.
