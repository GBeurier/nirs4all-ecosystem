# WAVE 7N - RC10 tag canonicalization

Date: 2026-07-06

## Scope

Release-lock coordination for the seven aggregation members only. `nirs4all-ui`
and `nirs4all-quality` were treated as protected worktrees and were not edited.

## Changes

- Published `n4a-v1-rc10-2026.07-refactor` on the selected commits that still
  only carried older coordination tags:
  - `dag-ml` `4238443c2ce5`
  - `nirs4all-formats` `181946f141ed`
  - `nirs4all-methods` `115077ae4551`
  - `nirs4all-core` `1708ab0305a8`
- Added `release_selection_policy.preferred_exact_tag` to the aggregation
  manifest.
- Updated `scripts/n4a_release_lock.py` so lock generation prefers the manifest
  tag when multiple exact tags point to the same selected commit.
- Regenerated `docs/contracts/release/aggregation-lock.n4a.lock.json`; all seven
  members now record `n4a-v1-rc10-2026.07-refactor` as `state.exact_tag` while
  keeping the same selected commits.
- Added a unit test covering deterministic preferred-tag selection.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3.11 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -p no:cacheprovider`
  - Result: `23 passed`
- `/usr/bin/python3.11 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-selected-rc10-20260706 validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - Result: validated
- `/usr/bin/python3.11 scripts/n4a_release_surface_matrix.py validate`
  - Result: validated
- `/usr/bin/python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output /tmp/n4a-fetch-rc10-audit.json`
  - Result: `7/7` member commits checked out, `0` unfetchable
- `git diff --check`
  - Result: passed

## Risks and Decisions

- This is a coordination/tagging change, not a runtime-code change.
- Existing historical tags were not moved or deleted.
- Python `nirs4all` and `nirs4all-studio` production releases remain held.
- Full Python parity was not rerun in this sub-lot; the last full parity gate
  remains `799 passed, 0 skipped, 0 xfailed` from the previous large batch.
