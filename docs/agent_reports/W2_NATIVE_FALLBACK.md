# W2 — Native fallback elimination (B-010 / DML-002)

**Agent:** W2 (Wave-2B native-lowering) · **Date:** 2026-07-01 · **Lane:** `L5` dag-ml runtime host-bridge
**Branch:** `refactor/W2-fallback-native` (worktree `_worktrees/W2-nirs4all`), based on committed L17 tip `1e4d8043`.
**Blocker:** `B-010` — shrink `EXPECTED_FALLBACK` toward empty (`LOCK-DROP`/`L19` gate `D1`).
**Owned surface:** `nirs4all/pipeline/dagml/{detect,run_paths,run_backend}.py`, the `EXPECTED_FALLBACK` allowlist, and `docs/compatibility.json` `expected_fallback` rows.
**Did NOT touch:** `dag-ml` (no Rust edits), `coverage_meter` *semantics* (W1), `tolerance_bands`/`authority` (W4), `PARALLEL_REFACTORING_SYNC.md`.

---

## 0. TL;DR

- **`EXPECTED_FALLBACK`: 11 → 10.** One shape migrated to native dag-ml at **full parity**: `preprocessing_explicit_keyword`.
- The fix is a **pure host-side normalization** in the owned file `run_backend.py`: unwrap a modifier-free `{"preprocessing": <op>}` wrapper to its bare operator before detection/dispatch, so the already-native concrete path runs it. **No `dag-ml` change** — the Rust runtime already runs a bare `SNV()`/`MSC()` concrete pipeline at parity (the baseline cases prove it).
- The other 10 cases were **investigated, not migrated** this slice. Each has its exact rejection point captured below; two (`fit_on_all`, `force_layout`) are **deliberately kept fallback** because the modifier changes fit-scope/layout semantics the native X-chain cannot represent — migrating them would be lying about parity. The 8 branch/merge/multi-source cases need genuine host-bridge lowering work (some with a likely Rust-core gap) and are scoped for follow-up slices.
- Gates green: targeted dual-engine **parity** (native), the never-xfailed **boundary**, the **compatibility-ledger** snapshot, `ruff`, `py_compile`, `json.tool`.

---

## 1. What shipped

### The one genuine, parity-safe migration: `preprocessing_explicit_keyword`

Pipeline: `[{"preprocessing": SNV()}, {"preprocessing": MSC()}, ShuffleSplit(3), {"model": PLSRegression(10)}]`.

**Why it fell back (measured, via `run_via_dagml` raising the raw catchable error):**
`dagml_bridge._step_to_dsl` lowers only bare operator instances + the structural keywords
(`model`/`y_processing`/`concat_transform`/`feature_augmentation`/generators). A `{"preprocessing": op}`
dict hits its fail-loud `NotImplementedError("does not yet serialize step keyword(s) ['preprocessing']")`,
so `run(engine="dag-ml")` transparently re-ran legacy.

**The fix (`nirs4all/pipeline/dagml/run_backend.py`, owned):**
`_unwrap_preprocessing_steps()` rewrites a step whose key set is **exactly** `{"preprocessing"}` to its
bare operator, applied at the top of `_dispatch_run` **after** `config_name`/`variant_config_names`/
`variant_model_params` are derived from the ORIGINAL pipeline (so the dag-ml `RunResult` keeps the
legacy-matching config name) and **before** detection/dispatch/lowering. Legacy's `StepParser` treats
`{"preprocessing": op}` as a pure synonym for a bare transform (`RESERVED_KEYWORDS` never lists
`preprocessing`), so the unwrapped pipeline is numerically identical — the operator fits/transforms the
same on the native X-chain. `_attach_export_spec` still sees the original wrapped pipeline (the unwrap is
local to `_dispatch_run`), so the `.n4a` legacy-refit replay is unchanged.

**Scope guard — never a silent-wrong native run:** a wrapper carrying ANY other key
(`fit_on_all`/`force_layout`/`na_policy`/`fill_value`/`name`) is left untouched, so it still fails loud →
legacy. The unwrap is the smallest faithful change: it touches only the canonical synonym, not the
modifier-bearing forms.

### Ledger mirror

- `test_conformance_dual_engine.EXPECTED_FALLBACK`: dropped `preprocessing_explicit_keyword` (comment updated).
- `docs/compatibility.json` `expected_fallback[]`: dropped the matching row.
- `docs/compatibility.json` `coverage_meter`: the two **derived** integers updated to stay self-consistent
  with the live authority — `fallback` 11→10, `native` 76→77. These are mechanically computed by
  `_authority._validate_coverage_meter` from `len(EXPECTED_FALLBACK)` (which W2 owns); the meter's
  *structure/semantics* are W1's. **W1 coordination note:** at land, W1's `coverage_meter` runner and W2's
  `expected_fallback`/allowlist reconcile through `test_compatibility_ledger` (the snapshot enforces
  equality); the only W2 touch to the meter block is these two forced derived counts.

---

## 2. Evidence (gates)

All run with the sibling venv `/home/delete/nirs4all/nirs4all/.venv` (matplotlib 3.11.0, dag_ml importable).

```text
# Targeted parity + boundary + ledger (the cases this slice can affect)
pytest tests/integration/parity/test_conformance_dual_engine.py \
       tests/integration/parity/test_compatibility_ledger.py -p no:cacheprovider -q \
       -k "preprocessing_explicit_keyword or preprocessing_fit_on_all or preprocessing_force_layout_2d or compatibility"
  → 8 passed, 176 deselected
    · test_dual_engine_conformance[preprocessing_explicit_keyword]  → NATIVE, full parity (score+num_predictions+RunResult contract+y_pred)
    · test_dual_engine_conformance[preprocessing_fit_on_all]        → fallback boundary (unchanged)
    · test_dual_engine_conformance[preprocessing_force_layout_2d]   → fallback boundary (unchanged)
    · test_native_fallback_boundary[preprocessing_explicit_keyword] → asserts NATIVE (left allowlist)
    · test_native_fallback_boundary[preprocessing_fit_on_all]       → asserts fallback
    · test_native_fallback_boundary[preprocessing_force_layout_2d]  → asserts fallback
    · test_compatibility_json_is_valid_json / _matches_live_parity_authority → pass

# Full never-xfailed boundary over all 87 runnable cases (regression guard)
pytest tests/integration/parity/test_conformance_dual_engine.py::test_native_fallback_boundary -p no:cacheprovider -q
  → 87 passed in 315.37s (0:05:15)

# Lint / compile / schema
ruff check nirs4all/pipeline/dagml/run_backend.py tests/integration/parity/test_conformance_dual_engine.py  → All checks passed
python -m py_compile <both files>                                                                            → OK
python -m json.tool docs/compatibility.json                                                                  → valid
```

**No-collateral proof:** the only parity cases anywhere that use a `{"preprocessing": ...}` wrapper are the
3 preprocessing cases themselves (`rg '"preprocessing"\s*:' tests/integration/parity/cases_*.py` → 4 hits,
all in `cases_tags_exclude.py`). No other case can change native/fallback status from this unwrap.

---

## 3. The remaining 10 — exact rejection points + disposition

Captured empirically by calling `run_via_dagml(case.pipeline, dataset)` directly (which raises the raw
catchable error the public `run()` swallows into a legacy fallback):

| Case | Raw rejection | Disposition |
|---|---|---|
| `preprocessing_fit_on_all` | `_step_to_dsl` unhandled `['fit_on_all','preprocessing']` | **Keep fallback.** `fit_on_all` fits the transform on train+val+test; the native X-chain fits per-fold-train. Not natively representable → migrating would break parity (a real fit-scope divergence for a stateful transform). |
| `preprocessing_force_layout_2d` | `_step_to_dsl` unhandled `['force_layout','preprocessing']` | **Keep fallback.** `force_layout` pins the input tensor layout; no native representation. (For SNV on 2D data it is a no-op, but a generic unwrap would silently drop a layout contract that matters for 3D models — fail-loud is correct.) |
| `branch_dup_three_way_merge_predictions` | `_step_to_dsl` unhandled `['branch']` | Follow-up. Named-**dict** duplication branch + `{"merge":"predictions"}` + Ridge meta = stacking. `_detect_stacking_branch` only accepts the **list** form `{"branch":[[A],[B]]}`; the Rust stacking handler exists, so this is host-side detection-generalization (dict→ordered list of bodies). Medium risk (deterministic branch order + full parity). |
| `multi_source_per_source_models_stacking` | `_step_to_dsl` unhandled `['branch']` | Follow-up. `by_source` branch with a model + `{"merge":"predictions"}` = per-source stacking. `_detect_by_source_branch` only accepts the **fusion** (mean) merge, not predictions/meta. Host-side work; reuses the stacking handler. |
| `branch_dup_two_way_merge_features` | `_step_to_dsl` unhandled `['branch']` | Follow-up. Named branches (bare preproc, **no** per-branch model) + `{"merge":"features"}` + PLSR. Candidate host rewrite into a single `concat_transform` of `[SNV, MSC]` (already native), pending parity proof. |
| `branch_dup_merge_all` | `_step_to_dsl` unhandled `['branch']` | Follow-up. `{"merge":"all"}` = feature-concat **and** prediction-stacking simultaneously. Needs both mechanisms wired; verify the Rust runtime exposes a combined "all" merge before claiming native (possible core gap). |
| `branch_dup_named_with_metamodel` | `DagMlUnsupported`: 2 top-level `{model}` steps | Follow-up / likely core gap. MetaModel + a second Ridge, a **structured** per-branch best-by-rmse selector merge (`output_as: features`), and a `concat_transform` inside a branch. Richest shape; `_reject_multi_model` + structured-merge selectors. Defer; document core needs before attempting. |
| `multi_source_by_source_branch_shared_preproc` | `_step_to_dsl` unhandled `['branch']` | Follow-up. `by_source` body is **bare preproc** (no model) + `{"merge":"concat"}` = per-source preprocessing then feature-concat then model. `_detect_by_source_branch` requires a model in the body + fusion merge; needs a per-source-preproc→concat lowering. |
| `multi_source_by_source_branch_distinct_preproc` | `_step_to_dsl` unhandled `['branch']` | Follow-up. As above but the **per-source DICT** body (`{source_0:[SNV], source_1:[MSC], source_2:[FD]}`) — explicitly a later slice per `_detect_by_source_branch` docstring. |
| `multi_source_sources_concat_then_rf` | `_step_to_dsl` unhandled `['merge']` | Follow-up. `{"merge": {"sources": "concat"}}` source-fusion-before-model is not lowered. Needs the source-concat merge token wired to the native multi-source collapse. |

**Working rule honored (mission + cross-cutting):** I did **not** edit `dag-ml`. For the cases above that may
need a Rust feature (`merge:"all"`, structured selectors, source-concat), the correct path is a `DEC-*` +
a dag-ml worktree (coordinate W3/W6), not reaching across the boundary — so they are documented here rather
than force-shrunk. Every shrink must keep the **full** dual-engine parity green; turning a green boundary
case into a red parity case (by declaring native without parity) would be worse than leaving it fallback.

---

## 4. Files changed

```text
nirs4all/pipeline/dagml/run_backend.py                       +29   (_unwrap_preprocessing_steps + call in _dispatch_run)
tests/integration/parity/test_conformance_dual_engine.py     +5 -2 (EXPECTED_FALLBACK: drop preprocessing_explicit_keyword)
docs/compatibility.json                                      +2 -7 (expected_fallback row drop + derived coverage_meter ints)
```

No edits to `detect.py` / `run_paths.py` were needed for this slice (the unwrap lives entirely in
`run_backend._dispatch_run`); both remain owned by W2 for the follow-up branch/multi-source slices.

## 5. Handoff

- `EXPECTED_FALLBACK` now has **10** entries; `coverage_meter.fallback == 10`, `native == 77`,
  `expected_fallback_target == 0` (the `L19`/`D1` target is still non-empty — 8 branch/merge/multi-source
  shapes + 2 deliberately-fallback modifier shapes remain).
- The 8 branch/merge/multi-source cases are the real remaining DML-002 work; §3 gives each one's exact
  rejection and the host-bridge generalization (or suspected core gap) needed. They are the natural next
  slice(s) and stay within the W2-owned `detect.py`/`run_paths.py`/`run_backend.py` surface.
- The 2 modifier cases (`fit_on_all`, `force_layout`) should remain fallback until the native X-chain gains
  a faithful fit-scope / layout representation — they are not coverage debt, they are correct fail-loud
  refusals.
- One local commit made on `refactor/W2-fallback-native`: `2f2f9c40 feat(dagml): lower explicit preprocessing fallback`; **not pushed**. Sync board not edited.
