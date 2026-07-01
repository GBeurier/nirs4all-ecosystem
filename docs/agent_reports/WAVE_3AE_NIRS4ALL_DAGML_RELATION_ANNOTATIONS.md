# Wave 3AE - nirs4all dag-ml relation annotations and parity harness

Date: 2026-07-01
Lane: C - Python nirs4all <-> dag-ml/native parity
Repo: `_worktrees/INT-nirs4all`
Commit: `98c33788 test(parity): preserve dagml relation annotations`

## Scope

- Preserve dag-ml relation `metadata` / `tags` through the nirs4all envelope bridge when the installed `dag_ml_data` wheel exposes only the JSON builder or drops annotations from normalized `coordinator_relations.records`.
- Keep public examples smoke tests pinned to the current worktree, not an unrelated installed `nirs4all`.
- Update dataplane fold validation tests to the current public `dag_ml_data` JSON API.
- Keep U03 classification public-example refusal strict across environments where optional XGBoost is or is not installed.

## Files changed

- `nirs4all/pipeline/dagml/envelope.py`
- `tests/integration/parity/test_conformance_examples_smoke.py`
- `tests/integration/parity/test_dagml_dataplane.py`

## Agent reports

- Godel the 2nd: fixed examples subprocess import root. The smoke subprocess runs from `examples/`, so `PYTHONPATH=...:.` could import an external installed `nirs4all`. Added `_PROJECT_ROOT` to subprocess `PYTHONPATH`. Targeted examples test: 2 passed.
- Hubble the 2nd: updated fold relation validation tests from removed typed API names to `validate_fold_set_against_sample_relations_json(...)`; kept the negative OOF assertion strict via `expected exactly once`. Targeted dataplane tests: 2 passed; ruff passed.
- Noether the 2nd: restored relation annotations into coordinator records by observation id for fan-out/tag bridge visibility. Targeted runner tests passed; ruff/mypy passed.
- Darwin the 2nd: read-only review GO. Confirmed annotation restoration matches source dag-ml-data contract, examples `PYTHONPATH` is local to the subprocess, and JSON validator use is an API update. Requested direct metadata/tags coverage.
- Confucius the 2nd: final read-only review GO. Confirmed U03 `marker_sets` are strict, direct metadata/tags test covers the risk, and merge-only annotation behavior preserves existing record fields. Residual risk noted: if the same metadata key exists in both normalized record and source relation, source relation wins.

## Tests and gates

Pre-full targeted reproduction:

- Initial targeted rerun reproduced six failures: two examples smoke failures from wrong import root, two runner metadata/tag failures from missing coordinator annotations, two dataplane API-name failures.
- After agent fixes, targeted six-test rerun passed:
  - `test_example_runs_on_engine[U01_hello_world-dag-ml]`
  - `test_example_runs_on_engine[U01_preprocessing_basics-dag-ml]`
  - `test_public_run_engine_dagml_tag_round_trip`
  - `test_public_run_engine_dagml_separation_branch_by_metadata`
  - `test_fold_set_requires_an_oof_partition`
  - `test_augmented_fold_set_passes_origin_boundary`
- `ruff check nirs4all/pipeline/dagml/envelope.py tests/integration/parity/test_conformance_examples_smoke.py tests/integration/parity/test_dagml_dataplane.py tests/integration/parity/test_dagml_cli_runner.py`: passed.
- `py_compile` on changed Python files: passed.
- `git diff --check`: passed.
- `coverage_meter --check`: `fallback=0, target=0`.
- Collect before the extra direct test: `635/848` selected.

Full parity batch:

- Command:
  `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python:. PATH=/home/delete/nirs4all/dag-ml/target/release:$PATH /home/delete/miniconda3/bin/python -m pytest tests/integration/parity/ -m parity -p no:cacheprovider --tb=short -ra`
- Result before final ledger/test delta:
  `1 failed, 607 passed, 16 skipped, 213 deselected, 11 xfailed, 104 warnings in 1643.75s`
- The only failure was `test_example_runs_on_engine[U03_basic_classification-dag-ml]`. Root cause: optional XGBoost is installed in this environment, so the public example appends a second top-level model and dag-ml correctly refuses the multi-model shape before the older ledgered ShuffleSplit refusal.
- The previously failing runner and dataplane tests passed inside the full run:
  - `test_public_run_engine_dagml_tag_round_trip`: passed.
  - `test_public_run_engine_dagml_separation_branch_by_metadata`: passed.
  - `test_fold_set_requires_an_oof_partition`: passed.
  - `test_augmented_fold_set_passes_origin_boundary`: passed.

Post-full targeted delta:

- Added U03 strict `marker_sets` alternatives for the two legitimate refusal frontiers: optional second top-level model, or remaining ShuffleSplit route refusal.
- Added `test_envelope_preserves_relation_metadata_and_tags`.
- Targeted seven-test rerun passed:
  - refusal ledger + U03 dag-ml example
  - direct metadata/tags envelope test
  - fold OOF tests
  - tag round-trip and metadata separation branch runners
- After merge-only helper adjustment, targeted three-test rerun passed:
  - direct metadata/tags envelope test
  - tag round-trip runner
  - metadata separation branch runner
- Final targeted seven-test rerun passed.
- `ruff`, `py_compile`, `git diff --check`: passed.
- `coverage_meter --check`: `fallback=0, target=0`.
- Collect after the new direct test: `636/849` selected.
- `python3 scripts/n4a_release_surface_matrix.py validate`: passed.
- Surface matrix report still lists the required V1 public surfaces:
  - `nirs4all.python.oracle`
  - `nirs4all.r.aggregate`
  - `nirs4all.browser_wasm.aggregate`
- `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-ws validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`: passed.

The full parity suite was not rerun after the final ledger/direct-test delta because the final changes were a strict harness ledger update plus targeted dataplane coverage, and the user explicitly asked to avoid repeated full parity runs except after big batches.

## Decisions

- No skip, xfail, fallback reduction, or legacy fallback was added to obtain green tests.
- `metadata`/`tags` restoration is bridge compatibility with the current dag-ml-data source contract: source `SampleRelation` annotations are expected to be visible on `CoordinatorRelation` for native fan-out and branch-view filtering.
- The helper now merges with any annotations already present in normalized coordinator records and deduplicates tags; source relation values win on same-key metadata conflicts because source relations are the host-owned authority.
- U03 public example remains an explicit dag-ml refusal, not a silent pass. The ledger now models both environment-dependent frontiers strictly.
- `nirs4all` Python repo is not a member of `aggregation-manifest.n4a.json` component pins; no `aggregation-lock.n4a.lock.json` refresh is required for commit `98c33788`.
- Release-lock validation must use the reviewed symlink workspace `/tmp/n4a-lock-ws`; validating against the raw sibling workspace reads superseded non-integration branches for `dag-ml`, `dag-ml-data`, and `nirs4all-io`.

## Risks

- Release-lock remote fetchability remains unchanged from prior reports: unpushed local pins in other lock members are still not fetchable until pushed/tagged.
- If a future `dag_ml_data` wheel starts emitting coordinator annotations plus computed additional metadata under the same key names, source relation values currently win. This is deliberate but should be revisited when the wheel is refreshed.
- Full parity should be rerun in the next large batch after more code changes; current post-full delta is covered by targeted tests only.
