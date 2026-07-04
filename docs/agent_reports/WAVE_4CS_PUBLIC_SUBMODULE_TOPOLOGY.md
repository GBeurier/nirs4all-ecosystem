# WAVE 4CS - Public submodule topology

Date: 2026-07-04
Owner: Codex integration

## Scope

Closed the release/topology gap reported by the read-only Claude Code audit:
`nirs4all-ecosystem/.gitmodules` still modeled the older pre-refactor topology.

## Integrated changes

- Replaced SSH submodule URLs with HTTPS URLs so public topology is fetchable in
  local/CI environments without a GitHub SSH key.
- Removed out-of-scope/private or superseded submodules from the public
  ecosystem topology:
  - `nirs4all-drafts`
  - `nirs4all-lab`
  - `nirs4all-lite`
- Added the public V1 refactor repos that were missing from `.gitmodules`:
  - `nirs4all-cockpit`
  - `nirs4all-core`
  - `nirs4all-providers`
  - `nirs4all-tools`
  - `nirs4all-ui`
- Updated all public gitlinks to their remote `main` heads, including the latest
  cockpit and web commits from this wave.
- Added `tests/test_gitmodules_topology.py` to lock the intended topology:
  public modules only, HTTPS URLs, `branch=main`, and exact match between
  `.gitmodules` paths and gitlink entries.

## Tests run

- `python3.11 -m pytest -q tests/test_gitmodules_topology.py tests/test_e2e_scenarios.py tests/test_release_lock.py`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`

## Notes

- Local direct release-lock validation was not rerun successfully in the live
  sibling workspace because it expects selected RC checkouts such as
  `/home/delete/nirs4all/RC-v1-dagml`; this is an existing selected-workspace
  validation mode, not caused by the submodule topology patch.
- The public submodule topology now follows the active operating constraint:
  `nirs4all-drafts` and `nirs4all-lab` are private/out of scope and are not
  modeled as public ecosystem submodules.
