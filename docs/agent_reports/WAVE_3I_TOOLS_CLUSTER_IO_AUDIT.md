# Wave 3I - Tools Cluster IO Audit

Date: 2026-07-01

## Scope

Parallel W3I audit and one implemented lane:

- Lane D (`nirs4all-tools`): standalone loose prediction lowering.
- Lane I (`nirs4all-cluster`): scheduler/RBAC audit only.
- Lane G (`nirs4all-datasets` + `nirs4all-io`): IO/datasets public binding audit
  only.

No full Python-reference parity was run.

## Agents

- Newton: read-only `nirs4all-tools` audit. Recommended a narrow
  `loose-predictions` lowering slice and explicitly no `.n4a`/DuckDB/full
  `runs/` YAML converter in this batch.
- Ampere: read-only `nirs4all-cluster` audit. Confirmed RBAC `read`/`execute`
  is coherent and recommended a future DB-only scheduler fairness slice.
- Lovelace: read-only datasets/IO audit. Confirmed `_worktrees/INT-io` is the
  authoritative IO integration checkout and identified a public binding gap
  around `to_dataset_package` / `to_io_spec`.
- Mendel + Banach: read-only tools reviewers. Initial no-go findings were
  resolved before commit.

## Integrated Lane D

Repository: `nirs4all-tools`

Commit:

- `3fceb72 feat(legacy): lower standalone loose predictions`

Files changed:

- `README.md`
- `src/nirs4all_tools/commands.py`
- `src/nirs4all_tools/loose_predictions.py`
- `tests/fixtures/legacy/old_workspace_mixed/run_predictions.json`
- `tests/test_real_golden_fixtures.py`

Behavior:

- Adds strict preview lowering for exactly one standalone
  `*_predictions.json` loose-prediction payload.
- Requires explicit metadata (`model_name`, `model_class`, `fold_id`,
  `task_type`, `sample_indices`, etc.) rather than inventing values.
- Writes workspace-v2 run/pipeline/chain/prediction metadata and
  `arrays/<dataset>.parquet` sidecars when the `parquet` extra is available.
- Always preserves the original loose JSON and sibling metadata files under
  `preserved/loose-predictions/`.
- Keeps mixed legacy workspaces (`store.duckdb`, `runs/`, loose prediction
  files) on opaque preservation in best-effort mode, and strict refusal.
- Aligns dry-run, best-effort, and strict behavior when `pyarrow` is missing:
  dry-run reports `would_preserve`, best-effort preserves opaque, strict refuses
  before writing.

## Tools Tests

From `nirs4all-tools`:

- `PYTHONPATH=src pytest -q`
  - PASS: 95 passed.
- `PYTHONPATH=src pytest tests/test_real_golden_fixtures.py tests/test_commands.py tests/test_native_results.py tests/test_cli.py -q`
  - PASS: 57 passed.
- `ruff check .`
  - PASS.
- `mypy`
  - PASS.
- `python3 -m py_compile src/nirs4all_tools/loose_predictions.py src/nirs4all_tools/commands.py`
  - PASS.
- `git diff --check`
  - PASS.

## Audit Results Not Yet Integrated

Cluster:

- Current head: `nirs4all-cluster@eac4d0b8`, clean, ahead of origin.
- Recommended future slice: in `lease_next_task`, keep `priority DESC`, then
  order by `job_in_flight ASC`, `created_at ASC`, `id ASC` so one large
  same-priority DAG/matrix job does not monopolize leases.
- Tests to add when implemented: scheduler fairness and high-priority override
  in `tests/test_scheduler.py`; targeted `tests/test_rbac.py`.

IO/datasets:

- `nirs4all-datasets@ac455f32` is the dataset checkout; clean but
  ahead/behind origin.
- `_worktrees/INT-io@eae8263` is the authoritative IO integration checkout,
  not raw `nirs4all-io@e52eecd`.
- Gap: datasets' `NirsDataset.to_dataset_package()` expects the MVP IO Python
  surface, while the public pyo3 binding currently exposes only
  `assembled`/`spectrodataset` targets.
- Recommended future slice: add a bounded `to_io_spec()` adapter in the IO
  Python binding and add an explicit datasets guard when `to_dataset_package`
  is absent.

## Risks

- The tools slice does not claim `.n4a`, DuckDB, or full legacy `runs/` YAML
  semantic conversion.
- The cluster and IO/datasets findings are audit outputs only; no code was
  integrated for those lanes in W3I.
- Release-lock remote reachability remains unresolved from W3G/W3H: six locked
  pins still need protected remote refs or a coordinated release decision.
