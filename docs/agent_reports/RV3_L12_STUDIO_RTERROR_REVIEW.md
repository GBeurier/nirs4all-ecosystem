# RV3 — Review of IMP-L12 Studio runtime `RtError` slice (B-018)

**Reviewer:** RV3 (read-only) · **Date:** 2026-07-01
**Target:** staged changes on branch `refactor/L12-runtime-routes` (worktree `/home/delete/nirs4all/_worktrees/L12-studio-runtime`)
**Implementation report reviewed:** `docs/agent_reports/IMP_L12_STUDIO_RUNTIME.md`
**Method:** direct file reads + `git diff --cached` + `git show HEAD:` for old/new comparison + targeted test runs + a direct old-vs-new equivalence probe. CodeGraph used only as a starting index.

## Final disposition: **APPROVE — additive, wire-compatible, no blocking findings.**

The slice does exactly what the report claims: introduces a dependency-free `RtError` Pydantic envelope and routes the execution-backend "unavailable" semantics through it, with **byte-identical** wire output for every currently-registered capability. All five review axes (wire compatibility, RuntimeError compatibility, Pydantic safety, import cycles, contract test coverage) pass. Four residual risks are documented below; all are LOW/INFORMATIONAL and none block the slice.

---

## Scope of staged change (verified against `git diff --cached`)

| File | Change | Verified |
|---|---|---|
| `api/runtime_errors.py` | NEW — `RtError` BaseModel + `RtErrorCause` Literal + `RtUnsupportedError(RuntimeError)` + `rt_error_from_execution_metadata` classifier | ✓ read in full (124 LOC) |
| `api/execution_driver.py` | `ExecutionDriverCapability.rt_error()` accessor added; `UnavailableExecutionDriver.submit` raises `RtUnsupportedError` (same message); `to_dict` untouched | ✓ |
| `api/runs.py` | `_execution_backend_unavailable_detail` rewritten to derive detail from `capability.rt_error("run").message` | ✓ (compared with `HEAD:api/runs.py`) |
| `tests/test_runtime_errors.py` | NEW — 12 tests | ✓ read in full |

The report's "changed files" table, the removal of the `label` param from the classifier, and the import direction all match the actual staged code.

---

## Axis-by-axis findings

### 1. Wire compatibility for execution-backend routes — PASS (proven byte-identical)

Both registered unavailable capabilities carry a `message` in metadata (`execution_driver.py:319-343`):
- cluster → `"Cluster execution is typed but no cluster driver is configured."`
- wasm-local → `"WASM local execution is typed but no WASM driver is configured."`

I reconstructed the **old** `_execution_backend_unavailable_detail` (from `git show HEAD:api/runs.py`) and ran it against the **new** logic for the real capabilities:

```
[cluster]    identical=True
  OLD/NEW: Execution backend 'cluster' is not available: Cluster execution is typed but no cluster driver is configured.
[wasm-local] identical=True
  OLD/NEW: Execution backend 'wasm-local' is not available: WASM local execution is typed but no WASM driver is configured.
```

- `/runs/execution-backends` exact JSON (`test_runs_execution_backend.py:200-241`) is driven by `to_dict()`, which is untouched → unaffected.
- 501 detail substring `"Cluster execution" in detail` (`test_runs_execution_backend.py:186, 1753, 2151`) → new detail contains the substring; green.
- Frontend mirror pins the `to_dict` `message` strings (`src/hooks/useNewExperimentExecutionEnvironment.test.tsx:94,105`), **not** the 501 detail format → unaffected by this change.

Additionally noted (strengthens the compatibility argument beyond the report): on the **HTTP route path**, `_start_run_job` calls `_get_available_execution_driver` → `_ensure_execution_driver_available`, which raises the 501 **before** `driver.submit` is ever reached for an unavailable backend (`runs.py:894-946`). So the only route-visible change is the (byte-identical) 501 detail string; `submit`'s new `RtUnsupportedError` is exercised only by direct unit tests on that path.

### 2. RuntimeError compatibility — PASS

`RtUnsupportedError(RuntimeError)` calls `super().__init__(rt_error.message)`, so `str(exc)` is the verbatim legacy message and the pinned regex `"no .* driver is configured"` still matches (`test_execution_driver.py:257`, plus the new parametrized `test_runtime_errors.py:142-153`). The only `driver.submit` call site is `runs.py:942`; every `except RuntimeError` handler in the codebase (`training.py:586/612`, `automl.py:1070`, `jobs/manager.py`) still catches the subclass. No code narrows on `type(exc) is RuntimeError`.

### 3. Pydantic model safety — PASS

`RtError` is a plain `BaseModel`; `cause: RtErrorCause` is a `Literal` and the classifier only ever supplies a valid member (`_DRIVER_REASON_TO_CAUSE.get(reason, "unavailable_backend")`), so no `ValidationError` on any exercised path. `to_envelope()` = `model_dump(exclude_none=True)` — standard. Optional fields default to `None`, no mutable-default hazard. The classifier defends its inputs (`isinstance(reason, str)`, `isinstance(message, str) and .strip()`, `metadata or {}`) so malformed metadata degrades to the fallback message rather than raising. Verified green on pydantic 2.12.5 (report used 2.13.4); only stable `BaseModel`/`Literal`/`model_dump` APIs are used, so version-robust.

### 4. Import cycles — PASS

`runtime_errors.py` is a **leaf**: static AST scan shows imports = `__future__, collections.abc, typing, pydantic` — zero intra-`api` imports. One-way DAG `runs → execution_driver → runtime_errors`, confirmed by `import api.runtime_errors` and `from api.execution_driver import …` both succeeding. Phase-1 safe (pydantic is already loaded via FastAPI; no `nirs4all`).

### 5. Test coverage of pinned contracts — PASS (one minor gap)

New `tests/test_runtime_errors.py` adds a frozen-wire-shape guard (`test_capability_rt_error_does_not_mutate_frozen_wire_shape`, pins the exact `to_dict` key set) and parametrized submit-raises-`RtUnsupportedError` for both backends. Pre-existing contract tests (`test_execution_driver.py`, `test_runs_execution_backend.py`) remain green. Minor gap → R4 below.

---

## Commands run & results

```
$ git diff --cached --stat
 api/execution_driver.py | 28 ++,  api/runs.py | 13 ±,  api/runtime_errors.py | 124 (new),  tests/test_runtime_errors.py | 153 (new)

# import-cycle (static AST + runtime)
runtime_errors imports: ['__future__', 'collections.abc', 'typing', 'pydantic']  -> intra-api: NONE (leaf, no cycle)
import api.runtime_errors OK ; cluster rt_error.message == 'Cluster execution is typed but no cluster driver is configured.'

# old-vs-new detail equivalence (real capabilities)
[cluster] identical=True ; [wasm-local] identical=True

# targeted suites
$ pytest tests/test_runtime_errors.py tests/test_execution_driver.py tests/test_runs_execution_backend.py -q
57 passed in 2.10s
$ pytest <the 7 files cited in the report> -q
90 passed in 2.96s

$ ruff check api/runtime_errors.py api/execution_driver.py api/runs.py tests/test_runtime_errors.py
Ruff 0.14.14: No issues found
```

(Venv: `../../nirs4all-studio/.venv` — the worktree `.venv` is absent; fastapi 0.128.0 / pydantic 2.12.5. `SENTRY_DSN=""` per repo convention.)

---

## Residual risks (all non-blocking)

**R1 — Latent 501-detail divergence for a future message-less capability (LOW).** The rewrite collapses the old three-tier fallback ladder (`metadata.message` → `metadata.reason` → `(label)`) into two tiers (`metadata.message` → generic sentence). For the two registered capabilities (both carry `message`) the detail is byte-identical, proven above. But a *future* unavailable backend registered with only a `reason` and no `message` would change the 501 detail:
- reason-only: old `"…is not available: driver_unavailable"` → new `"…is not available: Execution backend 'x' is typed but no execution driver is configured."`
- empty metadata: old `"…is not available (Label)"` → new generic sentence.

This is a behavior *improvement* (it stops leaking the raw `driver_unavailable` token / bare label into user-facing text) but it is unflagged by any test. **Mitigation:** when adding a new typed backend, give its capability a `message` (matching the existing two), or add a test pinning the message-less detail if that path is ever wanted. Not a regression today.

**R2 — `assert rt_error is not None` in `submit` under `python -O` (VERY LOW).** If asserts are stripped *and* an `UnavailableExecutionDriver` were ever constructed around an `available=True` capability (nothing does this — both wraps at `execution_driver.py:399-400` are unavailable), `submit` would raise `AttributeError` on `None.message` instead of a clean error. Unreachable in production; documented invariant. Acceptable as-is.

**R3 — Envelope is "carried but not yet read" on the wire (INFORMATIONAL).** `to_envelope()`, `mitigation`, `unsupported_capability`, `portable_level`, and `RtUnsupportedError.rt_error` are populated/serializable but no route surfaces them yet (the frozen `/execution-backends` and cancel shapes intentionally don't). This is the deliberate RT-003 forward surface for the next consumer, not dead code (`mitigation` is always set by the classifier; the rest are optional). Flagged only so a future reviewer doesn't mistake it for unused output.

**R4 — No direct unit test for the `runs.py` helper edit (LOW).** `_execution_backend_unavailable_detail`'s new behavior is covered only indirectly via the 501 route tests, which assert a substring (`"Cluster execution"`), not the full detail string. The byte-equivalence I proved manually is not pinned. Bracketed by the `to_dict` exact-JSON test + the substring tests, so low risk; a one-line assertion on the full cluster detail string would close it.

---

## Summary

The implementation report is accurate and its compatibility proof reproduces. The change is additive, the wire is byte-identical for all real capabilities, `RuntimeError` semantics are preserved by subclassing, the new module is an import leaf, and the contract tests (90) are green with ruff clean. **Approved for sync-board integration.** The one item a human should note is **R1** (latent detail-string change for any future capability that omits `message`) — a quality improvement rather than a regression, but currently unguarded by tests.
