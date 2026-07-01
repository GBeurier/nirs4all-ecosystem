# W53 report - dag-ml-data source layout contract

Summary:
Defined an explicit data-side by-source feature layout contract in
`dag-ml-data`. The contract is carried as optional `source_layout` metadata on
the existing `feature_fusion_selector.v1` surface, so existing consumers remain
compatible while by-source fallbacks can validate source order, per-source
preprocessing outputs and feature-axis concat spans.

Code changed:
- Added `FeatureFusionSourceLayout`, `SourceFeatureLayoutBlock`,
  `SourcePreprocessingOutput` and `SourceConcatLayout` Rust contracts in
  `dag-ml-data-core::fusion`.
- Added validation against concrete `SourceFeatureBlock`s for source order,
  source block width, preprocessing output feature-set/representation,
  optional feature names and concat feature spans.
- Wired optional `source_layout` validation into provider-backed fusion and
  the direct C ABI feature-fusion helper before existing fusion execution.
- Extended `feature_fusion_selector.v1` schema, canonical fixture,
  conformance pack digests/scenario metadata, and contract docs.
- Extended `scripts/validate_contracts.py` with source-layout semantic checks
  and a `--local-only` mode for validating local artifacts when an adjacent
  sibling checkout is incomplete.

Files touched in dag-ml-data:
- `crates/dag-ml-data-core/src/fusion.rs`
- `crates/dag-ml-data-provider/src/lib.rs`
- `crates/dag-ml-data-capi/src/lib.rs`
- `docs/ABI.md`
- `docs/contracts/README.md`
- `docs/contracts/feature_fusion_selector.schema.json`
- `docs/contracts/conformance_pack.v1.json`
- `examples/fixtures/oof_campaign/feature_fusion_selector_nir_chem.json`
- `scripts/validate_contracts.py`

Tests run:
- `cargo fmt --all --check`
- `cargo test -p dag-ml-data-core fusion -- --nocapture`
- `cargo test -p dag-ml-data-core fusion::tests::source_layout -- --nocapture`
- `cargo test -p dag-ml-data-provider`
- `cargo test -p dag-ml-data-capi exports_coordinator_feature_fusion_arrow_over_abi -- --nocapture`
- `cargo test -p dag-ml-data-capi inmemory_provider_feature_collation_uses_provider_buffers_and_fusion_selector -- --nocapture`
- `cargo test -p dag-ml-data-capi feature_fusion -- --nocapture`
- `cargo clippy -p dag-ml-data-core -p dag-ml-data-provider -p dag-ml-data-capi --all-targets -- -D warnings`
- `python3 -m json.tool docs/contracts/feature_fusion_selector.schema.json >/dev/null`
- `python3 -m json.tool docs/contracts/conformance_pack.v1.json >/dev/null`
- `python3 -m json.tool examples/fixtures/oof_campaign/feature_fusion_selector_nir_chem.json >/dev/null`
- `python3 scripts/validate_contracts.py --local-only`

Artifacts:
- Regenerated the `feature_fusion_selector.v1` normalized SHA-256 and
  `feature_fusion_selector_nir_chem.v1` canonical JSON SHA-256 in
  `conformance_pack.v1.json`.

Blockers:
- Full default `python3 scripts/validate_contracts.py` cannot complete in this
  workspace because the adjacent sibling checkout
  `/home/delete/nirs4all/_worktrees/dag-ml` is incomplete for the current shared
  artifact set and is missing `docs/contracts/representation_registry.v1.json`.
  Local-only validation passes.
