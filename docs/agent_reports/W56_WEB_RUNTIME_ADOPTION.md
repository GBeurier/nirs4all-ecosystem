# W56 - Web Runtime Adoption Gate

## Summary

Advanced B-018 by making the Web served worker path emit and validate Python-compatible runtime wire envelopes, not just static RT fixture projections.

- `worker.ts` can include a `rtResult` wire envelope beside successful `run` responses when the adoption smoke asks for it, produced with `runResultToRtResultEnvelope`.
- Typed worker failures now send `rtErrorToWire(...)`, so strict `allowFallback:false` errors cross the worker boundary without in-memory-only fields such as `detail`.
- `rt-fallback-smoke.mjs` now reads `python_rt_fixture_shape.v1.json` and asserts the served worker's `rtResult`/`rtError` keys against the Python fixture shape after a forced scheduler fallback.
- Offline `file://` smoke still covers the clean single-file path and verifies no fallback chip or console errors.

## Files Changed

- `studio-lite/src/engine/worker.ts`
- `studio-lite/src/engine/worker-engine.ts`
- `studio-lite/tests/rt-fallback-smoke.mjs`

## Validation

- `npx vitest run --config vitest.config.ts src/engine/rt.test.ts src/engine/rt.contract.test.ts src/engine/rt-result.goldens.test.ts src/engine/dagml-engine.rt-fallback.test.ts src/engine/worker-engine.test.ts` - passed, 31 tests.
- `npm run typecheck` - passed.
- `npm run build` - passed, with existing Vite/browser externalization and chunk-size warnings.
- `npm run build:single` - passed, with existing Vite browser externalization warnings.
- `SMOKE_URL="http://localhost:4345/" node tests/rt-fallback-smoke.mjs` - passed against served preview.
- `SMOKE_URL="file://$PWD/dist-single/index.html" node tests/rt-fallback-smoke.mjs` - passed.
- `npm run validate:catalog` - ran, self-skipped because the upstream `nirs4all-methods` ABI snapshot was not present at the validator's expected sibling path in this worktree layout.

## Blockers

No blockers for W56. The only incomplete optional gate is the catalog ABI enforcement self-skip noted above.
