# SW6_PROV_PLUGINS_spec — `L14` providers/plugins (datasets · repository · benchmarks · papers)

**Lane:** `L14` (Providers/plugins) · **Decision:** `DEC-PROV-001` (proposed, P1 `ARB-010`) · **Wave:** SW6 (second-wave spec)
**Mode:** read-only audit. No code/test/sync-board edits. This file is the only write.
**Roadmap tasks covered:** `PROV-001`, `PROV-002`, `PROV-003`, `PROV-004`, `PROV-005`.
**Scope (maintainer correction, honored):** in scope = `nirs4all-datasets`, `nirs4all-repository`, `nirs4all-benchmarks`, `nirs4all-papers`. **OUT of scope = `nirs4all-drafts`, `nirs4all-lab`** (private/personal; never modeled as ecosystem bricks — design §2.2, §12.1).

**Verification method:** direct `rg`/`Read`/`grep` against the working-tree heads; CodeGraph not relied on for facts (per SW6 prompt). Four parallel read-only repo maps + direct re-checks of every load-bearing claim (datasets `__init__.py`, repository `__init__.py`, benchmarks runner question, papers `__init__.py`).

**Legend (matches `IO_spec.md`):** `[LANDED]` = exists at the verified heads (evidence cited). `[NET-NEW]` = must be designed/built under this lane. `[STALE-DOC]`/drift hazards flagged.

**Cross-lane anchors (sync board `PARALLEL_REFACTORING_SYNC.md`):**
- `DEC-PROV-001` proposed (line 102): *"renommer sur les vraies APIs; couche provider unifiante = net-new."* This spec's central rule.
- `DEC-CAP-001` accepted / `LOCK-CAP` SIGNED (line 48): capability/`portable_level`/`unsupported` vocab — providers **reference** it, never fork it (`CAP_spec.md`).
- `DEC-RT-001` accepted / `LOCK-RT` SIGNED (line 55): the 8 verbs + `RtRunRequest`/`RtResult`/`RtError` envelopes anchored on dag-ml `ScoreSet` — providers that need execution **consume** these (`RT_spec.md`).
- `DEC-IO-001` accepted / `LOCK-IO` in_progress (line 54): `DatasetSpec v2`/`DatasetPackage` — the `DatasetProvider` future return type depends on it (`IO_spec.md`).
- `DEC-CTRL-001` accepted (line 104): providers are **NOT controllers** (design §4ter.8); core exposes them as **separate optional clients** (design §4ter.11).
- `L14` board line 76 + DAG line 834: *"PROV-001..005 depend on `LOCK-CAP` and feed CORE/STU/WEB/CLI"*; line 829 *"`IO-001..` → `PROV-001`"*; `CLU-006` line 556 *"queue benchmarks → cluster execution path."*

**Key structural finding (the whole point of `L14`):** the four "provider contracts" sketched in design §4bis.1 (`to_dataset_package`, `get_pipeline`, `queue_evaluation`, `build_repro_page`, …) are **target adapter names, not existing classes**. Every one of the four repos already ships a concrete public API (`list`/`get`/`card`/`fetch`/`read_bundle`/`Queries`/`build_site`) that does most of the job — but **no `Provider` class, no common base, and no cross-provider registry exists anywhere** (`rg "class .*Provider|ProviderPlugin|provider_id"` across all four `src/` trees = 0 hits). `L14` is therefore an **adapter-and-surface job**: wrap the real APIs under one thin optional client layer, not invent providers. The four repos are also **already at four different maturity points** for their write paths, which is exactly the maintainer correction this spec encodes.

---

## 0. Maturity / write-state matrix (the maintainer correction, grounded)

| Provider | Read surface (today) | Execute? | Write path (today) | Maintainer-stated state |
|---|---|---|---|---|
| `nirs4all-datasets` | `get`/`list`/`card`/`retrieve` `[LANDED]` | no (assembly only) | publish = **admin-only, governance-gated, FUTURE** | reference data provider; no generic write-back |
| `nirs4all-repository` | `list`/`card`/`get`/`fetch` `[LANDED]` | local `evaluate` only | **no ecosystem write path** (publish = gate-check) | preset/pipeline provider; `list/get pipeline` exist in-process, network **services eventual**; **no ecosystem write path yet** |
| `nirs4all-benchmarks` | `Queries.pipelines/leaderboard` + FastAPI `[LANDED]` | **no runner** (ingest-only) | Arena store **local only**, **disconnected** | can **get pipelines** + locally **queue/test** on n4a datasets, **disconnected in write** |
| `nirs4all-papers` | `read_bundle`/`build_site` `[LANDED]` | approximate JS replay only | export to `--out` dir, **explicit/local** | reproducible export using **methods docs**; **potential core/plugin feature, possibly needs UI** |

The rest of this spec grounds each row in `path:line`, then defines the four contracts, the runtime/core boundary, auth/cache/versioning, the write policy, and an implementation plan.

---

## 1. `PROV-001` — `DatasetProvider` (`nirs4all-datasets`)

### 1a. Verified real API `[LANDED]`
Package `nirs4all_datasets` (`__init__.py`, version `0.1.0.dev0` `:29`; CLI `n4a-datasets`; schema 2.0). The consumer surface is four module-level functions + the `NirsDataset` reader:

| Target adapter method (design §4bis.2) | Real API today (file:line) | Status |
|---|---|---|
| `list_datasets()` | `nirs4all_datasets.list(root, **filters) -> Sequence[dict]` (`__init__.py:58-62`) → `catalog.search`; filters `tier`/`domain`/`spectro_family`/`has_target` (`catalog.py:199`) | `[LANDED]` |
| `card(dataset_id)` | `nirs4all_datasets.card(name, root) -> dict | None` (`__init__.py:65-69`) → `catalog.get_card` (reads `datasets/<id>/card.json`) | `[LANDED]` |
| `get_dataset(dataset_id)` | `nirs4all_datasets.get(name, *, source, split, token, instance, cache_dir, concat, reproduce) -> NirsDataset` (`__init__.py:34-55`); resolution **local → personal-Dataverse DOI → OPEN origin** (`access.py:92-187`) | `[LANDED]` |
| *(raw acquisition)* | `nirs4all_datasets.retrieve(name, *, route_id, cache_dir, token, instance, …) -> dict` (`__init__.py:72-97`) → `retrieval.retrieve` (status dict, `kind: raw|canonical`) | `[LANDED]` |
| `to_dataset_package(dataset_id)` | **TODAY:** `NirsDataset.to_nirs4all() -> SpectroDataset` (`dataset.py:305-349`, imports `nirs4all.data.SpectroDataset` `:324`). **`to_dataset_package` / `DatasetPackage` = absent** (`rg` across `src/` = 0 hits). | **`to_nirs4all` `[LANDED]`; `to_dataset_package` `[NET-NEW]`** |
| *(io hand-off)* | `reproduce.py:85-88` lazy-imports `nirs4all_io as nio` and calls `nio.load(dir, target="spectrodataset", name=…)` — **only** in `get(..., reproduce=True)` fallback | `[LANDED, partial]` |

`NirsDataset` readers (all `[LANDED]`, `dataset.py`): `sources()` `:114`, `variables()` `:118`, `x(source, concat)` `:134`, `wavelengths` `:184`, `observation_ids`/`sample_ids` `:191/:195`, `y(name)` `:264`, `metadata(name)` `:278`, `split(name)` `:293`. Identity is sample-keyed, never row-position (CLAUDE.md "joined by sample_id"). This is the same identity story `IO_spec.md §3` carries into `SampleRelationTable`.

### 1b. `DatasetProvider` contract (target)
```
DatasetProvider(ProviderPlugin):
  list_datasets(**filters)        -> [card-dict]        # = nirs4all_datasets.list           [LANDED]
  card(dataset_id)                -> card-dict | None   # = nirs4all_datasets.card            [LANDED]
  get_dataset(dataset_id, **opts) -> NirsDataset        # = nirs4all_datasets.get             [LANDED]
  to_spectro_dataset(dataset_id)  -> SpectroDataset     # = NirsDataset.to_nirs4all()         [LANDED]
  to_dataset_package(dataset_id)  -> DatasetPackage     # via nirs4all-io, gated on LOCK-IO   [NET-NEW]
```
**Boundary (design §6.7, §3.2):** `datasets` is the **reference-data provider**; **`nirs4all-io` is still the assembly owner**. Today `to_nirs4all()` builds a `SpectroDataset` *directly* (bypassing io except the `reproduce` path). The `DatasetPackage` return type is the `LOCK-IO` future — `DatasetProvider.to_dataset_package` must route the canonical Parquet (`canonical/sources/*.parquet` + `variables.parquet`, CLAUDE.md) through the `io` assembly + the `nirs4all-io-dagml` bridge (`IO_spec.md §4`), **not** re-assemble in datasets or core. Core exposes the **client**; it does not rewrite assembly (design §6.7 policy).

### 1c. Auth / cache / versioning
- **Auth:** token only for `private`/`anonymized` tiers, via `X-Dataverse-key` header (never query param / log, `dataverse.py:52-56`); `public` needs none. Resolution: arg → `NIRS4ALL_DATAVERSE_TOKEN` → config file → `.env` (CLAUDE.md token-hygiene).
- **Cache:** Rust acquisition core `n4ds_` (`_acquire.py`): `resolve`/`fetch`/`retrieve_raw`/`verify_cached` (`:31-94`), pooch-style `pooch.os_cache("nirs4all-datasets")/<id>/canonical/`; **download SHA-256-verified** against the per-file manifest (`manifest.py:44-92`).
- **Versioning:** DOI + `dataverse.dataset_version` pin bytes; two descriptor axes `versions.content` (byte change) + `versions.schema_protocol` (re-qualify) (CLAUDE.md); content-addressed `processing_hash`/`metadata_hash` (`manifest.py:58-79`). Canonical is Parquet `tabIngest=false` so cached bytes stay byte-identical (the thing that makes SHA-256 verify work).
- **Write (`PROV-005`):** publish is **admin-only + governance-gated** — `assert_publishable()` is tier-gated, only `public` checked for open SPDX license + open origins (`publish.py:35-39`); `publish_dataset`/`update_dataset` (`publish.py:81-144`) target a **FUTURE** personal Dataverse for protected data; public bytes are **never re-hosted**. Ordinary `get()` consumers write **nothing** outside the local cache.

---

## 2. `PROV-002` — `PipelineProvider` (`nirs4all-repository`)

### 2a. Verified real API `[LANDED]`
Package `nirs4all_repository` (version `0.1.0`, `_version.py:9`). Public surface (`__init__.py:33-43`): `Pipeline`, `PipelineDescriptor`, `Settings`, `get_settings`, `list`, `card`, `get`, `fetch`.

| Target adapter method | Real API today (file:line) | Status |
|---|---|---|
| `list_pipelines()` | `nirs4all_repository.list(*, framework, task, tag, kind, trust, root) -> [dict]` (`__init__.py:68-93`) — filters the index `pipelines{}` | `[LANDED]` |
| `card(pipeline_id)` | `nirs4all_repository.card(name, root) -> dict` (`__init__.py:96-100`) = `PipelineDescriptor.model_dump` | `[LANDED]` |
| `get_pipeline(pipeline_id)` | `nirs4all_repository.get(name, *, root, cache_dir, verify, with_artifacts) -> Pipeline` (`__init__.py:126-170`); `Pipeline.to_nirs4all()` (`bridge.py:47-56`) → nirs4all `PipelineConfigs`-shaped dict; `Pipeline.to_dagml()` (`bridge.py:58-62`) → dag-ml DSL/artifact | `[LANDED]` |
| `get_bundle(pipeline_id)` | `nirs4all_repository.fetch(name, …) -> Path` (`__init__.py:182-191`) materializes the bundle dir; `kind=fitted` → `Pipeline.artifact_path()` (`bridge.py:64-71`, `.n4a`/`.joblib`/`.onnx`/`.safetensors`) | `[LANDED]` |
| `verify(pipeline_id)` | `Pipeline.verify()` (`bridge.py`); CLI `validate` (schema/structure/checksums/security, `cli.py:103-129`); `scan` security (`cli.py:81-100`, `security.py`) | `[LANDED]` |

**What a "pipeline" is:** a `descriptor.yaml` (`PipelineDescriptor`, `schema.py:289-353`) + a `Recipe` whose `format` ∈ {`nirs4all/pipeline-config`, `dag-ml/pipeline-dsl`, `dag-ml/compiled-artifact`} (`schema.py:90-95`), `kind` ∈ {`recipe`, `fitted`}. It is **served config, not a runnable object** — the consumer runs it via `nirs4all.run(pipeline.to_nirs4all(), …)`. Resolution is **local checkout → wheel-bundled catalogue → remote** with SHA-256 verify (`get` body; `fetch.py` `fetch_index`/`fetch_verified`/`materialize_remote`).

### 2b. "eventual get pipeline list / get pipeline **services**" — the maintainer correction
The in-process `list`/`get` **already exist** (above). What is "eventual" is a **network service**: there is **no server today** — `rg "fastapi|flask|uvicorn|@app\\.(get|post)"` across `src/` = 0 (only the typer CLI app). The remote path is a **static index over HTTPS** (`fetch_index(base_url)`, default `https://repository.nirs4all.org`, `index.py:101-114`). So `PipelineProvider`-as-a-**service** = `[NET-NEW]`: a thin read-only HTTP surface exposing `list`/`get`/`card`, which should be the `RT_spec.md` `inspect` surface, not a bespoke server.

### 2c. "no ecosystem write path yet" — confirmed
- **No upload / write-back.** `publish` CLI (`cli.py:196-212`) is a **gate-check only** (`descriptor.publication_blockers()`), it does **not** push/commit. Authoring is **local**: `scaffold_pipeline` (`scaffold.py:21-67`, CLI `add`), `build_catalog` (`builder.py:25-36`, CLI `build`, writes index/manifests to the **local checkout** only, idempotent for `git diff --exit-code`). No S3/git-push/credentials anywhere (`settings.py:38-54` = `root`/`cache_dir`/`base_url`/`extra_allowlist` only). Future **curated** upload is explicitly **not baseline** (design §4bis.3, §12.1).
- **Local `evaluate` exists** and is relevant to the benchmark story: `evaluate_pipeline(pipeline)` (`evaluate.py:67-99`) runs `nirs4all.run(pipeline.to_nirs4all(), dataset)` (`:81`) against a reference dataset (optionally via `nirs4all_datasets`) and compares to `descriptor.evaluation.expected`. This is a **single-pipeline local test** that already composes repository → datasets → `nirs4all` — a seed for the benchmark queue, but **not** an Arena runner.

### 2d. `PipelineProvider` contract (target)
```
PipelineProvider(ProviderPlugin):
  list_pipelines(**filters) -> [card-dict]   # = nirs4all_repository.list     [LANDED]
  card(pipeline_id)         -> dict          # = nirs4all_repository.card     [LANDED]
  get_pipeline(pipeline_id) -> Pipeline      # = nirs4all_repository.get      [LANDED]
  get_bundle(pipeline_id)   -> Path          # = nirs4all_repository.fetch    [LANDED]
  verify(pipeline_id)       -> None          # = Pipeline.verify / CLI scan   [LANDED]
  # serve over network (read-only) -> RT inspect surface                      [NET-NEW service]
  # write/upload -> NONE by default (future curated upload only)              [NET-NEW, gated]
```
- **Auth:** none for public read; integrity via SHA-256 recipe verify (`fetch.py`) + recipe security scan (`security.py`, `extra_allowlist`).
- **Cache:** `cache_dir/<id>/<recipe_sha256>/`, never overwrites a published bundle (`fetch.py:66-97`).
- **Versioning:** descriptor `version` + index `repository_version` + `schema_version` + content-addressed `recipe.sha256`/`descriptor.sha256` (`index.py`).

---

## 3. `PROV-003` — `BenchmarkProvider` (`nirs4all-benchmarks`, "the Arena")

### 3a. Verified real API `[LANDED]` — owns pipeline identity, serves reads, **has no runner**
Package `nirs4all_benchmarks` (`__init__.py` exports only `__version__` + `ARENA_SCHEMA_VERSION=1` / `ARENA_EXPORT_SCHEMA_VERSION=1` / `RESIDUALS_SCHEMA_VERSION=1` `:22-31`; functional API in submodules). CLI `n4a-benchmarks`.

| Target adapter method | Real API today (file:line) | Status |
|---|---|---|
| `list_pipelines()` | `Queries.pipelines() -> [dict]` (`store/queries.py:81-91`) + `GET /api/pipelines` (`service/app.py:82-85`). Benchmarks **owns** pipeline identity: `compute_pipeline_dag_hash(...) -> PipelineDagIdentity` (Merkle DAG hash, `identity/pipeline_dag.py:305-346`; dataclass `:56-77`) | `[LANDED]` |
| `get_pipeline(pipeline_id)` | **No dedicated getter** — filter `pipelines()` / SQL. Recipe extraction from `.n4a`: `extract_n4a_recipe(path)`, `n4a_pipeline_identity(path)` (`adapters/n4a_bundle.py:32-72`) | `[LANDED, partial]` → dedicated `get_pipeline(dag_hash)` `[NET-NEW]` |
| `leaderboard(query)` | `Queries.leaderboard(metric, scope, partition, …) -> dict` (`store/queries.py:115-162`); `Queries.matrix` (`:165-200`); `GET /api/leaderboard`, `/api/matrix` | `[LANDED]` |
| `get_results(run_id)` | `GET /api/run/{execution_hash}` (`app.py:210-216`), `/residuals` (`:218-221`), `Queries.runs` (`app.py:120-134`) | `[LANDED]` |
| `queue_evaluation(pipelines, datasets)` | **PLAN-ONLY:** `register_pipeline()` marks (pipeline × dataset) as `planned` (`ingestion/upload.py:150-160`); `GET /api/planned` (`app.py:187-190`). **"the Arena itself never runs compute"** (`ingestion/upload.py:1-15`). No `import nirs4all` / `dag_ml` / `subprocess` execution path anywhere in `src/` (verified). | **plan `[LANDED]`; runner `[NET-NEW]`** |

**Ingest, don't execute.** The **only** data-entry path is ingesting a pre-computed `ArenaRunExport` (`contract/arena_run_export.py`): adapters parse and **strip weights**, never run — `bundle_to_export` (dag-ml `ExecutionBundle` JSON, no dag-ml import, `adapters/dagml_bundle.py`), `WorkspaceAdapter` (nirs4all `store.sqlite` + `arrays/*.parquet`, ignores `artifacts/`, `adapters/nirs4all_workspace.py`), `extract_n4a_recipe` (`.n4a`, weights dropped). Scores are **recomputed from sample-keyed residuals** (`scoring/metrics.py`, `ScoreComputationSpec` `scoring/score_spec.py:11-40`) — never from a producer's metric.

### 3b. "locally queue/test on n4a datasets but disconnected in write" — grounded
- **get pipelines + datasets:** `Queries.pipelines()` (above); datasets via **soft-import best-effort** `load_catalog_card(dataset_id)` → `CatalogUnavailable` if `nirs4all-datasets` absent (`datasets/catalog.py:46-62`, `DatasetCard` `datasets/dataset_card.py:12-45`) — **no hard dep** (README "siblings are optional; every path degrades gracefully").
- **queue/test:** the *plan* lives in benchmarks (`planned` rows); the **run is external**. Per design §6.9 the queue targets a **runtime-python or cluster** runner that produces an `ArenaRunExport`, which benchmarks then ingests. So `queue_evaluation` in `BenchmarkProvider` is an **orchestration of `RtRunRequest` → runner → ingest**, where the runner is `runtime-python` first, then `cluster` (`CLU-006`). Benchmarks **must not** grow an embedded runner (boundary rule design §4bis.3, §12.1, ownership matrix §3.2 "non-goal: writing back into repository/ecosystem").
- **disconnected in write:** the Arena store is **local only** — SQLite `arena.sqlite` (WAL) + `arrays/residuals_<hash>.parquet` + `exports/` audit (`store/arena_store.py:39-70`), content-addressed idempotent `upsert`/`insert` (`:116-141`). The two write endpoints `POST /api/ingest`, `POST /api/upload` (`app.py:229-294`) write **into the local store only**. There is **no outbound write-back** to repository/datasets/core (verified: no such path). Results are published deliberately as a static snapshot (README "static, client-side now"), **never silently written back**.

### 3c. `BenchmarkProvider` contract (target)
```
BenchmarkProvider(ProviderPlugin):
  list_pipelines()                     -> [dict]   # = Queries.pipelines()              [LANDED]
  get_pipeline(dag_hash)               -> dict     # filter/SQL today                   [NET-NEW getter]
  leaderboard(query)                   -> dict     # = Queries.leaderboard/matrix       [LANDED]
  get_results(execution_hash)          -> dict     # = /api/run/{hash}(+/residuals)     [LANDED]
  queue_evaluation(pipelines, datasets)-> plan     # register_pipeline -> planned       [LANDED plan]
       # execution = RtRunRequest -> runtime-python|cluster -> ArenaRunExport -> ingest [NET-NEW runner, disconnected]
```
- **Result envelope overlap with `LOCK-RT`:** `ArenaRunExport` (weights-free, content-addressed, residuals-keyed) is a **sibling projection of the dag-ml `ScoreSet`/`RtResult`** — the adapters already parse the same native triple (`ExecutionBundle` / workspace `store.sqlite`) that `RT_spec.md` anchors `RtResult` on. The runner→Arena seam should emit `RtResult` and let the benchmark adapter pivot it into `ArenaRunExport` (one more group-by), not a third bespoke shape. Flag for `RT`/`L10` coordination.
- **Auth:** the local FastAPI service has **no RBAC today** (same class of gap as `nirs4all-cluster`, `CLU-002`); the "live meta-analysis server next" (README) needs it before any non-local exposure.
- **Versioning:** `ARENA_SCHEMA_VERSION`/`ARENA_EXPORT_SCHEMA_VERSION`/`RESIDUALS_SCHEMA_VERSION` + `pipeline_dag_hash`/`run_condition_hash` (six dimension hashes; producer UUIDs are **never** join keys, README).

---

## 4. `PROV-004` — `PaperExportProvider` (`nirs4all-papers`)

### 4a. Verified real API `[LANDED]` — reproducible export, methods-doc-sourced, self-contained UI
Package `nirs4all_papers` (`__version__ = "0.2.0"`, `__init__.py:12`; CLI `n4a-papers`; runtime dep PyYAML only). It is a **reproduction-document publisher**: `.n4a` + hand-written `paper.yaml` → static page (methods + bibliography + approximate in-browser replay) + deposit sidecars.

| Target adapter method (design §4bis.2) | Real API today (file:line) | Status |
|---|---|---|
| `inspect_bundle(bundle)` | `read_bundle(path) -> Bundle` (`bundle.py:160-199`); `Bundle` (`:57-86`) → `nirs4all_version`, `pipeline_uid`, `fingerprint` (SHA-256), `model_step_index`, `steps() -> [StepInfo]` (`:87-112`). **stdlib only** (`zipfile`/`json`), **no `nirs4all` import** (verified) | `[LANDED]` |
| `build_methods_section(bundle)` | `resolve_method(short_name, raw)` (`bibliography.py:119-129`), `reference_for(method_id)` (`:132-149`), `build_bibliography(method_ids) -> ([Reference], {id:Reference})` (`:159-184`); `Reference.to_bibtex()` (`:91-107`), `references_to_bibtex` (`:187-190`) | `[LANDED]` |
| `build_repro_page(bundle, paper_yaml)` | `build_site(root, out, io_wasm=None) -> Path` (`site/__init__.py:90-132`); CLI `n4a-papers build --out site [--io-wasm DIR]` (`cli.py:20-31`); page renderers `render_index`/`render_catalog`/`render_paper` (`site/pages.py`) | `[LANDED]` |
| `export_sidecars()` | `_write_paper_sidecars(view, out)` (`site/__init__.py:39-58`): copies `.n4a`, writes `pipeline.json`, `CITATION.cff` (`provenance.citation_cff` `:87-170`), `references.bib`, `ro-crate-metadata.json` (`provenance.ro_crate` `:173-265`); `reproduction_commands` (`:310-322`) | `[LANDED]` |

### 4b. "uses methods docs for reproducible export" — grounded (with a drift hazard)
The bibliography is a **bundled static seed** `data/bibliography.json` (`bibliography.py:18` `_DATA`, `@lru_cache` `_seed()`), **distilled from `nirs4all-methods/docs/_extras/methods_bibliography.py`** (docstring `:1-8`); `_SYNONYMS` (`:36-67`) normalizes 67+ operator aliases → stable method ids. **`[STALE-DOC] / drift hazard:** this is a **one-time distillation, not a live import** — `rg "import nirs4all_methods|n4m"` in papers `src/` = 0. If `nirs4all-methods` adds/changes a method's citation, the papers seed **silently rots** until re-distilled. `PROV-004` must define a **re-distill gate** (a small CI/contract check that `data/bibliography.json` is in sync with the methods catalog) — a lockstep-lite, analogous to `LOCK-LOCKSTEP` but one-directional methods → papers.

### 4c. "potential core/plugin feature, possibly needs UI" — grounded
- **Why it can be core:** the input is a **bundle** and the output is a **reproducibility artifact** (design §4bis.3, §6.10) — it is exactly the shape of a core `export` capability (the `RT_spec.md` `export` verb has two targets: `.n4a` and research-provenance/RO-Crate; papers is the human-facing RO-Crate/CITATION/replay target). It depends on **no** `nirs4all` runtime to *inspect/build* (stdlib + PyYAML), so it can live as a portable core/plugin feature.
- **UI:** rendering is **self-contained f-string templating + inline CSS/SVG** (`site/{pages,components,theme,charts,escape}.py`); **no `nirs4all-ui` import today** (verified). Design tokens are *lifted* from the family so it visually matches `datasets.nirs4all.org`. "Possibly needs UI" = `PaperExportProvider` may **consume `nirs4all-ui`** for consistent rendering (design §6.10, §11.4 "optional nirs4all-ui assets"; UML §3.1 `PaperExporter <.. Nirs4AllUI`) — `[NET-NEW]`, gated on `LOCK-UI`.
- **Replay portability claim (must be honest):** the in-browser replay is **pure-JS NIPALS PLS + preprocessing + k-fold OOF** (`site/assets.py` `replay_plan`/`replay_panel`/`REPLAY_JS`), explicitly labeled an **"alpha reference engine"** that does **not** reproduce the exact published run. Per `CAP-004` it must be surfaced as **approximate / not numerically-portable**, never "full". The **production swap seam** is the **libn4m WASM** engine in `nirs4all-web` (`--io-wasm` copies `nirs4all-formats`/`nirs4all-io` WASM); that is the `RT-WASM-001` path.

### 4d. `PaperExportProvider` contract (target)
```
PaperExportProvider(ProviderPlugin):
  inspect_bundle(bundle)                 -> Bundle   # = read_bundle (stdlib, no nirs4all) [LANDED]
  build_methods_section(bundle)          -> [Reference] # = build_bibliography             [LANDED]
  build_repro_page(bundle, paper_yaml)   -> Path     # = build_site                        [LANDED]
  export_sidecars()                      -> [files]  # = _write_paper_sidecars             [LANDED]
  # methods source = distilled seed (needs re-distill gate vs nirs4all-methods)            [NET-NEW gate]
  # optional nirs4all-ui rendering; production replay = libn4m WASM (RT-WASM)              [NET-NEW]
```
- **Write (`PROV-005`):** explicit, **local**, marker-guarded — `build_site` writes a `.n4a-papers-build` marker and **refuses to wipe** any `--out` dir lacking it (`site/__init__.py:106`). No network write.

---

## 5. The common base + the non-controller boundary

### 5a. `ProviderPlugin` base `[NET-NEW]`
No base class / registry exists in any repo. Design §4bis.2 proposes `ProviderPlugin{ provider_id, capabilities(), health(), version() }`; ground it:

| Base member | Real backing today | Status |
|---|---|---|
| `version()` | each package `__version__` (datasets `0.1.0.dev0`, repository `0.1.0`, benchmarks `version.py`, papers `0.2.0`) | `[LANDED]` |
| `health()` | datasets origin-health probe (`health.py` → `catalog/health.json`) is **adjacent** (origin liveness, not provider liveness); benchmarks `GET /api/healthz` (`app.py:60-65`); repository/papers none | `[LANDED, partial]` |
| `provider_id`, `capabilities()` | none | `[NET-NEW]` |

`capabilities()` here means *provider-level* capability (does it serve list? get? execute? write?) — **distinct from** the `LOCK-CAP` `ControllerCapability` enum, which is operator-level. Providers **reference** `portable_level`/`unsupported` (`CAP-002`/`CAP-004`) **for the pipelines/bundles they serve** (e.g. a repository recipe's portability, a paper bundle's portability), but do **not** define the vocabulary.

### 5b. Providers are NOT controllers
Per design §4ter.8 the provider/plugin clients (`datasets`, `repository`, `benchmarks`, `papers`) are in the **"easy-to-miss non-controller surfaces"** list, alongside data providers, artifact stores and cluster. Core must **expose them separately from controllers** (§4ter.11): a pipeline node is run by a *controller*; a *dataset/preset/benchmark/paper* is fetched/served by a *provider client*. `L14` and `L16` (controllers) must not be conflated.

---

## 6. Runtime / core boundary (where each contract lives)

```
core aggregate  ── exposes optional provider CLIENTS (read/fetch/inspect; no execution) ──┐
   DatasetProvider.list/card/get/to_spectro_dataset                                       │
   PipelineProvider.list/card/get/fetch                                                   │ design §1.1:
   BenchmarkProvider.list_pipelines/leaderboard/get_results                               │ "core expose
   PaperExportProvider.inspect/methods/build/export_sidecars                              │ des clients
                                                                                          │ providers
runtime  ── executes; providers DELEGATE execution here, never run through core ──────────┘ optionnels"
   BenchmarkProvider.queue_evaluation -> RtRunRequest -> runtime-python | cluster
   PaperExportProvider replay         -> libn4m WASM (runtime-wasm)
io  ── DatasetProvider.to_dataset_package routes through nirs4all-io assembly (LOCK-IO)
```

Rules (design §2.2, §3.2, §6.7–6.11):
- **Core** publishes the optional provider clients + validates; it holds **no** new business logic and **does not execute**.
- **Runtime** owns execution; the benchmark **runner** and the paper **production replay** are runtime/cluster/WASM, not provider-internal.
- **`io`** stays the dataset-assembly owner; `datasets` hands off, never re-assembles in core.
- **Providers may expose assets/contracts to core, but never become owners of base scientific execution** (design §2.2 policy).
- **The provider client layer is the only `[NET-NEW]` glue**: each repo keeps its own package + API (`DEC-PROV-001` "couche provider unifiante = net-new").

---

## 7. Write policy (`PROV-005`) — one table

| Provider | Default write | Allowed write | Forbidden |
|---|---|---|---|
| `datasets` | local cache only | admin publish to **future** personal Dataverse, governance-gated (`publish.py:35-39`) | re-hosting public bytes; consumer write-back |
| `repository` | local authoring (`scaffold`/`build`) | future **curated** upload (not baseline) | implicit ecosystem write/upload; community push now |
| `benchmarks` | Arena store **local** (sqlite+parquet) | deliberate static-snapshot publish | write-back to repository/datasets/core; silent writes |
| `papers` | explicit `--out` dir, marker-guarded | re-deploy static site (papers.nirs4all.org) | private drafts/lab content; hidden data |

Matches design §4bis.3 read/write flow and §12.1 import boundaries (`benchmarks` "must not mutate repository/datasets/core state implicitly"; `papers` "must not import private drafts/lab").

---

## 8. Implementation plan (waves, aligned to roadmap `PROV-001..005`)

**Phase 0 — spec freeze (this doc).** Ratify the four adapter contracts as **thin wrappers over the real APIs** (§1–4), the `ProviderPlugin` base (§5a), and the write policy (§7). Net-new surface = the client layer + `to_dataset_package` + benchmark `get_pipeline` getter + benchmark runner orchestration + papers re-distill gate + optional papers UI. Depends on `LOCK-CAP` (signed) for the capability/portability fields surfaced.

**Phase 1 — read-only provider clients in core (Vague 2).** Implement, all over existing APIs, **no execution**:
- `DatasetProvider` = `list`/`card`/`get`/`to_spectro_dataset` (datasets `[LANDED]`).
- `PipelineProvider` = `list`/`card`/`get`/`fetch` (repository `[LANDED]`).
- `BenchmarkProvider` (read) = `list_pipelines`/`leaderboard`/`get_results` (`Queries` + a `get_pipeline(dag_hash)` getter `[NET-NEW]`).
- `PaperExportProvider` = `inspect_bundle`/`build_methods_section`/`build_repro_page`/`export_sidecars` (papers `[LANDED]`).
- Surface `portable_level`/`unsupported` per `CAP-002`/`CAP-004` for served pipelines/bundles.

**Phase 2 — wire to runtime (Vague 3).**
- `DatasetProvider.to_dataset_package` via `nirs4all-io` assembly + `nirs4all-io-dagml` bridge — **gated on `LOCK-IO`** (`IO_spec.md`).
- `BenchmarkProvider.queue_evaluation` emits `RtRunRequest` → `runtime-python` (then `cluster`, `CLU-006`) → ingests `ArenaRunExport`/`RtResult`; benchmarks gains **no** embedded runner.
- `PipelineProvider` read-only **network service** (the "eventual services") = an `RT inspect` surface, not a bespoke server.
- `PaperExportProvider` production replay swaps the alpha JS engine for **libn4m WASM** (`RT-WASM-001`); optionally consumes `nirs4all-ui` (gated on `LOCK-UI`).

**Phase 3 — provider releases + promotions (Vague 4).**
- `papers` promoted toward a **core/UI export feature** (design §6.10).
- benchmark **live server** with RBAC, interacting with repository/datasets (still **no** silent write-back).
- repository **curated upload** only if a maintainer decision adds it.
- `papers` **methods-bibliography re-distill gate** wired into CI (drift vs `nirs4all-methods`).

**Cross-cutting:** drafts/lab stay out of every wave (private). The provider layer never re-implements `nirs4all`/`io`/`methods` (each repo's own boundary rule + ecosystem §2.2).

---

## 9. Proposed `LOCK-PROV` content (for A0, gated on P1 `ARB-010`)

```
LOCK-PROV (providers/plugins) — decision source DEC-PROV-001. Owner L14.
Scope: nirs4all-datasets, -repository, -benchmarks, -papers ONLY. drafts/lab OUT (private).

P1. Provider contracts are ADAPTERS over the REAL repo APIs (verified §1-4), not new classes.
    DatasetProvider     = nirs4all_datasets.{list,card,get} + NirsDataset.to_nirs4all   [LANDED]
    PipelineProvider    = nirs4all_repository.{list,card,get,fetch} + Pipeline.to_nirs4all/to_dagml [LANDED]
    BenchmarkProvider   = Queries.{pipelines,leaderboard} + /api reads (+get_pipeline getter NET-NEW) [LANDED read]
    PaperExportProvider = read_bundle + build_bibliography + build_site + sidecars      [LANDED]
P2. ProviderPlugin base {provider_id, capabilities(), health(), version()} = NET-NEW thin protocol;
    version()/health() partly landed; provider capabilities() != ControllerCapability (CAP).
    Providers REFERENCE portable_level/unsupported (CAP-002/004); they do not own ML execution (not controllers).
P3. NET-NEW work, explicitly: provider client layer in core; DatasetProvider.to_dataset_package (gated LOCK-IO);
    BenchmarkProvider.get_pipeline getter + queue runner orchestration (RtRunRequest->runtime/cluster, ingest-only);
    PipelineProvider read-only network service (= RT inspect); PaperExportProvider libn4m-WASM replay + optional UI;
    papers methods-bibliography re-distill gate vs nirs4all-methods.
P4. Write policy (PROV-005): datasets no generic write-back (publish admin/governance-gated, future);
    repository no ecosystem write path now (publish=gate-check; future curated only);
    benchmarks writes Arena-LOCAL + disconnected (no write-back to repository/datasets/core);
    papers export writes explicit + local (marker-guarded).
P5. Dependencies: LOCK-CAP (signed) for capability/portability fields; LOCK-RT (signed) for queue/replay
    envelopes (ArenaRunExport is a ScoreSet/RtResult sibling); LOCK-IO (in_progress) for DatasetPackage;
    LOCK-UI for optional papers UI. Providers feed CORE/STU/WEB/CLI, never gate them.
```

---

## 10. Open questions + gates

**Open questions (need `DEC-*` / maintainer before build):**
1. **`DatasetProvider` return seam:** keep `to_nirs4all() -> SpectroDataset` as the V1 contract and add `to_dataset_package` post-`LOCK-IO`, or route everything through `io` immediately? Today only `reproduce` mode touches `nio.load`. **Recommend:** `to_spectro_dataset` now (landed), `to_dataset_package` gated on `LOCK-IO`. **Gate: `LOCK-IO`.**
2. **Benchmark runner ownership:** confirm benchmarks stays runner-free and `queue_evaluation` orchestrates `RtRunRequest → runtime-python|cluster → ArenaRunExport ingest`. **Recommend yes** (boundary rule). **Gate: `LOCK-RT`, `CLU-006`.**
3. **`ArenaRunExport` vs `RtResult`:** make the runner→Arena seam emit `RtResult` and let the benchmark adapter pivot it (avoid a third score shape)? **Gate: `RT`/`L10`.**
4. **Papers methods-bibliography drift:** how to keep `data/bibliography.json` in sync with `nirs4all-methods` — manual re-distill vs a CI contract check (lockstep-lite)? **Gate: methods/`L9` coordination.**
5. **Papers as core feature + UI:** promote `PaperExportProvider` into a core `export` capability and let it consume `nirs4all-ui`? **Gate: `LOCK-UI`, core topology `ARB-013`.**
6. **`ProviderPlugin` home + registry:** ecosystem-spec base protocol + per-repo impl, with the client layer in `nirs4all-core`/`-lite`? **Gate: `LOCK-GOV` (core topology).**
7. **Benchmark live-server auth:** RBAC for the "live meta-analysis server next" (same gap class as cluster `CLU-002`). **Gate: future, not V1-blocking.**
8. **Repository network "services":** scope of the eventual read-only HTTP `list/get` surface (= RT inspect vs bespoke). **Recommend RT inspect.** **Gate: `LOCK-RT`.**

**Gates to run (none run here — read-only):**
- `nirs4all-datasets`: `ruff check . && mypy src && pytest -q`; `python catalog/scripts/validate.py` (descriptor schema).
- `nirs4all-repository`: `n4a-repository validate --all`; `n4a-repository build` + `git diff --exit-code catalog/index.json`; `pytest -q`.
- `nirs4all-benchmarks`: `n4a-benchmarks fixtures && n4a-benchmarks leaderboard --metric rmse`; `pytest -q` (ingest idempotency).
- `nirs4all-papers`: `n4a-papers build --out site && ruff check src tests && mypy src/nirs4all_papers && pytest -q` (lint+types+build+sidecar validation).
- Cross: a `provider-client` smoke that `list`→`card`→`get` round-trips on each provider without importing the runtime.

**Worklog line (for A0 to paste — I did not edit the sync board):**
`2026-06-30 | SW6/L14 | review | PROV-spec: 4 provider contracts grounded on REAL APIs (datasets get/list/card/to_nirs4all; repository list/card/get/fetch; benchmarks Queries+/api reads, NO runner; papers read_bundle/build_site, methods-distilled bib). drafts/lab OUT. repository=no ecosystem write path (publish=gate-check); benchmarks=local+disconnected write, queue needs external runtime/cluster runner; papers=reproducible export, potential core/UI feature, libn4m-WASM replay seam + bib re-distill gate. Proposed LOCK-PROV; gated on P1 ARB-010 + LOCK-IO/UI. No code/sync edits. | read-only; gates listed not run | NET-NEW: provider client layer, to_dataset_package, benchmark get_pipeline+runner orch, papers re-distill gate+UI; depends LOCK-CAP/RT(signed), LOCK-IO/UI.`

---

### Evidence (heads; read-only; only this file written)
`nirs4all-datasets/src/nirs4all_datasets/{__init__,access,catalog,dataset,retrieval,manifest,_acquire,publish,dataverse,reproduce,cli,health}.py` + `CLAUDE.md`;
`nirs4all-repository/src/nirs4all_repository/{__init__,_version,bridge,schema,store,fetch,index,scaffold,builder,evaluate,security,settings,cli}.py`;
`nirs4all-benchmarks/src/nirs4all_benchmarks/{__init__,cli,identity/pipeline_dag,store/{arena_store,queries},ingestion/{ingest,upload,resolve},scoring/{metrics,score_spec},adapters/{dagml_bundle,nirs4all_workspace,n4a_bundle},datasets/{catalog,dataset_card},contract/arena_run_export,service/app}.py` + `README.md`;
`nirs4all-papers/src/nirs4all_papers/{__init__,bundle,bibliography,provenance,site/{__init__,pages,assets},cli}.py` + `CLAUDE.md`.
Design/anchors: `MULTIMODAL_ECOSYSTEM_DESIGN_SCHEMAS.md` §1.1/§2.2/§3.2/§4bis/§4ter/§6.7-6.11/§11.3-11.5/§12.1; `PARALLEL_REFACTORING_ROADMAP.md` `L14`/`PROV-001..005`; `PARALLEL_REFACTORING_SYNC.md` `DEC-PROV-001`/board line 76; `CAP_spec.md`, `RT_spec.md`, `IO_spec.md`, `INTEGRATION_DIGEST_A0.md`.
