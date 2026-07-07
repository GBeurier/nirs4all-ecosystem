# Wave 7AW - Core 0.3.0 No-Legacy Alias Lock

Date: 2026-07-07

## Scope

Integrated the published `nirs4all-core` `v0.3.0` release into the ecosystem
release topology without keeping a public `nirs4all-lite` alias.

## Files Modified

- `README.md`
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/contracts/release/public-v1-surface-matrix.n4a.json`
- `tests/test_release_lock.py`
- submodule gitlink `nirs4all-core` -> `d8308793081457aa073b88e4376171e0c08bb535`

## Tests Run

- `python3.11 scripts/n4a_release_lock.py generate --manifest docs/contracts/release/aggregation-manifest.n4a.json --output docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3.11 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 -m pytest -q tests/test_release_lock.py tests/test_e2e_scenarios.py`

## Result

- Core lock member now pins `d830879` / `v0.3.0`, `dirty=false`.
- Python aggregate package remains `nirs4all-core` with imports
  `nirs4all_core` and `n4a`.
- Rust, npm/WASM, R, and MATLAB/Octave aggregate surfaces remain `nirs4all`.
- `repo_aliases`, `legacy_distribution`, and legacy topology artifact path were
  removed from the release lock source.
- E2E scenario prerequisites now use `nirs4all_core/_execution.py`.

## Risks / Follow-up

- Lockstep dag-ml/dag-ml-data parity case IDs still include
  `nirs4all_lite_browser_compile_plan`. They are shared historical case IDs,
  not package aliases. Rename only in a coordinated dag-ml/dag-ml-data bump.
- The full Python `nirs4all` and `nirs4all-studio` production surfaces remain
  held outside the non-prod release batch.
