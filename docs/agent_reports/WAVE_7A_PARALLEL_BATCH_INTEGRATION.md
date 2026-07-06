# Wave 7A Parallel Batch Integration

Date: 2026-07-06

## Scope

Integrated the parallel Codex/Claude batch after review and local targeted gates.

## Repinned Heads

- `dag-ml`: `0c6a4f2`
- `dag-ml-data`: `53dfb1c`
- `nirs4all`: `4b75d8c5` (`refactor/L17-pyref`, documentation only in this wave)
- `nirs4all-benchmarks`: `7c32149`
- `nirs4all-cluster`: `d8defd6`
- `nirs4all-cockpit`: `dc82da3`
- `nirs4all-core`: `f882867`
- `nirs4all-datasets`: `588e4673`
- `nirs4all-methods`: `d96560a4`
- `nirs4all-org`: `81b793b`
- `nirs4all-papers`: `cb804ef`
- `nirs4all-repository`: `bd82dd4`
- `nirs4all-studio`: `87b2a9d`
- `nirs4all-tools`: `9330e4a`
- `nirs4all-ui`: `73dcce9`
- `nirs4all-web`: `9a4cc84`

## Main Decisions

- Keep `nirs4all` Python full and `nirs4all-studio` prod out of final publication.
- Accept `nirs4all-studio` RC installer hardening as local/testable flow only; no tag or release.
- Sync `dag-ml` and `dag-ml-data` parity tolerance profiles together to avoid cross-repo contract drift.
- Sync `nirs4all-web` vendored `nirs4all-ui` after adding the dataset preview subpath.
- Keep `nirs4all-web` client-side-only; no backend dependency was introduced.

## Validation

- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_submodule_repin.py plan --json`
- `python3 -m pytest -q tests/test_submodule_repin_plan.py tests/test_gitmodules_topology.py tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_e2e_scenarios.py`

Result: `100 passed`.

## Remaining Risks

- `aggregation-lock.n4a.lock.json` still needs a dedicated refresh/validation pass after remote CI settles.
- Full parity was not run in this wave by request; the Python parity audit still reports 11 expected fallback shapes.
- `nirs4all-web@9a4cc84` Actions were still queued when this integration report was written.
