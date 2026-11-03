# nirs4all ecosystem snapshot — 2026-11-03 09:20 UTC

This snapshot freezes the published state at the end of the 2026-11-02/03 release batch: the Windows hotfix, the NA handling, DuckDB removal, the dual license, and version propagation. All versions below were checked against the live registries and git tags when the snapshot was taken.

**Canonical anchor:** [`GBeurier/nirs4all-ecosystem@1a8d86c2`](https://github.com/GBeurier/nirs4all-ecosystem/commit/1a8d86c20b52d247ee0ac37726e30c7e54e90af8). It pins every repository below as a submodule.

## Restore

```bash
# Whole tree at this exact state
git clone https://github.com/GBeurier/nirs4all-ecosystem.git
cd nirs4all-ecosystem
git checkout 1a8d86c20b52d247ee0ac37726e30c7e54e90af8
git submodule update --init dag-ml dag-ml-data nirs4all nirs4all-aom nirs4all-benchmarks nirs4all-cluster \
  nirs4all-cockpit nirs4all-core nirs4all-datasets nirs4all-device nirs4all-domains nirs4all-formats nirs4all-io \
  nirs4all-methods nirs4all-org nirs4all-papers nirs4all-preflight nirs4all-providers nirs4all-quality nirs4all-r \
  nirs4all-repository nirs4all-studio nirs4all-tools nirs4all-ui nirs4all-web

# One checkout in ~/nirs4all/<repo>
git -C <repo> fetch --tags origin && git -C <repo> switch --detach <tag-or-sha>

# Python environment matching Studio 0.15.9's embedded runtime
pip install "nirs4all==1.4.15" "nirs4all-core==0.4.7" "dag-ml==0.3.44" "dag-ml-data==0.2.16" \
  "nirs4all-io==0.2.14" "nirs4all-formats==0.2.14" "nirs4all-methods==1.3.13" "pls4all==1.3.13"
```

Do not initialize `nirs4all-drafts` or `nirs4all-lab`: they are private and are not part of the snapshot.

## Repositories (ecosystem pins)

| Repository | Tag / state | Commit | Commit date |
|---|---|---|---|
| nirs4all-studio | **0.15.9** (Latest) | `483566ee89f9976d17f710b6d95f42907ab436ed` | 2026-11-03 |
| nirs4all (Python SDK) | **1.4.15** | `b42c8c1cee292eb6e5ca9276e7357d0358f2b007` | 2026-11-03 |
| nirs4all-core | v0.4.7 | `1dffd9f4472551cc09ad9d99ed9d40814bd003cc` | 2026-11-03 |
| dag-ml | v0.3.44 | `01226120552529aad45e5ba60d3f6327894adc67` | 2026-11-02 |
| dag-ml-data | v0.2.16 | `eb2ad7835ca85feebf6f626d9f43f61575a1c9a9` | 2026-11-02 |
| nirs4all-io | v0.2.14 | `172a7acfcc029742f45fbcf477f55f46dc7fbafe` | 2026-11-02 |
| nirs4all-formats | v0.2.14 | `051fe9c0433160f26e8090566418dbc7546c4f96` | 2026-11-02 |
| nirs4all-methods | v1.3.14 | `6a6ba8cf5e4930953d2fc10c80748547805fc87d` | 2026-11-03 |
| nirs4all-datasets | v0.3.18 | `15fe4ce830f4985e5b628bcaf49d4106f45fa1e1` | 2026-11-03 |
| nirs4all-ui | v0.2.1 | `8bfc5f51600b59fc5cc899cd93f58da98fb2f851` | 2026-11-03 |
| nirs4all-web | v0.5.0 | `0335ef0bbd8517dbd81e7d93d12fafc97ca26d47` | 2026-11-03 |
| nirs4all-r | v0.7.4 | `9e487c487def7130c4fbffdd3c032729b1dfada7` | 2026-11-03 |
| nirs4all-preflight | v0.1.6 | `f90e9450f034758de5324d8a98c11acaa22966e9` | 2026-11-02 |
| nirs4all-domains (dcornet) | v0.1.0-alpha.17 | `133a58e77268e7f71d7daa17366c7af39c6468cd` | 2026-11-03 |
| nirs4all-benchmarks | v0.1.9 | `52d6cd03d19b8a4d1641b018831f2e5b619560aa` | 2026-11-03 |
| nirs4all-repository | v0.1.13 | `cc0b32848faa98986a5884d9dd358f64a48ec838` | 2026-11-03 |
| nirs4all-quality | v0.0.6 | `c9d6d091e9521d6dee82f286dc3da4d5936765c3` | 2026-11-03 |
| nirs4all-cluster | v0.1.5 | `8383adcfb78795866d375f3cfbec160bfb820eb0` | 2026-10-07 |
| nirs4all-tools | v0.0.8 | `ca5cc30c4f7ab748142cfe25ea6d6b3e4c983cc8` | 2026-09-30 |
| nirs4all-providers | v0.2.11 | `b2210ec717c0de0055fc8b9424b115a933efdb4e` | 2026-09-04 |
| nirs4all-device | v0.1.1 | `87bc83118b1508d5eddadcf888db646568ce58a4` | 2026-10-08 |
| nirs4all-aom | v0.10.4 + 16 (untagged) | `f96290943a504d9261f7a4e3753d041b0960fcfd` | 2026-09-02 |
| nirs4all-papers | untagged main | `a05eff7f119d5a3cdb1d6bae70148bd06ffa7063` | 2026-08-20 |
| nirs4all-org (site) | main | `89de641b463a93f41ab3755b1d2c5e6396a1cd7f` | 2026-11-03 |
| nirs4all-cockpit | main (snapshot 2026-11-03 09:13 UTC) | `ed8fef701203abb0ec20957e6271d9b0a58708cd` | 2026-11-03 |

## Registries (live values)

**PyPI**

| Package | Version |
|---|---|
| nirs4all | 1.4.15 |
| nirs4all-core | 0.4.7 |
| dag-ml | 0.3.44 |
| dag-ml-data | 0.2.16 |
| nirs4all-io | 0.2.14 |
| nirs4all-formats | 0.2.14 |
| nirs4all-methods | 1.3.14 |
| pls4all | 1.3.14 |
| nirs4all-datasets | 0.3.18 |
| nirs4all-benchmarks | 0.1.9 |
| nirs4all-repository | 0.1.13 |
| nirs4all-cluster | 0.1.5 |
| nirs4all-tools | 0.0.8 |
| nirs4all-providers | 0.2.11 |
| nirs4all-aom | 0.10.4 |

**npm**

| Package | Version |
|---|---|
| nirs4all (core WASM) | 0.4.7 |
| @nirs4all/methods | 1.3.14 |
| dag-ml-wasm | 0.3.44 |
| dag-ml-data-wasm | 0.2.16 |
| @nirs4all/io-wasm | 0.2.14 |
| @nirs4all/formats-wasm | 0.2.14 |
| @nirs4all/datasets-wasm | 0.3.18 |
| nirs4all-ui | 0.2.1 |
| @nirs4all/preflight | 0.1.6 |

**crates.io**

| Crate | Version |
|---|---|
| nirs4all (core) | 0.4.7 |
| nirs4all-io | 0.2.14 |
| nirs4all-formats | 0.2.14 |
| dag-ml | 0.3.44 |
| dag-ml-data | 0.2.16 |
| n4m | 0.4.1 |
| nirs4all-preflight | 0.1.6 (0.1.0–0.1.5 yanked) |

**R-universe (gbeurier)**

The registry [`GBeurier/gbeurier.r-universe.dev@8f72800a`](https://github.com/GBeurier/gbeurier.r-universe.dev/commit/8f72800a) points to:

| R package | Source repo | Pin | Subdir |
|---|---|---|---|
| nirs4all | nirs4all-r | `v0.7.4` | |
| dagml | dag-ml | `v0.3.44` | `bindings/r` |
| dagmldata | dag-ml-data | `bbddf63671a689a2afd51e97cb631b09db96af77` | `crates/dag-ml-data-r` |
| nirs4allio | nirs4all-io | `e67f0588b054c4d35e786306e139dfc92c9cf74b` | `bindings/r` |
| nirs4allformats | nirs4all-formats | `98d3daca831b54ba618d93ec50c8183578c4d1fd` | `bindings/r/nirs4allformats` |
| nirs4alldatasets | nirs4all-datasets | `v0.3.18` | `bindings/r/nirs4alldatasets` |
| n4m | nirs4all-methods | `main` | `bindings/r/n4m` |
| pls4all | nirs4all-methods | `v1.3.14` | `bindings/r/pls4all` |

The pins of dagmldata, nirs4allio and nirs4allformats are commits after the release tags that carry the dual-license fix in the R DESCRIPTION files.

> ✅ **Rebuilt by 2026-11-03 ~11:00 UTC:** R-universe serves nirs4all 0.7.4, nirs4allio 0.2.14, nirs4allformats 0.2.14, nirs4alldatasets 0.3.18, dagmldata 0.2.16, dagml 0.3.44, n4m 1.3.14 and pls4all 1.3.14, all `CeCILL-2.1 | AGPL (>= 3)` with build status success.

## Studio 0.15.9 — embedded runtime identity

Studio pins its scientific runtime exactly, from `build/runtime-cohort.json` at `483566ee`.

**SDK nirs4all 1.4.15**

| Field | Value |
|---|---|
| Source commit | `2ab9953ccb4b5e72f76be6cb637503622c5869cf` |
| Source tree | `026192334347bd3075e9d89fdf157793761b3fad` |
| SOURCE_DATE_EPOCH | `1793671925` |
| PyPI wheel sha256 | `1510b378be9d0afbe4a154154425ece75d0a17988b62a07a9c3ce576f00e8ef8` |
| Normalized wheel sha256 (pinned) | `27f3cefc9987b46e6850d3812bb4b5fcb651b82ec455b73d33469fb7bc43e6e0` |
| Installed manifest sha256 | `3d20a5efa05396c42663531092f077195bf37e4472a0cd2f19045897b1d8bc4a` |
| Qualification oracle sha256 | `3a497b5715280a99378f490d8e312e740dd9f489b77f1d57b855519bf5e0d315` |

**Native cohort**

| Component | Version | Source commit | Notes |
|---|---|---|---|
| core | 0.4.7 | `1dffd9f4` | |
| dag-ml | 0.3.44 | `01226120` | |
| dag-ml-data | 0.2.16 | `eb2ad783` | |
| io | 0.2.14 | `172a7acf` | |
| formats | 0.2.14 | `051fe9c0` | |
| methods | **1.3.13** | `fa8ff576` (tree `f4339ad1`) | ABI 2.20.0. The SDK was qualified on 1.3.13; 1.3.14 only adds SPDX/license headers. The Rust `n4m` crate stays 0.4.1. |

Custom user environments must satisfy `nirs4all>=1.4.15,<1.5`.

**Installers** (GitHub release `0.15.9`, each with its `.sha256`)

| Installer | sha256 prefix |
|---|---|
| `nirs4all.Studio-0.15.9-win-x64.exe` | `e1538fce…` |
| `nirs4all.Studio-0.15.9-mac-arm64.dmg` | `56a857c4…` |
| `nirs4all.Studio-0.15.9-mac-x64.dmg` | `b4a40691…` (uploaded from the build-only dispatch 41600968551) |
| `nirs4all.Studio-0.15.9-linux-amd64.deb` | `591a6773…` |

The Docker image is published by the tag release run 41600898717.

## Public sites at this point

- https://nirs4all.org: org `89de641`, shows Studio 0.15.9 and SDK 1.4.15.
- https://web.nirs4all.org: web 0.5.0; `nirs4all-web-version.json` lists core 0.4.7, dag-ml 0.3.44, dag-ml-data 0.2.16, io 0.2.14, formats 0.2.14, methods 1.3.14, datasets 0.3.18, ui 0.2.1.
- Cockpit: `data/current.json` generated 2026-11-03T09:13:01Z.

## Policies in force at this snapshot

- **Current version only.** No legacy or backward-compatibility code. DuckDB is removed from Studio. Old workspaces get a single notice pointing to the `nirs4all-tools` converter.
- **Missing values (NA).**
  - Rows are never dropped at load, preview or analysis unless the user asks.
  - Missing targets are excluded from training and scoring, and can still be predicted (dag-ml FoldSet `target_missing_sample_ids`).
  - Studio's New Experiment asks "exclude from training and predict" or "remove samples".
- **License.** Dual `CECILL-2.1 OR AGPL-3.0-or-later`, written `CeCILL-2.1 | AGPL (>= 3)` for R, unless a third-party copyleft dependency forbids it.
- **Studio training jobs.** Bounded at 24 h, and cancellable at any time.

## Known open items at this snapshot

- **Studio 0.15.9 "Show all trained models" fix** (`f8fb3258`, native chain-listing routes): it passed the automated tests but had neither a Codex review nor a manual check in the Windows app.
- **Methods licensing:**
  - `libPLS_1.95` (GPLv2 + MathWorks files) in the source archive;
  - OnPLS license file;
  - `rng_mt_r.c` provenance;
  - R tarballs lack the license texts.
- **aom:** `CITATION.cff` lacks CeCILL.
- **domains:** the commercial license file was not copied in. Methods refuses HDBSCAN and exact PCA on rank-deficient inputs.
- **Packaged Studio:** Excel import (openpyxl).
- **preflight:** `0.1.0-alpha.1` is not yanked.
- **datasets:** `processing_hash` limitation.
- **nirs4all-tools:** the docs still cite 0.0.7.
- **Studio:** 2 stale binned-classifier tests. `serialize_component` drops `**kwargs` arguments.
- **benchmarks:** there is no client to upload results to a benchmark server.
- **Saved CARS steps** that use `n_pls_components` now run with the default of 10 components. This is deliberate, since there is no back-compat.
