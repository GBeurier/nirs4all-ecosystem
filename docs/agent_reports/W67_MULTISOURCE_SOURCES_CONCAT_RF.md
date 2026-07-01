# W67 Multi-Source Sources Concat RF

## Status

Implemented native parity for `multi_source_sources_concat_then_rf` and removed its fallback allowlist entry.

## Finding

The native early-fusion path was not enough because legacy does two distinct things:

1. Applies the top-level SNV independently to each source.
2. Executes `{"merge": {"sources": "concat"}}` by storing the concatenated source matrix back into source 0 while leaving sources 1..N present. Downstream legacy materialization with `concat_source=True` therefore sees `[merged_source0, source1, source2, ...]`, not only the merged matrix.

The residual RF drift disappeared only after reproducing that storage-layout boundary.

## Implementation

- Added detection for the narrow native contract: multi-source, all sources selected, stateless pre-merge X transforms only, then splitter plus one model.
- Added source-concat model metadata carrying the source layout and per-source preprocessing chain.
- Reused the node runner source-concat wrapper and added a top-level merge mode that preserves legacy non-zero sources after replacing source 0 with the merged block.
- Removed `multi_source_sources_concat_then_rf` from `EXPECTED_FALLBACK`.

## Validation

- `pytest -k 'multi_source_sources_concat_then_rf'`: passed.
- Requested selector `pytest -k 'multi_source_sources_concat_then_rf or native_fallback_boundary or coverage_meter'`: passed, 88 passed / 94 deselected.
- `py_compile` on touched DagML files: passed.
- `ruff check` on touched DagML/parity files: passed.

Note: the first requested selector run exposed an unrelated `rep_to_sources_basic` failure in `envelope._source_layout` when a reshaped repetition source had no headers. A concurrent/unrelated workspace edit changed that path to tolerate missing headers; the selector passed after that fix was present.
