# W96 Studio/Web Runtime UX And E2E

## Status

Completed the W96 frontend runtime UX and smoke-coverage slice.

## Scope

- Studio worktree: `/home/delete/nirs4all/_worktrees/W96-studio-runtime-e2e`
- Studio branch: `refactor/W96-runtime-e2e`
- Studio commit: `a32fbb9` (`test(runtime): cover Studio fallback UX`)
- Web worktree: `/home/delete/nirs4all/_worktrees/W96-web-runtime-e2e`
- Web branch: `refactor/W96-runtime-e2e`
- Web commit: `f3ba05e` (`fix(studio-lite): render typed runtime errors`)

## Changed Files

Studio:

- `e2e/tests/runs-redesign.spec.ts`
- `src/components/runtime/RuntimeComponents.test.tsx`
- `src/ui/runtime/resultMetadata.test.ts`
- `src/ui/runtime/resultMetadata.ts`

Web:

- `studio-lite/src/app/App.tsx`
- `studio-lite/src/app/runtimeErrors.ts`
- `studio-lite/src/app/runtimeErrors.test.ts`

## Change

- Added Studio Playwright coverage for a mocked run using `engine=legacy`,
  `engine_requested=dag-ml`, and structured runtime diagnostics. The test now
  asserts the run card fallback badge and the run-detail pipeline diagnostics.
- Made the Studio native-results export affordance disabled when no native
  artifacts are attached, with focused pure-helper and component tests.
- Added Web runtime-error presentation for typed `RtErrorException` values so
  worker refusals render cause, message, mitigation, and missing capability
  without exposing in-memory `detail`.
- No Studio backend files, fallback defaults, request models, or `api/runs.py`
  were edited.

## Verification

Studio:

- `npx vitest run src/components/runtime/RuntimeComponents.test.tsx src/ui/runtime/resultMetadata.test.ts`
  - Passed: 7 tests.
- `npm run lint:tsc`
  - Passed.
- `npx playwright test e2e/tests/runs-redesign.spec.ts --config=playwright.w96.config.ts --project=web-chromium`
  - Passed: 2 tests.
- `git diff --check`
  - Passed.
- `git diff --cached --check`
  - Passed before commit.

Web:

- `npx vitest run --config vitest.config.ts src/app/runtimeErrors.test.ts src/engine/worker-engine.test.ts`
  - Passed: 6 tests.
- `npm run typecheck`
  - Passed.
- `npm run build`
  - Passed with existing Vite warnings about browser externalization/chunk size.
- `SMOKE_URL=http://localhost:4345/ node tests/rt-fallback-smoke.mjs`
  - Passed, including clean native badge, no spurious fallback chip, forced fallback diagnostics, and strict `RtErrorException` worker path.
- `git diff --check`
  - Passed.
- `git diff --cached --check`
  - Passed before commit.

## Failures And Blockers

- The stock Studio Playwright command first failed because the repo config tries
  to start `../nirs4all/.venv/bin/python main.py --no-reload`, but that venv is
  absent in this worktree layout. Port `8000` was already occupied by another
  process that returned `404` for `/api/health`, so the configured webServer
  could not reuse it. I did not stop or alter that external process.
- To keep the E2E verification practical and non-invasive, I ran the touched
  mocked spec against a manually started Vite server with a temporary
  no-webServer Playwright config, then removed the temporary config.
- No unresolved code blockers remain.

## Coordinator Follow-Up

- Coordinator integration is needed to merge the two W96 commits into the
  Studio and Web integration branches.
