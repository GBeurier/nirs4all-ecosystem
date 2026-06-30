<!-- Codex xhigh review of MIGRATION_BACKLOG.md — model gpt-5.5, model_reasoning_effort=xhigh,
     run 2026-06-14 from the ecosystem root with read-only access to all sibling repos.
     Verified independently and incorporated into MIGRATION_BACKLOG.md (see its §0.1 + §16). -->

# Codex xhigh review — nirs4all → Rust migration backlog

## Verdict
Not sign-off ready. The backlog is strongest where it inventories existing coupling and data contracts, but its keystone decision is contradicted by the source: `dag-ml-py` exists, but it is not an in-process Python controller vtable today. Safe next step is spikes/oracle work only, especially controller transport, feature-buffer transport, `.n4a`, and Studio contract preservation.

## Confidence in the document's claims

| claim-area | verified? | evidence |
|---|---:|---|
| `dag-ml-py` exists | Yes | `dag-ml/crates/dag-ml-py/Cargo.toml:14-27` |
| `dag-ml-py` provides in-process controller vtable | No | `dag-ml-py/src/lib.rs:1-5`, `:156-202`, `:221-229`; `dag-ml/docs/HOST_ADAPTER_BACKLOG.md:12-17`, `:85-90` |
| dag-ml-data Python shim numeric path is JSON-only | Yes | `_provider.py:151-158`; `_abi.py:165-175`; C header has unwired views at `dag_ml_data.h:273-275` |
| `AxisKind::Processing` is unused | Yes | enum only at `dag-ml-data-core/src/model.rs:11-15`; grep only finds docs mention |
| libn4m order of magnitude | Mostly | 548 method symbols -> 188 methods + 121 infra = 669 in `ABI_RECONCILE_GAP.md:5-7`; 204 fixture JSON including manifest |
| dag-ml maturity | Partly | control plane and process execution exist (`STATUS.md:274-281`, `:498-505`), but native/PyO3 host binding does not |
| Studio coupling | Yes, count ambiguous | raw SQL `_fetch_pl`/SQLite at `store_adapter.py:1023-1080`; imports in `lazy_imports.py:132-244`; I count 28 API files, not 57 files |
| `.n4a` format | Yes, with wrapper nuance | ZIP/joblib at `generator.py:54`, `:344-347`, `:648-650`; load at `loader.py:331-337`; libn4m wrappers persist bundle bytes at `pls4all/sklearn/_base.py:162-174` |
| `nirs4all-io` boundary | Partly | Python loader supports numpy/parquet/excel/vendor (`loaders.py:201-223`, `:241-276`); Rust facade CSV-only (`loaders.rs:57-64`) |
| dependency counts | Mostly | `sklearn` 147 files, `polars` 22, `joblib` 23 match; `sklearn.base` is 72 files / 78 occurrences, not cleanly 75 |
| `SpectroDataset` stays in nirs4all / lazy boundary | Yes | class in `nirs4all/data/dataset.py:37`; lazy io adapter imports at `nirs4all_io/_adapter.py:35-40`; import-boundary test `test_import_boundary.py:9-16` |

## Findings

**[CRITICAL: ERROR] — The pyo3 in-process controller path is not real today.**
Doc location: §3.3, §3.7, especially `MIGRATION_BACKLOG.md:226-248`, `:983`. The document says `dag-ml-py` is the default transport and “the only path” for sklearn-shaped operators, zero-copy f64 buffers, and in-process execution. Source says the opposite: `dag-ml-py` is “Python bindings for DAG-ML JSON contracts” and “does not execute host controllers or own data buffers” (`dag-ml-py/src/lib.rs:1-5`). Exported functions are JSON validate/compile/plan only (`:156-202`, `:221-229`). The host-adapter source of truth says the C ABI vtable “is not the path for Python/R hosts” and native PyO3 wrappers are out of scope (`HOST_ADAPTER_BACKLOG.md:12-17`, `:85-90`).
Concrete fix: rewrite §3.3/§3.7. Treat JSONL process adapters as the current runnable production path; treat PyO3 in-process as a spike/build project with its own design, tests, and exit criteria.

**[CRITICAL: SEQUENCING] — Gate-zero S1 cannot pass as written.**
Doc location: `MIGRATION_BACKLOG.md:886-888`. S1 says to drive a FIT_CV node “through `dag-ml-py`” with borrowed f64 views. But `dag-ml-py` has no execution path, and the Python data shim only calls JSON constructors (`_provider.py:151-158`); the borrowed view C functions exist in the header (`dag_ml_data.h:273-275`) but are not declared in the ctypes shim (`_abi.py:165-175`).
Concrete fix: split S1 into three gates: wire borrowed-view provider; choose/build host-controller runtime; then run a real FIT_CV latency benchmark.

**[HIGH: GAP] — No explicit FFI safety contract across dag-ml, dag-ml-data, libn4m, PyO3, and ctypes.**
The backlog mentions GIL and feature views, but not a hard ownership/threading/error/ABI matrix. Source shows why this must be first-class: dag-ml scheduler requires `Send + Sync` controllers (`STATUS.md:498-504`); manifests declare `thread_safe`, `process_safe`, `needs_python_gil` (`COORDINATOR_SPEC.md:112-117`); dag-ml-data has borrowed/Rust-owned allocation rules (`ABI.md:126-132`, `:239-244`); three ABIs have independent version surfaces (`dag_ml.h:120-141`, `dag_ml_data.h:209-216`, `n4m_version.h:20-22`).
Concrete fix: add an “FFI contract” epic before E5/E7 covering lifetimes, panic/error propagation, thread safety, ABI skew, GIL policy, and native-library loading.

**[HIGH: GAP] — Studio run lifecycle is under-modeled.**
Doc location: §7, E12. The backlog captures raw SQL, but misses job/progress/cancel semantics. Studio runs are JobManager-backed WebSocket jobs (`runs.py:1-18`, `:583-607`), submitted to a thread pool (`runs.py:1332-1338`), and cancellation is cooperative through `job_manager.cancel_job()` plus `should_stop` (`runs.py:1664-1680`).
Concrete fix: add acceptance tests for run start/progress/cancel/fail/retry/export over the Rust backend, not just schema and query parity.

**[HIGH: GAP] — Rollback strategy conflicts with deleting legacy.**
Doc location: feature flag and E15 (`MIGRATION_BACKLOG.md:763-765`, `:799`, `:916`). A strangler flag is sound, but deleting legacy controllers while Studio reads private SQL and `.n4a`/workspace contracts directly removes the rollback path.
Concrete fix: keep `legacy` runnable for at least one compatibility release; define abort criteria and rollback ownership before flipping default.

**[HIGH: GAP] — Licensing is material and not gated.**
`nirs4all-methods` is dual CeCILL/AGPL with optional commercial licensing; commercial/proprietary/SaaS use requires attention (`nirs4all-methods/LICENSING.md:1-33`). dag-ml and dag-ml-data also declare CeCILL/AGPL.
Concrete fix: add Phase 0 legal review for Studio/Electron distribution, hosted deployments, and libn4m commercial terms.

**[MEDIUM: ERROR] — libn4m count/symbol wording needs precision.**
The 669/188 reconciliation is real (`ABI_RECONCILE_GAP.md:5-7`; `bindings/SPEC.md:63-79`), and 204 JSON fixtures including manifest is real. But current split catalog has 209 YAML method files, so “188 catalog methods” should be “188 ABI-mapped catalog methods.” Some cited names are shorthand or wrong: `n4m_domain_adaptation_di_pls` is actually `n4m_domain_adaptation_di_pls_fit` (`domain_adaptation.h:130`). Kennard Stone uses `n4m_model_selection_kennard_stone_*` (`model_selection.h:35-42`).
Concrete fix: use exact ABI names and qualify the 188 count.

**[MEDIUM: UNDERSTATEMENT] — `.n4a` native model pickleability is not simply unknown.**
Raw C handles are not serializable, but existing `pls4all` sklearn wrappers already define the right pattern: persist `_bundle_` bytes and drop `_model_handle_` / `_model_ctx_` from pickle state (`pls4all/sklearn/_base.py:162-174`).
Concrete fix: make E10 require libn4m wrappers to implement bundle-byte pickle/deepcopy semantics; do not frame it as an unknown raw-handle pickle test.

**[MEDIUM: OVERSTATEMENT] — dag-ml host-adapter maturity is misstated.**
The backlog correctly says no end-to-end real nirs4all pipeline and no PyO3 production binding. But “every production execution path ... smoke/mock” is stale: STATUS lists sklearn production plus prospectr and mdatools shipped adapters (`STATUS.md:652-684`). Tuner execution is still smoke/process-fixture level (`cli_contracts.rs:4888-5022`) and advanced search lowering is still missing (`STATUS.md:639-646`).
Concrete fix: distinguish “production JSONL adapters exist” from “not enough for nirs4all end-to-end.”

**[MEDIUM: ERROR] — Studio import count is ambiguous.**
Doc location: `MIGRATION_BACKLOG.md:661`. I count 28 API Python files importing `nirs4all`, 112 API import occurrences, 37 files / 133 occurrences across all Studio Python. The “57 distinct import sites across ~28 backend files” needs a reproducible counting definition.
Concrete fix: replace with a checked command and freeze the list as a migration checklist.

**[MEDIUM: GAP] — `n_jobs` semantics are not a cleanup detail.**
Current nirs4all uses joblib/loky for variant parallelism (`orchestrator.py:89-110`, `:515-526`, `:751-753`) and threading for branches (`branch.py:2165-2193`, `:2494-2507`, `:2611-2615`). dag-ml’s scheduler has deterministic level-order commit semantics (`STATUS.md:498-504`).
Concrete fix: add a compatibility map for `n_jobs`, oversubscription, nested BLAS/torch threads, progress updates, cancellation points, and deterministic seed streams.

**[MEDIUM: ERROR] — `nirs4all-io` Python and Rust surfaces are conflated.**
Python `nirs4all-io` is not “vendor-only”: it reads numpy, parquet, Excel, CSV, and vendor files (`loaders.py:201-223`, `:241-276`). The Rust facade is CSV-family only today (`loaders.rs:57-64`).
Concrete fix: split claims by surface: Python MVP broader; Rust facade CSV-only until S1.7.

## Missing items the backlog should add

- Controller-transport ADR: JSONL current path vs PyO3 future path, with security and performance gates.
- FFI memory model: ownership, borrowed buffers, release callbacks, panic/error conversion, handle invalidation.
- ABI-skew matrix: dag-ml, dag-ml-data, libn4m versions tested together in Python wheels and Studio bundles.
- Studio lifecycle contract: WebSocket events, progress, cancellation, retry, persisted run manifests.
- Workspace rollback plan: legacy retention, dual-write/compare, abort criteria, major-version policy.
- `n_jobs` compatibility: scheduling semantics, CPU/GPU oversubscription, deterministic RNG, cancellation points.
- `.n4a` v1/v2 decision: wrapper serialization contract and saved-bundle compatibility tests.
- Dtype policy: f64/f32 copies, non-finite handling, row/column-major costs, tolerance ledger.
- Security model: process adapter artifact confinement, trusted in-process Python, workspace path hardening.
- Licensing gate: CeCILL/AGPL/commercial implications for Studio and proprietary/SaaS users.

## Effort & critical-path assessment

The central ~105 pw estimate is optimistic if PyO3 in-process remains the default. The backlog already has 81 pw host work plus 20–28 pw dependent lib-side work (`MIGRATION_BACKLOG.md:923-927`), before adding the missing PyO3 runtime, Studio lifecycle parity, packaging/CI, and FFI hardening. I would budget closer to 120–150 pw unless the team explicitly chooses the existing JSONL process path and accepts its performance envelope.

M2/E5 is not the linchpin. The linchpin is M0: prove or reject controller transport with real feature buffers and one real FIT_CV pipeline. Reorder to: oracle/flag/rollback, controller transport decision, borrowed f64 provider, workspace + `.n4a` contract, then libn4m low-risk cuts, then NN/Optuna/Studio breadth.

## Top 10 actionable corrections

1. Rewrite §3.3/§3.7: `dag-ml-py` is JSON contracts only; PyO3 in-process is not verified/default.
2. Split S1/S2 into provider-view binding, controller-runtime implementation, and end-to-end FIT_CV benchmark.
3. Add an FFI/ABI safety epic before E5/E7.
4. Correct libn4m counts and cited symbol names.
5. Update dag-ml maturity language: shipped JSONL adapters exist; PyO3/native host execution does not.
6. Clarify `nirs4all-io` Python vs Rust loader coverage.
7. Replace “n4m pickleability unknown” with an explicit bundle-byte wrapper contract.
8. Add Studio run lifecycle and WebSocket/job-queue parity tests.
9. Add `n_jobs`/scheduler compatibility and deterministic RNG acceptance criteria.
10. Add licensing, rollback, and CI/build-matrix gates before defaulting to Rust.