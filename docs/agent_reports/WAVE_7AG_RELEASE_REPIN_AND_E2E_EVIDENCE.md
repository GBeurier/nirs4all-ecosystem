# Wave 7AG — Release Repin and E2E Evidence Refresh

Date: 2026-07-07 05:42 CEST

## Scope

- Kept `nirs4all-ui` untouched because another agent is working there for `nirs4all-quality`.
- Released and repinned non-production repos only. `nirs4all` Python and `nirs4all-studio`
  remain outside the production switch.
- Refreshed the custom-app-host E2E evidence without editing `nirs4all-ui`.

## Releases and Pins

- `nirs4all-io` pinned to `d275a7b` / `v0.1.7`.
- `nirs4all-datasets` pinned to `ed168751` / `v0.3.5`.
- `nirs4all-tools` pinned to `cc72fc4` / `v0.0.3`.
- `nirs4all-benchmarks` pinned to `79724f2` / `v0.1.5`.
- `nirs4all-org` pinned to `fe18d5c`.
- `nirs4all-cockpit` pinned to `37323fc`.

## Local Validation

- `nirs4all-tools`: `python3.11 -m pytest -q`, `python3.11 -m ruff check .`,
  `python3.11 -m mypy src/nirs4all_tools`, `python3.11 -m build`,
  `python3.11 -m twine check dist/*`.
- `nirs4all-benchmarks`: `PYTHONPATH=src python3.11 -m pytest -q`,
  `python3.11 -m ruff check src tests`, `python3.11 -m mypy src/nirs4all_benchmarks`,
  `python3.11 -m build`, `python3.11 -m twine check dist/*`.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py run e2e-core-ui-custom-app-host --execute`.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py evidence --json`
  returned `verified_count=11`, `artifact_count=48`, `failed_count=0`.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py validate` returned
  `OK: 11 cross-language E2E scenarios`.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py coverage --json`
  returned `ready_count=11`.
- `nirs4all-ecosystem`: `python3 -m pytest -q tests/test_e2e_scenarios.py tests/test_submodule_repin_plan.py tests/test_release_surface_matrix.py tests/test_release_lock.py tests/test_gitmodules_topology.py`
  returned `114 passed`.

## Parallel Review

- Claude Code reviewer session `b761acee-58da-4c62-88df-6d8f67792b6c` ran read-only
  against the release/publication surface. It reported no file edits, no unpublished tags,
  no `nirs4all-ui` build dependency in this release wave, and confirmed the two unresolved
  blockers are PyPI Trusted Publisher setup for `nirs4all-tools` and `nirs4all-benchmarks`.
- Codex reviewer `019f3a9f-21d3-7eb3-b0c6-0068d2533869` checked the custom-app-host
  evidence path and verified that the five expected artifacts are produced without touching
  `nirs4all-ui`.
- Codex reviewer `019f3a9f-357a-76b2-866b-6547f3d4f194` checked the publication matrix for
  `nirs4all-io`, `nirs4all-datasets`, `nirs4all-org`, and `nirs4all-cockpit`, including
  registry and GitHub Actions status.

## Publication Status

- `nirs4all-tools v0.0.3`: GitHub Release created and sdist/wheel attached; CI green.
  PyPI publish is blocked by PyPI Trusted Publisher `invalid-publisher`.
- `nirs4all-benchmarks v0.1.5`: GitHub Release created and sdist/wheel attached; CI,
  version guard and Pages green. PyPI publish is blocked by PyPI Trusted Publisher
  `invalid-publisher`.
- `nirs4all-datasets v0.3.5`: Python wheels/sdist, R source tarball and GitHub Release
  assets published; CI, ABI, npm, crates, source, Pages and R release lane green.
- `nirs4all-io v0.1.7`: CI, ABI, npm, crates, source, Python binding, WASM binding,
  Octave binding, parity oracle, cross-binding parity and R release lane green; the R tarball
  is attached to the GitHub Release.
- `nirs4all-org`: Pages and version guard green for the cluster tools-hub update.
- `nirs4all-cockpit`: collect and Pages green for the refreshed release state.
- Registry spot checks: PyPI has `nirs4all-io 0.1.7` and `nirs4all-datasets 0.3.5`;
  npm has `@nirs4all/io-wasm 0.1.7`, `@nirs4all/datasets-wasm 0.3.5`, and `nirs4all 0.2.12`;
  crates.io search shows `nirs4all-io* 0.1.7`, `nirs4all-datasets-* 0.3.5`, and `nirs4all 0.2.12`.
  R-universe still reports `nirs4allio 0.1.6`, `nirs4alldatasets 0.3.4`, and `nirs4all 0.2.8`
  while its own build pipeline catches up.

## Open Risks

- Full Python-reference parity was not rerun in this wave, by request to batch it after
  larger changes.
- `nirs4all-tools` and `nirs4all-benchmarks` PyPI publication requires configuring PyPI
  Trusted Publisher for the `pypi` environment or providing a PyPI token; no `pypi_token`
  exists in the workspace token set.
- Cross-language E2E coverage is evidence-green, but still has known strictness debt:
  `strictness_gaps=12`, `v1_contract_phase_count=13`, `v1_gap_phase_count=31`, and
  `e2e-multimodal-python-r-wasm-roundtrip` still has no strict parity check.
- R-universe freshness still lags GitHub/PyPI/npm/crates publication status and should be
  rechecked before treating the R-universe package index as current.

## Decisions

- Kept `.n4a-e2e-artifacts/` unversioned; only the evidence result and commands are recorded.
- Treated `nirs4all-ui` as external ownership for this wave. The custom-app-host smoke uses
  the existing `nirs4all-web/studio-lite/vendor/nirs4all-ui` shim in `--check` mode and does
  not sync or mutate the UI repo.
- Did not attempt to bypass failed PyPI Trusted Publishing with unavailable credentials.
