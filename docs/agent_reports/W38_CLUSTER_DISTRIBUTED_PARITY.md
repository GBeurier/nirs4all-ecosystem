# W38 report - cluster distributed parity

Summary:
W38 added a live distributed parity harness for `nirs4all-cluster`. A fake deterministic `nirs4all` backend is executed through the server/worker/client flow and compared to the local envelope so scheduler/RBAC transport behavior stays aligned with local execution expectations.

Code changed:
- Added `tests/test_distributed_parity.py`.
- Covered server/worker registration, RBAC tokens, job submission, and normalized distributed/local result envelopes.
- Validated the new parity harness alongside existing adapter, server API, and RBAC tests.

Files touched:
- `tests/test_distributed_parity.py`

Commits:
- `nirs4all-cluster/refactor/W38-distributed-parity` `4ffda1d`
- Integrated into `nirs4all-cluster/refactor/integration-cluster` as `afacc0e`

Tests run:
- `.venv/bin/python -m pytest tests/test_distributed_parity.py tests/test_core_adapter.py tests/test_server_api.py tests/test_rbac.py -q` -> `49 passed`.
- `.venv/bin/ruff check .` -> passed.
- `.venv/bin/mypy nirs4all_cluster` -> passed.
- `.venv/bin/python -m pytest -q` -> `125 passed, 1 skipped`.

Impact:
Advances `DEC-CLU-001`/cluster readiness and gives `B-018` a distributed runtime parity hook.

Next action:
Replace the fake deterministic backend with a real nirs4all DAG job once cutover-safe runtime envelopes are stable.

Sync doc updated: yes
