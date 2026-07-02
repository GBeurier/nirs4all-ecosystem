# Wave 3AS - release lock publication and shared UI repo

Date: 2026-07-02

## Scope

This batch resumed after the reset/aborted run and the user authorization to publish/tag selected heads. It handled two blockers before full parity:

- Publish and tag selected aggregation-lock heads.
- Create the top-level `nirs4all-ui` repo and make Studio/Web consume it.

No Claude agents were used. Parallel workers were ChatGPT/Codex only.

## Agents

### Lorentz - `nirs4all-ui` worker

Ownership: `/home/delete/nirs4all/nirs4all-ui` only.

Result:

- Created new top-level repo `nirs4all-ui`.
- Added package `nirs4all-ui` with exports:
  - `nirs4all-ui/score`
  - `nirs4all-ui/runtime`
  - `nirs4all-ui/components`
- Extracted Studio's pure `score` and `runtime` foundations.
- Added first shared React component `RuntimeEngineBadge`.
- Added local `AGENTS.md`.

Commit:

- `nirs4all-ui` `ccef03b` - `feat(ui): seed shared nirs4all ui package`

Tests:

- `npm run typecheck`
- `npm run build`
- `npm test` - 45 passed

Risks:

- The package is a first shared slice, not a complete extraction of every graphical component.
- Consumers use source aliases for sibling development; package publication still requires `npm run build` before dist-based consumption.

### Hegel - Web worker

Ownership: `nirs4all-web/studio-lite` only.

Result:

- Initially staged a local `nirs4all-ui/runtime` shim because the sibling repo did not exist yet.
- Integration replaced that shim with real sibling package consumption.
- Web now imports `RuntimeEngineBadge` from `nirs4all-ui/components`.

Commit:

- `nirs4all-web` `5028704` - `feat(studio-lite): use shared nirs4all-ui runtime badge`

Tests:

- `npm run typecheck`
- `npx vitest run --config vitest.config.ts src/app/runtimeErrors.test.ts`

Risks:

- `origin/main` has one remote-only commit (`9098215 fix(studio-lite): add crawl discovery metadata`), so Web was published as branch `refactor/nirs4all-ui-adoption` plus tag instead of forcing `main`.

### Singer - reviewer/parity auditor

Ownership: audit only, no file edits.

Findings used:

- Release-lock validation can pass after regenerating from current selected heads.
- Tags are the correct fetchability anchor for repos where locked branch head differs from remote `main`.
- Top-level `nirs4all-ui` was missing before this batch.
- Python/R/WASM surfaces are covered in the public V1 matrix, but R/WASM still need explicit post-batch proof.

## Integration work

Release lock:

- Tagged seven selected lock member heads with `n4a-v1-2026.07-refactor`.
- Pushed refactor branches where applicable:
  - `dag-ml` `refactor/L20-lockstep`
  - `dag-ml-data` `refactor/L20-lockstep`
  - `nirs4all-io` `refactor/L7-io-dagml-sibling`
- Pushed the shared tag to all seven lock members.
- Regenerated `docs/contracts/release/aggregation-lock.n4a.lock.json` with `exact_tag: n4a-v1-2026.07-refactor`.

Commit:

- `nirs4all-ecosystem` `03976c7` - `chore(release): lock published refactor heads`

Release-lock checks:

- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable` - 7/7 fetchable
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all checkout-members --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output /tmp/n4a-lock-checkout-v1`

Studio:

- Replaced local `src/ui/{score,runtime}` implementation files with compatibility bridges to `nirs4all-ui`.
- Added `nirs4all-ui` file dependency and Vite/Vitest/TypeScript aliases.

Commit:

- `nirs4all-studio` `aa50e17` - `refactor(ui): consume shared nirs4all-ui foundations`

Tests:

- `npm run lint:tsc`
- `npx vitest run src/ui src/components/runtime/RuntimeComponents.test.tsx` - 45 passed

Web:

- Added `nirs4all-ui` file dependency and Vite/Vitest/TypeScript aliases.
- Replaced inline dag-ml lineage badge with `RuntimeEngineBadge`.

Commit:

- `nirs4all-web` `5028704` - `feat(studio-lite): use shared nirs4all-ui runtime badge`

Tests:

- `npm run typecheck`
- `npx vitest run --config vitest.config.ts src/app/runtimeErrors.test.ts`

## Published refs

- `nirs4all-ui`
  - remote created: `https://github.com/GBeurier/nirs4all-ui`
  - pushed `main` at `ccef03b`
  - pushed tag `n4a-ui-2026.07-refactor`
- `nirs4all-studio`
  - pushed `main` at `aa50e17`
  - pushed tag `n4a-ui-2026.07-refactor`
- `nirs4all-web`
  - pushed branch `refactor/nirs4all-ui-adoption` at `5028704`
  - pushed tag `n4a-ui-2026.07-refactor`
  - did not push `main` because local `main` is still behind `origin/main` by one crawl-metadata commit.

## Remaining gates

Run after this batch rather than before it:

- Full Python-reference parity from `INT-nirs4all`.
- dag-ml/dag-ml-data sibling contract validation.
- Studio full `npm run lint:parallel && npm run test:parallel`, then Playwright if runtime ports are clear.
- Web `npm run test`, `npm run build`, `npm run build:single`, catalog validation, and browser smokes.
- Explicit R and WASM surface gates for `nirs4all-lite` plus methods/datasets/formats/io where public surfaces are claimed.

