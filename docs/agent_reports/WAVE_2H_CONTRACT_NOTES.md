# Wave 2H Contract Notes

Date: 2026-07-01

These notes were collected by the coordinator while W62-W67 were running. They are support context for
integration and for the queued W68/W69 agents.

## Stacking OOF/REFIT

`dag-ml` already owns the runtime contract:

- Metadata key: `stacking_oof_refit_contract`.
- Shape: `{"policy": "require_full_coverage" | "cv_only" | "skip_refit_on_incomplete_oof"}`.
- Runtime entry point: `dag-ml/crates/dag-ml-core/src/runtime/oof.rs::validate_refit_oof_edge`.
- Semantic validator: `dag-ml/crates/dag-ml-core/src/oof.rs::validate_stacking_oof_refit_contract`.

Implications for nirs4all:

- Simple full-coverage duplication stacking should not need a special policy; default
  `require_full_coverage` is correct if base validation OOF covers the complete train/refit sample
  universe.
- Legacy CV-only stacking behavior should be encoded explicitly as `cv_only`, not approximated by
  producing native refit rows that legacy never emits.
- Incomplete-but-valid OOF coverage should use `skip_refit_on_incomplete_oof` only when it matches a
  documented legacy coverage/drop policy.
- Invalid OOF remains invalid under every policy.

Observed nirs4all gap:

- `_run_stacking_branch()` currently emits only `metadata.controller_id` for the meta node; it does not
  emit `stacking_oof_refit_contract`.

## Named Duplication Branches

`nirs4all/pipeline/dagml/detect.py` has a split-brain implementation:

- `_duplication_branch_bodies()` already normalizes both list syntax and named-dict duplication syntax.
- `_detect_stacking_branch()` later bypasses that helper and requires `branch_step["branch"]` to be a
  raw list-of-lists.

Likely consequence:

- `branch_dup_three_way_merge_predictions` is rejected even though its shape is simple stacking, because
  its branch is a named dict (`snv_plsr`, `msc_rf`, `fd_gbr`).

Important boundary:

- `branch_dup_named_with_metamodel` is not just the same bug. It also carries a non-default
  `MetaModel` coverage config and a structured per-branch `merge.predictions` selector. It must not be
  lowered as collect-all stacking unless selector/coverage semantics are proven equivalent.

## Source Layout

`dag-ml-data` already documents and validates a source-layout contract in its feature-fusion selector:

- `source_layout.kind = "by_source_concat"`.
- Authoritative `source_order`.
- Per-source blocks with preprocessing output representation.
- `concat` span/layout preserving source order.

Current nirs4all state:

- `build_envelope()` emits multi-source schema sources `src0`, `src1`, `src2` and a join to
  `feature_block_set`.
- `source_ids(dataset)` returns native ids `src0..srcK`.
- W54 probes in `tests/integration/parity/test_dagml_cli_runner.py` still xfail because
  `envelope["plan"]` has no `source_layout`.
- Existing runtime support already has:
  - `_SourceConcatEstimator` applying a shared X-chain independently per source then hstacking.
  - `MaterializationResolver.resolve_source_block()` selecting one source block by index.
  - `_canonical_source_branch()` binding `metadata.source_index` to model nodes.

Likely nirs4all addition:

- Add a typed `plan.source_layout` for multi-source envelopes with legacy-facing `source_order`
  (`source_0`, `source_1`, ...), native `source_ids` (`src0`, `src1`, ...), and a concat layout.
- For W65, a per-source dict body can then be mapped deterministically from legacy keys to source
  indexes before building the model's per-source preprocessing chains.
- For W67, reproducing `{"merge": {"sources": "concat"}}` may still require preserving the explicit
  merge/storage boundary; adding layout alone may not be enough for fixed-seed RF parity.
