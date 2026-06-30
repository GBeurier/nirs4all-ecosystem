# A6 report — Studio UI extraction audit (L11 `nirs4all-ui` + L12 Studio reassembly)

**Date:** 2026-06-30
**Workspace:** `/home/delete/nirs4all` (sibling repos, not a monorepo)
**Mode:** Multi-CLI report mode — read-only audit. No implementation code modified; `PARALLEL_REFACTORING_SYNC.md` NOT edited (handoff for A0 in §11). Only this report file was written.
**Repos in scope:** `nirs4all-studio` (React 19, the source of components) and `nirs4all-web/studio-lite` (React 18 WASM client, the prospective second consumer). Baseline heads per A1 preflight: studio `2ccbf68`, web `745eef8` (both clean / PRE-2 pristine).
**Method:** CodeGraph + direct `rg`/`Read` verification, fanned out across six read-only sub-audits (foundation/tokens, data, pipeline/controller, runtime+results+export, backend-orchestration, visual-baseline). Conclusions below are the synthesis; per-domain evidence tables follow.

---

## 0. Executive summary

1. **Do NOT create the `nirs4all-ui` repo yet.** Design `§10.2` and the sync board agree, and this audit confirms it: the precondition is a reconciled UI type contract (UI-004), not a package scaffold. Start as an **internal package inside Studio** (`src/ui/` or `packages/ui/`); promote to a repo only after Studio re-adopts ≥1 extracted component and Web consumes one (the `§10.3`/`§10.4` "real" bar). This satisfies the prompt constraint *"Ne cree pas `nirs4all-ui` sans DEC-UI accepte."*

2. **The extractable gold is the pure view-model layer, and Studio has already built it.** Across every domain, Studio separates `*Data.ts`/`*Presentation.ts` adapters (zero React/IO) from components: 73/74 `lib/inspector/*` are pure; `score-adapters`/`resultArtifacts`/`scoreValues`/`chartExport` are zero-import; pipeline `operatorCapability`/`variantCounting`/`pipelineStats`/`canonicalPipelinePreview` are pure. Studio has effectively pre-done the `§10.3` "separate pure view from app state" step. **Extract the adapters + types first; components second.**

3. **One uniform extraction recipe:** `wrapper (stays) → pure leaf (extract) → pure adapter (extract)`. It recurs verbatim in data (`*Chart.tsx` ctx-wrapper → `*RechartsPlot/*Svg` leaf → `*Data.ts`), pipeline (`PipelineNode` dnd-wrapper → `PipelineNodeContent` card → `PipelineNodePresentation`), and results (`Score*Card` → `ScoreCardRow` VM ← `score-adapters`). The blocker is always the same shape: **app-state arrives via context/hook; the pure leaf already accepts the equivalent as props.** A small set of injected **ports** (color/selection, registry, availability, runtime-event-source, link, theme) is the universal dependency-inversion seam.

4. **The Studio-first vs contract-first line is now empirical.** Foundation, data-viz leaves, and the entire score/result/predict *presentation* are extractable **now** (pure, VM-driven). Everything touching the **runtime** is genuinely un-locked: the codebase carries **3 coexisting job-status enums and 2 incompatible WebSocket message vocabularies** — that fragmentation *is* the content LOCK-RT must unify. Pipeline capability UI is **LOCK-CAP**-gated (vocab drafted in `operatorCapability.ts`, not locked; the portability/controller-ownership panel is **greenfield**). Dataset summary is **LOCK-IO**-gated.

5. **Web is a fork, not a blank consumer — "extraction" is really "convergence of two living codebases."** studio-lite has independently re-implemented dataset view, spectra, histogram, PCA, confusion/residual/parity, a **native raw-WebGL 3D scatter (no three/regl)**, a parallel pipeline editor with its own `PipelineDSL`/`catalog` model, a **newer shadcn generation**, and a **drifted theme**. The schedule risk is underestimating this. Mitigation everyone converges on: extract **pure contracts + adapters first**, treat studio-lite's `src/components/contracts.ts` + `src/engine/types.ts` as the **negotiating table** for UI-004.

6. **The primitive layer is a bidirectional fork that no version-pin can fix** (see `§3`): Studio = React 19 / Tailwind **v3** / HSL-triple tokens / older shadcn gen / `--radius:0.75rem` / density+zoom+glass chrome; Web = React 18 / Tailwind **v4** / hex tokens / newer shadcn gen / `--radius:1rem` / brand-spectrum+chart chrome + a *fuller* 47-primitive set. The component *bodies* differ by shadcn generation, so reconciling them will visibly restyle one app. This is the **"primitive decision"** LOCK-UI requires — presented as options in `§3`, not decided here.

7. **L11 (UI) is strategically coupled to L12 / the north star.** The backend audit shows the UI domains that *look* portable (playground/analysis/spectra/preprocessing) are blocked not by the UI but by **computation trapped in the FastAPI layer** (spectral descriptors in `metrics_computer.py`; PCA/t-SNE/UMAP in `analysis.py`; a mini step-runner in `playground/executor.py`; per-wavelength stats duplicated across ≥5 modules) that has **no home in `nirs4all`**. A component becomes reusable on the WASM client only **after its compute migrates down** — exactly the north-star "push algorithmic/coordination logic into dag-ml/nirs4all/io" work.

8. **Visual baseline is net-new** (`§7`): Storybook is fully gone, there are **zero** snapshots (DOM or pixel) in either repo, and Studio's test harness is copy-pasted `createRoot`/`act` with no `@testing-library`. Recommended path: a shared render harness → cheap **Vitest+jsdom DOM snapshots** (the only tier that survives the v3/v4 split for free) → **Playwright-CT pixels with per-theme baselines** later. Fixtures come free from the adapters' existing test factories.

**What this report supplies toward `LOCK-UI = UI-001 + UI-002 + LOCK-CAP + LOCK-RT + primitive decision + visual-baseline infra`:** UI-001 (`§2`), UI-002 taxonomy+order (`§4`/`§5`), the **primitive decision** input (`§3`), and the **visual-baseline infra** proposal (`§7`). LOCK-CAP / LOCK-RT remain external and blocked.

---

## 1. Scope, taxonomy, and alignment

Audited (component counts): `components/{datasets 78, spectra-synthesis 44, inspector 100, transfer-analysis 9, variable-importance 14, charts 1, pipeline-editor 230, pipelines 8, runs 38, results 26, scores 32, predictions 82, predict 21, experiments 87, ui 34, layout 13}` + `lib/` (~130 modules), `hooks/` (~60), `context/` (~30), `data/nodes/`, the `api/` backend + `src/api/` client. Lighter-touch / out-of-scope-by-boundary: `settings/` (55, app config), `setup/` (6, install wizard), `experiments/` (campaign/launch orchestration — mostly P2/P3, low extraction value), and the **`playground/visualizations/` 3D/WebGL stack (~90 files)** which holds the genuinely-reusable *spectra viewer* but sits outside the six "data" dirs — flagged for a **companion audit** (Risk, `§9`).

**Taxonomy** — use the canonical design `§10.2` seven layers (the prompt's "layout" folds into `foundation`/product-shell):
`foundation · data · pipeline · controllers · runtime · results · export`.

The audit classifies every component on: **purity** `P0` pure-presentational / `P1` view-model-coupled (pure adapter, no I/O) / `P2` app-or-editor-state (query/context/router/dnd) / `P3` backend-route-coupled (`src/api/*`); **track** Studio-first vs Contract-first; **web-likelihood** H/M/L. Design `§10.2` rule honored: *"runtime/results/export depend on LOCK-RT; foundation/data/pipeline can be extracted earlier."*

---

## 2. Component inventory by domain (UI-001)

### 2.1 Foundation (primitives + tokens + form layer)
- **shadcn primitives** `components/ui/*` (34): ~94% stock. Real customizations only: `badgeVariants.ts` (custom `success`/`warning` cva variants), `sonner.tsx` (wired to `@/context/useTheme`). **Not primitives:** `state-display.tsx` (13 app composites — `react-router` `Link`, hardcoded routes `/settings`/`/editor`, nirs4all copy) → **excluded** (`§10.1` product routing). Vestigial deps: `@radix-ui/react-avatar`, `-toast` (declared, no file).
- **`cn` is impure:** `lib/utils.ts` bundles `cn` with 6 app helpers (`formatNumber/Date/RelativeDate/Bytes`, `generateId`, `debounce`) → **must split `cn` into a pure module** (Web's `cn` is already pure). `tailwind-merge` major skew (Studio v2 / Web v3).
- **De-facto foundation form layer:** `components/pipeline-editor/shared/` — `ParameterInputComponent`, `ParameterSelect`, `ParameterSwitch`, `ValidationMessage`, `CollapsibleSection`, `InfoTooltip` (all P0, prop-driven) + a `demo.tsx` gallery. **Independently flagged by both the pipeline and visual-baseline audits** as the first extraction *and* first baseline slice. Currently has **no render-test coverage** (prop-shape tests only).
- Tokens: see `§3`.

### 2.2 Data
- Pattern: `*Chart.tsx` (P2, consumes the 6 Inspector contexts) → `*RechartsPlot.tsx`/`*Svg.tsx` (P0/P1 pure leaf, takes data+color callbacks) → `lib/inspector/*Data.ts` (pure adapter). ~65% of ~160 in-scope `.tsx` are P0/P1.
- **GOLD adapters (extraction-ready):** all in-scope `lib/dataset*`, `datasetDomain`, `partitionColors` (zero-import), `fold-utils`, and the **`lib/inspector/*Data.ts`/`*Presentation.ts` family (73/74 pure)** — `residualsData`, `predVsObsData`, `confusionMatrixData`, `scoreHistogramData`, `foldStabilityData`, `canvasScatterData`, `branchComparisonData`, plus the `chartInputs`/`chartRegistry`/`analytics`/`statistics`/`coloring`/`grouping`/`filtering` engine. **The single biggest asset.**
- **Extractable leaves:** `charts/BaseSpectraChart` (P0 keystone shell), `datasets/charts/{SpectraChart,TargetHistogram}`, `inspector/visualizations/{ConfusionMatrixSvg, ResidualsRechartsPlot, PredVsObsRechartsPlot, ScoreHistogramPlot, CanvasScatter, FoldStabilitySvg}`, `transfer-analysis/visualizations/TransferPCAScatter`, `PartitionToggle`, `InspectorOverviewCards`, `DiagnosticsSection`.
- **Blockers:** the **6 Inspector contexts** (`context/Inspector{Color,Data,Filter,Selection,Session,View}Context`) weld ~30 P2 wrappers; the leaves already accept the equivalent as props → invert context→props. `variable-importance/*` SHAP charts **self-fetch** from `@/api/shap` (P3). `datasets/DatasetWizard/*`, dialogs, `DatasetCard` (router+api) stay in Studio.
- **3D:** Studio's real spectra/scatter viewer is `three.js + @react-three/* + regl` in `playground/visualizations/` (heavy). studio-lite re-implements 3D in **raw WebGL, ships only recharts**. → **Do not share 3D via three.js** (the WASM bundle would reject it); 2D recharts/SVG/canvas is the shareable surface; 3D is a later, web-led track.

### 2.3 Pipeline + controllers
- **Neither canvas uses React Flow.** Studio = custom `@dnd-kit` + Framer Motion reorderable list; Web = native HTML5 DnD + its own model. The node-card split is **already done**: `PipelineNodeContent.tsx` (P1 pure card body) vs `PipelineNode.tsx` (P2 dnd/context wrapper). But sweep/tune/generator badges are **inlined** in the card → "extract a `<NodeBadge>` family" is the high-value micro-refactor.
- **LOCK-CAP draft home:** `lib/operatorCapability.ts` — `CAPABILITY_LEVELS = [unavailable, metadata, plan, execute_local, execute_remote, execute_wasm]`, `OperatorBackendId`, `OperatorImplementationRef`, `OperatorCapabilityResolution` (pure; `NodeDefinition.capabilities` references it). The capability **vocab** is extractable; the UI-007 **portability panel / controller-ownership display is greenfield** (capability today is only a binary "Unavailable" badge).
- **GOLD adapters:** `operatorCapability`, `editorGraphDocument` (v1), `pipelineGraphSpec` (v1), `pipelineGraphReducer`, `canonicalPipelinePreview`, `pipelineExecutionContract`, `pipelineComplexityPreview`, `pipelineStats`, `variantCounting`, `executionPreviewPresentation`, `stepFactory`, `stepPresentation`.
- **Extractable leaves:** `PipelineNodeContent`, `StepPaletteItem` (card body), `PipelineEditorHeaderBadges`, `ExecutionPreviewPanel`, `FinetuningBadge`, the `shared/` form primitives (§2.1), `PipelineCard` (inject `linkComponent`).
- **Blockers:** LOCK-CAP (B1); the **generated node-registry contract** (`data/nodes/`, `public/node-registry/extended.json`, Python introspection, `validate:nodes`) (B2); **two divergent `NodeDefinition` types** (canonical `data/nodes/types.ts` vs slimmer editor `useNodeRegistry.ts`) (B3); registry/availability are **React contexts → ports** (B4); **DnD strategy mismatch** `@dnd-kit` vs HTML5 (B5); `useVariantCount.ts` bundles pure helpers with the hook (split first) (B6); divergent web data model (B7).

### 2.4 Runtime · results · predictions · export
- **Studio-first NOW (pure, VM-driven):** the entire `scores/` cluster (minus `DatasetResultCard`, `ModelActionMenu`), the `results/` metric-card family (`ResultMetricCardGrid`, `ResultMetricsExecutionTimes/ArtifactSummary`, `AggregatedResultsStatsBar/TableRow`), `predict/` (`PredictResultsCards/Table`, `PredictChartPanel`), `predictions/` (`PredictionsTable/Stats/Pagination`, `SortableHeader`). Covers UI-008 archetypes *metrics tables, artifact/result cards* fully.
- **GOLD adapters:** `score-adapters*` (TopChainResult/PartitionPrediction → `ScoreCardRow`), `scoreMetricCatalog`, `scoreValues`/`scores`, `scoreRowData`/`scoreCardRowPresentation`/`scoreColumnData`, `resultArtifacts` (27K → `ResultArtifactRef`), `aggregatedResultsData`/`resultsPageData`, `predict-metrics`, **`chartExport` (zero-import CSV builder)**. Two are pure-but-runtime-parametrized: `run-progress-display`, `run-progress/reducer`.
- **LOCK-RT-gated:** `lib/websocket.ts`, `hooks/useWebSocket.ts`, `lib/run-progress/*`, and the UI bound to raw run payloads — `PipelineProgress`, `RefitPhaseIndicator`, `RunProgressSections`, `LogsPanel`, plus `MetricsCard`/`StatusBadge` (re-export the `RunStatus`/`RunMetrics` shapes). Route-coupled actions (`RunItem`, `DatasetResultCard`, `ExportDialog`, `ModelActionMenu`) are P3.
- **Export** is modeled as a **job** (`ExecutionJobRecordType` includes `"export"`); no separate enum. `chartExport`+`ResultMetricsExportAction` is the only route-free export piece.
- **Hidden P3 in P0/P1 trees:** `AggregatedResultsTableRow` (P1) embeds `ModelActionMenu` (P3); split via render-prop/slot or it drags `src/api` into the package.

### 2.5 Layout (verified)
`layout/` = app shell: `AppLayout`/`AppSidebar`/`MobileSidebar`/`FloatingRunWidget` are router + run-context coupled → **stays in Studio** per `§10.1` (product routing). Only generic panel/tab/list primitives belong in `foundation`. Note even here the pure-VM pattern holds (`BackendStartupBannerData.ts`, `FloatingRunWidgetData.ts` split out).

---

## 3. Primitive & token divergence — the "primitive decision" input (UI-002)

**The headline: it is two different shadcn *generations*, not a version gap.** Studio ships the older gen (`shadow`, `focus-visible:ring-1`, `transition-colors`, no `data-slot`, cva split into `*Variants.ts`); Web ships the newer gen (`data-slot`, `aria-invalid:*`, `focus-visible:ring-[3px]`, `text-white`, cva inline). Pinning versions cannot reconcile them — the bodies differ; choosing a canonical generation **will visibly restyle one app's controls.**

| Axis | Studio (`nirs4all-webapp`) | Web (`studio-lite`) | Severity |
|---|---|---|---|
| React / react-dom | `^19.2` | `18.3.1` | major |
| Tailwind | **v3** `^3.4.17`, JS `tailwind.config.ts`, `hsl(var())` | **v4** `4.1.12`, CSS-first `@theme`/`@source`, HEX | **paradigm** |
| TW build / animate | PostCSS + `tailwindcss-animate` | `@tailwindcss/vite` + `tw-animate-css` | full |
| Motion | `framer-motion@^12` | none (CSS `n4a-*`) | Studio-only |
| Theme switch | `@/context/useTheme` | `next-themes` | provider seam (esp. `sonner`) |
| shadcn generation | older | newer (`data-slot`/`aria-invalid`/`ring-[3px]`) | **bodies differ** |
| `cn` | `lib/utils.ts` (+6 app helpers), `@/lib` alias | `app/components/ui/utils.ts` (pure), rel | split needed |
| `tailwind-merge` | `^2.6` | `3.2` | major |
| Token format | HSL channels | HEX | conversion |
| canvas / radius / base font / display font | cool-slate `210 40% 98%` / `0.75rem` / ~14px / none | warm-paper `#faf7f0` / `1rem` / 15px / **IBM Plex** | value drift |
| Primitive set | 34 | **48** (16 surplus: `sidebar` 21K, `chart`, `calendar`, `carousel`, `form`, `drawer`, `menubar`, `navigation-menu`, `pagination`…) | surface mismatch |
| Radix per-primitive | caret `^`, newer (dialog `^1.1.15`, checkbox `^1.3.3`, slider `^1.3.6`, tooltip `^1.2.8`) | pinned, older (dialog `1.1.6`, checkbox `1.1.4`, slider `1.2.3`, tooltip `1.1.8`) | consistent skew |
| Studio-only token systems | `--density-*` (compact/spacious), `--ui-zoom`, glass/glow/gradient | — | scope risk |
| Web-only token systems | `--brand-*`, `--paper*`, `--chart-1..5`, `n4a-*` motifs | — | scope risk |

**Shared surface = the 31-primitive intersection**, not the union (the union forces Studio to pull `react-day-picker`/`embla`/`vaul`/`input-otp` it doesn't use).

**Primitive-decision OPTIONS (input only — for the maintainer / DEC-UI-001):**

- **(a) Standardize on Tailwind v4 + one shadcn generation; Studio migrates v3→v4.** Cost **high-Studio / low-Web**. Studio rewrites config→`@theme`, swaps animate lib, ports density/zoom/glass to v4 CSS, re-verifies every page. Best if the ecosystem wants **one visual identity** and to move with v4 momentum (the rest of the stack — org/datasets/web — is already on the family theme).
- **(b) Keep v3; Web re-adapts v4→v3.** Cost **high-Web / low-Studio**. Regresses Web onto the older toolchain; fights v4 momentum. **Not recommended.**
- **(c) Ship headless, token-less primitives + per-app theme.** `nirs4all-ui` exports behavior/structure (Radix wrappers + cva slots referencing `--color-*` semantic tokens), pins **one** Radix set + **one** shadcn generation; each app keeps its own `theme.css`/`index.css`, fonts, and chrome (density/zoom vs brand-spectrum). Cost **medium-both**. The token *value* drift becomes **intended per-app theming**. **Best fit for the observed two-brand reality** (cool-slate Studio vs warm-paper Web).
- **(d) React-18 API floor** (combine with a or c): author to the React-18 API, pin Radix supporting 18+19. Low cost if adopted up front.

**A6 lean:** if the goal is a single shared identity → **(a)+(d)**; if Studio and Web are intentionally distinct brands (which the drifted themes suggest) → **(c)+(d)**. Either way: **freeze a token-NAME contract** (`success`/`warning`, `--sidebar` vs `--sidebar-background`, radius, `--color-*`) and pick **one shadcn generation** before extracting any primitive. **This is the gating decision for the foundation layer.**

---

## 4. Extraction order (UI-002) — consolidated cross-domain plan

> Every wave follows `§10.3`: INV → CUT → FIX (fixtures) → PKG → ADOPT-in-Studio → TEST (Vitest + visual baseline + product smoke); Web adoption is the second proof.

- **Wave 0 — decisions & scaffolding (no component moves; needs none of the blocked locks):**
  - Maintainer rules the **primitive decision** (`§3`) and approves DEC-UI-001.
  - Stand up the **internal `src/ui/` package** in Studio (not a repo).
  - **Split `cn`** into a pure module; freeze the **token-NAME contract**.
  - Define the **port interfaces** (color/selection, registry, availability, runtime-event-source, link, theme).
  - Stand up **visual-baseline tier-1** (`§7`).
- **Wave 1 — pure VM + vocab layer (the gold; zero UI risk):** the `lib/inspector/*Data.ts` family; `score-adapters`/`scoreValues`/`scoreMetricCatalog`/`resultArtifacts`/`chartExport`/`aggregatedResultsData`; pipeline `operatorCapability`/`variantCounting`/`pipelineStats`/`canonicalPipelinePreview`/`stepPresentation`/`PipelineNodePresentation`; dataset `datasetDomain`/`datasetSchema*`/`partitionColors`. → becomes `@nirs4all/ui` **types + adapters** (UI-004 seed), reconciled against Web `contracts.ts` + `engine/types.ts`.
- **Wave 2 — Studio-first presentational leaves:** `shared/` form primitives + the 31-primitive shadcn intersection (after `§3`); data-viz leaves (`BaseSpectraChart`, `SpectraChart`, `TargetHistogram`, `ConfusionMatrixSvg`, `Residuals/PredVsObs/ScoreHistogram` plots, `CanvasScatter`, `TransferPCAScatter`); score/result/predict leaves (`ScoreCard*`, `ResultMetricCardGrid`, predict tables/cards/chart, predictions table chrome); pipeline node-card + a new `<NodeBadge>` family + `PipelineNodeContent` + `StepPaletteItem` + `PipelineEditorHeaderBadges` + `PipelineCard`.
- **Wave 3 — contract-first (gated):** runtime/progress/job/logs + export-status (**LOCK-RT**); capability/portability + controller-ownership UI + capability-aware palette (**LOCK-CAP**, greenfield); dataset summary/overview/targets (**LOCK-IO**); live pipeline canvas (data-model unification + DnD decision).
- **Wave 4 — strategic, parallel (the L12 ↔ north-star coupling):** migrate backend-trapped compute **down** (spectral descriptors, PCA/t-SNE/UMAP, the mini step-runner, the duplicated per-wavelength stats) into `nirs4all`/`dag-ml`/`nirs4all-io`. This is what eventually makes the playground/analysis/spectra UI WASM-portable. Owned jointly with L5/L16.

---

## 5. Studio-first vs Contract-first split (maps each cluster to its gate)

| Cluster | Track | Gate | Why |
|---|---|---|---|
| Pure VM adapters (all domains) | **Studio-first** | — | already pure, zero I/O |
| Foundation primitives + tokens | **Studio-first** | primitive decision (`§3`) | bidirectional fork; reconcile gen+token names |
| Data-viz leaves (2D recharts/SVG/canvas) | **Studio-first** | — | prop-driven; invert Inspector contexts→props |
| Score / result / predict / predictions presentation | **Studio-first** | — | VM-driven |
| Pipeline node-card + badges | **Studio-first** | (LOCK-CAP only for the capability badge) | card is pure |
| Dataset summary / overview / targets | Contract-first | **LOCK-IO** | `DatasetSpec`; reconcile Studio `Dataset` ↔ Web `MaterializedDataset` |
| Capability / portability / controller-ownership UI | Contract-first | **LOCK-CAP** | vocab drafted, not locked; panel greenfield |
| Pipeline live canvas | Contract-first | data-model unification + DnD | two divergent models/DnD strategies |
| Runtime / progress / job / logs | Contract-first | **LOCK-RT** | 3 status enums + 2 WS vocabularies |
| Export status | Contract-first | **LOCK-RT** | export-as-job; payload frozen |
| Results / Inspector / Predictions (store-bound) | Contract-first | **LOCK-RT** + workspace-store model | non-portable on *two* axes (state + compute) |
| 3D spectra / scatter | Web-led, later | — | Studio three.js must not leak; Web native WebGL is the seed |
| Layout / app shell | **Stays in Studio** | — (`§10.1`) | product routing |

---

## 6. Shared prop-schema needs (UI-004)

**The seed already exists on the Web side** and must be the negotiating table, not reinvented: `nirs4all-web/studio-lite/src/engine/types.ts` (293-line pure runtime/results contract: `MaterializedDataset`, `PipelineStep`/`ContainerNode` *explicitly 1:1 with Studio's NodeType tokens*, `Metrics`/`ScoreNode`/`RunResult`/`RunProgress`/`Engine`) and `src/components/contracts.ts` (7 domain-organized prop interfaces). Studio's equivalents are richer but scattered across `src/types/*` + `lib/*`.

| Domain | Types to unify into `nirs4all-ui` | Source (Studio) | Lock |
|---|---|---|---|
| Runtime / job | a single `JobStatus`, `RunStatus`+`runStatusConfig`+`VALID_RUN_TRANSITIONS`, `RunMetrics`, `RunProgress`/`GranularProgress`/`RefitState`, one `RuntimeEvent` tagged union (`MessageType` ⊕ the `run-progress` granular `fold_*`/`log_context` types) | `types/runs.ts`, `lib/websocket.ts`, `lib/run-progress/*`, `lib/runs/executionJobRecords.ts` | **LOCK-RT** |
| Results / scores | `ScoreCardRow`+`ScoreCardType` (keystone VM), `ResultMetricCardData`, aggregated-row VM, `ResultArtifactRef`, raw `TopChainResult`/`ChainSummary`/`PartitionPrediction` (frozen at lock) | `types/score-cards.ts`, `lib/score-adapters*`, `lib/resultArtifacts.ts` | LOCK-RT |
| Predictions | `PredictTableRow`/`Predict*ReadModel`, `PredictResponse`/`AvailableModel`/`PredictionArraysResponse` | `types/predict.ts`, `types/aggregated-predictions.ts` | LOCK-RT |
| Pipeline / step | `PipelineStep`/`StepType`/`StepOption`/`ParameterSweep`/`FinetuneConfig`, `NodeDefinition`/`ParameterDefinition` (**unify the two**), `PipelineNodePresentation` | `pipeline-editor/types.ts`, `data/nodes/types.ts` | LOCK-CAP |
| Capability / controller | `CapabilityLevel`/`OperatorBackendId`/`OperatorImplementationRef`/`OperatorCapabilityResolution`; `ControllerOwnership` (**net-new** for UI-007) | `lib/operatorCapability.ts` (+ greenfield) | **LOCK-CAP** |
| Data | `DatasetSummary`/`DatasetDescriptor` (reconcile `Dataset` ↔ `MaterializedDataset`), `PartitionKey`, spectra view-model, diagnostics VMs (`ResidualDot`, pred-vs-obs, confusion, fold-stability, score-histogram bins) | `types/dataset.ts`, `lib/inspector/*Data.ts` | **LOCK-IO** |
| Foundation | token-name contract, pure `cn`, `ButtonVariant`/`BadgeVariant` (incl. `success`/`warning`) | `lib/utils.ts`, `ui/*Variants.ts` | primitive decision |

**The universal "ports" (dependency-inversion seam — these keep components pure):** `ColorSelectionPort` (`getChainColor`/`getChainOpacity`/`select`/`hovered`), `RegistryPort` (`NodeRegistryContextValue`), `AvailabilityPort` (`OperatorAvailabilityContextValue`), `RuntimeEventSource` (`subscribe(jobId) → RuntimeEvent` — Studio=WS, Web=in-process), `LinkComponent`/`onOpen`, `ThemeProvider`. Standardizing these is what lets one component serve both apps without importing `src/api`, contexts, router, or `useWebSocket`.

---

## 7. Visual baseline proposal (UI-009 / `§10.4`)

**State today (both repos): no baseline of any kind.** Storybook fully gone (no `.storybook/`, no `*.stories.*`, no deps — nothing to revive). Studio: Vitest v4 + jsdom (opt-in per file), **501 tests, zero `toMatchSnapshot`/`toHaveScreenshot`, no `@testing-library`** — render tests are a copy-pasted `createRoot`+`act` harness; the `shared/` foundation primitives have **prop-shape tests only, no render coverage**. Playwright = functional E2E on the **real FastAPI+Vite stack** (no MSW/fixtures), `screenshot: only-on-failure` (debug, not baseline). studio-lite: Vitest v2 **node-only** numerics + `playwright-core` functional smokes; `tests/shots.mjs` is a one-off manual screenshot with no diff. Per `§10.4`: *"a debug screenshot on failure is not a baseline."*

**Options (tradeoffs — for DEC-UI-001):**

| Option | Setup | Catches | v3/v4 token split | Determinism |
|---|---|---|---|---|
| (a) Storybook + Chromatic/PW-shot | **High** (no SB today) | pixels + live explorer | host 2 themes via decorators | high (Chromatic) |
| (b) Playwright-CT + `toHaveScreenshot` | Medium (already on PW) | pixels, no backend | mount per-theme; **per-theme baselines** | medium (font/AA pin in CI Docker) |
| **(c) Vitest+jsdom DOM snapshots** | **Low** (reuse existing) | DOM/markup only | **survives v3/v4 for free** (markup identical) | high |
| (d) Vitest browser-mode shots | Med-High (lite on v2) | pixels, colocated | per-theme | medium |

**Recommendation (incremental, additive to the green gate):**
1. **First infra task:** a shared render harness (adopt `@testing-library/react`, or a small `renderToString`/`act` helper) — replaces the copy-pasted harness and is the prerequisite for any component baseline.
2. **Tier 1 (now, ~0.5d):** **(c) DOM snapshots** — the only tier that ignores the v3/v4 token divergence (shadcn class names are identical across generations at the markup level).
3. **Tier 2 (after `§3` decision):** **(b) Playwright-CT** pixels with **per-theme baselines** (don't try to share one baseline across v3 and v4), fonts/AA pinned in the existing CI Docker image.
4. Storybook is **optional** (doc value) — `§10.4` needs a baseline, not a gallery; the `shared/demo.tsx` already exists as a seed if wanted later.

**Fixtures (reuse, don't invent):** promote the adapters' existing test factories (e.g. `inspector-confusionMatrixData.test.ts`'s `cell()`/`response()`) to a shared `__fixtures__` module — single source of truth, stays in sync with the types. Plus `public/node-registry/extended.json` for palette fixtures, and Web's `contracts.ts` as the cross-repo prop contract.
**Canonical states per component:** `empty · loading/skeleton · populated · error/reason · dark · long-content/overflow · dense/large-N`. RTL deferred (LTR-only today).
**Minimal first slice (~2.5–3 days):** `shared/{CollapsibleSection, InfoTooltip, ValidationMessage}` (foundation, no render coverage today) + `ConfusionMatrix` view + `ScoreCardRow` (prove the adapter→fixture→story loop on non-trivial data). These are **also Wave-1/2 extraction targets** — double-validated.

---

## 8. Studio backend dependency risks (L12)

**Cardinal rule source:** `AGENTS.md:33` + `CLAUDE.md:9` (backend = thin orchestration only). **Note:** `nirs4all-studio/BACKEND_RULES.md` referenced by the ecosystem `CLAUDE.md` **does not exist** — stale doc reference; flag for cleanup.

**Orchestration-heaviness (modules doing real NIRS/ML compute that belongs *down*):**

| Module | In-backend compute | Severity |
|---|---|---|
| `api/shared/metrics_computer.py` | spectral descriptors invented in-backend (`l2_norm`, `rms`, `auc`, `peak_count` via scipy, `snr`, smoothness) — no home in `nirs4all` | **HIGH** |
| `api/analysis.py` | PCA / t-SNE / UMAP / correlation / `mutual_info`/`f_regression` via sklearn in a router | **HIGH** |
| `api/playground/charts.py` | per-wavelength stats, UMAP, Mahalanobis, confidence ellipses (only PCA delegated) | HIGH/MED |
| `api/playground/executor.py` | **mini step-runner "without full StepRunner"** — a parallel pipeline path | HIGH/MED |
| `api/spectra.py` | `_apply_preprocessing_chain` + per-wavelength stats | MED-HIGH |
| `api/datasets.py` | detection **delegated** ✓, but spectral stats + target distributions in-backend | MED |
| `api/evaluation.py` | `eval_multi` **delegated** ✓, but confusion + hand-rolled skewness/kurtosis | MED |
| `api/preprocessing.py` | `fit_transform` in-backend for previews | MED |
| `api/inspector.py` | results analytics (bias-variance, robustness, correlation, fold-stability) | MED |
| `api/pipeline_canonical.py` (65K) | "backend-authoritative" editor↔canonical conversion + branch/merge/generator semantics | MED |

**Appropriately thin (verified):** `runs.py` (→ `nirs4all.run`), `automl.py`, `predict.py`, `synthesis.py`, `store_adapter`/`aggregated_predictions`, `nirs4all_adapter`, `recommended_config`, `updates/*`, `workspace/*`, `system.py`, `websocket/manager`, `jobs/manager`, `shared/decimation` (LTTB). **Cross-cutting:** per-wavelength summary stats are recomputed in **≥5 modules** — duplicated and trapped in FastAPI.

**Route portability (which UI domains can ever reach the backend-less WASM client):**
- **Portable (stateless compute) — but only after the math migrates down:** `predict`, `playground/execute`, `analysis/*`, `preprocessing/apply`, `evaluation/*`, `transfer`, `datasets/detect-*`. These are the **LOCK-RT common-runtime-API candidates**.
- **Irreducibly Studio-host-specific:** `workspace/*`+`workspaces/*` (SQLite store + linked-workspace registry), all `inspector/*` + `aggregated-predictions/*` + `enriched-runs` reads (persistent store), `runs/execution-job-records` + `stop`/`retry` + WS `job:<id>` (queue + progress), `updates/*`, `system/*`, `config/*`, dataset `link`/`scan-folder`/`version-status`, custom-nodes, uploads, binary exports.

**Ranked risks:**
1. **Results/Inspector/Predictions UI is welded to the SQLite `WorkspaceStore` AND backend-side analytics** → non-portable on **two** axes (state + compute). The most-wanted reusable components are the **least** extractable.
2. **Playground/Spectra/Analysis UI calls stateless-*looking* routes whose math is trapped in FastAPI** → blocked until compute migrates down (the concrete L12 → north-star item; couples to Wave 4).
3. **Run/runtime UI depends on the job-queue + WS progress model** → no WASM equivalent; needs a different in-browser execution/progress abstraction (this is also *why* LOCK-RT must define a transport-agnostic `RuntimeEventSource`).
4. **Pipeline editor depends on "backend-authoritative" canonicalization** (`pipeline_canonical.py`) → the canonical form must be owned by `nirs4all`/`dag-ml` for a reusable editor.
5. **Dataset UI mixes portable inference with host filesystem** (`detect-*` portable; `link`/`scan` host) → split the calls.
6. **The `src/api/transport.ts` + `lib/websocket.ts` layer is itself Studio-bound** → every extracted component must reach the engine through an **injected interface**, never `src/api` directly.

---

## 9. Blockers & cross-repo dependencies

| ID | Blocks | Status | Resolved by |
|---|---|---|---|
| `LOCK-UI` | this whole lane (UI-003..010) | blocked | this report supplies UI-001/UI-002/primitive-decision/visual-baseline; **needs LOCK-CAP + LOCK-RT + DEC-UI-001 accepted** |
| `LOCK-RT` | runtime/results/export extraction; `RuntimeEventSource` port | blocked (`DEC-RT-001` proposed) | unify the 3 job-status enums + 2 WS vocabularies (evidence in `§6`) |
| `LOCK-CAP` | capability/portability/controller UI; capability-aware palette | blocked (`DEC-CAP-001` proposed) | lock the `operatorCapability.ts` vocab |
| `LOCK-IO` | dataset summary/overview/targets | blocked (`DEC-IO-001` proposed) | `DatasetSpec v2`; reconcile `Dataset` ↔ `MaterializedDataset` |
| node-registry contract | pipeline palette/inspector | external | versioned `extended.json` + `validate:nodes` replicated in the package CI (B2) |
| two `NodeDefinition` types | pipeline extraction | local | unify canonical vs editor (B3) |
| L12 compute push-down | WASM-portability of playground/analysis/spectra | strategic | Wave 4 / north star (couples L11↔L12↔L5/L16) |

**Scope caveats / coverage boundaries:** `playground/visualizations/` (the 3D/WebGL spectra viewer, ~90 files) was **not** deeply audited — it holds the genuinely-reusable spectra viewer and warrants a companion audit. `experiments/` (87, campaign/launch) is mostly P2/P3 orchestration (low extraction value); `settings/`/`setup/` are app-config (out of scope). SHAP (`variable-importance/`) and `spectra-synthesis/` have **no studio-lite counterpart** → defer (Studio-only payoff).

---

## 10. Recommendations (A6 verdict)

1. **Accept DEC-UI-001 with the design `§10.2` taxonomy and the `§4` wave order.** Keep `nirs4all-ui` an **internal Studio package** until Studio re-adopts one component and Web consumes one — **do not create the repo now** (honors the prompt constraint and `§10.2`).
2. **Rule the primitive decision (`§3`) first — it is the foundation critical path.** A6 lean: **(c)+(d)** headless primitives + per-app theme if Studio/Web stay distinct brands (the drifted themes suggest yes); **(a)+(d)** if one shared identity is wanted. Either way, freeze a **token-NAME contract** and pick **one shadcn generation** before moving any primitive.
3. **Start Wave 0–1 now** — they need *none* of the blocked locks: split `cn`, define the ports, extract the **pure adapter + UI-004 type layer** (reconciled against Web `engine/types.ts` + `contracts.ts`), and stand up visual-baseline tier-1. This is real, unblocked progress on `L11` today.
4. **Gate Wave 3 on the locks** (LOCK-RT/LOCK-CAP/LOCK-IO); feed the evidence in `§6`/`§8` into `DEC-RT-001`/`DEC-CAP-001`/`DEC-IO-001`.
5. **Schedule the L12 compute push-down (Wave 4) alongside L11** — surface it to L5/L16/north-star owners, because UI portability to the WASM client *depends* on it.

**Open questions for the maintainer (ARB):** (i) primitive strategy — one identity (a) vs two brands (c)? (ii) confirm internal-package-first over a new repo? (iii) is the L12 compute push-down scheduled with L11 given the coupling? (iv) does the 3D spectra viewer (`playground/visualizations/`) get a companion audit before any "spectra" component is called complete?

---

## 11. Sync board handoff (for A0 to integrate — not applied here)

**Lane lines (replace existing `L11`/`L12` rows):**

```text
| `L11` nirs4all-ui | review | TBD | `nirs4all-studio` (internal pkg) | A6 audit landed (docs/agent_reports/A6_A6-studio-ui.md): taxonomy=design §10.2, extraction order Wave0-4, primitive-decision options + bidirectional v3/v4 + shadcn-generation fork documented, visual-baseline infra proposed. Start Wave0-1 (cn split, ports, pure adapter+UI-004 layer, baseline tier-1) — needs no blocked lock. | `LOCK-CAP`, `LOCK-RT` (Wave3 only); `DEC-UI-001` + primitive decision pending |
| `L12` Studio reassembly | review | TBD | `nirs4all-studio` | A6 backend audit landed: orchestration-heaviness ranking + route-portability map. Heavy compute trapped in FastAPI (metrics_computer/analysis/playground.executor/spectra) must migrate down — couples to north star. Backend otherwise thin (runs/predict/automl/synthesis delegate correctly). | `RT-PY-001`, `LOCK-PYREF`; compute push-down depends on L5/L16 |
```

**Decision register — fill `DEC-UI-001` (was "A ecrire apres audit Studio"):**

```text
| `DEC-UI-001` | proposed | Scope/taxonomy nirs4all-ui | TBD | Internal Studio package first (NOT a repo) until Studio+Web each consume 1 component (design §10.2). Taxonomy = foundation/data/pipeline/controllers/runtime/results/export. Order = A6 §4 Wave0-4 (adapters+types → presentational → contract-first). Primitive decision = A6 §3 (maintainer to rule (a) one-identity / (c) two-brand; freeze token-NAME contract + one shadcn generation). Visual baseline = A6 §7 (DOM snapshots → PW-CT per-theme pixels; Storybook optional). UI-004 seed = Web engine/types.ts + contracts.ts. | roadmap UI-001..010, design §10, report A6 |
```

**Worklog entry (append-only):**

```text
2026-06-30 | Claude/A6 (L11+L12) | review | Studio UI extraction audit: component inventory by domain (UI-001), taxonomy+extraction order (UI-002), Studio-first vs LOCK-RT/CAP/IO contract-first split, UI-004 shared prop-schema needs, net-new visual-baseline proposal (UI-009), and L12 backend orchestration-heaviness + private-route portability map. Key: pure VM-adapter layer is the gold (extract first); primitive layer is a bidirectional v3/v4 + shadcn-generation fork; runtime has 3 status enums + 2 WS vocabularies (LOCK-RT content); UI portability couples to L12 compute push-down. Recommend internal Studio pkg, start Wave0-1 now. | read-only; 6 sub-audits via CodeGraph+rg; no gates run; no code or sync-board edits. | A0 to integrate lane lines + DEC-UI-001; maintainer to rule primitive strategy + ARB Qs in report §10. |
```

---

## Appendix — evidence & method

**Key paths.** Foundation: `nirs4all-studio/src/components/ui/*` (34), `…/ui/{button,badge}Variants.ts`, `…/ui/state-display.tsx`, `…/ui/sonner.tsx`, `src/lib/utils.ts`, `tailwind.config.ts`, `src/index.css`, `components.json`; Web `nirs4all-web/studio-lite/src/app/components/ui/*` (48), `src/styles/{theme,fonts,tailwind,index}.css`, `src/components/contracts.ts`, `src/engine/types.ts`. Adapters (gold): `src/lib/inspector/*Data.ts` (73/74 pure), `src/lib/{score-adapters*,scoreValues,scoreMetricCatalog,resultArtifacts,chartExport,aggregatedResultsData,operatorCapability,variantCounting,pipelineStats,canonicalPipelinePreview,stepPresentation,partitionColors,datasetDomain}`. Components: `src/components/pipeline-editor/{PipelineNodeContent,PipelineNode,StepPaletteItem,PipelineEditorHeaderBadges}.tsx`, `…/shared/{ParameterInputComponent,ParameterSelect,ParameterSwitch,ValidationMessage,CollapsibleSection,InfoTooltip}.tsx`, `src/components/{scores,results,predict,predictions}/*`, `src/components/inspector/visualizations/*`, `src/components/charts/BaseSpectraChart.tsx`. Runtime contracts: `src/types/{runs,score-cards,predict,aggregated-predictions}.ts`, `src/lib/{websocket,run-progress/*,runs/executionJobRecords}.ts`. Backend: `nirs4all-studio/api/{shared/metrics_computer,analysis,playground/charts,playground/executor,spectra,datasets,evaluation,preprocessing,inspector,pipeline_canonical}.py`, `main.py`, `websocket/manager.py`; client `src/api/*.ts` + `src/api/transport.ts`. Design intent: `nirs4all-ecosystem/docs/MULTIMODAL_ECOSYSTEM_DESIGN_SCHEMAS.md §10`, roadmap `PARALLEL_REFACTORING_ROADMAP.md` `UI-001..010` / `L11`/`L12`.

**Commands / method:** CodeGraph explorations (studio + web are indexed) plus direct `rg`/`Read`/`git` verification, across six read-only sub-audits. No build/lint/test gates were run (audit pass). No implementation code, fixtures, or the sync board were modified.
