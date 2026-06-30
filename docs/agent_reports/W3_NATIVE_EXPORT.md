# W3 — Cross-engine `.n4a` export parity (B-011 / native export)

**Agent:** W3 (Wave-2B native-export) · **Date:** 2026-07-01 · **Lane:** `L17` oracle (B-011), touching `L5`/`L9`/`L12` concerns
**Branch:** `refactor/W3-native-export` (worktree `_worktrees/W3-nirs4all`), based on committed L17 tip `1e4d8043`.
**Paired dag-ml worktree:** `_worktrees/W3-dagml` on `refactor/W3-native-export-dagml` — **UNCHANGED** (the `.n4a` path is entirely Python-side; no Rust edit was needed, so that branch stays clean).
**Blocker:** `B-011` — "workspace/artifact `.n4a` round-trip cross-engine" is not covered by the oracle (RV8-flagged; final `LOCK-PYREF` stays open until it is).
**Owned surface:** ONE new file — `tests/integration/parity/test_conformance_n4a_bundle_parity.py`.
**Did NOT touch:** export production code (`api/result.py`, `pipeline/dagml/run_backend.py`), the `.n4a` bundle format/generator/loader (watchlist surface — `L2`+`L4`+`L5`), W1's `coverage_meter`, W2's `detect`/`run_paths`/`run_backend` + `EXPECTED_FALLBACK`, W4's `tolerance_bands`/`authority`, `docs/compatibility.json`, `dag-ml` (no Rust), `PARALLEL_REFACTORING_SYNC.md`.

---

## 0. TL;DR

- **Closed the exact RV8/B-011 gap** "workspace/artifact `.n4a` round-trip cross-engine" with a focused **dual-engine conformance test** — test-only, single new file (W1 precedent). No production change; the `.n4a` format is a watched surface (`L2`+`L4`+`L5`), and the verification — not the format — was the gap.
- For the two registry cases that DECLARE the bundle-IO contract (`round_trip_baseline_export_predict`, `round_trip_with_y_processing_inverse`), it exports an `.n4a` from **both** engines, reloads via `BundleLoader`, predicts on the held-out test X, and pins **three independent links**:
  - **A — transitional bridge contract:** the dag-ml run's `.n4a` reload-predict reproduces the dag-ml run's **NATIVE** final-(test) `y_pred` within the cross-engine tol (`1e-3`). **Measured Δ ≤ 7.8e-4.**
  - **B — same-engine bundle-IO fidelity:** the legacy run's `.n4a` reload-predict reproduces the legacy run's final-(test) `y_pred` to float identity (`1e-6`). **Measured Δ = 0.0.**
  - **C — cross-engine bundle equivalence:** the legacy `.n4a` and the dag-ml `.n4a` predict identically on the same holdout X (`1e-3`). **Measured Δ = 0.0.**
- **Key discovery (documented for the P3 follow-up):** `RunResult.export(format="n4a")` for a dag-ml run has **NO native path** — it ALWAYS re-fits the frozen pipeline through the legacy engine (the P1c bridge). Only `export_model` (joblib) got the native single-artifact fast-path (`_dagml_native_export_model`, P3 2c-ii). A native `.n4a` is the next slice but is a **bundle-format change on a watched surface** — out of this focused, low-risk slice.
- Gates green: the new dual-engine test (2 passed), `ruff`, `mypy`, `py_compile`, and a full parity `--collect-only` (785 items, no breakage).

---

## 1. What shipped

### The gap (verified, not assumed)

The closest existing coverage stops one step short of cross-engine `.n4a`:

| Existing test | What it pins | What it does NOT pin |
|---|---|---|
| `test_parity_smoke::test_round_trip_bundle_export_load_predict` | run → `export(.n4a)` → `nirs4all.predict` on the **default engine**, asserts `preds is not None` | second engine; any numerical parity |
| `test_conformance_export_roundtrip` | `export_model` (joblib, single estimator) reload-predict exactness + the `.n4a` **refusal** contract (`source=`/`chain_id=` rejection, no-spec catchability) | the full `.n4a` **bundle** export → `BundleLoader` → predict, compared across engines |

So the `.n4a` *bundle* round-trip had never been asserted across engines — exactly the B-011 line RV8 corrected the L17 scope on.

### The test (`test_conformance_n4a_bundle_parity.py`)

`test_n4a_bundle_roundtrip_cross_engine_parity[case]`, parametrized over the two
fully-seeded single-model bundle-IO shapes. Per case:

1. `H.dual_engine_runner(case, dataset)` runs legacy + dag-ml and reports `dagml_native` (the suite's source-of-truth signal: no fallback warning AND the `per_dataset` engine marker). **Skips** (not fails) if dag-ml fell back — then A/C are legacy-vs-legacy and trivially true; the boundary can never silently widen.
2. Pull the held-out test sample ids + raw 2D X at the dataset's **native** dtype (float32 — the dtype the run predicts on; a float64 widen would inject ~1e-6 noise that is not the bundle's fault). Mirrors `test_conformance_export_roundtrip._test_x`.
3. `result.export(".n4a")` → `BundleLoader(path).predict(X)` for each engine, keyed by sample id (predict row order == X row order == id order).
4. Assert links **A**, **B**, **C** (above), reusing the canonical sample-keyed mapper `H._final_test_pred_by_sample` so the comparison is by identity, not row position.

Tolerances are **local literals** (not a coupling to another lane's constant): `_BUNDLE_IO_EXACT_TOL = 1e-6` (same-engine, measured 0.0) and `_CROSS_ENGINE_YPRED_TOL = 1e-3` (equal to `_conformance_helpers._DEFAULT_YPRED_TOL`, the suite's measured cross-engine PLS+inverse ceiling; measured deltas 0.0 and ≤7.8e-4 sit safely under it).

### Observed: the bridge stochastic warning over-warns (safely)

`dual_engine_runner` does not pass `run(random_state=...)`, so the dag-ml `.n4a`
export emits the **conservative** `_dagml_export_stochastic` warning (run-`None`
signal). Both cases are nonetheless locally seeded (`ShuffleSplit(random_state=42)`,
`Ridge(random_state=42)`, deterministic PLS), so the bridge refit is **exact**
(Δ=0.0 / ≤7.8e-4) despite the warning — a live confirmation of W2's note that the
run-`None` signal over-warns a fully-deterministic pipeline in the safe direction.

---

## 2. Evidence (gates)

All run with the sibling venv `/home/delete/nirs4all/nirs4all/.venv` (`dag_ml` importable; worktree `nirs4all` resolved via cwd).

```text
# The new dual-engine .n4a parity test
python -m pytest tests/integration/parity/test_conformance_n4a_bundle_parity.py -p no:cacheprovider -q
  → 2 passed, 12 warnings in 14.44s
    · [round_trip_baseline_export_predict]      NATIVE — A/B/C all Δ=0.0
    · [round_trip_with_y_processing_inverse]    NATIVE — A Δ=7.8e-4, B Δ=0.0, C Δ=0.0

# Lint / type / compile (new file)
ruff check  tests/integration/parity/test_conformance_n4a_bundle_parity.py   → All checks passed!
mypy        tests/integration/parity/test_conformance_n4a_bundle_parity.py   → Success: no issues found in 1 source file
py_compile  tests/integration/parity/test_conformance_n4a_bundle_parity.py   → OK

# Regression: full parity collection still intact with the new module present
python -m pytest tests/integration/parity/ --collect-only -q                 → 785 tests collected, 0 errors
```

### Measured cross-engine `.n4a` deltas (the basis for the tolerances)

| Case | dag-ml native | C: legacy `.n4a` vs dag-ml `.n4a` | B: legacy `.n4a` vs legacy run | A: dag-ml `.n4a` vs dag-ml native run |
|---|---|---|---|---|
| `round_trip_baseline_export_predict` (SNV→PLS) | yes | 0.0 | 0.0 | 0.0 |
| `round_trip_with_y_processing_inverse` (SNV→y:MinMax→Ridge) | yes | 0.0 | 0.0 | **7.8e-4** |
| `generator_range_n_components` (sweep, measured but not in the test set) | yes | 0.0 | 0.0 | 0.0 |

(The `1e-3` ceiling on A is the same tolerance the suite's existing `assert_y_pred_parity` already enforces on the y_processing+Ridge shape, so it is not a new bar — only a new *application point*, the reloaded bundle.)

---

## 3. Scope decisions (why this and not more)

- **Test-only, new file.** The `.n4a` *bundle format / portability metadata* is on the interface watchlist (owned by `L2`+`L4`+`L5`); the B-011 gap is *missing verification*, not a missing format. A new conformance test closes it without touching any owned/watched surface — the lowest-risk slice that actually moves the blocker. Mirrors W1's "new files only" precedent.
- **Explicit case names, not `by_tag("round_trip")`.** Pins exactly the shapes whose deltas were measured (mirrors `test_conformance_export_roundtrip._EXACT_CASES`), so a future non-deterministic `round_trip` case cannot silently flake the float-exact link B.
- **Local tolerance literals, reused mapper.** Tolerances are local (no coupling to a constant W4 may retune); only the non-trivial, identity-keyed `_final_test_pred_by_sample` mapper is reused from `_conformance_helpers` (as the sibling export test already does).
- **dag-ml worktree untouched.** The `.n4a` path is Python-only; no Rust change was warranted, so `refactor/W3-native-export-dagml` stays clean (no cross-boundary reach — consistent with the cross-cutting rule).

---

## 4. Files changed

```text
tests/integration/parity/test_conformance_n4a_bundle_parity.py   +156 (NEW)
```

No existing file modified → zero regression surface for the rest of the suite (collection verified).

## 5. Handoff — what remains on B-011

This slice closes **one** of the three B-011 remainders. Still open (keep final `LOCK-PYREF` open):

1. **Native `.n4a` export (P3).** Make `RunResult.export(format="n4a")` build the bundle from the **captured native refit artifact** for a single-artifact dag-ml run (the way `export_model`/`_dagml_native_export_model` already does for joblib), eliminating the legacy-refit bridge and the stochastic caveat for the common case. This is a **bundle-format change on the watched `.n4a` surface** → needs a `DEC-*` + coordination with `L2`/`L4`/`L5`, not a Python shim. When it lands, this test's link **A** becomes a *native* (not bridge) assertion and its tolerance should tighten toward `1e-6` — the test is already structured to catch that convergence.
2. **Error/refusal parity legacy vs dag-ml.** The dag-ml export *refusal* contract is pinned (`test_conformance_export_roundtrip`); a symmetric legacy-vs-dag-ml error-shape comparison for other misuses (no predictions, bad format, …) is a separate focused slice.
3. **Studio route bypass parity (SW8).** Out of scope here (`L12`).

One local commit on `refactor/W3-native-export` (the new test file only); **not pushed**. `refactor/W3-native-export-dagml` left clean. Sync board not edited.
