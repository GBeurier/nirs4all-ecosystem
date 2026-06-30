# W9 — Web runtime result/error PARITY with the W7 envelopes (B-018)

**Agent:** W9 (implementation) · **Repo:** `nirs4all-web` · **Worktree:** `_worktrees/W9-web` (`refactor/W9-web-rt`, base `488176b`)
**Date:** 2026-07-01 · **Scope:** the **Web** half of the `B-018` runtime result/error parity slice — align the Web `RtError` wire form + fallback diagnostics with the now-finalized **W7** schemas/contracts, and lock it with focused tests/smokes.
**Consumes (read-only):** W7 `nirs4all` `refactor/W7-rt-envelopes` @ `7f8cfe69` (`pipeline/dagml/rt.py` — `RtError` / `RtResult` / `RtRunRequest`); ecosystem `2e93a16` runtime contracts `docs/contracts/runtime/rt_error.v1.schema.json` (+ `rt_result` / `rt_run_request`); sync board `B-018`.

> Work confined to the `nirs4all-web` worktree. No sibling repo edited; `PARALLEL_REFACTORING_SYNC.md` untouched. The neutral
> `rt_error.v1.schema.json` is **referenced** (the TS wire form mirrors it field-for-field and is validated against the on-disk
> schema in a test) but **not authored/edited** here.

---

## 1. Problem (verified in-tree) — L13 guessed the schema; W7 finalized it differently

The prior Web slice (`488176b`, IMP-L13, dated 2026-06-30) introduced `studio-lite/src/engine/rt.ts` and claimed the envelope
"mirror[s] the neutral `rt_error.v1.schema.json` … so the Python / Studio / Web envelopes are **wire-identical**." It was authored
*before* W7 froze the contract (2026-07-01), so it guessed two fields that the finalized contract does **not** have:

| Field on the L13 Web `RtError` | W7 `rt_error.v1.schema.json` | Python `RtError.to_dict()` (`rt.py:84`) | Verdict |
|---|---|---|---|
| `schema_version: 1` | **absent** (`additionalProperties: false`) | **not emitted** (it is an `RtResult` field, not `RtError`) | **drift** — would fail validation |
| `detail?: string` | **absent** (`additionalProperties: false`) | **not emitted** | **drift** — would fail validation |

The contract is `additionalProperties: false`, required `["verb","cause","message"]`, optionals `mitigation` / `unsupported_capability`
/ `portable_level`. So a serialized L13 diagnostic carrying `schema_version` **or** `detail` is **not** wire-parity with Python/Studio —
exactly the gap this W9 slice closes. (`schema_version` does belong on `RtResult` — `rt.py:190`, `rt_result.v1.schema.json` requires it —
but never on `RtError`.)

## 2. Change (narrow, additive, behavior-preserving)

All changes are in `studio-lite/src/engine/rt.ts` + its tests; **no** engine/UI/worker file needed editing (they build `RtError`s via
`makeRtError` / `rtErrorFromUnknown`, neither of which ever received `schema_version`, and they keep using the in-memory `detail`).

| File | Change |
|---|---|
| **`src/engine/rt.ts`** | Split the type into **`RtErrorWire`** (the exact contract: `verb` / `cause` / `message` / `mitigation?` / `unsupported_capability?` / `portable_level?`) and **`RtError extends RtErrorWire`** (adds the **in-memory-only** `detail?`). **Removed `schema_version`** (contract has none). Added **`rtErrorToWire(e)`** — the byte-parity projection mirroring Python `RtError.to_dict()`: always `{verb,cause,message}`, each optional only when set, `portable_level` only when non-null, `detail` stripped. Vendored **`RT_VERBS`** / **`RT_ERROR_CAUSES`** / **`RT_ERROR_WIRE_KEYS`** consts (mirror the `rt.py` frozensets + the schema enums; `RtVerb`/`RtErrorCause` now derive from them). `makeRtError` no longer stamps `schema_version`. Header comment corrected (the wire form is `rtErrorToWire`, not the in-memory object). |
| **`src/engine/rt.contract.test.ts`** *(new, 10 cases)* | The parity gate. (1) self-contained: `rtErrorToWire` emits exactly the contract keys, omits unset/null optionals, strips `detail`, never carries `schema_version`; the vendored vocabularies are the expected 8 verbs / 5 causes; `RT_ERROR_WIRE_KEYS` excludes `schema_version`/`detail`. (2) **cross-repo drift guard**: walks up to the on-disk `rt_error.v1.schema.json` and asserts `additionalProperties === false`, `required === [cause,message,verb]`, and that the schema's property set / `verb` enum / `cause` enum **equal** the vendored consts, plus a projected wire validates structurally (additionalProperties:false + required + enums). Self-skips with a warning if the ecosystem repo isn't checked out (mirrors the `validate:catalog` convention). |
| `src/engine/rt.test.ts` | Updated the one `makeRtError` case that asserted `schema_version: 1` → now asserts the exact contract fields **and** `'schema_version' in e === false`. Other 8 cases (cause classifier, `RtErrorException`, guard refuse) unchanged and green — they only touch `verb`/`cause`/`message`/`mitigation`/`detail`. |
| **`tests/rt-fallback-smoke.mjs`** *(new)* | B-018 browser smoke: a clean run must be **silent**. Loads the sample, runs the default pipeline, asserts the amber "CV: libn4m fallback" chip is **absent** and there are no console errors (served build additionally asserts the "by dag-ml" badge). Guards against the engine regressing to an always-on/silent fallback — the WASM/browser half the node vitest env can't reach. |

**What stayed the same on purpose:** `RunResult.diagnostics` remains `RtError[]` (the rich in-memory form, with `detail`), and the
worker boundary keeps cloning it verbatim — that is internal transport (structured clone), not the contract wire. The contract wire is
produced by `rtErrorToWire` when a diagnostic is serialized for Python/Studio/REST parity. This mirrors W7 exactly: Python keeps a rich
`RtError` object and exposes the contract via `to_dict()`.

## 3. Parity matrix (Web ↔ W7) after this slice

| Concern | W7 (`rt.py` + schema) | Web (`rt.ts`) after W9 |
|---|---|---|
| Wire keys | `verb,cause,message,mitigation?,unsupported_capability?,portable_level?` | `RtErrorWire` / `rtErrorToWire()` — identical set |
| `additionalProperties:false` | enforced by schema | `rtErrorToWire` emits only contract keys; test enforces it |
| Omit unset optionals | `to_dict` omits `None` | `rtErrorToWire` omits `undefined` (+ null `portable_level`) |
| `schema_version` on the error | **absent** (only on `RtResult`) | **removed** |
| cause vocabulary | `RT_ERROR_CAUSES` frozenset (5) | `RT_ERROR_CAUSES` const (5) — asserted equal to schema enum |
| verb vocabulary | `RT_VERBS` frozenset (8) | `RT_VERBS` const (8) — asserted equal to schema enum |
| Rich object vs wire | `RtError` (raisable) + `to_dict()` | `RtError` (+`detail`, `RtErrorException`) + `rtErrorToWire()` |

`RtResult` / `RtRunRequest` are **Python-side projections** of the native dag-ml triple and the `run()` input; the Web engine produces
neither today (it returns the app's `RunResult`, and there is no REST surface in the full-WASM client), so no Web type is added for them.
The error envelope is the only W7 wire shape the Web runtime actually emits — that is the parity surface this slice covers.

## 4. Green gate (toolchain PATH per `studio-lite/CLAUDE.md`)

| Gate | Command | Result |
|---|---|---|
| Typecheck | `npm run typecheck` (`tsc --noEmit`, strict) | **exit 0** |
| Unit suite | `npm run test` (vitest) | **109 passed (15 files)**, incl. new `rt.contract.test.ts` (10) + updated `rt.test.ts` (9) |
| Catalog | `npm run validate:catalog` | self-skips (upstream `nirs4all-methods` ABI snapshot not reachable from a worktree — pre-existing/environmental, identical to L13) |
| Served build | `npm run build` | **exit 0** (pre-existing >4 MB WASM-chunk + `node:module` externalize warnings only) |
| Offline build | `npm run build:single` | **exit 0** (`dist-single/index.html`, ~50 MB inlined) |
| Browser smoke — new | `SMOKE_URL=file://…/dist-single/index.html node tests/rt-fallback-smoke.mjs` | **SMOKE PASSED** (clean run, no fallback chip, no console errors) |
| Browser smoke — regression | `… node tests/smoke.mjs` | **SMOKE PASSED** (load → run → results → predict, no console errors) |

The cross-repo drift guard in `rt.contract.test.ts` **did run** here (the ecosystem repo is a sibling in this working tree) and asserts
the live `rt_error.v1.schema.json` against the vendored Web vocabularies — i.e. this is a real Web↔W7 contract check, not a vendored copy.

## 5. Residual risks / deliberate scope boundaries

1. **Served (dag-ml) browser smoke not run.** The background-task harness in this environment kills a long-running `vite preview`
   server (exit 144), so the served-path smoke could not be executed. Both smokes were instead run green against the offline `file://`
   single-file build (real Chromium, full app slice). The served-only delta is "by dag-ml badge present **and** chip absent together";
   the chip-absence invariant + clean run + zero console errors are already verified offline, and the actual wire-parity guarantee is the
   unit/contract test, which validates against the real schema file regardless of build mode.
2. **No `RtResult`/`RtRunRequest` Web types.** Out of scope by construction (§3): the full-WASM client emits neither (no native triple
   export, no REST). If a future Web "export to native results" or a Studio-style REST bridge lands, an `RtResult` projection mirroring
   `from_run_result` would be the follow-up — tracked, not done here.
3. **`detail` retained (intentionally).** It carries the raw underlying error when `message` is a friendly override (the two
   `dagml-engine.ts` fallback sites). It is **in-memory only** and provably stripped by `rtErrorToWire` (test-locked), so it never breaks
   wire parity — the Web analogue of Python keeping `__cause__` off `to_dict()`.
4. **Contract file referenced, not authored.** `rt_error.v1.schema.json` lives in the ecosystem repo (W7/GOV); W9 only reads it.

## 6. Review readiness

Self-contained, additive, default-behavior-preserving (no engine/UI/worker logic changed — only the envelope's type split + the new
projection + tests). Full local gate green except the served-build browser smoke (environmental server limitation; the offline browser
smoke + the schema-validated unit test cover the slice). Committed on `refactor/W9-web-rt`; `PARALLEL_REFACTORING_SYNC.md` untouched.
