# Wave 10A - Core/UI/Providers/Cockpit refresh

## Scope

- Repinned `nirs4all-cockpit` from `bdcc93a` to `b81fbd0`, the dashboard smoke
  hardening and CRAN datasets size-exception correction head.
- Repinned `nirs4all-core` from `8386c37` to `0e09e53`, the release
  documentation status refresh head.
- Repinned `nirs4all-providers` from `c4c0f27` to `cebffb2`, the GitHub Pages
  install guidance refresh head.
- Repinned `nirs4all-ui` from `89c7af0` to `cc0b5db`, the npm prerelease publish
  guard head.

## Files Modified

- gitlinks: `nirs4all-cockpit`, `nirs4all-core`, `nirs4all-providers`,
  `nirs4all-ui`
- `docs/agent_reports/WAVE_10A_CORE_UI_PROVIDERS_COCKPIT_REFRESH.md`

## Tests And Gates

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py tests/test_cutover_state_gate.py`
- `python3.11 -m pytest -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/n4a_submodule_repin.py plan --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/n4a_release_surface_matrix.py --matrix docs/contracts/release/public-v1-surface-matrix.n4a.json validate`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/test_gitmodules_topology.py tests/test_submodule_repin_plan.py tests/test_release_surface_matrix.py`
- `python3.11 scripts/n4a_release_lock.py checkout-members --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output /tmp/n4a-lock-selected`
- `python3.11 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `git diff --check`

## Decisions

- Kept the aggregation release lock unchanged. Direct validation against the live
  sibling workspace is intentionally stale because several release members have
  post-tag main heads. The lock validated from an isolated selected checkout,
  and fetchability remained `7/7`.
- Did not run the full runtime E2E evidence job for this wave. The integrated
  changes are docs, static site guidance, CI release guards, cockpit generated
  status, and gitlinks; no runtime/schema/parity contract changed.
- Kept `nirs4all` Python production and `nirs4all-studio` production outside the
  final release train for this wave.

## Risks / Follow-Up

- `nirs4all` remains `ahead_of_remote` in the submodule repin plan and requires
  manual review before any production-facing Python cutover.
- Cockpit needs one more collect after this ecosystem pin lands so public status
  reflects the new ecosystem head and the latest green checks.
- Manual CRAN work remains outside automation: `n4m`, `pls4all`,
  `nirs4allio`, `nirs4alldatasets`, and `nirs4all`.
