# W24 report - Studio runtime routes

Summary:
Claude session `e84bd37a-9ec0-4851-a2c3-480bfa336725` stopped when the Claude weekly limit was reached, but left a small coherent Studio fix. Supervisor inspected, tested, and committed the slice.

Code changed:
`retry_run` now preserves the original run's requested `engine` when constructing the retry run, preventing a `dag-ml` run from silently falling back to the library default on retry.

Files touched:
`api/runs.py`
`tests/test_runs_engine_routing.py`

Commits:
`nirs4all-studio/refactor/W24-runtime-routes` `455e1f3` (`fix(runs): preserve requested engine on retry`)

Tests run:
`PYTHONPATH=. /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runs_engine_routing.py -k retry_run_preserves_requested_engine -q` -> `2 passed, 11 deselected`
`PYTHONPATH=. /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m compileall -q api/runs.py tests/test_runs_engine_routing.py`
`ruff check api/runs.py tests/test_runs_engine_routing.py` -> all checks passed

Tests not run and why:
Full Studio backend suite not run in this salvage pass; only the targeted retry-engine route regression was changed.

Blockers:
Claude quota exhaustion prevented the broader W24 runtime-route adoption scope.

Impact on blockers/locks:
Small advancement for `B-017`/`B-018`; retry now preserves requested engine. Route-level runtime adoption remains incomplete.

Next action:
Integrate `455e1f3` into the Studio integration branch if accepted, then resume broader W24 after quota reset or via Codex/manual work.

Sync doc updated: no
