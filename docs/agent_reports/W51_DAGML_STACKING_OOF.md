# W51 report - dag-ml stacking OOF/refit contract

Summary:
Implemented an explicit stacking OOF/refit contract in `dag-ml` so the runtime
distinguishes full-coverage stacking that may REFIT, explicit CV-only/refit-skip
stacking with incomplete OOF, and invalid stacking with stable causes.

Commit:
- `0681cc6610f67b04bb924c031697571e65625a72` (`fix(oof): make stacking refit coverage explicit`)

Code changed:
- Added `StackingOofRefitContract`, `StackingOofRefitPolicy`,
  `StackingOofRefitDecision`, stable causes, diagnostics, and
  `validate_stacking_oof_refit_contract`.
- Reserved node metadata key `stacking_oof_refit_contract` with policies
  `require_full_coverage`, `cv_only`, and `skip_refit_on_incomplete_oof`.
- Validated malformed contract metadata during graph validation.
- Wired REFIT OOF collection so default behavior still rejects incomplete OOF
  with `cause=partial_oof_without_policy`; explicit `cv_only` or
  `skip_refit_on_incomplete_oof` skips the stacking node instead of consuming
  incomplete OOF.
- Kept malformed OOF invalid under skip policy and averaged resampled repeated
  validation rows into one REFIT meta-feature row per sample.
- Documented the contract in coordinator and contract docs.

Files changed in dag-ml:
- `crates/dag-ml-core/src/graph.rs`
- `crates/dag-ml-core/src/oof.rs`
- `crates/dag-ml-core/src/runtime/dataview.rs`
- `crates/dag-ml-core/src/runtime/mod.rs`
- `crates/dag-ml-core/src/runtime/oof.rs`
- `crates/dag-ml-core/src/runtime/scheduler.rs`
- `crates/dag-ml-core/src/runtime/tests.rs`
- `docs/COORDINATOR_SPEC.md`
- `docs/OOF_FIXTURES.md`
- `docs/contracts/README.md`

Tests run:
- `cargo test -p dag-ml-core oof::tests::stacking_oof_refit_contract -- --nocapture`
- `cargo test -p dag-ml-core runtime::tests::requires_oof_prediction_edge_refit -- --nocapture`
- `cargo fmt --all --check`
- `cargo test -p dag-ml-core`
- `cargo clippy --workspace --all-targets -- -D warnings`
- `cargo run -p dag-ml-cli -- validate-graph examples/minimal_graph.json`
- `python3 scripts/check_so_freshness.py` failed, see blocker below.

Conformance:
No conformance pack, schema artifact, or fixture digest was changed. The
GraphSpec schema already permits node metadata; W51 only reserves and validates
one metadata key semantically in Rust, so cross-repo digest validation was not
required.

Blockers:
- `python3 scripts/check_so_freshness.py` reports the tracked Python extension
  binary `crates/dag-ml-py/python/dag_ml/_dag_ml.abi3.so` is stale relative to
  previously committed Rust sources (`controller_adapter.rs`, `data.rs`,
  `lib.rs`, `plan.rs`, `runtime/merge.rs`, `runtime/tests.rs`). This predates
  the W51 changes. The documented remediation requires `maturin develop
  --release` in `crates/dag-ml-py`, but `python3 -m maturin --version` reports
  `No module named maturin` in the active environment.

Notes:
- The old AGENTS pointers `docs/TOC.md` and `docs/design/source/*` are absent in
  this worktree; the design files are present under
  `docs/design/source/_archive/` and were used for context.
