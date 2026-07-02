# Wave 4O - Python compatibility ledger refresh

Date: 2026-07-02  
Coordinator: Codex

## Scope

Refresh the Python `nirs4all` compatibility ledger after the RC parity and
Studio runtime evidence updates. No runtime code was changed and full parity was
not rerun in this wave.

## Published Code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all` | `rc/v1-full-refactor-python` | `a103fd2` / `n4a-v1-rc1-2026.07-refactor` | `docs/compatibility.md`, `docs/compatibility.json` |

## Changes

- Updated `docs/compatibility.{md,json}` `last_reconciled` metadata from stale
  working-tree commits to the selected RC stack: Python `3d568abe`, `dag-ml`
  `7f86a9b`, and `dag-ml-data` `e681685`.
- Marked the `studio_oracle` cross-engine surface as `exists` with explicit
  Studio-side owning tests for engine threading, fallback policy, actual-engine
  recording, and manifest round-trip.
- Added a `Current RC parity proof` note explaining that the latest full
  `pyref_oracle_full` proof on the selected runtime stack is `659 passed, 227
  deselected`, with no parity skips or xfails.
- Clarified that the static marker audit reports skip call sites, not realized
  Python-reference parity skips.

## Local Gates

- `python3.11 -m json.tool docs/compatibility.json`
- `python3.11 -m tests.integration.parity._marker_audit --check`
  - `126` skip call sites are classified by the closed taxonomy.
  - `42` tolerance literals match the published bands.
  - Verdict: OK.
- `python3.11 -m pytest tests/integration/parity/test_marker_audit.py tests/integration/parity/test_compatibility_ledger.py tests/integration/parity/test_native_fallback_boundary.py -q`
  - `27 passed, 1 warning`.
- Studio-side proof with RC imports on `PYTHONPATH`:
  - `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runtime_engine.py tests/test_studio_oracle_routes.py tests/test_runs_engine_routing.py -q`
  - `45 passed, 7 warnings`.

## Remaining Risk

- The full numerical parity proof was not rerun on `a103fd2` because the commit
  only changes docs. The last full proof remains on runtime head `3d568abe`;
  final release should rerun full parity after the next material runtime batch
  or immediately before production cutover.
