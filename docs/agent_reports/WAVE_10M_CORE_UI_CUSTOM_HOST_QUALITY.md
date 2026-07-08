# WAVE 10M - Core/UI Custom Host Quality Evidence

Date: 2026-07-08

## Scope

Closed the custom app host evidence gap for the V1 refactor by requiring:

- published downstream Vite host execution from `nirs4all@0.3.7`,
  `nirs4all-ui@0.1.8`, and `@nirs4all/methods@1.0.8`;
- real `runPortablePipeline` + `predictPortablePipeline` execution and bundled
  WASM evidence in `published-custom-host.json`;
- `nirs4all-quality` as a static client-side host using shared `nirs4all-ui`
  theme/brand assets and executing `nirs4all-core-wasm`.

## Files Modified

- `nirs4all-web/studio-lite/scripts/smoke-published-custom-host.mjs`
- `nirs4all-quality/app/vite.config.ts`
- `nirs4all-quality/app/src/engine/wasmEngine.ts`
- `nirs4all-quality/app/scripts/wasm-smoke.mjs`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/e2e/run_quality_custom_host_smoke.py`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`

## Tests Run

- `nirs4all-web/studio-lite`: `npm run smoke:published-custom-host`
- `nirs4all-quality/app`: `npm run typecheck`
- `nirs4all-ecosystem`: `python3.11 scripts/e2e/run_quality_custom_host_smoke.py --workspace-root /home/delete/nirs4all --artifacts-dir /tmp/n4a-quality-custom-host-final`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py coverage --json-out /tmp/n4a-e2e-quality-coverage.json --markdown-out /tmp/n4a-e2e-quality-coverage.md`
- `nirs4all-ecosystem`: `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem`: `ruff check scripts/e2e/run_quality_custom_host_smoke.py scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py`
- `git diff --check` in `nirs4all-quality`, `nirs4all-web`, and `nirs4all-ecosystem`

## Decisions

- Treat `@nirs4all/methods` as the explicit downstream runtime peer for published
  JavaScript/WASM custom hosts. `nirs4all` keeps optional peers, but the host smoke
  must install the runtime it executes.
- Use `nirs4all-quality` as an additional strict host proof rather than only a
  branded site proof: the smoke now requires `nirs4all-core-wasm`, RMSEP render,
  static preview, no Python backend, shared UI theme/brand evidence, and zero
  console errors.
- Keep the `quality` browser smoke focused on one PLS/WASM calibration path so it
  is a runtime proof, not a long variant benchmark.

## Risks

- `nirs4all-quality` still aliases sibling staged WASM packages from
  `nirs4all-web/studio-lite`; this is acceptable for the current workspace proof,
  but a future packaged quality app should consume published runtime packages
  directly.
- The custom-host tests prove current published npm versions and the local quality
  app, not a full Studio adoption of `nirs4all-ui`.
