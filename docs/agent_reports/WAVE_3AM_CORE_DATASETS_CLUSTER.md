# Wave 3AM - Core Grouped Split, Datasets Privacy, Cluster Attestation

Date: 2026-07-02

## Scope

This batch integrated three independent lanes from the current Codex-only
refactoring run:

- Lane B/C: `nirs4all` dag-ml bridge parity for public grouped split syntax.
- Lane G: `nirs4all-datasets` anonymized-tier IO-spec privacy guard coverage.
- Lane I: `nirs4all-cluster` server-side scheduler-shape attestation.

Full Python-reference parity was intentionally deferred. The changes are focused
contract fixes with targeted tests; none touches `nirs4all-drafts` or
`nirs4all-lab`.

## Agent Board

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Ramanujan the 2nd | `nirs4all` grouped split audit | done | Found the real gap: public `{"split": ..., "group_by": ...}` was not preserved by the dag-ml bridge. |
| Bohr the 2nd | `nirs4all` first review | NO-GO | Identified missing train context, augmentation misalignment, and dict-split detector gaps. |
| Coordinator | `_worktrees/INT-nirs4all` implementation | integrated | Commit `f3005903` (`fix(dagml): preserve explicit grouped split steps`). |
| Turing the 2nd | `nirs4all` re-review | GO | Confirmed blockers fixed; noted residual lack of full end-to-end dag-ml run for grouped split. |
| Aquinas the 2nd | `nirs4all-datasets` implementation | integrated | Commit `d72e0be6` (`test(privacy): cover anonymized io spec guard`). |
| Einstein the 2nd | `nirs4all-datasets` review | GO | Confirmed the test exercises the existing privacy guard without weakening public-tier behavior. |
| Arendt the 2nd | `nirs4all-cluster` implementation | integrated | Commit `ed5fee5` (`fix(scheduler): attest inferred job shape`). |
| Carson the 2nd | `nirs4all-cluster` review | GO | Confirmed server ignores forged client scheduler shape and keeps RBAC provenance coherent. |

## Integrated Changes

### `nirs4all`

- Added internal `DagMlSplitStep` to carry public split dict metadata through
  dag-ml lowering:
  - `group_by`;
  - legacy `group`;
  - `ignore_repetition`;
  - `group_required`;
  - `aggregation`;
  - `y_aggregation`.
- Resolved explicit split groups through the same train-only context used by
  the Python reference controller.
- Aligned resolved groups against base train samples, not all stored rows, so
  existing augmented children no longer break group resolution.
- Passed explicit group IDs into dag-ml sample relations wherever folds are
  built from the host-side splitter.
- Made specialized dag-ml detectors and branch runners recognize public
  `{"split": ...}` steps in addition to bare splitter objects.
- Added focused unit coverage for:
  - group-aware folds and sample relations;
  - train/test connected-component isolation;
  - augmented-row alignment;
  - specialized detector routing for dict split syntax;
  - the existing fail-loud path for group-required splitters without a group
    source.

### `nirs4all-datasets`

- Added a privacy regression test proving that an anonymized tier whose
  canonical `variables.parquet` still contains unmasked variable names is
  refused by `NirsDataset(...).to_io_spec()`.
- No production code changed; the existing guard remains the source of truth.

### `nirs4all-cluster`

- Changed server job attestation so `scheduler.shape` is always inferred from
  the validated payload via `req.inferred_scheduler_contract()`.
- Added an RBAC test where the client forges `scheduler.shape="atomic"` and
  `submission.principal="admin"`; the persisted and leased job records keep
  `dag_shaped_whole_run` and server-attested `ops` provenance.

## Validation

`nirs4all` (`_worktrees/INT-nirs4all`):

- `python3.11 -m py_compile nirs4all/pipeline/dagml/steps.py nirs4all/pipeline/dagml/folds.py nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py tests/unit/pipeline/test_dagml_group_split.py`
- `ruff check nirs4all/pipeline/dagml/steps.py nirs4all/pipeline/dagml/folds.py nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py tests/unit/pipeline/test_dagml_group_split.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3.11 -m pytest tests/unit/pipeline/test_dagml_group_split.py tests/unit/data/test_group_split_validation.py tests/unit/operators/splitters/test_grouped_wrapper.py tests/integration/parity/test_compatibility_ledger.py -q -p no:cacheprovider` -> 64 passed.
- `git diff --check` -> passed.

`nirs4all-datasets`:

- `pytest -q tests/test_anon_enforcement.py -p no:cacheprovider` -> 5 passed.
- `ruff check tests/test_anon_enforcement.py` -> passed.
- Reviewer also ran `pytest -q tests/test_dataset.py -k 'to_io_spec or to_dataset_package or nirs4all_io_load'` -> 3 passed, 2 skipped.
- `git diff --check` -> passed.

`nirs4all-cluster`:

- `.venv/bin/python -m pytest tests/test_rbac.py::test_server_reinfers_attested_scheduler_shape_from_payload tests/test_rbac.py::test_dag_scheduler_contract_records_rights_and_result_provenance -q -p no:cacheprovider` -> 2 passed.
- `.venv/bin/python -m ruff check nirs4all_cluster/server/app.py tests/test_rbac.py` -> passed.
- Reviewer also ran `.venv/bin/python -m pytest tests/test_rbac.py -q` -> 24 passed.
- `git diff --check` -> passed.

## Release Surface Accounting

The release surface matrix still explicitly accounts for the required
`nirs4all` V1 surfaces:

- `nirs4all.python.oracle`: Python `nirs4all`, outside aggregation lock.
- `nirs4all.r.aggregate`: R `nirs4all`, covered by locked `lite`.
- `nirs4all.browser_wasm.aggregate`: browser/WASM `nirs4all`, covered by locked
  `lite`.
- `nirs4all.browser_wasm.methods_scoped`: methods WASM surface.
- `nirs4all.browser_wasm.datasets_scoped`: datasets WASM surface.

## Gate Policy

- Full Python-reference parity and full dag-ml/native parity were not run in
  this batch because they are long and were reserved for larger batches.
- The Python `nirs4all` library remains the oracle for grouped split parity.
- No tests were reduced, xfailed, or weakened to force green.
- No superseded Claude worktree or branch was merged blindly.

## Risks

- `nirs4all`: grouped split coverage is host-side/unit-level; an end-to-end
  dag-ml run with `{"split": GroupKFold(...), "group_by": ...}` remains a
  worthwhile larger-batch parity gate.
- `nirs4all`: legacy adjacent options `group` and `ignore_repetition` are
  transported but not newly exercised by the dag-ml-specific test.
- `nirs4all-datasets`: only targeted privacy tests were run, not the full suite.
- `nirs4all-cluster`: scheduler shape inference still uses the existing
  `_pipeline_ref_looks_dag` heuristic; this batch only removed client override
  trust.
