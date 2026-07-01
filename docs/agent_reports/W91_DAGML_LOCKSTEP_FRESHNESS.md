# W91 - dag-ml / dag-ml-data Lockstep Freshness Gate

Date: 2026-07-01

## Scope

- Created `dag-ml` worktree `_worktrees/W91-dagml-lockstep` on `refactor/W91-lockstep-freshness` from `refactor/integration-dagml`.
- Created `dag-ml-data` worktree `_worktrees/W91-dagml-data-lockstep` on `refactor/W91-lockstep-freshness` from `refactor/L20-lockstep`, then fast-forwarded to existing `refactor/integration-dmd`.
- Left the dirty main `dag-ml-data` checkout artifact `crates/dag-ml-data-py/python/dag_ml_data/_dag_ml_data.abi3.so` untouched.
- Left unrelated dirty `nirs4all-ecosystem` cutover/script/test files untouched.

## Contract Freshness Result

Initial paired validation exposed real drift:

- `dag-ml` expected `dag-ml-data/docs/contracts/representation_registry.v1.json`, but the W91 data branch base did not have it.
- `dag-ml-data` reported `feature_fusion_selector.schema.json` drift beyond repository-specific `$id`.

Resolution used the intended existing integration work, not a new schema vocabulary:

- Fast-forwarded W91 `dag-ml-data` to `818616e` (`refactor/integration-dmd`), which already merged:
  - `4f858c3` / `4003480`: published representation registry generated from existing `builtin_models.rs`.
  - `2a850a5`: model-input/data-requirements validation against the published registry.
  - `51aec52`: by-source feature-layout contract and conformance-pack digest update.
- Re-ran both paired validators successfully.
- Verified the surfaced contracts remain the existing DAG-ML/DAG-ML-DATA artifacts (`controller_manifest`, `node_task`, `node_result`, `model_input_spec`, `data_plan`, representation registry, feature-fusion selector, conformance pack), with no parallel CAP/CTRL/REL vocabulary introduced by W91.

## Changed Files

No manual code edits were made in `dag-ml`.

The W91 `dag-ml-data` branch now includes the existing integration commits that update:

- `docs/contracts/feature_fusion_selector.schema.json`
- `docs/contracts/conformance_pack.v1.json`
- `docs/contracts/representation_registry.v1.json`
- `examples/fixtures/data/model_input_spec_tabular_regressor.json`
- `examples/fixtures/oof_campaign/feature_fusion_selector_nir_chem.json`
- `scripts/validate_contracts.py`
- focused data-side Rust/C ABI support files from the integrated source-layout and registry work.

This report is the only W91 ecosystem file added:

- `docs/agent_reports/W91_DAGML_LOCKSTEP_FRESHNESS.md`

## Commits

- `dag-ml`: no new W91 commit; branch head `618ffb2` (`refactor/integration-dagml`).
- `dag-ml-data`: no new manual W91 commit; W91 branch fast-forwarded to `818616e` (`refactor/integration-dmd`), containing the existing lockstep fixes above.
- `nirs4all-ecosystem`: report-only commit adding this file.

## Verification

Passed:

- `DAG_ML_DATA_REPO=/home/delete/nirs4all/_worktrees/W91-dagml-data-lockstep python3 scripts/validate_contracts.py`
- `DAG_ML_REPO=/home/delete/nirs4all/_worktrees/W91-dagml-lockstep python3 scripts/validate_contracts.py`
- `python3.11 scripts/validate_abi_snapshot.py` in `dag-ml`
- `python3.11 scripts/validate_abi_snapshot.py` in `dag-ml-data`
- `cargo test -p dag-ml-data-core representation_registry`
- `cargo test -p dag-ml-data-core source_layout`
- `cargo test -p dag-ml-data-capi exports_coordinator_feature_fusion_arrow_over_abi`
- `cargo run -p dag-ml-data-cli -- validate-model-input --model-input examples/fixtures/data/model_input_spec_tabular_regressor.json`
- `cargo test -p dag-ml-core model_input_spec`
- `cargo test -p dag-ml-core published_node_task`
- `cargo test -p dag-ml-capi validates_model_input_and_data_plan_contracts_over_abi`
- `cargo test -p dag-ml-capi validates_controller_manifests_over_abi`
- `cargo test -p dag-ml-capi validates_node_result_against_task_over_abi`
- `cargo fmt --all --check` in both worktrees
- `cargo clippy --workspace --all-targets -- -D warnings` in `dag-ml-data`
- `cargo test --workspace` in `dag-ml-data`
- `cargo run -p dag-ml-data-cli -- fingerprint-schema examples/minimal_schema.json`
- `git diff --check` in both worktrees

Failures observed and resolved:

- Initial paired contract validation failed before the `dag-ml-data` fast-forward because the data branch was behind the existing integration contracts.
- `python3 scripts/validate_abi_snapshot.py` failed under Python 3.10 due missing stdlib `tomllib`; reran successfully with Python 3.11.
- First `dag-ml-data-cli validate-model-input` run used a positional path and failed usage validation; reran successfully with `--model-input`.

## Blockers And Follow-Up

No W91 blocker remains. Coordinator integration should ensure the W91 `dag-ml-data` branch/head used for final Wave 2K accounting is `818616e` or newer; `dag-ml` did not need a new commit for this check.
