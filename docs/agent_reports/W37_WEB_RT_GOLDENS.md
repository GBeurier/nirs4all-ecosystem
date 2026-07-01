# W37 report - Web runtime goldens

Summary:
W37 added Web-side runtime golden coverage for `RtResult`/`RtError` projection. The Web client now pins success envelopes, scheduler fallback diagnostics, and `allowFallback=false` refusal behavior against runtime fixtures.

Code changed:
- Added runtime fixture envelopes for Web.
- Added golden tests for `RunResult -> RtResult`, scheduler fallback envelope, and `RtError` wire projection.
- Covered typed refusal behavior when fallback is disabled.

Files touched:
- `studio-lite/src/engine/rt-result.ts`
- `studio-lite/src/engine/rt-result.goldens.test.ts`
- `studio-lite/src/engine/fixtures/runtime/*`

Commits:
- `nirs4all-web/refactor/W37-rt-goldens` `02a3570`
- Integrated into `nirs4all-web/refactor/integration-web` as `94ccc66`

Tests run:
- `npx vitest run --config vitest.config.ts src/engine/rt-result.goldens.test.ts src/engine/rt.contract.test.ts src/engine/dagml-engine.rt-fallback.test.ts src/engine/worker-engine.test.ts` -> `21 passed`.
- `npm run typecheck` -> passed.
- `npm run build` -> passed with existing chunk-size warnings.

Impact:
Advances `B-018` with cross-language runtime result/error fixture coverage on the Web side.

Next action:
Add matched Python/Studio fixtures and cutover assertions so runtime error/fallback semantics are verified end to end.

Sync doc updated: yes
