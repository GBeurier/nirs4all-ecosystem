# W55 - Studio Bypass Parity

Status: complete.

## Scope

Advanced B-011/B-017 by adding a route-level Studio parity gate for one
important run/result path:

- `POST /api/runs/quick` executes through the real `_execute_run_job` and
  `_execute_pipeline_training` path.
- `nirs4all.run(engine="dag-ml")` returns a Python runtime `RtResult`-shaped
  envelope whose manifest reports `engine="legacy"` with fallback diagnostics.
- `GET /api/runs/{run_id}` exposes the actual engine, requested engine, and
  diagnostics from that envelope.
- `GET /api/aggregated-predictions/chain/{chain_id}` preserves result metadata
  from the runtime-backed results repository view.

## Changes

- Added a focused backend test in `tests/test_runs_engine_routing.py`.
- Added a small in-test frame/repository adapter to exercise the
  `/aggregated-predictions` result retrieval route without real compute.
- No frontend or UI changes.
- No production adapter changes were needed.

## Verification

From `_worktrees/W55-studio-bypass-parity`:

```bash
/home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runs_engine_routing.py -q
/home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m compileall api tests/test_runs_engine_routing.py
/home/delete/.local/bin/ruff check api tests/test_runs_engine_routing.py
```

Results:

- `14 passed, 2 warnings` for the focused backend pytest. The warnings are the
  existing fallback-warning fixtures.
- `compileall` passed for `api` and the touched test.
- Ruff passed for `api` and the touched test.

## Blockers

None.

## Notes

The worktree did not contain its own `.venv`, and `python3 -m pytest` used the
system Python without `pytest`. The checks therefore used the existing Studio
virtualenv at `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python`, with the
current working directory pinned to the W55 worktree.
