# W87 Web Runtime V1

Date: 2026-07-01

Worker: W87

Repo/worktree: `/home/delete/nirs4all/_worktrees/W87-web-runtime-v1`

Branch: `refactor/W87-web-runtime-v1`

## Summary

Finalized the Studio-lite browser runtime cutover so the served browser/WASM path no longer silently drops to the direct compatibility runner when dag-ml is unavailable. Worker run replies now always include the neutral `RtResult` envelope, while strict/runtime refusals continue to cross the worker boundary as typed `RtError` payloads.

## Commit

- `825b7c2 fix(engine): fail closed on missing browser runtime`

## Changed Files

- `studio-lite/src/engine/main-engine.ts`
- `studio-lite/src/engine/main-engine.runtime-v1.test.ts`
- `studio-lite/src/engine/worker.ts`
- `studio-lite/src/engine/worker-engine.ts`
- `studio-lite/tests/rt-fallback-smoke.mjs`

## Verification

- `npm install`
- `npx vitest run --config vitest.config.ts src/engine/main-engine.runtime-v1.test.ts src/engine/worker-engine.test.ts src/engine/rt-result.goldens.test.ts src/engine/dagml-engine.rt-fallback.test.ts`
- `npm run typecheck`
- `npm run build`
- `CHROME=/usr/bin/google-chrome SMOKE_URL="http://localhost:4487/" node tests/rt-fallback-smoke.mjs`
- `npm run test`

## Failures / Blockers

- No test failures.
- No blockers.
- `npm install` reported existing npm audit vulnerabilities; no dependency changes were made for W87.
