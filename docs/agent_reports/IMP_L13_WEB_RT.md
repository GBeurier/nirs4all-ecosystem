# IMP-L13 — Web/WASM runtime error-envelope alignment (B-018, L13 slice)

**Agent:** IMP-L13 (implementation) · **Repo:** `nirs4all-web` · **Worktree:** `_worktrees/L13-web-rt` (`refactor/L13-web-rt`, base `745eef8`)
**Date:** 2026-06-30 · **Scope:** the **Web/WASM** slice of `B-018` only ("Web fallback silencieux … doivent devenir `RtError` explicite").
**Consumes:** `RT_spec.md` §RT-003 (error model), `SW8_RT_STUDIO_IMPL_spec.md` §5 (explicit fallback, V1), sync board `B-018`.

> No sibling repo, no sync board, no other report touched. Work confined to this worktree. The neutral
> `nirs4all-ecosystem/docs/contracts/runtime/rt_error.v1.schema.json` is **referenced** (the TS envelope mirrors it
> field-for-field) but **not authored here** — it lives in the ecosystem repo and is GOV-deferred per SW8 §2.4.

---

## 1. Problem (verified in-tree)

`DagMlEngine.runViaDagMl` (`studio-lite/src/engine/dagml-engine.ts`) had a **silent** degrade: when the dag-ml WASM
scheduler (`execute_campaign_phase_json`) threw, the `catch` quietly called `runChainOverFolds()` (the libn4m
fold chain) and continued. The returned `RunResult` still carried `lineage.executed: true` / `engine: 'dag-ml-wasm + libn4m'`,
so an unsupported/failed native path was **indistinguishable from a clean dag-ml execution**. A second, narrower silent
degrade existed in the model-only planning branch (`build_execution_plan_json` failure → `variants = [baseVariant]`,
dropping a configured sweep). The offline AOM/POP cost guard (`guard.ts`) already *threw*, but as an untyped `Error`.

## 2. Change (narrow, additive, UI-stable)

A small typed envelope + two instrumented fallback sites. **Default behavior is unchanged** (`allowFallback` defaults
`true`): the fallback still runs, but is now *recorded* and *surfaced* instead of silent. Opt-in strict mode
(`allowFallback: false`) **throws** a typed `RtErrorException` instead of degrading.

| File | Change |
|---|---|
| **`src/engine/rt.ts`** *(new)* | `RtError` v1 envelope (`verb`, `cause`, `message`, `mitigation?`, `unsupported_capability?`, `portable_level?`, `schema_version`, `detail?`) mirroring `rt_error.v1.schema.json`; `RtErrorException` carrier (a real `Error` that also carries `.rtError`); `makeRtError`, `rtErrorFromUnknown` (RT-003 cause classifier), `isRtErrorException` guard. Vocabulary **carried**, not redefined (DEC-RT-001 / CAP-004). |
| **`src/engine/rt.test.ts`** *(new)* | 9 focused vitest cases: envelope shape, cause classification (`unsupported_shape` / `unavailable_backend` / `invalid_request` / `runtime_error` default + override), `RtErrorException`/guard, and the guard refuse emitting a typed `RtError` with message preserved. |
| `src/engine/types.ts` | `RunResult.diagnostics?: RtError[]` and `RunOptions.allowFallback?: boolean` — both additive/optional. |
| `src/engine/dagml-engine.ts` | Collect `diagnostics[]` + `schedulerFallback` flag in `runViaDagMl`. Both fallback sites now: build an `RtError`; **throw `RtErrorException` when `allowFallback === false`**; else record the diagnostic. Scheduler fallback also flips `lineage.schedulerFallback` and attaches `RunResult.diagnostics`. Happy path is byte-for-byte unchanged (no diagnostics ⇒ field omitted). |
| `src/engine/dagml.ts` | `DagMlLineage.schedulerFallback?: boolean` (typed lineage marker). |
| `src/engine/guard.ts` | Main-thread AOM/POP refuse throws `RtErrorException` (`cause: 'unsupported_capability'`) **with the message string preserved verbatim** (existing UI + `guard.test.ts` unaffected). |
| `src/engine/worker-engine.ts` / `worker.ts` | Thread `allowFallback` into the worker payload; carry `rtError` across the worker `error` message so a strict-mode refusal is rebuilt as `RtErrorException` on the main thread (the served build runs the engine in a Worker, so the typed path survives the boundary). `RunResult.diagnostics` already crosses natively as cloned data. |
| `src/app/App.tsx` | One additive amber runtime-bar chip ("CV: libn4m fallback", with the diagnostic message/mitigation as `title`), rendered **only** when `lineage.schedulerFallback` — i.e. never on a clean run, so no existing smoke selector is affected. |

**Cause migration applied** (RT-003 table): scheduler failure → `runtime_error`/`unsupported_shape`; planning failure
→ `unsupported_shape`; AOM/POP guard → `unsupported_capability`.

## 3. Tests run (toolchain PATH per CLAUDE.md; `npm ci` in the fresh worktree)

| Gate | Command | Result |
|---|---|---|
| Targeted engine tests | `vitest run rt/guard/worker-engine/dagml/engine/main-engine` | **53 passed** |
| Full unit suite | `npm run test` | **99 passed (14 files)**, incl. new `rt.test.ts` (9) |
| Typecheck | `npm run typecheck` (`tsc --noEmit`, `strict`) | **exit 0** |
| Catalog | `npm run validate:catalog` | **exit 0** (warns the upstream methods ABI snapshot isn't reachable from a worktree path → validator self-skips; pre-existing/environmental, unrelated to this change) |
| Served build | `npm run build` | **exit 0** (the >4 MB chunk warning is pre-existing — the WASM bundles) |
| Offline build | `npm run build:single` | **exit 0** (exercises the main-thread `guard.ts` path that this change touches) |

`guard.test.ts` (unchanged, 9 cases) stays green — confirms the `Error → RtErrorException` swap preserved the
`/offline single-file/i` message contract.

## 4. Residual risks / deliberate scope boundaries

1. **Not converted: `orchestrate.ts:317-322` split swallow.** That `console.warn` lives in the **offline JS-orchestrated**
   `runPipeline` (StubEngine / `file://` path), not the dag-ml/WASM engine that B-018-web names. Converting it would
   require threading a diagnostics channel through `runPipeline`'s return shape (touches `StubEngine`). Left out to keep
   the change narrow; the **served** dag-ml path's own split (`dagml-engine.ts:249`) already *throws* (never swallows).
2. **Fallback path not exercised end-to-end in unit tests.** Triggering the real scheduler-failure branch needs staged
   dag-ml + libn4m WASM and a browser; the node vitest env can't. Mitigated by unit-testing the envelope, the cause
   classifier, and the typed guard directly. A browser smoke that forces a scheduler failure and asserts
   `RunResult.diagnostics` / the chip is a natural follow-up (`tests/*smoke.mjs`).
3. **Browser smokes not run here** (need Chromium + preview server). The UI addition is purely conditional on a
   fallback that clean pipelines never hit, so existing smoke selectors are unaffected by construction; both production
   builds compile.
4. **Contract file is referenced, not authored.** `rt.ts` field names match `rt_error.v1.schema.json`; freezing/
   publishing that ecosystem schema (and Python/Studio parity tests against it) is L10/GOV work in other repos — out
   of this worktree's scope.
5. **`portable_level` is carried but unused** by the web engine today (CAP-002 owns it); present for wire-parity only.

## 5. Review readiness

Self-contained, additive, default-behavior-preserving; full local gate green except the WASM/browser smokes (which
this TS-only change cannot regress). Ready for review. The worktree is left inspectable with the diff in place
(7 modified + 2 new files; `dist/`, `dist-single/`, `node_modules/` are gitignored).
