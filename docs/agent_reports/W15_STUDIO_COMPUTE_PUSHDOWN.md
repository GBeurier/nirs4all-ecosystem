# W15 — Studio compute push-down, first slice (B-017)

**Date:** 2026-07-01
**Agent:** W15
**Worktree:** `/home/delete/nirs4all/_worktrees/W15-studio-compute`
**Branch / base:** `refactor/W15-studio-compute-pushdown` (from `refactor/integration-studio`, tip `2ac5abe`)
**Commit:** `7c131d53c958e5549e1bf139ef4b98723837f9cb` (`7c131d5`) — local only, **not pushed**
**Review:** Codex `codex-cli 0.142.4` — verdict **SHIP** (no blocking findings; independently re-checked via CodeGraph)

---

## 1. Goal & scope

Start B-017 deep compute push-down with a **small production slice** that removes
duplicated / divergent Studio metric-math behavior in favor of library helpers,
preferring the **prediction-metric** and **result-analysis** seams over broad UI
work. Owned areas: `api/predict.py`, `api/metrics_computer.py`
(actual path `api/shared/metrics_computer.py`), focused tests. Explicitly avoid
`api/runs.py` engine-record behavior (owned by W14).

## 2. What shipped (the slice)

**Seam:** prediction metrics in `api/predict.py::_run_prediction`.

`predict.py` had already been moved off a Studio-side sklearn re-roll onto the
library's `nirs4all.core.metrics.eval_multi` (B-017 "V1", commit `5cb98f2`). But
it still **hardcoded the task type**:

```python
# before
eval_multi = get_cached("eval_multi")
raw_metrics = eval_multi(y_true_arr, y_pred_arr, "regression")
```

That is a residual piece of **metric-domain logic decided inside Studio**: it
assumes every prediction is regression. Consequences:

- A **classification** model was scored with `rmse`/`r2`/`mae`/`rpd` computed on
  its integer **class labels** — meaningless, misleading numbers surfaced in the
  UI.
- It **diverged** from the rest of Studio and the engine. `api/evaluation.py`
  (already shipped) resolves the task type with the library detector
  `nirs4all.core.task_detection.detect_task_type`; so does the engine's
  `score_calculator`. `predict.py` was the odd one out.

**Change** — defer the task-type decision to the same library helper, mirroring
`evaluation.py` exactly:

```python
# after
task_type = get_cached("detect_task_type")(y_true_arr).value
eval_multi = get_cached("eval_multi")
raw_metrics = eval_multi(y_true_arr, y_pred_arr, task_type)
```

Now the metric **set** and the metric **values** are 100% library-determined;
Studio makes no task-type assumption of its own. The block stays inside the
existing best-effort `try/except Exception → log, metrics=None`, so any detector
failure (e.g. all-NaN targets) degrades gracefully exactly as a metric error did
before.

Files:
- `api/predict.py` — the two-line push-down + comment (why detection, not a
  constant).
- `tests/test_predict_metrics.py` — extended (see §4).

Net diff: **2 files, +167 / −26** (most of it tests).

## 3. Why this is the right first slice (and what it is *not*)

- It is in the **preferred prediction-metric seam**, is a **real production code
  path** (not a test-only or cosmetic change), and it **removes** a Studio-local
  metric assumption rather than adding a shim.
- It is **minimal and low-risk**: it reuses helpers already cached in
  `api/lazy_imports.py` (`detect_task_type`, `eval_multi`) and an
  already-shipped in-repo pattern (`evaluation.py`). No new dependencies, no
  schema change, no frontend coupling.
- It does **not** touch `api/runs.py` / `api/runtime_engine.py` engine-record
  behavior (W14's territory), does not add response fields, and does not force a
  bad push-down of the spectral-descriptor compute that has no library home yet
  (see §6).

### Known, intentional behavior nuance

`detect_task_type` inspects the **targets only**: integer-valued (or `[0,1]`)
targets with few unique values are classified as classification. So an
**integer-valued regression** target can now be detected as classification and
receive classification metrics, whereas the old hardcode always produced
regression metrics. This is **accepted on purpose**: the whole point of the
push-down is library-consistency, and `api/evaluation.py` + the engine already
behave this way. If the detector is ever too aggressive, that is a single
library issue to fix once — not something Studio should special-case. Codex
flagged this as the only semantic change and judged it a non-blocker.

## 4. Tests

`tests/test_predict_metrics.py` (4 tests, all pass):

1. `test_run_prediction_routes_metrics_through_eval_multi` — regression path;
   asserts metrics come from `eval_multi` **and** that the task type handed to
   `eval_multi` is the value the detector returned (not a constant), **and** that
   detection ran on the ground-truth (same contract as `evaluation.py`).
2. `test_run_prediction_uses_detected_classification_task_type` — **the bug-fix
   test**: detector returns `binary_classification`; asserts `eval_multi` is
   called with `binary_classification` and a classification metric dict
   (`accuracy`/`f1`/…) flows through with **no `rmse`/`r2` leakage**.
3. `test_run_prediction_metrics_none_when_task_detection_fails` — detector raises
   (all-NaN); asserts `metrics is None` but predictions are still returned
   (best-effort block is never fatal); `eval_multi` must not be reached.
4. `test_run_prediction_without_y_true_has_no_metrics` — unchanged contract.

**Import-order guard:** `api.predict`'s first import is
`from .lazy_imports import get_cached`, which makes `lazy_imports` the entry
point of a **pre-existing** `lazy_imports ⇄ api.shared` import cycle
(`lazy_imports` L16 `from .shared.logger import get_logger` → `api/shared/__init__.py`
→ `pipeline_service` → `from ..lazy_imports import get_cached`, not yet defined).
The app avoids it because normal startup imports `api.shared` first; the full
pytest suite avoids it because an earlier-collected module loads `api.shared`
first. To make the file runnable **in isolation**, the test now imports
`api.shared` before `api.predict` (exactly what the app does at startup). This is
a test-only, self-documenting guard; the cycle itself lives in
`lazy_imports.py`/`api/shared/` which are **out of this slice's scope** (core
infra, shared with other agents) — flagged here for a future infra pass.

## 5. Validation & environment

- **Backend test env exists** and was used: `../../nirs4all-studio/.venv`
  (fastapi 0.128.0, pytest 9.0.2, numpy 2.3.5). The supervisor's system
  `python3` has **no fastapi/pytest** (as the Wave-2C brief warned); the sibling
  `../../nirs4all/.venv` also lacks fastapi. The studio `.venv` is the correct
  runner.
- `pytest tests/test_predict_metrics.py` → **4 passed**.
- `python -m compileall api/predict.py tests/test_predict_metrics.py` → OK.
- `ruff 0.14.14 check` (repo `ruff.toml`, line-length 220) on both files → clean
  (import block auto-sorted; guard order preserved: `import api.shared` precedes
  `from api import predict`).
- **Real-library routing sanity** (against the actual
  `/home/delete/nirs4all/nirs4all`, which the studio venv resolves on `sys.path`):
  the exact two lines `predict.py` now uses were run for continuous
  (→`regression`, keys incl. `rmse`/`r2`), binary-int (→`binary_classification`,
  keys incl. `accuracy`, no `rmse`), and 3-class-int (→`multiclass_classification`)
  targets — all correct. This proves the push-down works against the real
  helpers, not just the unit-test fakes.
- No other test references the predict path (`grep` over `tests/`), so no
  regression surface beyond the file edited.

## 6. Trapped compute that remains (B-017 backlog)

Per the brief, an explicit inventory of duplicated/local metric-math still living
in Studio and **why it was not pushed down in this slice**. Primary residence:
`api/shared/metrics_computer.py` (`MetricsComputer`, ~780 LOC), consumed by the
Playground (`api/playground/routes.py`, `api/playground/charts.py`).

| Group | Studio symbols | Library equivalent? | Verdict / why still trapped |
|---|---|---|---|
| **Prediction metrics** | `api/predict.py` metric block | `eval_multi` + `detect_task_type` | **DONE (this slice).** No trapped prediction-metric compute remains in `predict.py`. |
| **Chemometric** | `hotelling_t2`, `q_residual`, `leverage`, `distance_to_centroid`, `lof_score` | `XOutlierFilter`, `HighLeverageFilter` (`nirs4all.operators.filters`) | **Already delegated** (pre-existing). Good; no action. |
| **Quality counts** | `nan_count`, `inf_count`, `saturation_count`, `zero_count` (per-sample **integer counts**) | `SpectralQualityFilter` exposes **ratios + boolean masks** (`get_quality_breakdown`, `_quality_stats_`) for *filtering decisions*, not per-sample counts for *UI coloring* | **Trapped — contract mismatch.** The library gives ratios/masks (e.g. `nan_ratio`, `has_inf`), Studio's Playground colors by raw counts. The existing code comment ("simple numpy, **not using SpectralQualityFilter**") is deliberate. Clean push-down needs the library to grow a per-sample **count** accessor (or Studio to switch its UI to ratios). Do **not** force it. |
| **Amplitude / Energy / Shape / Noise descriptors** | `global_min/max`, `dynamic_range`, `mean_intensity`, `l2_norm`, `rms_energy`, `auc`, `abs_auc`, `baseline_slope/offset`, `peak_count`, `peak_prominence_max`, `hf_variance`, `snr_estimate`, `smoothness` | **None** — no canonical per-sample spectral-descriptor module in `nirs4all` today | **Trapped — no library home.** These are real duplicated math but pushing them down requires **adding a new library module** (e.g. `nirs4all.analysis.descriptors` / a `SpectralDescriptors` helper). That is a `nirs4all`-repo change, out of scope for a Studio-repo first slice. Strongest candidate for the *next* B-017 increment: land the library module first, then delegate here (mirroring the chemometric pattern). |
| **Per-metric stats** | `MetricsComputer.get_metric_stats` (min/max/mean/std/**p5..p95** percentiles) | `nirs4all.core.metrics.get_stats` returns a **different** set (`nsample/mean/median/min/max/sd/cv`, **no percentiles**) | **Trapped — not equivalent.** UI histogram percentiles aren't in the library helper. Would need `get_stats` extended (or a new `describe`-style helper) before delegating. |
| **UI distances** | `get_similar_samples`, `compute_pairwise_distances` (euclidean/manhattan/cosine/spectral_angle/correlation/mahalanobis/pca), `compute_repetition_variance` | None (and these are marked "UI-specific" in-code) | **Trapped, lower priority.** Genuinely interactive Playground features; not duplicated elsewhere today. Could later move to a library `distances`/`repetition` helper, but no divergence risk right now. |

**Summary:** the prediction-metric seam is now fully pushed down. The remaining
trapped compute in `metrics_computer.py` is **blocked on library surface that
does not exist yet** (per-sample spectral descriptors, per-sample quality counts,
percentile stats). The correct next B-017 move is a **`nirs4all`-side** helper
module for spectral descriptors, after which Studio can delegate exactly as it
already does for the chemometric metrics — not a Studio-only re-roll.

## 7. Constraints honored

- Worked only in the assigned worktree; wrote this report to
  `nirs4all-ecosystem/docs/agent_reports/`.
- Did **not** touch `api/runs.py` / `api/runtime_engine.py` engine-record
  behavior (W14).
- Did not edit `PARALLEL_REFACTORING_SYNC.md`.
- Committed locally on the agent branch; **did not push**.
- No dead code / compat shims / speculative abstraction; single focused change.

## 8. Handoffs / follow-ups

1. **B-017 next increment (library-side):** add a `nirs4all` per-sample
   spectral-descriptor helper (amplitude/energy/shape/noise), then delegate
   `MetricsComputer._compute_metric` to it. Optionally add a per-sample
   quality-**count** accessor to `SpectralQualityFilter` and percentile support
   to `get_stats`, unblocking the two other trapped groups.
2. **Infra (out of this slice's scope):** the `lazy_imports ⇄ api.shared` import
   cycle makes any `api.*` module that imports `lazy_imports` first fail to
   import in isolation. Worth a small infra fix (break the cycle so single-file
   test/imports don't depend on collection order).
