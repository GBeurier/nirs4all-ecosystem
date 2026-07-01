# W26 report - Web runtime adoption

Summary:
Continued B-018 for nirs4all-web by adding served-browser coverage for runtime fallback semantics. The served `rt-fallback` smoke now keeps the clean UI invariant and also drives the real built module worker directly to force a scheduler failure, proving both loud fallback diagnostics and strict `allowFallback:false` refusal across the worker protocol.

Code changed:
- Added a loopback-only BroadcastChannel fault hook in `studio-lite/src/engine/dagml.ts` for served smoke failure injection.
- Wired the hook into dag-ml variant planning and scheduler execution in `studio-lite/src/engine/dagml-engine.ts`.
- Expanded `studio-lite/tests/rt-fallback-smoke.mjs` to locate the built worker asset, run forced scheduler fallback, assert `RunResult.diagnostics`, and assert typed `RtErrorException` when `allowFallback:false`.
- Updated the focused fallback test header to document the new served browser coverage.

Files touched:
- `studio-lite/src/engine/dagml.ts`
- `studio-lite/src/engine/dagml-engine.ts`
- `studio-lite/src/engine/dagml-engine.rt-fallback.test.ts`
- `studio-lite/tests/rt-fallback-smoke.mjs`

Commits:
- `d501734` - `test(studio-lite): cover served rt fallback failures`

Tests run:
- `npm run typecheck` - pass
- `npx vitest run --config vitest.config.ts src/engine/dagml-engine.rt-fallback.test.ts` - pass
- `node --check tests/rt-fallback-smoke.mjs` - pass
- `npm run build` - pass
- `node scripts/run-smokes.mjs rt-fallback` - pass
- `npm run test` - pass, 115 tests
- `npm run validate:catalog` - exited 0, skipped enforcement because the upstream nirs4all-methods ABI snapshot is not present in this worktree
- `npm run build:single` - pass
- `node scripts/run-smokes.mjs` - pass, all 23 served smokes

Tests not run and why:
None for the requested Web gate. Catalog ABI enforcement could not run because the snapshot is absent from the W26 web worktree; the validator reported the skip and exited cleanly.

Blockers:
None.

Impact on blockers/locks:
B-018 Web runtime fallback semantics are harder to regress: served Chromium now covers clean native execution, forced scheduler fallback diagnostics, and strict no-fallback behavior through the production worker protocol.

Next action:
No W26 follow-up required before integration review. Future work could add a planning-failure variant to the served smoke if W27/W28 need browser coverage for variant search refusal specifically.

Sync doc updated: no
