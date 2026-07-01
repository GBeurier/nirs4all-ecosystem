# W77 - Web Runtime Cutover

## Summary

Advanced the Web/WASM runtime cutover by pinning the unsupported-shape diagnostic path to the same Python-published runtime fixture set used by `nirs4all.pipeline.dagml.rt`.

- Added the missing Web copy of Python's `rt_error.unsupported_shape.v1.json`.
- Extended `rt-result.goldens.test.ts` to compare shared RtError fixtures against Python sibling fixtures when present.
- Added a Web `RunResult -> RtResult` assertion proving unsupported-shape diagnostics project into `RtResult.diagnostics[]` as a detail-free RtError wire payload, with the Python runtime field shape and schema guards still enforced.

## Files Changed

- `studio-lite/src/engine/fixtures/runtime/rt_error.unsupported_shape.v1.json`
- `studio-lite/src/engine/rt-result.goldens.test.ts`

## Commit

- `1476653 test(studio-lite): pin unsupported rt diagnostics`

## Validation

- `npx vitest run --config vitest.config.ts src/engine/rt-result.goldens.test.ts src/engine/rt.contract.test.ts src/engine/dagml-engine.rt-fallback.test.ts src/engine/rt.test.ts src/engine/worker-engine.test.ts` - passed, 33 tests.
- `npm run typecheck` - passed.
- `npm run test` - passed, 121 tests.
- `npm run validate:catalog` - ran and self-skipped because the upstream `nirs4all-methods` ABI snapshot is not present at the validator's expected sibling path in this worktree layout.
- `npm run build` - passed, with existing Vite browser externalization and chunk-size warnings.
- `npm run build:single` - passed, with existing Vite browser externalization warnings.
- `SMOKE_URL="http://localhost:4345/" node tests/rt-fallback-smoke.mjs` - passed against served preview, no JS console errors.
- `git diff --check` - passed before commit.

## Notes

No runtime execution code changed. This is a bounded cutover/adoption gate: Web now consumes the same scheduler, strict-refusal, and unsupported-shape RtError fixtures as Python when the sibling checkout is available, and it proves unsupported diagnostics survive the Web `RtResult` projection without leaking in-memory-only fields.
