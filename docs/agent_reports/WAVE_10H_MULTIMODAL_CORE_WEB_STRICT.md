# WAVE 10H - multimodal core client-side strict evidence

## Scope

Promote `e2e-multimodal-python-r-wasm-roundtrip` from hybrid to strict for its
declared portable contract by adding real client-side `nirs4all-core`
JavaScript/WASM import evidence over the same multimodal pipeline and dataset
artifacts.

This does not claim full Studio shell rendering or native source-aware
multimodal execution. It proves reusable core runtime import, source slice
preservation, zero backend calls, and numeric parity within tolerance for the
dense-fused portable representation.

## Files modified

- `nirs4all-core/scripts/e2e/run_multimodal_roundtrip.py`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/CROSS_LANGUAGE_E2E.md`
- `nirs4all-ecosystem/docs/agent_reports/WAVE_10H_MULTIMODAL_CORE_WEB_STRICT.md`
- `nirs4all-ecosystem/nirs4all-core` submodule pointer

## Tests run

- `cd nirs4all-core && PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/test_run_multimodal_roundtrip_env.py -q`
  - `3 passed, 1 warning`
- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py validate`
  - `OK: 11 cross-language E2E scenarios`
- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/test_e2e_scenarios.py -q`
  - `129 passed`
- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-multimodal-strict run --execute e2e-multimodal-python-r-wasm-roundtrip`
  - passed
- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-multimodal-strict evidence --scenario e2e-multimodal-python-r-wasm-roundtrip --json`
  - `verified_count=1`, `artifact_count=9`, `failure_count=0`

## Evidence

`/tmp/n4a-e2e-multimodal-strict/multimodal-roundtrip/web-core-import.json`
records:

- `schema_version=n4a.e2e.multimodal_web_core_import.v1`
- `status=passed`
- `runtime=javascript_wasm`
- `client_side_only=true`
- `backend_api_calls=0`
- `capability_schema=nirs4all-core.capabilities.v1`
- `serialized_model_predict_surfaces=["javascript_wasm"]`
- `source_ids=["nir","sample_metadata"]`
- `source_slices=[[0,28],[28,32]]`
- `prediction_abs_max=8.881784197001252e-16` with `tolerance=1e-8`
- `predict_roundtrip_abs_max=0.0`

## Decisions

- Keep `languages` unchanged for this scenario: it proves JavaScript/WASM core
  runtime reuse, not a browser UI render.
- Mark `wasm_web_reuse` strict only for the reusable client-side core import
  phase, with acceptance text explicitly excluding a full Studio shell claim.
- Leave the multisource scenario as the only remaining hybrid scenario until
  source-aware `by_source` or external-corpus replay is implemented or split into
  separate strict scenarios.
- Advance the ecosystem `nirs4all-core` submodule pointer to the pushed core
  head that contains both the formats/IO core web import script and this
  multimodal web-core import evidence, so public GitHub checkouts plan the same
  paths as the local workspace.

## Risks

- The scenario still uses the portable dense-fused multimodal representation.
  Native source-aware multimodal runtime semantics remain outside this scenario.
- Browser shell/UI rendering remains covered by other Web/custom-host scenarios,
  not by this multimodal roundtrip.
