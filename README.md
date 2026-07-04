# nirs4all-ecosystem

> **This repository is not a monorepo.** It is a *minimal* parent repository which groups
> projects from the **nirs4all** ecosystem in the form of **Git submodules**.
> Each project remains an **independent repository** (history, issues, releases and
> own access rights). This repository only **references a specific commit** of
> each; it does not contain their code.

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
| `nirs4all-core` | `main` | public canonical V1 RC portable aggregate |
| `nirs4all-providers` | `main` | public provider/client contracts and Python client |
| `nirs4all-tools` | `main` | public migration/conversion tools |
| `nirs4all-ui` | `main` | public shared Studio/Web React components |
| `nirs4all-cockpit` | `main` | public release/status cockpit |
| `nirs4all-org` | `main` | public |
| `nirs4all-papers` | `main` | public |
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

- The RC V1 aggregate release target is **`nirs4all-core`**. `nirs4all-lite` remains only as a legacy compatibility alias during the package cutover.
- The **aggregation lock is intentionally narrower than the full product matrix**. It pins the reproducible aggregate core/runtime member set; it does **not** claim to cover every product, plugin, site, or publication repo.
- For RC V1, submodule gitlinks in this parent repository are **not** the release authority. Use `docs/contracts/release/aggregation-lock.n4a.lock.json` plus each manifest `selected_workspace_path` for aggregate members, and the surface matrix / agent reports for product surfaces outside the lock.
- `nirs4all-web` is the **client-side-only** browser/WASM product surface. Its release surface must not imply a Python server or Python parity proof by itself.
- `nirs4all-ui` is a shared React component and pure TypeScript view-model package consumed by product surfaces such as Studio/Web. It is accounted for as a public release surface outside the aggregation lock, not as a backend, parser, persistence, ML, or parity-proof surface.
- `nirs4all-providers` is a separately published Python client (`GBeurier/nirs4all-providers`), but the canonical provider surface for core/R/WASM/native consumers remains the neutral contracts under `docs/contracts/providers/`.
- `nirs4all-org` and `nirs4all-cockpit` are publication surfaces outside the aggregation lock. They should be accounted for as public release surfaces, not as aggregate-core lock members.
- Skip/xfail debt remains explicit release evidence, not implied green status: the Python parity/xfail inventory stays under the cutover gates, and the lite R surface may skip locally only when R is unavailable and must still be reported as release risk.

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
