# W4 — Cross-engine parity slice (B-011 / SW5 §6)

**Agent:** W4 (cross-engine parity, Wave-2B) · **Date:** 2026-07-01
**Worktree:** `_worktrees/W4-nirs4all` · **Branch:** `refactor/W4-cross-engine` (off committed `refactor/L17-pyref`)
**Scope (narrowed mid-run):** a focused B-011 cross-engine parity slice — tests around the *actual* cross-engine **export / error / workspace** behavior, no broad refactors. Commit only if targeted tests + ruff are green.

---

## 0. TL;DR

- Added **4 test modules / 15 tests** covering the three missing cross-engine surfaces from `SW5` §6 (PYREF-009a `.n4a`, PYREF-009b workspace, PYREF-err error/refusal), plus a fast deterministic export-surface module.
- All **17** gate tests pass (15 new + 2 ledger); **ruff clean** on every file I touched; `py_compile` clean.
- Flipped the three `compatibility.json` / `compatibility.md` **§D cross-engine rows** I landed tests for from `GAP` → `EXISTS`, each with its `owning_test` (the ledger bookkeeping W4 owns).
- **Did NOT** touch `expected_fallback` (W2), `coverage_meter` (W1), or `_authority.py` (no validation refactor). Ownership boundaries respected.
- **Provenance (this session):** the 3 slow modules + the 2 ledger edits were found **uncommitted in the worktree** from a prior interrupted W4 session (the first `rtk git status` was compacted to `"clean"` and hid them — the unfiltered `git status --porcelain -uall` surfaced them). I re-verified every one green under the real native path, and **authored `test_cross_engine_export_surface.py` this session** to the design the prior report already documented (the file was absent on disk). The whole coherent slice is landed together; nothing was adopted unverified.
- **W7 dependency reported:** the runtime classifier `nirs4all/pipeline/dagml/rt.py` (`RtError.from_dagml_error`, B-018/L10) is **not in-tree yet** (verified absent). The error-parity test pins the CAP-004/RT-003 cause vocab behind a local `_classify_cause` helper with a `TODO(W7)` to consume `rt.py` when it lands.
- Deferred (out of narrowed scope): the nirs4all-side wheel/`.so` freshness gate (`PYREF-011`/G8), the `make parity` one-entry command (G3), the `_authority.py` band-validation extension, and the broader `compatibility.md` band-table rewrites. None block the test slice; see §6.

---

## 1. What landed

### New tests (`tests/integration/parity/`)

| File | Tests | Marker | Surface (SW5) | Runtime |
|---|---|---|---|---|
| `test_cross_engine_export_surface.py` | 8 | `parity` (fast) | export gating / no-workspace error contract | 0.04 s |
| `test_conformance_n4a_cross_engine.py` | 3 | `parity, slow` | §6a `.n4a` cross-engine (PYREF-009a) | ~30 s |
| `test_conformance_error_parity.py` | 2 | `parity, slow` | §6c error/refusal (PYREF-err) | ~5 s |
| `test_conformance_workspace_cross_engine.py` | 2 | `parity, slow` | §6b workspace cross-engine (PYREF-009b) | ~20 s |

`test_cross_engine_export_surface.py` is the **fast** companion (constructed `RunResult`s, no pipeline run): it locks the `_is_dagml_engine()` truth table and the load-bearing ADR-17 cutover contract that the *same* no-workspace export call raises a **catchable `NotImplementedError`** on dag-ml but a **plain `RuntimeError`** (NOT a `NotImplementedError`) on legacy — so a genuine legacy misuse is never silently swallowed into a refit. (Authored **this session** to the design the prior report documented — the file was absent on disk; a mutation probe confirmed the `not isinstance(..., NotImplementedError)` assertion bites, since `NotImplementedError ⊂ RuntimeError`.)

### Ledger §D bookkeeping (`docs/compatibility.json` + `docs/compatibility.md`)

The three surfaces I landed tests for flipped `GAP → EXISTS`, each gaining an `owning_test`:

| Surface | Was | Now | Band | `owning_test` |
|---|---|---|---|---|
| `n4a_cross_engine` | gap | **exists** | `cross_impl_ypred` | `…::test_n4a_bundle_cross_engine_round_trip` |
| `workspace_cross_engine` | gap | **exists** | `cross_impl_score` | `…::test_native_results_triple_round_trips_and_agrees_cross_engine` |
| `error_refusal_parity` | gap | **exists** | `n/a_semantic` | `test_conformance_error_parity.py` |

The `n4a_cross_engine` and `error_refusal_parity` rows carry a `note` recording the transitional state (legacy-refit export bridge; local cause helper) and the tightening/upgrade path. Untouched: `n4a_export_roundtrip` (PARTIAL, L17), `studio_oracle` (GAP, W8), `methods_installed` (PARTIAL, L9).

---

## 2. Test design + measured evidence

All three numeric surfaces were **probed empirically first** (3 throwaway probes), so the assertions are sized against real measured deltas, not guesses. The canonical case is `baseline_vertical_slice` (no-preprocessing PLS); the n4a/workspace tests also cover `generator_range_n_components` (sweep) and `round_trip_with_y_processing_inverse` (the ~6e-4-noise y_processing case).

### §6a — `.n4a` cross-engine (`cross_impl_ypred`, 1e-3)

Two legs, both via the public detached path `nirs4all.predict(model="…n4a", data=X_raw)`:

- **Interchange:** a legacy-written `.n4a` and a dag-ml-written `.n4a` predict alike on the same raw test X. Measured `max|Δ| = 0.0` for `baseline_vertical_slice`.
- **Cross-engine round-trip:** the dag-ml bundle reproduces the dag-ml **NATIVE (Rust)** run's final-(test) `y_pred`, mapped by sample id. Measured `max|Δ| = 1.49e-6` — comfortably under the `1e-3` band.

Transitional note (carried in the test + ledger): dag-ml `.n4a` export currently delegates to a legacy-refit bridge (A3 §8), so this pins the **bridge** round-trip; it tightens to `native_export_reproduce` (1e-6) when native `.n4a` export (DML-008/W3) lands — a one-line band change. Cases that fall back or are not single-artifact native runs are **skipped**, not failed (mirrors `test_conformance_export_roundtrip`).

### §6b — workspace cross-engine (`cross_impl_score` / `cross_impl_ypred`, 1e-3)

The engines write **non-overlapping** on-disk formats, so the test is about *projection equality*, not byte-identity:

- **Read-back fidelity (same engine):** the dag-ml native triple (`manifest.json + score_set.json + predictions.parquet`) read back via `read_native_results` reproduces the live run's final-(test) `y_pred` exactly (`max|Δ| = 0.0`); `manifest.engine == "dag-ml"`, `score_set` non-empty.
- **Cross-engine agreement through the read path:** the persisted dag-ml triple, read **from disk**, agrees with the **legacy** oracle within `cross_impl_ypred` on per-sample `y_pred` and `cross_impl_score` on `best_score` (measured score Δ = `1.58e-7`).
- **Legacy workspace inspectable:** the legacy run exposes the runtime V1 read surface (finite selected `best_score` + final-(test) predictions).

Reuses the audited `H._final_test_pred_by_sample` over the read-back `Predictions` via a `SimpleNamespace` shim (no logic duplication).

### §6c — error / refusal parity (`n/a_semantic`; cause vocab CAP-004/RT-003)

Empirically, the **only** shape that raises on *both* engines at the public `run()` boundary is an **invalid-hyperparameter** model (multi-model / unknown-operator / no-splitter shapes silently *fall back* on dag-ml or are silently accepted by legacy — documented in the probe). So:

- **Cross-engine refusal parity:** an invalid pipeline (`PLSRegression(n_components=99999)`) RAISES on both `engine="legacy"` and `engine="dag-ml"` — the dag-ml leg *propagates* (a genuine fit failure is not an unsupported-shape fallback), proving the engines agree on which pipelines are invalid.
- **Stable cause vocab:** the dag-ml refusal classifies to a stable `RtError.cause` ∈ {`unsupported_shape`, `unsupported_capability`, `unavailable_backend`, `invalid_request`, `runtime_error`}. The genuine fit failure → `runtime_error`; the **real** `_reject_multi_model` refusal path → `DagMlUnsupported` → `unsupported_shape`; `DagMlUnavailable` → `unavailable_backend` (RT-003:182-184 migration table).

---

## 3. W7 dependency (reported, not blocking)

`SW5` §6c and `RT_spec` RT-003 say the dag-ml refusal cause vocabulary is owned by **CAP-004** and surfaced by the unified runtime envelope `nirs4all/pipeline/dagml/rt.py` (`RtError`, `from_dagml_error`) — **W7's deliverable** (B-018/L10).

**Status: `rt.py` is NOT in-tree** (`importlib.util.find_spec("nirs4all.pipeline.dagml.rt")` → `None`). Per the W4 brief, the error-parity test is therefore tolerant behind a local helper:

```python
# TODO(W7/B-018): replace with nirs4all.pipeline.dagml.rt.RtError.from_dagml_error
def _classify_cause(exc): ...  # applies the RT-003 migration table verbatim
```

When W7 lands `rt.py`, the single `_classify_cause` swap point consumes `RtError.from_dagml_error`; the vocabulary set and assertions are already aligned to RT-003, so no test-shape change is needed.

---

## 4. Gates run (all green)

```
pytest tests/integration/parity/test_cross_engine_export_surface.py \
       test_conformance_n4a_cross_engine.py \
       test_conformance_error_parity.py \
       test_conformance_workspace_cross_engine.py \
       test_compatibility_ledger.py
  → 17 passed  (15 new + 2 ledger)

ruff check  <4 new test files>            → All checks passed!
mypy        <4 new test files>            → Success: no issues found in 4 source files
pytest tests/integration/parity/ --collect-only   → 798 tests collected, 0 errors
json.tool   docs/compatibility.json       → valid (schema_version 1)
```

(The 15-test slice ran in 58.85 s with the `dag-ml-cli` binary present — `dag-ml/target/release/dag-ml-cli`, built 2026-06-30 — so the slow legs exercised the real native (Rust) path rather than skipping.)

`test_compatibility_ledger.py` stays green: the `cross_engine_surfaces` array is not asserted by `_authority.py`, so the §D edits cannot drift the snapshot.

> Pre-existing (NOT mine): `ruff check tests/integration/parity/` reports **one** `I001` import-order finding in `_authority.py` (the `Y_PRED_TOL_OVERRIDES` import block). `_authority.py` is **untouched** by W4 (`git diff --name-only` confirms). Out of W4's gate; flagged for the file's owner.

---

## 5. Files changed

```
A  tests/integration/parity/test_cross_engine_export_surface.py        (8 tests, fast)
A  tests/integration/parity/test_conformance_n4a_cross_engine.py       (3 tests, slow)
A  tests/integration/parity/test_conformance_error_parity.py           (2 tests, slow)
A  tests/integration/parity/test_conformance_workspace_cross_engine.py (2 tests, slow)
M  docs/compatibility.json   (§D: 3 cross_engine_surfaces rows gap→exists + owning_test/note)
M  docs/compatibility.md     (§D table: 3 rows GAP→EXISTS + owning test)
```

Ownership respected: **no** edit to `expected_fallback` (W2), `coverage_meter` (W1), `_authority.py`, `tolerance_bands` content, `test_conformance_dual_engine.py`, or any `nirs4all/` package source. `PARALLEL_REFACTORING_SYNC.md` not touched.

---

## 6. Deferred B-011 work (remaining for LOCK-PYREF G3/G8, out of narrowed slice)

These were in the original W4 brief but are out of the narrowed "tests around actual cross-engine behavior" slice; none block the landed tests:

1. **nirs4all-side wheel/`.so` freshness gate** (`PYREF-011`, G8, SW5 §7c) — `scripts/` gate asserting installed `dag_ml`/`n4m` satisfy pins + invoking sibling `../dag-ml/scripts/check_so_freshness.py` when present. *(Probe data: installed `dag_ml 0.2.1`, `n4m abi (1,22,0)`.)*
2. **`make parity` one-entry command** (`PYREF-006`, G3) — a `Makefile` exists in the worktree; wiring the §9a tier ladder behind one target is additive.
3. **`_authority.py` cross-engine §D validation** — extend `validate_compatibility_ledger` with a `_validate_cross_engine_surfaces` (band ∈ `tolerance_bands`, `owning_test` present when `status==exists`). Deferred to avoid a validation refactor in a test-focused slice; the §D edits are currently safe because they are unvalidated.
4. **Studio rides the oracle** (§6d, `studio_oracle`) — W8's lane; left `GAP`.
5. **dag-ml `parity_oracle.v1.json` tolerance-profile amendment** — W5's lane (reads W4's band names); not a W4 edit.

---

## 7. Notes for the integrator

- The slow tests follow the suite's **skip-on-fallback** discipline: they `pytest.skip` (never fail) when the dag-ml engine runs the legacy fallback or is not a single-artifact native run on a given build — so the cross-engine claim is only asserted when dag-ml ran natively.
- `nirs4all.predict(model="…n4a", data=X)` works **detached** (no workspace) and returns `y_pred` in test-sample order — relied on by the n4a test.
- One local commit made on `refactor/W4-cross-engine` (gates green). **Not pushed.**
