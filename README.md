# nirs4all-ecosystem

> **This repository is not a monorepo.** It is a *minimal* parent repository which groups
> projects from the **nirs4all** ecosystem in the form of **Git submodules**. > Each project remains an **independent repository** (history, issues, releases and
> own access rights). This repository only **references a specific commit** of
> each — it does not contain their code.

## Projects referenced

| Submodule | Tracked branch | Visibility |
| --- | --- | --- |
| `nirs4all-aom` | `main` | public |
| `dag-ml` | `main` | public |
| `dag-ml-data` | `main` | public |
| `nirs4all-arena` | `main` | public |
| `nirs4all` | `main` | public |
| `nirs4all-studio` | `master` | public |
| `nirs4all-web` | `main` | public |
| `nirs4all-lite` | `main` | public |
| `nirs4all-org` | `main` | public |
| `nirs4all-drafts` | `main` | **private** |
| `nirs4all-papers` | `main` | public |
| `nirs4all-lab` | `main` | target audience, currently private |
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

## Cloner

Full clone (parent + submodule contents):

```bash
git clone --recurse-submodules git@github.com:GBeurier/nirs4all-ecosystem.git
```

Initialize the submodules after a simple clone:

```bash
git submodule update --init --recursive
```

### Partial pull (private submodules)

`nirs4all-drafts`remains **private**. During migration,`nirs4all-lab`may
still be private on GitHub until a release audit confirms
that it contains nothing sensitive. A public repository can reference private
submodules (only the URL is exposed, not the content). Without access rights,
global init fails *for these submodules only*; the others initialize
normally. To initialize only what you can access, target the desired paths:

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
