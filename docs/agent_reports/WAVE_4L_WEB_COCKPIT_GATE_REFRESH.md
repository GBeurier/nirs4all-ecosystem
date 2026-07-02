# Wave 4L - Web and cockpit gate refresh

Date: 2026-07-02  
Coordinator: Codex

## Scope

Act on two audit findings without rerunning full Python parity:

- `nirs4all-web` Pages deployment was weaker than the RC CI gate.
- `nirs4all-cockpit` RC still described `dag-ml` and `dag-ml-data` as
  Rust-only, despite RC lock/package metadata exposing Python/WASM/R binding
  surfaces.

## Published Code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all-web` | `rc/v1-full-refactor` | `69c0b75` / `n4a-v1-rc1-2026.07-refactor` | Pages/CI workflows, core sibling action, lite shim sync script, vendored `nirs4all` shim, lockfile |
| `nirs4all-cockpit` | `rc/v1-full-refactor` | `33c91c3` / `n4a-v1-rc1-2026.07-refactor` | `ops/targets.yaml`, `data/current.json` |
| `nirs4all-ecosystem` | `rc/v1-full-refactor` | this report commit | control board, surface matrix, this report |

## Web

Changes:

- Added `.github/actions/nirs4all-core-sibling` to clone `GBeurier/nirs4all-lite`
  next to the Web workspace. The Web RC branch maps to
  `rc/v1-full-refactor-core` because the GitHub repo rename is pending.
- `studio-lite/scripts/sync-lite-shim.mjs` now supports
  `NIRS4ALL_LITE_SHIM_ROOT` and a local RC fallback. In strict mode it fails
  instead of silently skipping when the canonical shim is unavailable.
- Resynced `studio-lite/vendor/nirs4all` from `RC-v1-nirs4all-core`.
- Hardened both `.github/workflows/web-ci.yml` and
  `.github/workflows/deploy-pages.yml`: `npm ci`, client-side-only contract,
  typecheck, Vitest, catalog validation, strict lite/core shim check,
  `build:single`, `build`, and one browser smoke now block.

Local gates:

- `npm ci` -> passed, with existing npm audit warnings
  (`5 vulnerabilities`: 3 moderate, 1 high, 1 critical).
- `npm run test:client-only` -> `2 passed`.
- `npm run typecheck` -> passed.
- `npm run test` -> `134 passed`.
- `npm run validate:catalog` -> passed; Studio canonical registry sibling was
  not present locally, so that optional subcheck warned/skipped.
- `npm run check:lite-shim` -> `vendor/nirs4all is up to date`.
- `npm run build:single` -> passed.
- `npm run build` -> passed.
- `npm run smoke -- rt-fallback` -> passed (`1` browser smoke).

## Cockpit

Changes:

- `dag-ml` now tracks planned PyPI `dag-ml` and npm `dag-ml-wasm` targets in
  addition to existing docs/crates targets.
- `dag-ml-data` now tracks planned PyPI `dag-ml-data`, npm
  `dag-ml-data-wasm`, and R `dagmldata` targets in addition to existing
  docs/crates targets.
- `data/current.json` was updated only for those planned targets; the existing
  live snapshot values were preserved.

Local gates:

- `python3.11 -m cockpit.cli validate-targets ops/targets.yaml` ->
  `21 packages, 94 targets`.
- `python3.11 -m json.tool data/current.json` -> valid JSON.
- `python3.11 -m cockpit.cli summarize data/current.json` ->
  `green=75 stale=2 pending=5 missing=7 broken=0 unknown=0 excluded=0`.
- `python3.11 -m pytest tests/test_targets_topology.py -q` -> `3 passed`.
- `python3.11 -m pytest -q` -> `84 passed`.

## Remaining Risk

- Web `npm audit` still reports dependency vulnerabilities; no forced
  dependency upgrade was applied in this release-gate patch.
- Web catalog validation still skips the optional Studio canonical-registry
  subcheck when the Studio sibling is absent.
- Cockpit remains a release accounting snapshot, not proof that the planned
  binding packages are already published.
