# IMP-L15 — nirs4all-cluster RBAC (B-020) implementation report

**Agent:** IMP-L15. **Lane:** `L15` Cluster distribué. **Board item:** `B-020`
(open → tested foundation landed). **Worktree:** `/home/delete/nirs4all/_worktrees/L15-cluster-rbac`
(branch `refactor/L15-rbac`, base `dcced30`). **Source spec:** `SW7_CLUSTER_DISTRIBUTED_spec.md` §3.

This report is the only write outside the worktree. **No** edits to
`PARALLEL_REFACTORING_SYNC.md` or `AGENT_RUN_SUPERVISION.md`; no sibling repos/worktrees touched.

---

## 1. What landed (the B-020 slice)

Replaced the single shared bearer token + advisory `X-N4C-Role` model with
**credential-bound rights** `{submit, read, cancel, execute, admin}`, enforced at the
route level over the *existing* `/v1` surface (no new routes, no scheduler change —
faithful to `DEC-CLU-001` "harden the existing beta").

- **Rights → roles.** `submitter` = submit+read+cancel · `executor` ("rx") =
  read+execute (the worker agent) · `viewer` = read · `admin` = wildcard (all rights).
- **Credential-derived, not header-derived.** A caller's rights come from its bearer
  token; the `X-N4C-Role` header stays advisory (version-divergence logging only). A
  viewer self-asserting `X-N4C-Role: admin` gains nothing (tested).
- **Trusted-LAN usability preserved.** A bare `--token` is kept as a single all-rights
  `admin` principal (existing single-token deployments unchanged). With neither a token
  nor principals the server runs **open (dev mode)** exactly as before.
- **Route → right mapping** (per spec §3b): `POST /v1/jobs` + input `POST /v1/artifacts`
  → `submit`; all `GET /v1/jobs*`, `/v1/stats`, `/v1/workers`, `GET /v1/artifacts/{id}`,
  both WS streams → `read`; `POST /v1/jobs/{id}/cancel` → `cancel`; the whole worker API
  (`/v1/workers/*`, `/v1/tasks/*`) → `execute`. 401 on missing/invalid credential, 403
  on insufficient right.
- **Registration-with-rights handshake** (spec §3d, additive/non-breaking):
  `WorkerRegistered` now echoes the granted `rights[]` for executor self-diagnosis; the
  worker logs them.
- **Config plumbing:** `--principal NAME:TOKEN:ROLES` (repeatable) and `--auth-file`
  (JSON `[{name, token, roles}]`) on `n4cluster server`; unknown roles fail fast at
  startup.

Red-line preserved: `server/auth.py` imports nothing from `nirs4all`; the
`runners/nirs4all_run.py`-only invariant is untouched. State machines / scheduler
unchanged — RBAC is a pure authorization layer above them.

## 2. Files changed

| File | Kind | Change |
|---|---|---|
| `nirs4all_cluster/server/auth.py` | **new** | RBAC core: `Right` enum, `ROLES`, `Principal`, `Authorizer` (open/enforced modes, constant-time token match), `bearer_token`, `rights_from_roles`, `AuthError`. nirs4all-free. |
| `nirs4all_cluster/server/app.py` | mod | `ServerConfig.principals`; `_authorizer_from_config` (legacy `token` → admin principal); `requires(*rights)` dependency factory (stashes principal on `request.state`); per-route rights on all 19 `/v1` routes; WS auth via `_ws_authorized` requiring `read`; `register` echoes rights. Removed dead `import hmac` / old `auth()`. |
| `nirs4all_cluster/schemas.py` | mod | `WorkerRegistered.rights: list[str]` (additive, default `[]`). |
| `nirs4all_cluster/cli.py` | mod | `_load_principals`; `--principal`/`--auth-file` flags; `auth=rbac\|token\|off` startup banner. |
| `nirs4all_cluster/worker/agent.py` | mod | Log server-granted rights after register (3 lines). |
| `tests/test_rbac.py` | **new** | 16 tests (unit + route enforcement). |
| `docs/security-and-scope.md`, `docs/rest-api.md`, `docs/cli-reference.md`, `PROTOTYPE_TO_PRODUCTION.md` | mod | Document the rights/roles model, per-route rights table, new CLI flags, and downgrade the §4 "shared static token" gap to "RBAC landed; mTLS/OIDC/rotation still needed". |

## 3. B008 resolution (the blocker on resume)

Injecting the authenticated principal as a FastAPI arg-default
(`principal: Principal = Depends(requires(...))`) tripped Ruff **B008** ("function call
in argument defaults"). Resolved with a **local code change, no lint-config change**:
the `requires` dependency stashes the resolved principal on `request.state.principal`,
every route keeps the uniform decorator form
`dependencies=[Depends(requires(Right.X))]`, and `register_worker` reads
`request.state.principal` from the handler body. `pyproject.toml` is **unchanged**
(verified: empty diff — no `extend-immutable-calls` added), consistent with the repo
having zero arg-default `Depends` usages. Bonus: `request.state.principal` is now a
clean seam for future audit logging.

## 4. Tests run + results

Green gate from `CLAUDE.md` §Commands, run in a worktree venv
(`uv pip install -e ".[dev]"`, Python 3.11; nirs4all **not** installed — the designated
no-nirs4all unit/API gate):

```
ruff check .                  → All checks passed!
mypy nirs4all_cluster         → Success: no issues found in 19 source files
pytest -q                     → 98 passed, 1 skipped, 1 warning
pytest tests/test_rbac.py -q  → 16 passed
```

- The **1 skip** is `tests/test_integration_nirs4all.py` self-skipping (`No module named
  'nirs4all'`) — expected; that suite needs the sibling nirs4all venv.
- The **1 warning** is a pre-existing `StarletteDeprecationWarning` (httpx/testclient),
  unrelated to this change.
- Pre-existing `test_auth_required_when_token_set` (single-token path) still passes
  unchanged → backward compatibility confirmed by the existing suite *and* a new
  `test_single_token_is_admin_equivalent`.

**Not run** (out of this lane's reach, and untouched by it): `scripts/validation.py` and
the integration suite (need the nirs4all venv + nirs4all-data). This change is
control-plane authorization only — it does not touch the runner, materializer, executor,
scheduler transitions, or the parity path — so distributed==local metric parity is
unaffected.

## 5. Residual risks / remaining gaps (documented, post-slice)

1. **`admin` gates no dedicated route yet.** Today it is purely the all-rights wildcard;
   the spec's admin-only actions (worker eviction, `FAILED→QUEUED` retry, principal/token
   management, quotas) are not yet routes. The right exists as the stable seam.
2. **`python_entrypoint` not yet per-principal-gated.** Kept the existing double gate
   (`--allow-python-jobs` server + `--allow-python` worker). Spec §3c's "submit must also
   carry a `python` grant" is deliberately deferred to keep the slice to exactly the five
   named rights; documented as the next refinement.
3. **Static tokens only.** mTLS/OIDC, per-identity certificates, and token rotation remain
   post-V1 (`PROTOTYPE_TO_PRODUCTION.md` §4). Tokens are shared secrets — trusted-LAN only.
4. **Token match cost is O(#principals)** per request (constant-time per compare, no early
   exit — no timing oracle on *which* token matched). Fine for trusted-LAN scale.
5. **No audit persistence.** `request.state.principal` is populated but only consumed by
   the register echo; wiring it into the event log is a cheap follow-up.

## 6. Review readiness

**Ready for review.** Self-contained, additive, behind the existing auth seam; green on
ruff + mypy + the full no-nirs4all pytest gate; zero changes to wire state machines,
scheduler, or the nirs4all import boundary; backward-compatible (`--token` and dev mode
preserved); docs updated to match. Suggested reviewer focus: the route→right table in
`app.py` vs spec §3b, and the open/enforced-mode switch in `_authorizer_from_config`.
Worktree left clean and inspectable on `refactor/L15-rbac` (not committed — awaiting
review per house rule).
