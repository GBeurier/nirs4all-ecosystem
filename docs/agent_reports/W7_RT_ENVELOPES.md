# W7 — Runtime envelopes + explicit Python fallback (B-018 / L10) — IMPLEMENTED

**Agent:** W7 (runtime envelope, Wave-2B) · **Date:** 2026-07-01 · **Mode:** implementation.
**Branch:** `refactor/W7-rt-envelopes` (nirs4all worktree `_worktrees/W7-nirs4all`, off committed `refactor/L17-pyref`) + the `nirs4all-ecosystem` `docs/` tree.
**Blocker:** `B-018` (explicit `RtError`). **Spec consumed:** `SW8_RT_STUDIO_IMPL_spec.md` §2/§5, `RT_spec.md` §RT-002/§RT-003, `CAP_spec.md` §5 (cause vocab), `RV10_NEXT_WAVE_PLAN.md` W7 prompt.
**Scope honored:** NO change to `RunResult` fields, the `.n4a` bundle, or the native results format (all 0.9.x-stable). `api/result.py` touched **method-level only** (W3 owns export methods). Did NOT edit `PARALLEL_REFACTORING_SYNC.md`.

---

## 0. TL;DR

The runtime envelopes are **thin, pure projections** over surfaces that already exist on the dag-ml backend — they add **zero new dag-ml fields** and never recompute a score, exactly per `LOCK-RT`. Five additive pieces landed, all gated green:

1. **`nirs4all/pipeline/dagml/rt.py`** (new) — `RtResult` / `RtRunRequest` / `RtError` + the pure projection helpers `from_native_dir` / `from_run_result` / `from_dagml_error`.
2. **`nirs4all/runtime.py`** (new) — the public seam: `list_controller_manifests()`, `from_native_dir()`, and the `RtResult`/`RtRunRequest`/`RtError` re-exports, so Studio/Web/CLI never import the private `pipeline.dagml` package.
3. **`RunResult.to_rt_result()`** — additive method on `api/result.py` (method-level only).
4. **`api/run.py`** — `allow_fallback: bool = True`: the default still warns + degrades but now **attaches a structured `RtError` diagnostic**; `allow_fallback=False` **raises `RtError`** instead of degrading. Legacy default preserved (LOCK-DROP).
5. **`nirs4all-ecosystem/docs/contracts/runtime/{rt_result,rt_run_request,rt_error}.v1.schema.json`** (new dir) — the wire schemas, `$ref`-ing the dag-ml `score_set`/`selection_decision` contracts; cause vocab = CAP-004.

---

## 1. What was implemented (file-by-file)

### 1.1 `nirs4all/pipeline/dagml/rt.py` (new, ~335 LOC)
The Python projection, placed beside its four inputs (`native_results.py`, `result.py`, `errors.py`, `run_backend.py`).

- **`RtError(Exception)`** — `{ verb, cause, message, mitigation?, unsupported_capability?, portable_level? }`. Raisable AND `to_dict()`-serializable. Deliberately **NOT** a subclass of `DagMlUnsupported`/`NotImplementedError`, so raising it at the RT boundary is not re-caught by the legacy-fallback `except`. `cause` is validated against the coarse RT-003 set `{unsupported_shape, unsupported_capability, unavailable_backend, invalid_request, runtime_error}`. Classmethod **`from_dagml_error(exc, verb)`** is the RT-003 migration table: `DagMlUnavailable → unavailable_backend`, `DagMlUnsupported`/`NotImplementedError → unsupported_shape`, each with a derived `mitigation`.
- **`RtResult`** (`@dataclass`) — `{ schema_version, run_id, plan_id, selection, reports[], predictions[], manifest{engine,fingerprints,capabilities,portable_level,files}, artifacts?, diagnostics? }`. `reports` is **VERBATIM** `score_set.reports[]` (the partition/level/fold_id/variant_id/target join key). Constructors:
  - **`from_native_dir(run_dir)`** — wraps `native_results.read_native_results` (hash-validated read), projects the triple. No recompute.
  - **`from_run_result(rr)`** — reads `rr._dagml_score_set` (`reports` verbatim, `engine="dag-ml"`) for a dag-ml result; for a **legacy** result it produces a sparse envelope (`reports=[]`, `engine` from `per_dataset`) but still carries the predictions projection + any attached `RtError` diagnostics (the "ran legacy because `<cause>`" envelope).
  - `portable_level` is the **CAP-002** classifier slot — carried as an opaque referenced field, `None` in V1 (not computed here).
- **`RtRunRequest`** (`@dataclass`) — `{ pipeline_dsl, dataset_ref, cv, execution_backend, options }`; `execution_backend` (the environment) stays orthogonal to the ML `engine` (which rides in `options`). A thin descriptor the Studio/Web runtimes fill; V1 does not re-route `run()` execution through it.

### 1.2 `nirs4all/runtime.py` (new, public seam)
`list_controller_manifests()` forwards `dagml_bridge.controller_manifests()` verbatim (the static kind-level set — `transform`/`y_transform`/`model`/`prediction_join`/`meta_model` — already shaped to `controller_manifest.v1.schema.json`; the per-operator ledger waits on the CTRL-000 adapter). `from_native_dir()` re-exports `RtResult.from_native_dir`. Also re-exports the three envelope types. This is the **V1 seam only** — not the consolidated `nirs4all/runtime/` namespace or a published package (deferred to GOV/`LOCK-REL`).

### 1.3 `api/result.py` — `RunResult.to_rt_result()` (additive method only)
Returns `RtResult.from_run_result(self)`. Inserted after `get_models()` — a clean public-method region well away from the export methods W3 owns. Pure projection; does not mutate `RunResult` or touch the frozen `.n4a`/native-format surfaces. The fallback diagnostics it reads are a **dynamic `_rt_diagnostics` attribute** (read via `getattr(..., [])`), so **no dataclass field was added** to the shared file — the `api/result.py` change is exactly one method.

### 1.4 `api/run.py` — explicit fallback (`allow_fallback`)
Added `allow_fallback: bool = True` to `run()`. In the `engine="dag-ml"` dispatch, a new `_fallback(exc)` closure classifies the caught signal into an `RtError`:
- `allow_fallback=False` → **raises** the `RtError` (the explicit "no silent fallback" boundary), no warning.
- `allow_fallback=True` (default) → warns with the **unchanged** "falling back to the legacy engine" text (load-bearing for `_conformance_helpers._FALLBACK_WARNING_FRAGMENT`), re-runs legacy, and attaches the `RtError` via `setattr(result, "_rt_diagnostics", [rt_error])` so callers see it on `result.to_rt_result().diagnostics`.

The only signals caught remain `DagMlUnavailable` / `DagMlUnsupported` / `NotImplementedError`; a genuine dag-ml bug still propagates untouched.

### 1.5 Ecosystem schemas (`nirs4all-ecosystem/docs/contracts/runtime/`, new dir)
`rt_result.v1.schema.json`, `rt_run_request.v1.schema.json`, `rt_error.v1.schema.json` (Draft 2020-12). `rt_result` `$ref`s the dag-ml `score_set.v1.schema.json#/$defs/regression_metric_report` (reports verbatim) and `selection_decision.v1.schema.json` (the `selection` anyOf), and its `diagnostics[]` `$ref`s the local `rt_error` schema. `$comment`s flag every `NET-NEW` wrapper field and every CAP-owned token (cause/mitigation/portable_level).

---

## 2. Gates run (all green)

| Gate | Command | Result |
|---|---|---|
| rt.py unit tests | `pytest tests/unit/pipeline/test_rt_envelopes.py` | **15 passed** |
| `allow_fallback=False` raises on EXPECTED_FALLBACK | `pytest tests/integration/parity/test_rt_fallback_strict.py` | **12 passed** (11 allowlist cases → `RtError(cause=unsupported_shape)` + 1 degrade-attaches-diagnostic) |
| schema `json.tool` | `python -m json.tool runtime/*.v1.schema.json` | OK ×3 (+ metaschema `check_schema` ×3) |
| ruff | `ruff check` (all 6 touched files) | All checks passed |
| mypy | `mypy rt.py runtime.py api/run.py api/result.py` | Success: no issues |
| py_compile | all touched modules | OK |

**Cross-checks:** (a) the unit suite's schema-validation tests resolve the dag-ml `$ref`s against the sibling checkout via a `referencing` registry and validate each `to_dict()` — green; (b) a real in-process `run(engine="dag-ml", allow_fallback=False)` of a covered PLS pipeline runs **native** (no spurious `RtError`, `RtResult` carries the 5 real ScoreSet reports, 0 diagnostics), confirming the strict flag does not affect native runs; (c) the EXPECTED_FALLBACK allowlist + case registry are imported from `test_conformance_dual_engine` / `_registry`, so the strict gate and the dual-engine boundary can never drift.

Test env: nirs4all `.venv` (Python 3.11.15, matplotlib 3.11 present → suite collects; `dag_ml 0.2.1` in-process extension available). The worktree is on `sys.path` so the edited package (not the main-checkout editable install) is exercised.

---

## 3. Coordination notes

- **`api/result.py` (2-tenant with W3).** W7 added ONLY `to_rt_result()` (method-level), in the `get_models()` region. The fallback diagnostic uses a dynamic attribute set from `run.py` (no new dataclass field), so W7 added **no field** to the shared file. W3's export/export_model methods (line ~1055+) and `native_results.py` export side are untouched. Recommended landing order (per RV10 §5): W7's additive seam first, then W3 rebases.
- **Envelope home = ecosystem spec (RT_spec Q1 / SW8 §2.4).** Schemas live in `nirs4all-ecosystem/docs/contracts/runtime/`; the published-package home + `nirs4all/runtime/` namespace consolidation stay deferred to GOV/`LOCK-REL`. `nirs4all/runtime.py` is the V1 module seam only.
- **CAP vocab is referenced, never invented (CAP-004 / CAP-002).** `RtError.cause` uses the coarse RT-003 set; `unsupported_capability`/`portable_level` are opaque CAP-owned slots (`portable_level=None` in V1).
- **W8 (Studio) consumes `nirs4all.runtime.list_controller_manifests()`** for `GET /api/operators/manifests`; **W9 (Web)** mirrors `allow_fallback` + the `RtError` surface. **W4 (error-parity)** consumes `RtError.from_dagml_error` as the stable `cause` classifier. None of those are touched here.

## 4. Deferred (out of W7 scope)

- Full `selection_decision` projection (V1 carries the thin `{selected_variant}` from the native manifest), `coordinator_data_plan_envelope` fingerprints (V1 carries `score_set_hash`/`plan_id`/`bundle_id`), and the CAP-002 `portable_level` computation — all are nullable/opaque slots in the schema, ready to fill without a breaking change.
- Studio (`GET /api/operators/manifests`, engine threading/recording) = **W8**; Web `RtError` surfacing + browser smoke = **W9**; the hard "no implicit fallback" cutover (`allow_fallback=False` as default) = `LOCK-DROP`/`L19`.

---

### Evidence (files written)
nirs4all worktree: `nirs4all/pipeline/dagml/rt.py` (new), `nirs4all/runtime.py` (new), `nirs4all/api/result.py` (+`to_rt_result`), `nirs4all/api/run.py` (+`allow_fallback`/`_fallback`/diagnostic), `tests/unit/pipeline/test_rt_envelopes.py` (new), `tests/integration/parity/test_rt_fallback_strict.py` (new).
ecosystem: `docs/contracts/runtime/{rt_result,rt_run_request,rt_error}.v1.schema.json` (new), this report.
