# Vision and strategy - nirs4all ecosystem

**Date:** 2026-06-29
**Status:** strategic target, not a release promise
**Audience:** maintainers, agents, reviewers, future contributors

This document supersedes the earlier NIRS-only framing. NIRS remains the first
scientific proof domain and the historical product, but the target architecture
is now explicitly multimodal: spectra, tabular variables, time series, images,
hyperspectral cubes, omics/genotype matrices, metadata and multi-target outputs
must be handled through the same identity-safe ML/DL execution spine.

The central rule is simple: **multimodal capability lives in contracts and
runtimes, not in duplicated product code**.

---

## 1. One-page vision

The nirs4all ecosystem should become an open-source scientific ML/DL stack for
multimodal biological data, with NIRS as the anchor domain.

The target product promise is:

> load heterogeneous biological data, align it by sample/observation/group
> identity, build leakage-safe ML/DL pipelines, fuse modalities, evaluate and
> explain models, then replay or deploy the result in the runtimes that can
> support its capabilities.

The architecture has five product layers:

1. **`dag-ml` + `dag-ml-data` are the multimodal core.**
   `dag-ml-data` owns typed data contracts, identities, representations, views,
   fingerprints and provider ABI. `dag-ml` owns graph/campaign contracts,
   phases, folds, OOF safety, leakage rules, selection, refit, replay and
   lineage. Together they are the language-neutral ML spine.

2. **`nirs4all-core` is the low-level aggregate.**
   The former `nirs4all-lite` concept is now `nirs4all-core`: a thin aggregate
   of `dag-ml`, `dag-ml-data`, `nirs4all-methods`, `nirs4all-io`,
   `nirs4all-formats`, and optionally peripheral clients such as datasets,
   repository, benchmarks, cluster and papers. It must expose and package the
   upstream domains; it must not reimplement parsers, numerical kernels,
   dataset inference or DAG execution. The current local directory named
   `nirs4all-core` is a temporary integration clone of the Python `nirs4all`
   repository where the `dag-ml` / `dag-ml-data` convergence is being finished;
   it is not the final aggregate repository design by itself.

3. **`nirs4all` is the full Python library above core.**
   The historical repository name `nirs4all` means the Python product for
   historical reasons. Architecturally it is `nirs4all-python`: public API
   (`run`, `predict`, `explain`, `retrain`, `session`, `generate`), Python
   controllers/operators, sklearn/torch/JAX/TF/Optuna/SHAP integration,
   compatibility facades, prototyping surface and community bridge.

4. **`nirs4all-<language>` packages follow the same pattern.**
   R, MATLAB/Octave, Julia, Rust, WASM/JS, CLI and other language products
   should be built on `nirs4all-core` plus language-specific controllers and
   tools when those are real. Repository names can remain explicit
   (`nirs4all-r`, `nirs4all-julia`, etc.), while published package names should
   use the idiomatic simple name `nirs4all` where the ecosystem allows it
   (for example CRAN `nirs4all`, npm `nirs4all`).

5. **`nirs4all-runtime-<target>` and `nirs4all-ui` separate execution from UI.**
   Runtimes are the API/execution surfaces consumed by apps: Python desktop
   runtime, WASM browser runtime, CLI runtime, R runtime, Rust runtime, etc.
   `nirs4all-ui` is a shared React component library for pipeline editors,
   dataset inspectors, charts, result views, operator palettes and bundle
   inspectors. Studio and Web become products assembled from runtime + UI +
   product-specific logic.

The goal is not "everything runs everywhere". The goal is that every pipeline
declares what is portable, what is host-specific, and why.

---

## 2. Target architecture

```text
raw data / folders / arrays / catalog entries
        |
        v
nirs4all-formats        low-level vendor/scientific readers
        |
        v
nirs4all-io             dataset assembly, inference, roles, joins, packages
        |
        v
dag-ml-data             multimodal schemas, identities, views, providers
        |
        v
dag-ml                  graph, phases, folds, OOF, leakage, replay
        |
        +------------------------------+
        | controllers / kernels         |
        | - nirs4all-methods / libn4m   |
        | - ONNX or future native cores |
        | - Python/R/MATLAB/DL hosts    |
        +------------------------------+
        |
        v
nirs4all-core           aggregate package, bindings, compat matrix, releases
        |
        +---------------------+----------------------+----------------------+
        |                     |                      |                      |
nirs4all Python      nirs4all-<lang> libs   nirs4all-runtime-*     tools/catalogs
        |                     |                      |
        +----------+----------+----------------------+
                   |
             nirs4all-ui
                   |
        +----------+----------+
        |                     |
nirs4all-studio        nirs4all-web
```

### 2.1 Data flow

`nirs4all-formats` decodes bytes and emits lossless records. It does not know
which column is a target or how to train a model.

`nirs4all-io` turns real user inputs into a dataset package:

```text
RESOLVE -> INFER -> CONFIGURE -> MATERIALIZE -> EMIT
```

It owns input conventions, source roles, joins, sidecars, explicit partitions
and identity propagation. It should emit both legacy projections when needed
(`SpectroDataset`) and canonical `dag-ml-data` envelopes/providers.

`dag-ml-data` is the source of truth for `representation_id`, axes and sample
relations. It must cover at least:

- spectra: `signal_1d`, `signal_with_processings`, Raman, FTIR;
- tabular: `tabular_numeric`, `tabular_mixed`, `feature_block_set`;
- time series: `series_mv`;
- genotype/omics: `variant_matrix`, `dosage_matrix`;
- images/cubes: `rgb_image`, `gray_image`, `mc_image`,
  `multispectral_image`, `cube_hwb`;
- masks: `segmentation_mask`, `roi_mask`;
- metadata and targets: `sample_metadata`, numeric/categorical targets,
  multivariate target matrices;
- mass spectra and text where the contracts exist.

`dag-ml` must stay representation-agnostic. It sees identities, handles,
descriptors, fingerprints, folds, prediction tables and artifacts; it must not
own heavy feature buffers, file parsing, or numerical kernels.

### 2.2 Pipeline flow

Pipeline definitions can originate from:

- Python `nirs4all` DSL;
- Studio node graph;
- Web node graph;
- `nirs4all-core` / language binding pipeline spec;
- repository recipe or benchmark scenario.

They should compile toward common contracts:

```text
Pipeline DSL / node graph / recipe
        |
        v
PipelineDslSpec
        |
        v
dag-ml GraphSpec + CampaignSpec
        |
        v
ExecutionPlan
        |
        v
controller runtime
```

The controller runtime can be:

- portable numerical core (`nirs4all-methods` / `libn4m`);
- Python host controller (sklearn, torch, JAX, TF, SHAP, Optuna);
- R/MATLAB/Julia host controller when a language product actually owns it;
- WASM controller for browser-safe capabilities;
- ONNX or another explicit inference/runtime artifact when validated.

### 2.3 Portability model

Portability is a capability ledger, not a slogan.

| Level | Meaning |
|---|---|
| `contract_readable` | The runtime can open the bundle/spec and inspect graph, data schema and metadata. |
| `data_readable` | The runtime can materialize the required data representations. |
| `operator_available` | Every required operator exists in that runtime. |
| `numerical_parity` | Outputs match a cross-runtime fixture within declared tolerance. |
| `trainable` | The runtime can train/refit the pipeline. |
| `predictable` | The runtime can replay/predict with the stored artifact. |
| `explainable` | The runtime can compute the declared explanations. |

Every `.n4a` or successor bundle should be openable everywhere, but not every
artifact will be executable everywhere. Python-only artifacts remain legitimate
if they are explicitly tagged as Python-only.

---

## 3. Repository ownership map

| Repository / concept | Target role | Must not do | Current reading |
|---|---|---|---|
| `dag-ml` | Multimodal, data-agnostic ML coordinator: graph, phases, folds, OOF/leakage, selection, refit, replay, lineage. | Parse files, own matrices, implement PLS/SNV/SG, infer datasets. | Core contracts and gates are advanced; end-to-end host execution still needs hardening. |
| `dag-ml-data` | Canonical multimodal data contracts: representations, axes, relations, providers, fingerprints. | Run ML phases, choose splits, parse vendor files, do feature extraction. | Vocabulary is close to the target; production providers remain a key gap. |
| `nirs4all-formats` | Low-level Rust readers for spectroscopy/scientific files and provenance. | Dataset roles, joins, preprocessing, modelling, UI. | Strong NIRS/spectroscopy base, useful for HSI and scientific readers. |
| `nirs4all-io` | Dataset assembly and multimodal package creation. Emits `dag-ml-data`. | Random CV policies, ML orchestration, vendor parser duplication, numerical methods. | NIRS/tabular path mature; multimodal v2 package is the next workstream. |
| `nirs4all-methods` | Portable numerical NIRS/chemometrics core (`libn4m`) with C ABI and bindings. | Dataset loading, DAG scheduling, Studio logic, arbitrary Python/DL. | Rich and credible, but release/ABI/platform hardening remains critical. |
| `nirs4all-core` | Final aggregate low-level product: bindings, compatibility matrix, conformance pack, release glue. | Become a second `nirs4all`; patch upstream logic; hide unsupported capabilities. | Canonical public name for the low-level aggregate formerly discussed as `nirs4all-lite`; the local checkout is the active integration home for the ongoing `dag-ml`/`dag-ml-data` cutover. |
| `nirs4all` | Full Python library, historical API, Python ML/DL/explainability/prototyping layer. | Keep duplicating low-level parsing/orchestration long term. | Product-rich; migration to core must preserve public contracts. |
| `nirs4all-<language>` | Language-specific full library above core when the language has real extra controllers/tools. | Reimplement core logic in each language. | Future pattern; today most surfaces are bindings or aggregate packages. |
| `nirs4all-runtime-<target>` | API/runtime surface consumed by apps or tools for one target. | Become a separate scientific stack. | Concept to formalize; Python and WASM are first candidates. |
| `nirs4all-ui` | Shared React UI package for reusable components and product visual language. | Own backend logic, ML logic, parsers, persistence formats. | New project; current code is split between Studio/Web/sites. |
| `nirs4all-studio` | Desktop product: Python runtime + shared UI + Electron + backend + package management + Studio logic. | Reimplement `nirs4all` or scientific algorithms in the backend/frontend. | Functional and rich; must consume capabilities instead of maintaining divergent registries. |
| `nirs4all-web` | Browser product: WASM runtime + shared UI + browser-specific data/runtime logic. | Claim parity for unsupported heavy Python/DL workflows. | Real browser client exists; full WASM parity remains bounded and must be declared. |
| `nirs4all-datasets` | Citable dataset catalog and acquisition layer. | Bake benchmark tasks into datasets or rehost data against upstream terms. | Important for scientific proof; catalog/retrieval maturity must be tracked honestly. |
| `nirs4all-repository` | Versioned repository of recipes/bundles. | Score or rank methods itself. | Complements benchmarks and runtimes. |
| `nirs4all-benchmarks` | Curated, reproducible benchmark and result browser. | Become a Kaggle-style external execution platform by default. | Prototype/static path exists; live meta-analysis is later. |
| `nirs4all-cluster` | Trusted distributed execution prototype. | Production multi-tenant service without security/isolation investment. | Useful but not central to the multimodal MVP. |
| `nirs4all-papers` | Public reproduction kits and paper artifacts. | Hold private drafts or unpublished sensitive data. | Supports citation and reproducibility. |
| `nirs4all-ecosystem` | Meta-repo and likely first home for global aggregation manifests, rebuild scripts and version-lock orchestration. | Become a product runtime or duplicate cockpit monitoring. | Today pins submodules and has minimal `pull-all.sh`; should grow release/rebuild tooling before a new repo is created. |
| `nirs4all-cockpit` | Read-only release and health monitoring dashboard, plus guarded admin visibility. | Own rebuild logic or become the release orchestrator. | Already covers monitoring; should consume aggregation manifests and report drift. |

---

## 4. Naming decisions

### 4.1 Historical `nirs4all-lite` -> `nirs4all-core`

The concept formerly called `nirs4all-lite` is renamed in product and
architecture discussions to `nirs4all-core`. The old name is historical only;
there is no public compatibility alias to maintain.

Reason:

- it is not "lite" in the code sense; it aggregates the low-level stack;
- it is the foundation used by full language products;
- "lite" suggests a reduced user product, while the target is a canonical core.

Naming rule:

1. `nirs4all-core` is the canonical aggregate name;
2. do not create two competing aggregate repositories;
3. do not publish or preserve a public `nirs4all-lite` alias;
4. keep historical references only where they explain pre-rename decisions.

### 4.2 `nirs4all` repository name

The repository `nirs4all` remains the Python library for historical reasons. In
architecture documents, call it **`nirs4all Python`** or **`nirs4all-python`**
when ambiguity matters.

### 4.3 Published package names

For language communities, the public package name should usually be simply
`nirs4all` when available and idiomatic. Repository names can stay explicit:

- repo: `nirs4all-r`, package: `nirs4all`;
- repo: `nirs4all-julia`, package: `nirs4all`;
- repo: `nirs4all-web`, npm/browser product as appropriate;
- repo: `nirs4all-runtime-wasm`, npm runtime if split later.

---

## 5. Product assembly

### 5.1 Python library

`nirs4all` Python is the superset product. It should keep:

- stable public API and result objects;
- `SpectroDataset` compatibility where needed;
- sklearn ecosystem compatibility;
- SHAP, Optuna, torch, TensorFlow, JAX and TabPFN integrations where useful;
- workspace/bundle compatibility facades during migration;
- prototype operators before they are promoted to lower layers.

But every capability should be classified:

- `portable_core`: executable through `nirs4all-core`;
- `portable_methods`: executable through `nirs4all-methods`;
- `portable_onnx`: replayable through ONNX or another declared runtime;
- `host_validated`: equivalent exists in another language with parity fixtures;
- `python_only`: legitimate, but not portable.

### 5.2 Language libraries

A `nirs4all-<language>` library should exist only when it adds more than raw
bindings:

- idiomatic controllers/operators;
- language-native dataset ergonomics;
- language-specific ML/DL tooling;
- documented parity with core fixtures;
- package lifecycle and maintainers.

Otherwise, the language should be served by `nirs4all-core` bindings.

### 5.3 Runtimes

Runtimes are stable execution/API surfaces, not full user libraries.

Initial candidates:

- `nirs4all-runtime-python`: API surface used by Studio, CLI, notebooks and
  automation; wraps `nirs4all` Python.
- `nirs4all-runtime-wasm`: browser-safe execution over WASM packages, used by
  `nirs4all-web`.
- `nirs4all-runtime-cli`: command-line/automation runtime over core and Python
  where installed.
- future `nirs4all-runtime-r`, `nirs4all-runtime-rust`,
  `nirs4all-runtime-julia` if the language products justify them.

The runtime API should expose:

- capabilities;
- dataset inspection/materialization;
- graph compile/validate/plan;
- run/predict/replay when supported;
- result and bundle inspection;
- explicit unsupported diagnostics.

### 5.4 Shared UI

`nirs4all-ui` should centralize reusable React UI:

- pipeline editor primitives;
- node palette and capability badges;
- dataset/source/variable inspectors;
- spectra/image/cube/time-series previews;
- score, residual, prediction and explanation charts;
- run progress and job state components;
- bundle/repository/dataset cards;
- low-level design system components when not already provided by a shared
  dependency.

It should not own:

- FastAPI routes;
- Electron integration;
- browser file system/WASM runtime code;
- ML/data logic;
- persistence schemas.

Consumers:

- `nirs4all-studio`: shared UI + Python runtime + Electron/backend/product
  logic.
- `nirs4all-web`: shared UI + WASM runtime + browser-specific logic.
- `nirs4all-org`, papers, benchmarks or repository sites can reuse selected
  components only when that does not force application complexity into them.

---

## 6. Current state, honestly

What is already credible:

- `dag-ml` and `dag-ml-data` have advanced contracts, validation gates and
  release-hardening docs.
- The main `nirs4all` backend convergence is actively being finished in the
  temporary local `nirs4all-core` clone. If this work lands cleanly, the
  remaining effort moves from "prove the entire cutover" to hardening,
  contract completion, release and product reassembly.
- `dag-ml-data` has already moved toward the multimodal representation
  catalogue needed by the target design.
- `nirs4all-io` has an explicit multimodal backlog and is the next planned
  workstream for dataset package production.
- the former `nirs4all-lite` workstream already acted like an aggregate of the
  low-level stack and is therefore the historical starting point for
  `nirs4all-core`.
- `nirs4all-methods` has a serious portable C++/C ABI foundation and multiple
  bindings.
- `nirs4all-formats` and `nirs4all-io` already enforce the parser/assembly
  boundary.
- `nirs4all` Python and Studio provide the richest current user experience.
- `nirs4all-web` proves that a browser/WASM product is viable for a bounded
  portable subset.
- datasets, repository, benchmarks and papers exist as the right peripheral
  scientific infrastructure.

What is not yet solved:

- production `dag-ml-data` providers beyond conformance/in-memory paths;
- full `dag-ml` host-controller execution parity across Python/DL/operator
  surfaces;
- release-grade rebuild/version-lock tooling for aggregate packages;
- complete `nirs4all-methods` release hardening across platforms and ABI
  matrices;
- a clean final `nirs4all-core` naming/repo/package transition after the
  temporary integration clone has served its purpose;
- a runtime API contract shared by Studio/Web/CLI/language clients;
- a shared React UI package;
- full multimodal `nirs4all-io` v2 package support for images, cubes, time
  series and genotype/omics;
- cross-runtime bundle replay for anything beyond declared portable artifacts;
- public claims that stay synchronized with the real maturity of each repo.

---

## 7. Feasibility and effort

The proposal is feasible because the hardest conceptual boundaries already
exist. It is not cheap because it turns a set of strong repositories into a
coherent multi-language product platform.

Counting rule: the old migration backlog remains useful as **total work
already identified**, but it should not be read as the remaining effort if the
temporary `nirs4all-core` integration clone lands cleanly. The active work
changes the plan from "start the cutover" to "finish, harden, release and
package the cutover".

| Workstream | Total design estimate | Remaining if current integration lands |
|---|---:|---:|
| Python backend convergence to `dag-ml`/`dag-ml-data`/`libn4m` while preserving Studio contracts | 110-150 person-weeks | 15-35 person-weeks for parity closure, Studio lifecycle, fallback/rollback, release hardening |
| `nirs4all-core` final aggregate: rename/lineage, compatibility matrix, conformance pack, release train | 10-18 person-weeks | 8-14 person-weeks |
| Global aggregation rebuild/version tooling, likely first in `nirs4all-ecosystem` | 8-16 person-weeks | 8-16 person-weeks |
| Production `dag-ml-data` providers and `dag-ml` adapters needed for core runtimes | 10-20 person-weeks | 8-16 person-weeks |
| `nirs4all-io` multimodal v2 package path: source model, identity propagation, payload store, spectra/image/cube/series/genotype profiles | 26-44 person-weeks | 22-38 person-weeks |
| Runtime API layer: Python/WASM/CLI first, later R/Rust/Julia as justified | 18-34 person-weeks | 14-26 person-weeks |
| `nirs4all-ui` extraction and first consumers | 20-35 person-weeks | 18-30 person-weeks |
| Studio/Web reassembly on runtime + shared UI + capability registry | 22-44 person-weeks | 18-36 person-weeks |
| Datasets/repository/benchmarks integration for scientific proof | 18-34 person-weeks | 14-28 person-weeks |
| Cluster production-grade hardening, if pursued | 10-20 person-weeks | 10-20 person-weeks |

Practical framing:

- **If the temporary `nirs4all-core` integration is accepted as mostly done:**
  remaining MVP effort is roughly **105-190 person-weeks**, mainly hardening,
  `nirs4all-io` multimodal v2, aggregate release tooling, runtimes and UI.
- **If the integration has to be redone from the documented baseline:** fall
  back to the earlier **180-260 person-week** MVP range.
- **Production multi-language platform from here:** roughly **160-280
  person-weeks** after the active integration lands, excluding any serious
  multi-tenant cluster service.
- **Calendar:** 2-4 quarters with a small focused team; longer if one maintainer
  remains the only strategic reviewer.

Confidence: medium. The architecture is clear; the uncertain parts are
integration details, release discipline, platform packaging, and keeping public
claims aligned with real runtime support.

---

## 8. Backlog

### P0 - Decisions and source of truth

- Record that the current local `nirs4all-core` is a temporary integration clone
  of Python `nirs4all`, not the final aggregate repository.
- Record the completed `nirs4all-lite` -> `nirs4all-core` naming decision,
  including the no-legacy-alias rule.
- Keep the final aggregate lineage documented in the source-of-truth table as
  the integration clone is hardened.
- Define public naming: repositories, packages, imports, runtimes.
- Define the capability vocabulary and unsupported diagnostics.
- Freeze cross-repo compatibility matrix: `dag-ml`, `dag-ml-data`, `io`,
  `formats`, `methods`, `core`.

Exit: no two repositories claim to be the aggregate core; every public name has
one owner.

### P1 - Core execution and conformance

- Preserve the `nirs4all` Python API while routing supported execution through
  `dag-ml`.
- Keep current storage/bundle compatibility until all existing tests are green.
- Add a shared conformance pack across Python/core/WASM/R/MATLAB where possible.
- Add ABI-skew, FFI/lifetime, panic/error and thread-safety gates.
- Wire portable `nirs4all-methods` operators incrementally with parity gates.

Exit: supported NIRS pipelines are contract-compatible; unsupported ones fail
or fall back explicitly.

### P2 - Global aggregation/release tooling

- Add a machine-readable aggregation manifest for each aggregate product:
  component repo, component version/tag/commit, ABI version, artifact target,
  runtime target and compatibility range.
- Add commands for rebuild planning, version bump propagation, lockfile update,
  artifact matrix generation and dry-run release checks.
- Start this in `nirs4all-ecosystem`, which already pins the submodules and is
  the natural source of cross-repo truth.
- Keep `nirs4all-cockpit` as the read-only monitoring/health layer: it should
  consume the aggregation manifests and show drift, not own rebuild logic.
- Split to a dedicated `nirs4all-release` / `nirs4all-build` repository only if
  the tooling outgrows the meta-repo or needs independent release cycles.

Exit: rebuilding an aggregate is driven by a manifest and reproducible command,
not by hand-updated README instructions.

### P3 - Core aggregate release

- Rename `nirs4all-lite` to `nirs4all-core` without keeping a public legacy alias.
- Publish aggregate bindings for the first priority targets.
- Generate SBOM/provenance and release artifacts.
- Publish compatibility matrix and support window.
- Expose `formats`, `io`, `methods`, `dag_ml`, `dag_ml_data` domains directly.

Exit: a user can install core and inspect/execute the declared portable subset
without importing full Python `nirs4all`.

### P4 - Multimodal data path

- Add `DatasetSpec` v2 / `DatasetPackage` in `nirs4all-io`.
- Carry sample/observation/group/origin/repetition identities end to end.
- Emit multimodal `dag-ml-data` envelopes and payload stores.
- Support first profiles: native spectra + reference table, image folder,
  hyperspectral cube, fixed-length time series, genotype descriptor-first.
- Keep `SpectroDataset` as a projection, not the canonical multimodal model.

Exit: at least one NIRS, one image, one cube and one time-series fixture validate
through `nirs4all-io` -> `dag-ml-data` -> `dag-ml`.

### P5 - Runtime layer

- Define runtime API: capabilities, inspect, validate, plan, run, predict,
  replay, explain where supported.
- Implement Python runtime over `nirs4all`.
- Implement WASM runtime over core/WASM packages for the browser subset.
- Add CLI runtime for automation and smoke tests.
- Decide if R/Rust/Julia runtimes are needed or if bindings are enough.

Exit: Studio and Web can depend on runtime contracts instead of bespoke
execution assumptions.

### P6 - Shared UI

- Create `nirs4all-ui`.
- Extract stable components from Studio first, then adapt Web.
- Normalize React/version/build assumptions.
- Add capability badges and portability views as first-class UI concepts.
- Keep app-specific state, routing and backend calls outside the package.

Exit: Studio and Web render shared pipeline/dataset/result components while
keeping distinct runtimes.

### P7 - Product reassembly

- Studio = `nirs4all-runtime-python` + `nirs4all-ui` + Electron + backend +
  Python package management + Studio-specific workflows.
- Web = `nirs4all-runtime-wasm` + `nirs4all-ui` + browser-specific loaders,
  permissions and persistence.
- Repository/benchmarks/datasets/papers consume capabilities and bundle metadata
  without duplicating execution logic.

Exit: products share UI and contracts but keep their deployment-specific logic.

### P8 - Scientific proof

- Publish a citable NIRS reference release and examples.
- Curate datasets with DOI/licenses/cards/Croissant where applicable.
- Build benchmark scenarios with anti-leakage split policies.
- Demonstrate multimodal fusion on a real biological case, preferably CIRAD
  phenotyping or multi-instrument/campaign transfer.

Exit: the architecture is not only built; it is scientifically defensible.

---

## 9. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Naming confusion between `nirs4all`, `nirs4all-core`, historical `nirs4all-lite`, `nirs4all-web` | Users and packages cannot understand what to install. | ADR, one source-of-truth table, historical note only for `nirs4all-lite`, no public legacy alias. |
| Confusion between the temporary local `nirs4all-core` integration clone and the final aggregate product | Wrong repository lineage or premature public naming. | Document the temporary status; merge or retire it before freezing the final aggregate repository. |
| `nirs4all-core` becomes a second implementation | Maintenance collapse and divergent results. | Core may aggregate and expose; all fixes go upstream. |
| Aggregate rebuilds and version bumps remain manual | Broken releases, ABI skew and unreproducible Studio/Web/Core bundles. | Add manifests, lockfiles, dry-run release checks and rebuild commands, likely first in `nirs4all-ecosystem`; Cockpit monitors the result. |
| `dag-ml` remains a validator rather than actual runtime | Multimodal claim stays architectural only. | Prioritize executable host-controller path and conformance fixtures. |
| Browser over-claims parity | Reputational risk and broken demos. | Capability ledger, explicit unsupported diagnostics, WASM parity tests. |
| UI extraction becomes a design-system rewrite | Long stall without product value. | Extract only consumed components; Studio first, Web second. |
| Multimodal data abstractions flatten biological identities | Leakage or invalid science. | Keep sample/observation/group/origin/repetition explicit through `dag-ml-data`. |
| Too many language targets at once | Release train instability. | Prioritize Python, WASM/browser, R, MATLAB/Octave; defer the rest until users exist. |
| License ambiguity blocks industrial use | Adoption risk. | Maintain public license matrix by repo/artifact/runtime. |
| Strategic bus factor | Architecture and claims depend on too few people. | Executable gates, public ADRs, external validation, visible maintainers. |

---

## 10. Strategic rule

Do not sell this as "all NIRS tools in all languages".

The defensible long-term position is:

> nirs4all is a reproducible, leakage-safe, cross-runtime scientific ML stack
> for spectroscopy and multimodal biological data, with clear capability
> contracts and explicit portability.

That story is stronger than a pile of bindings, and it is realistic if the
ecosystem keeps its current boundary discipline.
