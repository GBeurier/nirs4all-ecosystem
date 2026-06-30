# W1 — Fallback coverage meter (B-010 / DML-003)

**Agent:** W1 · **Date:** 2026-07-01 · **Repo:** `nirs4all` · **Branch:** `refactor/W1-fallback-meter` (off committed L17 tip `1e4d8043`) · **Worktree:** `_worktrees/W1-nirs4all`
**Commit:** `b135baef54dae1a56d80661307af36d9a124bf9a` (local only — NOT pushed)
**Status:** complete, all targeted gates green.

---

## 1. Mission

Implement the **B-010 / DML-003** fallback coverage meter slice: a PYREF
native-vs-fallback meter that classifies each parity case, emits machine-readable
JSON + a short markdown summary, and gates the `coverage_meter` section of
`docs/compatibility.json` (the LOCK-DROP D1 instrument). Owned files only: new
tools/tests under `tests/integration/parity/` + the `coverage_meter` key. No
edits to `expected_fallback` / `tolerance_bands` / `authority` ledger sections or
to `nirs4all/pipeline/dagml/{detect,run_paths,run_backend}.py` (W2 owns those).

## 2. What changed

Two **new files** (no existing file modified):

| File | Role |
|---|---|
| `tests/integration/parity/coverage_meter.py` | The meter: case classifier + `CoverageReport` (summary / buckets / inventory / markdown) + `--json/--md/--check` CLI. |
| `tests/integration/parity/test_native_fallback_boundary.py` | Static boundary + meter gate (12 fast, engine-free tests). |

### Classification (one disposition bucket per case, precedence-ordered)

`registry skip` (legacy_bug → `xfail`, else `skip`) ▸ `KNOWN_DIVERGENCES` →
`xfail` ▸ observed off-allowlist fallback → `unexpected` ▸ `EXPECTED_FALLBACK` →
`expected_fallback` ▸ native route (`python_pre_materialized` if a
rep-fusion/augmentation keyword, else `python_expanded` if a generator keyword,
else `native`). Roll-up `legacy_fallback = expected_fallback + unexpected`.

The meter is **static** — it reads the declared parity structures only (registry
+ `EXPECTED_FALLBACK` + `KNOWN_DIVERGENCES` + `NUM_PREDICTIONS_DIVERGENCE` +
registry skip kinds), no engine run. The **dynamic** per-case truth stays in the
existing `test_conformance_dual_engine.py::test_native_fallback_boundary` (which
runs the real dag-ml leg); the static meter trusts that guard, so `unexpected`
is 0 here. A caller with dynamic observations may pass `observed_fallback=` to
compute `unexpected` without the meter running anything itself — exercised by a
test that proves an off-allowlist fallback surfaces as a regression.

### Live measurement (this branch)

```
registered 95 | runnable 87 | native(reach) 76 | fallback 11 (expected 11, unexpected 0)
xfail_strict 11 | skip 6 | expected_fallback_target 0
partition leaves: native 21 · python_expanded 46 · python_pre_materialized 0
                  · expected_fallback 11 · unexpected 0 · xfail 11 · skip 6  (= 95)
```

`python_pre_materialized` is 0 today because every rep-fusion/augmentation shape
is currently a `KNOWN_DIVERGENCES` strict-xfail (xfail outranks route); the
bucket is still wired and unit-tested via synthetic input, so it populates the
moment such a shape converges to native.

### `coverage_meter` ledger key

**Not modified** — the L17-authored value already equals the meter's computed
summary exactly (`--check` reports zero drift). The meter is now its
authoritative generator and the new test gates it against drift. The richer
8-bucket inventory is emitted by the meter tool (`--json` / `--md`), not folded
into the ledger key, to keep the existing `_authority.py::_validate_coverage_meter`
exact-equality snapshot intact and avoid co-editing a W4-adjacent file.

## 3. Tests / gates (all green)

```
pytest tests/integration/parity/test_native_fallback_boundary.py -q -p no:cacheprovider
  → 12 passed in 0.05s
pytest tests/integration/parity/test_compatibility_ledger.py -q -p no:cacheprovider   (regression check)
  → 2 passed
ruff check tests/integration/parity/coverage_meter.py test_native_fallback_boundary.py
  → All checks passed
mypy <both files>            → Success: no issues found
py_compile <both files>      → OK
python -m tests.integration.parity.coverage_meter --check
  → coverage_meter OK (fallback=11, target=0)
```

Gate semantics covered by the 12 tests: summary == ledger == independent
recomputation; full-partition completeness + uniqueness; `expected_fallback` /
`unexpected` boundary == live `EXPECTED_FALLBACK` == ledger rows; partition→
summary roll-up identities (`native = native_family + xfail_divergence`, etc.);
route-keyword sets ⊆ canonical DSL; `unexpected` regression detector;
`KNOWN_DIVERGENCES` outranks route; inventory JSON-serializable; CLI zero-drift +
artifact emission.

The existing slow dynamic `test_conformance_dual_engine.py::test_native_fallback_boundary`
was confirmed intact via `--collect-only` (not executed — it requires the dag-ml
engine and is out of this fast slice's scope).

## 4. Failures / blockers

None. No blockers raised. No DEC needed (pure measurement slice, no contract
change). No cross-repo surface touched.

## 5. Boundaries respected

- New files only under `tests/integration/parity/`; `git status` shows exactly
  the two new files, nothing else.
- Did **not** touch `compatibility.json` `expected_fallback` / `tolerance_bands`
  / `authority` (or the `coverage_meter` value — already consistent), `_authority.py`,
  `test_compatibility_ledger.py`, or `pipeline/dagml/{detect,run_paths,run_backend}.py`.
- Did not edit `PARALLEL_REFACTORING_SYNC.md`. Not pushed.

## 6. Handoff notes

- The meter decrements `fallback` automatically as **W2** lands native lowering
  and removes entries from `EXPECTED_FALLBACK` (the meter reads the live
  frozenset). `coverage_meter.fallback == 0` is the LOCK-DROP D1 gate W2 feeds.
- If a maintainer later wants the 8-bucket breakdown *inside* the ledger key,
  that is a one-line enrichment to `coverage_meter` + a matching update to
  `_authority.py::_validate_coverage_meter` (exact-equality → key-superset). Left
  out deliberately to avoid co-editing the W4-adjacent `_authority.py`.
- CI visibility: wire `python -m tests.integration.parity.coverage_meter --check`
  (exit 1 on drift) and/or `--md` into the parity job to surface the fallback
  count per PR.
