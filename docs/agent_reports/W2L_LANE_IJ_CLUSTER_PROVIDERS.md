# W2L Lane I/J Cluster / Providers / Repository / Benchmarks / Papers

Date: 2026-07-01

## Agent

Codex Lane I/J post-reset, no Claude tools used.

## Lane

Lane I/J: `nirs4all-cluster`, `nirs4all-providers`, `nirs4all-repository`,
`nirs4all-benchmarks`, `nirs4all-papers`.

## Files modified

- `nirs4all-ecosystem/docs/agent_reports/W2L_LANE_IJ_CLUSTER_PROVIDERS.md`

No code files were modified. `nirs4all-drafts` and `nirs4all-lab` were not touched.

## Evidence

### Post-reset checkout vs preserved integration heads

- `nirs4all-cluster` current checkout:
  - branch `main`, head `dcced303543e`, clean.
  - preserved integration worktree `_worktrees/INT-cluster`, branch
    `refactor/integration-cluster`, head `eac4d0b8a62a`, clean.
  - current `main` is an ancestor of `eac4d0b8a62a`; the integration head is not in
    current `main`.
  - missing integration commits include W19/W28/W38/W47/W58/L15/W88:
    `259d598`, `7a8d48f`, `bd8ce70`, `4ffda1d`, `e2a99c2`, `b70ca42`,
    `ffad507`, `eac4d0b`.
  - diff size from current to integration: 27 files, 3247 insertions, 216 deletions.
  - W88-specific behavior is report-backed and code-backed in the integration head:
    `_reaper_loop` calls `db.reap_tasks_for_workers(dead)` before lease expiry; `Database`
    adds `_resolve_lost_task()` and `reap_tasks_for_workers()`; tests cover dead-worker
    requeue/cancel and stale completion rejection.

- `nirs4all-providers` current checkout:
  - branch `main`, head `3ecc67915786`, clean.
  - preserved integration worktree `_worktrees/INT-providers`, branch
    `refactor/integration-providers`, head `1e289a9ee96d`, clean.
  - current `main` is an ancestor of `1e289a9ee96d`; the integration head is not in
    current `main`.
  - missing integration commits include W18/W27/W48/W57/W80/W89:
    `2411568`, `55f79cd`, `074d07d`, `441d3b7`, `a9fb457`, `1e289a9`.
  - diff size from current to integration: 16 files, 1068 insertions, 76 deletions.
  - current checkout is the original L14 read-adapter slice: `PipelineProvider` exposes
    `list_pipelines` but not `get_pipeline_list`/`recipe`, and `BenchmarkProvider`
    has no `queue_pipeline_test`.
  - integration head adds the bounded local planning adapter:
    `BenchmarkProvider.queue_pipeline_test(...)` delegates to
    `nirs4all_benchmarks.ingestion.upload`, writes only local Arena `planned_runs`,
    keeps `executes=False`, returns the backing `UploadResult.to_json()` shape, and
    validates non-empty target dataset tokens before opening the store.

### Architecture boundaries

- `nirs4all-cluster`:
  - Current checkout preserves the core import boundary: `rtk grep "import nirs4all|from nirs4all" nirs4all_cluster`
    found only `nirs4all_cluster/runners/nirs4all_run.py:114` plus a comment in
    `worker/executor.py`.
  - The runner executes `nirs4all.run(...)` in a subprocess and emits a summarized
    `result.json`; the server, worker agent, materializer, and executor remain
    `nirs4all`-free.
  - Current scheduler is DAG-aware at the whole-run contract level, but the W88
    deterministic dead-worker path and credential-bound DAG provenance remain
    integration-head-only until `eac4d0b8a62a` is merged/replayed.

- `nirs4all-repository`:
  - Current code matches the documented boundary: `list/card/get/fetch` resolve the
    static catalogue local-first, bundled, then remote; `Pipeline.recipe()` returns
    canonical recipe data; `to_nirs4all()`/`to_dagml()` only hand recipes to the owning
    framework surface.
  - No benchmark execution or ranking logic is present in the repository surface.
    Evaluation is a CLI/maintenance command against reference datasets, not Arena
    scoring.

- `nirs4all-benchmarks`:
  - Current code implements the Arena as a sink/store/query layer. `upload()` routes
    result-bearing `ArenaRunExport`/dag-ml bundles to `ingest_export`; bare recipes and
    `.n4a` bundles go to `register_pipeline`.
  - `register_pipeline()` upserts pipeline dimensions and creates/detects local
    `planned_runs`; it does not execute pipelines.
  - `.n4a` handling in `adapters/n4a_bundle.py` reads `manifest.json`/`pipeline.json`,
    lists `artifacts/*` as stripped artifacts, and never reads fitted artifact bytes.
  - This matches the boundary: benchmarks consumes/tests/ranks pipelines and stores
    weights-free results, without writing back to repository/datasets/papers.

- `nirs4all-papers`:
  - Current code implements the reproduction publisher as a local static-site/export
    tool. `read_bundle()` uses `zipfile`/`json`/`hashlib` to inspect `.n4a` bundles and
    fingerprint members; it does not import `nirs4all`.
  - `build_site()` is marker-guarded with `.n4a-papers-build`, refuses to wipe unknown
    non-empty output directories, writes local sidecars (`CITATION.cff`,
    `references.bib`, `ro-crate-metadata.json`, `pipeline.json`), and copies the
    deposited bundle verbatim.
  - The live replay remains the documented approximate JS reference path; the libn4m
    WASM replay swap is still future integration.

### Implemented vs report-only vs needs integration

- Implemented in current checkouts:
  - Repository static catalogue/read/verify/bridge API.
  - Benchmarks ingestion, upload-to-plan, planned-runs, stripped `.n4a` recipe path,
    and read queries.
  - Papers local reproduction publisher with marker-guarded output and sidecars.
  - Cluster base trusted-LAN queue, subprocess runner boundary, matrix decomposition,
    lease/retry/cancel basics, and import boundary.

- Implemented only in preserved integration heads:
  - Cluster W88/L15/W58 chain: credential-bound RBAC, DAG rights/provenance metadata,
    deterministic dead-worker task recovery, stale reporter rejection, and expanded
    parity/RBAC tests.
  - Providers W80/W89 chain: explicit `get_pipeline_list` contract, repository
    `recipe()` read method, richer benchmark read surface, and local
    `queue_pipeline_test()` planning adapter.

- Still report-only or future integration:
  - Providers are not integrated into the current `main` checkout and are not yet a
    stable ecosystem-wide service interface until the preserved head is reviewed and
    merged/replayed.
  - Cluster remains whole-run DAG-aware; it does not and should not duplicate runtime
    fold/variant semantics. Deeper DAG/fold distribution remains out of scope.
  - Papers replay productionization through libn4m WASM is documented but not landed.
  - Repository-to-benchmarks continuous public scoring is still an integration step,
    not a repository write path.

## Tests/gates run

- `cd nirs4all-cluster && rtk uv run --extra dev pytest tests/test_scheduler.py tests/test_server_api.py -q`
  - Passed: 39 tests, 1 Starlette/httpx deprecation warning.
- `cd nirs4all-providers && rtk env PYTHONPATH=src python3.11 -m pytest -q`
  - Passed: current provider test suite, 35 tests observed.

Previously reported gates for preserved heads were also reviewed:

- W88 cluster integration head: `ruff check .`, `mypy nirs4all_cluster`, targeted tests,
  and full `pytest -q` reported as passing (`133 passed, 1 skipped`).
- W89/W80 providers integration heads: `pytest`, `ruff`, and `mypy` reported as passing
  with `PYTHONPATH=src` / Python 3.11.

## Risks

- The current reset checkouts are clean but behind the preserved integration heads;
  consumers looking at `main` will not see W88 cluster fixes or W80/W89 provider service
  contracts.
- Cluster current `main` can leave dead-worker in-flight tasks waiting for lease expiry;
  W88 fixes this in `INT-cluster`.
- Providers current `main` advertises a narrower read-only slice than the desired
  pipeline-service contract; local Arena planning is integration-head-only.
- Integration should not blindly copy reports as proof: merge/replay the preserved
  commits with review, because other lanes are moving in parallel.
- Papers replay is honest but approximate; do not market it as portable numerical
  parity until the libn4m WASM seam is landed and tested.

## Decisions needed

- Decide whether `nirs4all-cluster` should integrate the whole preserved
  `refactor/integration-cluster` head or replay a smaller W88/L15/W58 subset onto
  current `main`.
- Decide whether `nirs4all-providers` should integrate the full
  `refactor/integration-providers` head as the provider service contract baseline.
- Decide the naming contract for provider pipeline listing before external consumers
  bind to it: `get_pipeline_list` as primary with `list_pipelines` compatibility is the
  integration-head design.
- Decide who owns fulfillment of `benchmarks.planned_runs` after provider planning:
  a future runner/cluster bridge should execute elsewhere and then ingest
  `ArenaRunExport`; benchmarks itself must stay non-executing.
- Decide timing for the papers libn4m WASM replay upgrade; current JS replay is
  suitable only as an approximate publication companion.

## Recommended integration steps

1. Review and merge/replay `nirs4all-cluster` integration head `eac4d0b8a62a` onto the
   current checkout, preserving the runner-only `nirs4all` import invariant.
2. After cluster integration, run:
   `uv run --extra dev ruff check .`,
   `uv run --extra dev mypy nirs4all_cluster`,
   `uv run --extra dev pytest -q`,
   plus the sibling-venv integration test if `nirs4all` data is available.
3. Review and merge/replay `nirs4all-providers` integration head `1e289a9ee96d` onto
   current `main`; keep repository read-only, benchmark planning local-only, and papers
   local-output-only.
4. After provider integration, run:
   `PYTHONPATH=src python3.11 -m pytest -q -ra`,
   `python3.11 -m ruff check .`,
   `PYTHONPATH=src python3.11 -m mypy src`.
5. Add cross-repo integration tests only after the heads are merged: repository
   `get_pipeline_list`/`recipe` -> benchmarks `queue_pipeline_test` -> planned run ->
   external runner -> `ArenaRunExport` ingest. The test should assert no write-back to
   repository/datasets/papers and no benchmark-side execution.
6. Keep `nirs4all-papers` unchanged for this wave unless a released public paper bundle
   is being added; any future replay upgrade should be a separate, explicitly reviewed
   libn4m WASM integration.
