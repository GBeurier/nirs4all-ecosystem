# W2L Lane H Studio/Web Runtime

## Agent

Codex Lane H Studio/Web runtime UX post-reset.

## Lane

H - `nirs4all-studio` and `nirs4all-web` review, with report-only write in `nirs4all-ecosystem`.

## Files modified

- `nirs4all-ecosystem/docs/agent_reports/W2L_LANE_H_STUDIO_WEB_RUNTIME.md`

No Studio or Web source files were modified. I did not touch `nirs4all-drafts`, `nirs4all-lab`, `nirs4all` core, or release lock files.

## Evidence

- Current reset checkouts are clean:
  - `nirs4all-studio` `main` at `2ccbf68e03a7`
  - `nirs4all-web` `main` at `745eef89406e`
- W2K integration heads are clean:
  - `_worktrees/INT-studio` `refactor/integration-studio` at `83aab1c18108`
  - `_worktrees/INT-web` `refactor/integration-web` at `ee8ea7a95946`
- The integration heads are not ancestors of current `main`:
  - `git merge-base --is-ancestor 83aab1c18108a43f38d9940d9c929fedf7680526 HEAD` in Studio returned exit code 1.
  - `git merge-base --is-ancestor ee8ea7a95946a0c5a84a57e5fab6a70f5bb90ce9 HEAD` in Web returned exit code 1.
- Current `main..INT` diffs are broad:
  - Studio: `76 files changed, 5126 insertions(+), 484 deletions(-)`
  - Web: `27 files changed, 2349 insertions(+), 24 deletions(-)`
- Studio ancestry path from current `main` to `INT-studio` includes the runtime foundation plus W95/W96/W102:
  - `155678b feat(studio): add runtime error envelope`
  - `5cb98f2 feat(studio): record runtime engine/fallback/RtError + manifests route`
  - `83b0580 test(studio): prove requested engine run routing`
  - `455e1f3 fix(runs): preserve requested engine on retry`
  - `69f576a fix(runs): preserve runtime engine route metadata`
  - `8654ea7 refactor(ui): extract runtime status display helpers`
  - `96f9239 fix(runs): accept mapping runtime result envelopes`
  - `0e2282a fix(runtime): persist structured Studio runtime outcomes`
  - `1979b72 feat(runtime-ui): extract runtime result primitives`
  - `a32fbb9 test(runtime): cover Studio fallback UX` (W96)
  - `88fbd99 fix(runtime): require explicit fallback opt-in` (W95)
  - `83aab1c fix(runtime): bridge Studio fallback contract` (W102)
- Current Studio `main` has no matches for `allow_fallback`, `engine_requested`, `fallback_policy`, `RuntimeEngineBadge`, or `buildRuntimeEngineStatus` under `api`, `src`, and `tests`.
- Current Studio `main` request models/builders are pre-runtime-contract:
  - `api/runs.py` `ExperimentConfig` has `execution_backend` but no `engine` or `allow_fallback`.
  - `api/runs.py` `QuickRunRequest` has no `engine` or `allow_fallback`.
  - `src/types/runs.ts` `ExperimentConfig` has no `engine` or `allow_fallback`.
  - `src/lib/experimentLaunchConfig.ts` and `src/lib/experimentLaunchPayload.ts` cannot emit runtime engine/fallback policy.
- W102 Studio is not a standalone patch against current `main`: it modifies `src/ui/runtime/resultMetadata.ts` and related runtime display/tests introduced by earlier commits, and enriches store output with fields whose source contracts are introduced before W95/W96/W102.
- Web ancestry path from current `main` to `INT-web` includes the runtime foundation plus W96/W102:
  - `488176b feat(web): surface runtime fallback errors`
  - `5cc8d8c feat(web): align RtError wire form with W7 runtime contract`
  - `1a1bdba test(web): add reliable runtime fallback smoke gate`
  - `d501734 test(studio-lite): cover served rt fallback failures`
  - `02a3570 test(studio-lite): add runtime result goldens`
  - `a7b98bd test(studio-lite): pin cross-runtime rt fixtures`
  - `77eec0e test(studio-lite): gate runtime fixtures through worker`
  - `b498159 test(studio-lite): pin unsupported rt diagnostics`
  - `60a0967 fix(engine): fail closed on missing browser runtime`
  - `f3ba05e fix(studio-lite): render typed runtime errors` (W96)
  - `ee8ea7a fix(studio-lite): require fallback opt-in` (W102)
- Current Web `main` has no matches for `allowFallback`, `RtError`, `rt-result`, `schedulerFallback`, or `runtimeErrors` under `studio-lite/src` and `studio-lite/tests`.
- Current Web `main` `RunOptions` only has `onProgress` and `signal`; W102's strict `allowFallback` semantics depend on runtime-error and RtResult files absent from current `main`.

Decision: do not patch Studio/Web source in this lane. The requested W95/W96/W102 fixes are absent, but they are not cleanly bounded on the reset checkouts. Porting only the final commits would create a partial runtime contract without the source files and telemetry contracts that W102 depends on.

## Tests/gates run

Studio:

- `rtk .venv/bin/python -m pytest tests/test_runs_execution_backend.py -q`
  - Passed: 37 tests.
- `env "PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH" rtk npx vitest run src/lib/__tests__/experimentLaunchConfig.test.ts src/lib/__tests__/experimentLaunchPayload.test.ts src/hooks/useNewExperimentLaunchFlow.test.tsx`
  - Passed: 3 files, 21 tests.

Web:

- `env "PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH" rtk npm run typecheck`
  - Passed (`tsc --noEmit`).
- `env "PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH" rtk npm run test`
  - Passed: 13 files, 90 tests.

Notes:

- Initial Node test invocations failed before running because `$PATH` contained unquoted Windows entries with spaces. The same commands were rerun with `env "PATH=..."` and passed.
- I did not run Studio Playwright. W96/W100's port-8000 contamination risk remains relevant before treating stock Playwright as a gate.

## Risks

- Current reset `main` branches lack the runtime contract surface that W95/W96/W102 assume. A cherry-pick of only W95/W96/W102 would either conflict or leave incomplete behavior.
- Studio store-runtime enrichment in W102 depends on earlier runtime persistence and UI extraction commits. Applying only the store summary code would expose fields that current route execution does not reliably populate.
- Web strict fallback opt-in in W102 depends on the typed `RtError`, `RtResult`, worker envelope, and runtime-error UI introduced by earlier Web runtime commits.
- If integration is delayed, Studio/Web `main` remain divergent from the strict fallback policy described in W100/W102. They are not "permissive with W102 missing"; they are mostly pre-contract.

## Decisions needed

- Decide whether Lane H should integrate the full W2K runtime chains from `INT-studio` and `INT-web`, not just W95/W96/W102.
- If the coordinator wants a reduced integration, define a new minimal runtime contract for reset `main`; the existing W102 patches are not the right minimal unit.
- Decide whether Studio Playwright should be rerun after freeing/repointing port `8000`, as W96/W100 reported contamination from another service.

## Recommended integration steps

1. Review `main..INT-studio` as a runtime stack, not as isolated W95/W96/W102 commits. Prefer merging or rebasing `refactor/integration-studio` after review, or cherry-pick the ancestry path in order from `155678b` through `83aab1c`.
2. Review `main..INT-web` similarly. Prefer merging or rebasing `refactor/integration-web`, or cherry-pick the ancestry path in order from `488176b` through `ee8ea7a`.
3. After integration, rerun the W102 verification set:
   - Studio pytest: `tests/test_runs_engine_routing.py tests/test_runs_execution_backend.py tests/test_execution_driver.py tests/test_store_adapter_enriched_runs.py tests/test_store_integration.py`
   - Studio Vitest: `src/components/runtime/RuntimeComponents.test.tsx src/ui/runtime/resultMetadata.test.ts src/lib/__tests__/runsPageData.test.ts src/lib/__tests__/experimentLaunchConfig.test.ts src/lib/__tests__/experimentLaunchPayload.test.ts src/hooks/useNewExperimentLaunchFlow.test.tsx`
   - Studio: `npm run lint:tsc`, `ruff check` on changed backend files, and `git diff --check`
   - Web Vitest: `src/engine/dagml-engine.rt-fallback.test.ts src/engine/rt-result.goldens.test.ts src/engine/worker-engine.test.ts src/app/runtimeErrors.test.ts`
   - Web: `npm run typecheck`, `npm run build`, and `git diff --check`
4. Run Studio stock Playwright only after resolving the port-8000 issue. Then run the runtime UX spec with the repo `playwright.config.ts`, not a temporary no-webServer config.
