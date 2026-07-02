# RC-F — Providers as neutral service/content contracts

**Lane:** RC-F (providers/contracts) · **Date:** 2026-07-02 · **Decision source:** `DEC-PROV-001` / `LOCK-PROV`.
**Worktrees:** `_worktrees/RC-v1-providers` (branch `rc/v1-full-refactor`) + docs in `_worktrees/RC-v1-ecosystem`.
**Builds on:** `SW6_PROV_PLUGINS_spec.md`, `IMP_L14_PROVIDERS_IMPL_PLAN.md`, `W10_PROVIDERS.md`, `W18_PROVIDERS_PHASE2.md`,
`W27_DATASET_PROVIDER_BRIDGE.md`, `WAVE_3AL_PROVIDERS_PAPERS_FACADE.md`.

## Objective

Close the RC evidence gap recorded on the control board:

> Providers must become **neutral contract clients**, not a Python-only dependency for core/language packages.

Clarify and implement the provider surface as **neutral service/content contracts** so datasets/repository
access is reachable from R and WASM by **porting schemas/manifests + a thin fetcher**, not by reusing Python
code — with explicit gates where a cross-language client does not yet exist.

## Audit of prior providers work (before editing)

- `nirs4all-providers` (from W10/W18/W27/W3AL) is a dependency-light Python package that soft-imports the four
  Python siblings and exposes `ProviderPlugin` + `Health`/`Capabilities`/`WriteAccess` + a soft-import registry.
  Verified at heads: adapters are thin, read-only, never execute, never write back; `release_gate.py` already
  guards the "serve/plan/export only" boundary. **Nothing was reverted or merged blindly.**
- The gap: the *contract* only existed as Python types. A non-Python surface (R/WASM) or `nirs4all-core` could
  only consume it by depending on the Python package — the exact anti-pattern the control board flags.
- Grounding read (read-only): real `nirs4all-datasets` `card.json` + `manifest.json` (schema 2.0), real
  `nirs4all-repository` `catalog/index.json` + `descriptor.yaml` (schema 1). Both read paths are already
  **static content artifacts + per-file SHA-256 verify** — i.e. language-neutral by construction.

## What was delivered

### 1. Canonical neutral contracts (ecosystem) — `docs/contracts/providers/`

New JSON Schemas (2020-12, authored in a portable subset: `type`/`enum`/`required`/`properties`/`items`/
`additionalProperties`/`minimum`/`minItems`, **no `$ref`/`anyOf`** so any host language can revalidate them):

- `provider_descriptor.v1.schema.json` — language-neutral `{provider_id, version, health, capabilities}` a
  client of any language emits. `executes` is always `false`; `writes` never `gated` in the read slice.
- `dataset_card.v2.schema.json` — dataset identity/metadata card (discovery surface behind `card`/`list_datasets`).
- `dataset_manifest.v2.schema.json` — per-file SHA-256 **fetch** manifest (the fetcher contract).
- `repository_index.v1.schema.json` — pipeline catalogue index (discovery + fetch).
- `pipeline_descriptor.v1.schema.json` — pipeline descriptor/card (served config).
- `README.md` — the spec: contract table, language-neutral fetch semantics, the **R/WASM story**, boundaries,
  and per-language gates.

### 2. Conformance implementation (providers package)

- `src/nirs4all_providers/contracts/` — the 5 schemas vendored **byte-identical** to the ecosystem canonical
  copies + `fixtures/` with one valid example per schema (the R/WASM porting-reference corpus).
- `src/nirs4all_providers/contracts.py` (pure stdlib): `provider_descriptor()` / `all_provider_descriptors()`
  (turn any `ProviderPlugin` into `provider_descriptor.v1`), `load_contract_schema()` / `load_contract_fixture()`,
  and a **dependency-free subset JSON-Schema validator** `iter_contract_errors()` (keeps the base install
  `deps=[]` and the test suite hermetic — no `jsonschema` dep, no skips).
- `scripts/validate_contracts.py` — standalone gate (schemas well-formed, fixtures conform, live descriptors
  conform + read-slice invariants, and `--canonical <dir>` cross-repo byte-identity drift guard).
- `tests/test_contracts.py` — 20 hermetic tests.
- `__init__.py` exports the contracts API; `pyproject.toml` ships the schema/fixture data via `package-data`;
  `README.md` gains a "Neutral contracts (multi-language)" section + an explicit boundary line.

## The R and WASM story (explicit)

The read slice is static-artifact + verify, so a per-language client is small and needs **no Python**:

1. vendor the schemas (byte-identical) or trust the served artifacts;
2. discovery: GET `index.json` (repository) / read `card.json` (datasets), list/filter in-language;
3. fetch: GET each artifact by URL/DOI, **SHA-256-verify**, cache locally;
4. emit `provider_descriptor.v1` for a uniform health/capabilities surface;
5. delegate bytes→object bridging to that language's existing stack (formats/io WASM, lite aggregate), never a
   provider-owned parser.

Where a client does not yet exist the deliverable is the **contract + a gate**, never a Python shim:

| Surface | State | Gate |
|---|---|---|
| Python | implemented (conformant emitter of `provider_descriptor.v1`) | `pytest` + `scripts/validate_contracts.py` (green) |
| R | **TODO** — no provider-level catalogue/discovery client | `GATE-PROV-R` |
| JS/WASM | **TODO** — `datasets_scoped` reads bytes; no index/card discovery client | `GATE-PROV-WASM` |
| Rust / MATLAB | deferred | `GATE-PROV-NATIVE` |

## Decisions

- **D-F1** Source of truth = the contract-as-data (schemas + served static artifacts). The Python package is
  one conformant client, not the definition.
- **D-F2** Read-slice datasets/repository access is a content + fetch-manifest contract; language clients port
  schemas + a thin HTTP-GET/SHA-256 fetcher.
- **D-F3** `provider_descriptor.v1` is the neutral projection of `ProviderPlugin`; `executes=false` and
  `writes!=gated` are enforced by the gate and tests.
- **D-F4** Keep the package pure-stdlib; ship a dependency-free subset validator (hermetic tests, zero new skips).
- **D-F5** Vendored schemas are byte-identical to the ecosystem canonical copies; drift guarded by
  `validate_contracts.py --canonical` (family convention).
- **D-F6** Providers is **not** made a dependency of `nirs4all-core`/`-lite`/`dag-ml`/`nirs4all-io`; no
  cross-language shims added (stop conditions honored).

## Tests run (exact)

Providers worktree, via sibling `nirs4all/.venv` (Python 3.11.15; ruff 0.15.20, mypy 2.1.0):

- `ruff check .` → **All checks passed** (after 1 autofix: import order in the new test).
- `mypy src` → **Success: no issues found in 11 source files**.
- `PYTHONPATH=src pytest -q` → **90 passed, 4 skipped**. The 4 skips are the pre-existing optional-extra
  conformance skips (`nirs4all_datasets/repository/benchmarks/papers` not installed in this venv — real
  optional-environment skips, hard-failed by `release_gate.py` in a real release env). `test_contracts.py`
  = **20 passed, 0 skipped**, including the anchor test that validates the **real production**
  `ecostress_vegetation_all_550points/card.json` against `dataset_card.v2`.
- `PYTHONPATH=src python scripts/validate_contracts.py` → **PASS (5 schemas, 5 fixtures)**.
- `PYTHONPATH=src python scripts/validate_contracts.py --canonical …/docs/contracts/providers` → **PASS**
  (vendored ↔ canonical byte-identity).
- Packaging: setuptools egg-info `SOURCES.txt` lists all 10 contract data files → `package-data` globs resolve
  (schemas ship in the wheel; `importlib.resources` path works for installed users).

## Files

**`_worktrees/RC-v1-providers`** (normally tracked):
`src/nirs4all_providers/contracts.py` (new); `src/nirs4all_providers/contracts/{provider_descriptor.v1,
dataset_card.v2,dataset_manifest.v2,repository_index.v1,pipeline_descriptor.v1}.schema.json` (new, vendored);
`src/nirs4all_providers/contracts/fixtures/*.json` (5 new); `scripts/validate_contracts.py` (new);
`tests/test_contracts.py` (new); `src/nirs4all_providers/__init__.py`, `pyproject.toml`, `README.md` (modified).

**`_worktrees/RC-v1-ecosystem`** (`docs/` is gitignored — see integration note):
`docs/contracts/providers/{provider_descriptor.v1,dataset_card.v2,dataset_manifest.v2,repository_index.v1,
pipeline_descriptor.v1}.schema.json` + `docs/contracts/providers/README.md` (new); this report (new).

## Risks / open questions

- **Cross-language clients (R, WASM) are not implemented** — out of scope and explicitly forbidden to shim.
  Gates `GATE-PROV-R` / `GATE-PROV-WASM` / `GATE-PROV-NATIVE` filed; the neutral schemas + fixtures are the
  unblocking deliverable. The `datasets_scoped` WASM surface reads bytes but has no catalogue/discovery client.
- **Byte-identity is enforced only when the gate runs with `--canonical`.** No automated CI yet wires the two
  repos (ecosystem `docs/` is gitignored and force-added, so no watcher). Follow-up: wire `validate_contracts.py`
  into providers CI with a canonical path/submodule.
- `dataset_card.v2` intentionally constrains only stable load-bearing fields (`additionalProperties:true`
  elsewhere) so it stays robust to qualification-metric evolution; a stricter card schema would be brittle.
- No runtime/adapter behavior changed; **no Python parity/runtime implementation was edited**. No full-parity
  run is needed for this lane.

## Integration note

The ecosystem repo ignores `/docs/` (`.gitignore:9`); existing runtime schemas and agent reports (261 tracked
files under `docs/`) are **force-added**. The 6 new files under `docs/contracts/providers/` and this report must
be staged with `git add -f` when integrating, matching that convention. Per the global rule, **no commit/push
was made** in either worktree; changes are on disk and green, ready for the coordinator to review and commit.

Suggested commits (not executed):
- providers: `feat(providers): neutral provider contracts + conformance gate`
- ecosystem: `docs(contracts): freeze neutral provider service/content contracts`
