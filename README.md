# nirs4all-ecosystem

> **This repository is not a monorepo.** It is a *minimal* parent repository which groups
> projects from the **nirs4all** ecosystem in the form of **Git submodules**.
> Each project remains an **independent repository** (history, issues, releases and
> own access rights). This repository only **references a specific commit** of
> each; it does not contain their code.

## Current owner cohort — November 2026

The active [manifest](docs/contracts/release/aggregation-manifest.n4a.json) and
[generated lock](docs/contracts/release/aggregation-lock.n4a.lock.json) select the
current seven aggregate owners. The [surface matrix](docs/contracts/release/public-v1-surface-matrix.n4a.json)
accounts for independent products; the [native ledger](docs/contracts/release/native-capability-ledger.v1.json)
limits qualification to its explicit operation, source, runtime and platform evidence.
Source declarations and parent gitlinks do not establish universal parity or publication.

Providers **0.2.12** is public from
[`93cf8381`](https://github.com/GBeurier/nirs4all-providers/commit/93cf8381de15adff54d30255da295666f8deb096),
and Papers **0.2.4** is public from
[`f587d238`](https://github.com/GBeurier/nirs4all-papers/commit/f587d238c8b6902a4caf6850d213bf1aa4e0fa11).
Their selected source references are included in this parent; this does not assert
that their current Main branches or public sites have been updated.
R is the independent `nirs4all-r` product, with its own runtime prerequisites.
Its accepted source includes the nine-script Core prerequisite correction
[`6e8412ac`](https://github.com/GBeurier/nirs4all-r/commit/6e8412ac4fcd2f353e552da972c54f4ebcf7b6bd).
R-universe source propagation and served platform checks remain separate;
no successful corrected R-universe build is claimed here.
Studio retains its historical parent reference while its Main integration is deferred;
this parent update makes no new Studio Main, GUI or release claim.

The [2026.07 profile](docs/contracts/release/history/2026.07-refactor/aggregation-lock.n4a.lock.json)
is retained as historical provenance and is not the active CI selection.

## Historical public cohort — 3 November 2026

The following records the publication state on 3 November. Its versions, source
pins and deployment descriptions are historical, not the current integration status.

Python SDK **1.4.15**, Core **0.4.7**, DAG-ML **0.3.44**, Data **0.2.16**,
Formats **0.2.14**, Methods **1.3.14**, IO **0.2.14**, Datasets **0.3.18**,
UI **0.2.1**, Web **0.5.0**, Benchmarks **0.1.9**,
Repository **0.1.13**, Cluster **0.1.5** and Tools **0.0.8** are published.
R **0.7.4** is pinned to its tag and served by R-universe.
[Studio 0.15.10](https://github.com/GBeurier/nirs4all-studio/releases/tag/0.15.10)
has public Linux, Windows, macOS ARM and macOS Intel installers and checksums.
[Preflight 0.1.6](https://github.com/GBeurier/nirs4all-preflight/releases/tag/v0.1.6)
and [Domains v0.1.0-alpha.17](https://github.com/dcornet/nirs4all-domains/releases/tag/v0.1.0-alpha.17)
join the public submodules; Domains remains an alpha prerelease.
Quality **0.0.6** was published separately and its submodule tracks the current
publication head. Providers **0.2.11** and Device **0.1.1** are also pinned to
their published release tags. The website tracks its current publication head;
the cockpit snapshot follows the completed collect and Pages deployment.
The full restorable state (every pin, registry version, Studio runtime identity and
open item) is frozen in [snapshots/ECOSYSTEM_2026-11-03.md](snapshots/ECOSYSTEM_2026-11-03.md).

The **8 October** local qualification passed **11/11 scenarios and 70 artifacts**;
the [published evidence ledger](docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json)
preserves those sources, numerical tolerances and local performance results.
Python/DAG refit predictions matched; browser predictions met their declared
tolerance. Cross-validation metrics were not asserted identical. This cohort
update preserves that historical evidence; it does not record a new scientific
qualification of the November releases.

The [common guide and Legacy Python documentation](https://gbeurier.github.io/nirs4all/)
are public. Existing Read the Docs routes redirect there; a new native RTD build
requires RTD to remove its administrative block. The
[public cockpit](https://cockpit.nirs4all.org/) tracks registry and deployment
state. Full scientific E2E and performance qualification runs locally;
hosted workflows package and verify deliveries, with short platform UI checks.

## Projects referenced

| Submodule | Tracked branch | Visibility |
| --- | --- | --- |
| `nirs4all-aom` | `main` | public |
| `dag-ml` | `main` | public |
| `dag-ml-data` | `main` | public |
| `nirs4all-benchmarks` | `main` | public |
| `nirs4all-repository` | `main` | public |
| `nirs4all` | `main` | public |
| `nirs4all-studio` | `main` | public |
| `nirs4all-web` | `main` | public client-side-only browser/WASM app |
| `nirs4all-quality` | `main` | public client-side-only NIRS lab quality app |
| `nirs4all-device` | `main` | public phone/tablet spectrometer workbench |
| `nirs4all-core` | `main` | public portable aggregate owner |
| `nirs4all-r` | `main` | public independent R product |
| `nirs4all-providers` | `main` | public provider/client contracts and Python client |
| `nirs4all-tools` | `main` | public migration/conversion tools |
| `nirs4all-ui` | `main` | public shared Studio/Web React components |
| `nirs4all-cockpit` | `main` | public release/status cockpit |
| `nirs4all-org` | `main` | public |
| `nirs4all-papers` | `main` | public |
| `nirs4all-preflight` | `main` | public preflight checks |
| `nirs4all-domains` | `main` | public domain packages (alpha; dcornet) |
| `nirs4all-formats` | `main` | public |
| `nirs4all-io` | `main` | public |
| `nirs4all-methods` | `main` | public |
| `nirs4all-datasets` | `main` | public |
| `nirs4all-cluster` | `main` | public |

> **`nirs4all-formats`vs`nirs4all-io`.** Reading responsibilities of
> files and assembly of datasets have been separated: > - **`nirs4all-formats`** (formerly`nirs4all-io`): Rust library of
> *readers* of spectroscopic files (read only, ~45 formats). > - **`nirs4all-io`** (new): *assembly bridge* of datasets
> (resolution → inference → configuration → materialization). Python in phase 1
> (`SpectroDataset`compatible), Rust in phase 2 (`dag-ml-data`compatible). > It consumes`nirs4all-formats`for reading files.

## Release topology notes

- Core is the portable aggregate owner; end-user R lives in `nirs4all-r`.
- The active aggregation lock is narrower than the product matrix. CI materializes
  its exact commits and validates the manifest/lock, surface matrix and evidence-bound
  native ledger. Parent source gitlinks do not replace that selected-member gate.
- Runtime dependency artifacts follow the selected owners' manifests and exact pins;
  a newer source gitlink does not silently upgrade a consumed artifact. See the
  [distribution note](docs/RELEASE_DISTRIBUTION_MATRIX.md) for scope and checks.
- `nirs4all-web` is the **client-side-only** browser/WASM product surface. Its release surface must not imply a Python server or Python parity proof by itself.
- `nirs4all-quality` is a **client-side-only** browser/WASM quality workflow surface built from the same core/UI direction; it is tracked publicly because the cockpit links and monitors it.
- `nirs4all-device` is a **phone/tablet spectrometer workbench** surface. The cockpit tracks its public Pages app and GitHub Android debug APK; these do not claim production-store delivery or hardware validation.
- `nirs4all-ui` is a shared React component and pure TypeScript view-model package consumed by product surfaces such as Studio/Web. It is accounted for as a public release surface outside the aggregation lock, not as a backend, parser, persistence, ML, or parity-proof surface.
- `nirs4all-providers` is a separately published Python client (`GBeurier/nirs4all-providers`), but the canonical provider surface for core/R/WASM/native consumers remains the neutral contracts under `docs/contracts/providers/`.
- `nirs4all-org` and `nirs4all-cockpit` are publication surfaces outside the aggregation lock. They should be accounted for as public release surfaces, not as aggregate-core lock members.
- Required scientific checks report actual failures and skips. R product qualification follows `nirs4all-r` and its declared native prerequisites; a missing R runtime is not green evidence. Package and source accounting do not qualify an operation.

## Cloner

Full clone (parent + submodule contents):

```bash
git clone --recurse-submodules git@github.com:GBeurier/nirs4all-ecosystem.git
```

Initialize the submodules after a simple clone:

```bash
git submodule update --init --recursive
```

### Partial pull

This parent repository references only public submodules. To initialize a subset
of the ecosystem, target the desired paths:

```bash
git submodule update --init nirs4all nirs4all-formats nirs4all-io   # exemple
```

## To update

Bring all submodules to the last commit of their tracked branch:

```bash
git submodule update --remote --merge
```

Global status of all submodules:

```bash
git submodule foreach 'git status --short'
```

## Freeze state

After a`git submodule update --remote --merge`, the submodule pointers have
moved locally but **are not fixed**. To freeze the state in the repository
parent, you must **commit the pointers**:

```bash
git add .
git commit -m "Update submodule pointers"
git push
```

## Script

```bash
./pull-all.sh   # updates the parent, (re)initializes, then synchronizes the submodules
```

## License

`nirs4all-ecosystem` is a meta-repository of git submodules: **each submodule carries its own license**
(see that project). This repository's own glue (README, scripts, CI) is dual-licensed open-source —
**`CeCILL-2.1 OR AGPL-3.0-or-later`** — with an optional **commercial license** (for any commercial use,
contact <nirs4all-admin@cirad.fr>). See [`LICENSING.md`](LICENSING.md) and [`LICENSES/`](LICENSES/).
