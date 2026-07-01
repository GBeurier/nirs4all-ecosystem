# Wave 3AJ - Studio/Web runtime result surfaces

Date: 2026-07-01
Lane: H - Studio UI / Web runtime UX

## Scope

Close two runtime-result propagation gaps without changing computation boundaries:

- Studio consumes `native_result_refs` in result artifact/detail helpers.
- Web `studio-lite` carries worker-posted `rtResult` on the returned `RunResult`.

## Commits

- `_worktrees/INT-studio` `fb64c10 fix(studio): surface native result refs`
- `_worktrees/INT-web` `0f50c25 fix(studio-lite): carry worker runtime result`

## Files Modified

Studio:

- `src/lib/resultArtifacts.ts`
- `src/lib/__tests__/resultArtifacts.test.ts`
- `src/components/results/resultDetailData.ts`
- `src/components/results/resultDetailData.test.ts`
- `src/types/runs.ts`

Web / studio-lite:

- `studio-lite/src/engine/worker-engine.ts`
- `studio-lite/src/engine/types.ts`
- `studio-lite/src/engine/worker-engine.test.ts`
- `studio-lite/src/engine/rt-result.goldens.test.ts`

## Decisions

- Studio normalizes `native_result_refs` / `nativeResultRefs` into `ResultArtifactRef`s with source `native-results`.
- Native result directories use kind `native_result`; runtime model artifacts keep their known kind such as `model`.
- Studio preserves raw native pointer metadata (`path`, `manifestPath`, `uri`, `backend`, native run id, content fingerprint) and does not dereference files or reimplement backend logic.
- Web keeps `rtResult` optional on `RunResult`; the worker facade attaches it only when a worker `run` response posts it and the result payload is an object.
- `predict` results remain unchanged because the worker only posts `rtResult` for `run`.

## Agents / Review

- Worker `Copernicus the 2nd` implemented the Studio patch.
- Reviewer `Anscombe the 2nd` re-reviewed Studio and returned GO.
- Worker `Hooke the 2nd` implemented the Web patch.
- Reviewer `Bernoulli the 2nd` re-reviewed Web and returned GO.

## Tests

Studio:

- `./node_modules/.bin/vitest run src/lib/__tests__/resultArtifacts.test.ts src/components/results/resultDetailData.test.ts src/ui/runtime/resultMetadata.test.ts` -> 31 passed.
- `./node_modules/.bin/tsc --noEmit` -> passed.
- `./node_modules/.bin/eslint src/lib/resultArtifacts.ts src/lib/__tests__/resultArtifacts.test.ts src/components/results/resultDetailData.ts src/components/results/resultDetailData.test.ts src/types/runs.ts` -> passed.
- `git diff --check` -> passed.

Web / studio-lite:

- `npx vitest run --config vitest.config.ts src/engine/worker-engine.test.ts src/engine/rt-result.goldens.test.ts` -> 12 passed.
- `npm run typecheck` -> passed.
- `git diff --check` -> passed.

## Risks

- Full Studio `lint:parallel` / `test:parallel` and Web full build/smoke gates were not run in this focused lane.
- Studio intentionally does not consume `rt_result` itself as an artifact surface in this patch, avoiding double counting with `native_result_refs`.
- Web direct/in-thread engine runs do not gain `rtResult`; this patch covers the worker boundary only.
