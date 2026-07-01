# W100 Studio/Web Runtime Integration Review

## Scope

Read-only review of Wave 2K Studio/Web runtime integration. I read the top-level `AGENTS.md`, `W95_STUDIO_STRICT_RUNTIME.md`, and `W96_RUNTIME_UX_E2E.md`; both W95 and W96 reports are present. I fact-checked:

- Studio W95: `_worktrees/W95-studio-strict-runtime` at `88fbd99`
- Studio W96: `_worktrees/W96-studio-runtime-e2e` at `a32fbb9`
- Web W96: `_worktrees/W96-web-runtime-e2e` at `f3ba05e`

I did not edit runtime repositories.

## Findings

### 1. Studio launch payloads cannot express W95's explicit fallback opt-in or requested engine

W95 correctly changes the backend contract to strict-by-default: `Run.allow_fallback`, `ExperimentConfig.allow_fallback`, and `QuickRunRequest.allow_fallback` default to `False`, while `engine` remains optional (`_worktrees/W95-studio-strict-runtime/api/runs.py:197-258`). `ExecutionRequest.allow_fallback` also defaults to `False`, and its metadata serializes `fallback_policy.mode` as `refuse_fallback` unless explicitly opted in (`_worktrees/W95-studio-strict-runtime/api/execution_driver.py:86-118`).

W96 Studio's frontend request types/builders have not been extended for that backend contract. `ExperimentConfig` has no `engine` or `allow_fallback` field (`_worktrees/W96-studio-runtime-e2e/src/types/runs.ts:247-271`), `QuickRunRequest` has neither field (`_worktrees/W96-studio-runtime-e2e/src/api/runs.ts:139-153`), and `buildExperimentLaunchConfig()` only emits name, datasets, pipeline ids, inline pipelines, grouping, and optionally `execution_backend` (`_worktrees/W96-studio-runtime-e2e/src/lib/experimentLaunchConfig.ts:84-98`). `createRun()` posts exactly `{ config }` (`_worktrees/W96-studio-runtime-e2e/src/api/runs.ts:126-128`).

Impact: after W95 is preserved in the merge, normal Studio launches will rely on backend defaults. That is strict for fallback, but they also cannot intentionally request `engine="dag-ml"` or `allow_fallback=true` from the UI/type surface. The W96 E2E scenario that shows `engine_requested: "dag-ml"` is therefore not reachable from the current Studio launch payload without an external/API client.

### 2. W96 Runs-page E2E mocks runtime fields that the workspace-store endpoints do not emit at run-summary level

W95 records runtime outcome fields on in-memory `PipelineRun`: `engine`, `engine_requested`, `engine_diagnostics`, `runtime_source`, `runtime_manifest`, `fallback_policy`, and `native_result_refs` (`_worktrees/W95-studio-strict-runtime/api/runs.py:142-162`). During execution, it sets `pipeline.engine_requested` and `pipeline.fallback_policy` before training (`_worktrees/W95-studio-strict-runtime/api/runs.py:1083-1092`), copies successful runtime records into the pipeline (`_worktrees/W95-studio-strict-runtime/api/runs.py:1133-1141`), and returns those fields from `_execute_pipeline_training()` (`_worktrees/W95-studio-strict-runtime/api/runs.py:1621-1634`). W95 tests only prove manifest/direct `/api/runs/{run_id}` behavior for these fields (`_worktrees/W95-studio-strict-runtime/tests/test_runs_engine_routing.py:639-709`, `_worktrees/W95-studio-strict-runtime/tests/test_runs_engine_routing.py:863-879`).

W96 Studio's UX consumes runtime status from workspace endpoints. The run card renders `<RuntimeEngineBadge source={run} />` (`_worktrees/W96-studio-runtime-e2e/src/components/runs/RunItem.tsx:245-269`), the detail header renders `<RuntimeEngineBadge source={detail ?? run} />` (`_worktrees/W96-studio-runtime-e2e/src/components/runs/RunDetailSheetHeader.tsx:81-103`), and pipeline detail renders both `<RuntimeEngineBadge source={pipeline} />` and `<RuntimeDiagnosticsList source={pipeline} />` (`_worktrees/W96-studio-runtime-e2e/src/components/runs/RunDetailPipelines.tsx:24-37`, `_worktrees/W96-studio-runtime-e2e/src/components/runs/RunDetailPipelines.tsx:83-84`).

The W96 E2E mock injects `engine`, `engine_requested`, and `engine_diagnostics` into `/workspaces/{id}/runs/enriched` and `/workspaces/{id}/runs/{run_id}` responses (`_worktrees/W96-studio-runtime-e2e/e2e/tests/runs-redesign.spec.ts:39-58`, `_worktrees/W96-studio-runtime-e2e/e2e/tests/runs-redesign.spec.ts:154-206`), then asserts the fallback badge and diagnostics (`_worktrees/W96-studio-runtime-e2e/e2e/tests/runs-redesign.spec.ts:417-434`).

The actual backend workspace-store summary builder does not emit those root runtime fields. `_build_run()` returns `run_id`, name/status, counts, datasets, error, config, and model classes only (`_worktrees/W95-studio-strict-runtime/api/store_enriched_runs.py:385-403`; W96 has the same code at `_worktrees/W96-studio-runtime-e2e/api/store_enriched_runs.py:385-403`). The detail path attaches sanitized store pipeline rows and log summaries, but does not synthesize root `engine`/`engine_requested`/`engine_diagnostics` from W95 run manifests or `config.fallback_policy` (`_worktrees/W95-studio-strict-runtime/api/store_adapter.py:519-573`, `_worktrees/W95-studio-strict-runtime/api/workspace/router_discovery.py:270-309`).

Impact: the W96 mocked E2E can pass while real completed workspace-store runs still show no run-card/header runtime badge. Pipeline-level display may work only if the underlying WorkspaceStore pipeline rows already contain those columns; I found no W95 Studio-side code adding those fields to the workspace-store schema.

### 3. W96 runtime badge extraction does not read W95's persisted fallback policy shape

W95 persists the policy as `{source, engine_requested, allow_fallback, mode}` (`_worktrees/W95-studio-strict-runtime/api/runtime_engine.py:191-198`) and includes it in store-run config (`_worktrees/W95-studio-strict-runtime/api/runs.py:1010-1019`). W96's `buildRuntimeEngineStatus()` only looks for direct/root candidates, metadata/runtime envelopes, manifest engine, and direct `engine_requested`/`requested_engine` keys (`_worktrees/W96-studio-runtime-e2e/src/ui/runtime/resultMetadata.ts:102-110`, `_worktrees/W96-studio-runtime-e2e/src/ui/runtime/resultMetadata.ts:235-282`). The W96 enriched-run type's config shape includes `engine`, but not `requested_engine` or `fallback_policy` (`_worktrees/W96-studio-runtime-e2e/src/types/enriched-runs.ts:24-36`).

Impact: even when W95 stores `requested_engine`/`fallback_policy` under run config, W96's display helper will not infer "Requested DAG-ML" or strict/refuse policy from that persisted config. This reinforces finding 2.

### 4. Studio/Web default fallback semantics diverge by surface

W95 Studio backend strictness is explicit: the dag-ml attempt is forced to `allow_fallback=False`, and only a structured `RtError` plus caller `allow_fallback=True` triggers an explicit legacy rerun (`_worktrees/W95-studio-strict-runtime/api/runs.py:1508-1535`).

W96 Web still defaults browser runtime fallback to allowed. `RunOptions.allowFallback` documents omitted/default as `true` (`_worktrees/W96-web-runtime-e2e/studio-lite/src/engine/types.ts:282-289`), `App.tsx` calls `engine.run()` without `allowFallback` (`_worktrees/W96-web-runtime-e2e/studio-lite/src/app/App.tsx:230-243`), the worker forwards an undefined flag (`_worktrees/W96-web-runtime-e2e/studio-lite/src/engine/worker-engine.ts:112-117`), and the RtResult envelope records `allow_fallback: opts.allowFallback ?? true` (`_worktrees/W96-web-runtime-e2e/studio-lite/src/engine/rt-result.ts:210-224`). Strict Web behavior is covered only when callers pass `allowFallback:false` (`_worktrees/W96-web-runtime-e2e/studio-lite/src/engine/dagml-engine.rt-fallback.test.ts:141-174`, `_worktrees/W96-web-runtime-e2e/studio-lite/src/engine/dagml-engine.rt-fallback.test.ts:179-208`).

Impact: this is not a merge conflict, but it is a product semantics divergence. Studio backend default is fail-closed; Web default is diagnosed fallback-allowed. If Wave 2K expects uniform "explicit fallback opt-in" across Studio and Web, W96 Web needs a follow-up.

### 5. E2E server environment is still contaminated on port 8000

W96 already reported the stock Studio Playwright command was blocked because port `8000` was occupied by a process returning `404` for `/api/health` (`nirs4all-ecosystem/docs/agent_reports/W96_RUNTIME_UX_E2E.md:74-83`). The checked-in Studio Playwright config still expects to start or reuse a backend at `http://localhost:8000/api/health` (`_worktrees/W96-studio-runtime-e2e/playwright.config.ts:126-140`). In this review, port `8000` was still occupied by `uvicorn` from `nirs4all-benchmarks`, not Studio. I found no tracked temporary W96 Playwright config in the Studio worktree.

Impact: rerunning the stock Studio Playwright suite without freeing/changing port `8000` is likely to reproduce W96's server failure. Do not treat a no-webServer/manual-Vite pass as equivalent to the post-merge stock E2E gate.

## Merge Notes

- W96 Studio is based before W95 and its own worktree still shows the old backend defaults (`allow_fallback=True` in `_worktrees/W96-studio-runtime-e2e/api/runs.py:197-258`). Its W96 commit changed only frontend/runtime test files (`a32fbb9`), while W95 changed backend/tests (`88fbd99`). The current `refactor/integration-studio` branch contains both W95 and W96 commits, so the expected merge result should preserve W95's backend defaults. Recheck this explicitly after any coordinator merge.
- W96 Web's commit only changes App error formatting and new runtime error tests; it does not change Web fallback defaults.

## Tests To Rerun After Merge

Studio:

- `rtk .venv/bin/python -m pytest tests/test_runs_engine_routing.py tests/test_runs_execution_backend.py tests/test_execution_driver.py -q`
- Add or rerun store/workspace coverage around `GET /workspaces/{id}/runs/enriched` and `GET /workspaces/{id}/runs/{run_id}` for runtime fields; existing W95 tests do not cover that contract.
- `npx vitest run src/components/runtime/RuntimeComponents.test.tsx src/ui/runtime/resultMetadata.test.ts src/lib/__tests__/runsPageData.test.ts src/hooks/useNewExperimentLaunchFlow.test.tsx`
- `npm run lint:tsc`
- After clearing/repointing port `8000`, rerun the stock Playwright path for `e2e/tests/runs-redesign.spec.ts` with the repository `playwright.config.ts`, not only a temporary no-webServer config.

Web:

- `npx vitest run --config vitest.config.ts src/app/runtimeErrors.test.ts src/engine/worker-engine.test.ts src/engine/dagml-engine.rt-fallback.test.ts src/engine/rt-result.goldens.test.ts`
- `npm run typecheck`
- `npm run build`
- With a clean served app URL, `SMOKE_URL=http://localhost:4345/ node tests/rt-fallback-smoke.mjs` from `studio-lite/`.
