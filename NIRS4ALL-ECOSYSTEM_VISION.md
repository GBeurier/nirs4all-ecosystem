# Vision and strategy — nirs4all ecosystem

## 1. One-page vision

The nirs4all ecosystem has three overlapping ambitions:

1. **Make`nirs4all`(Python lib) +`nirs4all-studio`(Electron) an open-source reference option for applied NIRS** — aiming to complement, or even compete for certain uses, established proprietary tools (PLS_Toolbox, Unscrambler, SIMCA) and existing open-source bricks (R`prospectr`/`mdatools`/`pls`/`hyperSpec`, Python`SpectroChemPy`, Orange-Spectroscopy/Quasar, HyperSpy/Spectral Python), with native integration of modern ML/DL frameworks (sklearn, PyTorch, JAX, TabPFN) and reproducibility by build. 2. **Build underneath a reusable infrastructure layer outside the NIRS domain**:`dag-ml`(Rust reproducible ML coordination core, OOF-safe) and`dag-ml-data`(identity-aligned data contracts). A publishable, domain-agnostic foundation in computer science/ML. 3. **Port everything to all useful scientific ecosystems**: lightweight Python, R, MATLAB/Octave, Julia, C/C++, WASM, Android — via thin bindings hosted in`nirs4all-methods`/`nirs4all-formats`, and via`nirs4all-lite`which distributes **the chain of low-level packages** (`nirs4all-formats`+`nirs4all-io`+`nirs4all-methods`+`dag-ml`[+`dag-ml-data`]) in installable bundles per target language (PyPI under`nirs4all-lite`, CRAN/R-universe under`nirs4all`, MATLAB toolbox, Julia Pkg, npm under`nirs4all`, Conda, Docker, vcpkg/Conan/Homebrew, .deb/.rpm). **The “lite” is semantic: excluding the complete`nirs4all`Python library, we lose sklearn/PyTorch/TF/JAX, therefore reduced capability; it is neither a subset of the code nor a rewrite.** Zero new digital code. Build, release and supply-chain recipes live in`nirs4all-lite`as long as they serve this distribution.

In the long term:`nirs4all-studio`becomes a multi-modal scientific workshop (time series, hyperspectral, genomics, tabular) thanks to`dag-ml`/`dag-ml-data`, and`nirs4all-arena`becomes a public repository of pipelines + reproducible datasets, with a methods × datasets comparison matrix curated internally and published for reading (not an external competition platform).

---

## 2. Ecosystem mapping

Four logical layers. Each repository lives in parallel in`~/nirs4all/`;`nirs4all-ecosystem`is the parent that pins them into submodules.

### Layer 0 — Agnostic foundations (Rust)

| Repository | Role | State |
|---|---|---|
| `dag-ml` | Rust core: graph compilation, scheduling, replay, lineage, fingerprints, OOF validation, C ABI boundary. External operators (controllers). | active, versioned contracts |
| `dag-ml-data` | Schemas + data contracts aligned by identity (sample/group/origin), representation planner, multi-source fusion, ABI host-provider. | active, contracts shared with`dag-ml` |

### Layer 1 — NIRS readers and assemblers (Rust + Python)

| Deposit | Role | State |
|---|---|---|
| `nirs4all-formats` | Rust readers for ~58 spectroscopic formats (OPUS, JCAMP, SPC, ASD, ENVI, HDF5, MATLAB v7.3…). Parsers are Rust-only; Python/R/WASM/C bindings convert. | active, under conformance validation |
| `nirs4all-io` | Assembly bridge: arbitrary input →`RESOLVE → INFER → CONFIGURE → MATERIALIZE`→`SpectroDataset`. Python (phase 1 OK, parity with`DatasetConfigs`), Rust (phase 2 delayed). | Python alpha+, Rust planned |
| `nirs4all-methods` (`libn4m`) | Portable PLS / NIRS C++17 engine + stable C ABI. Python bindings (`nirs4all-methods`, `pls4all`), R (vendored CRAN-ready build), MATLAB/Octave (MEX), JS/WASM. Julia / JNI / Android are still at scaffold stage. | post-merge refactor in progress; 4 bindings build + publicly documented`<1e-12`parity (local CI reports tighter) |

### Layer 2 — Reference library and UI

| Repository | Role | State |
|---|---|---|
| `nirs4all` | Lib Python pipeline NIRS:`SpectroDataset`, controllers, operators (SNV, MSC, SG, OSC, EPO, CARS, MCUVE, physical augmentations…), PLS variants (AOM-PLS, POP-PLS, IKPLS, MBPLS, DiPLS, SparsePLS, LWPLS, KOPLS…), parallel execution, SQLite+Parquet workspace,`.n4a`bundle, integration sklearn/TF/PyTorch/JAX, SHAP. | 0.9.x, API stable, riche |
| `nirs4all-studio` | Electron + React 19 + FastAPI app on top of`nirs4all`. Drag-and-drop pipeline editor, dashboards, runs/predictions, playground. The backend never reimplements the lib. | active, UI stabilization |

### Layer 3 — Data, benchmarks, papers, community

| Deposit | Role | State |
|---|---|---|
| `nirs4all-datasets` | Catalog + *pooch-style* access to NIRS datasets on Dataverse (Research Data Gouv / CIRAD), targeted outputs: DOIs, data cards, Croissant. Reuses`nirs4all-io`. | functional stub: 1 example dataset, DOIs/cards/manifests not yet populated; public repos |
| `nirs4all-arena` | Publishable benchmark environment: pipelines × datasets × methods, reproducible runs via`.n4a`files, browsing site. | stub (README only) |
| `nirs4all-aom` | Companion code for the AOM-PLS / POP-PLS / AOM-Ridge / FastAOM paper. To be migrated to`nirs4all-methods`eventually. | beta, paper in progress |
| `nirs4all-lab` | Private prototyping space: NICon, FCK-PLS, synthesis (ViTnirs), TabPFN, subset analysis, benchmark harness. | active, private |
| `nirs4all-org` | Static landing page for nirs4all.org. | online, formerly `nirs4all-webpage` |
| `nirs4all-papers` | Public repository of ecosystem papers + reproducible`.n4a`artifacts. | public, README seed; reproducible code to migrate per paper |
| `nirs4all-drafts` | Drafts and private papers +`.n4a`artifacts. | private, former role of`nirs4all-papers` |
| `nirs4all-lite` | **Simplified multi-language distribution** of the low-level chain (`nirs4all-formats`+`nirs4all-io`+`nirs4all-methods`+`dag-ml`[+`dag-ml-data`]). Installable bundles for lightweight Python (PyPI`nirs4all-lite`), R (CRAN/R-universe`nirs4all`), MATLAB/Octave, JS/WASM (npm`nirs4all`), then Julia, C/C++ (vcpkg / Conan / Homebrew / .deb / .rpm), Conda channel, Docker images. **The “lite” is semantic: reduced capability excluding the full Python library, not a reduced codebase.** Zero digital code, zero upstream patches. Strict scope, upstream libs pinned by tag. | public, buildable bindings scaffold and green CI |
| `nirs4all-cluster` | Public distributed execution prototype. Used to control worker/server risks and controlled spikes; it does not yet replace a stable`nirs4all.run(executor=...)`backend. | public alpha/prototype, not a product |

### Dependency schema (NIRS “live” path)

```
fichiers terrain
      │
      ▼
nirs4all-formats   (lecture Rust, 58 formats)
      │
      ▼
nirs4all-io       (assemblage, inférence, parité DatasetConfigs)
      │
      ▼
nirs4all          (pipelines, opérateurs, runs, predictions, bundle .n4a)
      │
      ▼
nirs4all-studio   (UI, visualisations, project management)


            independent but designed to integrate
nirs4all-methods (libn4m)  ──►  callable from nirs4all (controllers) or standalone
dag-ml + dag-ml-data       ──►  potential/conditional execution substrate + multimodal layer for nirs4all-studio
                              (conditioned on effective coupling with `nirs4all`, item P1 §6.4)
nirs4all-aom               ──►  AOM methods, future candidates to migrate into nirs4all-methods
nirs4all-datasets          ──►  provider consumed by nirs4all-io
nirs4all-arena             ──►  consumer of published .n4a bundles
```

---

## 3. Current state (honest snapshot)

What is **really in hand** today:

- **`nirs4all`0.9.x**: stable public API (`run / predict / explain / retrain / session / generate`), stable SQLite+Parquet workspace schemas, stable`.n4a`bundle. Very broad NIRS operator coverage. Parallelism via`joblib`. sklearn/PyTorch/TF/JAX/Optuna integration. Highly expressive DSL pipeline (`_or_`,`_grid_`,`_cartesian_`,`_zip_`,`_chain_`,`_sample_`,`branch`/`merge`,`tag`/`exclude`,`concat_transform`,`rep_to_sources`/`rep_to_pp`). - **`nirs4all-studio`**: Electron + Vite + FastAPI functional, drag-and-drop pipeline editor, node register (static + auto-generated from sklearn/nirs4all/TF), WebSocket for progress, desktop packaging (PyInstaller bundling). Remaining UX debt (see`Roadmap.md`). - **`nirs4all-methods`**: 4 BUILD bindings + verified digital parity (publicly:`rmse_rel < 1e-12`on the SPEC side; local CI R`~9e-18`, Octave`~4e-16`, JS`~1e-16`). Catalog ↔ ABI: the internal working note`finish-lib-progress.md`reports 669/669 reconciled, the public docs (SPEC, release_process) are more cautious (catalogued 427/669, guessed 419, unmapped 662) — **freshness delta to be clarified in the repo before external communication**. Remaining items: OS wheels macOS/Windows matrix, CRAN submission (form), PyPI Trusted Publishing publication. - **`nirs4all-formats`**: Rust registry + readers in place, double conformance (golden summaries + comparison to brukeropus/spc-spectra/jcamp/spectrolab/h5py). Bindings Python/R/WASM, C ABI scaffold. Workflow release tag-triggered ready. - **`nirs4all-io`**: Phase 1 Python completed + byte-for-byte parity with`nirs4all.DatasetConfigs`, ~200 tests, ruff/mypy clean. Phase 2 Rust pending. - **`dag-ml`+`dag-ml-data`**: active crates, shared JSON contracts, C ABI + Python bindings ctypes smoke, stable fingerprints, validation envelope + materialize. Maturity level: **scaffold + advanced conformance pack**; the production host controller adapters, the production providers, and the connector from the DSL`nirs4all`are not implemented. Today no`nirs4all`pipeline runs through`dag-ml`. - **`nirs4all-aom`**: code used for the manuscript, 3 families (`pls`/`ridge`/`fast`). **arXiv v2 ready** (`paper/aom_arxiv_v2.tar.gz`bundle, abstract finalized, public repo referenced in`main.tex`). For Talanta, recent benchmark audit (May 28): the initial`paper/review/paper_review.md`(May 17) overestimated the compute blockers. **The missing experiences cited by the review already exist** in the archived workspaces (Blender + AutoSelect seeds 0/1/2 on 26 datasets in`_archive/trashed_runs/AOM_v0_legacy/Ridge/benchmark_runs/da001_*_seeds012/`, RMSEP identical between seeds — caveat: the SPXY3 split is deterministic by protocol, so it is *protocol determinism*, not robustness to repeated partitions; strong conventional baseline covered by`pls-tabpfn-hpo-25trials`which does HPO on`norm`/`smooth`/`baseline`/`osc`/ components — to be presented as “conventional search space under HPO”, not as a fixed recipe). Remaining Talanta work: (a) re-aggregate workspaces archived in`final_stats.md`+ supplement, by deduplicating`(dataset, variant, seed)`and scaling the claim to N=26 (or rerun the 6 missing datasets to reach N_cap=32); (b) promote the missingness audit in published tables; (c) failure-modes paragraph + table; (d) SPORT/PORTO/PROSAC + ML-bias quotes; (e) reflow Figure 5; (f) explain the PLS-HPO search space in the text; (g) smoke-test the reproducibility repo. **Total effort ~2-3 human days, ~0 additional compute** (or +6 datasets if we aim for strict N_cap=32 for multi-seed). Details in the revised header of`paper/review/paper_review.md`. - **`nirs4all-datasets`**: structure + CLI + Dataverse integration in place, but the local catalog contains **only one example dataset** with`doi: null`,`has_card: false`,`has_manifest: false`. Actual status: *working stub*, not alpha in the publishable sense. - **`nirs4all-org`**: aligned inline with public names (`nirs4all-web`,`nirs4all-lite`,`nirs4all-cluster`); formerly`nirs4all-webpage`. - **`nirs4all-web`**: former`nirs4all-lite`browser/WASM role, published under its own name; build, single-file build and browser smokes validated. - **`nirs4all-papers`/`nirs4all-drafts`**: remotes aligned with the target separation (`papers`public,`drafts`private). - **`nirs4all-lite`**: public remote; multi-bindings distribution scaffold in place with CI Rust, Python, npm/WASM, R and MATLAB/Octave. Remaining work: replace thin loaders with complete upstream integrations and add pipeline parity fixtures. - **`nirs4all-cluster`**: public remote; documentation framed as an alpha prototype, not as a ready multi-tenant service.

What is **not** in hand today:

- A **cited "software" publication** (JOSS / SoftwareX) which anchors`nirs4all`in the literature. - A measurable **NIRS community presence** (ICNIRS presence, chemometrics mailing lists, citations). - An **effective consumption of`dag-ml`** per`nirs4all`. Today the two worlds coexist. - A **public benchmark** (the arena) with method × scenario comparison matrix and cross-results.

---

## 4. Critique objective

### 4.1 Scope vs. maintenance capacity — recalibrated by the automation bet

15 repositories (planned included), each with "lots of bindings + idiomatic bindings" — if we take`nirs4all-methods`as a reference (4 active bindings + Julia/JNI/Android/Native JS planned) and multiply by the 4 other technical libraries (`nirs4all-formats`,`nirs4all-io`,`dag-ml`,`dag-ml-data`), it's a Cartesian product of **~25-30 binding targets × project**, plus the application layer. Under a classic artisanal maintenance model, **this does not hold**.

The ecosystem makes a structural bet that changes the equation: **systematic automation by AI agents (Claude Code, Codex, etc.) on the front-line processing of tickets, PRs, issues, requests, routine releases, dependency updates, generation of changelogs and cross-repo migrations**. Details in §7.6.

What changes with this bet: - The marginal cost of an additional deposit drops sharply on the *routine operations* side (triage, dependabot-like, doc updates, release notes, first level PR review). - The boundary discipline already in place (CLAUDE.md / AGENTS.md by repository, parsers in Rust only, backend never reimplements, bindings without digital logic, core dag-ml does not touch matrices) is *exactly* the breeding ground that agents need to operate under supervision and executable gates. *Not a substitute for review;* SWE-bench and the Claude Code documentation remind us that agents remain fallible in real software engineering and recommend review + tests + isolation. - Grouped`release trains`and public *deprecation* of unused bindings become agent-driven routines themselves.

What does not change: - Architectural decisions, scientific framing, licensing choices, response to a security incident, drafting of papers, product arbitration, industrial contact remain human. - The cost of *qualified* review of changes generated by agent remains human and increases with volume. - An explicit prioritization of bindings by community ROI remains necessary — automation does not invent the strategy.

The bet is therefore defensible, but conditional on: 1. continued investment in CLAUDE.md / AGENTS.md / validation scripts by deposit (the fuel of agents),
2. a policy of *systematic* human review of changes produced by agent before merge on`main`,
3. a claims discipline (see §7.5 decision 6) — agents must not reintroduce corrected over-claims in this pass.

### 4.2`dag-ml`in a crowded market

The idea of ​​positioning`dag-ml`as a “computing/ML” publication is ambitious but the market is dense: MLflow, DVC, OpenLineage, MLMD, Hamilton, Metaflow, Flyte, Kedro, ZenML, Pachyderm, Sacred, Hopsworks, RO-Crate, W3C PROV. The`dag-ml`differentiator must be **explicit and defensible**:

- **OOF-safety verifiable mechanically** rather than by convention. - **Cross-language by C ABI** at the core, where most competitors are Python-centric. - **Default refutation of escape paths** (train predictions as training features), explicit opt-in and traced otherwise.

For a paper to pass, you need an *empirical bench*: run`dag-ml`on N real pipelines (NIRS + others) and show that it catches leaks that MLflow / DVC / Hamilton do not see, or that it replays at lower cost. Without this benchmark, no paper. And the plausible outcome is **MLOSS / JMLR open-source track**, or an ML workshop (e.g. NeurIPS *ML4PS*), not OSDI/EuroSys which would require a heavy systems evaluation not envisaged.

### 4.3`nirs4all-lite`: the low-level package chain packaged for multiple ecosystems

`nirs4all-lite`is the **end user product** that distributes the low-level ecosystem chain —`nirs4all-formats`,`nirs4all-io`,`nirs4all-methods`(`libn4m`),`dag-ml`,`dag-ml-data`— in an installable form in the target scientific ecosystems: **Lightweight Python (PyPI`nirs4all-lite`), R (CRAN/R-universe`nirs4all`), MATLAB / Octave (FileExchange,`.mltbx`), Julia (`Pkg`), JavaScript / WASM (npm`nirs4all`), C / C++ (vcpkg / Conan / Homebrew / .deb / .rpm), Conda channel multi-language, Docker images**.

What`nirs4all-lite`*is not*: - not a rewrite of the Python code; - not a subset of the source code; - not a fork.

What it *is*: a **distribution and release packaging** repository, zero new digital code. A`nirs4all-lite`release = an immutable bundle that pins specific versions of upstream libs and exposes them in one product per target language.

#### “lite” is capability semantics, not codebase

Without the complete Python library`nirs4all`, we lose`sklearn`/`PyTorch`/`TensorFlow`/`JAX`. Even the Python`nirs4all-lite`binding therefore deliberately remains more restricted on the ML side: reading of spectroscopic formats, assembly of datasets, PLS and variants (libn4m), reproducible DAG coordination. It's *lite* by capability, not by code. To be kept at the front of the README to avoid any misunderstanding.

#### Pour qui

- **Python** users who want the low-level stack without the ML/visu/DL armada of`nirs4all`:`pip install nirs4all-lite`. - **R chemometrics** community (prospectr / mdatools / pls / hyperSpec / ChemoSpec):`install.packages("nirs4all")`consumes a single release. - **MATLAB** users who want to leave PLS_Toolbox: packaged`.mltbx`toolbox. - Online **WASM** demos (nirs4all.org page) with`nirs4all-formats`+ PLS on the client side. - **C / C++** integrators (pharma PAT, industrial): C ABI headers + libs linked via`vcpkg`/`Conan`/`Homebrew`. - **Julia**, **Octave**, OS packaging (`.deb`,`.rpm`) to be instructed next.

#### Previous OSS of the distribution / feedstock model

The pattern exists and is mature: **conda-forge feedstocks** (recipes + CI + validation + upload, human PRs + automation), **Homebrew taps** (external formulas), **NixOS nixpkgs**, **vcpkg / Conan ports**, **ROS metapackages**, **CRAN third-party feedstocks** (rstanarm / cmdstanr packaging).

#### Hygiene (to be written at the start)

- **No upstream patch** in`nirs4all-lite`. If a binding needs a fix, it goes up to PR in the source lib. This rule protects the distribution from drift. - **Semver strict + tags`v1`,`v2`**. Compat matrix published “`lite`version × upstream libs versions”. Depreciation on ≥ 2 minor releases. Breaking changes only via new major. - **Tests on rest fixtures**: a minimal test repository which consumes each`lite`bundle at each PR — otherwise it is impossible to validate that a change does not break the downstream chain. - **SBOM + provenance + supply-chain certificates** (Sigstore / SLSA / in-toto) on published bundles. **CVE rebuild policy** explicit (upstream dep vulnerable → rebuild). **Removal policy** for broken artifacts (yank from PyPI / Conda, Docker image dump). **EOL / support window** for old bundles explicit — N rolling versions, depreciation dates published. - **Compatibility matrix** documented (glibc / OpenSSL / R version / MATLAB version / OS targets). Without that, a bundle “works for me” fails for the user. - **Redistribution rights**: any binary bundle that aggregates libs with heterogeneous licenses (CeCILL, MIT, AGPL, third-party dependencies such as BLAS / Eigen) requires license verification per target. Not optional. - **Documented scope of target artifacts**: better 2-3 well-made targets (e.g. CRAN source + Conda channel + Docker images) than 10 failed targets. **Admission rule for a new target**: CODEOWNER named for this target + dedicated CI fixture + release/withdrawal policy written before the first published artifact.

#### Residual risk

`nirs4all-lite`becomes a critical centralization point on the distribution side. If a release breaks, *all downstream users* see their installation broken. Mitigation: strict semver policy + pinned tags on the upstream libs side + fixture tests + automation §7.6 (refs bumps and regen of packaging recipes are precisely adapted agent-driven tasks, see explicit mention §7.6).

> **Note** — build/release recipes for`nirs4all-lite`bundles remain in`nirs4all-lite`. > If real redundancy appears in the upstream repositories, it must be factored out in small amounts
> documented bricks, not by a separate factory repository recreated by default.

### 4.4`nirs4all-arena`: perimeter and framing

The arena is a **curated repository of reproducible comparisons** methods × datasets × scenarios. **Not a Kaggle type competition platform**: no external submission, no runs hosted on demand, no user leaderboard, no SaaS. The compute remains internal (CIRAD or equivalent); the result is public and browsable. This avoids the costs of a multi-tenant platform (sandboxing, moderation, IP, GDPR, scaling) and remains scientifically defensible.

Two aspects to separate in communication:

1. **The reproducible scientific benchmark** — a set of qualified *scenarios* (dataset + split + metric combinations), accompanied by a method × scenario matrix executed internally and published. Each run produces an archiveable and downloadable`.n4a`bundle. Achievable at 6-12 months. 2. **The browsing website** — pages per dataset, per method, per scenario; cross-tabs; gain plots; direct link to`.n4a`; link to DOI-pinned datasets (`nirs4all-datasets`). Achievable at 12-18 months when the initial matrix is ​​stable.

Four operational points to be explained from the start (otherwise the arena is not scientifically defensible):

- **Scenario quality protocol**: inclusion criterion of a dataset (size, quality of the label, provenance), inclusion criterion of a method (referenced implementation, no hyperparameter overfit), explicit main and secondary metrics, treatment of failures (NaN, fit error, timeout) with documented codes. - **Anti-leakage split policy**: group-aware, instrument-aware, campaign-aware, temporal-aware when applicable. Documented by scenario, not implied. This is what`dag-ml`can guarantee if coupled (see §6.4 P1). - **DOI version of the datasets**: each scenario points to a DOI-pinned *version* of a dataset via`nirs4all-datasets`(and not to a moving file). A re-published dataset = a new scenario, not a silent update. - **Archiving and versioning of`.n4a`**: each cell of the matrix is ​​an immutable, content-addressable, archived`.n4a`bundle (Zenodo / Software Heritage / institutional CIRAD). Guaranteed re-execution as long as major dependencies remain compatible.

The trap to avoid: publicly promising *“Kaggle for NIRS”*. The NIRS market (≈ a few thousand active practitioners worldwide, dominated by Bruker / PerkinElmer / ABB / Foss / Metrohm) does not support a dedicated SaaS, and the scope/maintenance drift would be massive (see R2). The arena derives its value from the **quality of curation** (clean datasets, defensive splits, representative methods, transparent metrics), not from the volume of submissions.

### 4.5 The bindings matrix: prioritize by community, not by symmetry

Today the reflex is “all deposit → all bindings”. The reality of the NIRS and ML communities:

- **R**: the active chemometric community (mdatools, prospectr, pls, ChemoSpec) is R-first. **Priority 1.** A polished R suite (`nirs4all-methods`+ native player + optional studio) opens the ICNIRS and CRAN doors. - **MATLAB**: remains very established in industry and senior academics (PLS_Toolbox / Eigenvector). **Priority 2.** A clean MATLAB binding allows you to capture part of the PLS_Toolbox database. - **WASM / JavaScript client-side**: enormous marketing leverage (online demo of the studio without installation) and viable for preprocessing + PLS, **not** for DL. **Priority 3 as a demonstration tool**, not as a platform. - **Julia / JNI / Android**: niches. Bindings to be maintained only if a dedicated user pushes them. - **Octave / Python**: already covered, to stabilize not extend.

### 4.6 Licenses and industrial adoption

The ecosystem mixes **CeCILL-2.1**, **AGPL-3.0**, **MIT** (formats), **commercial dual-license** (`nirs4all-aom`). To target the industrial market (instrument vendors, pharma PAT, agtech, food QC), AGPL and CeCILL are documented obstacles. To clarify:

- Which repositories will be **free for commercial adoption without contagion** (Apache-2 / MIT / BSD)? - Which repositories maintain a **strong reciprocal** license (CeCILL / AGPL)? - Is there an explicit **commercial model** (commercial offer / support / contractual studies via CIRAD)?

A written, ecosystem-wide licensing policy is a prerequisite for industrial discussions.

### 4.7 Bus factor — to be reformulated from the automation bet

Risk must be read in two layers:

- **Operational layer (routine maintenance)**: *strongly assisted* by automation (§4.1, §7.6), mitigated under supervision and executable gates. Issue triage, first level PR review, dependency bumps, tagged releases, doc updates, changelogs, *bounded* cross-repo migrations are done via agents with mandatory human review before`main`merge. The channel only works as long as CLAUDE.md / AGENTS.md / golden gates are up to date. - **Strategic layer (decisions, vision, science, security)**: **unmitigated**. Today, a single person is responsible for the architectural choices, the scientific framing of the papers (AOM, DSL, JOSS, benchmark arena), licensing decisions, the response to a security incident, industrial contact, and long-term management. No agent covers this layer. CIRAD (Cornet, Rouan) is listed as a contributor, but without public signal from other decision-makers.

Mitigations in addition to automation:

- **Public architecture document** — release the CLAUDE.md / AGENTS.md in public form in the`docs/`of each repository, so that *external* agents can also operate if someone else takes over. - **Tests + golden gates + green CIs** by deposit as an executable contract of expected behavior — this is what allows a buyer (human or agent) to modify without breaking. - **CONTRIBUTING.md + good first results** on the 3-4 most welcoming public repositories (`nirs4all`,`nirs4all-formats`,`nirs4all-io`) to initiate human contributors beyond agents. - **Externalize CI/release** beyond the personal machine (GitHub-hosted runners, organizational secrets): if the maintainer's machine disappears, the release chain survives. - **Recruitment of a postdoc / engineer** dedicated to`nirs4all-arena`(infra side) or`dag-ml`(algorithm side) remains relevant in the medium term for the strategic layer — less priority than in the pre-automation version, but not useless.

### 4.8 The “Python without pricing” risk

`nirs4all`is becoming a very broad lib: pipelines, controllers, ML, DL, visualizations. Without a **scope freeze** strategy (what are we no longer adding to`nirs4all`and delegating to another repository?), the lib swells, the test/code ratio drops, and each redesign costs more. The rule “methods go in`nirs4all-methods`, IO goes in`nirs4all-io`, datasets in`nirs4all-datasets`” is the right one — it still needs to be applied retroactively (audit of what is in`nirs4all/operators/`and which could be migrated).

---

## 5. The heart: what is distinctive and defensible

Five differentiating elements. The claims below are *to be demonstrated comparatively* in the papers, not to be presented as acquired.

### 5.1 Pipeline DSL

`nirs4all`'s pipeline API (`_or_`,`_grid_`,`_cartesian_`,`_zip_`,`_chain_`,`_sample_`,`branch`/`merge`with strategies, separate`tag`/`exclude`,`concat_transform`,`rep_to_sources`/`rep_to_pp`,`finetune_params`coupled with Optuna) is **densely expressive** for the NIRS/chemometrics domain.

To my knowledge, no open-source NIRS tool combines this particular set (flat DSL in Python dict, automatic OOF-safe execution, reproducible`.n4a`export bundle, native sklearn + DL + SHAP integration). Individual building blocks exist elsewhere — Kedro, Hamilton, MLflow, mlr3 / tidymodels on the generic ML side; Orange-Spectroscopy / Quasar, SpectroChemPy on the spectro side. The contribution is the **combination** applied to NIRS, not each part in isolation.

To be published as a *systems / software* paper — not before having a documented comparative matrix vs. Pinard, SpectroChemPy, Orange-Spectroscopy and at least one equivalent Kedro/Hamilton workflow.

### 5.2 La famille AOM / POP

AOM-PLS / POP-PLS / AOM-Ridge / FastAOM constitute the clearest methodological contribution to the ecosystem. Main result (AOM-Ridge Blender vs Ridge-default, RMSEP median ratio 0.918 on N_cap=32, 27/32 wins, Wilcoxon Holm-corrected p = 2.6e-04) solid; AOM-PLS vs PLS-HPO runtime (1.6 s vs 710 s on the same N=32) very readable. The arXiv v2 bundle is ready and the repo public.

For Talanta, recent benchmark audit (May 28): the necessary calculation already exists almost entirely. The`nirs4all-lab/benchmark_master_results.csv`CSV master (35,930 lines) covers AOM-PLS, AOM-Ridge, PLS / Ridge tuned baselines, HPO TabPFN-guided, TabPFN, CatBoost, NICON/CNN, multi-kernel, MoE, POP-PLS, FCK-PLS. Blender + AutoSelect seeds 0/1/2 on 26 unique datasets (deduplicated union of`da001_audit20_seeds012`+`da001_partial_fast12_seeds012`), with identical RMSEP between seeds — caveat: the SPXY3 split is deterministic by protocol, therefore “zero seed-variance” to be reformulated as *protocol determinism* + multi-seed audit on N=26 rather than *“headline survives seeds”*. The strong conventional baseline (SNV + SG + baseline + OSC + components under HPO) is in`pls-tabpfn-hpo-25trials`× seeds 0/1/2 — to be presented as “strong conventional preprocessing search under HPO”, not as a fixed recipe. Remains (≈ 2-3 human days, ≈ 0 compute, or + 6 datasets to reach strict N_cap=32 in multi-seed):`final_stats.md`re-aggregation + supplement, failure-modes paragraph, missingness audit in table, citations SPORT / PORTO / PROSAC + Cawley-Talbot / Varma-Simon / Bergstra-Bengio, reflow Figure 5, clarification of the PLS-HPO search space in the text, smoke test repo. Consistent appearance: Talanta; Chemometrics & ILS remains possible for a pure methodological framework.

### 5.3 Boundary discipline

Five hard, written, verified borders:

- parsers only in Rust (`nirs4all-formats`),
- backend does not touch the lib (`nirs4all-studio`),
- bindings without digital logic (`nirs4all-methods`),
- core`dag-ml`never sees the matrices,
-`dag-ml-data`does not carry ML logic.

This discipline is not new in scientific open-source (NumPy/SciPy, Arrow/Parquet, PyTorch/XLA are organized around similar boundaries). What is **differentiating on the scale of an NIRS / chemometrics ecosystem**: the combination of these five boundaries, written, and maintained by the CLAUDE.md/CONTRIBUTING.md of each repo. This is an argument for multi-language support, not a CS novelty.

### 5.4 NIRS operator coverage

The catalog (`operators/transforms`,`operators/models`,`operators/splitters`,`operators/augmentation`,`operators/filters`) covers a rare range *in Python*, especially on the physically based augmentation side (PathLength, BatchEffect, InstrumentalBroadening, DeadBand, ScatterSimulationMSC, Spline-X/Y disturbances). A comparative matrix remains to be produced vs`prospectr`(R, sample selection + preprocessing),`mdatools`(R, PLS/SIMCA diagnostics),`SpectroChemPy`(Python, IO + preprocessing + analysis),`pls`/`hyperSpec`/`ChemoSpec`(R), Orange-Spectroscopy / Quasar (UI + workflow). Without this matrix, the “upper cover” claim is not tenable. *With* this matrix, a dedicated paper on physically based NIRS augmentation is writeable on its own.

### 5.5 Le studio

`nirs4all-studio`is not the first open-source studio for spectroscopy: Orange-Spectroscopy / Quasar exists, with an installed community and a visual workflow editor. What`nirs4all-studio`adds: NIRS-first pipeline-reproducible orientation, drag-and-drop editor plugged into`nirs4all`DSL, and native`.n4a`export. The wording to be carried publicly is *a reproducible pipeline-oriented NIRS-first studio*, not *the studio that PLS_Toolbox was missing*. It is a lever for rapid adoption for the non-Python applied NIRS community (field lab, agronomists, quality engineers), provided you invest in the documentation, video tutorials and concrete examples.

### 5.6 Le pari Rust + C ABI portable

`nirs4all-methods`(`libn4m`) reaches a rare point: a portable C++17 PLS / NIRS core + stable ABI C + 4 verified build bindings (Python wheel, R CRAN-ready, Octave MEX, JS-WASM) with digital parity publicly documented at`< 1e-12`. This is the basis which makes the R / MATLAB / WASM porting ambitions credible — provided that the discrepancies between the internal note “100% reconciled” and the public docs (catalog 427/669, guessed 419, unmapped 662) are clarified in the repo before any external communication.

---

## 6. Opportunities to aim for

Prioritized list. The items are noted **(P1/P2/P3)** by priority and **(0-6m / 6-12m / 12-24m)** by horizon.

### 6.1 Publications

| # | Cible | Horizon | Prerequisites and conditions |
|---|---|---|---|
| **P1** | **JOSS paper `nirs4all`** | 6-12m | JOSS submission is not done cold: Zenodo/DOI archive, *statement of need*, alternatives discussed (at least prospectr, mdatools, SpectroChemPy, Orange-Spectroscopy, Pinard), tests + green CI + coverage, *contribution guidelines*, *example gallery*, stable release (≥ 1.0.0). Otherwise, the JOSS reviewer requests corrections. The writing is light but the repo upgrade is non-trivial. |
| **P1** | **Papier AOM-PLS / POP-PLS** | 1-3m | arXiv v2 uploadable as-is. For Talanta: ~2-3 human days of writing + aggregation, ~0 compute. The missing experiences cited by the review (Blender/AutoSelect seeds 1/2, conventional baseline SNV+SG+OSC+tuned components) **already exist**; it remains to aggregate the archived`da001_*_seeds012`workspaces in`final_stats.md`, promote missingness + failure-modes in supplement tables, add SPORT/PORTO/PROSAC + Cawley-Talbot + Bergstra-Bengio + Varma-Simon, reflow Figure 5, explain the PLS-HPO search space in the text, and a smoke test repo. Coming Talanta. |
| **P1** | **`nirs4all-org`update** (not a paper, but preliminary) | 0-3m | Align the versions displayed (0.8.8 → 0.9.x), correct the gallery, add *statement of need* and package links. Conditions the credibility of any advertisement cited. |
| **P2** | Paper formats / IO (`nirs4all-formats`+`nirs4all-io`) to JOSS or SoftwareX | 12-18m | Conditioned on clean public fixtures + documented conformance matrix + comparison vs`spc-spectra`,`jcamp`,`brukeropus`,`spectrolab`. SoftwareX has a significant APC, to be arbitrated against free JOSS. |
| **P2** | DSL pipeline paper (Chemometrics & ILS or SoftwareX) | 12-18m | To be released **after** 1.0 of`nirs4all`and **after** at least one documented comparative benchmark vs Kedro/Hamilton/MLflow on ≥ 3 workflows. Otherwise the “DSL differentiating” claim is unproven. |
| **P2** | `dag-ml`paper to MLOSS/JMLR | 12-18m | Not OSDI/EuroSys (heavy systems evaluation not envisaged). MLOSS / JMLR open-source ML track is the right lane. **Conditioned to: (a)`dag-ml`backend actually consumed by`nirs4all`, (b) empirical benchmarking on ≥ 5 pipelines with ≥ 2 competitors (MLflow, DVC, Hamilton or Metaflow), (c) concrete demonstration of leak cases/leaks caught.** Without (a)(b)(c), no paper. |
| **P2** | Physically based NIRS augmentation paper | 12-18m | Can be written alone once the comparative matrix has been produced (see 5.4). |
| **P3** | Benchmark `nirs4all-arena` (Scientific Data en *data descriptor*, ou Chemometrics & ILS) | 18-24m | To be released when we have 5-10 datasets × 20+ pipelines with documented group/instrument/campaign splits, archived`.n4a`bundles (Zenodo / Software Heritage), DOI-pinned datasets via`nirs4all-datasets`. Variant of high interest: **benchmark cross-instrument / calibration transfer** — compare DiPLS, PDS, deep DA, conformal on pairs of documented instruments; well aligned with plant phenotyping CIRAD. |
| **P3** | Calibration transfer paper (DiPLS + extensions modernes : DANN, MMD, conformal) | 18-24m | Promising domain; to be coupled with a real multi-instrument dataset (CIRAD?). |
| **P3** | Foundation model NIRS (`NIRS-FM`pre-trained on public corpus, extends ViTnirs) | 18-30m | High visibility if submitted to a NeurIPS/ICLR spectroscopy applications workshop. Conditioned on a net pre-train corpus (≥ 100k aggregated public spectra). |

### 6.2 Standards and community

- **(P1, 0-6m)** R-side reconciliation: offer`nirs4all-formats`as a reader backend for`prospectr`/`mdatools`/`hyperSpec`packages (targeted PRs + emails to maintainers). This is the most active and accessible NIRS community. - **(P1, 6-12m)** Complete ML metadata crescent on`nirs4all-datasets`— conditioned on a catalog with ≥ 5 DOI datasets + cards + manifests, **not before**. Aligns CIRAD with MLCommons / Google open-data. - **(P1, 6-12m)** Attendance **ICNIRS 2027** (poster + talk + studio demo). The calendar is preparing for 12 months. - **(P2, 6-12m)** Presence of **Eurosense** (food sensory + NIRS) and **Pittcon / SCIX** (analytical chemistry). Direct target communities for industrial adoption. - **(P2, 6-12m)** Presence **CAC** (Chemometrics in Analytical Chemistry conference, biennial) and **IASIM** (imaging spectroscopy). CAC is the chemometrics event in the broad sense, IASIM opens the HSI door. - **(P2, 6-12m)** Nirs4all workshop / tutorial at a chemometrics summer school (CHEMOMETRICS Summer School, COTAS, *Chemometrics in Analytical Chemistry* tutorials). - **(P2, 12-18m)** Vertical community engagement: *NIR Forum* / *NIR News* (specialized journal), plant phenotyping groups (TerraRef, G2F), *Aquaphotomics* (rising school in biomedical NIRS), *PROSPECT/PROSAIL* (remote sensing vegetation). - **(P3, 12-24m)** Workshop dedicated to an ML conference (NeurIPS workshop *Machine Learning for Physical Sciences* or similar). ML side visibility tank.

### 6.3 Industrie

- **(P1, 0-6m)** Remove the **public license matrix** from the ecosystem (see critique 4.6). Prerequisite for any industrial discussion: a seller does not sign without clarity. Includes a possible double license (free CeCILL + commercial with CIRAD support). - **(P2, 6-12m)** Approach **instrument vendors** (Bruker, Foss, Metrohm, ABB, PerkinElmer, ASD/Malvern) — **conditional on**: (a) license matrix released, (b)`nirs4all`1.0 stable and published, (c)`nirs4all-org`up to date, (d) at least one releaseable. Demonstration:`nirs4all-formats`plays their native outputs + interactive studio without proprietary software. Without (a)(b)(c)(d), premature. - **(P2, 12-24m)** Vertical target **PAT pharma** (Process Analytical Technology). GxP compliance audit, run traceability, electronic signature integrity (CFR 21 Part 11). Paid market;`nirs4all`already has traceability by construction. Packaged at an identified pharmaceutical partner. - **(P3, 12-24m)** Vertical target **agronomy / breeding** (CIRAD is on site): NIRS + SNP genotype via`dag-ml-data`. CIRAD internal pilot (G2F-like, breeding NIRS) → publication (e.g. *Plant Phenomics*, *G3*) → diffusion. Good lever for interdisciplinary publication. - **(P3, 12-24m)** Vertical target **soil / agronomy NIRS** (soil measurements, field probes) and **food quality control**. Diffuse markets but numerous users.

### 6.4 Technique (R&D)

- **(P1, 0-12m)** **`dag-ml`backend consumed by`nirs4all`**: ensure that a`nirs4all`pipeline can run via`dag-ml`(opt-in mode). Without this,`dag-ml`remains a scaffold. This is the coupling item that conditions the`dag-ml`paper. - **(P1, 0-12m)** **Advanced split protocols**: beyond Kennard-Stone / SPXY already present, explain and test *group split* (samples grouped by batch / instrument / campaign), *repeated measurements* (already partially via`rep_to_*`), *instrument leakage*, *temporal leakage*. This is the first thing a chemometrics or ML methods reviewer checks. - **(P2, 6-12m)** **Spectroscopic interpretability beyond SHAP**: VIP (Variable Importance in Projection) on the PLS side, loadings and bi-plots, *stability wavelength selection* (stable variants of CARS / VIP-stable), *saliency sanity checks*, *confound detection*. This is the lingua franca of chemometrics. SHAP alone is not enough to convince the NIRS community. - **(P2, 6-12m)** **TabPFN as operator first-class** in`nirs4all`: already explored in lab. NIRS = small-data tabular = ideal ground for TabPFN v2 / v2.5. Short paper possible (NeurIPS workshop *Tabular ML*). - **(P2, 6-12m)** **Modernized calibration transfer**: extend DiPLS with deep domain adaptation (DANN, MMD), *piecewise direct standardization* (PDS), conformal prediction for calibration intervals. Promising domain. - **(P2, 12-24m)** **Hyperspectral imaging beyond NIRS**:`nirs4all-formats`already reads ENVI / AVIRIS, but the pipeline strategy must deal with *spatial CV* (ROI-aware, block-CV to avoid spatial leakage), management of cubes (H × W × λ), *region of interest* extraction, integration with image phenotyping workflows. Prerequisite for the studio's multi-modal pivot. - **(P2, 12-24m)** **Foundation model NIRS**: pre-training transform (masked spectral modeling) on ​​a large aggregated public corpus. Broadcast in`nirs4all.operators.models.NIRSTransformer`. The ViTnirs lab work is a prototype. - **(P2, 12-24m)** **Uncertainty quantification**: conformal prediction on PLS/DL predictions, Bayesian PLS, rigorous comparison. Underdeveloped area in applied NIRS, crucial for PAT and cross-instrument calibration. - **(P3, 12-24m)** **Multi-modal`dag-ml-data`** consumed by`nirs4all-studio`: HSI extension, time-series, SNP genotype. Long-term vision of the studio. Conditioned on P1 items first.

### 6.5 Communications

- **(P1, 0-3m)** **`nirs4all-org`upgrade **: align versions (0.8.8 stale → 0.9.x), correct screen gallery, add *statement of need*, direct link to packages (PyPI, CRAN, crates.io), BibTeX citation, real status of projects. Prior to any publication that points to the site. - **(P1, 0-6m)** Progressive overhaul: studio demo in GIF/video, concrete examples “10 lines of code”, dedicated pages per ecosystem project. - **(P1, 0-6m)** Launch a technical blog (`posts/`in`nirs4all-org`) with 4-6 target posts: *Why we built nirs4all*, *The pipeline DSL*, *AOM-PLS in 5 minutes*, *From OPUS file to prediction in Studio*, *Reproducible NIRS bundles*, *nirs4all-formats: reading 58 vendor formats from Rust*. Long-tail SEO visibility. - **(P2, 6-12m)** Online WebAssembly demo:`nirs4all-formats`+ basic client-side PLS, demo on nirs4all.org. Concrete demonstration of portable betting, useful for R/industry outreach. - **(P2, 6-12m)** YouTube presence / CIRAD channel: 4-5 video tutorials (15-30 min) on typical uses. - **(P3, 12-24m)** Open a forum (Discourse or GitHub Discussions) if the community grows sufficiently.

---

## 7. Strategic recommendations

### 7.1 Three axes for the next 6-12 months

The ecosystem has accumulated more code than distribution. Three axes in parallel:

1. **Consolidate what exists.** Finish stable 0.9.x, release 1.0.0 of`nirs4all`with explicit public API promises, release`nirs4all-methods`on PyPI + CRAN, release`nirs4all-formats`on PyPI + crates.io, update`nirs4all-org`. Align public claims (parity, reconciled ABI, dataset statuses) with the documented reality of the repo. 2. **Two target publications first**, not three in parallel: (a) JOSS`nirs4all`once 1.0 is released + JOSS checklist completed (see 7.2), (b) AOM-PLS once the`paper_review.md`blockers are lifted. DSL and`dag-ml`come next, conditioned on public artifacts and comparative benchmarks. 3. **`nirs4all-arena`— reproducible internal benchmark published for reading.** Choose 5 public datasets (NIRS pharma + agro + food + soil + plant phenotyping if possible), 10-15 pipelines (PLS, AOM, RF, NN, TabPFN…), group/instrument/campaign splits, method × scenario matrix generated internally, public browsing pages, downloadable`.n4a`bundles. **No external submission, no competition platform.** The *citable version* (DOIs, licenses, cards, full Croissant) is an additional level at 12-18 months.

### 7.2 Checklist JOSS minimale pour `nirs4all`

Prerequisite for any submission: - Zenodo / DOI archive of the submission tag; - *explicit statement of need* (vs`prospectr`,`mdatools`,`Pinard`,`SpectroChemPy`, Orange-Spectroscopy / Quasar); - *alternatives* discussed in the paper, not just listed; -`CONTRIBUTING.md`,`CODE_OF_CONDUCT.md`, *issue templates*, label *good first issue* populated; - Green CI on Linux + macOS + Windows, documented coverage; - *example gallery* executable (which`examples/`already provides — check that it runs on the 3 OS); - stable release tagged (≥ 1.0.0); - the Sphinx doc published at a stable URL (ReadTheDocs or GitHub Pages).

### 7.3 What to defer (and write it down)

- **`nirs4all-lite`as digital code repository/native rewrite** → **discontinued**. The repository exists as a *simplified multi-language distribution* of the low-level string (see §4.3), not as a rewrite or subset. Startup conditional on the written stability policy (strict semver, pinned tags, fixture tests, compat matrix, SBOM/CVE/redistribution). - **`nirs4all-dist`(shared factory build / scaffolding / supply-chain)** → **abandoned as active repository**. Its role is taken over by`nirs4all-lite`workflows, scripts and docs; do not reference reusable`GBeurier/nirs4all-dist`workflows. - **External submission platform / Kaggle type competition for the arena** → **abandoned**. The arena remains curated + internal compute + public browsing. Don't advertise it as a Kaggle-NIRS, even in the long term. - **Client/server/workers distributed execution** (see *Appendix — Perspective: distributed execution* at the end of the document) →`nirs4all-cluster`exists publicly as an alpha prototype, but should not be presented as a stable product or multi-tenant endpoint. Industrialization remains conditional on go/no-go criteria; a Dask opt-in spike in`nirs4all`remains the shortest route to test. - **Bindings Julia / JNI / Android** of all projects → defer until explicit user request. - **Generalized studio multi-modal** (HSI / SNP) → differ post-1.0.0`nirs4all`and post-coupling`dag-ml`.

### 7.4 What to cut or freeze

- **Additions of operators in`nirs4all/operators/`** which could live in`nirs4all-methods`or in an external plugin: audit + migration rather than addition. - **Heavy Python ML dependencies by default**: keep and harden lazy-loading, expose clear`[dl-tf]`,`[dl-torch]`,`[dl-jax]`extras. - **Any unsourced public claim**: *standard*, *better*, *equivalent to*, *no equivalent*, *changes everything* — replace with claims bounded and testable by a comparative matrix.

### 7.5 Decisions to be made explicitly (to be written in a public document)

1. **Public licensing policy** of the ecosystem (matrix by deposit × commercial use × contagion). 2. **`nirs4all-lite`**: scope of priority target artifacts (PyPI`nirs4all-lite`, CRAN/R-universe`nirs4all`, npm`nirs4all`, MATLAB/Octave zip/toolbox first, then Conda channel + Docker images + Julia Pkg + vcpkg), semver and compat matrix policy, CODEOWNERS and release frequency. 3. **`nirs4all-arena`**: target levels (a) *reproducible internal benchmark*, (b) *public browsing site*, (c) *citable resource* DOIs + cards + Croissant + versioned`.n4a`bundles, and realistic schedule for each. **No “external submission platform” level** (abandoned, see §4.4 and §7.3). 4. **Prioritization of bindings**: R = P1, MATLAB = P2, JS/WASM demo = P3, Julia/JNI/Android = on request. 5. **`dag-ml`↔`nirs4all`coupling **: which version of`nirs4all`does`dag-ml`become opt-in backend? Conditions`dag-ml`paper. 6. **Public freshness policy**: commitment to align the claims of the repo / webpage / README with the documented reality (versions, parity, ABI, datasets) before each release. 7. **Automation policy** (see §7.6): which agent perimeters *can* operate autonomously, which require systematic human review, how to audit.

### 7.6 The automation bet as a maintenance strategy

The ecosystem makes the explicit choice to automate as much as possible, using AI agents (Claude Code, Codex, etc.), the processing of **tickets, PRs, issues, requests, routine releases, dependency updates, generation of changelogs, cross-repo migrations, updating of documentation, propagation of schemas, conformance checks**. This is the bet that makes the order of magnitude of the scope (15+ deposits, multi-bindings) defensible.

#### Agent-driven scopes (autonomy + light human review)

- Sorting and categorization of incoming issues (labels, priority, target deposit). - Routine PR: dependency bumps, formatting, lint, doc strings, updating tests on symbol renaming. - Generation and updating of changelogs, release notes, BibTeX citations, SemVer versioning. - Propagation of JSON schemas/contracts between linked repositories (`dag-ml`↔`dag-ml-data`,`nirs4all-formats`↔ its bindings). - Update of CLAUDE.md / AGENTS.md /`MEMORY.md`index on structural evolution. - Small/medium scale cross-repo migrations **strictly bounded** (some cloud agents remain single-repo per session — cut the perimeter). - First level responses to issues (clarification, request for repro, doc pointing) before human escalation. - Build / parity / ABI snapshot diffs on Rust and C++ repositories — *reading* diffs; any *change* to the public ABI goes back humanly. - **`nirs4all-lite`(§4.3) — agent-driven model case**: bumps of refs to upstream libs (lock files), update of packaging recipes (Conda, Docker, R DESCRIPTION/Makevars, MATLAB toolbox), rebuild CVE triggered on supply-chain signal, regen of SBOM/attestations. The scope is *perfect* for automation because (a) zero numeric code, (b) clear boundaries between upstream configs and libs, (c) test fixtures check for non-regression at each PR.

#### Scopes that remain human (systematic qualified review, never in complete autonomy)

- Architecture decisions (boundary between repositories, public ABI, versioned schema contract). - **Breaking changes API / public ABI**: any change of public signature or versioned wire schema — valid human, agent can prepare the PR. - Scientific framing of papers (claims, denominators, statistics, baselines). - License and double licensing arbitrations. - Response to a **security incident, dependency vulnerability, secret leak**. SCA / SBOM / provenance policy read by human, not auto-merged on green signal. - **Release credentials**: PyPI tokens / CRAN / npm / crates.io / GitHub secrets / org-level organization. No agent pushes a tagged release alone. Short tokens, documented rotation, provenance of published artifacts. - **Community moderation** (GitHub Discussions, mailing list, future forums): agent-assisted technical responses OK; bans / arbitrations / conflicts = human. - Industrial contact and partnerships. - Studio product choice (UX, user priorities). - Public communication (webpage, posts, papers, talks).

#### Fuel required for the bet to stand

- **CLAUDE.md / AGENTS.md up to date** in each filing, aligned with documented reality (see §7.5 decision 6). An agent that operates on outdated documents propagates errors. - **Green tests + golden gates by deposit**: this is the enforceable contract that agents respect. Without testing, the agent doesn't know it's broken. - **Schemas + fingerprints +`scripts/validate_contracts.py`** in cross-repo contract deposits. Drift detected → agent corrects or opens an issue. - **E2E tests** (Studio in browser, golden workflows screenshots, CLI smoke tests by repository) in addition to unit tests. It’s the net that catches UX regressions that an agent doesn’t see in context. - **Dependency policy**: SCA (Software Composition Analysis), SBOM (Software Bill of Materials), provenance of artifacts. No auto-update agent on *security-critical* flagged dependency without human review. - **Agent memory/context policy**: avoid inter-session context-window pollution, isolation by task, *no carry-over* of unverified claims between PRs. - **Human review policy**: each agent-driven PR has a human reviewer responsible for the merge. **No auto-merge on`main`** — hard rule. Reviewer sub-agent required in *first pass* to pre-filter. - **Audit trail**: log agent actions in PRs and issues for traceability. Appropriate Co-Authored-By code. - **Activity dashboard**: agent/human PR ratio, merge rate, revert rate, E2E coverage score — publicly visible for quality pressure. - **CI matrix “agent-friendly”**: single command per depot (`make ci`/`cargo make ci`/`npm run ci`) that the agent executes before each PR. No implicit command chain to rebuild. - **Stable claims policy**: agents should not reintroduce over-claims corrected in this document. Reference §7.5 decision 6 in each CLAUDE.md.

#### Residual risk and warning signal

Automation is *not* a replacement for the strategic layer. The strategic bus factor (§4.7) remains high. Warning signals that automation is drifting: - Silent regressions in the doc (claims too strong, false comparisons, obsolete versions re-written). - Self-merged PRs that re-introduce dead code or compatibility shims. - Multiplication of deposits without prior human strategic clarification. - Green CI but broken end user behavior — E2E coverage hole that agents cannot detect on their own. - **MCP plugin / dependency / compromised agent chain** (agentic supply-chain) — signed provenance and SBOM required. - **Progressive expansion of agent permissions** (*privilege creep*) without documented decision. - **Context/memory pollution**: unverified claims re-introduced from one session to another, hallucination of private API or repo state that does not exist. - **PR which adds tests validating the bug instead of correcting it** — known pattern and easy to let go through quickly.

Mitigation: quarterly human review of the ecosystem's actual state + merged agent-driven PRs, claim/reality alignment, and tightening of CLAUDE.md / AGENTS.md around the areas where the agent drifted.

---

## 8. Risques majeurs

| # | Risque | Impact | Mitigation |
|---|---|---|---|
| R1 | **Strategic bus factor** (architectural decisions, scientific framing, security, partnerships, public communication) | High on the strategic layer; the operational layer is *strongly assisted, mitigated under supervision and executable gates* by the automation bet (§7.6) | Public architecture doc, CONTRIBUTING.md, tests + golden gates as an enforceable contract, outsource CI/release beyond the personal machine, postdoc/engineer recruitment for the strategic layer. *Automation does not cover this layer*. |
| R2 | **Scope explosion** (≥ 15 deposits × N target bindings) | Medium — the marginal *operational* cost of a repository is greatly reduced by §7.6; the *strategic* marginal cost (architecture review, product decisions) remains linear | Prioritization R = P1, MATLAB = P2, WASM demo = P3, rest = on request. *Release trains* grouping linked deposits (agent-driven). *Public deprecation* of unused bindings. CLAUDE.md / AGENTS.md updated as a prerequisite for betting automation. |
| R3 | **Licences incompatibles industrie** (AGPL / CeCILL) | Bred for industrial adoption | Matrice licence publique, double-licensing CIRAD-supported si pertinent. |
| R4 | **`dag-ml`remains scaffold** (never consumed by`nirs4all`in production) | Raised for ML publication | Item P1: opt-in coupling in`nirs4all`at 6-12 months. Otherwise the`dag-ml`paper will not come out. |
| R5 | **Public/private mismatch**:`nirs4all-datasets`is private,`nirs4all-lab`is private, but the “public arena” + “public benchmark” ambition depends on their openness. | Raised for community | Explicitly decide which datasets/pipelines go public, and do so before announcing a public arena. |
| R6 | **Stale public metadata** : webpage, READMEs, versions divergent (webpage 0.8.8 vs lib 0.9.1, finish-lib-progress 100% ABI vs SPEC 64% catalogued). | Average, but harms scientific and industrial credibility | Freshness policy (see 7.5 decision 6); pre-release checklist. |
| R7 | **Benchmark leakage** in the arena (single split, repeated ungrouped samples, instrument leakage, temporal leakage). | Scientifically raised (published rejected or retracted) | Group/instrument/campaign splits from day 1; document the strategy. This is precisely what`dag-ml`can guarantee. |
| R8 | **`nirs4all-arena`announced as a submission / competition platform ** while the scope is curated + internal compute + public browsing | Medium, reputational and scope | Framing §4.4 explicit; public communication limited to *curated reproducible benchmark* and *browsing site*, never *external submission* nor *competition*. |
| R9 | **R competition** (mdatools, prospectr, hyperSpec, ChemoSpec) which adopts these ideas before us | Moyen | Sortir vite JOSS + outreach R-side (PRs, atelier ICNIRS, posts blog). |
| R10 | **Established tools** (PLS_Toolbox, Unscrambler, SIMCA, Quasar/Orange-Spectroscopy) ignore open-source or reinforce themselves | Moyen | Network effect via *instrument vendors*, trained students, CIRAD plant phenotyping. Long term. |
| R11 | **Electron studio extra cost** vs pure web | Moyen | Maintain standalone web mode; Electron as an optional distribution. |
| R12 | **AOM submitted Talanta prematurely** (without aggregating multi-seeds already calculated + without citations + without failure-modes paragraph) | Scientifically raised | ~2-3 human days of writing + aggregation on existing data (see revised header`paper/review/paper_review.md`). Do not submit without this pass. |
| R13 | **Sloppy distributed execution** — either`nirs4all-cluster`leaves its role as an alpha prototype without a security framework, or a Dask prototype is deployed without an mTLS/secrets/workspaces/quotas isolation model. Risk even if the browsing arena site remains *read-only*: a poorly isolated worker can be exploited | Very high for scope *and* for reputation (data/security incidents) | Keep`nirs4all-cluster`public but explicitly prototype. Do not make it a multi-tenant service. For the short term, favor Option C (Dask backend opt-in in`nirs4all`) with documented go/no-go criteria. Data + security + recovery model written before any deployment. The “public” of the arena remains a *consultation site*, never an *execution endpoint accessible to third parties*. |
| R14 | **Drift of the automation bet**: auto-merge on`main`, corrected over-affirmations re-introduced, dead code, deposits multiplied without strategic clarification, green CI but broken UX, compromised agentic supply-chain (MCP / plugin / dependency), *privilege creep* on agent permissions, context pollution / private API hallucination, PR which adds a test validating the bug | Medium-high (silent erosion of quality, or even security incident) | No`main`auto-merge (hard rule); obligatory sub-agent reviewer + responsible human reviewer (see §7.6); quarterly agent vs. human audit (dashboard); E2E tests + measured coverage; SBOM + provenance + SCA on MCP dependencies and plugins; agent permissions documented and reviewed; CLAUDE.md / AGENTS.md up to date as an operational contract; explicit referencing §7.5 decision 6 in each CLAUDE.md. |
| R15 | **`nirs4all-lite`distribution too central** — if the build/release recipes are modified without testing per target, a release breaks several cascading bindings | Medium-high for velocity and release reliability | Dedicated CI per target (Rust, Python, R, JS/WASM, MATLAB/Octave), release artifacts reconstructed for each tag, strict semver, tags pinned on the upstream libs side, CODEOWNER per target, no autonomous merge, compat matrix published. |

---

## 9. Executive summary

The nirs4all ecosystem is architecturally more advanced than its public visibility suggests. The boundaries are clean, the multi-language C ABI infrastructure is supported by four bindings, the pipeline DSL has broad expressiveness in the NIRS/chemometrics scope (to be demonstrated by comparative matrix), and the science (AOM-PLS / POP-PLS) relies on a serious statistical signal. Several claims which are still circulating in certain repositories or public pages, however, exceed the documented state: numerical parity mentioned at`1e-16`when the public doc is at`1e-12`, ABI announced 100% reconciled in internal note when the public SPEC has 427/669 cataloged,`nirs4all-datasets`qualified as *alpha* while the catalog contains a single example, webpage which displays an outdated version. Conversely, certain internal *under-claims*: the`paper_review.md`AOM (May 17) listed compute blockers (multi-seed Ridge headline, strong conventional baseline) which are in reality *already calculated* in archived workspaces; the rest for Talanta is writing + aggregation (~2-3 human days). **First job: align these claims with documented reality — not add new code.**

The main risk is no longer technical or raw maintenance, it is **dissemination, focus, consistency of claims, and keeping the automation bet**:

- **a defensible core** (DSL + AOM + Studio + Rust layer + disciplined borders) buried in not yet mature or stale repositories,
- **not enough publication / citation** vs what is already built,
- **hidden dependencies** between objectives: publishable`dag-ml`assumes that it is consumed by`nirs4all`; Publishable AOM assumes the blockers are lifted; arena assumes open datasets and curated internal compute,
- **too many parallel ambitions vs *qualified*** decision and review capacity: the automation bet (§7.6) recalibrates routine maintenance but does not absorb the strategic layer (architecture, science, security, partnerships, communication), which scales linearly with the number of deposits and remains supported by very few people.

The 2026-S2 / 2027-S1 period should be a phase of **consolidation and consistency**, *before* the diffusion phase: 1.0.0 of`nirs4all`, alignment of claims, two papers first (JOSS + AOM cleaned), arena in curated reproducible benchmark + browsing site, presence of ICNIRS 2027.`nirs4all-lite`can start in parallel as soon as a first multi-language bundle is useful (CRAN, Conda or Docker) and directly carries its build/release recipes. Multi-modal studio, exotic bindings await. The Kaggle-type external submission platform is explicitly abandoned; native Rust/C++ rewriting was never the project (see §4.3).

The defensible long-term objective is not “to write even more code”: it is **to become an open-source reference cited in applied NIRS and chemometrics**, with a clean and used infrastructure layer (`dag-ml`), publishable separately in open-source ML (MLOSS / JMLR). The two objectives serve each other, provided the claims are held.

---

## Appendix — Source-of-truth table by repository

To be kept up to date. All external communication should reflect this table, not more enthusiastic wording.

| Deposit | Version | Visibility | Release published | CI publique | Tests | Bindings actifs | Notes |
|---|---|---|---|---|---|---|---|
| `nirs4all` | 0.9.x | public | PyPI (in progress, aiming for 1.0.0) | yes (to be confirmed multi-OS) | pytest unit + integration, coverage to be documented | — (lib Python) | Stable public API announced 0.9.x, to be frozen in 1.0 |
| `nirs4all-studio` | dev | public | no release tag | partial | vitest + pytest + Playwright | — (app) | Launch via `npm run start:*` ; backend FastAPI + Electron |
| `nirs4all-formats` | crates dev | public | not yet on PyPI / crates.io | Rust CI OK; release workflow tag-triggered | cargo test + goldens + conformance | Python (PyO3), R (extendr), WASM | Conformance vs `brukeropus`, `spc-spectra`, `jcamp`, `spectrolab`, `h5py` |
| `nirs4all-io` | alpha | public | not yet on PyPI | ruff + mypy + pytest | ~200 tests, byte-vs-byte parity with`DatasetConfigs` | Python (phase 1) | Phase 2 Rust pending |
| `nirs4all-methods` | post-merge refactor | public | wheels ready, CRAN vendored build ready; not yet published | partial (R, Octave, JS-WASM in CI) | doctest`n4m_tests`+ parity by binding | Python (`nirs4all-methods`, `pls4all`), R, Octave (MEX), JS-WASM | `< 1e-12`public parity; ABI reconciliation: internal claims ≠ public documents, to be clarified |
| `dag-ml` | dev | public | no release | rust ci OK | cargo + validate_contracts | C ABI + Python ctypes smoke | No production host controller yet; not yet consumed by`nirs4all` |
| `dag-ml-data` | dev | public | no release | rust ci OK | cargo + validate_contracts cross-repo | C ABI + Python ctypes smoke | Contracts shared with`dag-ml` |
| `nirs4all-aom` | beta | public | not yet on PyPI | partial | pytest + benchmarks | Python | Paper in progress, experimental blockers to be lifted |
| `nirs4all-datasets` | dev | public | no release | partial | pytest minimal | Python | 1 example dataset, DOIs/cards/manifests not yet populated |
| `nirs4all-lab` | dev | **private** | n/a | n/a | n/a | Python | Prototyping space |
| `nirs4all-arena` | stub | public | n/a | n/a | n/a | n/a | README only |
| `nirs4all-org` | online | public | n/a | GitHub Actions deploy | n/a | n/a | Former`nirs4all-webpage`; public links aligned with`nirs4all-web`,`nirs4all-lite`and`nirs4all-cluster` |
| `nirs4all-ecosystem` | dev | public | n/a (parent submodules) | n/a | n/a | n/a | Contains no code |
| `nirs4all-cluster` | alpha/prototype | public | n/a | oui | pytest + mypy + ruff | Python | Public distributed prototype; not present as a stable service |
| `nirs4all-papers` | seed | public | n/a | n/a | n/a | n/a | Public deposit of submitted papers and reproducible bundles to be migrated by paper |
| `nirs4all-drafts` | active | private | n/a | n/a | n/a | n/a | Current drafts and submission artifacts |
| `nirs4all-lite` | dev | public | not yet published | oui | cargo fmt/clippy/test, Python build+twine, npm test/pack, R CMD build/check, Octave smoke/package | Rust, Python, R, MATLAB/Octave, JS/WASM | Thin aggregator; Green CI, upstream/pipeline parity integrations to be completed |

---

## Appendix — Perspective: distributed execution client / server / workers

> *Excluding short/medium term recommendations.* This appendix records the analysis of a planned request — not a roadmap. To be reread when concretely instructing the subject, not before. Referenced from §2 cartography, §7.3 differ, §8 R13.

Envisioned request: allow several machines to share the execution of`nirs4all`pipelines, with a central server which receives jobs/execution requests and dispatches the work to remote workers. **To be strictly defined before any investment**: this is the expansion scope class that R2 indicates.

### Four possible uses, very different constraints

1. **Lab cluster** — internal sharing on 5-10 machines in a research group. Simple security, co-located datasets. 2. **Arena in distributed internal execution** — the arena remains curated (internal computing, no external submission — cf. §4.4), but its method × dataset scenarios are numerous enough to benefit from multi-machine dispatch on the host side. Simple security (CIRAD internal network), no third-party sandboxing to manage. 3. **Multi-tenant studio** — shared backend for multiple Studio users. Adds auth, workspace isolation. 4. **Federated calculation** — interesting variant: the datasets *remain* on the original machine (organizations which cannot share their data), only the aggregated result goes back.

### What already exists

- Local parallelism via`joblib.Parallel(backend='loky')`in`PipelineOrchestrator`(`nirs4all/pipeline/execution/orchestrator.py:310`); naturally independent`_grid_`/`_cartesian_`/`_or_`/`_chain_`expansion. -`JobManager`in`nirs4all-studio`(`api/jobs/manager.py:94`): **ThreadPoolExecutor in-memory** with callbacks and WebSocket dispatch — not a durable distributed queue. The gap in multi-machine is greater than the code suggests. - Portable and reproducible`.n4a`bundle — a worker can load and run it without shared state *modulo* access to the dataset (shared store / NFS / S3), compatible Python environment (TF / Torch / JAX if required) and secret provisioning. -`dag-ml`C ABI (`dag_ml.h`) provides`invoke`+ replay + process-adapter controllers, but **no RPC remote controller for the moment** — the border is prepared, the transport remains to be written.

### Quatre options architecturales

| Option | Description | Effort | Quand |
|---|---|---|---|
| **A. Worker `nirs4all` natif minimal** | `nirs4all worker --connect <url>`registers with the extended Studio backend; the coordinator pushes`.n4a`+ dataset hash, the worker retrieves from a shared store. Built on existing FastAPI infrastructure *but* requires replacing the ThreadPoolExecutor with a real queue (Redis/RabbitMQ). | 3-6 mois, 1 personne | If the mono-org request is confirmed |
| **B. Backend `dag-ml` + host controllers RPC distants** | Assumes (i)`dag-ml`↔`nirs4all`coupling (item P1 §6.4), **(ii) add a remote transport to the vtable controller in`dag_ml.h`** (does not exist), (iii) transport provider (gRPC or similar). We then inherit the OOF-safety, lineage, replay. | 6-12 months *after* (i) + spec (ii) | Architecturally clean track, conditioned to mature dag-ml |
| **C. Adopter un orchestrateur existant en backend** | `nirs4all.run(executor=DaskExecutor(...))`or`RayExecutor(...)`. Integrated sklearn/joblib dask (`joblib.parallel_backend('dask')`is native), well suited to light lab/HPC. Ray more ML/DL/GPU/actors oriented but heavier. Celery = task queue (not scientific data locality). Temporal = durable orchestration (not a compute backend). Nextflow = batch HPC bioinfo, but imposes its own pipeline model which would clash with DSL`nirs4all`. | 1-3 mois prototype | **Test first** — Dask first |
| **D. Industrialize complete`nirs4all-cluster`** (server + worker + scheduler + UI + security + multi-tenancy) | Equivalent to recoding Celery + Prefect + minimal MLOps. | 12-24 months, team | **Avoid** unless dedicated funding — exactly the scope that R2 warns about |

### Topics to be covered from the framing stage (do not postpone)

- **Worker / server security**: mTLS, authentication, secrets, post-job cleaning. - **Sandboxing of third-party pipelines**: only applicable to uses 3 (multi-tenant studio) and 4 (inter-organization federated); not required for the arena since it remains in internal compute curate (see §4.4). If enabled: containers, restricted env, no-network, CPU/RAM/disk quotas. - **IP / GDPR datasets**: policy applicable to datasets *internal to the host organization* and to DOI-pinned`nirs4all-datasets`datasets (retention, lineage, re-executability). No management of datasets uploaded by a third party — the arena does not receive an external repository. - **Heavy Python environments compatibility** per worker: different TF / Torch / JAX workers? routing by capacity? - **Cost of transfers**: datasets and artifacts (fitted models can weigh >1 GB) — pre-positioning vs streaming. - **Idempotence and retry**: worker dies mid-job → retry on another worker without corrupting the workspace. - **Quotas and fairness**: a user does not monopolize the cluster. - **Heterogeneous scheduling**: GPU vs CPU, memory, dedicated slots.

### Use cases that justify (and those that do not justify)

**Justify**: heavy grid search / HPO (AOM × N preprocessings × seeds × datasets), pre-training *foundation model* NIRS, distributed cross-validation, nightly cron arena, federated inter-organization calculation, extensive simulation with`nirs4all-lab`.

**Do not justify**: daily user calibration (10-1000 samples, fits on a laptop), demo / tutorial, single-pipeline single-dataset.

### Recommendation (for the day the subject is instructed)

**0-12 months**: do not extend`nirs4all-cluster`beyond the public prototype. Prototype **Option C** as a priority, as a module/extra in`nirs4all`(e.g.`nirs4all[dask]`). Target *power users* lab with their own Dask cluster. Technically demonstrates and serves the internal compute of the arena (method × scenario matrix). Explicit validation criteria (see go/no-go criteria below).

**12-24 months**: conditioned on (i) validated Dask prototype, (ii) effective`dag-ml`↔`nirs4all`coupling, (iii) remote controller transport specification written and reviewed. *Then* Option B —`dag-ml`host controllers with remote RPC.

**24m+**: Option A or D only if a third-party use case emerges (e.g. need for federated multi-organization execution or community batch managed by CIRAD) *and* dedicated funding/team arrives. In no case as a Kaggle-type public submission platform.

**Never start with D.** Classic trap of “ML platform” projects.

### Go/no-go criteria for spike Dask (Option C)

The go is conditional on all these conditions: 1. ≥ 2 labs / partners explicitly request distributed execution. 2. Speedup ≥ 3× measured on a real workload (grid search AOM / HPO on ≥ 32 datasets). 3. *bit-identical or metric-identical* results (≤ 1e-10) at single-machine execution. 4. Data + security + recovery model written before the code. 5. **No new repositories** created — only a module in`nirs4all`.

Sans ces 5 conditions : no-go.

---
