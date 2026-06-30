# A13 - Core, Naming, Release Topology Report

Date: 2026-06-30T21:38:17+02:00
Agent lane: A13, L1/L3/L4 governance/release/core
Mode: read-only audit plus dedicated report update. Shared sync board was not
edited because this prompt is in multi-CLI report mode.

## Executive Summary

Recommendation: keep three concepts explicitly separated until `LOCK-GOV` is
accepted.

1. `dag-ml-core` is the Rust contract/control crate inside `dag-ml`. It is not
   the nirs4all aggregate product.
2. The temporary `nirs4all-core` clone/worktree has no public release identity.
   It must be merged back, retired, or renamed internally before any public
   `nirs4all-core` package is announced.
3. `nirs4all-lite` is the observed portable aggregate scaffold today. It may be
   the ancestor of the final aggregate, but a public `nirs4all-core` rename
   should wait for `DEC-GOV-001`, `DEC-GOV-002`, and `DEC-REL-001`.

Observed `nirs4all-lite` is a facade/registry plus a portable execution subset,
not a second implementation of parsers, dataset assembly, DAG orchestration, or
numerical kernels. `nirs4all-datasets` is intentionally optional/external by
default.

## Ground Truth Checked

- Root instructions: `/home/delete/nirs4all/AGENTS.md`.
- Target repo instructions: `nirs4all-lite/AGENTS.md`, `nirs4all-lite/CLAUDE.md`,
  `dag-ml/AGENTS.md`, `dag-ml/CLAUDE.md`.
- CodeGraph used for indexed code paths in `nirs4all-lite` and `dag-ml`.
- `nirs4all-lite`: branch `main`, HEAD `c14dcca`, clean worktree before this
  report.
- `dag-ml`: branch `main`, HEAD `f58d7bf`, clean worktree.
- `nirs4all-ecosystem`: existing planning docs are staged/added in this
  checkout; this report is the only file intentionally changed by A13.
- No `/home/delete/nirs4all/nirs4all-core` directory was present. `git worktree
  list` for `nirs4all` showed only `/home/delete/nirs4all/nirs4all` and a
  `.claude/worktrees/...` worktree, not a named `nirs4all-core` worktree.

## GOV Decision Draft

### DEC-GOV-001 - Temporary `nirs4all-core` Clone Status

Proposed decision: accepted once maintainer confirms.

Decision text:

> The current temporary `nirs4all-core` clone/worktree is an integration vehicle
> for the Python `nirs4all` cutover only. It has no independent public release
> identity, no registry package, and no durable repository lineage. It must be
> merged back, retired, or renamed to an internal integration/worktree label
> before any final aggregate product is named `nirs4all-core`.

Consequences:

- Do not publish any package named `nirs4all-core` from the temporary clone.
- Public docs may mention it only as "temporary integration clone/worktree".
- All release inventory rows should say "none / temporary" for its distribution.
- `L4` stays blocked on `DEC-GOV-002` until this is accepted.

### DEC-GOV-002 - `nirs4all-lite` to Final Core Aggregate

Proposed decision: proposed, not ready to accept until `DEC-GOV-001` and
`DEC-REL-001` land.

Decision text:

> `nirs4all-lite` remains the transition name for the current aggregate
> scaffold. The final low-level aggregate may be named `nirs4all-core`
> conceptually, but public registry names should move only after the temporary
> clone ambiguity is gone, the aggregation manifest/lock exists, and the
> conformance/capability matrix proves what is actually executable.

Recommended staged policy:

- T0 now: keep `nirs4all-lite` for Python distribution and repository docs.
- T1 after GOV/REL locks: reserve or introduce `nirs4all-core` as an alias or
  successor package, never as a fork with divergent behavior.
- T2 release promotion: final aggregate publishes from the `nirs4all-lite`
  lineage or renamed repo with compatibility aliases and deprecation notes.

### DEC-REL-001 - Aggregation Manifest and Lock

Proposed decision:

> The ecosystem release train is defined by a human-reviewed aggregation
> manifest and an exact generated lockfile. The manifest describes intended
> components, package names, optionality, capabilities, and policy. The lockfile
> pins commits, tags, package versions, schema/ABI/API digests, artifact hashes,
> SBOM/provenance references, and fixture digests for one reproducible release.

The manifest and lock should live in `nirs4all-ecosystem` or in the final core
aggregate release repo, but the release inventory should reference them as
contract artifacts.

## Current `nirs4all-lite` Public Surface

Observed package names:

| Target | Current package/distribution | Import/module | Notes |
|---|---|---|---|
| Python | `nirs4all-lite` 0.2.0 | `nirs4all_lite` | Pure Python, hard dep `PyYAML`; extras `dag-ml`, `dag-ml-data`, `formats`, `io`, `methods`, `datasets`, `all`, `everything`. |
| Rust | crate `nirs4all` 0.2.0 | `nirs4all` | Single workspace crate under `bindings/rust/nirs4all`; default features empty; `datasets` feature off by default. |
| npm/WASM | package `nirs4all` 0.2.0 | ESM `nirs4all` | Pure JS ESM facade with `.d.ts`; upstream WASM packages are optional peers. |
| R | package `nirs4all` 0.2.0 | `library(nirs4all)` | Pure R; Imports `jsonlite`, `yaml`; ecosystem packages are Suggests. |
| MATLAB/Octave | archive/namespace `nirs4all` | `+nirs4all` | Source archive, delegates portable execution to `+pls4all` MEX shims. |
| Source/SBOM | `nirs4all-lite-<version>-src.*` | n/a | Release workflow builds source tar/zip, CycloneDX SBOM, SHA256SUMS, provenance attestation. |

Python `__all__` exports:

- upstream registry/proxies: `LazyUpstream`, `Upstream`, `upstreams`,
  `available_upstreams`, `upstream_status`, `import_upstream`,
  `require_upstream`, `dag_ml`, `dag_ml_data`, `formats`, `io`, `datasets`,
  `methods`;
- pipeline contract: `PORTABLE_OPERATOR_CLASSES`, `PipelineDefinition`,
  `load_pipeline_definition`, `portable_class_names`;
- execution subset: `PortableDataset`, `parse_execution_plan`,
  `run_portable_pipeline`.

R `NAMESPACE` exports:

- `nirs4all_upstreams`, `nirs4all_require`;
- `nirs4all_load_pipeline`, `nirs4all_portable_class_names`,
  `nirs4all_parse_execution_plan`, `nirs4all_run_portable_pipeline`;
- domain accessors `formats`, `io`, `datasets`, `methods`, `dag_ml`,
  `dag_ml_data`.

npm TypeScript surface exports:

- upstream metadata/loaders: `upstreams`, `upstream`, `importUpstream`,
  `loadFormats`, `loadIo`, `loadDatasets`, `loadMethods`, `loadDagMl`,
  `loadDagMlData`, `loadPortableStack`, WASM loaders, and domain proxies;
- portable pipeline APIs: `loadPipelineDefinition`, `portableClassNames`,
  `parseExecutionPlan`, `runPortablePipeline`, `predictPortablePipeline`;
- result/data model interfaces.

Rust surface exposes:

- `UPSTREAMS` with keys `dag_ml`, `dag_ml_data`, `formats`, `io`, `datasets`,
  `methods`;
- `upstream(key)`, `PORTABLE_OPERATOR_CLASSES`,
  `load_pipeline_definition_str`, `portable_class_names`;
- portable dataset/execution types and tests for the current portable subset.

Observed portable execution subset:

- splitters: Kennard-Stone;
- preprocessing: SNV/StandardNormalVariate, Savitzky-Golay;
- model: PLSRegression;
- execution delegates to `nirs4all-methods` surfaces (`n4m`, `pls4all`) or
  corresponding host bindings. It does not own the kernels.

## Core Aggregate Scope Matrix

| Domain | Owner repo | In current lite registry | Default bundled? | Final core recommendation |
|---|---|---:|---:|---|
| DAG orchestration, phases, OOF, replay, scoring/prediction coordination | `dag-ml` / crate `dag-ml-core` | yes | yes in aggregate extra, not hard base dep in Python | Include as control core. Never call it `nirs4all-core`. |
| Data vocabulary/contracts | `dag-ml-data` | yes | yes in aggregate extra | Include as data contract dependency. |
| Vendor/scientific readers | `nirs4all-formats` | yes | yes in aggregate extra | Include as reader domain. No parsers in core. |
| Dataset assembly/materialization | `nirs4all-io` | yes | yes in aggregate extra | Include as assembly domain. No assembly logic duplicated in core. |
| Numerical kernels and portable methods | `nirs4all-methods` | yes | yes in aggregate extra | Include as methods domain. No kernels in core. |
| Reference dataset catalog | `nirs4all-datasets` | yes | no, optional/external | Keep optional by default; expose capability when installed. |
| Full Python API/controllers/oracle | `nirs4all` | no | no | Stay separate compatibility/oracle package; may consume core later. |
| Studio/Web product UI | `nirs4all-studio`, `nirs4all-web` | no | no | Consume core capabilities; not part of aggregate. |

Practical implication: `CORE-002` is not a rename-only task. Today the aggregate
mostly exposes lazy registry/proxy/loaders and a portable subset. Direct `pub
use`/hard binding, lazy dynamic loading, and optional dataset semantics need an
accepted design before calling it final core.

## Proposed Package / Install / Import Namespace Policy

Python V1:

| Role | Install name | Import name | Policy |
|---|---|---|---|
| Full Python library | `nirs4all` | `nirs4all` | Keep stable, including serialized `nirs4all.operators.*` paths. |
| Current portable aggregate | `nirs4all-lite` | `nirs4all_lite` | Keep until GOV/REL locks. |
| Future aggregate | `nirs4all-core` if accepted | `nirs4all_core` initially | Add only as alias/successor, not fork. Do not steal `nirs4all` import while full library exists. |
| Ergonomic facade | none or small package later | `n4a.*` | Optional facade only; not a replacement for compatibility paths. |
| Methods | `nirs4all-methods` | `nirs4all_methods`; compat `n4m`, `pls4all` | Public docs prefer explicit install; keep ABI/compat names. |
| Formats | `nirs4all-formats` | `nirs4all_formats` | Keep explicit. |
| IO | `nirs4all-io` | `nirs4all_io` | Keep explicit. |
| Datasets | `nirs4all-datasets` | `nirs4all_datasets` | Optional default. |
| DAG runtime | `dag-ml` | `dag_ml` | Keep separate engine identity. |
| Data contracts | `dag-ml-data` | `dag_ml_data` | Keep separate data identity. |

R V1:

| Role | Package | Policy |
|---|---|---|
| Aggregate | `nirs4all` | Current observed name; acceptable because no full R `nirs4all` exists. |
| Methods | `n4m` now; consider `nirs4allmethods` public facade | Keep `n4m` low-level compatibility. Public docs can say "nirs4all-methods". |
| Formats | `nirs4allformats` | Keep. |
| IO | `nirs4allio` | Keep. |
| Datasets | `nirs4alldatasets` | Optional/Suggests. |
| Data contracts | `dagmldata` | Keep unless a later migration justifies rename. |
| DAG runtime | no declared R binding in lite registry today | Do not document as installable until it exists. |

npm/WASM V1:

| Role | Current | Recommended public direction |
|---|---|---|
| Aggregate | `nirs4all` | Migrate/alias toward `@nirs4all/core` or explicitly document `nirs4all` as transitional JS umbrella. |
| Methods WASM | `@nirs4all/methods-wasm` | Keep scoped. |
| Datasets WASM | `@nirs4all/datasets-wasm` | Keep scoped and optional. |
| Formats/IO WASM | `nirs4all-formats-wasm`, `nirs4all-io-wasm` | Migrate toward scoped names when public registry ownership is ready. |
| dag-ml WASM | `dag-ml-wasm`, `dag-ml-data-wasm` | Keep current names or define scoped aliases consistently in manifest. |

## Aggregation Manifest Draft Fields

Suggested file: `aggregation-manifest.n4a.json`.

```json
{
  "schema_version": "n4a.aggregation-manifest/v1",
  "aggregate_id": "nirs4all-lite",
  "future_aggregate_id": "nirs4all-core",
  "release_train": "2026.06",
  "status": "proposed",
  "compatibility_policy": {
    "python_compat_namespace": "nirs4all",
    "facade_namespace": "n4a",
    "datasets_default": "optional",
    "private_repos_allowed": false
  },
  "components": [
    {
      "key": "methods",
      "repo": "GBeurier/nirs4all-methods",
      "role": "Portable C ABI PLS/NIRS numerical engine",
      "owner_boundary": "kernels",
      "default_inclusion": "aggregate-extra",
      "optional": false,
      "packages": {
        "python": {"distribution": "nirs4all-methods", "imports": ["nirs4all_methods", "n4m", "pls4all"]},
        "r": {"packages": ["n4m", "pls4all"]},
        "npm": {"packages": ["@nirs4all/methods-wasm"]}
      },
      "capabilities": ["portable_methods", "pls", "preprocessing"],
      "required_gates": ["abi_snapshot", "method_parity", "lite_pipeline_parity"]
    }
  ]
}
```

Required component fields:

- `key`, `repo`, `role`, `owner_boundary`;
- package names per ecosystem: Python distribution/imports, R package, npm,
  Rust crate, C ABI, MATLAB/Octave namespace when applicable;
- `default_inclusion`: `base`, `aggregate-extra`, `optional-extra`, or
  `external`;
- `optional`, `private`, `license_expression`;
- `capabilities` and `unsupported_policy`;
- required gates and parity fixtures;
- docs and support owner.

## Aggregation Lockfile Draft Fields

Suggested file: `aggregation-lock.n4a.lock.json`.

```json
{
  "schema_version": "n4a.aggregation-lock/v1",
  "generated_at": "2026-06-30T00:00:00Z",
  "manifest_digest": "sha256:...",
  "release_train": "2026.06",
  "components": [
    {
      "key": "dag_ml",
      "repo_url": "https://github.com/GBeurier/dag-ml",
      "git_commit": "f58d7bf...",
      "git_tag": "v0.2.1",
      "versions": {
        "rust_workspace": "0.2.1",
        "python": "0.2.1",
        "npm": "0.2.1"
      },
      "artifacts": [
        {"kind": "crate", "name": "dag-ml-core", "version": "0.2.1", "sha256": "..."}
      ],
      "contract_digests": {
        "schemas": "sha256:...",
        "c_abi_header": "sha256:...",
        "abi_snapshot": "sha256:...",
        "conformance_pack": "sha256:..."
      },
      "sbom": "sha256:...",
      "provenance": "github-attestation:..."
    }
  ]
}
```

Required lock rules:

- exact commit and tag for every public component;
- exact package version per ecosystem;
- artifact hashes for wheels, crates, npm tarballs, R tarballs, zips, source
  archives, headers/libs, schemas, fixtures and SBOMs;
- ABI/API/schema/conformance digests, especially for `dag-ml` and
  `dag-ml-data` lockstep;
- optional components still get pins when included in a release train;
- no `nirs4all-drafts` or private `nirs4all-lab` content.

## Release Artifact Inventory Diff Proposal

No direct edit was made to `/home/delete/nirs4all/RELEASE_DISTRIBUTION_INVENTORY.md`
because this lane is in report mode. Suggested changes for A0:

1. Under `nirs4all-core`, add: "Observed in current workspace: no named
   `nirs4all-core` checkout/worktree. Historical docs describe a temporary
   integration clone; it remains non-releaseable until `DEC-GOV-001`."
2. Under `nirs4all-lite`, update observed artifacts to include:
   - Python `nirs4all-lite` 0.2.0, pure Python wheel/sdist, import
     `nirs4all_lite`;
   - Rust crate `nirs4all` 0.2.0, default features empty, `datasets` off by
     default;
   - npm `nirs4all` 0.2.0, pure ESM facade, optional peer dependencies;
   - R `nirs4all` 0.2.0, pure R, `jsonlite`/`yaml` hard deps;
   - MATLAB/Octave zip;
   - source archive + CycloneDX SBOM + SHA256SUMS + provenance attestation.
3. Add a note that the Rust crate manifest is the current version source of
   truth in `nirs4all-lite`; release workflows validate tag/manifest drift.
4. Change "candidate for future `nirs4all-core` aggregate" to "candidate after
   `DEC-GOV-001`, `DEC-GOV-002`, `DEC-REL-001`; current reality is a scaffold
   plus portable subset."
5. For npm, mark `nirs4all` as current/transitional and add
   `@nirs4all/core` as the recommended public scoped target if GOV accepts the
   final aggregate rename.
6. Add aggregation manifest and aggregation lock as explicit contract artifacts
   in the `nirs4all-lite`/future-core row and in the release train inventory.

## Sync Board Handoff

Shared sync board was not edited. Suggested append-only worklog entry:

```text
2026-06-30T21:38:17+02:00 - A13 - Audited core/naming/release topology.
Findings: dag-ml-core is a Rust crate only; no current named nirs4all-core
checkout was observed; nirs4all-lite 0.2.0 exposes a registry/facade plus
portable subset across Python/Rust/npm/R/MATLAB, with datasets optional by
default. Wrote GOV draft, scope matrix, namespace policy, release inventory diff,
and manifest/lock fields in docs/agent_reports/A13_A13-core-release.md.
Tests/gates: no code tests run; read-only audit using CodeGraph and manifests.
Blockers: DEC-GOV-001, DEC-GOV-002, DEC-REL-001 remain required before L4
implementation or public nirs4all-core rename.
```

Suggested lane updates for A0:

| Lane | Suggested status | Next action |
|---|---|---|
| `L1` Governance/naming/ADR | `review` | Turn this report into `DEC-GOV-001` and `DEC-GOV-002`; ask maintainer to accept or revise. |
| `L3` Aggregation/release tooling | `review` | Turn manifest/lock fields into `DEC-REL-001` schema draft. |
| `L4` Core aggregate | `blocked` | Stay blocked until GOV/REL accepted; audit complete. |

## Tests / Gates

- CodeGraph exploration: `nirs4all-lite` public API/package surface; `dag-ml`
  `dag-ml-core` crate context.
- Direct read checks: package manifests, release workflows, release docs,
  compatibility registry, sync board, release inventory, worktree metadata.
- No implementation tests were run because no implementation code changed.

## Blockers

- `DEC-GOV-001`: temporary `nirs4all-core` clone status.
- `DEC-GOV-002`: final `nirs4all-lite` to `nirs4all-core` naming/promotion.
- `DEC-REL-001`: aggregation manifest/lockfile schema and ownership.
- `LOCK-CAP`: exact capability vocabulary still needed before UI/Web/runtime
  claims can be public.
