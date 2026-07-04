# Wave 5E - Ready E2E execution mode

Date: 2026-07-04

## Scope

Make the cross-language E2E runner more useful for the V1 coordination gate without turning the two known public-checkout data blockers into artificial red CI.

## Changes

- `run-ready --execute` now accepts `--allow-blocked`.
- Without `--allow-blocked`, blocked scenarios still make the command exit `2`.
- With `--allow-blocked`, the command executes every ready scenario and exits `0` only if those ready scenarios pass and every blocked scenario is explicitly listed with `--allowed-blocked-scenario`.
- Allowlisted blocked scenarios must also have every missing requirement matched by a `--allowed-blocked-requirement SCENARIO_ID=REQUIREMENT_FRAGMENT` entry.
- The GitHub workflow exposes `allow_blocked` for manual `workflow_dispatch` execute runs.
- For `run-ready`, `allow_blocked=true` means "ready subset passed" can be green only while the two declared public-checkout blockers remain reported.
- For a selected blocked scenario, `--allow-blocked` can execute ready steps for debugging, but the command still exits `2` if any selected step remains blocked.
- Allowlisted blocked scenarios are emitted as a GitHub warning and appended to the step summary so a green manual run cannot silently hide them.
- Claude review found that scenario-id-only allowlisting could false-green if a different blocker appeared in an already allowlisted scenario; the final implementation now allowlists both scenario IDs and expected missing-requirement fragments.

## Current public-checkout behavior

With `N4A_WORKSPACE_ROOT=/home/delete/nirs4all/nirs4all-ecosystem`, the dry `run-ready` plan reports:

- ready: 8 scenarios
- blocked: 2 scenarios
  - `e2e-r-dataset-io-pipeline-save`
  - `e2e-cluster-dag-rights-client-core`

Those blockers remain data/fixture availability blockers; this change does not mark them as passed.

## Tests

- `python3 scripts/n4a_e2e_scenarios.py validate`
- `N4A_WORKSPACE_ROOT=/home/delete/nirs4all/nirs4all-ecosystem python3 -m pytest -q tests/test_e2e_scenarios.py` (`39 passed`)
- `N4A_WORKSPACE_ROOT=/home/delete/nirs4all/nirs4all-ecosystem python3 scripts/n4a_e2e_scenarios.py run-ready`
- `python3 scripts/n4a_e2e_scenarios.py run e2e-python-reopen-paper-repository-refit --execute --allow-blocked`
- `python3 -m pytest -q` (`63 passed`)
- `git diff --check`

## Risk

Manual execute runs can now succeed while explicitly allowlisted blockers remain. This is intentional only for `run-ready --allow-blocked --allowed-blocked-scenario ... --allowed-blocked-requirement ...`; reports and stderr must be read as "ready subset passed", not "full parity completed".
