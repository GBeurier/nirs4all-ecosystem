# W10_PROVIDERS — providers scaffold + read adapters (L14, Wave-2B)

**Agent:** W10 (providers scaffold) · **Date:** 2026-07-01 · **Lane:** `L14` (Providers/plugins) · **Decision source:** `DEC-PROV-001` (still *proposed*).
**Repo:** `nirs4all-providers` (new sibling package, branch `main`, was an empty git repo). **This file + the new package are the only writes.** Sync board **not** edited.
**Builds on:** `IMP_L14_PROVIDERS_IMPL_PLAN.md` (the buildable map) and `SW6_PROV_PLUGINS_spec.md` (the contract audit). `RV10_NEXT_WAVE_PLAN.md` §4 W10 prompt.
**Scope honored:** read-adapter slice only. In scope = `nirs4all-datasets`, `nirs4all-repository`, `nirs4all-benchmarks`, `nirs4all-papers`. OUT = `nirs4all-drafts`, `nirs4all-lab` (private). No write path, no `to_dataset_package`, no publish/upload, no benchmark runner.

---

## 0. TL;DR

- Created the standalone **dependency-light `nirs4all-providers`** package (`IMP_L14` decision **D1**): hard-deps on **nothing** but the stdlib; each backing repo is an **optional extra**, soft-imported. This sidesteps the install-cycle hazard (providers depend *up* on `nirs4all`; folding the client into `nirs4all` as a hard dep would cycle — `IMP_L14` §1a).
- Implemented the **`ProviderPlugin` contract** + **soft-import registry** + **four read adapters** as thin delegations over each repo's *real* public API. No provider business logic is re-implemented here; adapters are pure wrappers (`DEC-PROV-001`: "renommer sur les vraies APIs; couche provider unifiante = net-new").
- **Unavailable backings degrade**, never raise at import: `health().available == False`, `version() == "unavailable"`, and read calls raise a single uniform `ProviderUnavailable` naming the exact extra.
- **Gates green:** `ruff check .` (clean) · `mypy src` (9 files, no issues) · `pytest -q` (**35 passed**). One local initial commit made. **Not pushed.**
- Validated both with **hermetic fakes** (no network, no real backing) and a **real smoke** against the installed `nirs4all-datasets 0.3.0` (164 datasets enumerated, cards resolved) — adapter signatures match the real API.

---

## 1. What was built (package layout)

```
nirs4all-providers/
  pyproject.toml          # setuptools, src-layout, dynamic version, py.typed; extras [datasets|repository|benchmarks|papers|all|dev]
  README.md  LICENSE  .gitignore
  src/nirs4all_providers/
    __init__.py           # re-exports the contract, the 4 adapters, and the registry fns
    base.py               # ProviderPlugin Protocol + Health/Capabilities/WriteAccess value objects
    _softimport.py        # soft_import() + SoftImport + ProviderUnavailable (uniform "extra missing")
    _adapter.py           # _BaseProvider: soft-import wiring + version()/health() (DRY scaffolding)
    datasets.py           # DatasetProvider     -> nirs4all_datasets
    repository.py         # PipelineProvider    -> nirs4all_repository
    benchmarks.py         # BenchmarkProvider   -> nirs4all_benchmarks (Queries facade)
    papers.py             # PaperExportProvider -> nirs4all_papers
    py.typed
  tests/                  # 8 files, 35 tests, hermetic (sys.modules fakes/hiding; no network)
```

`src` ≈ 612 LOC, `tests` ≈ 513 LOC. Each adapter is a few lines of delegation per method; the
soft-import/availability logic lives once in `_BaseProvider`.

## 2. Adapters — exact real API wrapped (re-verified at heads this pass)

| Provider (`provider_id`) | Backing (`__version__` seen) | Read methods → real API | Writes |
|---|---|---|---|
| `DatasetProvider` (`datasets`) | `nirs4all_datasets` (`0.3.0`) | `list_datasets`→`list(root,**f)` · `card`→`card(name,root)` · `get_dataset`→`get(name,...)` · `to_spectro_dataset`→`NirsDataset.to_nirs4all()` | `local-cache` |
| `PipelineProvider` (`repository`) | `nirs4all_repository` (`0.1.0`) | `list_pipelines`→`list(**f)` · `card`→`card(name,root=)` · `get_pipeline`→`get(...)` · `get_bundle`→`fetch(...)` · `verify`→`Pipeline.verify()` | `none` |
| `BenchmarkProvider` (`benchmarks`) | `nirs4all_benchmarks` (`0.1.0`) | `list_pipelines`→`Queries.pipelines()` · `get_pipeline(dag_hash)`→adapter-side filter · `leaderboard`→`Queries.leaderboard(**q)` · `get_results`→`Queries.run_detail(h)` · `planned`→`Queries.planned()` | `none` |
| `PaperExportProvider` (`papers`) | `nirs4all_papers` (`0.2.0`) | `inspect_bundle`→`bundle.read_bundle` · `load_paper`→`model.load_paper` · `build_methods_section`→`bibliography.build_bibliography` · `build_repro_page`→`site.build_site` | `local-output` (marker-guarded) |

Notes:
- `version()` reads each backing's live `__version__` (never hardcoded — confirmed `0.3.0` for datasets, which has drifted from the `0.1.0.dev0` the SW6 audit recorded).
- `benchmarks` reads go through the `Queries` facade over a local `ArenaStore(store_root)` (`store_root` from arg → `NIRS4ALL_BENCHMARKS_STORE` → `./arena-store`); the store is constructed only on a read call, never during `health()`.
- `get_pipeline(dag_hash)` is the one net-new read (`IMP_L14` **D4**): an adapter-side filter over `pipelines()`, zero benchmarks-repo change.

## 3. Contract decisions realized (from `IMP_L14` §7/§8)

- **D1 — home:** standalone `nirs4all-providers`, `dependencies = []`, providers as extras, soft-imported. Foldable into `nirs4all-core` later (file map is root-relative; only the package root would move). The `[all]` extra docstring flags the `nirs4all >=0.10,<0.11` co-resolution caveat (repository's pin is the tightest); this package never imports/pins `nirs4all`.
- **D5 — `health()`:** uniform `{available, reachable, version, detail}`. `available` = import-availability; `reachable` = an optional **network-free** deeper probe (`datasets`: local catalogue enumerates; `benchmarks`: `arena.sqlite` exists without constructing the store; `repository`/`papers`: `None` — no cheap non-network probe, matching "they have none today"). Datasets origin-health / benchmarks `/api/healthz` are deliberately **not** folded in (kept as separate deeper probes).
- **D6 — `capabilities()`:** provider-level `{serves, executes, writes, portability}`, **distinct** from the operator-level `ControllerCapability` (LOCK-CAP). `executes=False` for all four (read slice). `portability` only *references* CAP-002/CAP-004 per served artifact (e.g. papers replay surfaced as approximate / not numerically-portable).
- **Registry / not-controllers (`DEC-CTRL-001`):** `available_providers()` soft-imports each backing (never raises); `get_provider(id, **config)` raises the uniform `ProviderUnavailable` when the extra is absent; `provider_health(id)` returns liveness without raising. The registry is a surface separate from any controller registry.

## 4. Explicitly deferred (gated; NOT in this slice)

- `DatasetProvider.to_dataset_package` → gated **LOCK-IO** (`nirs4all-io` stays the assembly owner).
- `BenchmarkProvider.queue_evaluation` + any runner → gated **LOCK-RT** / **CLU-006** (the Arena stays runner-free; ingest-only).
- `PipelineProvider` network read service (= RT `inspect`), repository/datasets publish/upload → out of slice.
- Papers `export_sidecars` (wraps a private `_write_paper_sidecars`), `nirs4all-ui` rendering (LOCK-UI), libn4m-WASM replay (RT-WASM-001), and the methods-bibliography re-distill gate (methods/`L9`).

## 5. Gates (run from the package root; all green)

| Gate | Command | Result |
|---|---|---|
| Lint | `ruff check .` | **No issues found** |
| Types | `mypy src` | **Success: no issues found in 9 source files** |
| Tests | `pytest -q` | **35 passed** |

Tooling note: the package targets Python `>=3.11`; the repo's global `python3` is 3.10 and has no
`mypy`/`pytest` module, so the gates were run with the sibling `nirs4all/.venv` (Python 3.11.15; ruff
0.15.20, mypy 2.1.0, pytest 9.1.1) and `PYTHONPATH=src`. `ruff` also available globally (0.14.14).

**Test design (hermetic, "tests using fakes"):** `tests/conftest.py` provides `fake_modules(...)` and
`hidden_modules(...)` context managers that swap `sys.modules` entries, so every test controls backing
availability without importing a real provider package, touching the network, or creating an on-disk
store. Coverage: soft-import + uniform error; the contract value objects + `runtime_checkable`
`isinstance`; registry discovery/degradation; and per-adapter delegation + degradation for all four.

**Real-world validation (beyond fakes):** a no-fake smoke against the installed `nirs4all-datasets`
returned `available=['datasets']`, `version 0.3.0`, `health(available=True, reachable=True)`,
`list_datasets()` → 164 rows, and a resolved card — confirming the wrapped signatures match the live
API. With no backings installed, all four correctly report `available=False`.

## 6. Boundaries respected

- Net-new glue only; no re-implementation of `nirs4all` / `nirs4all-io` / `nirs4all-methods`. Lower layer stays the single source of truth.
- No network call originates in this layer; no ecosystem write-back; `health()` probes are local-only.
- Providers are **not** controllers; the read slice never reaches a `gated` write.
- `nirs4all-drafts` / `nirs4all-lab` untouched (private, out of scope). Sync board not edited.

## 7. Commit

One local initial commit on `main` (`feat: scaffold nirs4all-providers ...`). **Not pushed** (per brief).

---

### Worklog line (for A0 to paste — sync board NOT edited by W10)
`2026-07-01 | W2B/L14 | impl | nirs4all-providers scaffolded: ProviderPlugin contract + soft-import registry + 4 read adapters (datasets list/card/get/to_spectro_dataset; repository list/card/get/fetch/verify; benchmarks Queries pipelines/leaderboard/run_detail/planned + adapter-side get_pipeline; papers read_bundle/load_paper/build_bibliography/build_site) over the REAL repo APIs. Standalone dependency-light pkg (deps=[], providers as soft-imported extras) per IMP_L14 D1 — sidesteps the nirs4all install cycle. Unavailable extra -> health unavailable + uniform ProviderUnavailable; no network/writes. NO to_dataset_package/publish/runner (deferred LOCK-IO/RT/UI). Gates green: ruff + mypy(9) + pytest(35). Local initial commit, not pushed. | DEC-PROV-001 still proposed; slice-1 needs no decision.`

### Evidence (heads; only the new package + this report written)
APIs re-read this pass: `nirs4all-datasets/src/nirs4all_datasets/{__init__,dataset}.py`;
`nirs4all-repository/src/nirs4all_repository/{__init__,bridge}.py`;
`nirs4all-benchmarks/src/nirs4all_benchmarks/{__init__,version,store/queries,store/arena_store}.py`;
`nirs4all-papers/src/nirs4all_papers/{__init__,bundle,bibliography,model,site/__init__}.py`.
Convention template: `nirs4all-tools/` (src-layout, setuptools, dynamic version, py.typed, dual license).
Plans: `IMP_L14_PROVIDERS_IMPL_PLAN.md`, `SW6_PROV_PLUGINS_spec.md`, `RV10_NEXT_WAVE_PLAN.md` §4 (W10).
Gates: `ruff check .` / `mypy src` / `pytest -q` via `nirs4all/.venv` (py3.11); real-backing smoke via `nirs4all-datasets/.venv`.
