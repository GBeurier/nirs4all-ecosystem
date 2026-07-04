# Wave 4CM - Release And Product E2E Sync

Generated: 2026-07-04T04:48:21Z

## Scope

- Consolidated the post-reset release state across `nirs4all-core`, `nirs4all-web`, `nirs4all-cockpit`, `nirs4all-providers`, `nirs4all-benchmarks`, `nirs4all-repository`, `dag-ml`, `dag-ml-data`, `nirs4all-cluster`, `nirs4all-org`, and `nirs4all-ui`.
- Kept `nirs4all` Python and `nirs4all-studio` production release out of scope for this wave.
- Audited existing worktrees as historical/superseded sources only; no old worktree was merged without review.
- Hardened the Web converted-predictions E2E path so it renders through the real React `ResultsList` and `ResultsVisualization` components instead of test-injected HTML panels.
- Updated the cross-language E2E contract wording for the converted-predictions/Web scenario.

## Agents / Review

- Codex release audit reviewed selected heads, tags, CI runs, and package publication state.
- Codex cockpit/pages/web audit reviewed Pages status, public topology copy, and client-side-only Web behavior.
- Codex E2E audit found the 10/10 ready batch executable but called out weak smokes; this wave closes the Web result-rendering gap.
- Main integrator reviewed and pushed the Web hardening diff as `nirs4all-web` commit `722a744` (`test(web): render converted predictions through results UI`).

## Files Modified

- `nirs4all-web/studio-lite/src/engine/rt-result.ts`: added `rt_result` to display `RunResult` rehydration for imported runtime result evidence.
- `nirs4all-web/studio-lite/src/app/App.tsx`: added an e2e-only `?n4a_e2e=1` hook to hydrate runtime results into the normal app state.
- `nirs4all-web/studio-lite/src/components/results/ResultsList.tsx`: added product test selector.
- `nirs4all-web/studio-lite/src/components/results/ResultsVisualization.tsx`: added product test selector.
- `nirs4all-web/studio-lite/tests/converted-predictions-render-smoke.mjs`: removed injected DOM panels and asserts real React results components.
- `nirs4all-web/studio-lite/src/engine/rt-result.goldens.test.ts`: added reverse mapping coverage from shared `rt_result` golden.
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`: updated Web evidence text for the converted-predictions scenario.

## Tests Run

- `nirs4all-web/studio-lite`: `npm run typecheck` -> passed.
- `nirs4all-web/studio-lite`: `npx vitest run --config vitest.config.ts src/engine/rt-result.goldens.test.ts` -> 8 passed.
- `nirs4all-web/studio-lite`: `npm run build` -> passed with existing Vite externalization/chunk warnings.
- `nirs4all-web/studio-lite`: `SMOKE_URL=http://localhost:4345/ ARTIFACTS_DIR=/tmp/n4a-web-converted-product-smoke CHROME=/usr/bin/google-chrome npm run smoke:converted-predictions` -> passed; rendered `n4a-results-list` and `n4a-results-visualization`.
- `nirs4all-web/studio-lite`: `npm run test` -> 135 passed.
- `nirs4all-ecosystem`: `PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py validate` -> OK, 10 scenarios.
- `nirs4all-ecosystem`: `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py` -> 16 passed.
- `git diff --check` in `nirs4all-web` and `nirs4all-ecosystem` -> clean.

## Published / Verified

- `nirs4all-web` release `v0.1.1` exists; Web CI, GitHub Pages deploy, and version guard were green for `79e3398`. A newer Web hardening commit `722a744` is pushed and awaiting/triggering fresh remote runs.
- `nirs4all-cockpit` release `v0.1.3` exists; latest version guard for `b85304e` is green.
- `nirs4all-core` latest checked CI for `79d34d1` is green.
- `nirs4all-providers` latest checked Providers CI for `66cf125` is green.
- `nirs4all-benchmarks` release `v0.1.2` exists; CI/pages/version guard are green for `cf6c605`.
- `nirs4all-repository` release `v0.1.2` exists.
- `dag-ml` release `v0.2.2`, `dag-ml-data` release `v0.2.3`, and `nirs4all-cluster` release `v0.1.1` exist.

## Blockers

- PyPI publication for `nirs4all-benchmarks` failed on GitHub run `28695118856` with Trusted Publishing `invalid-publisher`.
- PyPI publication for `nirs4all-repository` failed on GitHub run `28695107796` with Trusted Publishing `invalid-publisher`.
- `nirs4all-providers` PyPI publication remains blocked by the same Trusted Publisher class of failure.
- No PyPI API token is available in the root token files; fixing these requires PyPI project Trusted Publisher configuration or an explicit publish token.

## Decisions

- Treat Web result rendering as a product-component E2E now: tests must hydrate and assert the real app components, not create standalone HTML.
- Keep the `?n4a_e2e=1` hook hidden from normal Web behavior; it exists only to let e2e tests inject externally produced runtime result evidence into app state.
- Continue deferring full Python-reference parity until another large integration batch is ready, per operator instruction; targeted parity/product checks remain active.

## Remaining Risks

- The 10 cross-language scenarios are run-ready, but not all are equally strong. Remaining priority gaps are real Python-vs-WASM numeric parity, R dataset-provider/catalog+IO materialization, and cluster numerical pipeline parity.
- `dag-ml` checkout is still on `refactor/L20-lockstep`; release-selected head is `origin/main`/`rc/v1-full-refactor`. Do not merge the local checkout branch without a fresh audit.
