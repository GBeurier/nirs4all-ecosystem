# Wave 4AM - Skip / Xfail Parity Audit

Date: 2026-07-03
Agent: Codex Lane K, read-mostly parity auditor.

Scope read:

- `_worktrees/RC-v1-nirs4all-python` (`rc/v1-full-refactor-python`, `5071a0b0`)
- `_worktrees/RC-v1-dagml` (`rc/v1-full-refactor`, `a8f6cb3`). Note: no local `_worktrees/RC-v1-dag-ml` directory exists.
- `_worktrees/RC-v1-studio` (`rc/v1-full-refactor`, `5907639`)
- `_worktrees/RC-v1-benchmarks` (`rc/v1-full-refactor`, `6e4c630`)
- `_worktrees/RC-v1-tools` (`rc/v1-full-refactor`, `7c5070f`)

No `nirs4all-drafts` or `nirs4all-lab` access was used. No full parity run was started.

## Commands

- Read local `AGENTS.md` / `CLAUDE.md` for Python, dagml, and Studio; benchmarks/tools/ecosystem have no local files at repo root.
- Static scans: `rtk rg` over the five worktrees for `pytest.skip`, `pytest.importorskip`, `pytest.mark.skipif`, `pytest.mark.xfail`, `pytest.xfail`, `#[ignore]`, and JS/Vitest skip forms.
- Python fast parity accounting:
  - `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /home/delete/nirs4all/nirs4all/.venv/bin/python -m tests.integration.parity.coverage_meter --check` -> `coverage_meter OK (fallback=0, target=0)`.
  - `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /home/delete/nirs4all/nirs4all/.venv/bin/python -m tests.integration.parity._marker_audit --check` -> OK; static call sites: `3` sanctioned xfail, `126` sanctioned skip, `42` tolerance literals.
  - `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity/test_marker_audit.py tests/integration/parity/test_compatibility_ledger.py -q -p no:cacheprovider` -> `15 passed`.
- Benchmarks collect-only: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest --collect-only -q -p no:cacheprovider` -> `88` tests collected.
- Tools collect-only: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3.11 -m pytest --collect-only -q -p no:cacheprovider` -> `114` tests collected.

## 1. Already Burned / Proved To 0 In Python Full Parity

Latest full Python parity proof is Wave 4X, not rerun here:

- `docs/agent_reports/WAVE_4X_FULL_PARITY_SECURITY_FETCHABILITY.md:43-55`: non-slow split `444 passed`, slow split `443 passed`; combined `887 passed`, `0 skipped`, `0 xfailed`, `0 failed` on Python `6a2c7200` with selected RC `dag-ml` / `dag-ml-data` and `NIRS4ALL_REQUIRE_N4M=1`.
- `docs/agent_reports/RC_SKIP_XFAIL_AUDIT.md:36-53`: stale `30 skipped / 11 xfailed` and intermediate `14 skipped / 6 xfailed` are superseded; coverage meter summary is `registered=95`, `fallback=0`, `native=95`, `xfail_strict=0`, `skip=0`.
- Current Python worktree is newer (`5071a0b0`, four commits after `6a2c7200`; see `WAVE_4AJ_PERF_GATE.md:7-13` and `:115-117`). I did not rerun full parity by instruction. Fast static gates on `5071a0b0` still show `fallback=0`, no untracked marker/tolerance debt, and the ledger tests pass.

Python authority lines:

- `RC-v1-nirs4all-python/docs/compatibility.md:265-281`: registered `95`, non-runnable `0`, fallback `0`, native `95`, strict-xfail `0`, `pytest.skip` registry debt `0`.
- `RC-v1-nirs4all-python/docs/compatibility.md:331-359`: xfail containment and closed skip taxonomy.
- `RC-v1-nirs4all-python/tests/integration/parity/test_marker_audit.py:26-55`: live-tree gate and marker-policy drift gate.

Decision: Python parity skip/xfail debt is considered burned for the latest full proof. For `5071a0b0`, cite only "static gates clean" until a final full parity is rerun.

## 2. Acceptable Env / Toolchain Skips To Document

Python outside the parity suite has no xfail markers in tests. Remaining skip call sites are optional-dependency or fixture-precondition gates, not PYREF debt:

- Optional ML/extras: `tests/integration/explainability/test_shap_integration.py:34,74,112,152,190,239,280`, `tests/integration/pipeline/test_finetune_integration.py:34-282`, `tests/unit/operators/models/test_pytorch.py:9`, `tests/unit/operators/models/test_jax.py:8`, `tests/unit/operators/models/test_sklearn_pls.py:454-5648`, `tests/unit/operators/models/test_tabpfn_nirs.py:13,35`, `tests/unit/operators/models/test_aom_pls_aomlib.py:22`, `tests/unit/operators/methods/test_n4m_ops.py:73`.
- Optional file/storage deps: `tests/unit/data/loaders/test_parquet_loader.py:18-38`, `tests/unit/data/loaders/test_excel_loader.py:41,159`, `tests/unit/data/loaders/test_matlab_loader.py:37,148`, `tests/unit/pipeline/storage/test_migration.py:300-541`, `tests/unit/pipeline/storage/test_array_store_lock.py:23`.
- Optional sibling/schema deps: `tests/unit/data/test_config_from_io.py:19,485`, `tests/unit/pipeline/test_rt_envelopes.py:268,356-360`.

Studio static skip sites remain, but selected gates have already shown zero realized skips:

- Backend proof: `docs/agent_reports/WAVE_4W_STRICT_DAGML_WASM_STUDIO_DATASETS.md:70-77` -> full backend `2335 passed`, `0 skipped`; Wave 4AC repeats `2335 passed` at `WAVE_4AC_NONPY_GATES_SECURITY.md:51-53`.
- Frontend proof: `docs/agent_reports/WAVE_4Y_STUDIO_METHODS_CORE_WASM.md:26-31` -> `3709` Vitest tests, `0 failed`, `0 skipped`.
- Static call sites to document:
  - OS / host behavior: `tests/test_update_downloader.py:31`, `tests/test_update_downloader_symlinks.py:19`, `tests/test_smoke_update_zip_permissions_script.py:38`, `tests/test_self_update_e2e.py:31`, `tests/test_updater_apply_sandbox.py:22,139,201`, `electron/smoke-self-update.test.ts:116`.
  - ML/native availability: `tests/conftest.py:181`, `tests/test_datasets_detection.py:35-37`, `tests/test_pipeline_roundtrip.py:43-46`, `tests/test_pipeline_canonical.py:107-108`, `tests/integration/test_native_results_format.py:44-47,91-92`.
  - Operator/runtime optional preconditions: `tests/test_operators_manifests.py:73,83,85`, `tests/test_operator_definitions.py:218,247,252,329,383,423`, `tests/test_playground.py:808,921,943,961,979`.
  - Quick-run integration guard sites: `tests/integration/test_quick_run_flow.py:105-526`, `tests/integration/test_run_lifecycle.py:47-645`, `tests/integration/test_run_errors.py:253-532`. These are acceptable only because the latest full backend gate realized `0 skipped`; if they trigger in a release gate, treat as a blocker.
  - Frontend noisy timing diagnostic: `src/components/pipeline-editor/validation/__tests__/benchmark.test.ts:441-446` skips only on CI; absolute-budget benchmarks remain active.

Dagml has no standard skip/xfail markers in the static scan (`pytest`, JS skip forms, or Rust `#[ignore]`). Two C conformance tests return early if the sibling `dag-ml-data` checkout is absent:

- `crates/dag-ml-capi/tests/c_conformance.rs:2047-2057`
- `crates/dag-ml-capi/tests/c_conformance.rs:2497-2507`

This is acceptable for local ad hoc runs, but RC CI must provide the sibling checkout when claiming cross-header/provider conformance. `scripts/check_so_freshness.py:112-130` also has graceful local skips when the tracked extension binary/git history is absent.

Benchmarks has one optional service extra skip:

- `tests/test_service_api.py:14` -> `pytest.importorskip("fastapi")`.
- Current collect-only found all `88` tests; Wave 4AJ full local gate reports `.venv/bin/pytest -q` -> `88 passed` at `docs/agent_reports/WAVE_4AJ_PERF_GATE.md:90-92`.

Tools has Parquet/Arrow optional skips:

- `tests/test_real_golden_fixtures.py:82,187,262,335,667,776`
- `tests/test_commands.py:26,361,575,675,1088,1125`
- `tests/test_native_results.py:58`
- Current collect-only found all `114` tests; Wave 4AF full local gate reports `114 passed` at `docs/agent_reports/WAVE_4AF_TOOLS_MIGRATION_GOLDENS.md:20-23`.

Decision: these are environment/toolchain gates to document. For release gates that claim the related surface, install the extra and require zero realized skips.

## 3. Real RC Blockers

No active skip/xfail blocker was found in the selected evidence set.

Conditional blockers:

- Full Python parity proof freshness: latest long proof is `6a2c7200`; current selected Python worktree is `5071a0b0`. Static gates are clean, but final RC should rerun full parity on the final Python head before claiming the `887/0/0/0` proof for that head.
- Studio quick-run skips are not acceptable if realized. The latest full backend gate realized `0 skipped`; any future release run with skips at `tests/integration/test_quick_run_flow.py`, `test_run_lifecycle.py`, or `test_run_errors.py` should fail the RC sign-off.
- Benchmarks service API and Tools Parquet/native-results coverage depend on `fastapi` and `pyarrow`. If those extras are missing in final RC CI and the tests skip, the release claim for those surfaces is incomplete.
- Dagml C ABI cross-repo conformance depends on a `dag-ml-data` peer checkout. A final RC gate that omits it cannot claim cross-header/provider conformance.

Decision: keep no new xfail/skip debt. Treat realized skips in the final RC gates as red unless they are explicitly non-claimed host/toolchain gates (Windows-only, licensed MATLAB/Octave/R, or similar) and are documented with the exact missing toolchain.
