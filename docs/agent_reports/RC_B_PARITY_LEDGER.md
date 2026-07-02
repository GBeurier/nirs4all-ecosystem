# RC-B — Python Parity Ledger, Strict Gate & xfail/skip/tolerance Accounting

Date: 2026-07-02
Lane: RC-B (parity ledger / gate / compatibility docs / xfail-skip accounting)
Worktree: `_worktrees/RC-v1-nirs4all-python` (branch `rc/v1-full-refactor-python`, at `aab640c9`)
Spec of record: `SW5_PYREF_COMPATIBILITY_LEDGER_spec.md`

## Objective (restated)

Turn the `810 passed / 30 skipped / 11 xfailed` parity state into **auditable,
enforceable release debt** — explicit compatibility docs, machine-readable
accounting, and a strict gate that fails on **untracked** xfails/skips/tolerance
overrides — without blessing the debt as production-ready and without editing
runtime algorithm code (RC-C/RC-D own fixes).

## Starting state (what already existed)

The ledger was already mature and bidirectional:

- `docs/compatibility.md` + `docs/compatibility.json` — human + machine ledger
  (tolerance bands §A, 3-tier authority §B, orthogonal axes §C, cross-engine
  surfaces §D, coverage meter §E, invariants §F).
- `_authority.py` reconciles the JSON against the **live parity constants**
  (`KNOWN_DIVERGENCES`, `NUM_PREDICTIONS_DIVERGENCE`, `Y_PRED_TOL_OVERRIDES`,
  `SAME_WINNER_CASES`, `EXPECTED_FALLBACK`, registry `skip_kind`), driven by
  `test_compatibility_ledger.py`. `coverage_meter.py` statically classifies cases.

**The gap:** every check reconciles the JSON against the *ledgered structures*.
Nothing catches debt added **directly in a test body** — a bare
`pytest.mark.xfail(reason="TODO")`, a `pytest.skip("flaky")`, or a loosened
`atol=1e-1` — which never touches those constants. That is exactly the
"untracked" surface the task targets.

## What I built

A **static `ast` gate** over `tests/integration/parity/*.py` (line-number
independent; keys on module + reason template + tolerance value), plus a
machine-readable policy face and a corrected tolerance band.

### Files modified (owned)
- `docs/compatibility.json` — added `marker_policy` (v1: xfail sanctioned module,
  9-entry skip taxonomy with kinds, tolerance allowlist source); corrected the
  `per_case_tight` band `abs_tol` `1e-6 → 1e-3`.
- `docs/compatibility.md` — corrected §A.2/§A.3 `per_case_tight`; added §G
  (marker & tolerance debt gate) + invariant F.6; refreshed the reconciliation
  header.
- `tests/integration/parity/_authority.py` — added `_validate_per_case_tight_band`
  (binds the band to the live `baseline_vertical_slice.metric_tolerances` so it
  can't drift again) and wired `validate_marker_policy` into the ledger check.
- `tests/integration/parity/test_compatibility_ledger.py` — added an explicit
  `marker_policy` schema assertion.

### Files added (owned)
- `tests/integration/parity/_marker_audit.py` — the scanner + CLI. Three **closed**
  policies, each failing on the first exception:
  1. **xfail containment** — `pytest.mark.xfail`/`pytest.xfail` only in
     `test_conformance_dual_engine.py` (the two `_params()` marks = the 11 xfails).
  2. **skip taxonomy** — every skip maps to one of 9 sanctioned categories
     (`registry_skip`, `optional_env_*`, `runtime_na`, `baseline_capture`,
     `lockdrop_empty`); an unclassifiable skip fails.
  3. **tolerance band** — every explicit `atol/rtol/abs/rel` kwarg, `*_TOL`
     constant, and `metric_tolerances`/`Y_PRED_TOL_OVERRIDES` value must equal a
     published band (`tolerance_bands[].abs_tol` — the ledger *is* the allowlist);
     a value in a **negative** assertion (`assert not allclose` / `!= approx`) is a
     divergence floor and is exempt.
- `tests/integration/parity/test_marker_audit.py` — live-tree gate + **negative
  self-tests** that prove the gate flags injected debt.

## Ledger inaccuracy found & fixed

The ledger claimed `per_case_tight = 1e-6` "pinned by `baseline_vertical_slice`".
The case actually pins `metric_tolerances={"rmse": 1e-3, "r2": 1e-3}` (author
comment confirms `1e-3` intent; the "tight" is the *secondary r2* guard that
caught the `best_r2` re-rank bug, not a smaller magnitude). Corrected to `1e-3`
and **bound to the live case value** in `_authority.py`, so the doc and the code
can never diverge again. This changes no runtime behavior and no tolerance
actually enforced — it only makes the ledger truthful.

## Tests run (exact results)

All from `_worktrees/RC-v1-nirs4all-python`, `../../nirs4all/.venv/bin/python` (3.11.15):

- `pytest tests/integration/parity/test_compatibility_ledger.py test_marker_audit.py -q`
  → **14 passed in 0.66s** (3 ledger + 11 marker, incl. negative self-tests).
- `python -m tests.integration.parity._marker_audit --check` → **exit 0**.
  Live inventory (static call sites @ `aab640c9`): xfail **2** (both sanctioned),
  skip **131** (registry_skip 8, optional_env_import 13, optional_env_dagml_cli 96,
  optional_env_dependency 1, optional_env_sibling 1, optional_env_methods 1,
  runtime_na 8, baseline_capture 2, lockdrop_empty 1 — **0 untracked**),
  tolerance **42** (all in-band or negative-guard).
- `python -m tests.integration.parity.coverage_meter --check` → **OK
  (fallback=0, target=0)**.
- `ruff check` (all 4 touched py files) → **All checks passed**.
- `mypy tests/integration/parity/_marker_audit.py` → **Success: no issues** (the
  module imports only stdlib). CI's `mypy nirs4all` scope is unaffected — I touched
  no package files.
- `pytest tests/integration/parity/ --collect-only -q` → **863 collected, no
  import errors** (confirms the `_authority → _marker_audit` import and the new
  test module are collection-clean).

Negative-path proof: fed the auditor a rogue module (`@pytest.mark.xfail(reason=
'TODO')`, `pytest.skip('flaky')`, `atol=1e-1`, and a negated `assert not
allclose(atol=2e-1)`); it flagged the xfail, the skip, and the positive `1e-1`,
and correctly **exempted** the negative guard. Encoded as
`test_gate_flags_*` / `test_gate_classifies_each_sanctioned_skip_shape`.

## How the headline maps (accounting)

- **11 xfailed** — exact and fully ledgered: `KNOWN_DIVERGENCES` (9) + registry
  `legacy_bug` (2), applied only in the sanctioned builder. The gate fails on a 12th.
- **30 skipped** — environment-dependent (optional bins / `dag-ml-cli` presence),
  decomposing entirely into the G.1 taxonomy above. Only `registry_skip` (the 4
  §C.2 fixture/unknown_semantics cases) is genuine coverage debt, and it is pinned
  in `coverage_skips`. The gate guarantees no skip is off-taxonomy.
- **tolerance overrides** — 42 literals, each a published band or a divergence
  floor; a new looser value fails.

## Decisions

- **Gate = static AST, not per-run counts.** Robust to edits, needs no engine run,
  and directly implements "fails on untracked …". Consistent with the repo's
  manifest-reconciliation style (`_authority.py`, `coverage_meter.py`).
- **The ledger's bands are the tolerance allowlist** (derived, not hard-coded), so
  adding a band is a documented decision and any off-band test tolerance fails.
- **`runtime_na` skips are sanctioned, not failed** — they gate a cross-engine
  comparison to its applicable inputs (single-artifact native run); with
  `fallback=0` the fallback branch does not fire for covered cases. They hide no
  divergence. Recorded as `runtime_precondition`, not `tracked_debt`.
- **Did not expand any xfail/skip; did not touch runtime.** Per RC-B scope.

## Risks & open questions

- **Concurrent lane in the same worktree.** During this pass, 7 `nirs4all/**`
  runtime files (`controllers/data/branch.py`, `merge.py`, `pipeline/bundle/{generator,loader}.py`,
  `pipeline/config/pipeline_config.py`, `pipeline/resolver.py`, `pipeline/retrainer.py`)
  became modified — these are **RC-C's** work, not mine. I staged/committed nothing.
  If RC-C's fixes converge a `KNOWN_DIVERGENCES` case (XPASS) or promote a
  `registry_skip`, the pre-existing `_authority` reconciliation flags the JSON
  drift; they must update `compatibility.json` accordingly. My marker/tolerance
  gate is orthogonal (scans test files, unaffected by runtime edits).
- **Open debt remains open.** The 11 xfails and 4 `registry_skip` cases are still
  release debt owned by RC-C/RC-D — §G only prevents silent growth. Not blessed.
- **`optional_env_*` skips are legitimate but env-shaped.** In a release proof the
  gate should run where `dag-ml-cli` is built and optional deps installed, so those
  skips resolve to real assertions (otherwise the debt-free verdict is partial).
- **Handoff to RC-C/RC-D (not fixed here, by scope):** the 9 `KNOWN_DIVERGENCES`
  (2 permanent rep-OOF semantics, 7 RNG/Optuna), the 2 `legacy_bug` xfails
  (`branch_separation_by_tag`/`_by_filter`), and the 3 fixture + 1
  `unknown_semantics` skips (`refit_params_use_all_partitions`).

## Full parity needed?

**No** for this lane. The gate is static + targeted-test only; I ran no full
parity (per the cost constraint). A full `pytest tests/integration/parity/` remains
the coordinator/RC-I call after RC-C/RC-D batches — and should be run in an
environment with `dag-ml-cli` + optional deps so the `optional_env_*` skips
collapse into real parity assertions.
