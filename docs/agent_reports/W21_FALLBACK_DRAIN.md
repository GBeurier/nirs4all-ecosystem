# W21 report - B-010 fallback drain

## Summary

`EXPECTED_FALLBACK` remains at 10. I did not remove any allowlist entry because the local native proof path is blocked: a known-native case (`baseline_vertical_slice`) fails before parity with `AttributeError: module 'dag_ml_data' has no attribute 'build_coordinator_data_plan_envelope'` while the installed module suggests `build_coordinator_data_plan_envelope_json`.

The code change makes the remaining fallback boundary explicit and catchable: after all supported native composition detectors have first refusal, raw `branch`, raw `merge`, and modifier-bearing `preprocessing` shapes now raise `DagMlUnsupported` via `run_backend._unsupported_fallback_reason` instead of falling through to the generic concrete route and crashing later during native setup.

## Files changed

- `nirs4all/pipeline/dagml/run_backend.py`
  - Added `_unsupported_fallback_reason`.
  - Routed unmatched raw fallback shapes to `DagMlUnsupported` before sample augmentation, exclude/tag resolution, generator dispatch, or generic concrete dispatch.
- `tests/integration/parity/coverage_meter.py`
  - Updated the static basis text for expected fallback rows to "explicit dag-ml coverage boundary".
- `tests/integration/parity/test_conformance_dual_engine.py`
  - Updated `EXPECTED_FALLBACK` comments to point at the current code-backed boundary and remaining blockers.

## Blocker map for remaining expected fallback

All ten remaining cases are still code-backed fallbacks. The guard is `run_backend._unsupported_fallback_reason`.

| case | blocker |
|---|---|
| `branch_dup_three_way_merge_predictions` | Named-dict duplication branch plus `merge: predictions` and downstream Ridge does not match the native list-of-lists/default-stacking detector. Needs deterministic named-branch normalization plus prediction-OOF stacking parity. |
| `branch_dup_two_way_merge_features` | Named-dict branch with model-less preprocessing branches and `merge: features`; native branch paths currently fuse/stack predictions, not fold-local transformed feature blocks. |
| `branch_dup_named_with_metamodel` | Rich named branch with `concat_transform`, named `MetaModel`, non-default `StackingConfig`, and structured per-branch prediction selector. Needs native support for those merge/model options before parity can be claimed. |
| `branch_dup_merge_all` | Named-dict branch with `merge: all`; no native contract for combined feature+prediction merge output or downstream model parity. |
| `multi_source_by_source_branch_shared_preproc` | `by_source` + concat-feature reassembly + one downstream model. Existing native by-source path is late prediction fusion; it does not reproduce legacy's 51-row branch prediction bookkeeping / concat-feature boundary. |
| `multi_source_by_source_branch_distinct_preproc` | Same concat-feature blocker as shared case, plus per-source dict body and stateful per-source preprocessing (`MSC`) that the shared-body native detector does not cover. |
| `multi_source_per_source_models_stacking` | `by_source` per-source models + `merge: predictions` stacking. No native by-source stacking path; legacy refit is also broken for this shape, so there is no clean legacy final-row oracle yet. |
| `multi_source_sources_concat_then_rf` | `{'merge': {'sources': 'concat'}}` source merge boundary. Native early-fusion applies preprocessing on concatenated blocks, while legacy applies per-source preprocessing and includes a storage round-trip that shifts the fixed-seed RF. |
| `preprocessing_fit_on_all` | Modifier-bearing `{'preprocessing': ..., 'fit_on_all': True}` requires train+val+test fit scope; native X-chain only represents fold-local/default fit scope. |
| `preprocessing_force_layout_2d` | Modifier-bearing `{'preprocessing': ..., 'force_layout': '2d'}` requires an explicit layout contract not represented by the native X-chain. |

## Tests run

- `pytest -q tests/integration/parity/test_conformance_dual_engine.py::test_native_fallback_boundary --tb=short -k "branch_dup or multi_source_by_source_branch or multi_source_per_source_models_stacking or multi_source_sources_concat_then_rf or preprocessing_fit_on_all or preprocessing_force_layout_2d"`
  Result: 10 passed, 77 deselected.
- `pytest -q tests/integration/parity/test_conformance_dual_engine.py::test_dual_engine_conformance --tb=short -k "branch_dup or multi_source_by_source_branch or multi_source_per_source_models_stacking or multi_source_sources_concat_then_rf or preprocessing_fit_on_all or preprocessing_force_layout_2d"`
  Result: 10 passed, 85 deselected, 2 warnings from stacking reconstructor imputation.
- `pytest -q tests/integration/parity/test_native_fallback_boundary.py tests/integration/parity/test_compatibility_ledger.py --tb=short`
  Result: 14 passed.
- `/home/delete/miniconda3/bin/python3 -m tests.integration.parity.coverage_meter --check`
  Result: `coverage_meter OK (fallback=10, target=0)`.
- `/home/delete/miniconda3/bin/python3 -m py_compile nirs4all/pipeline/dagml/run_backend.py tests/integration/parity/coverage_meter.py tests/integration/parity/test_conformance_dual_engine.py tests/integration/parity/test_native_fallback_boundary.py`
  Result: passed.
- `ruff check nirs4all/pipeline/dagml/run_backend.py tests/integration/parity/coverage_meter.py tests/integration/parity/test_conformance_dual_engine.py tests/integration/parity/test_native_fallback_boundary.py`
  Result: passed.

## Blocked tests / proof gaps

- `pytest -q tests/integration/parity/test_conformance_dual_engine.py::test_native_fallback_boundary --tb=short -k "baseline_vertical_slice"` failed before native parity proof with `dag_ml_data.build_coordinator_data_plan_envelope` missing from the installed `dag_ml_data` module. This prevents safely draining any fallback entry in this environment.

## Commits

- `b8205343 fix(dagml): pin unsupported fallback boundary`

## Next action

Fix or align the local `dag_ml_data` API (`build_coordinator_data_plan_envelope` vs `build_coordinator_data_plan_envelope_json`), then rerun native parity for candidate fallback drains. The first candidates to re-evaluate are not the modifier-bearing preprocessing cases; they need native contracts. The only plausible near-term drain candidates are branch/by-source cases after dedicated native feature/stacking contracts are implemented and proven by dual-engine parity.
