# W69 Source Layout Contract Audit

Date: 2026-07-01

## Scope

Audited the missing nirs4all source-layout contract needed by W54/W65/W67 against:

- `docs/agent_reports/WAVE_2H_CONTRACT_NOTES.md`
- nirs4all integration baseline: `_worktrees/INT-nirs4all`
- dag-ml-data integration baseline: `_worktrees/INT-dmd`

Changes were made only in the nirs4all fork workspace and this report.

## Conclusion

`build_envelope()` should expose `plan.source_layout` for multi-source envelopes. The integration nirs4all baseline already emits native plan sources `src0..srcK`, joins them to `feature_block_set`, and marks relations at sample grain with `source_id=None`, but it does not expose the layout map W54/W65 need to lower legacy by-source dict bodies without guessing.

The required nirs4all bridge shape is:

```json
{
  "kind": "by_source_concat",
  "source_order": ["source_0", "source_1", "..."],
  "source_ids": ["src0", "src1", "..."],
  "blocks": [
    {
      "source_name": "source_0",
      "source_id": "src0",
      "source_index": 0,
      "preprocessing_output": {
        "feature_set_id": "x:src0",
        "representation_id": "tabular_numeric",
        "adapter_id": "preprocess:src0",
        "fit_scope": "fold_train"
      },
      "column_start": 0,
      "column_count": 123,
      "feature_names": ["..."]
    }
  ],
  "per_source_preprocessing_outputs": {
    "source_0": {
      "source_id": "src0",
      "source_index": 0,
      "feature_set_id": "x:src0",
      "representation_id": "tabular_numeric",
      "adapter_id": "preprocess:src0",
      "fit_scope": "fold_train"
    }
  },
  "concat_layout": {
    "strategy": "concat",
    "axis": "feature",
    "source_order": ["source_0", "source_1", "..."],
    "source_ids": ["src0", "src1", "..."],
    "total_column_count": 369,
    "output_source_index": 0,
    "preserves_storage_roundtrip": true
  },
  "concat": {
    "feature_set_id": "x",
    "representation_id": "tabular_numeric",
    "axis": "feature",
    "total_column_count": 369,
    "preserve_source_order": true,
    "namespace_columns": true
  }
}
```

`source_order` is intentionally legacy-facing (`source_0`, `source_1`, ...) because W65 must match the keys in legacy `{"branch": {"by_source": true, "steps": {...}}}` dict bodies. `source_ids` is the native data-plan order (`src0`, `src1`, ...). The two lists are positional peers.

## dag-ml-data Compatibility Note

The dag-ml-data integration baseline documents and validates `feature_fusion_selector.source_layout` with `kind`, authoritative `source_order`, per-source `blocks`, and `concat`. That strict selector schema uses `source_order` as source ids matching each block's `source_id`, has `additionalProperties: false`, and validates the layout against concrete feature blocks.

The nirs4all `plan.source_layout` added here is a bridge contract, not a verbatim `feature_fusion_selector` payload. It keeps dag-ml-data-compatible concepts (`kind`, `blocks`, contiguous feature-axis spans, `concat`) while adding W54/W65 bridge fields (`source_ids`, `source_name`, `source_index`, `per_source_preprocessing_outputs`, `concat_layout`). If a future path exports it as a dag-ml-data selector, it should adapt the bridge layout into the strict selector shape rather than pass it through unchanged.

Adding it under `plan` is low risk for the current envelope path: the shared coordinator envelope schema allows additional plan properties, and Rust `DataPlan` deserialization ignores unknown fields for the canonical plan fingerprint. The added metadata is therefore visible to nirs4all consumers without changing the dag-ml-data fingerprinted plan contract.

## Implementation

Implemented in nirs4all only:

- Added `source_order(dataset)` for legacy by-source key order.
- Added `_source_layout(dataset, sources)` to build the explicit multi-source layout.
- `build_envelope()` now attaches `out["plan"]["source_layout"]` only when `len(source_ids(dataset)) > 1`.
- Restored W54 probes as normal passing tests in `test_dagml_cli_runner.py`, covering:
  - `source_order`, `source_ids`, `blocks`, and `per_source_preprocessing_outputs`
  - `concat_layout` strategy/order/output placement/storage-roundtrip flag
  - `concat` feature-axis span metadata

Single-source envelopes remain unchanged and do not get `source_layout`.

## W65/W67 Readiness

W65 can proceed without guessing the by-source dict mapping: it should consume `plan.source_layout.source_order` and `plan.source_layout.source_ids` positionally, and reject dict bodies whose keys do not exactly match `source_order`.

Source layout alone is insufficient for W67 fixed-seed RF storage-roundtrip parity. It supplies the required boundary metadata, but W67 still needs the runner to preserve the explicit `{"merge": {"sources": "concat"}}` storage semantics: per-source preprocessing before concat, the merged output placement, and any legacy retained-source behavior after the merge. Without those execution semantics, ordinary early fusion can still feed a different matrix/order into RF.

## Guardrails

- Did not update `EXPECTED_FALLBACK`.
- Did not update `docs/compatibility.json`.
- Did not change dag-ml-data.
- Did not push.

Note: the local nirs4all fork already contained broader uncommitted W65/W67 edits when W69 started, including an `EXPECTED_FALLBACK`/compatibility change. Those are outside this W69 report and should not be attributed to this source-layout commit unless their targeted parity cases are independently green.

## Validation

- `python -m py_compile ...` could not run because `python` is not on PATH in this shell.
- `.venv/bin/python -m py_compile nirs4all/pipeline/dagml/envelope.py nirs4all/pipeline/dagml/node_runner.py nirs4all/pipeline/dagml/resolver.py nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py` -> passed.
- `.venv/bin/python -m pytest tests/integration/parity/test_dagml_cli_runner.py -k 'w54_contract or multi_source_emission_emits_feature_block_set' -q` -> 3 passed.
- `.venv/bin/python -m pytest tests/integration/parity/test_conformance_dual_engine.py::test_dual_engine_conformance -k 'multi_source_by_source_branch_distinct_preproc or multi_source_sources_concat_then_rf' -q` -> 2 passed.

The targeted conformance pass used the current dirty fork workspace, which already contained broader W65/W67 runner edits before W69 started. It confirms those cases are green in that workspace, but source layout itself remains only the contract prerequisite for W67's storage-roundtrip behavior.
