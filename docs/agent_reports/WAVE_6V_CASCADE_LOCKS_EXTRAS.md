# Wave 6V - Cascade Locks And Provider Extras

Date: 2026-07-06

## Scope

- `nirs4all-web`: package-lock alignment for vendored `nirs4all` and `nirs4all-ui`
- `nirs4all-studio`: package-lock alignment for sibling `nirs4all-ui`
- `nirs4all-providers`: optional extras aligned with the current release train

## Changes

- `nirs4all-web` head: `51440c9`
  - Updated `studio-lite/package-lock.json` so `vendor/nirs4all` is `0.2.5` and
    `vendor/nirs4all-ui` is `0.1.4`.
- `nirs4all-studio` head: `5814b6a`
  - Updated `package-lock.json` so `../nirs4all-ui` is `0.1.4`.
  - No Studio version bump and no production release change.
- `nirs4all-providers` head: `e5416cd`
  - Raised optional extras to the release train:
    - `nirs4all-repository>=0.1.6`
    - `nirs4all-benchmarks>=0.1.4`
    - `nirs4all-papers>=0.2.3`
    - `nirs4all-io>=0.1.6`
  - Kept base `dependencies = []`; providers remains a soft-import read/discovery layer.

## Validation

- Web, Node 22:
  - `NIRS4ALL_LITE_SHIM_REQUIRED=1 npm run check:lite-shim`
  - `npm run check:ui-shim`
  - `npm run test:client-only`
- Studio, Node 24:
  - `npm run smoke:nirs4all-ui-package`
- Providers:
  - `.venv/bin/python -m pytest` - 109 passed, 2 skipped
  - TOML validation of optional extras and empty base dependencies
- Ecosystem:
  - `python3 scripts/n4a_e2e_scenarios.py validate`
  - `python3 scripts/n4a_release_surface_matrix.py validate`
  - `python3 -m pytest -q tests/test_submodule_repin_plan.py tests/test_gitmodules_topology.py tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_e2e_scenarios.py`
  - Result: 98 passed

## Risk

Low. The changes are lockfile/package metadata only and do not alter Python full `nirs4all`, Studio
runtime behavior, or release-lock protected artifacts.
