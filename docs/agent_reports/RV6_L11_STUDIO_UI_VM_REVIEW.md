# RV6 — Review of IMP-L11 (Studio UI reusable view-model extraction, `src/ui/score`)

**Date:** 2026-07-01
**Reviewer:** RV6 (read-only)
**Scope reviewed:** staged changes on branch `refactor/L11-ui-vm` in `/home/delete/nirs4all/_worktrees/L11-studio-ui` + the implementation report `docs/agent_reports/IMP_L11_STUDIO_UI_VM.md`.
**Repo touched by IMP-L11:** `nirs4all-studio` only.
**Focus areas (per task):** import compatibility, module boundaries, duplicate/shim risks, test coverage, and whether `src/ui/score` is a safe internal foundation.
**Constraints honored:** No source files edited, nothing staged/unstaged, nothing committed. Only this report was written (to the designated handoff location). One throwaway *detached* git worktree was created at HEAD for a base-vs-change type-check comparison and then removed — it never touched the L11 worktree's tracked files or index.

---

## 0. Disposition — **APPROVE (safe to proceed / merge after caveats noted)**

The change is exactly what the report describes: a behavior-preserving relocation of three already-pure score/metric modules (+ two colocated tests) from `src/lib/` into a new internal foundation package `src/ui/score/`, with all importers repointed and **no backward-compat shim**. I independently verified the mechanics end-to-end. `src/ui/score` **is** a safe internal foundation: pure, self-contained, acyclic, byte-identical to the originals, fully consumed, type-clean, lint-clean, test-green.

No code changes are required for L11 itself. The findings below are one **methodology/evidence** correction (Medium) and four **low/informational** maintainability notes; none block the change.

---

## 1. What the diff actually is (verified)

`git diff --cached --name-status -M`:

| Kind | Files | Verified |
|---|---|---|
| **R100 renames** (byte-identical) | `metricKeys.ts`, `scoreValues.ts`, `scoreMetricCatalog.ts`, `metricKeys.test.ts`, `scoreValues.test.ts` → `src/ui/score/` | `R100` = 100% similarity → **zero content change**. Confirmed. |
| **Modified importers** (specifier-only) | `src/lib/scores.ts`, `src/lib/metricSelectorData.ts`, `src/lib/score-adapters-prediction-records.ts`, `src/components/predictions/detail/chainDetailData.ts`, `src/lib/__tests__/scoreValues.test.ts` | Each edit changes only the `from "…"` path; no logic touched. Confirmed line-by-line. |
| **Added** | `src/ui/README.md`, `src/ui/index.ts`, `src/ui/score/index.ts`, `src/ui/score/index.test.ts` | Additive scaffolding + barrels + a new surface-pinning test. Confirmed. |

Net **14 files, +129 / −12** — matches the report exactly. `src/ui` is a fresh directory (absent in HEAD); no collision with pre-existing code.

---

## 2. Findings

### F1 — [Medium · methodology/evidence, not a code defect] The report's primary type-check evidence is non-probative; the real type-check was never run

The report's headline gate (§4, §6) is:
> Type-check — `npx tsc --noEmit` (full project) — **exit 0** — every import across the project resolves post-move.

This command does **not** prove that. The root `tsconfig.json` is a **solution-style** config (`"files": []` + `"references"`). Plain `tsc --noEmit` (without `-b`/`--build`) does **not** follow project references, so it compiles an **empty program** and returns exit 0 **regardless of any import breakage in `src/**`**. I reproduced this in-worktree: `./node_modules/.bin/tsc --noEmit` → `ROOT_TSC_EXIT=0` while type-checking nothing.

The real app program is `tsconfig.app.json` (`"include": ["src"]`). Running **that** is what proves import resolution:

- `tsc -p tsconfig.app.json --noEmit` on the **L11 change** → **3 errors**, all in files L11 never touches:
  - `src/api/inspector.test.ts:41` — `ScoreRef` missing `key, metric`
  - `src/components/predictions/viewer/fetchPartitionData.ts:50,51` — `PredictionArrayPayload` not assignable to `number[]`
- I then ran the **identical** command on a detached worktree at **HEAD (pre-L11 base)** → the **exact same 3 errors**, same files/lines/messages.

**Conclusion: L11's app-config type-error delta is exactly zero.** The 3 errors are pre-existing on the branch and unrelated to the score extraction (none of the offending types — `ScoreRef`, `PredictionArrayPayload`, `PredictionMatrix` — live in or are touched by the moved modules). So the report's *conclusion* ("no new type errors, imports resolve") is **correct and independently confirmed by me** — but the *evidence it cited does not support it*.

Two corollaries, both **out of L11 scope** but worth flagging to the project owners:
- The project's own gate `lint:tsc` is literally `tsc --noEmit` (root config) — a **pre-existing no-op** that type-checks nothing. A genuine import break inside this new package could pass `lint:tsc` today.
- There are **3 pre-existing app-config type errors** already on `refactor/L11-ui-vm` (and on its base). Not caused by L11; flagged for separate cleanup.

**Recommendation (non-blocking):** have IMP-L11 (and future UI-VM slices) verify with `tsc -b` or `tsc -p tsconfig.app.json --noEmit`, and cite that. Consider fixing `lint:tsc` to use `tsc -b` so the green gate actually type-checks the app.

### F2 — [Low] Root `@/ui` barrel (`src/ui/index.ts`) is currently unconsumed
`git grep` for `from "@/ui"` (exact root) → **no importers**. All real consumers use the `@/ui/score` subpath barrel (3 app sites) or `@/ui/score/*` deep paths (`scores.ts`). `src/ui/index.ts` (`export * as score from "./score"`) is forward-looking scaffolding. This is in mild tension with the ecosystem "no dead code / no features for hypothetical future requirements" rule, though a package root barrel is a conventional entry point and is trivially small. **Acceptable**; optionally defer until a second domain lands, or note it explicitly as the seed entrypoint (the README does).

### F3 — [Low] Dual import surface for the same symbols
`@/lib/scores` re-exports the **entire** `@/ui/score` foundation surface (all of `metricKeys` + `scoreValues` + the catalog), so every foundation symbol is now reachable via **two** paths. Consumers mix them — e.g. `src/lib/metricSelectorData.ts` imports `canonicalMetricKey`/`formatMetricDisplayName`/`isLowerBetter` from `@/ui/score` while importing `getAvailableMetrics`/`getMetricDefinitions`/… from `@/lib/scores` in the same file. This is **pre-existing** (`scores.ts` always re-exported these) and not introduced by L11, but the new package makes the "which path do I import from?" ambiguity more visible. **Recommendation (non-blocking):** add a short guideline — *foundation vocabulary lives in `@/ui/score`; `@/lib/scores` is the runtime score-map layer* — and over time stop having the runtime layer re-export the whole foundation. Not required now.

### F4 — [Low] Stale documentation paths after the move
`docs/ARCHITECTURE_BOUNDARIES.md` (lines ~726–729) still describes these modules at `src/lib/metricKeys.ts` / `src/lib/scoreValues.ts` / `src/lib/scoreMetricCatalog.ts` — those paths no longer exist post-move. `ARCHITECTURE_BOUNDARIES.md` is a *living* boundary doc and will mislead future contributors; it should be repointed to `src/ui/score/*`. (`docs/STUDIO_PRISTINE_PROGRESS.md` also references the old paths but is an append-only historical log — fine to leave.) These files are not in the staged diff; flagged for a follow-up (I am read-only).

### F5 — [Info] Pre-existing duplicate `scoreValues` test (report's own note #4, confirmed)
Two tests cover `scoreValues`: the comprehensive colocated `src/ui/score/scoreValues.test.ts` (17 tests) and the small `src/lib/__tests__/scoreValues.test.ts` (2 tests: `parseJsonRecord`/`parseScoreNumber`), the latter now reaching across the package boundary via `@/ui/score/scoreValues`. Pre-existing; keeping both was the right call (don't delete another contributor's coverage). Consolidation candidate later.

### F6 — [Info] Barrel test pins a representative subset, not the full surface
`src/ui/score/index.test.ts` guards the core re-exports (metric-key helpers, score-value helpers, and a handful of catalog symbols + the layering smoke test). `scoreMetricCatalog` exports ~30 symbols; non-pinned ones (e.g. `getPresetsForTaskTypes`, `groupMetricDefinitions`) aren't directly asserted by this test. In practice the app-config compile of consumers + `scores.ts` would catch any consumer-affecting drop, so coverage is adequate; just noting the barrel test is not an exhaustive surface lock.

---

## 3. Focus-area verdicts

| Area | Verdict | Evidence |
|---|---|---|
| **Import compatibility** | ✅ Complete | Precise `git grep` shows **no** remaining `@/lib/{metricKeys,scoreValues,scoreMetricCatalog}` or relative old-path specifiers anywhere in `src/lib`, `src/components`, `electron`; no `vi.mock`/`require` to old paths. `@/* → ./src/*` (tsconfig.json + tsconfig.app.json) and `@ → ./src` (vite.config.ts + vitest.config.ts) all resolve `@/ui/score` and `@/ui/score/scoreValues` in build **and** test. App-config type-check adds **0** errors vs base. |
| **Module boundaries / purity** | ✅ Upheld | No `react`/`@/api`/`@tanstack`/`react-router`/`@/hooks`/`@/components` imports and no `fetch`/`axios`/`window.`/`document.`/`localStorage` usage anywhere under `src/ui`. Dependency DAG is clean and acyclic: `metricKeys` (0 deps) → `scoreValues`, `scoreMetricCatalog`. Runtime score-map layer correctly stays in `@/lib/scores` and builds on top. |
| **Duplicate / shim risks** | ✅ No shim; ⚠️ benign dual-surface | No old-path re-export shim (rule honored — every importer updated). `export *` from the 3 modules has **no overlapping exported names** → no silently-dropped/ambiguous symbols (corroborated by the green barrel test + app-config compile). Dual-surface via `@/lib/scores` is pre-existing (F3), benign. |
| **Test coverage** | ✅ Green | Independently ran: moved+new+repointed tests `src/ui` + `src/lib/__tests__/scoreValues.test.ts` → **32 passed**; consumer blast-radius `scores.test.ts` + `metricSelectorData.test.ts` + `src/components/predictions/detail` → **38 passed**. **70 tests green, 0 failures** under my own runs. New `index.test.ts` meaningfully pins the public surface + layering. |
| **Safe internal foundation?** | ✅ Yes | Pure + acyclic + byte-identical move + fully consumed (`@/ui/score` used by 3 app sites) + type/lint/test clean. Reusable by a second host (WASM web client) without dragging the app shell. README encodes the contract clearly. |

---

## 4. Validation evidence (commands I ran)

All in-worktree (`node_modules` symlinked to `../../nirs4all-studio/node_modules`; `package.json` **and** `package-lock.json` byte-identical to the main checkout → no dependency drift). Local bins invoked directly to avoid the RTK `vitest` passthrough-parse issue the report noted.

```text
git diff --cached --name-status -M           → 5×R100 renames, 5 M importers, 4 A files (matches report)
git grep (precise old specifiers)            → none in src/lib, src/components, electron; no mock/require refs
tsconfig.json / tsconfig.app.json / vite / vitest → @/ alias resolves in build + test
./node_modules/.bin/vitest run src/ui + scoreValues.test  → 4 files / 32 tests PASS
./node_modules/.bin/vitest run scores.test + metricSelectorData.test + predictions/detail → 7 files / 38 tests PASS
./node_modules/.bin/eslint <9 touched paths> → ESLINT_EXIT=0
./node_modules/.bin/tsc --noEmit (root cfg)  → exit 0 BUT compiles empty program (non-probative — see F1)
./node_modules/.bin/tsc -p tsconfig.app.json --noEmit (CHANGE) → 3 errors, all in untouched files
   same command on detached worktree @HEAD (BASE)            → identical 3 errors  ⇒ L11 delta = 0
git grep purity (react/IO/app-state under src/ui)            → clean
```

---

## 5. Residual risks

- **R1 (Low, pre-existing, out of scope):** `lint:tsc` is a no-op and 3 app-config type errors already live on the branch (`inspector.test.ts`, `fetchPartitionData.ts`). Not introduced by L11, but they mean the green gate isn't catching real type errors. Recommend a separate fix (switch gate to `tsc -b`; fix the 3 errors).
- **R2 (Low):** Future UI-VM slices that rely on the report's `tsc --noEmit` recipe would get **false assurance** of import integrity. Standardize on `tsc -b` / `tsconfig.app.json` for this workstream.
- **R3 (Low):** Doc drift in `ARCHITECTURE_BOUNDARIES.md` (F4) until repointed.
- **R4 (Low):** Dual import surface (F3) could let the foundation/runtime boundary blur as the package grows; cheap to govern with a one-line convention now.
- **No correctness/behavioral risk** identified: the modules are byte-identical, the export surface of `@/lib/scores` is unchanged for its consumers (only its internal `from` paths moved), and consumer tests pass.

---

## 6. Bottom line

IMP-L11 is a clean, minimal, mechanically-verifiable first slice of the internal `nirs4all-ui` foundation. **Approve.** The single substantive correction is that the report's `tsc --noEmit` evidence is non-probative (empty-program compile); I re-verified with the correct command and confirmed the change adds **zero** type errors and breaks **no** imports. The remaining notes (unconsumed root barrel, dual import surface, stale boundary docs, duplicate test, partial surface pin) are low-severity maintainability items that do not block the change. `src/ui/score` is a safe internal foundation and a sound template for the next slices (`chartExport`/`partitionColors`, then the `lib/inspector/*Data.ts` family).
