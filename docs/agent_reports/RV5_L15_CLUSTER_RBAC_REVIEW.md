# RV5 — Review of L15 nirs4all-cluster RBAC (B-020)

**Reviewer:** RV5 (read-only). **Subject:** staged changes on `refactor/L15-rbac`
(worktree `/home/delete/nirs4all/_worktrees/L15-cluster-rbac`, base `dcced30`, **staged but not
committed** — HEAD is still `dcced30`, consistent with the house "await review" rule).
**Implementation report reviewed:** `docs/agent_reports/IMP_L15_CLUSTER_RBAC.md`.
**Spec (source of truth):** `docs/agent_reports/SW7_CLUSTER_DISTRIBUTED_spec.md` §3.
**Scope of write:** this file only. No source edits, no stage/unstage, no commit.

## Disposition: ✅ APPROVE — non-blocking minor notes only

The slice is correct, faithful to spec §3b/§3c/§3d, fully tested, and preserves every
load-bearing invariant (nirs4all import boundary, state machines/scheduler untouched,
legacy single-token + dev open mode unchanged). I reproduced the green gate independently.
Four findings, all **Low / Informational** — none block the merge; all are either already
disclosed as residual risks or are operator-clarity refinements.

---

## 1. Method

- Read every staged hunk via `git diff --cached` (not CodeGraph alone) plus the full
  `server/auth.py`, the route bodies in `server/app.py`, `cli.py`, `worker/agent.py`,
  `schemas.py`, `tests/test_rbac.py`, and all four doc diffs.
- Cross-checked the route→right table against spec §3b line by line.
- Re-ran ruff, mypy, the focused RBAC suite, and the full no-nirs4all unit/API gate.
- Scanned the whole package for `import nirs4all` and for any leftover `config.token`/`hmac`
  auth logic.

## 2. Focus-area findings (all 7 requested areas)

### 2.1 Route → right mapping — ✅ faithful 1:1 to spec §3b
Every `/v1` endpoint carries a `dependencies=[Depends(requires(Right.X))]` (19 HTTP routes)
or authorizes in-body for the 2 WS routes; the four health/dashboard routes (`/`, `/healthz`,
`/version`, `/ui`) are intentionally open (documented "no auth"). Verified mapping:

| Right | Routes (impl) | Spec §3b |
|---|---|---|
| `submit` | `POST /v1/jobs`, `POST /v1/artifacts` | ✓ match |
| `read` | `GET /v1/jobs`, `/v1/jobs/{id}`, `/{id}/tasks`, `/{id}/events`, `/{id}/artifacts`, `/v1/stats`, `/v1/workers`, `GET /v1/artifacts/{id}`, both WS streams | ✓ match |
| `cancel` | `POST /v1/jobs/{id}/cancel` | ✓ match |
| `execute` | `POST /v1/workers/register`, `/{id}/heartbeat`, `/{id}/lease`, `/v1/tasks/{id}/start\|events\|artifacts\|complete\|fail` | ✓ match |
| `admin` | wildcard, no dedicated route yet | ✓ match (deferred, see §3.1 of report) |

No `/v1` route is left unguarded (verified by enumerating all `@app.*` decorators). 401 on
missing/invalid credential, 403 on insufficient right — confirmed in code and tests.

### 2.2 Legacy token compatibility — ✅ preserved
`_authorizer_from_config` turns a bare `config.token` into one all-rights `admin` principal
("default"). `test_single_token_is_admin_equivalent` and the pre-existing
`test_auth_required_when_token_set` both pass. A single-token deployment is unchanged.

### 2.3 Dev open mode — ✅ preserved
No token + no principals ⇒ `Authorizer` runs unenforced; `principal_for_token` returns the
synthetic all-rights `_DEV` principal regardless of token, so every route (incl. WS and worker
API) is open exactly as in the prototype. `test_open_mode_grants_everything` confirms.

### 2.4 Worker registration rights — ✅ correct
`register/heartbeat/lease` and all `tasks/*` require `execute`. The worker sets
`Authorization: Bearer <token>` once at the httpx client level (`agent.py:58-62`), so **every**
worker request carries the credential — no per-call regression. `WorkerRegistered.rights`
echoes the granted rights (additive, default `[]`); the agent logs them. Crucially,
**`WorkerRegister` (the request) has no `rights` field** — rights stay credential-bound, not
self-declared, exactly as spec §3d mandates.

### 2.5 WebSocket auth — ✅ correct
Both `/v1/events/stream` and `/v1/jobs/{id}/events/stream` call `_ws_authorized(..., Right.READ)`
on the `?token=` query param before `accept()`; failure ⇒ `close(code=4401)`. In dev mode the
authorizer grants `read`, so the dashboard still works tokenless. `test_ws_stream_requires_read`
covers both the viewer-can-stream and unknown-token-rejected paths.

### 2.6 Docs accuracy — ✅ accurate
`rest-api.md` rights table, `cli-reference.md` (`--token`/`--principal`/`--auth-file`),
`security-and-scope.md`, and `PROTOTYPE_TO_PRODUCTION.md` all match the implemented behavior
(including the precise "POST /v1/workers/*" scoping that leaves `GET /v1/workers` under `read`).
No doc overstates the slice — mTLS/OIDC/rotation are still listed as outstanding.

### 2.7 nirs4all import boundary — ✅ intact
No file under `nirs4all_cluster/` imports nirs4all except `runners/nirs4all_run.py`, which does
so lazily inside `main()`. The new `server/auth.py` is stdlib-only (`hmac`, `collections.abc`,
`dataclasses`, `enum`). The server/client/worker stay nirs4all-free.

## 3. Defect findings (all non-blocking)

**F1 — Low (operator clarity / least surprise): a legacy token silently becomes an undisclosed
`admin` principal in RBAC mode.**
`cli.py:101` resolves `token = args.token or os.environ.get("N4CLUSTER_TOKEN")`, and
`_authorizer_from_config` (`app.py:108-111`) appends that token as an all-rights `admin`
principal *even when `--principal`/`--auth-file` are configured*. The startup banner computes
`auth_mode = "rbac" if principals else ("token" if token else "off")` from the CLI principal
list only (`cli.py:116`), so it prints `auth=rbac` while a full-admin token is simultaneously
live and unmentioned. An operator who sets up RBAC with a stale `$N4CLUSTER_TOKEN` in their
environment gets an admin backdoor named "default" they were not told about. The merge behavior
is intentional/documented (migration aid), but the banner should disclose it — e.g.
`auth=rbac+legacy-admin-token` or a warning when both are set. Trusted-LAN, operator-held
secret ⇒ Low severity, not a privilege-escalation path for an external caller.

**F2 — Informational (spec §3c, already disclosed as residual #2): `python` grant deferred.**
Spec §3c lists, under V1, that `python_entrypoint` "additionally requires the principal's
`submit` right to include a `python` grant". The slice keeps only the existing double-gate
(`--allow-python-jobs` + `--allow-python`) and defers the per-principal `python` grant. **No
security regression** — the double-gate is unchanged — but this is a spec item marked "V1" that
is consciously postponed; it is accurately documented in the report's residual risk #2.

**F3 — Informational (spec §3d, partial): worker not persisted under its authenticated
principal.** Spec §3d also says "the server records the worker under its authenticated principal
so admin eviction and audit have an identity to act on." `register_worker` reads
`request.state.principal` only to echo rights; it does not store the principal name on the
worker row. Consistent with admin eviction (residual #1) and audit persistence (residual #5)
being deferred, so acceptable for this slice — but the §3d "records under principal" clause is
not yet satisfied and will need wiring when admin actions land.

**F4 — Low (config foot-gun): duplicate-token principals resolve last-wins, silently.**
`principal_for_token` loops without early exit (correct for constant-time matching) and keeps
the *last* match, and nothing at startup rejects two principals sharing a token. A
mis-configured `--auth-file` with a repeated token silently grants the last-defined identity.
Trusted-LAN, operator error ⇒ Low. A startup uniqueness check would be a cheap hardening.

## 4. Commands run + results

```
.venv/bin/python -m pytest tests/test_rbac.py -q   → 16 passed, 1 warning
.venv/bin/ruff check .                              → All checks passed!
.venv/bin/mypy nirs4all_cluster                     → Success: no issues found in 19 source files
.venv/bin/python -m pytest -q                       → 98 passed, 1 skipped, 1 warning   (6.37s)
grep -rn 'import nirs4all|from nirs4all' nirs4all_cluster/   → only runners/nirs4all_run.py (lazy)
grep -rn 'config.token|hmac|def auth' server/               → no leftover auth path; hmac only in auth.py
```

The green gate exactly reproduces the report's numbers (16 RBAC; 98/1 full; ruff/mypy clean).
The 1 skip is `test_integration_nirs4all.py` self-skipping (no nirs4all installed — expected
for this gate); the 1 warning is the pre-existing `StarletteDeprecationWarning`, unrelated.

## 5. Residual risks (carried forward)

1. `admin` gates no dedicated route yet — wildcard-only seam (report residual #1). Confirmed.
2. `python_entrypoint` not per-principal gated — F2 above (report residual #2).
3. Worker identity not persisted on the worker row — F3 above; blocks future admin eviction/
   audit until wired (report residuals #1/#5).
4. Static shared-secret tokens only; mTLS/OIDC/rotation post-V1 (report residual #3). Trusted
   LAN only.
5. Token-match cost is O(#principals) per request, constant-time per compare (report residual
   #4). Fine at LAN scale.
6. Banner does not disclose a concurrently-active legacy admin token — F1 above.

## 6. Conclusion

Faithful, additive, well-tested authorization layer that lands B-020 without touching the wire
state machines, scheduler, or the nirs4all import red-line, and without breaking the legacy
single-token or dev-open deployments. No correctness bug found. **Approve**; F1 (banner
disclosure of an active legacy admin token) and F4 (duplicate-token startup check) are worth a
cheap follow-up but do not block the slice. F2/F3 are already on the disclosed residual-risk
list.
