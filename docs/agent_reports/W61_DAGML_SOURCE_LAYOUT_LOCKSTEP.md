# W61 report - dag-ml source-layout lockstep

Summary:
Closed the lockstep gap exposed after W53. `dag-ml-data` had added the optional
`source_layout` contract to `feature_fusion_selector.v1`, but `dag-ml` still
carried the older mirror schema and fixture. W61 synchronized the dag-ml copy and
extended its validator with the same semantic source-layout checks.

Code changed:
- Updated `docs/contracts/feature_fusion_selector.schema.json` in dag-ml with
  optional `source_layout`.
- Updated `examples/fixtures/data/feature_fusion_selector_nir_chem.json` with
  source order, preprocessing output metadata, and feature-axis concat layout.
- Updated `docs/contracts/conformance_pack.v1.json` hashes/scenarios.
- Extended `scripts/validate_contracts.py` to validate source-layout order,
  per-source preprocessing outputs, feature names, and concat spans.

Files touched:
- `docs/contracts/conformance_pack.v1.json`
- `docs/contracts/feature_fusion_selector.schema.json`
- `examples/fixtures/data/feature_fusion_selector_nir_chem.json`
- `scripts/validate_contracts.py`

Commits:
- `624e143` on `refactor/W61-dagml-source-layout-lockstep`
- Integrated into `refactor/integration-dagml` before W51 as merge `d684644`

Tests run:
- `python3 -m json.tool` on the changed schema, conformance pack, and fixture.
- `python3 scripts/validate_contracts.py`
- `DAG_ML_DATA_REPO=/home/delete/nirs4all/_worktrees/INT-dmd python3 scripts/validate_contracts.py`
- `DAG_ML_REPO=/home/delete/nirs4all/_worktrees/INT-dagml python3 scripts/validate_contracts.py` from `INT-dmd`
- `python3 -m py_compile scripts/validate_contracts.py`
- `git diff --check`

Blockers:
None. The dag-ml and dag-ml-data contract mirrors validate bidirectionally after
W53 and W61 are integrated.
