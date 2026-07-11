# Wave 9ZX - E2E and pin alignment

## Scope

- Repo: `nirs4all-ecosystem`
- Lane: release lock / E2E contract hygiene

## Changes

- Advanced the `nirs4all-datasets` submodule from `67d47c55` to `2b074472` (`v0.3.8`).
- Updated the published custom-host E2E contract from `nirs4all-ui@0.1.11` to `nirs4all-ui@0.1.12`.

## Rationale

- After fetching tags, `nirs4all-datasets` was proven to be four commits behind the published `v0.3.8` release tag.
- `nirs4all-ui` is pinned and published at `v0.1.12`; the E2E contract still expected `0.1.11`.

## Validation

- `python3.11 -m pytest -q tests/test_e2e_scenarios.py::test_cross_language_e2e_manifest_validates_current_contract tests/test_e2e_scenarios.py::test_cross_language_e2e_cli_coverage_full_strict_gate_passes tests/test_gitmodules_topology.py tests/test_submodule_repin_plan.py`
  - Result: `7 passed in 3.47s`
- `python3.11 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_held_transition_readiness.py`
  - Result: `24 passed in 0.35s`
- `git diff --check`
  - Result: passed

## Risks

- This does not execute the full runtime E2E suite; it aligns the manifest and gitlink so the next full run uses the current published datasets/UI surfaces.
- `nirs4all` transition pre-publish run `29146982675` was still in progress when this report was written and remains monitored separately.
