# UI-SPEC report — lanes L11 (`nirs4all-ui` extraction) + L12 (Studio reassembly) — LOCK-UI

**Agent:** UI-SPEC (read-only audit). No code/test/sync-board edits — this file is the only write.
**Lock:** `LOCK-UI` (in_progress) · **Decision:** `DEC-UI-001` (accepted, `ARB-007`=A).
**Date:** 2026-06-30
**Method:** direct `rg`/`sed`/`ls`/`git` against working-tree heads (local code is authoritative; CodeGraph
not relied on for facts). Heads verified: **`nirs4all-studio 2ccbf68`**, **`nirs4all-web 745eef8`** (both
clean). Builds on the prior `A6_A6-studio-ui.md` audit — **every load-bearing A6 claim below was
re-verified against code**; where A6 was wrong it is corrected (see *Corrections to A6*).

**Contract inputs (already SIGNED — consumed as-is, not re-specified):**
- `LOCK-CAP` (`CAP_spec.md`): enum `ControllerCapability` (19) + `ControllerFitScope`/`RngPolicy`/
  `ArtifactPolicy` (4+4+4) + derived `portable_level` (6 levels) + `unsupported` `{cause_code, mitigation}`.
- `LOCK-RT` (`RT_spec.md`): 8 verbs + `RtResult v1` (anchored on dag-ml `ScoreSet`) + `RtRunRequest v1` +
  `RtError v1`. ScoreSet `report` = `{partition∈train|validation|test|final, level∈observation|sample|
  target|group, fold_id, variant_id, target_names, metrics}`.

**One-line thesis:** the UI does not need to be re-architected — Studio has *already* split a pure
view-model/adapter layer (the "gold") away from app-state components; LOCK-UI's job is (a) extract that
layer + the CAP/RT-derived types into an **internal Studio package** (not a new repo), (b) settle the
**primitive fork** (Studio shadcn-gen/Tailwind-v3 vs Web shadcn-gen/Tailwind-v4 — a *generation* gap no
version-pin fixes), and (c) replace the **3 coexisting status enums + 2 incompatible WebSocket
vocabularies** with the LOCK-RT envelopes. Foundation/data/pipeline are extractable now; runtime/results/
export are gated on LOCK-RT (now signed) + the FastAPI-compute push-down (L12).

---

## 0. Corrections to the prior A6 audit (verified)

| A6 claim | Verdict | Evidence |
|---|---|---|
| "`nirs4all-studio/BACKEND_RULES.md` **does not exist** — stale ecosystem-doc reference" | **WRONG** — the file exists, only the *path* in the ecosystem `CLAUDE.md` is stale. | `nirs4all-studio/docs/_internals/BACKEND_RULES.md` is present (4 mandatory rules: library-first, new-features-in-nirs4all, ask-before-implementing). The ecosystem `CLAUDE.md` link `nirs4all-studio/BACKEND_RULES.md` is the wrong path; **fix the link, not the file.** |
| Studio `ui/` = "34 primitives", Web `ui/` = "48" | **imprecise** — those are *file* counts, not primitive counts. | Studio `src/components/ui/`: **32 `.tsx`** + `badgeVariants.ts` + `buttonVariants.ts` = 34 files; `state-display.tsx` (13.2K) is an app-composite, not a primitive. Web `src/app/components/ui/`: **45 `.tsx`** + `use-mobile.ts` + `utils.ts` = 47 files. |
| A6 "FAILED (empty)" per `INTEGRATION_DIGEST_A0.md` | **stale** — A6's `.md` is present (39.8 KB) and was later integrated (sync board worklog 2026-06-30 Codex/supervisor). Only its `.log` is 0 B. This `UI_spec.md` is the formal lane report (the L11/L12 analogue of `CAP_spec.md`/`RT_spec.md`), which **did not exist** until now. |

Everything else in A6 (the gold-adapter purity, the fork, the runtime enum/WS fragmentation, the
net-new baseline, the L12 compute trap) **re-verified TRUE** at the current heads — citations inline below.

---

## 1. UI-001 — Studio stable components + probable Web consumers (verified counts)

### 1a. Verified inventory (methodology: recursive `.ts`+`.tsx` per `src/components/<domain>`)

| Domain (`src/components/…`) | files | Stability for extraction | Probable Web (studio-lite) consumer? |
|---|---:|---|---|
| `ui/` (shadcn primitives) | 34 | **stable** but **forked** (see §5) | **YES** — Web has its own 47-file `ui/` fork (convergence target) |
| `pipeline-editor/` | 230 | mixed: pure card/preview stable, canvas/DnD app-state | partial — Web has its own editor (`NodePalette`/`CanvasFlow`/`Inspector`) |
| `inspector/` | 100 | **stable presentation** over 6 React contexts | YES (2D recharts/SVG only; **not** 3D) |
| `experiments/` | 87 | P2/P3 campaign orchestration | no (Studio-only) |
| `predictions/` | 82 | **stable** table/stats/pagination | YES |
| `datasets/` | 78 | mixed (wizard/dialogs Studio-only; summary LOCK-IO) | partial (Web `DatasetView`) |
| `settings/` | 55 | app config | no (out of scope) |
| `spectra-synthesis/` | 44 | Studio-only (no Web counterpart) | no |
| `runs/` | 38 | **LOCK-RT-gated** (progress/logs/job) | partial |
| `scores/` | 32 | **stable, VM-driven** | YES |
| `results/` | 26 | **stable** metric-card family | YES |
| `predict/` | 21 | **stable** cards/table/chart | YES |
| `variable-importance/` | 14 | SHAP — **self-fetches** `@/api/shap` (P3) | no (Studio-only payoff) |
| `layout/` | 13 | app shell (router+run-context) — **stays in Studio** | no |
| `transfer-analysis/` | 9 | mixed (PCA scatter extractable) | no Web counterpart |
| `pipelines/` | 8 | card list | partial |
| `charts/` | 1 | `BaseSpectraChart` (P0 keystone shell) | YES |
| `playground/` | **292** | the 3D/WebGL spectra viewer (`three.js`+`regl`) lives here | **Web-led, later** — Studio `three.js` must **not** leak into the WASM bundle |

Whole-`src` totals (verified): **806 `.tsx`** components, **522 `.ts`** in `src/lib/`, **59** hooks,
**45** contexts.

### 1b. The extractable "gold" = the pure view-model / adapter layer (verified pure)

A6's central claim — Studio has already separated pure VM adapters from components — is **confirmed**:

- `src/lib/inspector/*Data.ts` — **15 files, ALL pure** (0 imports of `react`/`@/api`/`@/context`/
  `react-router`). `src/lib/inspector/` is 65 `.ts` total. These are the diagnostics VMs (`residualsData`,
  `predVsObsData`, `confusionMatrixData`, `scoreHistogramData`, `foldStabilityData`, `canvasScatterData`,
  `branchComparisonData`, …) — **the single biggest asset.**
- Zero-`react`/`api` (verified): `src/lib/score-adapters.ts`, `scoreValues.ts`, `scoreMetricCatalog.ts`,
  `resultArtifacts.ts`, `chartExport.ts` (**zero imports at all** — pure CSV builder), `pipelineStats.ts`,
  `canonicalPipelinePreview.ts`. Pipeline VMs `variantCounting.ts` live under
  `src/components/pipeline-editor/variantCounting.ts` (not `lib/`); the bundling hook is
  `src/hooks/useVariantCount.ts` (split the pure helper from the hook first).
- **Near-pure (one coupling to cut on extraction):** `src/lib/aggregatedResultsData.ts:1` imports
  `isClassificationTask` from `@/components/runs/modelDetailClassification` (a runtime *value* import from a
  component) — invert to a prop/param when extracting.

**Probable Web consumers (high-likelihood):** `scores/`, `results/`, `predict/`, `predictions/` presentation
+ the 2D `inspector/visualizations/*` leaves + `charts/BaseSpectraChart` + the entire `lib/inspector/*Data.ts`
adapter family. These map 1:1 onto Web's existing `RunResult`/`ScoreNode`/`PredRow` surface
(`nirs4all-web/studio-lite/src/engine/types.ts`). **Low/none:** `spectra-synthesis/`, `variable-importance/`
(SHAP), `experiments/`, `settings/` (no Web counterpart).

---

## 2. UI-002 — extraction taxonomy (7 buckets) + the empty `controllers` bucket

Roadmap `UI-002` taxonomy (`PARALLEL_REFACTORING_ROADMAP.md:435`): **foundation · data · pipeline ·
controller(s) · runtime · results · export**. Mapping each bucket to where its code *actually* lives:

| Bucket | Maps to (verified existing) | Extraction track | Gate |
|---|---|---|---|
| **foundation** | `components/ui/*` (32 primitives) + `ui/{button,badge}Variants.ts` + the de-facto form layer `pipeline-editor/shared/*` (`ParameterInput*`, `ParameterSelect`, `ValidationMessage`, `CollapsibleSection`, `InfoTooltip`); pure `cn` (after split) | **Studio-first** | **primitive decision (§5)** |
| **data** | `lib/inspector/*Data.ts` (15 pure) + `charts/BaseSpectraChart` + `inspector/visualizations/*` (2D) + `datasets/charts/*` + `lib/{datasetDomain,partitionColors,fold-utils}` | Studio-first (viz) / contract-first (summary) | viz: none; summary: **LOCK-IO** |
| **pipeline** | `pipeline-editor/{PipelineNodeContent,StepPaletteItem,PipelineEditorHeaderBadges}` + adapters `{variantCounting,pipelineStats,canonicalPipelinePreview,stepPresentation}` | Studio-first (card) | live canvas: data-model + DnD unify |
| **controller(s)** | **ZERO dedicated folder** — `src/components/controllers/` **does not exist** (verified). Capability vocab is scattered: `lib/operatorCapability.ts` (vocab) + capability badges **inlined** in `PipelineNodeContent`. The portability / controller-ownership **panel is greenfield**. | **contract-first / greenfield** | **LOCK-CAP** |
| **runtime** | `lib/websocket.ts`, `lib/run-progress/*`, `hooks/useWebSocket.ts`, `runs/{PipelineProgress,RefitPhaseIndicator,RunProgressSections,LogsPanel}` | contract-first | **LOCK-RT** |
| **results** | `scores/*`, `results/*`, `predictions/*`, `predict/*` + adapters `score-adapters`/`resultArtifacts`/`aggregatedResultsData` | Studio-first (presentation) | **LOCK-RT** (raw row shapes) |
| **export** | **no separate enum** — modeled as a *job*: `ExecutionJobRecordType` includes `"export"` (`lib/runs/executionJobRecords.ts`). Route-free piece = `chartExport` + `ResultMetricsExportAction` | contract-first | **LOCK-RT** |

**Headline finding for UI-002:** the **`controllers` bucket maps to zero existing component directory.**
It is the one genuinely greenfield layer — today "capability" surfaces only as a binary *Unavailable* badge
(`lib/operatorCapability.ts` → `isExecutableCapabilityLevel`), with no controller-ownership / portability
panel. This bucket is built **from** LOCK-CAP, not extracted.

**Extraction order (waves; only Wave 0–1 need none of the locks):**
- **Wave 0** — decisions+scaffold: rule §5 primitive decision; stand up internal `src/ui/` package; **split
  `cn`**; freeze token-NAME contract; define the **ports** (color/selection, registry, availability,
  `RuntimeEventSource`, link, theme).
- **Wave 1** — the gold: `lib/inspector/*Data.ts` + score/result/predict adapters + pipeline VMs → the
  `@nirs4all/ui` **types + adapters** layer (UI-004), reconciled against Web `engine/types.ts` + `contracts.ts`.
- **Wave 2** — Studio-first presentational leaves: `shared/` form primitives + the shadcn-intersection
  primitives (after §5) + 2D data-viz leaves + score/result/predict leaves + pipeline node-card + a new
  `<NodeBadge>` family.
- **Wave 3** — contract-first (now unblocked by LOCK-CAP+RT): runtime/progress/job/logs (LOCK-RT);
  capability/portability/controller-ownership panel (LOCK-CAP, greenfield); dataset summary (LOCK-IO);
  live canvas (data-model + DnD unification).
- **Wave 4** — strategic L11↔L12: migrate FastAPI-trapped compute **down** (§7).

---

## 3. UI-003 — package scaffold (internal Studio first) + build/test/version policy

**No `nirs4all-ui` exists anywhere** (verified: no top-level repo, no `nirs4all-studio/packages/`, no
`@nirs4all/ui` import — the two `@nirs4all/ui`-looking hits in `lib/clientStorage/keyRegistry.ts:53,63` are
storage-key *strings* `"nirs4all-ui-density"`/`"nirs4all-ui-zoom"`, not a package). This satisfies
`DEC-UI-001` "internal Studio package first, NOT a repo."

**Scaffold (proposed):**
- **Home:** `nirs4all-studio/src/ui/` (or `nirs4all-studio/packages/ui/` if a workspace boundary is wanted
  for the dep-fence). Internal path alias `@nirs4all/ui` → that dir; **no publish, no version tag** until the
  promotion bar is met.
- **Promotion bar (repo only after):** Studio re-adopts ≥1 extracted component **and** Web consumes ≥1 — the
  `DEC-UI-001` "real" bar. Until then it is a folder, not a release artifact.
- **Layering (enforced by lint):** `types/` (pure, zero deps) → `adapters/` (pure VM, depends only on
  `types/`) → `primitives/` (Radix + cva, depends on the token-NAME contract) → `components/` (composes
  primitives + adapters via injected **ports**, never `src/api`/contexts/router). A dep-cruiser/eslint
  boundary rule forbids `@/api`, `@/context`, `react-router`, `useWebSocket` inside the package.
- **Build:** the package is **source-only** inside Studio first (Vite/tsc compiles it with the app); a
  standalone build (tsup/Vite-lib, ESM + `.d.ts`) is added only at repo-promotion. **React as a peer dep**;
  target the **React-18 API floor** (works in Studio's 19 and Web's 18 — see §5(d)).
- **Test:** the package owns its own `vitest` config + the shared render harness (§6); its CI mirrors Studio's
  green gate (`lint:eslint` + `tsc --noEmit` + `vitest`). The pipeline-palette fixtures depend on the
  generated node-registry contract (`public/node-registry/extended.json` + `validate:nodes`) — replicate that
  validation in the package CI when the pipeline bucket lands.
- **Version policy:** while internal, **no semver** — it moves with Studio's commit. On repo-promotion: semver,
  changelog, and a published `@nirs4all/ui` consumed by Studio + Web as a normal dep.

---

## 4. UI-004 — pure UI types derived from CAP + RT (the contract layer)

**The seed already exists on the Web side and is the negotiating table, not a reinvention:**
`nirs4all-web/studio-lite/src/engine/types.ts` (293 lines — `TaskType`, `Partition`, `MaterializedDataset`,
`PipelineDSL`/`PipelineStep`/`ContainerNode`, `Metrics`/`ScoreNode`/`RunResult`/`FittedPipeline`/`RunProgress`/
`Engine`) + `src/components/contracts.ts` (7 prop interfaces: `DatasetUpload/View/ConfigDialog`,
`PipelineBuilder`, `ResultsList`, `ResultsVisualization`, `PredictionPanel`). Studio's equivalents are richer
but scattered across `src/types/*` + `src/lib/*`. **UI-004 = unify these onto the CAP/RT vocabularies.**

### 4a. Capability types — from LOCK-CAP (reconcile two related axes)

The UI carries its **own** capability ladder that is a **different axis** from CAP's `portable_level`:

| UI `CapabilityLevel` (`lib/operatorCapability.ts:1-7`) | CAP `portable_level` (`CAP_spec §3`) |
|---|---|
| `unavailable, metadata, plan, execute_local, execute_remote, execute_wasm` — *"can this run here, and how far?"* (`isExecutableCapabilityLevel` = `≥ execute_local`, `:107`) | `non_portable, host_specific, contract_portable, numerically_portable, artifact_portable, full` — *"is the operator/result portable across runtimes?"* |

These are **complementary, not duplicate**: the UI ladder is a per-(operator×backend) *reachability* level for
the editor palette; CAP's `portable_level` is a *classifier* over manifest enums. **UI-004 must keep both**
and define the join: a node's editor badge derives from `CapabilityLevel` (reachability in the current
runtime) **plus** `portable_level` (portability label from the manifest). The UI `OperatorBackendId`
(`local|cluster|wasm|nirs4all|n4a-methods|sklearn|custom`, `:12-20`) **already aligns** with RT's
`execution_backend` (`local-python|wasm-local|cluster`) — wire them to one enum. The 19-value
`ControllerCapability` enum is consumed verbatim as `RtResult.manifest.capabilities` and surfaced in the
greenfield controller-ownership panel (§2 `controllers` bucket).

### 4b. Result types — from LOCK-RT `RtResult` (Studio + Web both become views)

Both apps already project the dag-ml `ScoreSet`; UI-004 freezes the **view types** over `RtResult`:
- `RtResult.reports[]` = verbatim `ScoreSet.reports[]` (the `partition/level/fold_id/variant_id/target` join
  key). Studio `ChainSummary` (flat pivot) and Web `RunResult`/`ScoreNode` (nested) are deterministic
  group-bys — keep the **raw** `TopChainResult`/`ChainSummary`/`PartitionPrediction` (Studio
  `types/aggregated-predictions.ts`) and `ScoreNode`/`PredRow` (Web `engine/types.ts:202,215`) as **frozen
  view models**, with `ScoreCardRow` (Studio `types/score-cards.ts`) as the shared keystone VM.

### 4c. Status enums — the 3+ to collapse into LOCK-RT (verified)

The "runtime is genuinely un-locked" finding is **3 coexisting job/run status enums** (4–5 if you count the
results + Web variants), all with **different vocabularies**:

| Enum | Values | Source (file:line) |
|---|---|---|
| `RunStatus` | `queued, running, completed, failed, partial` | `src/types/runs.ts:7` |
| `RefitStatus` | `idle, running, completed, failed` | `src/lib/run-progress/types.ts:64` |
| `ExecutionJobRecordStatus` | `pending, running, completed, failed, cancelled` | `src/lib/runs/executionJobRecords.ts:9` |
| `PipelineRunStatus` (results variant) | `success, failed, running, pending` | `src/types/pipelines.ts:7` |
| Web `ScoreNode.status` | `completed, running, failed` | `nirs4all-web/.../engine/types.ts:222` |

**Proof they are un-unified:** `src/lib/run-progress/pageData.ts:30` literally declares
`type RunExecutionProgressDisplayStatus = ExecutionJobRecord["status"] | RunStatus` — a *runtime union of two
disjoint vocabularies* (`pending` vs `queued`, `cancelled` vs `partial`). LOCK-RT must define **one**
`JobStatus` and a phase axis (`RunProgress.phase` is yet another: Web `preprocess|fit_cv|select|refit|predict|
done`, `engine/types.ts:265`).

### 4d. WebSocket vocab — the 2 incompatible message languages (verified)

| Vocab | Shape | Source |
|---|---|---|
| **V1 — transport envelope** | strict 24-value union `MessageType` (`job_started, job_progress, job_completed/failed/cancelled, job_metrics, maintenance_*, training_epoch/batch/checkpoint, refit_started/progress/step/completed/failed, ping, pong, error, connected, subscribed, unsubscribed`) — **no schema for granular data** | `src/lib/websocket.ts:14-37` |
| **V2 — granular progress** | **`type: string` (untyped)** `WsMessage` with a fat `data{ progress, log, log_context{fold_id,total_folds,branch_name,variant_index,total_variants}, current_fold, branch_path, current_variant, step_name, step_type, score, traceback }` | `src/lib/run-progress/types.ts:4-49` |

They model the **same wire** but disagree on both the discriminator (24-value enum vs `string`) and the payload
(none vs fat granular object). LOCK-RT's job: one `RuntimeEvent` tagged union (`MessageType` ⊕ the granular
`fold_*`/`variant_*`/`log_context` fields) delivered through a transport-agnostic **`RuntimeEventSource`** port
(Studio = WebSocket, Web = in-process engine callback `RunOptions.onProgress`, `engine/types.ts:277`). This is
the single seam that lets the same progress UI serve both apps.

### 4e. Error types — from LOCK-RT `RtError` (links B-018)

UI-004 carries `RtError v1 {verb, code, cause∈{unsupported_shape, unsupported_capability,
unavailable_backend, invalid_request, runtime_error}, message, mitigation, unsupported_capability?,
portable_level?}` (RT-003). The `cause`/`mitigation`/`portable_level` vocabulary is **owned by CAP-004/CAP-002**
(referenced, not redefined). UI gate (B-018): today's **silent fallbacks** (Web `DagMlEngine` falls back to
`runPipeline` on any error; Python warn+fallback) must surface as an explicit `RtError` with `mitigation`, or
the unified UI leaks divergent UX.

---

## 5. Primitive decision — recommend **(c) headless + per-app theme** (with (d) React-18 floor)

**The fork is a shadcn *generation* gap, not a version gap — proven by `button.tsx`:**

| | Studio `src/components/ui/button.tsx` | Web `src/app/components/ui/button.tsx` |
|---|---|---|
| `data-slot` | **absent** | **`data-slot="button"`** (`:51`) |
| cva | **split** into `buttonVariants.ts` (imported `:6`) | **inline** (`:7-35`) |
| newer-gen markers | none | `focus-visible:ring-[3px]`, `aria-invalid:ring-destructive/20`, `bg-destructive text-white`, `has-[>svg]:px-3`, `size-9` (`:8,14,24,27`) |
| `cn` import | `@/lib/utils` (impure, see below) | `./utils` (pure) |

The cva **strings differ** — choosing a canonical generation will visibly restyle one app's controls. Backing
version data (verified `package.json`):

| Axis | Studio (`nirs4all-webapp`) | Web (`studio-lite`) |
|---|---|---|
| React | `^19.2.3` | `18.3.1` |
| Tailwind | **v3** `^3.4.17` (JS config, `hsl(var())`) | **v4** `4.1.12` + `@tailwindcss/vite` (CSS-first `@theme`, HEX) |
| `tailwind-merge` | `^2.6.0` | `3.2.0` |
| `cva` | `^0.7.1` | `0.7.1` (same) |
| `cn` | `src/lib/utils.ts:4` **bundled** with `formatNumber:11/formatDate:24/formatRelativeDate:36/formatBytes:53/generateId:64/debounce:71` | `ui/utils.ts` **pure** (`clsx`+`twMerge` only) |
| Real Studio customizations | `badgeVariants.ts:14-17` custom `success`/`warning`; `sonner.tsx` wired to `@/context/useTheme`; `--density-*`/`--ui-zoom`/glass/glow chrome; `framer-motion@^12` | `--brand-*`/`--paper*`/`--chart-1..5`/`n4a-*`; IBM Plex; CSS-only animation; 47-primitive superset incl. `sidebar`(21K)/`chart`/`calendar`/`carousel` |

**Options:**
- **(a) One identity — Studio migrates v3→v4, one shadcn generation.** Cost **high-Studio/low-Web**. Best if
  the ecosystem wants a single visual identity. **Con:** forces Studio to either drop or re-port its
  density/zoom/glass + `framer-motion` chrome, and re-verify every page.
- **(b) Keep v3, Web regresses to v4→v3.** **Not recommended** (fights v4 momentum; Web is the WASM-constrained
  consumer).
- **(c) Headless + per-app theme.** Package ships **behavior/structure only** (Radix wrappers + cva slots
  referencing semantic `--color-*` token *names*), pins **one** Radix set + **one** shadcn generation;
  **ships no theme, no fonts, no motion.** Each app keeps its `theme.css`/chrome. Cost **medium-both**.
- **(d) React-18 API floor** — combine with (a) or (c); author to the 18 API, pin Radix supporting 18+19.

**RECOMMENDATION: (c) + (d).** Rationale, grounded in the verified divergence and the WASM constraint (§7):
1. The two themes are **intentionally different products**, not accidental drift — cool-slate + density/zoom/
   glass + `framer-motion` (Studio) vs warm-paper + IBM Plex + brand-spectrum + CSS-only motion (Web). "One
   identity" (a) would have to erase one of them.
2. The **WASM bundle cannot afford** Studio's `framer-motion`/`three.js`/glass chrome; a shared package that
   shipped *one identity* would drag Studio's weight into Web or strip Web's lean theme. A **theme-less,
   motion-less headless** package is exactly what the WASM-portability rule (§7) requires.
3. The cross-language future (R/MATLAB/WASM bindings of the lite stack) makes a single React visual identity
   meaningless anyway — only the **token-NAME contract + behavior** travel.
4. (c) works **across the v3/v4 split**: the package ships cva slots + a frozen token-NAME contract; Studio maps
   the names via `hsl(var())` in `tailwind.config`, Web via `@theme` — neither app's toolchain is forced to
   move. Pick the **newer (Web/v4-aligned) shadcn generation** as canonical so the forward direction wins;
   Studio re-verifies its 32 primitives once but keeps its v3 toolchain + chrome.

**Non-negotiable prerequisites for *any* option (do in Wave 0):** (i) **split `cn`** into a pure module
(`lib/utils.ts:4` today drags 6 app helpers); (ii) **freeze a token-NAME contract** (`success`/`warning`,
`--sidebar` vs `--sidebar-background`, `--radius`, `--color-*`); (iii) **pick one shadcn generation.** The
shared surface is the **31-primitive intersection**, never the union (the union forces Studio to pull
`react-day-picker`/`embla`/`vaul`/`input-otp` it has no use for).

---

## 6. Visual baseline — recommend **Playwright `toHaveScreenshot` (CT, per-theme)**, Storybook optional

**State today (verified, both repos): no baseline of any kind.** No `.storybook/` dir, no `*.stories.*`, **zero**
`toHaveScreenshot`/`toMatchSnapshot` in `nirs4all-studio/src` + `e2e`, no `storybook` dependency. Studio's
render tests are a copy-pasted `createRoot`+`act` harness (no `@testing-library`); the `shared/` foundation
primitives have prop-shape tests only. Playwright is functional E2E on the real FastAPI+Vite stack with
`screenshot: only-on-failure` (debug, not baseline). studio-lite has node-only Vitest numerics + functional
`*smoke.mjs`; `tests/shots.mjs` is a one-off screenshot with no diff. **The baseline is net-new** — there is
nothing to revive.

`DEC-UI-001` (accepted) already names **Playwright `toHaveScreenshot`** as the baseline tool. This audit
**concurs** and refines it into a tiered, additive plan (the v3/v4 split means a single pixel baseline cannot be
shared across the two apps):

| Tier | Tool | Catches | v3/v4 split | When |
|---|---|---|---|---|
| **0 (prereq)** | shared render harness (`@testing-library/react`) | — replaces the copy-paste harness | n/a | Wave 0 |
| **1** | **Vitest+jsdom DOM snapshots** | DOM/markup | **survives v3/v4 for free** (shadcn class names identical at markup level) | Wave 0–1, ~0.5d |
| **2** | **Playwright-CT `toHaveScreenshot`**, **per-theme baselines** | pixels, no backend | **separate baseline per theme** (don't share v3/v4) | after §5, fonts/AA pinned in the CI Docker image |

**Storybook is NOT recommended as the gate** — `UI-009`/design need a *baseline*, not a gallery; Storybook is
high-setup (gone today) and optional doc value only (the `pipeline-editor/shared/demo.tsx` gallery is a
sufficient seed if wanted later). **Fixtures:** promote the adapters' existing test factories (e.g.
`inspector-confusionMatrixData.test.ts`) to a shared `__fixtures__` module + `public/node-registry/
extended.json` for palette fixtures + Web `contracts.ts` as the cross-repo prop contract. **Canonical states
per component:** `empty · loading · populated · error · dark · overflow · dense/large-N`. **First slice
(~2.5–3d):** `shared/{CollapsibleSection, InfoTooltip, ValidationMessage}` + `ConfusionMatrix` + `ScoreCardRow`
(also Wave-1/2 extraction targets — double-validated).

---

## 7. L11 ↔ L12 coupling — WASM portability requires pushing compute *down* (B-017)

L11 (extract UI) is strategically welded to L12 (Studio reassembly) and the North Star. The components that
*look* portable to the WASM client are blocked not by the UI but by **NIRS/ML compute trapped in the FastAPI
layer with no home in `nirs4all`/`dag-ml`** — a direct `BACKEND_RULES.md` violation (Rule 2: new features go in
`nirs4all`). A component becomes WASM-reusable **only after its math migrates down.**

**Verified compute hotspots (the L12 → North-Star push-down list, = sync board B-017):**

| FastAPI module | In-backend compute that belongs *down* | Severity |
|---|---|---|
| `api/shared/metrics_computer.py` | spectral descriptors invented in-backend (`l2_norm`, `rms`, `auc`, `peak_count`, `snr`, smoothness) — no home in `nirs4all` | **HIGH** |
| `api/analysis.py` | PCA / t-SNE / UMAP / correlation / `mutual_info` / `f_regression` in a router | **HIGH** |
| `api/playground/executor.py` | a **mini step-runner "without full StepRunner"** — a parallel pipeline path | HIGH/MED |
| `api/playground/charts.py` | per-wavelength stats, UMAP, Mahalanobis, confidence ellipses | HIGH/MED |
| `api/spectra.py` | `_apply_preprocessing_chain` + per-wavelength stats | MED-HIGH |
| `api/{datasets,evaluation,preprocessing,inspector,pipeline_canonical}.py` | spectral stats / confusion+skew/kurtosis / preview `fit_transform` / results analytics / "backend-authoritative" canonicalization | MED |

Per-wavelength summary stats are **recomputed in ≥5 modules** — duplicated and trapped. **Appropriately thin
(delegate correctly):** `runs.py`→`nirs4all.run`, `automl.py`, `predict.py`, `synthesis.py`,
`store_adapter`/`aggregated_predictions`, `recommended_config`, `workspace/*`, `system.py`,
`websocket/manager`, `jobs/manager`.

**Consequence for L11 (ranked):**
1. **Results/Inspector/Predictions UI is non-portable on *two* axes** — welded to the SQLite `WorkspaceStore`
   **and** backend-side analytics. The most-wanted components are the least extractable.
2. **Playground/Spectra/Analysis UI calls stateless-*looking* routes whose math is in FastAPI** → portable only
   after Wave-4 push-down.
3. **Run/runtime UI depends on the job-queue + WS progress model** — no WASM equivalent; this is *why* LOCK-RT
   must define a transport-agnostic `RuntimeEventSource` (§4d).
4. Every extracted component must reach the engine through an **injected port**, never `src/api` /
   `lib/websocket.ts` directly.

**Push-down is owned jointly by L5 (dag-ml) / L16 (controllers) / L12 — surface it on the L11 schedule** because
UI portability *depends* on it. The portable-route candidates (`predict`, `playground/execute`, `analysis/*`,
`preprocessing/apply`, `evaluation/*`, `transfer`, `datasets/detect-*`) are exactly the LOCK-RT
common-runtime-API surface.

---

## 8. Proposed `LOCK-UI` content (for A0 to sign)

```
LOCK-UI (nirs4all-ui extraction taxonomy + primitive policy + visual baseline) — DEC-UI-001 accepted (ARB-007=A).
Owner: UI-SPEC. Consumes LOCK-CAP + LOCK-RT (both SIGNED) as referenced vocabularies, never redefined.

U1. PACKAGE HOME. nirs4all-ui starts as an INTERNAL Studio package (src/ui/ or packages/ui/), alias
    @nirs4all/ui, NO repo / NO publish / NO semver until Studio re-adopts >=1 component AND Web consumes
    >=1 (the DEC-UI-001 "real" bar). Layering types/ -> adapters/ -> primitives/ -> components/, with an
    eslint/dep boundary forbidding @/api, @/context, react-router, useWebSocket inside the package.

U2. TAXONOMY = foundation, data, pipeline, controllers, runtime, results, export (roadmap UI-002). The
    `controllers` bucket maps to ZERO existing folder (verified: no src/components/controllers/) — it is
    BUILT from LOCK-CAP (capability/portability/controller-ownership panel = greenfield), not extracted.

U3. EXTRACTION ORDER = Wave0 (decisions+scaffold: split cn, freeze token-NAME contract, define ports) ->
    Wave1 (the gold: lib/inspector/*Data.ts + score/result/predict adapters + pipeline VMs = the UI-004
    types+adapters layer) -> Wave2 (Studio-first presentational leaves + primitives) -> Wave3 (contract-
    first: runtime/results/export = LOCK-RT, controllers = LOCK-CAP, dataset summary = LOCK-IO) -> Wave4
    (push FastAPI-trapped compute DOWN). Wave0-1 need NONE of the locks and start now.

U4. UI-004 TYPES are DERIVED from CAP+RT, seeded by Web engine/types.ts + contracts.ts (the negotiating
    table). Keep BOTH capability axes distinct: UI CapabilityLevel (reachability: unavailable..execute_wasm)
    AND CAP portable_level (portability: non_portable..full); join them for the node badge. Result types =
    views over RtResult (Studio ChainSummary pivot, Web RunResult nest). Collapse the 3+ status enums
    (RunStatus/RefitStatus/ExecutionJobRecordStatus + PipelineRunStatus + Web ScoreNode.status) into ONE
    LOCK-RT JobStatus, and the 2 WS vocabularies (websocket.ts MessageType ⊕ run-progress WsMessage) into
    ONE RuntimeEvent delivered via a transport-agnostic RuntimeEventSource port. Errors = RtError (silent
    fallbacks become explicit, B-018).

U5. PRIMITIVE POLICY = (c) HEADLESS + per-app theme + (d) React-18 API floor. The fork is a shadcn
    GENERATION gap (button.tsx: data-slot + ring-[3px] vs split buttonVariants), not a version gap — no pin
    fixes it. The package ships behavior/structure only (Radix + cva slots over a frozen token-NAME
    contract), NO theme / NO fonts / NO motion; each app keeps its chrome (Studio density/zoom/glass +
    framer-motion; Web brand-spectrum/IBM-Plex/CSS-motion). Pick the NEWER (Web/v4-aligned) shadcn
    generation as canonical; shared surface = the 31-primitive intersection, not the union. Prereqs: split
    cn (lib/utils.ts), freeze token-NAME contract, pick one generation.
    [Alternative on file: (a) one-identity (Studio migrates v3->v4) — choose only if a single visual
     identity across Studio+Web is an explicit product goal.]

U6. VISUAL BASELINE = NET-NEW (Storybook gone, zero snapshots). Tool = Playwright toHaveScreenshot (CT,
    PER-THEME baselines), additive to the green gate. Tier0 shared render harness -> Tier1 Vitest+jsdom DOM
    snapshots (survive the v3/v4 split) -> Tier2 Playwright-CT pixels per theme (fonts/AA pinned in CI
    Docker). Storybook is OPTIONAL doc value, NOT the gate. Fixtures reuse the adapters' test factories.

U7. L11<->L12 COUPLING. UI portability to the WASM client DEPENDS on migrating FastAPI-trapped compute down
    (B-017: metrics_computer/analysis/playground.executor/charts/spectra/...). Extracted components reach the
    engine ONLY through injected ports, never src/api or lib/websocket directly. Push-down scheduled with L11.

U8. DOC FIX (out of band): the ecosystem CLAUDE.md link "nirs4all-studio/BACKEND_RULES.md" is the wrong path;
    the file lives at nirs4all-studio/docs/_internals/BACKEND_RULES.md. Fix the link.
```

---

## 9. Open questions + gates

**Open questions (for A0 / maintainer):**
1. **Primitive strategy (B-016):** ratify **(c)+(d) headless+theme** (recommended) vs **(a)+(d) one-identity**?
   And confirm the **newer (Web/v4) shadcn generation** is canonical (Studio re-verifies its 32 primitives).
2. **Token-NAME contract owner:** who freezes `success`/`warning`, `--sidebar*`, `--radius`, `--color-*` — the
   package, or a shared `nirs4all-org` design token source? Gate for the entire foundation layer.
3. **Capability double-axis:** confirm UI-004 keeps **both** `CapabilityLevel` (reachability) and CAP
   `portable_level` (portability) and defines their join for the node badge — or collapse to one? (CAP owns
   `portable_level`; do not fork it.)
4. **Silent-fallback policy (B-018):** must Web (`DagMlEngine` → `runPipeline`) and Python (warn+fallback)
   convert fallback into an explicit `RtError` at the RT boundary? Affects the unsupported ledger + UX.
5. **Compute push-down scheduling (B-017):** is the Wave-4 FastAPI→`nirs4all`/`dag-ml` migration scheduled
   *with* L11 given the portability coupling, and who owns it (L5/L16/L12)?
6. **3D spectra viewer:** does `playground/visualizations/` (292-file dir; `three.js`+`regl`) get a companion
   audit before any "spectra" component is called complete? It must **not** leak `three.js` into the WASM bundle.
7. **`RtResult` home repo (inherited from RT open-Q1):** UI-004 result types reference `RtResult`; its package
   home (ecosystem spec vs shared contract) is unresolved (`DEC-DESIGN-001`/`ARB-013`). UI can ship against the
   spec and defer.

**Gates to run (none run here — read-only audit):**
- `npm run lint:parallel` (eslint + `tsc --noEmit` + `validate:nodes` + ruff + dep-sync) — Studio green gate.
- `npm run test:parallel` (Vitest frontend/electron + pytest backend); add the **shared render harness** + the
  Tier-1 DOM-snapshot suite to this gate (§6).
- `npm run validate:nodes` — the generated node-registry contract the pipeline-palette fixtures depend on; must
  be replicated in the package CI when the pipeline bucket lands.
- Web (`nirs4all-web/studio-lite`): `npm run typecheck` + `npm run test` + `npm run validate:catalog` +
  `tests/*smoke.mjs` — the cross-repo proof that an extracted component still runs in the WASM client.
- On §5 sign-off: a one-page-restyle smoke (the chosen shadcn generation visibly restyles one app's controls —
  verify per-theme).

**Worklog line (for A0 to paste into the sync board — I did not edit it):**
`2026-06-30 | UI-SPEC/L11+L12 | review | UI_spec.md: UI-001 verified component inventory + gold pure-adapter layer (inspector/*Data.ts 15 pure), UI-002 7-bucket taxonomy (controllers=ZERO folder), UI-003 internal-Studio-package scaffold+policy, UI-004 types derived from CAP+RT (dual capability axis, RtResult views, 3 status enums + 2 WS vocabularies to collapse), primitive decision = (c) headless+theme+(d) React-18 floor with button.tsx shadcn-generation fork proof, net-new baseline = Playwright toHaveScreenshot per-theme, L11<->L12 compute push-down (B-017). Corrected A6: BACKEND_RULES.md EXISTS at docs/_internals/. | read-only; no gates run; no code/sync edits. | Maintainer: rule B-016 primitive (a/c); B-018 RtError fallback; B-017 push-down schedule. LOCK-CAP+LOCK-RT already signed -> Wave0-1 unblocked now.`

---

### Evidence (heads, read-only; only this file written)
Studio `2ccbf68`: `src/components/ui/{button,badgeVariants}.tsx/.ts`, `src/lib/{utils,websocket,operatorCapability,
chartExport,score-adapters,aggregatedResultsData}.ts`, `src/lib/inspector/*Data.ts`, `src/lib/run-progress/{types,
pageData}.ts`, `src/lib/runs/executionJobRecords.ts`, `src/types/{runs,pipelines}.ts`, `src/components/pipeline-editor/
variantCounting.ts`, `docs/_internals/BACKEND_RULES.md`, `package.json`. Web `745eef8`: `studio-lite/src/engine/types.ts`,
`studio-lite/src/components/contracts.ts`, `studio-lite/src/app/components/ui/{button,utils}.tsx/.ts`, `package.json`.
Contracts: `CAP_spec.md`, `RT_spec.md`, `PARALLEL_REFACTORING_SYNC.md` (L11/L12/LOCK-UI/DEC-UI-001/B-016..B-018),
`PARALLEL_REFACTORING_ROADMAP.md` (UI-001..010). Prior audit: `A6_A6-studio-ui.md` (claims re-verified).
