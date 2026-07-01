# W86 - Studio UI Runtime Components

Date: 2026-07-01

## Summary

Extracted reusable Studio frontend runtime/result UI primitives for engine status, run state presentation, runtime diagnostics, and native-results export affordances. Existing result and run screens now consume the shared components while preserving the prior visual structure.

## Changed Files

Repository/worktree: `/home/delete/nirs4all/_worktrees/W86-studio-ui-runtime`

- `src/components/runtime/NativeResultsExportAffordance.tsx`
- `src/components/runtime/RuntimeDiagnosticsList.tsx`
- `src/components/runtime/RuntimeEngineBadge.tsx`
- `src/components/runtime/RuntimeStatus.tsx`
- `src/components/runtime/index.ts`
- `src/components/runtime/RuntimeComponents.test.tsx`
- `src/hooks/useRuntimeResultPresentation.ts`
- `src/ui/runtime/resultMetadata.ts`
- `src/ui/runtime/resultMetadata.test.ts`
- `src/ui/runtime/index.ts`
- `src/ui/runtime/index.test.ts`
- `src/components/results/ResultDetailHeader.tsx`
- `src/components/results/ResultDetailMetricsTab.tsx`
- `src/components/results/ResultMetricsExportAction.tsx`
- `src/components/results/resultDetailData.ts`
- `src/components/results/resultDetailData.test.ts`
- `src/components/runs/PipelineDetailSheet.tsx`
- `src/components/runs/PipelineProgress.tsx`
- `src/components/runs/RunDetailPipelines.tsx`
- `src/components/runs/RunDetailSheetHeader.tsx`
- `src/components/runs/RunItem.tsx`
- `src/components/runs/StatusBadge.tsx`
- `src/types/enriched-runs.ts`
- `src/types/runs.ts`

## Commit

- `6211ab6 feat(runtime-ui): extract runtime result primitives`

## Verification

Run from `/home/delete/nirs4all/_worktrees/W86-studio-ui-runtime`:

- `rtk npx vitest run src/ui/runtime/index.test.ts src/ui/runtime/statusDisplay.test.ts src/ui/runtime/resultMetadata.test.ts src/components/runtime/RuntimeComponents.test.tsx src/components/results/resultDetailData.test.ts` - 5 files, 23 tests passed
- `rtk npm run lint:tsc` - passed
- `rtk npm run lint:eslint` - passed
- `rtk npm run lint:parallel` - passed
- `rtk npm run test:frontend` - 516 files, 3690 tests passed, 1 skipped
- `rtk git diff --check` - passed

## Failures / Notes

- Initial frontend test execution used the Windows `npm`/Node shim on PATH and failed before a meaningful run. Final Node commands sourced `~/.nvm/nvm.sh` and used Node 24.
- `npm ci` was required in the W86 worktree before frontend verification.
- A local `.venv` was created with Python 3.11 to try the full parallel test gate because the system `python3` run failed before collection on missing pytest plugins for `--timeout=120 -n auto`.

## Blockers

- `rtk npm run test:parallel` did not pass in this worktree after the frontend suite completed successfully. The backend pytest side failed in the local environment because scientific/runtime dependencies were not installed/importable, including `numpy`, `polars`, and `nirs4all`; the run summary reported `37 failed, 1515 passed, 26 skipped, 120 warnings, 67 errors`. No backend routing modules were edited by W86.
