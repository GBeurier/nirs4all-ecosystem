# Wave 9P - Performance Web Strict Parity

Status: integrated and verified

Scope:
- `nirs4all`: performance E2E now emits a Python/dag-ml prediction oracle and a Web materialized dataset fixture.
- `nirs4all-web`: Studio-lite E2E hook can run an injected materialized dataset and selected generated pipeline in the browser/WASM runtime.
- `nirs4all-ecosystem`: `e2e-pipeline-generation-performance-compare` is promoted from hybrid/contract to strict Web numeric parity.

Files changed:
- `nirs4all/tests/e2e/test_pipeline_generation_performance.py`
- `nirs4all-web/studio-lite/src/app/App.tsx`
- `nirs4all-web/studio-lite/tests/performance-compare-smoke.mjs`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/nirs4all`
- `nirs4all-ecosystem/nirs4all-web`

Tests run:
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/e2e/test_pipeline_generation_performance.py::test_generate_family --artifacts-dir=/tmp/n4a-perf-strict/performance-compare`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH node --check tests/performance-compare-smoke.mjs`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH ARTIFACTS_DIR=/tmp/n4a-perf-strict/performance-compare npm run smoke:performance-compare`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run typecheck`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run build`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-perf-strict evidence --scenario e2e-pipeline-generation-performance-compare --json`

Evidence:
- Web/WASM imported the selected generated candidate and ran it on `dataset-web-oracle.json`.
- The browser runtime compared 59 refit predictions against the Python/dag-ml oracle.
- Observed max prediction delta: `0.00014333785557951728`.
- Enforced Web/WASM tolerance: `0.0005`.
- Ecosystem coverage now reports `strictness_gaps=8` and `v1_contract_phases=3`.

Decisions:
- Keep Python native parity at `1e-8`.
- Use a separate Web/WASM prediction tolerance of `5e-4`, below the existing cross-engine guard and enforced by the smoke.
- Treat Studio runtime validation as a separate production track; this scenario now claims strict client-side Web/WASM parity only.

Risks:
- The Web strict gate currently covers the selected generated candidate from this family, not every generated candidate variant.
- The browser smoke depends on Python only for reproducing the Python canonical hash of JSON artifacts.
