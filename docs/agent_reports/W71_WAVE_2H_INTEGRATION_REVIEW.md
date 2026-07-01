# W71 Wave 2H Integration Review

Date: 2026-07-01

Reviewer: W71

Scope reviewed:

- W62 core commit `5d41b52c` on `refactor/W62-branch-dup-three-way`
- W64 core commit `7f6aa4a3` on `refactor/W64-branch-dup-merge-all`
- W68 core commit `8ef94242` and integration cherry-pick `0aa2a674`
- W69 core commit `8eff3b57` and integration cherry-pick `362c2d79`
- W65 core commit `5e00e400`
- W67 dirty core diff in `/home/delete/nirs4all/nirs4all`
- W63 and W66 blocked reports

No core code was modified by this review.

## Findings

### P0 - Integration worktree is currently not clean

The integration worktree `/home/delete/nirs4all/_worktrees/INT-nirs4all` was no longer at the prompt's clean `316bfc69` baseline during review. It first contained W68 as `0aa2a674`, then advanced to W69 as `362c2d79`, and is now mid-conflict.

Current unresolved files:

- `docs/compatibility.json`
- `nirs4all/pipeline/dagml/detect.py`
- `nirs4all/pipeline/dagml/node_runner.py`
- `nirs4all/pipeline/dagml/run_backend.py`
- `nirs4all/pipeline/dagml/run_paths.py`
- `tests/integration/parity/test_conformance_dual_engine.py`
- `tests/integration/parity/test_dagml_cli_runner.py`

The conflicts match a W65 cherry-pick on top of W69. Do not apply additional Wave 2H patches until this is resolved or the active cherry-pick is intentionally abandoned by the integrator.

### P0 - W62 uses the wrong OOF/refit policy

W62 `5d41b52c` changes `nirs4all/pipeline/dagml/run_paths.py::_run_stacking_branch` to emit:

```python
"stacking_oof_refit_contract": {"policy": "skip_refit_on_incomplete_oof"}
```

W68 explicitly recommends `require_full_coverage` for this full-coverage duplication stacking path. A dry merge of W62 against the integration branch after W68 conflicts exactly on this metadata field.

Resolution: keep W62's named-branch detector/projection work, but resolve `_run_stacking_branch` metadata to:

```python
"stacking_oof_refit_contract": {"policy": "require_full_coverage"}
```

Do not let the W67 dirty diff's `_detect_stacking_branch` hunk reintroduce list-only detection; that would undo W62.

### P0 - W67 dirty diff is mixed with W66 blocked code

The W67 work is not staged and not committed in `/home/delete/nirs4all/nirs4all`. The dirty diff includes both the green W67 source-concat RF work and non-green W66 by-source stacking work.

Extract only these W67 pieces:

- `nirs4all/pipeline/dagml/detect.py`: `_source_concat_indices`, `_is_stateless_x_transform`, `_detect_source_concat_merge`
- `nirs4all/pipeline/dagml/run_backend.py`: imports, exports, detection, repetition guard, and dispatch for `_detect_source_concat_merge` and `_run_source_concat_merge`
- `nirs4all/pipeline/dagml/run_paths.py`: `_source_concat_layout`, `_graph_upstream_x_chain`, `_source_concat_preprocessing_metadata`, `_mark_source_concat_model_nodes`, `_run_source_concat_merge`
- `docs/compatibility.json` and `tests/integration/parity/test_conformance_dual_engine.py`: remove only `multi_source_sources_concat_then_rf`

Do not extract these W66 pieces:

- `detect.py::_detect_by_source_stacking_branch`
- `run_backend.py` imports/dispatch for `_detect_by_source_stacking_branch` and `_run_by_source_stacking_branch`
- `run_paths.py::_run_by_source_stacking_branch` and its private helper block
- Any removal of `multi_source_per_source_models_stacking` from fallback lists

### P1 - W65 is a manual port, not a clean cherry-pick

W65 `5e00e400` was based on the L17/main line, not on `refactor/integration-nirs4all`. It conflicts with the integration branch's existing shared by-source concat implementation.

The integrator must preserve the existing shared-preproc path:

- `detect.py::_detect_by_source_concat_shared_preproc`
- `run_backend.py::_run_by_source_concat_shared_preproc` dispatch
- `node_runner.py::_source_concat_x_chain` semantics, or an equivalent adapted metadata path

Then add W65's distinct-preproc path beside it:

- `detect.py::_detect_by_source_distinct_preproc_concat`
- `run_paths.py::_source_preprocessing_metadata`
- `run_paths.py::_run_by_source_distinct_preproc_concat`
- `node_runner.py::_source_concat_chains` / `_source_concat_preserve_legacy_sources`

Taking W65's side wholesale would drop the already-integrated shared-preproc behavior.

### P1 - W69 must keep the integration envelope wrapper

The original W69 commit used `dict(envelope.to_dict())` in `build_envelope()`. The integration branch uses `_build_coordinator_envelope(...)`.

The correct port is the current `362c2d79` shape in `nirs4all/pipeline/dagml/envelope.py::build_envelope`: build through `_build_coordinator_envelope(...)`, then attach `out["plan"]["source_layout"]` for multi-source datasets.

### P1 - Combined fallback ledger must be resolved manually

W62 and W64 both independently update fallback count `6 -> 5`; W65 and W67 also remove one case each. The combined Wave 2H green outcome should remove four of the original six fallbacks.

After integration, among the original Wave 2H six, only these should remain:

- W63: `branch_dup_named_with_metamodel`
- W66: `multi_source_per_source_models_stacking`

Do not keep W62/W64/W65/W67 fallbacks if their corrected patches land green. Do not remove W63 or W66.

### P2 - W64 is green but has row-projection risk

W64 `7f6aa4a3` adds native support for `branch_dup_merge_all`, but much of the public row surface is reconstructed in host code:

- `run_paths.py::_run_duplication_merge_all_branch_result`
- `run_paths.py::_run_duplication_merge_all_downstream_result`
- `run_paths.py::_combine_duplication_merge_all_rows`

This is acceptable for the targeted green case, but it should be verified after integration with W62 and the combined fallback ledger because it duplicates scoring/weighting behavior outside the generic dag-ml projection path.

## Recommended Integration Order

1. Return `/home/delete/nirs4all/_worktrees/INT-nirs4all` to a clean state or finish the current W65 conflict intentionally.
2. Keep W68 `0aa2a674` first. It establishes the correct `require_full_coverage` policy.
3. Keep W69 `362c2d79` next, preserving `_build_coordinator_envelope(...)`.
4. Integrate W62, resolving `_run_stacking_branch` to `require_full_coverage`.
5. Integrate W64, resolving ledger/test comments so both W62 and W64 removals are represented.
6. Manually port W65 beside the existing shared by-source concat implementation.
7. Extract W67 source-concat RF only after W65 is in place. Exclude all W66 by-source stacking hunks.
8. Final fallback state for the original six should be W63 and W66 only.

Minimum post-merge checks:

- `pytest tests/integration/parity/test_conformance_dual_engine.py -k 'branch_dup_three_way_merge_predictions or branch_dup_merge_all or multi_source_by_source_branch_distinct_preproc or multi_source_sources_concat_then_rf or native_fallback_boundary or coverage_meter' -q`
- `pytest tests/integration/parity/test_native_fallback_boundary.py -q`
- `python -m tests.integration.parity.coverage_meter --check`
- focused `test_dagml_cli_runner.py` detector/layout tests for stacking, duplication merge-all, source layout, by-source distinct concat, and source-concat merge

