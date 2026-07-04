# Wave 5A - RC release pins and provider gate hardening

Date: 2026-07-04
Coordinator: Codex

## Scope

This wave pins the non-prod V1 release candidate heads in `nirs4all-ecosystem`
after parallel agent publication work. It intentionally excludes the production
sensitive `nirs4all` Python library and `nirs4all-studio` production release.

Private/off-scope repositories were not touched: `nirs4all-drafts`,
`nirs4all-lab`, and token files.

## Parallel agents

- Python/repository lane agent: released `nirs4all-aom`, `nirs4all-benchmarks`,
  `nirs4all-cluster`, `nirs4all-papers`, `nirs4all-providers`,
  `nirs4all-repository`, and `nirs4all-tools`.
- Native/Rust/core lane agent: released `nirs4all-formats`, `nirs4all-io`,
  `nirs4all-datasets`, `nirs4all-methods`, and `nirs4all-core`.
- Reviewer agents:
  - low-level release audit for `formats/io/datasets/methods`;
  - core/providers cascade audit.

## Pinned release heads

| Repo | Version | Commit | Notes |
|---|---:|---|---|
| `nirs4all-aom` | `v0.10.3` | `736429c7e6b9a74f19c5713935da3a71af6de55d` | Python package release. |
| `nirs4all-benchmarks` | `v0.1.3` | `d8d2d4a3f22314a5972082147160a00f9c2992df` | Python package release; local JS check was not rerun by worker because node was unavailable there. |
| `nirs4all-cluster` | `v0.1.2` | `d97239fdc6d0a56abf4a27528eb934c6436c4db0` | Python package release. |
| `nirs4all-cockpit` | `v0.1.4` | `cdf302a25b611e44592887e21476879a2f0b0971` | Cockpit target validation release. |
| `nirs4all-core` | `v0.2.4` | `0df950adff05c7de68f50a20743e6d164e3c34ce` | Aggregate release; Python distribution is `nirs4all-core`; R/Rust/WASM/MATLAB surfaces are `nirs4all`. |
| `nirs4all-datasets` | `v0.3.3` | `8551c9f0f31dc96c5ac75d5d6857b6468ba84136` | Dataset catalog/bindings cascade release. |
| `nirs4all-formats` | `v0.2.2` | `07beca5b67623f8660eca904332565a1c96b2a1c` | Formats cascade release. |
| `nirs4all-io` | `v0.1.6` | `023421ce16e1e6403a6b805275a0e511f011a9b9` | IO cascade release. |
| `nirs4all-methods` | `v1.0.2` | `f452d95aaf828d2e9a5176e8a6815455424483e3` | Native methods/bindings release. |
| `nirs4all-org` | `v1.0.1` | `d6fe66a86e20d44754dd4c2dcf6c827b679ecedd` | Static site release for shared UI links. |
| `nirs4all-papers` | `v0.2.2` | `9130b2de2129cba74eec820a0c8aa47ec76ac33c` | Papers package release. |
| `nirs4all-providers` | `v0.2.3` | `46fa0410a7e3e66eda841be823548e559f814140` | Supersedes `v0.2.2`; publish workflow now runs CI/release gate, local backing gate, and tag/version validation. |
| `nirs4all-repository` | `v0.1.3` | `62a86040c5156ac5609642c2f2a13a3c53b33f5d` | Repository/catalog release. |
| `nirs4all-tools` | `v0.0.2` | `7c46b43b848a180bd0c2fb1ac5744bb2959d6b52` | Converter/tools release. |
| `nirs4all-ui` | `v0.1.2` | `58fe3e0ab578d576d7a23cd989ed853feaf497ca` | Component package and GitHub Pages showcase release. |
| `nirs4all-web` | `v0.1.2` | `ea1a8bb33bf8870317e38da78ef6aa5a268b4bf4` | Client-side-only web release with vendored UI/core shims. |

## Local checks reviewed in this wave

- `nirs4all-core`:
  - `PYTHONPATH=bindings/python/src python3 -m unittest discover -s bindings/python/tests`
  - `PATH="$HOME/.nvm/versions/node/v22.21.1/bin:$PATH" npm test --prefix bindings/wasm`
  - `PYTHONPATH=bindings/python/src python3 -m unittest bindings.python.tests.test_release_topology`
  - `python3.11 -m build bindings/python`
  - `python3.11 -m twine check bindings/python/dist/*`
- `nirs4all-providers`:
  - `python3.11 scripts/ci_gate.py`
  - `PYTHONPATH=src python3.11 -m nirs4all_providers.local_release_gate --workspace-root /home/delete/nirs4all --json`
  - `python3.11 -m build`
  - `python3.11 -m twine check dist/*`
- `nirs4all-datasets` risk recheck:
  - `.venv/bin/python -m pytest tests/test_acquire.py::test_resolve_returns_contract -q`
  - `.venv/bin/python -m pytest tests -q` -> `234 passed`
- `nirs4all-ecosystem`:
  - `python3 scripts/n4a_e2e_scenarios.py validate` -> `OK: 10 cross-language E2E scenarios`
  - `python3 -m pytest -q tests/test_e2e_scenarios.py` -> `32 passed`
  - `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_gitmodules_topology.py tests/test_cutover_state_gate.py` -> `24 passed`
  - `python3 scripts/n4a_release_surface_matrix.py validate` -> public V1 surface matrix validated
  - `python3 scripts/n4a_release_lock.py checkout-members ... --output /tmp/n4a-release-lock-external`
    then `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-release-lock-external validate ...`
    -> release lock validated. Note: the lock member key remains the historical
    `lite` key while its `repo_path`/`repo_url` target is `nirs4all-core`; this
    is currently asserted by `tests/test_release_lock.py`.

## Remote state to monitor

- Many GitHub Actions release workflows were still queued or in progress when
  this report was written. They must be polled before claiming final
  publication completion.
- `nirs4all-core` PyPI Trusted Publisher remains a known risk until
  `release-python` completes successfully.
- `nirs4all-papers` had a previous GitHub Pages deploy failure at the
  `deploy-pages` step despite CI/content checks passing; monitor the
  `v0.2.2` site workflow for whether GitHub Pages recovers.
- `dag-ml` and `dag-ml-data` were deliberately not released by the native lane:
  local branch heads were not aligned with their stable release tags.
- The aggregation lock still carries the legacy member key `lite` for the core
  aggregate target. This is tested/documented, but it remains naming debt to
  remove after the final cutover.

## Decisions

- Keep `nirs4all` Python and `nirs4all-studio` production releases out of this
  wave.
- Treat `nirs4all-providers v0.2.2` as superseded by `v0.2.3`, because the
  latter hardens the publish workflow before PyPI publication.
- Do not run full parity yet; use targeted gates while the release batch is
  still integrating, then run broad parity after remote workflows settle.
