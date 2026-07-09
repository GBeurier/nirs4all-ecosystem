# WAVE 9ZC — R-universe core 0.3.9 tracking and cockpit cleanup

Date: 2026-07-10

## Coordination

- Main Codex lane prepared the `GBeurier/gbeurier:update-nirs4all-core-0.3.9` branch from current
  `r-universe/gbeurier:master`.
- No Claude lane was used for this narrow follow-up.

## Files/repos changed

- `GBeurier/gbeurier` fork branch `update-nirs4all-core-0.3.9`: rebased on upstream master and reduced to one
  gitlink change, `nirs4all` submodule `5f207202124725d749cf3f2a013b57caaa1d0b20` -> `2d416b72e9c417a064d3ca3501e4e84280cee1f0`.
- `nirs4all-cockpit`: removed cached dashboard references to the removed Release bundles UI, corrected R-universe manual-action
  affects to point at the active `r-universe/gbeurier` submodules/workflow, and regenerated `data/manual-actions.json`.
- `nirs4all-ecosystem`: advanced the `nirs4all-cockpit` gitlink to `d2400aa`.

## Validation

- `nirs4all-cockpit`: `n4a-cockpit validate-targets ops/targets.yaml`.
- `nirs4all-cockpit`: `pytest -q tests/test_targets_topology.py tests/test_local_manifests.py tests/test_version.py tests/test_cli.py::test_admin_actions_can_write_public_json`.
- `nirs4all-cockpit`: GitHub `ci`, `version-guard`, and Pages are green for `d2400aa`.
- Public cockpit JSON now serves `runiverse-core-rebuild` with the prepared fork branch and `r-universe/gbeurier:Update universe`.

## Risks/decisions

- R-universe still serves aggregate `nirs4all 0.3.8`; the cockpit keeps this as a visible `todo` action instead of marking green.
- PR creation against `r-universe/gbeurier` failed with the available GitHub credentials (`createPullRequest` not accessible);
  the compare branch remains ready for a manual merge or a token with pull-request write scope.
- Full parity was not rerun in this micro-batch.
