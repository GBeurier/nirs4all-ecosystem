# W58 report - Cluster DAG rights/result contract

Summary:
Added an additive scheduler/rights/result contract for cluster DAG-shaped whole-run jobs. The server now records credential-derived job submission metadata, returns server-authoritative executor assignment metadata on leases, and overwrites stored task result provenance from the authenticated executor principal. The contract keeps V1 scheduling at whole `nirs4all.run` task granularity and does not claim fine-grained graph execution.

Code changed:
- Added `DagSchedulerContract`, `JobSubmissionMetadata`, `TaskAssignmentMetadata`, and `ResultProvenance` to the shared wire schemas.
- SDK-built jobs now include inferred scheduler metadata; raw REST submissions are normalized by the server.
- Server persistence stores submitter metadata in the existing job request payload and propagates it into task leases.
- Worker result completion stores server-attested provenance while preserving metrics/counts/artifacts/extra result fields.
- Added a focused RBAC/API test covering client-submitted DAG job rights, server-leased executor assignment, denied completion by a submitter-only credential, and result provenance preservation.
- Documented the new additive metadata in `docs/job-spec.md`.

Files touched:
- `docs/job-spec.md`
- `nirs4all_cluster/client.py`
- `nirs4all_cluster/schemas.py`
- `nirs4all_cluster/server/app.py`
- `nirs4all_cluster/server/db.py`
- `tests/test_core_adapter.py`
- `tests/test_rbac.py`

Commits:
- `b70ca42` - `feat(cluster): add DAG rights provenance contract`

Tests run:
- `uv run --extra dev pytest tests/test_rbac.py::test_dag_scheduler_contract_records_rights_and_result_provenance tests/test_core_adapter.py::test_build_nirs4all_run_request_records_parity_contract tests/test_core_adapter.py::test_submit_nirs4all_run_uses_adapter_contract -q` -> 3 passed.
- `uv run --extra dev pytest tests/test_rbac.py tests/test_core_adapter.py tests/test_server_api.py tests/test_distributed_parity.py -q` -> 51 passed.
- `uv run --extra dev ruff check .` -> passed.
- `uv run --extra dev mypy nirs4all_cluster` -> passed.
- `uv run --extra dev pytest -q` -> 127 passed, 1 skipped.

Tests not run and why:
- Real `tests/test_integration_nirs4all.py` via the sibling nirs4all venv was not run separately; full repo pytest included it and it skipped in this environment.

Blockers:
- None for this W58 slice.

Impact on blockers/locks:
- Advances L15/cluster by making the client-submitted job, server-requested executor lease, credential-derived rights, and task result provenance explicit in the wire contract.
- Fine-grained DAG node/fold/subtree scheduling remains intentionally deferred to future core/dag-ml execution-unit contracts.

Next action:
- Integrate this additive contract into the cluster integration branch; future work can bind worker IDs to executor principals if the security model grows beyond trusted-LAN V1.

Sync doc updated: no
