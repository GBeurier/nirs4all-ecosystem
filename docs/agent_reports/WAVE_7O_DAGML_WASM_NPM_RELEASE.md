# WAVE 7O - DAG-ML WASM npm release and cockpit reconciliation

Date: 2026-07-06
Agent: Codex
Lane: release/cockpit coordination

## Scope

- Published the DAG-ML browser/WASM bindings that were still cockpit `planned` surfaces.
- Added idempotent GitHub Actions workflows for future npm publication.
- Regenerated and validated the cockpit after registry reconciliation.
- Did not edit `nirs4all-ui` or `nirs4all-quality`; those repos are reserved for the active quality work.

## Repositories and files changed

- `dag-ml`
  - `.github/workflows/release-npm.yml`
  - Branch commit: `c05ef06` on `refactor/L20-lockstep`
  - Default-branch workflow commit: `ee24370` on `main`
- `dag-ml-data`
  - `.github/workflows/release-npm.yml`
  - Branch commit: `92967e0` on `rc/v1-full-refactor`
  - Default-branch workflow commit: `d038375` on `main`
- `nirs4all-cockpit`
  - `ops/targets.yaml`
  - `data/current.json`

## Published artifacts

- npm `dag-ml-wasm@0.2.3`
  - `latest` dist-tag set to `0.2.3`
- npm `dag-ml-data-wasm@0.2.4`
  - `latest` dist-tag set to `0.2.4`

The workflows were also run with `publish=true` and completed successfully:

- `GBeurier/dag-ml`, workflow `release-npm.yml`, run `28823252598`
- `GBeurier/dag-ml-data`, workflow `release-npm.yml`, run `28823252280`

## Tests and validation

- `wasm-pack build crates/dag-ml-wasm --target web --release`
- `wasm-pack build crates/dag-ml-data-wasm --target web --release`
- `node scripts/smoke_wasm_web_bindings.mjs /tmp/dag-ml-wasm-pkg`
- `node scripts/smoke_wasm_tarball_metadata.mjs /tmp/dag-ml-wasm-pkg`
- `node scripts/smoke_wasm_web_bindings.mjs /tmp/dag-ml-data-wasm-pkg`
- `node scripts/smoke_wasm_tarball_metadata.mjs /tmp/dag-ml-data-wasm-pkg`
- `python -m cockpit.cli collect --only dag-ml,dag-ml-data`
  - Result: `green=15 stale=0 pending=0 missing=3 broken=0 unknown=0 excluded=0`
- `python -m cockpit.cli collect --out data/current.json`
  - Result: `green=85 stale=2 pending=4 missing=8 broken=0 unknown=0 excluded=1`
- `python -m pytest -q tests/test_targets_topology.py tests/test_cli.py tests/test_reconcile.py -p no:cacheprovider`
  - Result: `33 passed`
- `python -m cockpit.cli validate-targets`
  - Result: `OK: ops/targets.yaml - 21 packages, 100 targets`
- `python -m cockpit.cli summarize data/current.json`
  - Result: `green=85 stale=2 pending=4 missing=8 broken=0 unknown=0 excluded=1`
- `git diff --check`

## Decisions

- The npm surfaces are now `tracked`, not `planned`, because the packages are published and registry-visible.
- The workflows skip already-published versions to make repeated dispatches safe.
- PyPI and R-universe surfaces were not force-marked green. They remain explicit cockpit work items until the external publishing prerequisites are satisfied.

## Remaining risks / blockers

- No local `pypi_token` is present. PyPI publications still require Trusted Publisher configuration or a valid API token.
- `dag-ml` PyPI `dag-ml`, `dag-ml-data` PyPI `dag-ml-data`, and R-universe `dagmldata` remain `planned/missing` in cockpit.
- The full Python parity gate was intentionally not rerun in this batch; no Python runtime code changed.
