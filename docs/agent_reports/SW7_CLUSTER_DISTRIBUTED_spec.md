# CLU-SPEC report — lane L15 (Cluster distribue) — `DEC-CLU-001`

**Agent:** SW7 (second-wave). **Lane:** `L15`. **Decision:** `DEC-CLU-001` (proposed, P1 `ARB-011`).
**Lock proposed:** `LOCK-CLU` (not yet signed). **Mode:** read-only audit. No code/test/sync-board edits.
This file is the only write.

**Method:** direct `rg`/`Read` against local heads (CodeGraph not relied on for facts).
Verified head: `nirs4all-cluster dcced30` (clean, matches sync board pass 2); cross-refs
`nirs4all-studio 2ccbf68`, `dag-ml f58d7bf`. Every claim below cites `file:line` in the cluster repo
unless marked **`NET-NEW`**.

**One-line thesis (faithful to `DEC-CLU-001`):** `nirs4all-cluster` is **already a working trusted-LAN
beta** (client / server / polling workers, FastAPI + SQLite + content-addressed object store, leases +
retries + cooperative cancel, capability routing, metric-identical parity at Level 0/1). `LOCK-CLU` is a
**hardening contract over the existing `/v1` surface**, not a scheduler built from scratch. The four real
V1 gaps are: (1) **RBAC** — there is only one shared token and no role separation today; (2) an **optional
core/Studio/CLI client** seam; (3) wiring cluster results to the **`LOCK-RT` `RtResult`/`RtError`
envelopes**; (4) a **distributed==local parity gate** in the program's CI. Fine-grained DAG scheduling
(Levels 2/3) is **explicitly post-V1** and must route through `dag-ml`, never bypass it.

---

## 0. Cross-program anchors (sync board `PARALLEL_REFACTORING_SYNC.md`)

- `DEC-CLU-001` (proposed, line 103): "durcir le `/v1` existant (RBAC), pas un scheduler from scratch."
- `L15` (line 77): repo `nirs4all-cluster`; next action "RBAC, client core, Studio/CLI adapter,
  distributed==local parity"; blockers `LOCK-RT`, `LOCK-CAP`; **"fine-grained DAG depends on `L5`/`L16`."**
- `LOCK-RT` **landed** (line 55): `RtResult` anchored on dag-ml `ScoreSet`; `RtRunRequest`/`RtError`
  wrappers; `execution_backend ∈ {local-python, wasm-local, cluster}`.
- `LOCK-CAP` **landed** (line 48): `ControllerCapability` (19) + `fit_scope`/`rng_policy`/`artifact_policy`;
  `portable_level` classifier; `unsupported {cause_code, mitigation}` envelope.
- North Star (roadmap `CLU-004`): "fine-grained DAG seulement quand `dag-ml` expose le coordinateur
  necessaire; **ne pas contourner `dag-ml`**."
- Design schema §5.5 (`MULTIMODAL_ECOSYSTEM_DESIGN_SCHEMAS.md`): cluster = "load balancer/scheduler adapted
  to nirs4all/DAG"; executor clients/workers register with **rights and capabilities**; submitter clients
  submit; "Cluster must not own parsers, kernels or graph semantics."
- Roadmap task IDs: `CLU-001` core client · `CLU-002` RBAC · `CLU-003` worker capabilities · `CLU-004`
  job/task DAG mapping · `CLU-005` Studio/CLI adapter · `CLU-006` benchmarks queue path.
- Note: `nirs4all-cluster` is **not** in the ecosystem index and has **no GA commitment**
  (`nirs4all-cluster/CLAUDE.md:8-15`); `LOCK-CLU` is a beta-hardening lock, not a release gate.

---

## 1. Verified inventory — what the beta already is (the contract `LOCK-CLU` hardens)

### 1a. Topology (`CLAUDE.md:67-130`, `docs/concepts/architecture.md`)
Single FastAPI server process owns: SQLite queue (WAL, single writer → atomic leasing without an external
broker), content-addressed object store (`objects/aa/bb/<sha256>`), scheduler (state machines + matching),
in-process WebSocket event broker. Workers **poll** (long-poll lease + heartbeat); no push. Server splits
**policy** (`server/scheduler.py`) from **mechanism** (`server/db.py`); `server/app.py` = routes + reaper.

### 1b. The one load-bearing invariant (`CLAUDE.md:22-30`)
**Only `nirs4all_cluster/runners/nirs4all_run.py` imports `nirs4all`**, as a child subprocess. Server,
client, worker agent, materializer, executor stay `nirs4all`-free (control plane runs without the library;
native-backend segfault can't kill the worker; parent `terminate()` = real cancellation). **`LOCK-CLU`
must preserve this red-line verbatim** — it is the same boundary rule `nirs4all-studio` uses.

### 1c. Wire contract (`schemas.py` — the *only* boundary validation point)
- State enums: `JobStatus` (`:21-27` queued/running/succeeded/failed/cancelling/cancelled), `TaskStatus`
  (`:30-37` queued/leased/running/succeeded/failed/lost/cancelled), `WorkerStatus` (`:40-42` alive/dead).
- Inputs: `PipelineRef` (`:64` kinds `path|artifact|inline_json|python_entrypoint`),
  `DatasetRef` (`:93` kinds `shared_path|artifact|catalog|worker_local`).
- `Requirements` (`:115-136`): `labels`, `min_memory_gb`, `min_gpu_count`, `packages` (PEP 440, validated).
- `JobRequest` (`:153-201`): one-of `pipeline`/`pipelines` × one-of `dataset`/`datasets` → cartesian
  (Level 1); `rank_metric="best_rmse"`/`rank_mode="min"`; `idempotency_key`; `retry` (`RetryPolicy`
  `max_attempts` 1..10 default 2, `:144`).
- Worker: `WorkerRegister` (`:208-213` labels/capabilities/slots_total/version/name) →
  `WorkerRegistered` (`:216-219` worker_id/heartbeat_interval_s 10/lease_ttl_s 60); `HeartbeatAck`
  (`:222-225` `cancel_task_ids` = cooperative cancellation channel); `TaskPayload` (`:228-239`).
- Reports: `TaskResult` (`:267-279` incl. `pipeline_fingerprint`, `RunMetrics`, `artifacts` by role),
  `TaskFailure` (`:282-285` error/traceback/`retriable`).
- Views: `JobAggregate` (`:306-316` ranking/best_metric/best_task_id/best_model_artifact_id/errors),
  `JobView`/`TaskView`/`EventView`/`ArtifactView`/`ClusterStats`.

### 1d. Scheduler / load balancer (`server/scheduler.py`)
Pure, unit-tested. `JOB_TRANSITIONS`/`TASK_TRANSITIONS` (`:19-36`) mirror the design state machines; the DB
*enforces* them on every status change. `requirements_match` (`:84-113`) routes in order: **exact label
match → soft memory floor → GPU fail-closed (undeclared = 0) → PEP 440 package versions**
(`version_satisfies`, `:66-81`; undeclared package = unavailable). `aggregate_metric_better` (`:116-122`)
ranks composite jobs. **This is whole-run (Level-0/1) capability routing — not DAG-aware** (see §8).

### 1e. Recovery & correctness (`CLAUDE.md:113-129`, `server/db.py`, `server/app.py`)
Lease + TTL renewed on heartbeat; reaper requeues expired leases / marks silent workers dead; bounded
retry (`max_attempts`); `idempotency_key` dedupe (unique index + `IntegrityError` race handling);
cooperative cancel (a cancelled job's reaped lease never relaunches); **worker slot usage derived live from
the task table (`_in_flight_count`), never a counter**; `_finalize_job`/`try_set_job_status` flip the job
aggregate atomically/idempotently (two workers finishing the last tasks can't double-flip).

### 1f. Versioning handshake (`versioning.py`)
`API_VERSION=1` (`:26`, protocol major, independent of package version); headers `X-N4C-Version`/`X-N4C-Api`/
`X-N4C-Role` (`:32-34`) on every `/v1` call+response; incompatible major → **HTTP 426** (`is_incompatible`
`:55-61`); compatible drift → `version_divergence` event. Canonical pipeline `fingerprint_obj`/`_file`
(`:73-84`) = the parity-traceability anchor (client and worker agree on inline-pipeline identity).

### 1g. Parity already measured (`PROTOTYPE_TO_PRODUCTION.md:18`, `docs/concepts/job-decomposition.md`)
Level 0 (atomic) and Level 1 (`pipelines × datasets`) are **metric-identical to local `nirs4all.run()`,
diff = 0.0 (≤ criterion 1e-10)**. Level 2 (explicit variants) and Level 3 (folds) are **declared
non-goals** of the beta (`docs/security-and-scope.md:29`).

---

## 2. The client/server/workers model + terminology reconciliation

The prompt's framing ("client registers with rx rights; server can ask clients to execute; clients can send
jobs") unifies two roles the code keeps physically separate. Reconciliation (no contradiction):

| Prompt phrasing | Design-schema term (§5.5) | Code today | `LOCK-CLU` reading |
|---|---|---|---|
| "client … send jobs to server" | **submitter client** | `ClusterClient` → `POST /v1/jobs` (`client.py:108`) | client holding **`submit`** right |
| "client registers … with rx rights" | **executor client / worker** | `worker/agent.py` → `POST /v1/workers/register` | client whose credential carries **`read`+`execute`** ("rx") |
| "server can ask clients to execute jobs" | server **assigns/leases** to eligible executor | `POST /v1/workers/{id}/lease` (long-poll **pull**) | server-authoritative assignment, **delivered on the worker's lease** |

Two faithful clarifications `LOCK-CLU` must state once:
1. **"rx" = read + execute**, a right-set on the registering principal — not a new transport. A worker is
   "a client with the `execute` right". One process may hold several rights (a Studio host that both submits
   and executes), but the credential, not a self-asserted header, decides (see §3).
2. **"server asks client to execute" = pull, not push, in V1.** The server *decides* the assignment
   (scheduler + atomic lease) and *hands it out* when the executor long-polls `/lease`. This keeps NAT/LAN
   simplicity (`PROTOTYPE_DESIGN.md:94`). **Server-initiated push is a post-V1 transport option** (§8), not
   a V1 requirement; the assignment authority is already server-side.

---

## 3. `CLU-002` — RBAC (the #1 V1 gap)

### 3a. Verified current state: there is no RBAC
`auth()` (`server/app.py:171-177`) checks a **single** `Bearer {config.token}` via `hmac.compare_digest`;
**no token configured ⇒ no auth at all** (`:173-174` dev mode). The *same* `Depends(auth)` guards **every**
`/v1` route — client and worker alike (`:211,246,258,271,278,285,310,316,332,353,418,436,452,471,494,512,
536,587,620`; WS via `?token=` `:365,392`). `X-N4C-Role` is **advisory only** — used solely for
divergence logging (`:162`), never for authorization. **Any token holder can submit, read, cancel,
register, lease, and execute.** This is acceptable for trusted-LAN beta but is the documented "biggest gap"
(`PROTOTYPE_TO_PRODUCTION.md:62-63`).

### 3b. Proposed V1 role/right model (**`NET-NEW`**, minimal, trusted-LAN-appropriate)
Five **roles** (= roadmap `CLU-002` list) composed from granular **rights**, mapped onto the *existing*
routes (no new routes required for V1 RBAC — it is an authorization layer over today's surface):

| Right | Existing routes it gates (`server/app.py`) |
|---|---|
| `submit` | `POST /v1/jobs` (`:211`), `POST /v1/artifacts` input upload (`:332`) |
| `read` | all `GET /v1/jobs*`, `/v1/stats` (`:258`), `/v1/workers` (`:620`), `GET /v1/artifacts/{id}` (`:353`), both WS streams (`:364,392`) |
| `cancel` | `POST /v1/jobs/{id}/cancel` (`:285`) |
| `execute` | `POST /v1/workers/register` (`:418`), `/heartbeat` (`:436`), `/lease` (`:452`), `/tasks/{id}/start|events|artifacts|complete|fail` (`:471,494,512,536,587`) |
| `admin` | worker eviction, retry of `FAILED→QUEUED` (`scheduler.py:23,33`), token/principal management, server config, (future) quotas |

| Role | Rights | Maps to |
|---|---|---|
| `submitter` | submit, read, cancel | CLI/SDK/Studio user, benchmarks queue |
| `executor` ("rx") | read, execute | worker agent (the "registers with rx rights" principal) |
| `operator`/`viewer` | read | dashboard/monitoring, cockpit |
| `admin` | all | server operator |

### 3c. Identity model — staged, matching `PROTOTYPE_TO_PRODUCTION.md:62-63`
- **V1 (trusted-LAN hardening):** replace the single secret with **named principals → role-set**, each
  bound to a static credential (still no mTLS — smallest step that yields real RBAC). The server derives
  granted rights from the **credential**, never from the client-asserted `X-N4C-Role` header (which stays
  advisory). `python_entrypoint` stays double-gated (`--allow-python-jobs` server + `--allow-python`
  worker, `app.py:215-219`) **and** additionally requires the principal's `submit` right to include a
  `python` grant — never enabled when a third party can submit (non-goal `security-and-scope.md:26`).
- **Post-V1 (multi-tenant):** mTLS/OIDC, per-identity credentials, token rotation, per-task sandbox +
  quotas (`PROTOTYPE_TO_PRODUCTION.md:62-63`). Out of `LOCK-CLU` V1 scope; the role/right vocabulary above
  is the stable seam that survives the credential-mechanism swap.

### 3d. Registration-with-rights handshake (small **`NET-NEW`** additive field)
`WorkerRegister` (`schemas.py:208-213`) has no rights field today — correct, because **rights are
credential-bound, not self-declared**. `LOCK-CLU`: registration is authorized iff the credential carries
`execute`; `WorkerRegistered` (`:216-219`) **may echo** the granted `rights[]` for client-side diagnostics
(additive, non-breaking). The server records the worker under its authenticated principal so `admin`
eviction and audit have an identity to act on.

---

## 4. `CLU-001` — optional core/SDK client

`ClusterClient` (`client.py:68`) is **already** the thin SDK: REST-only, never imports `nirs4all`
(`client.py` docstring + verified no import), submit/wait/get_result/artifacts. It already matches the
design's `ClusterProvider`/`ClusterClient` surface (`MULTIMODAL_ECOSYSTEM_DESIGN_SCHEMAS.md:570-577,804-811`:
`register/submit/status/cancel/artifacts/worker_capabilities`).

`CLU-001` work = expose this client as an **optional** core/runtime plugin (per design §4bis "cluster is an
execution provider", and `RT-002`'s `execution_backend="cluster"`), so apps don't re-plumb
submit/status/artifact. **`NET-NEW` (small):** a `register/version handshake` helper surfacing `API_VERSION`
+ granted rights, and a typed `diagnostics()` that maps cluster refusals to the `RtError` envelope (§7).
**Red-line:** the core client wraps the REST surface; it does **not** absorb scheduler/worker logic and does
**not** import `nirs4all`.

---

## 5. `CLU-005` — Studio / CLI adapters (the seam already exists, typed-but-off)

**Studio already types `cluster` as an execution backend and ships an *unavailable* driver** awaiting
configuration:
- `ExecutionBackend = Literal["local-python","cluster","wasm-local"]` (`nirs4all-studio/api/execution_driver.py:13`).
- `CLUSTER_UNAVAILABLE_CAPABILITY` (`:305-313`): `available=False`, reason `driver_unavailable`, message
  *"Cluster execution is typed but no cluster driver is configured."*; registered in `_DRIVERS["cluster"]`
  (`:380`).
- Studio's pristine audit already lists `nirs4all_cluster` among **adapter-only** imports
  (`nirs4all-studio/docs/STUDIO_PRISTINE_AUDIT.md:406`).

So `CLU-005` = provide a **real** Studio driver wrapping `ClusterClient` (flips `available=true`,
`supports_progress`/`supports_cancellation=true`) **inside the Studio adapter layer** (BACKEND_RULES: never
reimplement nirs4all logic), replacing the local `JobManager` **opt-in**. Event-vocabulary mapping is
already specified in `PROTOTYPE_TO_PRODUCTION.md:78-83`: cluster job states `queued/running/succeeded/failed/
cancelling/cancelled` → Studio WS `job_started/job_progress/job_completed/job_failed/job_log` on channel
`job:{id}`. CLI adapter (`n4cluster`, `CLAUDE.md:56-63`) already covers submit/status/logs/cancel/artifacts.

---

## 6. `CLU-006` — benchmarks queue path

`nirs4all-benchmarks` (the Arena) is the natural `submitter`-role consumer: `BenchmarkProvider.queue` /
`queue_evaluation` (design §4bis.2) maps to `ClusterClient.submit_run(pipelines=…, datasets=…)`
(Level-1 cartesian). **Red-line (roadmap `PROV-003`, `CLU-006`):** the cluster runs the jobs and returns
artifacts/ranking; the **benchmark store remains the Arena's**, disconnected from repository/datasets/core
writes. The cluster never becomes the benchmark result catalog.

---

## 7. Job model & relation to `LOCK-RT` verbs

The cluster is **one realization of the RT runtime surface where `execution_backend="cluster"`**. Mapping
(faithful to today's black-box `nirs4all.run()` boundary, `PROTOTYPE_DESIGN.md:557`):

| RT verb (`RT_spec.md`) | Cluster V1 realization | Status |
|---|---|---|
| `run` | `POST /v1/jobs` → decompose → worker subprocess `nirs4all.run(workspace=task_ws)` (the run may itself be `engine=legacy` or `dag-ml`) | existing |
| `inspect`/`validate`/`plan` | done **client-side / by Studio before submit** in V1; cluster exposes no separate verb | **`NET-NEW` (optional)** `/v1/validate` preflight, post-V1 |
| `predict` | post-V1 (today `nirs4all.run` is the only job type, `schemas.py:161`) | post-V1 |
| `replay`/`export` | `.n4a` returned as a task artifact (`Outputs.export_best_model`, `schemas.py:139`) | existing (export); replay post-V1 |

**Result envelope bridge (the key `LOCK-RT` alignment):**
- `RtRunRequest` (`{pipeline_dsl, dataset_ref, cv, execution_backend, options}`) → `JobRequest`
  (`pipeline(s)/dataset(s)/params/requirements`). `execution_backend="cluster"` selects this path.
- Today the cluster returns a **coarser** projection than `RtResult.reports[]` (= dag-ml `ScoreSet`):
  `TaskResult.metrics` is a flat `RunMetrics` (`schemas.py:259-265`) and `JobAggregate.ranking`
  (`:306-316`). **V1:** cluster returns the **`.n4a` bundle + summary**; full `RtResult`/`ScoreSet` fidelity
  is obtained by reading the returned native results, **not** from the cluster wire — honest and lossless at
  the artifact level.
- **Post-V1 (`NET-NEW`):** have `TaskResult` carry/reference the native `ScoreSet` so cluster results
  *are* `RtResult` views (one more producer of the same envelope Studio/Web already consume). This is the
  clean convergence point with `LOCK-RT`; it depends on `L5` native-results export maturing
  (`A3_A3-dagml.md` DML-008 native `.n4a` export).
- `RtError` ← `TaskFailure{error, retriable}` (`schemas.py:282-285`) + version `426` + driver-unavailable
  (`execution_driver.py:305-313`). Mapping table for `LOCK-CLU` (vocabulary **owned by `CAP-004`**, RT just
  carries it): `TaskFailure(retriable=false)` → `cause:runtime_error`; capability mismatch (no eligible
  worker) → `cause:unsupported_capability` + mitigation "add a worker with labels/packages/GPU X"; `426` →
  `cause:unavailable_backend`/protocol; python-gate refusal (`app.py:215`) → `cause:invalid_request`.

---

## 8. `CLU-003` — worker capabilities, and its relation to `LOCK-CAP` (keep namespaces separate)

There are now **three distinct capability namespaces**; conflating them is the trap `LOCK-CAP` §1f already
warns about. `LOCK-CLU` must keep them separate:

| Namespace | Owner | Examples | Used for |
|---|---|---|---|
| `ControllerCapability` (19) | `LOCK-CAP` / dag-ml manifest | `thread_safe`, `needs_python_gil`, `emits_predictions` | per-operator portability classification |
| process-adapter capabilities | dag-ml `process_adapter_description` | `one_shot`/`jsonl`, `node_task_json_v1` | host↔controller transport |
| **worker/host capabilities** | **`nirs4all-cluster`** | `labels`, `gpu_count`/`gpu_names`/`cuda_version`, `memory_gb`, declared package versions, slots, data locality | **deployment routing** (`requirements_match`) |

`CLU-003` = the **third** (host/deployment) namespace: it already carries labels + GPU (auto via
`nvidia-smi`, `CLAUDE.md:115-118`) + memory floor + declared package versions
(`scheduler.py:84-113`; `WorkerRegister.capabilities/version`, `schemas.py:208-213`). It is **not**
`ControllerCapability` and must not be merged into the manifest enum. Two faithful reuses of `LOCK-CAP`
*shape* (not vocabulary): (1) the `unsupported {cause_code, mitigation}` envelope shape for "no eligible
worker" refusals; (2) `data_locality` labels become load-bearing only post-V1 (today `worker_local` behaves
like `shared_path`, `CLAUDE.md:144`; `catalog` is an explicit `NotImplementedError`,
`PROTOTYPE_TO_PRODUCTION.md:69`). `portable_level` (a per-operator classifier) does **not** apply at the
host/worker level — do not stamp it on workers.

---

## 9. Distributed == local parity gates

| Level | Parity status | Gate `LOCK-CLU` requires |
|---|---|---|
| L0 atomic | **metric-identical, diff = 0.0** (`PROTOTYPE_TO_PRODUCTION.md:18`) | keep as a CI gate; wire into program oracle |
| L1 `pipelines×datasets` | **metric-identical** (independent tasks; aggregation is rank-only) | per-task L0 parity ⇒ job parity; ranking determinism (`aggregate_metric_better`) |
| L2 explicit variants | **no parity promise** (non-goal) — selection/refit semantics not reproduced by rank aggregation | **blocked**: needs a written L2 parity measure before any auto-variant decomposition |
| L3 folds | non-goal (postponed) | n/a in V1 |

Mechanics already present to enforce parity: `pipeline_fingerprint` (`schemas.py:273`) + canonical
`fingerprint_obj/_file` (`versioning.py:73-84`) trace that the worker ran exactly what was submitted
(`expected_fingerprint` mismatch → divergence event, never fatal, `schemas.py:74-76`). **`NET-NEW` for the
program:** add a **cluster-vs-local parity case to the `PYREF`/conformance oracle** (`L17`), so "cluster
result == `nirs4all.run()` result" is a *checked* gate in the refactoring CI, not only a one-off
`scripts/validation.py` measurement. The fine-grain parity criterion for any future decomposition is
**fingerprint-identical predictions/scores (≤ 1e-10)** (`DISTRIBUTED_EXECUTION_DESIGN.md:175`), and the
cluster **propagates** fingerprints — it never recomputes them differently (`DISTRIBUTED_EXECUTION_DESIGN.md:135`).

---

## 10. Failure / retry semantics (already implemented — `LOCK-CLU` freezes them)

All verified in `server/scheduler.py` + `CLAUDE.md:113-129`:
1. **Lease + TTL + heartbeat renew** (`schemas.py:218-219`): a long task is not reaped while its worker is
   healthy; silent worker ⇒ lease lapses ⇒ requeue (or fail after attempts).
2. **Bounded retry** `max_attempts` 1..10 (`schemas.py:144-145`); `LOST→QUEUED`/`FAILED→QUEUED` transitions
   (`scheduler.py:30-33`).
3. **Idempotency** `idempotency_key` dedupe (unique index + `IntegrityError` race handling, `CLAUDE.md:128`).
4. **Cooperative cancellation** via `HeartbeatAck.cancel_task_ids` (`schemas.py:225`); the agent terminates
   the matching subprocess; **a cancelled job's reaped lease never relaunches** (`CLAUDE.md:128`).
5. **No slot drift**: slot usage derived live from the task table (`_in_flight_count`), never a mutable
   counter (`CLAUDE.md:101-104`) — survives reaping/revival/races.
6. **Idempotent terminal flip**: `_finalize_job`/`try_set_job_status` so concurrent last-task completions
   can't double-flip the job (`CLAUDE.md:106-108`).
7. **Protocol safety**: incompatible major → 426; oversized JSON → 413 (`docs/rest-api.md:47`).
**State changes go through the state machine** (`scheduler.py` first, DB enforces) — `LOCK-CLU` forbids
ad-hoc `UPDATE … status` (`CLAUDE.md:138-140`). RBAC (§3) adds an **authorization** layer *above* these;
it does not alter the transition tables.

---

## 11. V1 vs post-V1 fine-grained DAG scheduling (the load-bearing scope call)

### V1 (`LOCK-CLU` signs this) — whole-run, capability-routed, hardened
- Levels **0 + 1** only (proven parity); `JobRequest` cartesian (`schemas.py:181-191`).
- **RBAC** role/right model (§3); optional **core client** (§4); **Studio/CLI adapters** (§5);
  **benchmarks** submitter path (§6); **`RtResult`/`RtError` envelope** binding at the artifact level (§7);
  **cluster-vs-local parity gate** in the oracle (§9); failure/retry frozen (§10).
- Scheduler stays **whole-run capability routing** — FIFO+priority+labels+slots+GPU+packages
  (`scheduler.py`). "Adapted to NIRS4ALL DAG" is **aspirational at V1**: today it routes `run()`s, not DAG
  nodes. State this honestly.

### Post-V1 — fine-grained DAG (Levels 2/3), **must route through `dag-ml`**
`DISTRIBUTED_EXECUTION_DESIGN.md` maps three distributable grains in the real engine: **A** variant
(already a process-safe scatter-gather, `orchestrator.py`), **B** `(variant, fold)` (folds loop in the model
controller, picklable `fold_args`), **C** subtree/preprocessing (cross-variant cache key
`(chain_path_hash, input_data_hash)`). What is **missing is the control plane**, not the engine
(§4 of that doc): explicit graph/task reification, remote task transport, a **distributed data provider**
(resolve `DataSelector` remotely without moving datasets), and a **shared content store** (serve artifacts
by `content_hash`).

`LOCK-CLU` post-V1 rule (binding, = `CLU-004` + North Star):
- **Do not invent a parallel scheduler that bypasses `dag-ml`.** Fine-grained units = `dag-ml` `NodeTask`
  scopes `(variant, fold, phase)`; cluster maps "ship `variant_data`/`fold_args`" → `NodeTask`, "serve
  artifacts by hash" → object store, "GPU placement" → GPU routing
  (`DISTRIBUTED_EXECUTION_DESIGN.md:161-163`). Recommended trajectory (a): expose the `nirs4all` engine as a
  **host controller of `dag-ml`** (`NodeTask → OperatorController.execute`; `NodeResult ← StepOutput` +
  content-addressed artifact). Trajectory (b) "thin orchestrator" is explicitly flagged as risking a
  re-implemented mini-`dag-ml` — avoid.
- Therefore fine-grained scheduling is **gated on `L5` (dag-ml runtime exposes the coordinator/native
  orchestration; `A3_A3-dagml.md` DML-002 migrates branch/generator/rep-fusion/augmentation down) and
  `L16` (controller adapter)** — exactly the `L15` blocker the sync board records (line 77).
- L2 explicit-variant distribution additionally requires the **written L2 parity measure** (§9) first.
- Server-initiated **push transport** and **Postgres/S3** multi-server scale-out
  (`PROTOTYPE_TO_PRODUCTION.md:58-60`) are post-V1 infra, independent of the DAG question.

---

## 12. Boundaries / red-lines `LOCK-CLU` must preserve

- **Only `runners/nirs4all_run.py` imports `nirs4all`** (§1b). Non-negotiable.
- Cluster **never owns** parsers, kernels, ML schemas, or graph/OOF/leakage/selection semantics — it
  consumes runtime + `dag-ml` contracts (design §5.5; `DISTRIBUTED_EXECUTION_DESIGN.md:127-136`). Anti-leakage
  / OOF / selection / refit / fingerprints stay authoritative in `nirs4all`/`dag-ml`.
- Beta **non-goals** stay in force (`docs/security-and-scope.md:23-29`): no modifying other libs; no open
  multi-tenancy; no secure sandbox for arbitrary Python; no K8s/Ray/Dask-class scheduler; no concurrent
  writes to a shared `nirs4all` workspace; no fold distribution; no L2 parity promise.
- `LOCK-CLU` is a **beta-hardening** contract; it does **not** preempt the open native-vs-`nirs4all[dask]`
  product decision (`PROTOTYPE_TO_PRODUCTION.md:7-9,29-38`).

---

## 13. Proposed `DEC-CLU-001` sign content + `LOCK-CLU` skeleton (for A0)

```
DEC-CLU-001 (accept): Cluster = harden the EXISTING /v1 beta (client/server/workers), not a new scheduler.

LOCK-CLU (proposed) — Cluster distribue. Source DEC-CLU-001. Owner L15.
 CL1. Preserve red-lines: only runners/nirs4all_run.py imports nirs4all; cluster owns no parser/kernel/
      ML-schema/graph-semantics; state changes go through the scheduler.py state machines.
 CL2. RBAC (NET-NEW, V1): rights {submit, read, cancel, execute, admin} composed into roles
      {submitter, executor("rx"=read+execute), viewer, admin}, mapped onto today's routes (no new routes).
      Rights are credential-bound and server-derived; X-N4C-Role stays advisory. python_entrypoint stays
      double-gated + needs an explicit python grant. mTLS/OIDC/rotation = post-V1; vocabulary stable across.
 CL3. Client/server/workers model: "rx" = read+execute right-set; "server asks to execute" = server-
      authoritative assignment delivered on the worker long-poll lease (PULL). Push transport = post-V1.
 CL4. Job/RT binding: execution_backend="cluster" selects the cluster path; RtRunRequest->JobRequest;
      RtError<-{TaskFailure, 426, driver_unavailable} carrying CAP-004 vocab. V1 returns .n4a+summary;
      TaskResult-carries-native-ScoreSet (RtResult fidelity) = post-V1, gated on L5 native export.
 CL5. Worker/host capabilities are a THIRD namespace (labels/GPU/memory/packages/locality), SEPARATE from
      ControllerCapability and process-adapter capabilities; reuse only the {cause,mitigation} envelope SHAPE.
 CL6. Optional core/Studio/CLI client (CLU-001/005): ClusterClient is the REST-only SDK; Studio driver
      wraps it in the adapter layer (cluster backend already typed-but-unavailable), opt-in over JobManager.
 CL7. Parity gates: L0/L1 metric-identical (diff=0.0) becomes a checked PYREF/conformance case; fingerprints
      propagated, never recomputed; fine-grain criterion = fingerprint-identical <=1e-10.
 CL8. Scope: V1 = Levels 0/1 + RBAC + adapters + client + RT envelope + parity gate + frozen failure/retry.
      Post-V1 fine-grained DAG (Levels 2/3, grains A/B/C) MUST route through dag-ml NodeTask scopes
      (do not bypass dag-ml); gated on L5 + L16, and L2 needs a written parity measure first.
 CL9. LOCK-CLU is a beta-hardening lock; it does not preempt the native-vs-nirs4all[dask] product decision.
```

---

## 14. Open questions + gates

**Open questions (A0 / maintainer):**
1. **RBAC credential mechanism for V1**: named-static-tokens→role (smallest step, trusted-LAN) vs jump
   straight to mTLS/OIDC? SW7 recommends named-static-tokens for V1, mTLS/OIDC post-V1 (§3c).
2. **`RtResult` fidelity timing**: accept V1 "`.n4a`+summary, full ScoreSet via artifact read", with
   `TaskResult`-carries-`ScoreSet` deferred to post-V1 (gated on `L5` DML-008)? (§7) — **Gate: `L5`.**
3. **Transport**: confirm PULL-only for V1 (push post-V1)? (§2,§11)
4. **Where the optional client lives**: `nirs4all-cluster` ships it (today's `ClusterClient`) vs core
   re-exports it — depends on `LOCK-GOV` core topology. **Gate: GOV.**
5. **Push the cluster-vs-local parity case into `L17`'s oracle** (owner L15 or L17?). (§9)
6. **L2 parity measure** owner/spec before any explicit-variant decomposition (§9,§11).

**Gates to run (none run here — read-only):**
- `ruff check . && mypy nirs4all_cluster && pytest -q` (45 unit/API tests, no `nirs4all` needed) —
  `nirs4all-cluster/CLAUDE.md:41-43`.
- `…/nirs4all/.venv/bin/python -m pytest tests/test_integration_nirs4all.py -q` (needs nirs4all venv).
- `…/nirs4all/.venv/bin/python scripts/validation.py` — real OS processes, SIGKILLs a worker to prove
  recovery + measures local-parity (the distributed==local gate, §9).
- Program-side: add a cluster-vs-local parity case to `nirs4all/tests/integration/parity/` (`L17`).

**Worklog line (for A0 to paste — I did not edit the board):**
`2026-06-30 | SW7/L15 | review | CLU-SPEC: harden existing /v1 beta. RBAC {submit/read/cancel/execute/admin}`
`over current single-token (auth app.py:171, no role sep today); "rx"=read+execute executor client; PULL`
`lease = server-authoritative assignment. RtRunRequest->JobRequest, RtError<-{TaskFailure,426,driver_unavail};`
`RtResult fidelity via .n4a now / native-ScoreSet post-V1 (gated L5). Worker caps = 3rd namespace, separate`
`from ControllerCapability. Studio cluster driver typed-but-unavailable (execution_driver.py:305) = the`
`adapter seam. Parity L0/L1 diff=0.0 -> wire into L17 oracle. V1=Levels0/1; fine-grained DAG (grains A/B/C)`
`post-V1, MUST route through dag-ml (CLU-004/North Star), gated L5/L16. Red-line preserved: only`
`runners/nirs4all_run.py imports nirs4all. No code/sync edits.`

---

### Evidence (heads, read-only; only this file written)
`nirs4all-cluster dcced30`: `nirs4all_cluster/{schemas,client,versioning}.py`,
`nirs4all_cluster/server/{app,scheduler}.py`, `CLAUDE.md`, `PROTOTYPE_DESIGN.md`,
`PROTOTYPE_TO_PRODUCTION.md`, `docs/{rest-api,security-and-scope,DISTRIBUTED_EXECUTION_DESIGN}.md`,
`docs/concepts/{architecture,job-decomposition}.md`. Cross-refs: `nirs4all-studio/api/execution_driver.py`,
`nirs4all-studio/docs/STUDIO_PRISTINE_AUDIT.md`; `nirs4all-ecosystem/docs/{PARALLEL_REFACTORING_SYNC,
PARALLEL_REFACTORING_ROADMAP,MULTIMODAL_ECOSYSTEM_DESIGN_SCHEMAS}.md` and
`docs/agent_reports/{CAP_spec,RT_spec,A3_A3-dagml}.md`.
