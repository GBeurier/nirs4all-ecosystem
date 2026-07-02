# Providers — neutral service/content contracts

**Lane:** RC-F (providers/contracts) · **Decision source:** `DEC-PROV-001` / `LOCK-PROV` (see `SW6_PROV_PLUGINS_spec.md`, `IMP_L14_PROVIDERS_IMPL_PLAN.md`).
**Status:** contract freeze for the read slice (datasets · repository · benchmarks · papers). Publish/upload and the benchmark runner stay deferred and gated.

## Why this exists

`nirs4all-providers` (the Python package) is **one client** of the provider surface, not the definition of
it. If core or the non-Python language packages had to *depend on that Python package* to reach datasets
or the pipeline repository, providers would be a Python-only dependency — which is impossible for R/WASM
and undesirable for `nirs4all-core`. The RC control board records this explicitly:

> Providers must become **neutral contract clients**, not a Python-only dependency for core/language packages.

So the **source of truth is the contract, expressed as data**, not code. The read slice for datasets and
repository is fundamentally a set of **static content artifacts** (an index, identity cards, per-file
fetch manifests, descriptors, recipes) served over HTTPS/DOI and verified by SHA-256. None of that
requires Python. This directory freezes those artifacts as JSON Schemas plus a provider-level descriptor
so that **every language** (Python today; R, JS/WASM, Rust, MATLAB next) implements a *conformant thin
client* over the same bytes.

## The contracts

| Schema | What it governs | Backing artifact (today) | Provider method it stands behind |
|---|---|---|---|
| `provider_descriptor.v1.schema.json` | Language-neutral `{provider_id, version, health, capabilities}` a client emits | — (emitted by the client) | `provider_id` · `version()` · `health()` · `capabilities()` |
| `dataset_card.v2.schema.json` | Dataset identity/metadata card (discovery surface) | `nirs4all-datasets` `datasets/<id>/card.json` (schema 2.0) | `DatasetProvider.card` · `list_datasets` |
| `dataset_manifest.v2.schema.json` | Per-file SHA-256 **fetch** manifest (the fetcher contract) | `nirs4all-datasets` `datasets/<id>/manifest.json` (schema 2.0) | `DatasetProvider.get_dataset` / `retrieve_dataset` (byte acquisition) |
| `repository_index.v1.schema.json` | Pipeline catalogue index (discovery + fetch) | `nirs4all-repository` `catalog/index.json` (schema 1) | `PipelineProvider.get_pipeline_list` · `list_pipelines` |
| `pipeline_descriptor.v1.schema.json` | Pipeline descriptor/card (served config) | `nirs4all-repository` `pipelines/<id>/descriptor.yaml` (schema 1) | `PipelineProvider.card` |

These schemas use a small, portable subset of JSON Schema 2020-12 (`type`, `enum`, `required`,
`properties`, `items`, `additionalProperties`, `minimum`, `minItems`) with **no `$ref`/`anyOf`** across
files, so a minimal validator can be implemented in any host language without a JSON-Schema engine.
`additionalProperties: true` is used deliberately on the heavy datasets qualification blocks so the
contract is stable against metric/profiling evolution.

### What is *not* in the read-slice contract

- **Execution.** A provider never runs ML. `capabilities.executes` is always `false`; runtime execution
  is the `rt_run_request.v1` / `rt_result.v1` surface (LOCK-RT), owned by runtime-python / cluster / WASM.
- **Ecosystem write-back / publish / upload.** `capabilities.writes` reaches at most `local-cache`
  (datasets), `local-store` (benchmark planning) or `local-output` (papers export). `gated` (admin/
  governance-gated remote write) is reserved and never emitted by the read slice.
- **Assembly.** `nirs4all-io` remains the dataset-assembly owner. `DatasetProvider.to_dataset_package`
  is a transparent pass-through to `nirs4all-io`; it is not part of this neutral read contract and stays
  gated on `LOCK-IO`.

## Fetch semantics (language-neutral)

Both read providers are **static-artifact + verify**, which is why they port cleanly:

- **Datasets:** read `card.json` (discovery) → read `manifest.json` → for each `files[]` entry resolve
  bytes (local cache → DOI → open-origin URL), stream to a pooch-style local cache, and **verify
  `sha256`** before use. `versions.content` pins bytes; `canonical_hashes`/`row_counts` validate the
  materialized canonical Parquet. Tokens are needed only for `private`/`anonymized` tiers (header, never
  logged); `public` needs none.
- **Repository:** read `index.json` (discovery, filter by `framework`/`task`/`tag`/`kind`/`trust`) → for a
  chosen pipeline fetch `descriptor` + `recipe` by `url`, **verify `sha256`**. A recipe is *served config*;
  turning it into a runnable object (`to_nirs4all` / `to_dagml`) is a separate, language-specific step.

No provider read path originates an ecosystem write, and integrity is always content-addressed.

## The R and WASM story (explicit)

**Rule:** port the **schemas + a thin fetcher** over these neutral contracts. **Do not** reuse or bind
the Python `nirs4all-providers` package, and **do not** re-implement datasets/repository logic.

A conformant per-language provider read client is small:

1. **Vendor the schemas** in this directory (byte-identical) and implement the subset validator, or trust
   the served artifacts and validate opportunistically.
2. **Discovery:** GET `index.json` (repository) / read `card.json` (datasets); list/filter in-language.
3. **Fetch:** GET each artifact by URL/DOI, `sha256`-verify, cache locally.
4. **Emit** a `provider_descriptor.v1` for health/capabilities so the surface is uniform across languages.
5. Bridging a recipe or dataset to a runnable/loadable object is delegated to that language's existing
   stack (e.g. the `nirs4all-formats`/`nirs4all-io` WASM readers, the lite aggregate), **not** to a
   provider-owned parser.

### Current coverage and gates

| Surface | Provider read client | State | Gate |
|---|---|---|---|
| Python | `nirs4all-providers` (`DatasetProvider`, `PipelineProvider`, …) | **implemented** — conformant emitter of `provider_descriptor.v1`; soft-imports the Python siblings for the rich object surface | `nirs4all-providers` `pytest` + `scripts/validate_contracts.py` |
| R | catalogue/index + card/manifest read client over these schemas | **TODO — `GATE-PROV-R`** | not yet created; R aggregate is covered by locked `lite` for *reads of bytes*, but there is **no provider-level catalogue/discovery client** in R |
| JS/WASM | catalogue/index + card/manifest read client (client-side, no server) | **TODO — `GATE-PROV-WASM`** | the `datasets_scoped` WASM surface reads dataset *bytes/formats*; a provider-level **index/card discovery** client over these schemas is not yet created |
| Rust / MATLAB | same neutral client | **TODO — `GATE-PROV-NATIVE`** | deferred |

These gates are **contract-first**: the neutral schemas + fixtures in this repo are the deliverable that
unblocks each language client. Until a language client exists, the correct action is to extend the neutral
contract and file the gate — **never** to add a Python shim or make another package depend on
`nirs4all-providers`.

## Boundaries (non-negotiable)

- **Providers is not a dependency of `nirs4all-core`, `nirs4all-lite`, `dag-ml`, or `nirs4all-io`.** The
  dependency arrow points the other way or not at all: consumers depend on the **contract** (these
  schemas / the served artifacts), and may optionally use the Python client. Core exposes provider
  clients as *separate optional surfaces*, never as controllers (`DEC-CTRL-001`).
- Each backing repo (`nirs4all-datasets`, `-repository`, `-benchmarks`, `-papers`) stays the single
  source of truth for its domain; the contract mirrors its artifacts, it does not fork them.
- `nirs4all-drafts` / `nirs4all-lab` are private and out of scope.

## Conformance & sync

- The Python package vendors byte-identical copies of these five schemas under
  `src/nirs4all_providers/contracts/` and validates them (well-formedness, fixtures, live provider
  descriptors) in `scripts/validate_contracts.py` and `tests/test_contracts.py`.
- Cross-repo the schemas MUST stay byte-identical with this directory (the family rule for shared
  contracts). The providers gate accepts a `--canonical <dir>` pointing here to assert byte-identity.
- Example instances (the R/WASM porting reference) live next to the Python copies under
  `src/nirs4all_providers/contracts/fixtures/`.
