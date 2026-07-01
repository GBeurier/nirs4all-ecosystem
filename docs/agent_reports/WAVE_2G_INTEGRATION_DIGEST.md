# Wave 2G integration digest

Date: 2026-07-01

Summary:
Wave 2G is integrated across the prepared integration branches. The wave closed
the native stacking export blocker, made dag-ml stacking OOF/refit policy
explicit, added the shared source-layout contract, strengthened Studio/Web
runtime gates, added provider/cluster V1 service contracts, and advanced tools
native-results migration preview. The Python reference fallback meter remains
the main hard cutover blocker at `fallback=6`.

Integrated branches:
- `dag-ml/refactor/integration-dagml`
  - `d684644` merged W61 source-layout contract mirror.
  - `ab98b78` merged W51 stacking OOF/refit contract.
  - `618ffb2` rebuilt the tracked `_dag_ml.abi3.so`.
- `dag-ml-data/refactor/integration-dmd`
  - `818616e` merged W53 source-layout contract.
- `nirs4all/refactor/integration-nirs4all`
  - `883948b2` merged W52 native stacking replay manifest/export.
  - `316bfc69` merged W54 source-layout xfail contract probes.
- `nirs4all-studio/refactor/integration-studio`
  - `b427a22` merged W55 route runtime result parity.
- `nirs4all-web/refactor/integration-web`
  - `f87a969` merged W56 worker runtime adoption gate.
- `nirs4all-providers/refactor/integration-providers`
  - `8476a3f` merged W57 benchmarks read bridge.
- `nirs4all-cluster/refactor/integration-cluster`
  - `51ee2a6` merged W58 DAG rights/result provenance contract.
- `nirs4all-tools/main`
  - `f8e3708` merged W59 native-results metadata lowering preview.
- `nirs4all-ecosystem/main`
  - W60 readiness matrix is merged.
  - W51-W61 reports are recorded.

Validation highlights:
- dag-ml: `cargo fmt --all --check`, targeted W51 tests, `cargo test -p dag-ml-core`
  (`446 passed, 2 ignored`), `cargo clippy --workspace --all-targets -- -D warnings`,
  CLI `validate-graph`, bidirectional contract validation with `INT-dmd`,
  `check_so_freshness.py`, and `dag-ml-py` tests.
- dag-ml-data: `cargo fmt --all --check`, source-layout tests, provider/capi
  focused tests, `cargo clippy`, local contract validation, and bidirectional
  contract validation with `INT-dagml`.
- nirs4all: native `.n4a` bundle suite plus focused native-results tests
  (`11 passed`), W54 contract probes (`2 xfailed`), fallback boundary and ledger
  (`14 passed`), coverage meter (`fallback=6, target=0`), py_compile, Ruff.
- Studio: `tests/test_runs_engine_routing.py` (`14 passed, 2 warnings`),
  compileall, Ruff.
- Web: `npm run typecheck`, RT/worker Vitest set, `npm run build:single`.
- Providers: `PYTHONPATH=src pytest -q` (`58 passed, 3 skipped`), Ruff, mypy.
- Cluster: `uv run --extra dev pytest -q` (`127 passed, 1 skipped`), Ruff, mypy.
- Tools: pytest (`72 passed`), Ruff, mypy, py_compile, and module CLI
  migrate/verify smoke for a lowerable native-results preview.
- Ecosystem: cutover gate runner validate/readiness JSON and JSON syntax checks.

Remaining hard blockers:
- `B-010-FALLBACK-ZERO`: fallback meter remains `6`. The missing contracts have
  moved from dag-ml/dag-ml-data into nirs4all consumption/lowering work.
- `DROP-002-DEFAULT-ENGINE`: expected failure until the final release commit
  flips `DEFAULT_ENGINE` to `dag-ml`.

Current remaining fallback cases:
- `branch_dup_three_way_merge_predictions`
- `branch_dup_named_with_metamodel`
- `branch_dup_merge_all`
- `multi_source_by_source_branch_distinct_preproc`
- `multi_source_per_source_models_stacking`
- `multi_source_sources_concat_then_rf`

Next wave:
- Drain the three duplicate-branch stacking fallbacks by consuming W51 in
  nirs4all lowering.
- Consume W53/W61 `source_layout` in nirs4all by-source lowering and replace
  W54 strict xfails with passing parity probes.
- Extend native-results migration from metadata preview to array sidecars only
  after the workspace grouping contract is fixed.
