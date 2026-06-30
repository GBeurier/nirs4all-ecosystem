# RV8 — L17 Python parity / PYREF staged-slice review

**Reviewer:** RV8 (read-only)
**Date:** 2026-07-01
**Repo / branch:** `nirs4all` @ `refactor/L17-pyref` (HEAD merge `e41362b4`)
**Scope:** the 8 staged (`git diff --cached`) changes implementing `B-009`, `B-011` (export/error sub-slice), `B-013`, `B-015`; sync-board entries around `LOCK-PYREF` / `B-009` / `B-011` / `B-015`.
**Method:** direct file reads + `git diff --cached` + focused test runs in `.venv` (Python 3.11.15, `nirs4all-methods` 0.98.0 / `n4m` abi 1.22.0 installed). CodeGraph not relied upon.

---

## Disposition (TL;DR)

**APPROVE the staged slice** — the code, tests, and docs are correct, internally consistent, and green. No source edit is required and nothing in the staged content blocks.

**`LOCK-PYREF` must stay `in_progress`** (as the board has it). **One documentation correction is required before final sign-off:** the `B-011` *remaining-scope* line (and the mirroring `L17` "Prochaine tranche") **understates** the residual L17 work relative to the ledger's own §D surface table — it omits **error/refusal *parity*** and **cross-engine `.n4a` round-trip**, both still GAP in §D and (partly) L17-owned. The just-delivered "error" tests are *single-engine* dag-ml catchability tests, **not** cross-engine error parity, so "export/error livré" should not be read as closing the error-parity gap.

Severity legend: **MED** = fix before signing `LOCK-PYREF`; **LOW** = nit / residual risk to track.

---

## Validation evidence (tests I ran)

| Gate | Command | Result |
|---|---|---|
| Export/error parity (`B-011`) | `pytest test_conformance_export_roundtrip.py -k dagml_n4a_export` | **3 passed** (0.03s) |
| Ledger drift (`B-009`) | `pytest tests/integration/parity/test_compatibility_ledger.py` | **2 passed** (0.02s) |
| Methods strict CI (`B-015`) | `NIRS4ALL_REQUIRE_N4M=1 pytest -m methods test_n4m_ops.py` | **11 passed** (4.02s) |
| Drift validator *has teeth* | in-memory mutation harness (see below) | **6/6 mutations raised**, baseline passes |

**Drift-test teeth** — `validate_compatibility_ledger` was run against deep-copied, mutated ledgers (no files touched). All of these correctly raised `AssertionError`: drop a tolerance band; corrupt `cross_impl_score.abs_tol`; append an authority row for a non-existent case; bump `coverage_meter.registered`; drop an `xfail_strict` authority row; corrupt a `num_predictions` count. The validator is **not** vacuous, and — importantly — it recomputes every expected value **dynamically** from the live registry (`all_cases()`) and the live constants in `test_conformance_dual_engine.py`, so the static JSON cannot silently drift from the harness.

**Cross-reference spot-checks (all accurate):**
- dag-ml `parity_oracle.v1.json`: `consumer_ledger {path: docs/compatibility.md, required_before_bridge: true}` at lines 5-9; `regression.default` `abs=rel=1e-9` with **`owner: "nirs4all compatibility ledger"`** at lines 15-19; `classification.default` `0/0` at 21-27. The B-009 reconciliation's load-bearing claim — *the contract delegates the authoritative number to this ledger via the `owner` field* — is **literally true**.
- `_conformance_helpers.py`: `assert_score_parity:170`, `assert_runresult_contract:253`, `assert_y_pred_parity:355`, `assert_num_predictions_divergence:220` — all match MD citations. `_DEFAULT_SCORE_TOL`/`_DEFAULT_YPRED_TOL` both `1e-3` at `:60`/`:65`.
- `test_conformance_dual_engine.py`: `EXPECTED_FALLBACK:310`, `test_native_fallback_boundary:373`, `Y_PRED_TOL_OVERRIDES:244`, `assert_same_winner` usages at 437/455/461 (MD §A.3 "457-462" is within range).

---

## Focus-area findings

### A. Compatibility ledger MD ↔ JSON consistency — **PASS**

Cross-checked field-by-field; MD (`docs/compatibility.md`, 291 lines) and JSON (`docs/compatibility.json`, 407 lines) agree:

- **Header**: schema_version 1, owner, `consumer_of`, `last_reconciled` (`2026-06-30`, `nirs4all e41362b4`, `dag-ml f58d7bf`) all match. `nirs4all_commit e41362b4` == current HEAD. ✓
- **Tolerance bands (§A.2 ↔ `tolerance_bands`)**: all 10 bands match on `abs_tol` and measured ceilings — `kernel_snv 1e-12`, `kernel_pls 1e-9`, `native_export_reproduce 1e-6`, `per_case_tight 1e-6`, `cross_impl_score 1e-3 (ceil 7e-6)`, `cross_impl_ypred 1e-3 (ceil 6e-4)`, `cross_impl_ypred_firstderiv 5e-3 (ceil 3.45e-3)`, `classification_label 0`, `n/a_semantic`/`n/a_rng` null. ✓
- **Authority (§B ↔ `authority`)**: the 11 `xfail_strict` (9 KNOWN_DIVERGENCES + 2 legacy_bug), the 2 `pass_parity_note` (`generator_or_models_pls_ridge` 34/32, `generator_chain_model_configs` 49/47), tiers and `authoritative_engine`/band assignments all align between the §B tables and the JSON rows. ✓
- **Coverage meter (§E ↔ `coverage_meter`)**: 95 / 8 / 87 / 11 / 76 / 11 / 6 / 2 / 0 match exactly, and reconcile internally (76 native = ~65 Tier-1 green + 9 KNOWN_DIVERGENCES + 2 num-pred notes). ✓
- **§A.4 amendment** is correctly framed as a *future* paired dag-ml↔nirs4all change (the contract today ships exactly the 2 profiles the MD describes); not done here, correctly. ✓

**A-nit (LOW):** MD §C.4 heading says "`SAME_WINNER_CASES` (~22)"; the live frozenset and the JSON both contain **19**. The `~` softens it but it is off by 3 — recommend changing to 19.

### B. Authority drift test (`_authority.py` + `test_compatibility_ledger.py`) — **PASS, strong design**

- Validates set-membership of every key structure (tolerance bands, strict + parity-note authority, expected-fallback, num-pred divergences, ypred overrides, same-winner, coverage skips) and the coverage meter, **recomputing the expected values from the live registry/constants** rather than hard-coding — so the JSON is pinned to the harness, not to a copy of itself. Teeth verified (6/6 above).
- Robust outside pytest: the side-effect `cases_*` imports populate the registry, `REPO_ROOT = parents[3]` resolves `docs/compatibility.json` correctly, and re-importing already-loaded case modules does not double-register (coverage_meter `registered==95` held). ✓
- Guards beyond membership: `expected_fallback` owner must be `L5`; every `ypred_tol_override` must keep the `assert_same_winner` guard; num-pred counts pinned to exact `34/32` & `49/47`.

**B-risk (LOW, residual):** the validator does **not** check, against any live source:
1. the `abs_tol` *values* of the same-impl / native / per-case / classification bands (`1e-12`, `1e-9`, `1e-6`, `0`) — only the three `cross_impl_*` tolerances are asserted against `_conformance_helpers`/literal `5e-3`. The kernel-band numbers in §A.2 are doc-trust; if `test_n4m_ops` retuned its tolerance, the ledger would not notice.
2. authority `tier` / `authoritative_engine` / `mechanism` and the *correctness* of each band assignment (only that the band id and case name exist).
3. `cross_engine_surfaces` (§D) and `measured_ceiling` values — entirely doc, unchecked.

This is an acceptable scope for a v1 ledger, but §A.2 kernel-band values and the §D surface table are **assertions of trust, not test-enforced invariants**, and should be understood as such.

### C. Methods-installed strict CI (`B-015`) — **PASS**

- `test_n4m_ops.py` cleanly separates two modes: default = opt-in `pytest.skip(allow_module_level=True)` when `n4m` is absent (preserves today's behavior); `NIRS4ALL_REQUIRE_N4M=1` = `pytest.fail(...)` so a missing/broken binding turns the run **red**. Both the import failure and the `METHODS_AVAILABLE is False` path are covered. Marker `methods` registered (`pyproject.toml:233`). Verified: **11 passed** in strict mode with the binding present.
- `methods-installed.yml` is coherent: install `.[dev]` → `pip install nirs4all-methods` → verify `import n4m` (the package→module mapping is correct: `nirs4all-methods` 0.98.0 ships the top-level `n4m` module) → run the `methods` marker with `NIRS4ALL_REQUIRE_N4M=1`. The `pyproject` `matplotlib>=3.7.0` dev add is justified — `tests/conftest.py:34,50` imports matplotlib unconditionally and sets the Agg backend, so it gates **all** collection (this is the `B-013` collection fix).

**C-risk (LOW, unverified):** the `pull_request` trigger always installs `nirs4all-methods` from the **default index (PyPI)**. If that wheel is not published to PyPI (it is a sibling-repo Rust binding; locally it is present as a built wheel, provenance not confirmable offline), the PR-path job fails at the install step. The `workflow_dispatch` `methods_package` input mitigates *manual* runs only — not the automatic PR trigger. The workflow has been YAML-validated but **never executed in real CI** (branch unpushed). Also worth a pre-merge glance: `actions/checkout@v6` / `actions/setup-python@v6` major-version pins should be confirmed to resolve. Recommend confirming PyPI availability (or switching the default spec to a git/artifact ref) before this gate is relied upon.

**C-nit (VERY LOW):** module-scope `pytest.fail(...)` surfaces as a *collection error* rather than a test "failure"; the exit code is still non-zero so the gate holds, but `raise RuntimeError(...)` would be the more idiomatic module-level fail-loud. Functionally fine.

### D. Export / error parity tests (`B-011` sub-slice) — **PASS, faithful to the implementation**

Traced both new tests against the real `RunResult.export` (`nirs4all/api/result.py`):
- `test_dagml_n4a_export_rejects_workspace_selectors_before_legacy_refit`: with `_dagml_export_spec` set, `export(..., source=/chain_id=)` hits the fail-fast at `result.py:1110-1116` and raises `NotImplementedError` ("…explicit source=/chain_id=…") **before** `_dagml_export_delegate()` (1117) — so the monkeypatched delegate is never materialized and `_dagml_legacy_result` stays `None`. The `match="source=/chain_id"` substring is present. ✓
- `test_dagml_n4a_export_without_workspace_or_spec_is_catchable`: with no spec and no workspace, the resolver path reaches `_no_workspace_export_error()` (1141), which — because `per_dataset` marks `engine="dag-ml"` (`_is_dagml_engine()` True) — returns the catchable `NotImplementedError` ("engine='dag-ml' … no workspace artifacts …"). `match` fragment present. ✓
- The `RunResult` dataclass exposes `_dagml_export_spec` / `_dagml_legacy_result` / `_dagml_export_delegate` exactly as the test uses them (`result.py:411-412, 975`). Construction via `_minimal_dagml_result` is valid (all other fields default). ✓

These tests correctly pin the **transitional dag-ml export bridge's fail-fast contract**. They are *single-engine* (dag-ml-only) by design — see finding E.

### E. `B-011` remaining-scope accuracy — **MED finding**

The board's `B-011` *scope* column lists four L17 gaps (cross-engine `.n4a`, workspace, **error-parity**, Studio-bypass) and states the **delivered** slice as "export/error". The *Restant* column, however, lists only **two**: "tests workspace/artifact cross-engine + Studio route bypass parity". The `L17` lane row mirrors this ("Prochaine tranche = workspace cross-engine + Studio-bypass").

Against the ledger's own **§D surface table** — the authoritative tracker — the following remain **GAP** and are (at least partly) **L17**-owned, yet are absent from the *Restant* summary:

1. **Error / refusal parity (PYREF-err, L17)** — §D still reads *"every `pytest.raises` in the parity dir is single-engine dag-ml-only"*, which is **still true after this slice**: the two new `pytest.raises` tests assert dag-ml export *catchability*, not *cross-engine* refusal parity (same invalid pipeline → same refusal on both engines). Labeling the delivered work "export/**error**" risks being read as "error parity done"; it is not.
2. **`.n4a` *cross-engine* round-trip (PYREF-009a, L17+L5)** — legacy-written bundle predicted via dag-ml runtime and the reverse; §D GAP, untouched by this slice (the slice covers the dag-ml export *refusal* path + the pre-existing native single-model reproduce).
3. **nirs4all-side `.so` / wheel freshness (PYREF-011, L17+L9)** — §D GAP; partially acknowledged in the `B-013` note ("garder `.so` freshness comme futur gate consumer-side"), so this one is *tracked elsewhere*, just not under `B-011`.

**Net:** the *ledger §D is accurate and honest* (it keeps error-parity and cross-engine `.n4a` as GAP). The inaccuracy is in the **sync-board `B-011` *Restant* summary**, which collapses the remainder to "workspace + Studio" and could lead to `LOCK-PYREF` being signed against an understated remainder. **Recommend** the `B-011` *Restant* line enumerate the §D GAP rows it still owns — explicitly "error/refusal **parity** (single-engine catchability ≠ parity)" and "cross-engine `.n4a` round-trip" — alongside workspace cross-engine and Studio-bypass.

---

## Findings table

| # | Sev | Area | Finding | Recommendation |
|---|-----|------|---------|----------------|
| E | **MED** | B-011 scope | *Restant* line understates residual L17 work; omits error/refusal **parity** and cross-engine `.n4a` (both §D GAP); delivered "error" tests are single-engine catchability, not parity | Expand the `B-011` *Restant* (and `L17` "Prochaine tranche") to match §D before signing `LOCK-PYREF` |
| C | LOW | Methods CI | PR trigger installs `nirs4all-methods` from PyPI; availability unconfirmed; workflow never run in real CI; `@v6` action pins | Confirm PyPI availability or pin a git/artifact spec for the default; do one real CI run |
| B | LOW | Drift test | Same-impl/native/classification band *values* and §D surfaces are doc-trust, not test-enforced | Optionally assert kernel-band tolerances against `test_n4m_ops` constants in a later pass |
| A | LOW | Ledger MD | §C.4 says "~22" same-winner cases; actual = 19 | Correct to 19 |
| C2 | v.LOW | Methods test | module-scope `pytest.fail` → collection *error* (still non-zero exit) | Cosmetic; `raise RuntimeError` is more idiomatic |

No correctness defects found in the staged code/tests/docs.

---

## Residual risks

1. **`LOCK-PYREF` premature-sign risk** (finding E): if the *Restant* summary is taken at face value, error-parity and cross-engine `.n4a` could be skipped. The ledger §D itself guards against this, but the board summary should be reconciled to it.
2. **Methods gate is unproven in CI** (finding C): green locally with a pre-installed wheel; the PR-path `pip install nirs4all-methods` is the untested link.
3. **Doc-trust surface** (finding B): the §A.2 kernel-band numbers and the entire §D surface ledger are not machine-pinned; they rely on manual upkeep at each reconciliation.
4. **Cross-repo reconciliation pointers** (`dag-ml f58d7bf`, the §A.4 amendment) are not enforced by any test; drift between this ledger and the dag-ml contract is caught only by the lockstep/L20 process, not by CI.

## What is solid (no action)

- `B-009` ledger (MD + JSON + drift test) — consistent, accurate cross-refs, drift test has real teeth, validator works standalone. **Resolved.**
- `B-013` — matplotlib dev dep correctly justified by `conftest.py`; full PYREF green (`556 passed / 14 skipped / 11 xfailed`, exit 0) per board evidence. **Resolved.**
- `B-015` — strict-mode methods gate validated (11 passed strict); install→verify pairing coherent. **Resolved** (modulo the C-risk PyPI caveat).
- `B-011` export/error sub-slice — tests faithful to `RunResult.export`, 3 passed. **Correctly remains `in_progress`.**

---

*Read-only review. No source files edited, nothing staged/unstaged/committed. Tests run were read-only and cheap (≤ ~4s each) in the project `.venv`.*
