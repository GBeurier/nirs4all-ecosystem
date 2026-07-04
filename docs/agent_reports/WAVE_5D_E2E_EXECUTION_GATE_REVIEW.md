# Wave 5D - E2E execution gate review

Date: 2026-07-04

## Review result

Claude/Codex read-only review confirmed that the 10 cross-language E2E scenarios are honestly labelled, but the default GitHub gate is still a contract/plan gate, not a full behavioral parity gate.

The push/PR workflow validates the manifest, runs pytest contract tests, and plans scenarios. It does not execute the heavy scenario commands unless `workflow_dispatch` is called with `execute=true`.

## Changes integrated

- Added `.n4a-e2e-artifacts/` to `.gitignore` so local execution evidence cannot be committed accidentally.
- Added a test that the runtime artifact directory is ignored.
- Added a test that `requires_paths` stay within declared scenario repos unless the scenario is explicitly allowlisted as a public-checkout data blocker.

## Remaining E2E debt

- Default push/PR green means "contract and wiring are coherent", not "all cross-language runtime flows passed".
- Two scenarios remain explicitly data-blocked in public checkout:
  - `e2e-r-dataset-io-pipeline-save`
  - `e2e-cluster-dag-rights-client-core`
- `repository_forced_best_refit` is still contract-level in the scenario matrix; no scenario gives it strict runtime parity coverage yet.
- Real-data R/datasets/io and cluster numeric oracle execution must be moved out of allowlisted blockers before this gate can be called a full parity gate.
- A future scheduled or label-gated execute job should run `run-ready --execute` once the required public fixtures are available.

## Tests

- `python3 scripts/n4a_e2e_scenarios.py validate`
- `N4A_WORKSPACE_ROOT=/home/delete/nirs4all/nirs4all-ecosystem python3 -m pytest -q tests/test_e2e_scenarios.py`
