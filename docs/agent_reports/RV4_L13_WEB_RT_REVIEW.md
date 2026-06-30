# RV4 — Review of the L13 Web/WASM RtError / fallback slice (B-018)

**Reviewer:** RV4 (read-only) · **Repo:** `nirs4all-web` · **Worktree:** `_worktrees/L13-web-rt` (`refactor/L13-web-rt`)
**Date:** 2026-07-01 · **Scope reviewed:** the 9 staged files in `git diff --cached` + `IMP_L13_WEB_RT.md`.
**Method:** direct file reads + staged diff; independently ran typecheck + the node-env unit suites. No CodeGraph-only conclusions. No source edited, nothing staged/unstaged/committed.

## Disposition: **APPROVE** (merge-ready; follow-ups are non-blocking)

The change is narrow, additive, and default-behavior-preserving. Every local gate I could run reproduces green and matches the IMP report exactly. All findings below are **Low / informational** — no correctness defect, no default-behavior regression, no broken test. The strict (`allowFallback:false`) and worker error-propagation paths are implemented correctly but rest on unit coverage of the envelope only (the end-to-end fallback needs WASM+browser, acknowledged by IMP).

---

## Validation evidence (independently reproduced)

| Gate | Command | Result |
|---|---|---|
| Typecheck (strict) | `tsc --noEmit` | **exit 0** |
| Targeted units | `vitest run rt.test.ts guard.test.ts worker-engine.test.ts` | **20 passed** (rt 9, guard 9, worker-engine 2) |
| Full unit suite | `vitest run` | **99 passed (14 files)** — matches IMP report |

- `guard.test.ts` (unchanged) stays green: `.toThrow(/offline single-file/i)` matches `RtErrorException` because it extends `Error` with `super(message)` → the message contract survived the `Error→RtErrorException` swap **verbatim** (the `mitigation` string is concatenated identically to the prior inline literal).
- Vocabulary checked against `RT_spec.md §RT-003` (l.177-178): the web `RtErrorCause` set `{unsupported_shape, unsupported_capability, unavailable_backend, invalid_request, runtime_error}` is an **exact** match; verbs match RT-001. Vocabulary is carried, not redefined (DEC-RT-001) — faithful.

## Focus-area verdicts

1. **Default behavior preservation — PASS.** `DagMlEngine.run(ds,dsl,opts:RunOptions={})` defaults `opts`, and both fallback sites gate strict mode on `opts.allowFallback === false` (strict equality): `undefined`/omitted/`true` all keep the existing fallback. Grep confirms **nothing in production/UI ever sets `allowFallback:false`** — only the type definition, the worker plumbing, and the two `=== false` checks reference it. The compute in both sites is unchanged (`runChainOverFolds()` / `variants=[baseVariant]`); only `diagnostics[]` + the `schedulerFallback` flag are added, and `diagnostics` is omitted via a conditional spread on clean runs.
2. **Strict `allowFallback=false` — PASS.** Both sites `throw new RtErrorException(rtError)` before degrading. Threaded end-to-end: `WorkerEngine.run` → payload `allowFallback` → `worker.ts` opts → `MainEngine.run` (l.39) → `DagMlEngine`. At the scheduler site, `signal?.aborted` is checked **before** the strict/rtError logic (l.544), so a cancel is never misclassified as a fallback.
3. **Worker error propagation — PASS (correct, untested).** `worker.ts:48` posts `rtError` using `isRtErrorException(e)` on the **original** caught value `e` (correct — `err` is only the name/message normalization; no variable-mismatch bug). `WorkerEngine` (l.69) rebuilds `new RtErrorException(m.rtError)` with the right precedence (rtError before AbortError/Error). `RtError` is plain string/number data → structured-clone-safe. AbortError path is untouched (a `DOMException` isn't an `RtErrorException` → `rtError` undefined → name-based rebuild). See F2 for the coverage gap.
4. **Diagnostics / lineage schema — PASS with parity caveat (F1).** `RunResult.diagnostics?` and `DagMlLineage.schedulerFallback?` are additive/optional; `rt.ts` is dependency-free (no circular import; `types.ts → rt.ts` one-way).
5. **UI conditionality — PASS.** `schedulerFallback = lineage?.schedulerFallback ? selectedRun?.diagnostics?.[0] ?? true : null` is `null` on every clean run, and the chip is `!running && schedulerFallback` — so it can **never** render on a clean run; no existing smoke selector is touched (new string `"CV: libn4m fallback"`). `Cpu` is already imported (existing `runEngineLabel` chip); `lineage`/`selectedRun` are in scope; typecheck passes.

---

## Findings (severity-ordered)

### F1 — LOW · Cross-sibling envelope drift; canonical schema unauthored
`rt.ts RtError` = `{ schema_version:1, verb, cause, message, mitigation?, unsupported_capability?, portable_level?, detail? }`. The sibling Studio envelope (`_worktrees/L12-studio-runtime/api/runtime_errors.py`) is `{ verb, cause, message, mitigation?, unsupported_capability?, portable_level? }`.
- The `code` field in the RT-003 *sketch* (`{verb, code, cause, …}`) is omitted by **both** web and Studio → consistent, not a web regression.
- But web **always** emits `schema_version:1` (and optionally `detail`), neither of which the Studio dataclass carries → the two "wire-identical" envelopes are **not** byte-identical on the wire today.
- `nirs4all-ecosystem/docs/contracts/runtime/rt_error.v1.schema.json` **does not exist** (verified absent), so the IMP report's "mirrors the schema field-for-field" is asserted, not verifiable.
IMP risk #4 discloses the schema is GOV-deferred, but not the specific `schema_version`/`detail` vs `code` deltas. **Impact:** none today (the web envelope is consumed only inside the web app; no cross-process RtError exchange). **Action (non-blocking):** reconcile `schema_version`/`detail`/`code` when GOV freezes `rt_error.v1.schema.json` and add the parity tests.

### F2 — LOW · Worker rtError rebuild + `allowFallback` forwarding are untested
`worker-engine.test.ts` covers only `result` and `abort`. The new `else if (m.rtError) reject(new RtErrorException(m.rtError))` branch and the `{type:'run', …, allowFallback}` payload forwarding have **no** unit test, despite the existing `FakeWorker` harness making it trivial (dispatch a `{type:'error', id, rtError}` message; assert `rejects` is an `RtErrorException` with the cause; assert `fake.messages[0].allowFallback`). **Action (non-blocking):** add ~2 cases to the existing harness — this is the one focus area with a reachable-but-unwritten test.

### F3 — LOW · Planning-fallback diagnostic is recorded but not surfaced in the UI
The model-only planning fallback (`dagml-engine.ts:386-394`) pushes an `RtError` to `diagnostics[]` but does **not** set `schedulerFallback`. Since the amber chip is gated on `lineage.schedulerFallback`, a dropped variant-sweep produces a machine-readable diagnostic with **no** visual indicator (the scheduler fallback gets both). It is therefore "recorded" but not "surfaced" — a partial gap against the IMP's "recorded *and* surfaced" framing. Defensible (this branch is described as unexpected for a model-only graph), but worth an explicit UI follow-up or a note.

### F4 — INFORMATIONAL · Report line-citation & "byte-for-byte" nuance
- IMP risk #1 cites "served dag-ml split (`dagml-engine.ts:249`) already throws"; line ~249 is actually the dag-ml-**data** provider catch (surfaced via the `dataProvider` chip, not silent). The served *split* that genuinely throws is ~l.258. Substance correct; citation imprecise.
- `lineage: { …, schedulerFallback: schedulerFallback || undefined, … }` always adds the key (value `undefined`) on clean runs. `JSON.stringify` drops undefined-valued keys, so JSON/wire output is unchanged; only `Object.keys`/`structuredClone` would observe it. No lineage snapshot test exists → harmless. "Byte-for-byte unchanged" is accurate at the JSON level, slightly loose at the object level.
- The `max_variants` cap (`dagml-engine.ts:378-379`) still throws a plain `Error`, not a typed one. Out of B-018 scope (it is a **visible** hard throw, not a silent fallback); noted for completeness only.
- On a scheduler-fallback run, the existing `"executed by dag-ml"` badge still shows (by design — dag-ml owns folds/OOF/selection); the new amber chip disambiguates. Multi-node graphs bypass the scheduler up-front (not a fallback) and intentionally emit no diagnostic. Both consistent with the slice's scope.

---

## Residual risks (carried from IMP, confirmed accurate)
1. **Fallback not exercised end-to-end** (needs staged dag-ml+libn4m WASM + browser); only the envelope, classifier, and typed guard are unit-tested. A browser smoke that forces a scheduler failure and asserts `RunResult.diagnostics` + the chip is the natural follow-up.
2. **Browser smokes not run here** (no Chromium/preview in this pass). The UI addition is conditional on a fallback clean runs never hit, so selectors are unaffected by construction; both `build` and `build:single` are reported green by IMP.
3. **`orchestrate.ts:316-323` split swallow** (offline `runPipeline`, `console.warn`) left unconverted — **verified** present and correctly scoped out (converting it would touch `StubEngine`'s return shape).
4. **Canonical `rt_error.v1.schema.json` unauthored** (F1) — no arbiter for envelope parity until GOV freezes it.

## Bottom line
Correct, contained, and default-preserving; gates reproduce green (typecheck 0 · 99/99 unit · 20/20 targeted). **Approve to merge.** Suggested non-blocking follow-ups, in priority order: **F2** (cheap worker-path unit test), **F1** (envelope reconciliation at schema-freeze), **F3** (surface the planning diagnostic), **F4** (fix the l.249 citation).
