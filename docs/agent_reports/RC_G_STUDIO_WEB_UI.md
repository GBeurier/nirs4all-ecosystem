# RC-G — Studio/Web/UI Lane Report

Date: 2026-07-02
Agent: RC-G (Studio/Web/shared-UI runtime UX)
Worktrees: `_worktrees/RC-v1-ui`, `_worktrees/RC-v1-studio`, `_worktrees/RC-v1-web` (all on `rc/v1-full-refactor`)

## Summary

The shared `nirs4all-ui` package was already seeded (score/runtime foundations +
`RuntimeEngineBadge`) and consumed by Studio (15 files via the `@/ui` bridge)
but only minimally by Web (one badge), and the whole arrangement could not
actually build anywhere: the `file:../nirs4all-ui` deps and `../nirs4all-ui/src`
aliases resolved nowhere in the RC worktree layout and in GitHub CI
workflow. This lane made the package real in three ways: (1) completed the
shared runtime domain so it models the **full rt_error.v1 contract**, (2) moved
Web's duplicated refusal-rendering and metric vocabulary onto the shared
package with byte-identical UI (pinned by tests), and (3) made the sibling
package resolvable on CI/Pages so the RC heads can go green upstream. Web's
client-side-only property was audited (clean) and is now **enforced by a test**.

## Files modified

### `nirs4all-ui` (RC-v1-ui)
- `src/runtime/resultMetadata.ts` — `RuntimeDiagnosticItem` gains
  `unsupportedCapability` (reads `unsupported_capability`/`unsupportedCapability`),
  completing coverage of the rt_error.v1 envelope (`portable_level` stays
  opaque per DEC-RT-001). New `formatRuntimeRefusalText()` — the shared
  multi-line refusal rendering both hosts use.
- `src/runtime/resultMetadata.test.ts` — updated `toEqual` for the new field.
- `src/runtime/rtErrorContract.test.ts` — **new** contract test: mirrors the
  schema's verb/cause enums + wire key set, proves every interpreted wire key
  normalizes, pins cause→tone mapping and severity escalation, pins the exact
  refusal text hosts render.

### `nirs4all-studio` (RC-v1-studio)
- `src/api/inspector.test.ts` — baseline tsc fix: `ScoreRef` literal now carries
  required `key`/`metric` (mirrors `projectInspectorScoreRef`), and the wire
  assertion now proves they serialize.
- `src/components/predictions/viewer/fetchPartitionData.ts` — baseline tsc fix:
  `PredictionArraysResponse.y_true/y_pred` widened to vector-or-matrix in the RC
  contract; added `toPlottableVector()` projecting matrices to their first
  column (the `(n,1)` `tolist()` case) at the fetch boundary.
- `src/components/runtime/RuntimeDiagnosticsList.tsx` — renders
  `Missing capability: <token>` when a diagnostic carries one (full contract
  now visible in Studio).
- `src/components/runtime/RuntimeComponents.test.tsx` — asserts the capability
  line renders.
- `src/ui/runtime/resultMetadata.test.ts` — bridge-consumption test updated for
  the new field (this suite now proves `@/ui` re-exports the shared package).
- `.github/actions/nirs4all-ui-sibling/action.yml` — **new** composite action:
  clones `GBeurier/nirs4all-ui` at `$GITHUB_WORKSPACE/../nirs4all-ui` and now
  requires the branch matching the current ref when a GitHub ref is known, so
  RC Studio cannot silently validate against `nirs4all-ui@main`.
- `.github/workflows/ci.yml` (2 sites), `playwright.yml` (1),
  `release-unified.yml` (8) — the action runs before every `npm ci`.

### `nirs4all-web` (RC-v1-web)
- `studio-lite/src/app/runtimeErrors.ts` — deletes the local `formatToken`/
  `formatRtError`; the typed `RtError` path now renders through
  `formatRuntimeRefusalText` from `nirs4all-ui/runtime`. Output byte-identical
  (pre-existing pinned test unchanged and green).
- `studio-lite/src/lib/format.ts` — `primaryMetric`/`metricChips` labels and
  direction now derive from `nirs4all-ui/score` (`getMetricDefinition`,
  `isLowerBetter`); `fmt()` number formatting stays a Web display policy.
- `studio-lite/src/lib/format.test.ts` — **new**: pins the derived vocabulary
  (labels/direction byte-identical to the previous hardcoded values).
- `studio-lite/src/app/client-side-only.test.ts` — **new** enforcement test:
  scans app sources (excluding the staged WASM glue) for `fetch(`, XHR,
  WebSocket/EventSource, `process.env`, `node:` imports, `require(`, `/api/`
  routes, local server origins, and stray plain-JS files. Current tree: zero
  violations.
- `.github/actions/nirs4all-ui-sibling/action.yml` — **new** (same action;
  web's `file:../../nirs4all-ui` from `studio-lite/` resolves to the same
  parent-of-workspace path — verified by path math). The coordinator follow-up
  made the ref requirement strict here too.
- `.github/workflows/deploy-pages.yml` — action runs before `npm ci`.

### Environment (not a repo change)
- Created symlink `_worktrees/nirs4all-ui -> _worktrees/RC-v1-ui` (mirrors the
  existing `_worktrees/dag-ml` pattern) so the RC worktrees resolve the sibling
  package. Without it, `npm install`/tsc/vite fail in RC-v1-studio and
  RC-v1-web. Coordinator: this symlink is required for any lane touching these
  worktrees.

## Tests run (exact results)

| Gate | Result |
| --- | --- |
| nirs4all-ui `npm run typecheck` + `npm test` + `npm run build` | pass — 50 tests / 8 files (45 baseline + 5 new contract) |
| Studio `tsc --noEmit -p tsconfig.app.json` | **baseline was failing (3 errors)** → now clean |
| Studio full Vitest | 516 files / 3695 passed, 1 skipped |
| Studio eslint (touched files) | clean |
| Web `typecheck` + `test` + `validate:catalog` + `build` | pass — 133 tests / 21 files (unit build + served build OK) |
| Web browser smokes `tests/smoke.mjs` + `tests/rt-fallback-smoke.mjs` (real Chromium vs `vite preview`) | both PASSED, no console errors — typed RtError across the worker, wire diagnostics, schema_version intact |
| Workflow YAML | all 6 touched files parse |

Not run: full Web smoke suite (23 smokes), Studio Playwright e2e, Studio pytest
backend — out of scope per lane brief (changes are frontend/contract-only; the
two most relevant smokes were run).

## Decisions

1. **The shared runtime domain now models rt_error.v1 completely.** The
   normalizer previously dropped `unsupported_capability`; the vocabulary is
   OWNED by CAP-004 and only CARRIED here, so the field is surfaced verbatim
   (token-formatted for display only).
2. **Refusal rendering is a shared convention** (`formatRuntimeRefusalText`),
   not a Web-private formatter. Web's pinned strings were adopted as the shared
   shape — proven byte-compatible because Web's pre-existing test passed
   unmodified.
3. **Formatting policy stays host-owned; vocabulary is shared.** Web keeps its
   compact `fmt()`; labels/abbreviations/direction come from the shared catalog.
4. **CI resolution via parent-of-workspace clone**, not repo-path changes: the
   sibling-checkout layout is the ecosystem convention; CI now reproduces it.
   Branch-matching is strict for RC branches, so `rc/v1-full-refactor` must be
   pushed to `nirs4all-ui` before Studio/Web RC CI can pass.
5. **Multi-target prediction payloads project to column 0** in the Studio
   viewer. Viewer targets are per-target prediction rows; the matrix case is
   the `(n,1)` serialization artifact. A true `(n,k>1)` block would need a
   column-selection UI — deliberately not built now (Codex review raised it;
   accepted as residual, see risks).

## Risks / open questions

- **`nirs4all-ui` must exist on GitHub and be public** (remote
  `GBeurier/nirs4all-ui` is configured locally). If the repo is private, the
  composite action needs a token input; if unpushed, CI falls back… to nothing —
  the clone step fails loudly. Coordinator should push `nirs4all-ui` (main +
  `rc/v1-full-refactor`) before the RC branches of studio/web hit CI.
- **Matching UI branch required**: Studio/Web RC CI now fails if
  `nirs4all-ui` does not expose the same branch ref. This is intentional for
  release proof, but it makes pushing the UI branch a prerequisite for CI.
- **Schema mirroring**: `rtErrorContract.test.ts` (nirs4all-ui) and
  `src/engine/rt.ts` (web) both mirror `rt_error.v1.schema.json` as in-repo
  fixtures. Recommend the ecosystem contract validator additionally checks
  these mirrors against the schema (RC-A/RC-B lane).
- **`(n,k>1)` prediction blocks** would silently plot the first target in the
  Studio viewer. Believed unreachable (per-target rows), flagged for RC-D/RC-C
  if the native results path ever emits multi-column arrays per prediction.
- Web `validate:catalog` **skips** ABI enforcement in the worktree layout
  (`../../nirs4all-methods` absent under `_worktrees/`); it enforces in the
  production sibling tree. A `_worktrees/nirs4all-methods` symlink would
  re-enable it — left to the coordinator since methods has no RC worktree.

## Backend/API contract notes (not edited — outside UI ownership)

None required. The RC Studio backend types (`ScoreRef` with `key`/`metric`,
vector-or-matrix `y_true`/`y_pred`) were consumed as-is on the client side.

## Follow-up full parity needed?

No. Changes are display-layer contracts + CI plumbing; no pipeline/runtime
semantics touched. Normal Studio/Web gates suffice at integration.

## Coordinator Follow-Up

- Studio commit `521dc89` and Web commit `a2e7952` made the shared UI sibling
  action fail when the matching RC ref is absent.
- Studio commit `0653ee0` aligned backend tests with the RC default-engine
  contract (`None` delegates to `nirs4all`, currently `dag-ml`) instead of
  asserting the old legacy default.
- Python commit `8b69fd4f` fixed the real dag-ml backend bug exposed by Studio:
  canonical editor pipelines with string/dict class refs now deserialize before
  splitter detection.
- Targeted Studio backend gate with RC Python/dag-ml/dag-ml-data passed:
  `tests/test_runtime_engine.py`, `tests/test_studio_oracle_routes.py`,
  `tests/integration/test_native_results_format.py`, and the real quick-run
  completion test -> `40 passed`.
