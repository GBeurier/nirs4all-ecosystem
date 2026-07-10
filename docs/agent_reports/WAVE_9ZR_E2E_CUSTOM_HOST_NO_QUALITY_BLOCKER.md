# WAVE 9ZR - E2E Custom Host Without Quality Blocker

## Scope

Removed `nirs4all-quality` from the required `e2e-core-ui-custom-app-host` gate because that repo is being modified by a separate agent and must not block the NIRS4ALL V1 core+UI custom host validation.

## Files Modified

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

## Decisions

- The custom host gate now remains scoped to `nirs4all-core`, `nirs4all-ui`, `nirs4all-web`, and `nirs4all-methods`.
- The published package custom-host smoke remains strict and still proves public `nirs4all` + `nirs4all-ui` composition from a downstream Vite/React app.
- `nirs4all-quality` references are kept out of the central E2E contract and guarded by negative assertions.

## Tests Run

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/n4a_e2e_scenarios.py validate`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/n4a_e2e_scenarios.py --artifacts-dir .n4a-e2e-artifacts evidence-ledger --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/test_e2e_scenarios.py tests/test_release_lock.py tests/test_gitmodules_topology.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/n4a_release_surface_matrix.py --matrix docs/contracts/release/public-v1-surface-matrix.n4a.json --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json validate`

## Results

- 11/11 scenarios verified.
- Runtime ledger now tracks 70 artifacts.
- 151 local tests passed.

## Risks

- `nirs4all-quality` is no longer covered by the central custom-host gate. This is intentional until the separate `nirs4all-quality` work is merged and can be validated independently.
