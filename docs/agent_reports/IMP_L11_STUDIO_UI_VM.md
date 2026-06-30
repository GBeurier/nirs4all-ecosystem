# IMP-L11 — Studio UI reusable view-model extraction (first `nirs4all-ui` slice)

**Date:** 2026-06-30
**Agent:** IMP-L11 (implementation)
**Worktree:** `/home/delete/nirs4all/_worktrees/L11-studio-ui` (branch `refactor/L11-ui-vm`)
**Repo touched:** `nirs4all-studio` only. Report written to the designated `nirs4all-ecosystem/docs/agent_reports/` handoff location (per task instructions). No sibling code or sync board edited.
**Predecessor context:** A6 audit (`docs/agent_reports/A6_A6-studio-ui.md`). `UI_spec.md` was named in the task but **does not exist anywhere in the workspace** (see Blockers); I proceeded on the A6 audit as the operative spec.

---

## 0. Summary

Stood up the **internal `nirs4all-ui` foundation package** inside Studio at `src/ui/` and extracted the first coherent, already-pure view-model domain into it: the **score / metric view-model stack**. This realizes A6 Wave 0–1 ("stand up the internal `src/ui/` package … extract the pure adapter + UI-004 type layer") at a small, verifiable scale.

- **Moved** 3 pure modules + their 2 colocated tests from `src/lib/` → `src/ui/score/` (git-tracked renames, zero content change).
- **Added** the package scaffolding: a `score` barrel, the package root barrel, a `README` encoding the purity contract, and a new focused test pinning the public surface.
- **Repointed** all 5 importer sites — 3 app consumers now import the formal public API `@/ui/score`; the in-`lib` runtime aggregator and one unit test import specific modules.
- **No backward-compat shim** (honors the ecosystem "no shims" rule): every importer was updated, and a full `tsc --noEmit` proves the tree is internally consistent.

**Net diff: 14 files, +129 / −12.** No visual/component churn — only file relocation and import-path edits.

---

## 1. Why this slice

The A6 audit's core finding is that "the extractable gold is the pure view-model layer, and Studio has already built it" (§0.2), and that the unblocked starting move is the pure adapter/type layer (§4 Wave 1, §10.3), kept separate from the app-runtime layer that builds on it.

The **score/metric utilities** are the cleanest possible first slice:

- **Genuinely pure & layered** — verified zero `react` / `@/api` / `fetch` / `window` / `document` imports across all three modules. Dependency graph is a clean DAG:
  `metricKeys` (0 deps) → `scoreValues`, `scoreMetricCatalog`.
- **Self-describing** — the modules' own docstrings already call them a "self-contained, pure slice" / "small, self-contained, easily testable slice." The extraction formalizes intent that was already there.
- **Cross-cutting vocabulary** — metric-key canonicalization + the metric catalog + score formatting are consumed across Datasets/Runs/Results/Predictions, so they belong in a shared foundation rather than `lib/`.
- **Bounded blast radius** — only 5 importer sites repo-wide, all in `src/`, making "update every importer" (no shim) tractable and fully verifiable.
- **Models the target architecture** — pure foundation in `src/ui/score/`; the app-runtime score-map layer (`src/lib/scores.ts`) stays in `lib/` and now builds *on top of* the foundation. This is exactly the `wrapper (stays) → pure leaf (extract)` recipe A6 §0.3 describes.

I deliberately did **not** pull in adjacent runtime-coupled pieces (`score-adapters*`, `scoreCardRow*`, `resultArtifacts`) — those are LOCK-RT-gated per A6 §2.4/§6 and would exceed "small but real."

---

## 2. Changes

### New foundation package (`src/ui/`)
| File | Purpose |
|---|---|
| `src/ui/README.md` | Encodes the `nirs4all-ui` foundation **contract** (pure TS, IO-free, app-state-free, unit-testable), the internal-package-not-a-repo decision (DEC-UI-001), and how the layer grows. |
| `src/ui/index.ts` | Package root barrel — `export * as score from "./score"`. |
| `src/ui/score/index.ts` | `score` domain public barrel — re-exports `metricKeys` + `scoreValues` + `scoreMetricCatalog`. The formal API app code imports. |
| `src/ui/score/index.test.ts` | **New focused test** pinning the barrel's public surface (fails loudly if a re-export is dropped/renamed) and smoke-testing the metricKeys→scoreValues layering through the barrel. |

### Moved (git renames, content unchanged — intra-package relative imports preserved)
- `src/lib/metricKeys.ts` → `src/ui/score/metricKeys.ts`
- `src/lib/scoreValues.ts` → `src/ui/score/scoreValues.ts`
- `src/lib/scoreMetricCatalog.ts` → `src/ui/score/scoreMetricCatalog.ts`
- `src/lib/metricKeys.test.ts` → `src/ui/score/metricKeys.test.ts`
- `src/lib/scoreValues.test.ts` → `src/ui/score/scoreValues.test.ts`

### Repointed importers (import-path edits only)
| File | Change |
|---|---|
| `src/lib/scores.ts` | `./metricKeys` / `./scoreMetricCatalog` / `./scoreValues` → `@/ui/score/*` (the runtime aggregator stays in `lib`, now builds on the foundation; kept granular as it pulls many internal symbols). |
| `src/lib/metricSelectorData.ts` | Two `@/lib/{metricKeys,scoreValues}` imports merged into one `@/ui/score` barrel import. |
| `src/lib/score-adapters-prediction-records.ts` | `@/lib/scoreValues` → `@/ui/score`. |
| `src/components/predictions/detail/chainDetailData.ts` | `@/lib/scoreValues` → `@/ui/score`. |
| `src/lib/__tests__/scoreValues.test.ts` | `../scoreValues` → `@/ui/score/scoreValues` (this is the second, complementary `scoreValues` test — it owns the `parseJsonRecord` coverage; left in place, repointed). |

---

## 3. Compatibility & churn posture

- **Compatibility = full internal consistency, no shim.** These modules are internal (`src/`-only; no public package boundary). I updated all 5 importers rather than leaving a re-export at the old path, which keeps the ecosystem "no backward-compat shims" rule intact. `tsc --noEmit` (whole project, exit 0) is the proof that nothing else imported them.
- **No broad component churn.** Zero `.tsx` component bodies changed; zero visual/markup/style changes. The only edits are import specifiers (2–14 lines each). The moves are 0-line renames.
- **Public-API ergonomics.** App consumers import the curated `@/ui/score` barrel; the barrel is genuinely used (3 consumers), not dead scaffolding.

---

## 4. Tests & gates run (touched-code scope)

All run in-worktree (see Blockers re: `node_modules`).

| Gate | Command (narrowed) | Result |
|---|---|---|
| Type-check | `npx tsc --noEmit` (full project) | **exit 0** — every import across the project resolves post-move |
| Lint | `npx eslint` on the 9 touched paths | **exit 0** |
| Unit (touched) | `vitest run src/ui` + 4 direct consumers | **6 files / 45 tests passed** |
| Unit (blast radius) | `vitest run src/ui src/lib src/components/{predictions,results}` | **253 files / 1421 tests passed**, 0 failures |

The new `src/ui/score/index.test.ts` adds 4 cases (16 assertions) over the barrel; the 2 moved test files (metricKeys, scoreValues) and the repointed `parseJsonRecord` test continue to pass at their new import paths.

---

## 5. Blockers / notes / deviations

1. **`UI_spec.md` not found.** The task said to read `UI_spec.md`; it exists nowhere under `/home/delete/nirs4all` (checked ecosystem + studio + worktree). I proceeded on the A6 audit, which is the substantive UI-extraction spec and fully covers the intent. If `UI_spec.md` was meant to be a distinct artifact, it is a missing input — flag for the task author.
2. **Worktree had no `node_modules`.** To run the gates I symlinked `node_modules → ../../nirs4all-studio/node_modules` after verifying `package.json` **and** `package-lock.json` are byte-identical to the main checkout (no dependency drift; I changed no manifest). The symlink is gitignored, touches no tracked file and no sibling source, and is safe to delete (`rm node_modules`) — it is a local test-run convenience only.
3. **RTK's `vitest` parser** errored (`[RTK:PASSTHROUGH] … All parsing tiers failed`); I ran vitest via `npx` directly. Non-blocking, tooling-only.
4. **Pre-existing duplicate test.** Two `scoreValues` tests existed before this change (a comprehensive colocated one + a small `__tests__/` one covering `parseJsonRecord`). I kept both (moved one, repointed the other) rather than consolidating, to avoid deleting another contributor's coverage. Minor, pre-existing; candidate for later consolidation.

---

## 6. Review readiness

**Ready for review.** Changes are staged in the worktree (not committed — no commit/push was requested). The slice is intentionally minimal and mechanically verifiable:

- Reviewer can confirm correctness from the diff alone: 5 renames are 0-line, 5 import edits are one-liners, 4 new files are additive.
- Green on `tsc` (full), `eslint` (touched), and `vitest` (1421 tests across the blast radius).
- Suggested reviewer focus: (a) the `@/ui/score` barrel as the intended public surface, (b) the `src/ui/README.md` contract wording, (c) agreement that `src/lib/scores.ts` correctly stays the app-runtime layer atop the foundation.

**Natural next slices** (still unblocked, same recipe): the zero-import `chartExport` + `partitionColors` adapters into a `src/ui/export` / `src/ui/data` domain; then the `lib/inspector/*Data.ts` pure family (A6's "single biggest asset"). Runtime/score-card/results presentation remains LOCK-RT-gated and should wait.

---

## Appendix — verification commands

```bash
# purity check (all empty/none):
rg -n "react|@/api|fetch\(|axios|window\.|document\." src/ui/score/*.ts
# importer completeness (whole repo, before+after): src + electron, ts/tsx
rg -n "from ['\"][^'\"]*(metricKeys|scoreValues|scoreMetricCatalog)['\"]" src electron
# gates:
npx tsc --noEmit
npx eslint src/ui src/lib/scores.ts src/lib/metricSelectorData.ts \
  src/lib/score-adapters-prediction-records.ts \
  src/components/predictions/detail/chainDetailData.ts src/lib/__tests__/scoreValues.test.ts
npx vitest run src/ui src/lib src/components/predictions src/components/results
```
