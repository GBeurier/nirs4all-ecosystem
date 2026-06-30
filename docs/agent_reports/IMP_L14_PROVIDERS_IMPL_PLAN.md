# IMP_L14_PROVIDERS_IMPL_PLAN — implementation map for provider/plugin adapters

**Lane:** `L14` (Providers/plugins) · **Decision:** `DEC-PROV-001` (proposed, P1 `ARB-010`)
**Agent:** `IMP-L14` (provider/plugin integration) · **Mode:** read-only audit → **implementation map**. No code/test/sync-board edits; this file is the only write.
**In scope:** `nirs4all-datasets`, `nirs4all-repository`, `nirs4all-benchmarks`, `nirs4all-papers`. **OUT:** `nirs4all-drafts`, `nirs4all-lab` (private; never modeled as ecosystem bricks).
**Builds on:** `SW6_PROV_PLUGINS_spec.md` (the contract audit). This report is the **buildable layer under it**: exact functions/routes/CLIs to wrap, adapter file names, read/write boundaries, the first minimal PR slice per provider, and the contract decisions that still block `DEC-PROV-001`.

**Verification method (independent re-check, not inherited from SW6):** direct `Read`/`Grep`/`Bash` against the working-tree heads on `main` (all four repos **clean**, dirty count 0). Every API row below was opened and read this pass; every `[NET-NEW]`/absence claim was re-grepped. The single cross-repo grep `class \w*Provider|ProviderPlugin|provider_id|def capabilities\(|registry` over all four `src/` trees returns **0 matches** — there is no provider class, base, or registry anywhere. L14 is an **adapter-and-surface job**, confirmed.

**What this report adds over the SW6 spec (the delta):**
1. A concrete **home + import topology** for the client layer, with a **dependency-cycle hazard** the audit did not surface (§1).
2. A **per-provider adapter file map** with exact method→`file:line` wiring tables, re-verified at heads (§3–§6).
3. A **PR DAG**: one keystone scaffold PR + the first minimal slice per provider, each with files, ~LOC, and the exact green-gate command (§7, §9).
4. The **contract decisions for `DEC-PROV-001`** distilled to 7 items, each with a recommendation and the gate it waits on (§8).

---

## 0. TL;DR

- **Nothing to invent inside the four repos for the read path.** Each already ships the real API; the adapter is a thin uniform client over it. Wrap, don't reimplement (this is `DEC-PROV-001`: *"renommer sur les vraies APIs; couche provider unifiante = net-new"*).
- **The one real architectural choice is *where the client layer lives*** — and it is load-bearing because three of the four providers already depend on `nirs4all` (as an optional extra). Putting the client layer **inside `nirs4all` as a hard dep would create an install cycle.** Recommendation: a standalone, dependency-light `nirs4all-providers` package (soft-imports each provider as an optional extra), foldable into `nirs4all-core` once `LOCK-GOV` lands. (§1, decision **D1**.)
- **First buildable unit = the scaffold** (`ProviderPlugin` Protocol + soft-import registry), then four independent read-only adapter PRs, each mergeable alone. No execution, no write, no `LOCK-IO`/`LOCK-RT`/`LOCK-UI` dependency in slice 1.
- **Net-new beyond the client layer (all deferred past slice 1):** `DatasetProvider.to_dataset_package` (gated `LOCK-IO`), benchmark `get_pipeline(dag_hash)` getter (trivial, adapter-side), benchmark `queue_evaluation` runner orchestration (gated `LOCK-RT`/`CLU-006`), papers methods-bibliography **re-distill gate** (methods/`L9`), optional papers `nirs4all-ui` rendering (gated `LOCK-UI`).

---

## 1. Where the adapter layer lives (decision **D1**, the keystone)

### 1a. The dependency-cycle hazard (new finding)
`nirs4all/pyproject.toml` does **not** depend on any provider today (re-grepped: 0 hits). But the providers depend *up* on `nirs4all`:

| Provider | Declares `nirs4all` as | Source |
|---|---|---|
| `nirs4all-datasets` | extra `[nirs4all] = nirs4all>=0.9` | `pyproject.toml` `[project.optional-dependencies]` |
| `nirs4all-repository` | extra `[nirs4all] = nirs4all>=0.10,<0.11` | idem |
| `nirs4all-benchmarks` | extra `[nirs4all] = nirs4all>=0.10` | idem |
| `nirs4all-papers` | **none** (runtime dep = PyYAML only) | idem |

If the client layer is a **subpackage of `nirs4all` that hard-depends on the providers**, the required-dependency graph becomes `nirs4all → nirs4all-repository → nirs4all` — a cycle. It is avoidable only by keeping the providers **optional** (extras, soft-imported) on the `nirs4all` side, which is workable but couples the home to `nirs4all`'s release train (and its `>=0.10,<0.11` pin, see §1c).

### 1b. Recommended home — standalone `nirs4all-providers`, import-path-agnostic adapters
Put the four adapters + base + registry in a **new dependency-light package** that:
- hard-depends on **nothing** but `typing_extensions` (Protocol on 3.11 is stdlib; the dep is belt-and-braces);
- declares each provider as an **optional extra** (`[datasets] [repository] [benchmarks] [papers] [all]`), mirroring the providers' own extras pattern;
- **soft-imports** each provider and degrades to `health() = unavailable` when its extra is absent — exactly the pattern already used by `nirs4all-benchmarks/datasets/catalog.py` (`CatalogUnavailable` on missing `nirs4all-datasets`) and `nirs4all-datasets`' lazy `nirs4all` import.

This sidesteps the cycle (no provider depends on `nirs4all-providers`, and `nirs4all-providers` *requires* none of them), and it is consumed identically by `nirs4all` (the aggregate), `nirs4all-studio` backend (already guards `import nirs4all`), `nirs4all-lite`, and the CLI.

**The adapter source is the same wherever it lands** — the only thing decision **D1** changes is the package root (`nirs4all_providers/` vs `nirs4all/providers/` vs `nirs4all_core/providers/`). Throughout this report the file map is written relative to `<providers_root>/`; substitute the chosen root at build time. Open question `Q6`/`LOCK-GOV` (core topology) owns the final word; this report does **not** pre-empt it, it just makes the layer buildable today and movable later.

### 1c. Install-matrix caveat (one line, real)
With the `[all]` extra installed, the three `nirs4all` pins must co-resolve: `repository` is the tightest (`>=0.10,<0.11`), so the meet is `nirs4all >=0.10,<0.11`. The provider home must not pin `nirs4all` itself (it never imports it). Flag in the `[all]` extra docstring.

### 1d. Proposed file map (`<providers_root>/`)
```
<providers_root>/
  __init__.py        # re-export ProviderPlugin, the 4 adapters, get_provider/available_providers
  base.py            # ProviderPlugin Protocol {provider_id, version(), health(), capabilities()}
  registry.py        # soft-import discovery; get_provider(id), available_providers()
  datasets.py        # DatasetProvider      -> wraps nirs4all_datasets
  repository.py      # PipelineProvider     -> wraps nirs4all_repository
  benchmarks.py      # BenchmarkProvider    -> wraps nirs4all_benchmarks
  papers.py          # PaperExportProvider  -> wraps nirs4all_papers
  _softimport.py     # tiny helper: import-or-None + a uniform "extra missing" message
```
Every adapter is `~40–90 LOC`: a constructor that records the soft-imported module (or marks unavailable), then one method per row of the tables in §3–§6, each a 1–3 line delegation. No business logic — that stays in the provider repos.

---

## 2. Maturity / write-state matrix (re-grounded at heads)

| Provider | Read surface (verified) | Execute? | Write path (verified) | Slice-1 scope |
|---|---|---|---|---|
| `datasets` | `get`/`list`/`card`/`retrieve` + `NirsDataset` readers `[LANDED]` | no (assembly only) | publish = admin/governance-gated, **FUTURE** (`publish.assert_publishable` `:35-39`) | read + `to_spectro_dataset` |
| `repository` | `list`/`card`/`get`/`fetch`/`Pipeline.verify` `[LANDED]` | local `evaluate` only | **no ecosystem write** (`cli publish` = gate-check `:196-212`); no server (re-grepped: 0 `fastapi/uvicorn`) | read + verify |
| `benchmarks` | `Queries.*` + FastAPI `/api/*` `[LANDED]` | **no runner** (ingest-only; `register_pipeline` = plan rows `:167-176`) | Arena store **local only** (`/api/ingest`,`/api/upload` write local sqlite/parquet) | read (`pipelines`/`leaderboard`/`get_results`) + `get_pipeline` getter |
| `papers` | `read_bundle`/`build_bibliography`/`build_site`/sidecars `[LANDED]` | approximate in-browser JS replay only | export to `--out`, marker-guarded (`build_site` `:106-117`) | full read + build (all landed) |

---

## 3. `PROV-001` — `DatasetProvider` (`nirs4all-datasets`)

**Adapter file:** `<providers_root>/datasets.py` · **class** `DatasetProvider(ProviderPlugin)` · **wraps** `nirs4all_datasets` (`__version__ = "0.1.0.dev0"`).

### 3a. Exact API to wrap (re-verified at heads)
| Adapter method | Real API today (`file:line`) | Status |
|---|---|---|
| `list_datasets(**filters)` | `nirs4all_datasets.list(root, **filters) -> Sequence[dict]` (`__init__.py:58-62`) → `catalog.search` (filters `tier`/`domain`/`spectro_family`) | `[LANDED]` |
| `card(dataset_id)` | `nirs4all_datasets.card(name, root) -> dict|None` (`__init__.py:65-69`) → `catalog.get_card` | `[LANDED]` |
| `get_dataset(dataset_id, **opts)` | `nirs4all_datasets.get(name, *, source, split, token, instance, cache_dir, concat, reproduce) -> NirsDataset` (`__init__.py:34-55`) → `access.get` (local → DOI → OPEN origin) | `[LANDED]` |
| `to_spectro_dataset(dataset_id, **opts)` | `NirsDataset.to_nirs4all() -> SpectroDataset` (`dataset.py:305-349`; lazy `from nirs4all.data import SpectroDataset` `:324`) | `[LANDED]` |
| `retrieve(dataset_id, **opts)` *(raw acquisition, optional surface)* | `nirs4all_datasets.retrieve(name, *, route_id, cache_dir, token, instance, …) -> dict` (`__init__.py:72-97`) → `retrieval.retrieve` | `[LANDED]` |
| `to_dataset_package(dataset_id)` | **absent** (re-grepped `to_dataset_package|DatasetPackage` across all four `src/` = 0) — must route canonical Parquet through `nirs4all-io` assembly + the io→dagml bridge | **`[NET-NEW]`, gated `LOCK-IO`** |

**`NirsDataset` reader surface to expose verbatim through the returned handle** (all `dataset.py`, `[LANDED]`): `sources()` `:114`, `variables()` `:118`, `x(source, concat)` `:134`, `wavelengths(source)` `:184`, `observation_ids(source)` `:191`, `sample_ids(source=None)` `:195`, `y(name)` `:264`, `metadata(name)` `:278`, `split(name)` `:293`, `card()` `:100`, `descriptor`/`tier` `:78/:90`. Identity is **sample-keyed**, never row-position (`x(concat=True)` *refuses* a row-position concat across asymmetric sources, `:171-176`).

### 3b. Read/write boundary
- **Read:** all of §3a top rows. `get_dataset` resolution is local-first → personal-Dataverse DOI → OPEN origin (`access.get`); ordinary consumers write **nothing** outside the local pooch cache (`pooch.os_cache("nirs4all-datasets")/<id>/canonical/`).
- **Assembly owner stays `nirs4all-io`.** `to_spectro_dataset` builds a `SpectroDataset` *directly today* (bypasses io except the `get(..., reproduce=True)` path, which lazy-imports `nirs4all_io as nio` and calls `nio.load(...)`). The adapter exposes `to_spectro_dataset` **as-is for V1**; `to_dataset_package` is the `LOCK-IO` future and must route through io, **not** re-assemble in the adapter or core.
- **Write:** none in scope. Publish (`publish.py` `assert_publishable` `:35-39`, `publish_dataset`/`update_dataset`, CLI `publish`/`grant`/`revoke`/`restrict` `:314-414`) is admin-only + governance-gated against a **future** personal Dataverse; never wrapped by the provider client.
- **Auth/cache/versioning:** token only for `private`/`anonymized` via `X-Dataverse-key` header (resolution arg → `NIRS4ALL_DATAVERSE_TOKEN` → config → `.env`); downloads SHA-256-verified; two version axes (`versions.content` / `versions.schema_protocol`). The adapter **passes `token`/`instance` through**, never stores them.

### 3c. First minimal PR slice — `feat(providers): DatasetProvider read client`
- **Add** `<providers_root>/datasets.py`: `DatasetProvider` with `list_datasets`, `card`, `get_dataset`, `to_spectro_dataset` (4 delegations) + `version()`/`health()`/`capabilities()`/`provider_id="datasets"`. `health()` = `{available: <module import ok>}` (origin-health probe via `health.run_health_check` is **adjacent**, not provider liveness — do not conflate).
- **~70 LOC** + `tests/test_datasets_provider.py`: a `list → card → get → to_spectro_dataset` round-trip on a tiny local fixture catalog, asserting **no `nirs4all` import is required** for `list`/`card` (only `to_spectro_dataset` needs it).
- **Gate:** `cd <providers_root repo> && ruff check . && mypy src && pytest -q tests/test_datasets_provider.py`. Provider repo untouched → its own gate (`ruff check . && mypy src && python catalog/scripts/validate.py && pytest -q`) does not re-run.
- **No `to_dataset_package`, no publish, no `retrieve`** in this slice (retrieve is an optional later add; publish never).

---

## 4. `PROV-002` — `PipelineProvider` (`nirs4all-repository`)

**Adapter file:** `<providers_root>/repository.py` · **class** `PipelineProvider(ProviderPlugin)` · **wraps** `nirs4all_repository` (`__version__ = "0.1.0"`).

### 4a. Exact API to wrap (re-verified at heads)
| Adapter method | Real API today (`file:line`) | Status |
|---|---|---|
| `list_pipelines(**filters)` | `nirs4all_repository.list(*, framework, task, tag, kind, trust, root) -> [dict]` (`__init__.py:68-93`) | `[LANDED]` |
| `card(pipeline_id)` | `nirs4all_repository.card(name, root) -> dict` (`__init__.py:96-100`) = `PipelineDescriptor.model_dump` | `[LANDED]` |
| `get_pipeline(pipeline_id)` | `nirs4all_repository.get(name, *, root, cache_dir, verify, with_artifacts) -> Pipeline` (`__init__.py:126-170`); the handle gives `Pipeline.to_nirs4all()` (`bridge.py:47-56`) and `Pipeline.to_dagml()` (`bridge.py:58-62`) | `[LANDED]` |
| `get_bundle(pipeline_id, *, with_artifacts=False)` | `nirs4all_repository.fetch(name, …) -> Path` (`__init__.py:182-191`) = `get(...).path`; fitted → `Pipeline.artifact_path(name)` (`bridge.py:64-71`) | `[LANDED]` |
| `verify(pipeline_id)` | `Pipeline.verify()` (`bridge.py:73-77`, recompute SHA-256); CLI `validate`/`scan` (`cli.py:103-129`,`:81-100`) | `[LANDED]` |
| *serve over network (read-only)* | **no server** (re-grepped `fastapi/flask/uvicorn/@app` across `src/` = 0); remote = static index over HTTPS, `DEFAULT_BASE_URL="https://repository.nirs4all.org"` (`settings.py:15,53`) | **`[NET-NEW]` service = an `RT inspect` surface, not slice 1** |
| *write/upload* | `cli publish` = gate-check only (`cli.py:196-212` → `descriptor.publication_blockers()`, no push); authoring is local (`scaffold`/`build`) | **NONE by default (future curated only)** |

**What "get a pipeline" returns:** a `Pipeline` handle (`bridge.py:25-77`) wrapping a materialized bundle dir + validated `PipelineDescriptor`. It is **served config, not a runnable object** — the consumer runs it via `nirs4all.run(pipe.to_nirs4all(), …)`. `to_nirs4all`/`to_dagml` raise `BridgeError` if the descriptor's `framework` doesn't match (`:54-55`,`:60-61`).

### 4b. Read/write boundary
- **Read:** `list`/`card`/`get`/`fetch`/`verify`. Resolution local checkout → wheel-bundled catalogue → remote static index, all SHA-256-verified. Adapter passes `root`/`cache_dir`/`verify`/`with_artifacts` through.
- **Execute:** out of provider scope. `evaluate_pipeline` (`evaluate.py`, CLI `evaluate` `:175-193`) runs `nirs4all.run(pipe.to_nirs4all(), dataset)` against a reference dataset — it **already composes repository → datasets → nirs4all** and is a seed for the benchmark queue, but is **not** wrapped by the read client (it executes).
- **Write:** none. No S3/git-push/credentials anywhere (`settings.py` = `root`/`cache_dir`/`base_url`/`extra_allowlist` only). Future curated upload is explicitly not baseline.

### 4c. First minimal PR slice — `feat(providers): PipelineProvider read client`
- **Add** `<providers_root>/repository.py`: `PipelineProvider` with `list_pipelines`, `card`, `get_pipeline`, `get_bundle`, `verify` + base members (`provider_id="repository"`, `version()` = `nirs4all_repository.__version__`, `health()` = import-available, `capabilities()` = serves list/card/get/fetch/verify; executes=False; writes=none).
- **~75 LOC** + `tests/test_repository_provider.py`: `list → card → get → verify` over the wheel-bundled catalogue (works offline; no `nirs4all` needed for `list`/`card`; `to_nirs4all()` only exercised behind a `pytest.importorskip("nirs4all")`).
- **Gate:** `ruff check . && mypy src && pytest -q tests/test_repository_provider.py`.
- **Explicitly out:** network service (RT inspect, gated `LOCK-RT`), any write.

---

## 5. `PROV-003` — `BenchmarkProvider` (`nirs4all-benchmarks`, "the Arena")

**Adapter file:** `<providers_root>/benchmarks.py` · **class** `BenchmarkProvider(ProviderPlugin)` · **wraps** `nirs4all_benchmarks` (`version.py:3` `__version__="0.1.0"`; `ARENA_SCHEMA_VERSION`/`ARENA_EXPORT_SCHEMA_VERSION`/`RESIDUALS_SCHEMA_VERSION=1`). Reads go through the **`Queries` facade** (`store/queries.py`) over a local `ArenaStore`; the FastAPI app (`service/app.py`) is the same facade behind HTTP.

### 5a. Exact API to wrap (re-verified at heads — `Queries` is richer than the SW6 sketch)
| Adapter method | Real API today (`file:line`) | Status |
|---|---|---|
| `list_pipelines()` | `Queries.pipelines() -> [dict]` (`queries.py:81-91`) + `GET /api/pipelines` (`app.py:82-85`). Identity owned here: `compute_pipeline_dag_hash(...)` (Merkle DAG hash, `identity/pipeline_dag.py`) | `[LANDED]` |
| `get_pipeline(dag_hash)` | **no dedicated getter** (re-grepped `def get_pipeline` in `src/` = 0). Filter `pipelines()` client-side, **or** `store.get("pipeline_dags","pipeline_dag_hash",dag_hash)` | **`[NET-NEW getter]`, trivially adapter-side** |
| `leaderboard(**q)` | `Queries.leaderboard(metric, scope, partition, dataset_fingerprint, task_hash, collection_id, …)` (`queries.py:115-162`); `Queries.matrix` (`:165-200`); `GET /api/leaderboard`,`/api/matrix` | `[LANDED]` |
| `get_results(execution_hash)` | `Queries.run_detail(hash)` (`queries.py:307-351`) + `Queries.residuals` (`:366-373`); `GET /api/run/{hash}` (`app.py:210-216`), `/residuals` (`:218-221`) | `[LANDED]` |
| `planned()` *(read the queue)* | `Queries.planned() -> [dict]` (`queries.py:573-583`); `GET /api/planned` (`app.py:187-190`) | `[LANDED]` |
| *(rich dataviz, optional pass-through)* | `overview`/`datasets`/`operators`/`operator_effect`/`parameter_effect`/`robustness`/`pivot`/`parallel`/`stats`/`pipeline_graph`/`operator_graph`/`composition`/`residual_compare` (`queries.py`, all `[LANDED]`) | `[LANDED]` (expose on demand) |
| `queue_evaluation(pipelines, datasets)` | **plan-only**: `register_pipeline(...)` upserts `planned_runs` rows (`ingestion/upload.py:106-185`, plan rows `:167-176`); `upload(...)` auto-detects + plans (`:190-259`). **"the Arena never runs compute"** (`upload.py:14-15`; re-grepped: no `import nirs4all`/`dag_ml`/`subprocess` exec path in `src/`) | **plan `[LANDED]`; runner `[NET-NEW]`, gated `LOCK-RT`/`CLU-006`** |

**Ingest, don't execute.** The only data-entry path ingests a precomputed `ArenaRunExport` (`contract/arena_run_export.py`) via adapters that **strip weights** (`adapters/dagml_bundle.bundle_to_export`, `adapters/nirs4all_workspace.WorkspaceAdapter`, `adapters/n4a_bundle.extract_n4a_recipe` `:32-63` + `n4a_pipeline_identity` `:66-72`). Scores are recomputed from sample-keyed residuals, never trusted from the producer.

### 5b. Read/write boundary
- **Read:** §5a `[LANDED]` rows, all through `Queries` on a local `ArenaStore(root)` (or the HTTP base if a service URL is configured). Adapter constructor takes `store_root` (default `./arena-store` / `NIRS4ALL_BENCHMARKS_STORE`).
- **`get_pipeline(dag_hash)`** is the only net-new read, and it is **adapter-side** in slice 1: `next((p for p in q.pipelines() if p["pipeline_dag_hash"] == dag_hash), None)`. Promoting it to a real `Queries.pipeline(dag_hash)` in the benchmarks repo is a clean follow-up (decision **D4**) but **not required** to ship the getter.
- **Execute/write:** out of scope. `queue_evaluation` is an **orchestration of `RtRunRequest → runtime-python|cluster → ArenaRunExport → ingest`** — the runner is external; benchmarks must **not** grow an embedded runner. The Arena store writes are **local only** (`/api/ingest`,`/api/upload` → local sqlite/parquet); **no outbound write-back** to repository/datasets/core (re-verified: none).
- **Auth:** the FastAPI service has **no RBAC** today (`/api/healthz` `app.py:60-65` is the only meta endpoint) — same gap class as cluster `CLU-002`; needed before any non-local exposure (not V1-blocking).

### 5c. First minimal PR slice — `feat(providers): BenchmarkProvider read client`
- **Add** `<providers_root>/benchmarks.py`: `BenchmarkProvider(store_root=None)` with `list_pipelines`, `get_pipeline` (adapter-side filter), `leaderboard`, `get_results`, `planned` + base members (`version()` = `__version__`; `health()` = `{available, store_exists: (root/"arena.sqlite").exists()}` mirroring `/api/healthz`; `capabilities()` = serves list/get/leaderboard/results/planned; executes=False; writes=local-only).
- **~85 LOC** + `tests/test_benchmark_provider.py`: seed a tiny store via the package's own `fixtures.seed_store(..., demo=False)`, then `list_pipelines → get_pipeline(dag_hash) → leaderboard → get_results`. No `service` extra needed (facade is used directly, not HTTP).
- **Gate:** `ruff check . && mypy src && pytest -q tests/test_benchmark_provider.py`.
- **Explicitly out:** `queue_evaluation`, any runner, any ingest/upload wrapping (those are write/execute).

---

## 6. `PROV-004` — `PaperExportProvider` (`nirs4all-papers`)

**Adapter file:** `<providers_root>/papers.py` · **class** `PaperExportProvider(ProviderPlugin)` · **wraps** `nirs4all_papers` (`__version__ = "0.2.0"`; runtime dep PyYAML only — **the lightest provider, no `nirs4all` import to inspect/build**).

### 6a. Exact API to wrap (re-verified at heads)
| Adapter method | Real API today (`file:line`) | Status |
|---|---|---|
| `inspect_bundle(path)` | `read_bundle(path) -> Bundle` (`bundle.py:160-199`); `Bundle` → `nirs4all_version`, `pipeline_uid`, `fingerprint` (SHA-256, `:82-85`), `model_step_index`, `steps() -> [StepInfo]` (`:87-112`). **stdlib only** (`zipfile`/`json`/`hashlib`), no `nirs4all` import (re-verified) | `[LANDED]` |
| `load_paper(paper_dir)` *(bundle + paper.yaml → view)* | `load_paper(dir) -> PaperView` (`model.py:273-311`); `load_catalog(root) -> Catalog` (`model.py:314-331`) | `[LANDED]` |
| `build_methods_section(bundle)` | `resolve_method(short, raw)` + `build_bibliography(method_ids) -> ([Reference], {id:Reference})` (`bibliography.py`); `references_to_bibtex` | `[LANDED]` |
| `build_repro_page(root, out, io_wasm=None)` | `build_site(root, out, io_wasm) -> Path` (`site/__init__.py:90-132`); CLI `n4a-papers build --out site [--io-wasm DIR]` (`cli.py:20-31,68-78`) | `[LANDED]` |
| `export_sidecars(view, out)` | `_write_paper_sidecars(view, out)` (`site/__init__.py:39-58`): copies `.n4a`, writes `pipeline.json` + `CITATION.cff` (`provenance.citation_cff`) + `references.bib` + `ro-crate-metadata.json` (`provenance.ro_crate`) | `[LANDED]` |
| *methods-bibliography sync* | seed `data/bibliography.json` (13.3 KB, present) **distilled** from `nirs4all-methods/docs/_extras/methods_bibliography.py` (128.4 KB, **present**) — a one-time distillation, **not a live import** (`bibliography.py:4-7` docstring; re-grep `import nirs4all_methods|n4m` in papers `src/` = 0) | **`[NET-NEW]` re-distill gate, methods/`L9`** |
| *optional UI* | rendering is self-contained f-string + inline CSS/SVG (`site/{pages,components,theme,charts}.py`), **no `nirs4all-ui` import** (re-verified) | **`[NET-NEW]`, gated `LOCK-UI`** |

### 6b. Read/write boundary
- **Read/build:** all of §6a top rows — **fully landed and `nirs4all`-free**, so this provider can ship complete in slice 1 (no `pytest.importorskip` needed for anything).
- **Write:** explicit, **local**, marker-guarded — `build_site` writes a `.n4a-papers-build` marker and **refuses to wipe** any `--out` dir lacking it (`site/__init__.py:106-117`), refusing `--out .`/`src`/`papers`. No network write. The adapter surfaces `build_repro_page`/`export_sidecars` **as-is** (they write only into the caller-chosen `out`).
- **Replay honesty (`CAP-004`):** the in-browser replay is **pure-JS NIPALS PLS** (`site/assets.py`), an *approximate* reference engine — must be surfaced as **not numerically-portable**, never "full". Production swap seam = **libn4m WASM** via `--io-wasm` (`_copy_io_wasm` `:61-74`, the `RT-WASM-001` path).

### 6c. First minimal PR slice — `feat(providers): PaperExportProvider client`
- **Add** `<providers_root>/papers.py`: `PaperExportProvider` with `inspect_bundle`, `load_paper`, `build_methods_section`, `build_repro_page`, `export_sidecars` + base members (`version()` = `"0.2.0"`; `health()` = import-available (always, given PyYAML-only); `capabilities()` = serves inspect/methods/build/sidecars; executes=approximate-replay-only; writes=local-marker-guarded).
- **~80 LOC** + `tests/test_papers_provider.py`: `inspect_bundle` on a fixture `.n4a` asserts the stdlib path needs no `nirs4all`; `build_repro_page(out=tmp)` then re-build asserts the marker-guard round-trips.
- **Gate:** `ruff check src tests && mypy src/nirs4all_papers && pytest -q tests/test_papers_provider.py` (this provider is the most self-contained; build is part of its own CI).
- **Explicitly out:** re-distill gate (methods/`L9`), `nirs4all-ui` rendering (`LOCK-UI`), libn4m-WASM replay swap (`RT-WASM-001`).

---

## 7. The `ProviderPlugin` base + registry (scaffold PR-0, the prerequisite)

**Files:** `<providers_root>/base.py`, `registry.py`, `_softimport.py`, `__init__.py`.

### 7a. `ProviderPlugin` Protocol (`base.py`)
```
class ProviderPlugin(Protocol):
    provider_id: str                       # "datasets" | "repository" | "benchmarks" | "papers"
    def version(self) -> str: ...          # backed by each pkg __version__   [LANDED]
    def health(self) -> dict: ...          # {available: bool, ...}            [partial today]
    def capabilities(self) -> dict: ...    # provider-level, NOT ControllerCapability  [NET-NEW]
```
- `version()` backing is **landed** for all four (`0.1.0.dev0` / `0.1.0` / `0.1.0` / `0.2.0`).
- `health()` is **partial**: benchmarks `/api/healthz` (store liveness) and datasets origin-health (`health.run_health_check` → `catalog/health.json`, *origin* not *provider* liveness) are adjacent; repository/papers have none. Uniform contract = **import-availability + backing-reachability**, defined fresh (decision **D5**).
- `capabilities()` is **net-new everywhere** and is **provider-level** (`serves: [...]`, `executes: bool`, `writes: <policy enum>`), explicitly **distinct from** the `LOCK-CAP` `ControllerCapability` enum (operator-level). Providers *reference* `portable_level`/`unsupported` (`CAP-002`/`CAP-004`) **for the pipelines/bundles they serve**, but do not own that vocabulary. Shape is decision **D6**.

### 7b. Registry (`registry.py`) — soft-import discovery
- `available_providers() -> list[str]`: returns the ids whose backing package imports cleanly (soft-import each; absent extra → omitted, never raises). Mirrors `nirs4all-benchmarks/datasets/catalog.py`'s `CatalogUnavailable` degradation.
- `get_provider(id) -> ProviderPlugin`: instantiates the adapter, or raises a single uniform `ProviderUnavailable(id, extra="nirs4all-providers[<id>]")` message when the extra is missing.
- **Providers are NOT controllers** (`DEC-CTRL-001`): the registry is a *separate* surface from any controller registry; core exposes provider clients alongside controllers, never as them.

### 7c. PR-0 — `feat(providers): ProviderPlugin base + soft-import registry`
- **Add** the four files above; **~120 LOC** + `tests/test_registry.py` (degradation: with no extras installed, `available_providers() == []` and `get_provider("datasets")` raises the uniform error; with one extra, exactly that id appears).
- **Gate:** `ruff check . && mypy src && pytest -q tests/test_registry.py`.
- **This PR ships first** — it is the keystone every adapter PR imports. It has **zero** provider deps (all soft), so it merges before any extra is wired.

---

## 8. Contract decisions still needed for `DEC-PROV-001`

Distilled to the items that **block or shape the buildable layer** (each maps to an SW6 open question / gate). Recommendation given; none are mine to ratify.

| # | Decision | Recommendation | Gate / owner |
|---|---|---|---|
| **D1** | **Home of the client layer + registry.** Standalone `nirs4all-providers` vs `nirs4all/providers/` subpackage vs `nirs4all-core`. The cycle hazard (§1a) makes a hard-dep subpackage of `nirs4all` unsafe. | **Standalone dependency-light `nirs4all-providers`**, providers as optional extras, soft-imported; foldable into `nirs4all-core` later. Adapter source is identical either way. | `Q6` / `LOCK-GOV` (core topology, `ARB-013`) |
| **D2** | **`DatasetProvider` return seam.** `to_spectro_dataset` now vs route everything through `nirs4all-io` immediately. | **`to_spectro_dataset` (landed) as V1**; add `to_dataset_package` post-`LOCK-IO`, routed through io — never re-assembled in the adapter. | `Q1` / `LOCK-IO` |
| **D3** | **Benchmark runner ownership.** Confirm benchmarks stays runner-free; `queue_evaluation` orchestrates `RtRunRequest → runtime-python|cluster → ArenaRunExport ingest`. | **Yes, runner-free** (boundary rule). Runner is `runtime-python` first, then `cluster`. | `Q2` / `LOCK-RT`, `CLU-006` |
| **D4** | **Benchmark `get_pipeline` placement.** Adapter-side filter over `pipelines()` vs a real `Queries.pipeline(dag_hash)` in the benchmarks repo. | **Adapter-side filter for slice 1** (zero repo change); promote to `Queries.pipeline()` as a clean follow-up if hot. | `L14` ↔ benchmarks |
| **D5** | **`health()` semantics.** Provider import-availability vs backing reachability (store file / origin / remote index). | Uniform `{available: import-ok, reachable: backing-probe}`; keep datasets origin-health and benchmarks `/api/healthz` as *separate* deeper probes, not the provider `health()`. | `DEC-PROV-001` |
| **D6** | **`capabilities()` shape.** The provider-level descriptor (`serves`/`executes`/`writes`) and how it *references* `portable_level`/`unsupported` without forking `LOCK-CAP`. | `{serves: [verbs], executes: enum, writes: enum}` + a `portability` field that **cites** `CAP-002/004` per served artifact. | `DEC-CAP-001` (`LOCK-CAP` signed) — reference only |
| **D7** | **Papers methods-bibliography drift.** Keep `data/bibliography.json` in sync with `nirs4all-methods/docs/_extras/methods_bibliography.py` (both present, 13.3 KB ⇆ 128.4 KB) via manual re-distill vs a CI contract check (lockstep-lite, one-directional methods → papers). | **CI contract check** in papers that fails when the seed is stale vs the methods catalog. | `Q4` / methods `L9` |

Secondary (not slice-1-blocking, recorded for completeness): repository read-only **network service** = an `RT inspect` surface, not a bespoke server (`Q8`/`LOCK-RT`); benchmark **live-server RBAC** (`Q7`, future); papers as a **core `export` capability + `nirs4all-ui`** (`Q5`/`LOCK-UI`).

---

## 9. Implementation sequencing (PR DAG)

```
PR-0  providers: ProviderPlugin base + registry         (no provider deps; merges first)
        │
        ├── PR-1  DatasetProvider read         [extra: datasets]      (slice §3c)
        ├── PR-2  PipelineProvider read        [extra: repository]    (slice §4c)
        ├── PR-3  BenchmarkProvider read       [extra: benchmarks]    (slice §5c, +adapter-side get_pipeline)
        └── PR-4  PaperExportProvider          [extra: papers]        (slice §6c; fully landed, no importorskip)
        │
        ▼  (Vague 3+, each gated)
PR-5  DatasetProvider.to_dataset_package        gated LOCK-IO          (D2)
PR-6  BenchmarkProvider.queue_evaluation        gated LOCK-RT, CLU-006 (D3)  — runner external, ingest-only
PR-7  PipelineProvider network read service     = RT inspect           (Q8)
PR-8  Papers re-distill gate (CI)               methods/L9             (D7)
PR-9  Papers libn4m-WASM replay + optional UI   RT-WASM-001 / LOCK-UI  (Q5)
```
PR-1..PR-4 are **mutually independent** (different adapter files, different extras) and can land in any order / in parallel once PR-0 is in. Each touches **only `<providers_root>`** — no edits to the four provider repos in slice 1 (honors "boundaries are sacred" + the read-only constraint of neighbouring repos).

---

## 10. Gates / commands (per PR, and the cross smoke)

**Provider-home gate (every PR):** `cd <providers_root repo> && ruff check . && mypy src && pytest -q`.

**Provider repos — unchanged by slice 1; their own gates (run only if a follow-up touches them):**
- `nirs4all-datasets`: `ruff check . && mypy --config-file pyproject.toml src && python catalog/scripts/validate.py && pytest -q`
- `nirs4all-repository`: `n4a-repository validate --all && n4a-repository build && git diff --exit-code catalog/index.json && pytest -q`
- `nirs4all-benchmarks`: `n4a-benchmarks fixtures && n4a-benchmarks leaderboard --metric rmse && pytest -q`
- `nirs4all-papers`: `n4a-papers build --out site && ruff check src tests && mypy src/nirs4all_papers && pytest -q`

**Cross smoke (add in PR-0, extend per adapter PR):** a `provider-client` test that, for each `available_providers()` id, round-trips the read path **without importing the runtime** — `list → card/inspect → get`, asserting `nirs4all` is imported only by `DatasetProvider.to_spectro_dataset` / `PipelineProvider.get_pipeline().to_nirs4all()` (behind `importorskip`), never by `list`/`card`/`leaderboard`/`inspect_bundle`.

---

## 11. Evidence (heads, `main`, all repos clean; only this file written)

**Files read this pass (verbatim, line-cited above):**
- `nirs4all-datasets/src/nirs4all_datasets/`: `__init__.py`, `dataset.py`, `cli.py`, `publish.py` (`assert_publishable` `:35-39`); `pyproject.toml`; `CLAUDE.md`.
- `nirs4all-repository/src/nirs4all_repository/`: `__init__.py`, `bridge.py`, `cli.py`, `settings.py` (`DEFAULT_BASE_URL:15`); `pyproject.toml`.
- `nirs4all-benchmarks/src/nirs4all_benchmarks/`: `store/queries.py`, `service/app.py`, `ingestion/upload.py`, `adapters/n4a_bundle.py`, `cli.py`, `version.py`; `pyproject.toml`.
- `nirs4all-papers/src/nirs4all_papers/`: `bundle.py`, `model.py`, `bibliography.py` (`:1-60`), `site/__init__.py`, `cli.py`; `pyproject.toml`; `CLAUDE.md`.
- `nirs4all-methods/docs/_extras/methods_bibliography.py` (existence + size, re-distill source).
- `nirs4all/AGENTS.md`; `nirs4all-ecosystem/docs/agent_reports/SW6_PROV_PLUGINS_spec.md`.

**Commands run (read-only):**
- `git rev-parse --abbrev-ref HEAD` + `git status --porcelain` ×4 → all `main`, dirty count 0.
- `grep -rn "class \w*Provider|ProviderPlugin|provider_id|def capabilities\(|registry"` over all four `src/` → **0 matches** (no provider class/base/registry exists).
- `grep -rn "to_dataset_package|DatasetPackage"` over all four `src/` → **0** (NET-NEW confirmed).
- `grep -rln "fastapi|flask|uvicorn|@app\.(get|post)"` over `nirs4all-repository/src` → **0** (no server; remote = static index).
- `grep -rn "def get_pipeline"` over `nirs4all-benchmarks/src` → **0** (no dedicated getter).
- `grep` `nirs4all/pyproject.toml` for provider names → **0** (`nirs4all` does not depend on providers today → cycle hazard if folded in as hard dep).
- `pyproject.toml` `[project.scripts]` + `[project.optional-dependencies]` ×4 → entry points `n4a-datasets`/`n4a-repository`/`n4a-benchmarks`+`n4a-arena`/`n4a-papers`; extras as tabulated in §1a.

**Worklog line (for A0 to paste — sync board NOT edited):**
`2026-06-30 | SW6/L14 | impl-map | IMP_L14: buildable map for provider adapters over the REAL APIs (datasets list/card/get/to_nirs4all; repository list/card/get/fetch/verify; benchmarks Queries.pipelines/leaderboard/run_detail+/api, NO runner; papers read_bundle/build_bibliography/build_site/sidecars, stdlib-only). New finding: folding the client layer into nirs4all = install cycle (providers depend up on nirs4all) → recommend standalone nirs4all-providers, soft-import extras, foldable to core. PR DAG = PR-0 base+registry (no deps) → 4 independent read-only adapter PRs (no provider-repo edits) → gated to_dataset_package(LOCK-IO)/queue runner(LOCK-RT,CLU-006)/RT-inspect service/papers re-distill gate(L9)/UI(LOCK-UI). 7 DEC-PROV-001 decisions (D1 home/Q6 LOCK-GOV biggest). No code/sync edits. | read-only; gates listed not run | depends LOCK-CAP/RT(signed), LOCK-IO/UI/GOV.`
