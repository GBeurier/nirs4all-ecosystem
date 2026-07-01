# W102 Studio/Web Runtime Contract Fix

## Status

Completed the Studio/Web runtime contract follow-up from W100.

## Implementation Commits

- Studio: `_worktrees/INT-studio` on `refactor/integration-studio`
  - `83aab1c18108a43f38d9940d9c929fedf7680526` (`fix(runtime): bridge Studio fallback contract`)
- Web: `_worktrees/INT-web` on `refactor/integration-web`
  - `ee8ea7a95946a0c5a84a57e5fab6a70f5bb90ce9` (`fix(studio-lite): require fallback opt-in`)

## Fact Check

- Confirmed W100 against the current integration worktrees, not the stale W95/W96 worktrees.
- Studio backend already had W95 strict defaults: `ExperimentConfig.allow_fallback`, `QuickRunRequest.allow_fallback`, and execution-driver metadata default to refusal.
- Studio frontend launch request/builders still lacked `engine` and `allow_fallback`.
- Workspace-store enriched summary/detail did not promote runtime status from persisted config or pipeline rows.
- Runtime badge extraction did not understand W95 persisted `config.requested_engine` / `config.fallback_policy`.
- Web omitted `allowFallback` still meant fallback allowed.

## Changes

Studio:

- Added frontend request/type support for `engine` and `allow_fallback` on `ExperimentConfig` and `QuickRunRequest`.
- Threaded optional `runtimeEngine` and `allowFallback` through launch config/payload builders and `useNewExperimentLaunchFlow`.
- Added store-runtime normalization in `api/store_adapter.py` that reads actual runtime fields from store rows and requested fallback policy from run config/metadata.
- Enriched workspace-store run summaries with `engine`, `engine_requested`, `engine_diagnostics`, `fallback_policy`, and `allow_fallback` when available or inferable.
- Enriched workspace-store run detail and pipeline rows with runtime request/policy hints so W96 UI badges can render real runtime status outside mocked E2E data.
- Updated runtime UI extraction to read `config.requested_engine`, `config.engine` as a request selector, and nested `config.fallback_policy`.

Web:

- Changed omitted `allowFallback` to strict fail-closed semantics.
- Preserved diagnosed fallback only for explicit `allowFallback: true`.
- Updated worker RtResult metadata, Web golden fixture, runtime fallback tests, and smoke script expectations.

## Verification

Studio:

- `rtk /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_store_adapter_enriched_runs.py tests/test_store_integration.py -q`
- `rtk /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runs_engine_routing.py tests/test_runs_execution_backend.py tests/test_execution_driver.py tests/test_store_adapter_enriched_runs.py tests/test_store_integration.py -q`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npx vitest run src/components/runtime/RuntimeComponents.test.tsx src/ui/runtime/resultMetadata.test.ts src/lib/__tests__/runsPageData.test.ts src/lib/__tests__/experimentLaunchConfig.test.ts src/lib/__tests__/experimentLaunchPayload.test.ts src/hooks/useNewExperimentLaunchFlow.test.tsx`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run lint:tsc`
- `ruff check api/store_adapter.py api/store_enriched_runs.py tests/test_store_adapter_enriched_runs.py tests/test_store_integration.py`
- `git diff --check`

Web:

- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npx vitest run --config vitest.config.ts src/engine/dagml-engine.rt-fallback.test.ts src/engine/rt-result.goldens.test.ts src/engine/worker-engine.test.ts src/app/runtimeErrors.test.ts`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run typecheck`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run build`
- `git diff --check`

## Notes

- `python -m ruff` was unavailable in the referenced Studio venv, so I used the global `ruff` binary.
- I did not rerun Studio Playwright; W100's port-8000 contamination note remains an environment issue outside this scope.
- No remaining code blockers.
