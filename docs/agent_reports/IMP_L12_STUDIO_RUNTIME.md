# IMP-L12 — Studio runtime-wrapper slice (B-018): neutral `RtError` envelope for execution-backend routes

**Agent:** IMP-L12 (implementation) · **Lane:** `L12` Studio reassembly · **Date:** 2026-06-30
**Worktree:** `/home/delete/nirs4all/_worktrees/L12-studio-runtime` · **Branch:** `refactor/L12-runtime-routes` · baseline head `2ccbf68`
**Consumes:** `SW8_RT_STUDIO_IMPL_spec.md` §5, `RT_spec.md` §RT-003, `A6_A6-studio-ui.md` §8, sync board `B-017`/`B-018`.
**Scope guard:** worktree-only; no sibling-repo edits; no sync-board edits. This report + the listed Studio files are the only writes.

---

## 0. TL;DR

Implemented the **smallest** of the two L12 slices: the explicit-error half of **`B-018`** (not the `B-017` compute push-down). Introduced a neutral, dependency-free **`RtError`** Pydantic envelope in Studio's `api/` and made it the single source of truth for the execution-backend "unavailable / unsupported" semantics, wired through the existing `ExecutionDriverCapability` and `UnavailableExecutionDriver`.

The change is **additive and wire-compatible**: every existing response shape and error message is byte-identical (proven below). The B-018 deliverable lands at the Python/driver layer (a typed `RtUnsupportedError` carrying the structured envelope, plus a capability accessor), exactly because the existing strict-equality tests **prove the current wire shapes are expected** — per the task instruction to preserve compatibility unless tests prove the new envelope is already expected (they prove the opposite).

**Gate:** 90 backend tests pass (12 new + 78 pre-existing across the affected modules); ruff clean.

---

## 1. Why this slice (and not the other)

The task offered two options; I took the lower-risk one and deliberately did **not** attempt the full push-down.

| Option | Maps to | Verdict |
|---|---|---|
| **(A) neutral Pydantic/runtime models for explicit RtError/unsupported semantics around execution-backend routes** | `B-018` (L10+**L12**) | **CHOSEN** — additive, self-contained in `api/`, no `nirs4all` dependency, no numeric behavior change, no frozen-shape change. |
| (B) move one compute hotspot behind a runtime/core adapter (e.g. `predict.py` metrics → `eval_multi`) | `B-017` (L12+L5/L16) | Rejected for V1: changes numeric computation (RPD/R²/MAE re-implementation parity), requires `require_ml_ready()`, and risks the exact API-compat regression the task warns against. Left for Wave-4 per SW8 §4.B. |

The "unsupported/unavailable" surface around the execution-backend routes today is **ad-hoc**: a free-form `metadata.reason="driver_unavailable"` string on the capability and a **bare `RuntimeError`** on submission (`RT_spec` §RT-003 calls these out as the divergent shapes to converge). That is precisely what B-018 asks to make explicit.

---

## 2. Changed files

| File | Change | LOC |
|---|---|---|
| `api/runtime_errors.py` | **NEW.** Neutral `RtError` Pydantic envelope + `RtErrorCause` vocab + `RtUnsupportedError` (RuntimeError subclass) + `rt_error_from_execution_metadata` classifier. Pure pydantic + stdlib (Phase-1-safe, no `nirs4all`). | 124 (new) |
| `api/execution_driver.py` | **EDIT.** Added `ExecutionDriverCapability.rt_error(verb="run") -> RtError \| None` (derives the envelope from existing fields; `to_dict()` untouched). `UnavailableExecutionDriver.submit` now raises `RtUnsupportedError` instead of a bare `RuntimeError` (same message). | +26 / −2 |
| `api/runs.py` | **EDIT.** `_execution_backend_unavailable_detail` now derives its 501 detail string from `capability.rt_error("run").message` (single source of truth). Output byte-identical for all real/tested capabilities. | +3 / −10 |
| `tests/test_runtime_errors.py` | **NEW.** 12 tests: envelope serialization, cause mapping, message fallback, typed-exception RuntimeError subclassing, driver integration, and a wire-shape regression guard. | 153 (new) |

### 2.1 The envelope (RT_spec §RT-003 / SW8 §2.3, wrapper only — zero new vocabulary)

```python
RtError = { verb, cause, message, mitigation?, unsupported_capability?, portable_level? }
RtErrorCause = unsupported_shape | unsupported_capability | unavailable_backend | invalid_request | runtime_error
```

- `cause` / `unsupported_capability` / `portable_level` vocabulary is **owned by CAP-004 / CAP-002**; this envelope only *carries* it (`DEC-RT-001`).
- Migration mapping implemented for this slice: driver `metadata.reason == "driver_unavailable"` → `cause = "unavailable_backend"` (the SW8 §5.1 row). Unknown reasons default to `unavailable_backend` (the backend *is* unavailable); the reason strings on the wire are unchanged.
- `to_envelope()` = `model_dump(exclude_none=True)` is the canonical wire serializer (symmetric with the existing `ExecutionDriverCapability.to_dict()` pattern).

---

## 3. API compatibility — preserved, and proven

The execution-backend routes are pinned by **strict-equality / regex** tests; these are the contract the task says to honor. All remain green, and I additionally proved string equivalence directly:

| Pinned contract | Test | Status |
|---|---|---|
| `/runs/execution-backends` exact JSON incl. `metadata == {"reason","message"}` | `test_runs_execution_backend.py:192-241` | unchanged (`to_dict()` not touched) |
| `driver.submit(...)` raises `RuntimeError` matching `"no .* driver is configured"` (cluster **and** wasm-local) | `test_execution_driver.py:257` | green — `RtUnsupportedError(RuntimeError)`, same message |
| `cancel_job` metadata `== {"reason":"driver_unavailable"}` | `test_execution_driver.py:265` | unchanged |
| POST run to unavailable backend → **501**, `"Cluster execution" in detail` (detail is a **string**) | `test_runs_execution_backend.py:185-186` | green — detail derived from `rt_error.message`, byte-identical |

**Direct equivalence proof** (executed against the real cluster/wasm-local capabilities):

```
[cluster]    submit-message == legacy: True · regex matches: True · 501-detail == old logic: True
[wasm-local] submit-message == legacy: True · regex matches: True · 501-detail == old logic: True
```

So a consumer that does `except RuntimeError` / reads `str(exc)` / reads the 501 detail string sees **exactly** what it saw before; a consumer that understands the envelope can additionally read `exc.rt_error` / `capability.rt_error(...)`. No wire shape changed, so the frontend message mirrors (`src/lib/__tests__/*` reference the same `"...is typed but no cluster driver is configured."` strings) are unaffected.

---

## 4. Tests run

Runner: `nirs4all-studio/.venv/bin/python -m pytest` from the worktree (the sibling `nirs4all/.venv` lacks fastapi/httpx; the studio venv has fastapi 0.128.0, pydantic 2.13.4). `SENTRY_DSN=""` per repo convention.

```
tests/test_runtime_errors.py ............              [12 new]
tests/test_execution_driver.py ........               [8]
tests/test_runs_execution_backend.py ................. [37]
tests/test_analysis_execution_metadata.py .........    [9]
tests/test_runs_estimation.py ...                      [3]
tests/test_sentry_filter.py ..........                 [10]
tests/test_training_preflight.py ...........           [11]
============================== 90 passed ==============================
```

Lint: `ruff check api/runtime_errors.py api/execution_driver.py api/runs.py tests/test_runtime_errors.py` → **All checks passed** (one auto-fixed import-ordering in the new test file).

Not run (out of scope / blocked): the full `npm run test:parallel` / `lint:parallel` green gate — `test:e2e` and the frontend half need Node + a running stack; the integration suite needs `nirs4all` + matplotlib (sync-board `B-013`, the suite does not collect on this `.venv`). The slice touches only three backend modules, all covered by the targeted run above.

---

## 5. Scope discipline — what I did NOT do

- **No `B-017` compute push-down.** `analysis.py` / `metrics_computer.py` / `playground.*` / `predict.py` metrics stay where they are (Wave-4, couples L5/L16/north-star).
- **No engine threading / recording** (`runs.py:1431`, `training.py:466`, `automl.py:903`, `predict.py:81,89`) — that is the other L12 V1 item (SW8 §4.A) but is a larger, separately-testable change.
- **No new route**, no new response field on a frozen model, no change to `RunResult`/native format/`.n4a`.
- **No Web (`dagml-engine.ts`) changes** — that is `L13` / the same B-018 row's web half.

---

## 6. Blockers & dependencies (recorded, not resolved)

- **CAP-004 vocab** (`cause`/`mitigation`/`unsupported_capability`/`portable_level`): this slice carries the vocabulary; the full cause table and capability ids remain CAP-owned. Only the `driver_unavailable → unavailable_backend` row is exercised here.
- **Frozen wire shapes**: the `/execution-backends` list and the cancel metadata are strict-equality-pinned, so surfacing the envelope *on those payloads* is intentionally deferred (would require a contract change + test update; the task says preserve). The envelope is therefore available at the Python layer (`capability.rt_error()`, `RtUnsupportedError.rt_error`) for the next route-level consumer.
- **`B-013`** (matplotlib absent from `.venv`): blocks the full integration suite from collecting; unrelated to this slice but limits the green gate to the targeted backend run.

---

## 7. Review readiness

- Self-verified: 90 targeted tests green, ruff clean, direct old-vs-new string-equivalence proof for both unavailable backends.
- External review: requested from Codex (`codex exec`) and a code-review subagent. **Outcome appended in §7.1.**
- Recommended reviewer focus: the message/detail equivalence (done), import direction `runtime_errors ← execution_driver ← runs` (one-way, no cycle), and the `assert rt_error is not None` invariant in `submit` (an `UnavailableExecutionDriver` always wraps an unavailable capability; acceptable invariant documentation, not runtime input validation).

### 7.1 External review outcome

**Code-review subagent — CLEAN (no findings at confidence ≥ 80).** Read all four changed files plus the two frozen-contract test files and independently verified:
1. `str(RtUnsupportedError)` is byte-identical to the old `RuntimeError` text for **both** cluster and wasm-local (message threaded verbatim from `capability.metadata["message"]`; no extra formatting) → the `"no .* driver is configured"` regex still matches.
2. The 501 detail stays a substring-compatible string for both backends; the `/execution-backends` exact-JSON shape and `cancel_job` metadata are untouched. It also flagged **two additional** substring assertions (`test_runs_execution_backend.py:1753, 2151`) that likewise stay green.
3. Strict one-way import DAG `runs → execution_driver → runtime_errors`; **no cycle**.
4. `assert rt_error is not None` in `submit` is **unreachable from any HTTP route** (`_ensure_execution_driver_available` raises 501 before `submit` for any unavailable capability; the only other `get_execution_driver` site is cancel-only) — exercised only by direct unit tests, so `-O` stripping changes nothing. Not a correctness risk.
5. No dead code: `_unavailable_execution_backend_message` is still used by `cancel_job`; `to_envelope()`/`unsupported_capability`/`portable_level` are the contractually-exempt RT-003 envelope surface.

**Codex (`codex exec`) — CLEAN on contracts, one minor cleanup.** "No verified correctness findings against the pinned contracts": confirmed `submit()` still raises a `RuntimeError` subclass with the same text, the 501 detail stays a string containing `Cluster execution`, `/execution-backends` serializes from `to_dict()` only (no `RtError` leak), and no import cycle (`runtime_errors` → stdlib/Pydantic only). Ran `pytest tests/test_execution_driver.py tests/test_runtime_errors.py -q` → 20 passed (route tests need fastapi, which its sandbox venv lacked; verified statically). Minor finding: the classifier's `label` parameter was accepted/documented but **never used**.

**Resolution applied:** removed the unused `label` parameter from `rt_error_from_execution_metadata` (and its `capability.rt_error()` caller + the test call sites). Folding it into the message was rejected because the legacy fallback message — `"Execution backend '<backend>' is typed but no execution driver is configured."` — must stay byte-identical to preserve the proven regex/detail equivalence. Codex's second note (`to_envelope()` + optional fields currently test-only) is the intentional, task-exempt RT-003 envelope surface (Codex marked it "Harmless"); left as-is. Re-ran after the cleanup: **ruff clean, 57 targeted tests green.**

**Disposition:** both reviewers clean on the compatibility contract; the one actionable nit (dead `label` param) is fixed. Slice is ready for human/A0 review and sync-board integration (§8).

---

## 8. Suggested sync-board handoff (for A0 — NOT applied here)

> `L12` Studio reassembly · `review` · IMP-L12 · `nirs4all-studio` · **Done (slice 1/n):** neutral `RtError` envelope (`api/runtime_errors.py`) wired into execution-backend routes (`UnavailableExecutionDriver.submit` → `RtUnsupportedError`; 501 detail derived from envelope). Additive, wire-compatible (90 tests green). **Next:** thread+record `engine=` (SW8 §4.A); surface `rt_error` on a route once the frozen `/execution-backends` shape is allowed to extend; Web silent-catch → `RtError` (`L13`). · Blockers: `B-017` (compute push-down, Wave-4), `B-013` (suite collection), CAP-004 vocab.

---

### Evidence (worktree-only writes)
`api/runtime_errors.py` (new), `api/execution_driver.py`, `api/runs.py`, `tests/test_runtime_errors.py` (new). Verified against `tests/test_execution_driver.py`, `tests/test_runs_execution_backend.py` (unmodified). Context: `SW8_RT_STUDIO_IMPL_spec.md`, `RT_spec.md`, `A6_A6-studio-ui.md`, `PARALLEL_REFACTORING_SYNC.md` rows `B-017`/`B-018`.
