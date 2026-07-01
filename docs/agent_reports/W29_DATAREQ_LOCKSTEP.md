# W29 report - data requirements lockstep

Summary:
Implemented the W29 data-requirements consumption slice manually with Codex after
the earlier Claude quota stop. `dag-ml` now consumes
`ControllerManifest.data_requirements` during execution-plan validation: each
`DataBinding` must target a declared `ModelInputSpec` port, use an accepted
representation, and match the frozen registry type when the representation is
known. `dag-ml-data` now validates `ModelInputSpec` values against the
published representation registry and exposes that path through
`dag-ml-data-cli validate-model-input`.

Code changed:
- `dag-ml`: added plan-time data-binding vs. controller data-requirements
  validation; tightened tabular model-input/controller-manifest fixtures to
  `tabular_numeric` / `table`; pinned the shared model-input fixture in the
  conformance pack and cross-repo contract validator.
- `dag-ml-data`: added registry-backed `ModelInputSpec` validation; added CLI
  `validate-model-input`; added the shared tabular regressor model-input
  fixture; pinned and compared it in lockstep validation.

Commits:
- `dag-ml` `_worktrees/W29-dagml-datareq`: `beef11b` -
  `feat(data): consume controller data requirements`
- `dag-ml-data` `_worktrees/W29-dmd-datareq`: `2a850a5` -
  `feat(data): validate model inputs against registry`

Tests run:
- `dag-ml`: `cargo fmt --all --check`
- `dag-ml`: `cargo test -p dag-ml-core data_requirements`
- `dag-ml`: `cargo test -p dag-ml-core build_execution_plan_rejects_binding_registered_type_outside_data_requirements`
- `dag-ml`: `cargo test -p dag-ml-core`
- `dag-ml`: `cargo clippy -p dag-ml-core -p dag-ml-cli --all-targets -- -D warnings`
- `dag-ml`: `cargo run -p dag-ml-cli -- validate-execution-plan --graph examples/minimal_graph.json --campaign examples/campaign_oof_generation.json --controllers examples/controller_manifests.json`
- `dag-ml`: `cargo run -p dag-ml-cli -- validate-graph examples/minimal_graph.json`
- `dag-ml`: `DAG_ML_DATA_REPO=/home/delete/nirs4all/_worktrees/W29-dmd-datareq python3 scripts/validate_contracts.py`
- `dag-ml-data`: `cargo fmt --all --check`
- `dag-ml-data`: `cargo test -p dag-ml-data-core model_input_spec_registry_validation`
- `dag-ml-data`: `cargo run -p dag-ml-data-cli -- validate-model-input --model-input examples/fixtures/data/model_input_spec_tabular_regressor.json`
- `dag-ml-data`: `cargo test -p dag-ml-data-core`
- `dag-ml-data`: `cargo test -p dag-ml-data-cli`
- `dag-ml-data`: `cargo clippy -p dag-ml-data-core -p dag-ml-data-cli --all-targets -- -D warnings`
- `dag-ml-data`: `cargo run -p dag-ml-data-cli -- fingerprint-schema examples/minimal_schema.json`
- `dag-ml-data`: `DAG_ML_REPO=/home/delete/nirs4all/_worktrees/W29-dagml-datareq python3 scripts/validate_contracts.py`

Tests not run and why:
- Full `cargo test --workspace` was not run in either repo; touched-crate Rust
  gates, CLI smokes, and both cross-repo contract validators passed.
- Python provider tests were not run because no Python provider/binding files
  were touched.

Blockers:
None.

Impact on blockers/locks:
`LOCK-LOCKSTEP` remains compatible. The conformance pack now explicitly
requires `model_input_spec.fixture_equivalence` alongside
`representation_registry.parity`, and both lockstep validators pass against
the assigned sibling worktrees.

Next action:
Integrate the two commits together. No push or merge was performed.

Sync doc updated: no
