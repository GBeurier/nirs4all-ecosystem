# SW3 — LOCK-REL: Aggregation Manifest & Ecosystem Lockfile spec

**Agent:** SW3 (second wave, L3 aggregation/release tooling) · read-only audit + dedicated spec file
**Date:** 2026-06-30
**Lane:** `L3` · **Lock:** `LOCK-REL` (in_progress) · **Decision:** `DEC-REL-001` (direction accepted) · **Blocker resolved by this spec:** `B-004` (no manifest/lockfile schema yet)
**Mode:** report-only. This file is the **only** write. Sync board, roadmap, code and other reports were not touched.
**Write scope honored:** `nirs4all-ecosystem/docs/agent_reports/SW3_REL_MANIFEST_LOCKFILE_spec.md`.

**Verification method:** direct `Read`/`Bash` against local heads (CodeGraph used only as a hint). Every digest/version/field below is anchored to a file I opened. Heads per sync board pass-2 audit, re-confirmed where I touched them:

| Repo | Head (audit) | What I verified directly |
|---|---|---|
| `dag-ml` | `f58d7bf` | `abi_snapshot.v1.json` (crate `dag-ml`, `0.2.1`, header sha256), `conformance_pack.v1.json`, `parity_oracle.v1.json`, `validate_release_metadata.py`, `scripts/release/check_publish_plan.py` |
| `dag-ml-data` | `347c15f` | `abi_snapshot.v1.json` (crate `dag-ml-data`, `0.2.2`, header sha256), byte-identical pack + parity oracle |
| `nirs4all-lite` | `c14dcca` | version `0.2.0` across Py/Rust/R/npm; `version-guard.yml` (`cargo_package`); `release-source.yml` (SBOM/SHA256SUMS/Sigstore) |
| `nirs4all-methods` | `7602eb08` | `cpp/include/n4m/n4m_version.h` (project `1.0.1`, **ABI `2.0.0`**); `cpp/abi/expected_symbols_{linux,macos,windows}.txt`; `version-sync.yml`/`abi-check.yml` |
| `nirs4all-formats` | `89231b2` | workspace `0.2.1`; crates `-core/-formats/-capi/-cli`; cbindgen header `NIRS4ALL_FORMATS_H` |
| `nirs4all` | `e41362b4` | `docs/compatibility.md` **ABSENT** (confirms `B-009`) |

---

## 0. Executive summary

`LOCK-REL` defines **two files**, owned by `nirs4all-ecosystem`:

1. **`aggregation-manifest.n4a.json`** — *human-reviewed intent*. Which repos are members of a release train, their roles/boundaries, package names per language, optionality, which gates each must pass. Versions are **ranges/policy**, never exact pins. Changes by PR review.
2. **`aggregation-lock.n4a.lock.json`** — *machine-generated exact state*. One reproducible release: exact commits, tags, per-ecosystem package versions, and — the load-bearing part — **references to each member's already-produced conformance/ABI/schema digests**, plus the cross-repo lockstep attestation and release-artifact hashes.

### The one load-bearing principle (`DEC-REL-001`, sync board line 96; roadmap `REL-008`; `LOCKSTEP-004`)

> **The lock CONSUMES per-repo conformance hashes; it never re-pins them in a second, competing format.**

Every schema digest, ABI version, fixture fingerprint and parity-case id that lives in a member repo's own contract artifact (`abi_snapshot.v1.json`, `conformance_pack.v1.json`, `parity_oracle.v1.json`, `n4m_version.h`, `expected_symbols_*.txt`) is **referenced by `(producer_id, sha256)`** in the lock. CI **re-derives** each value from the checked-out commit and asserts equality. The lock is therefore a *coherence proof over existing producers*, not a new source of truth. This is exactly the constraint `CAP_spec` §C6 and A9 §4 already assumed, and it is what keeps the ecosystem from having "two formats pinning the same schema" (review DEC-10).

Consequence: when a member changes a schema, the digest changes **in that member's own pack** (the producer), the member's own `validate_contracts.py` / `validate_abi_snapshot.py` catches it, and the lock simply fails re-derivation until regenerated. No hash is ever authored by hand into the lock.

---

## 1. Verified ground truth — the substrate the lock references

The lock does not invent conformance machinery; the ecosystem already ships it per repo. The lock points at these:

| Member | Canonical version source (verified) | Conformance / ABI producer artifact(s) | Equivalence/guard validator |
|---|---|---|---|
| `dag-ml` | `Cargo.toml [workspace.package].version = 0.2.1` | `docs/contracts/conformance_pack.v1.json` (`pack_id dag-ml.shared.conformance.v1`), `parity_oracle.v1.json` (`oracle_id dag-ml.nirs4all.parity_oracle.v1`), `abi_snapshot.v1.json` (header `dag_ml.h` sha256 `96914365…`) | `validate_contracts.py`, `validate_abi_snapshot.py`, `validate_release_metadata.py`, `scripts/release/check_publish_plan.py --dry-run` |
| `dag-ml-data` | `0.2.2` (independent cadence) | byte-identical `conformance_pack.v1.json` + `parity_oracle.v1.json`; own `abi_snapshot.v1.json` (header `dag_ml_data.h` sha256 `ca5d3426…`) | same trio + cross-repo `validate_contracts.py` (sibling) |
| `nirs4all-methods` | `cpp/include/n4m/n4m_version.h`: `N4M_PROJECT_VERSION_STRING 1.0.1` | **C ABI** `N4M_ABI_VERSION 2.0.0` (`MAJOR=2 MINOR=0 PATCH=0`, `N4M_ABI_VERSION_INT`); symbol allowlists `cpp/abi/expected_symbols_{linux,macos,windows}.txt`; serialization magic `N4MM` v1 | `abi-check.yml` (symbol diff), `version-sync.yml` (`bump_version.sh --check`) |
| `nirs4all-formats` | `Cargo.toml [workspace.package].version = 0.2.1` | crates `nirs4all-formats{-core,,-capi,-cli}`; cbindgen C header guard `NIRS4ALL_FORMATS_H`; `conformance.yml` | `version-guard.yml` (`cargo_workspace`), `version-sync.yml` |
| `nirs4all-io` | per-repo manifest (`84ab189`) | `DatasetSpec v2`/`DatasetPackage` schemas (owned by `LOCK-IO`, not yet frozen) | (pending `LOCK-IO`) |
| `nirs4all-datasets` | per-repo manifest | catalog cards + checksums | (optional member; see §3) |
| `nirs4all-lite` (→ future `nirs4all-core`) | `bindings/rust/nirs4all/Cargo.toml version = 0.2.0` (the `version-guard` `VG_MANIFEST`) | portable-subset conformance fixtures; `scripts/parity/generate_python_oracle.py`; `release-source.yml` emits CycloneDX SBOM (syft) + `SHA256SUMS` + keyless Sigstore provenance | `version-guard.yml` (`cargo_package`) across Py/Rust/R/npm/MATLAB |

**Two distinct C-ABI namespaces exist and must stay separate in the lock** (do not collapse):
- `dag-ml`/`dag-ml-data` data-provider/tensor ABI — `conformance_pack.c_abi`: `data_provider_vtable_abi_version = 2`, tensor f64/f32 = 1, borrowed/owned tensor = 1.
- `nirs4all-methods` numerical C ABI — `N4M_ABI_VERSION 2.0.0` + the `n4m_*` symbol allowlist.
They are different surfaces with independent cadence; the lock records both under `members.<m>.c_abi`, never merged.

**License note (read from code, not policy memory):** every workspace manifest I opened (`dag-ml`, `nirs4all-formats`, `nirs4all-lite`) carries SPDX `CECILL-2.1 OR AGPL-3.0-or-later` (also asserted by `dag-ml/scripts/validate_release_metadata.py:22`). The lock must record the **actual** `license_expression` read from each member at its pinned commit — it must not assume a per-repo license from ecosystem notes, which can drift from the manifests.

---

## 2. Design principles (`REL-P*`)

- **`REL-P1` Manifest = intent, Lock = state.** Manifest holds policy and ranges; lock holds exact pins + derived references. A release is reproducible from `(manifest, lock)`.
- **`REL-P2` Consume, never re-pin.** Every conformance/ABI/schema/fixture value is a *reference* `(producer_id, sha256, source_path)` re-derivable from the member commit. The lock authors **zero** new authoritative digests of upstream contracts (`DEC-REL-001`, `LOCKSTEP-004`, `CAP` C6).
- **`REL-P3` Single source of truth deference.** Version comes from each repo's guarded manifest (`version-guard`/`version-sync`); ABI from `abi_snapshot.v1.json` / `n4m_version.h`; schemas from the owning repo's `conformance_pack`. The lock copies values it can re-verify, and only those.
- **`REL-P4` Lockstep pairs are atomic.** `dag-ml` + `dag-ml-data` pin together with an `equivalence_attestation` (A9 §4); a release that changes a shared contract is invalid unless the paired member is re-pinned in the same lock and the equivalence gate is green.
- **`REL-P5` Optionality is explicit and still pinned.** `default_inclusion ∈ {base, aggregate-extra, optional-extra, external}` lives in the manifest; if an optional member (e.g. `nirs4all-datasets`) is *included* in a train, the lock still pins it exactly. `datasets` defaults to `external` (`DEC-GOV-002`).
- **`REL-P6` No private content.** `nirs4all-drafts`, `nirs4all-lab`, raw `nirs4all-data` are refused by the validator (`REL-VERIFY`), never appear as members.
- **`REL-P7` Capability-aware, not capability-owning.** The lock references `parity_oracle.required_case_ids` + `conformance_pack` ids that prove portability; it stores no `portable_level` of its own (that is `CAP_spec` §3, a derived classifier). It records *which* gates were green, by id.
- **`REL-P8` Cockpit/org read, never write.** `nirs4all-cockpit` and `nirs4all-org` consume manifest+lock read-only (`REL-007`); they are not members and never regenerate the lock.

---

## 3. File A — `aggregation-manifest.n4a.json`

Human-reviewed. Declares membership + policy. **No exact pins.** (Extends the A13 draft; adds availability matrix + lockstep grouping + gate ids.)

### 3.1 Top-level fields

| Field | Type | Req | Meaning |
|---|---|---|---|
| `schema_version` | const `n4a.aggregation-manifest/v1` | ✓ | manifest schema id |
| `aggregate_id` | string | ✓ | current aggregate name (`nirs4all-lite`) |
| `future_aggregate_id` | string\|null | – | reserved successor (`nirs4all-core`), pending `DEC-GOV-002` |
| `release_train` | string | ✓ | train label, e.g. `2026.07` |
| `status` | enum `proposed\|candidate\|released\|yanked` | ✓ | train lifecycle |
| `compatibility_policy` | object | ✓ | `python_compat_namespace="nirs4all"`, `facade_namespace="n4a"`, `datasets_default="external"`, `private_repos_allowed=false`, `r_packages="explicit"` (`DEC-GOV-002`) |
| `lockstep_groups` | array<object> | ✓ | named atomic pairs/sets, e.g. `{ "id":"dagml-pair", "members":["dag-ml","dag-ml-data"], "equivalence":"validate_contracts.py" }` (`REL-P4`) |
| `components` | array<Member> | ✓ | member declarations (§3.2) |
| `cross_project_deliverables` | array | – | non-member release artifacts (parity oracle, capability matrix, SBOM index) from `RELEASE_DISTRIBUTION_INVENTORY.md` |

### 3.2 Member declaration (manifest side)

| Field | Type | Req | Meaning |
|---|---|---|---|
| `key` | string | ✓ | stable short key (`dag_ml`, `methods`, …) |
| `repo` | string | ✓ | `GBeurier/<repo>` |
| `role` | string | ✓ | one-line role |
| `owner_boundary` | enum `control\|data\|kernels\|readers\|assembly\|aggregate\|catalog\|product\|tools` | ✓ | red-line boundary (CLAUDE.md cross-cutting rules) |
| `default_inclusion` | enum `base\|aggregate-extra\|optional-extra\|external` | ✓ | `REL-P5` |
| `optional` / `private` | bool | ✓ | `private=true` ⇒ rejected by `REL-VERIFY` (`REL-P6`) |
| `packages` | object | ✓ | per-ecosystem **names** only (no versions): `python{distribution,imports[]}`, `rust{crates[]}`, `npm{packages[]}`, `r{packages[]}`, `c_abi{header}`, `matlab{namespace}` |
| `availability` | object<lang→enum `full\|subset\|inspect_only\|none`> | ✓ | declared reach per `python\|r\|wasm\|matlab\|native` (becomes the lock's measured availability matrix, §4) |
| `capabilities` | array<string> | – | references `ControllerCapability` tokens / `parity_oracle` topics (no new vocab — `LOCK-CAP`) |
| `required_gates` | array<gate_id> | ✓ | gate ids that must be green for this member (e.g. `abi_snapshot`, `validate_contracts`, `parity_oracle:python_wheel_facade_integration`, `method_parity`, `lite_pipeline_parity`) |
| `conformance_refs` | array<producer_id> | ✓ | which producer artifacts the lock will consume (e.g. `dag-ml.shared.conformance.v1`, `dag-ml.nirs4all.parity_oracle.v1`) — names the contract, not the hash |

### 3.3 Manifest example (abbreviated)

```jsonc
{
  "schema_version": "n4a.aggregation-manifest/v1",
  "aggregate_id": "nirs4all-lite",
  "future_aggregate_id": "nirs4all-core",
  "release_train": "2026.07",
  "status": "proposed",
  "compatibility_policy": {
    "python_compat_namespace": "nirs4all", "facade_namespace": "n4a",
    "datasets_default": "external", "private_repos_allowed": false, "r_packages": "explicit"
  },
  "lockstep_groups": [
    { "id": "dagml-pair", "members": ["dag_ml", "dag_ml_data"], "equivalence": "scripts/validate_contracts.py" }
  ],
  "components": [
    {
      "key": "methods", "repo": "GBeurier/nirs4all-methods", "role": "Portable C-ABI PLS/NIRS kernels",
      "owner_boundary": "kernels", "default_inclusion": "aggregate-extra", "optional": false, "private": false,
      "packages": {
        "python": { "distribution": "nirs4all-methods", "imports": ["nirs4all_methods", "n4m", "pls4all"] },
        "r": { "packages": ["n4m"] }, "npm": { "packages": ["@nirs4all/methods-wasm"] },
        "c_abi": { "header": "n4m.h" }, "matlab": { "namespace": "+pls4all" }
      },
      "availability": { "python": "full", "r": "full", "wasm": "subset", "matlab": "subset", "native": "full" },
      "capabilities": ["pls", "preprocessing", "portable_methods"],
      "required_gates": ["n4m_abi_symbols", "method_parity", "version_sync", "lite_pipeline_parity"],
      "conformance_refs": ["n4m.abi.v2", "n4m.parity_ledger"]
    },
    {
      "key": "datasets", "repo": "GBeurier/nirs4all-datasets", "role": "Reference dataset catalog",
      "owner_boundary": "catalog", "default_inclusion": "external", "optional": true, "private": false,
      "packages": { "python": { "distribution": "nirs4all-datasets", "imports": ["nirs4all_datasets"] } },
      "availability": { "python": "full", "r": "subset", "wasm": "subset", "matlab": "none", "native": "full" },
      "required_gates": ["catalog_checksums"], "conformance_refs": []
    }
  ]
}
```

---

## 4. File B — `aggregation-lock.n4a.lock.json`

Machine-generated by `rel lock`. One reproducible release. Merges the A13 lockfile draft with A9 §4's `(dag-ml, dag-ml-data)` pair fields, and adds the explicitly requested per-member availability + release-artifact + verification-command coverage.

### 4.1 Top-level fields

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | const `n4a.aggregation-lock/v1` | lock schema id |
| `aggregation_lock_version` | int `1` | numeric form A9 §4 used; kept as alias for tooling |
| `manifest_digest` | `sha256:…` | sha256 of the manifest this lock was generated from (drift guard) |
| `release_train` | string | mirrors manifest |
| `generated_from` | object | `{ ecosystem_repo, ecosystem_commit }` — provenance of the generator run (no wall-clock authored by hand; `generated_at` stamped by the runner, see §8 note) |
| `members` | object<key→MemberLock> | §4.2 |
| `lockstep_groups` | array<GroupAttestation> | §4.3 |
| `release_artifacts` | object<key→array<Artifact>> | §4.4 |
| `verification` | object | §4.5 — the commands a third party runs to reproduce the gate |
| `policy_assertions` | object | `{ private_repos_present:false, datasets_included:false, all_required_gates_green:true }` |

### 4.2 `MemberLock` — every requested field, per member

| Group | Field | Source (consumed, re-derivable) |
|---|---|---|
| **commit/tag** | `commit` | `git rev-parse` at pin |
| | `tag` | `git describe`/release tag; `tag ≥ manifest_version` (`version-guard` rule) |
| | `repo_url` | manifest |
| **package versions** | `package_versions` | object per ecosystem: `{ python, rust_workspace|rust_crate, npm, r, matlab, c_project }` — each read from that repo's guarded manifest at `commit`. e.g. `dag_ml.rust_workspace="0.2.1"`, `methods.c_project="1.0.1"`, `lite.python="0.2.0"` |
| | `version_guard` | `{ strategy, manifest_path }` it was read from (e.g. `methods` → `c_header:N4M_PROJECT_VERSION_STRING`, `lite` → `cargo_package:bindings/rust/nirs4all/Cargo.toml`) — proves *where* the version is authoritative |
| **schema digests** | `schema_digests` | map `<contract.vN> → normalized_sha256`, **copied from that repo's `conformance_pack.v1.json`** (e.g. `coordinator_data_plan_envelope.v1 → 63b0d862…`). Re-derived by re-hashing the normalized schema. NOT re-pinned: value *equals* the producer's pinned value |
| | `pack_ref` | `{ pack_id, sha256 }` of the whole `conformance_pack.v1.json` (e.g. `dag-ml.shared.conformance.v1`) |
| | `parity_oracle_ref` | `{ oracle_id, canonical_json_sha256 }` (e.g. `dag-ml.nirs4all.parity_oracle.v1` → `eb754d83…`) |
| **C ABI info** | `c_abi` | namespace-scoped. dag-ml/data: `{ data_provider_vtable_abi_version:2, data_tensor_f64_abi_version:1, … , header_sha256 }` from `conformance_pack.c_abi` + `abi_snapshot.v1.json`. methods: `{ n4m_abi_version:"2.0.0", n4m_abi_version_int:20000, symbols_sha256:{linux,macos,windows}, serialization:{magic:"N4MM", format_version:1} }`. formats: `{ header_guard:"NIRS4ALL_FORMATS_H", header_sha256 }` |
| **availability** | `availability` | measured `{ python, r, wasm, matlab, native } → full\|subset\|inspect_only\|none`, validated against the manifest's declared availability and the gates that actually ran (a `wasm:subset` claim requires the member's WASM smoke gate id to be present in `verification`) |
| **conformance packs** | `conformance_refs` | array of `{ producer_id, sha256, gates_green:[case_id…] }` — references only; ties each member to the `required_case_ids`/scenarios it satisfied |
| **lockstep attestation** | (member-level) `attested_in` | the `lockstep_groups[].id` this member participates in (back-pointer; the attestation body is §4.3) |
| **artifacts** | `artifacts` | per-ecosystem built outputs with hashes (§4.4 shape) |
| **license** | `license_expression` | SPDX read from the member manifest at `commit` (`REL-P3`) |
| **sbom/provenance** | `sbom`, `provenance` | `sha256:` of CycloneDX SBOM + provenance ref (Sigstore keyless for lite via `release-source.yml`) |

### 4.3 `GroupAttestation` (lockstep pairs — A9 §4, `REL-P4`)

```jsonc
{
  "id": "dagml-pair",
  "members": ["dag_ml", "dag_ml_data"],
  "shared_contracts": {
    "conformance_pack": { "pack_id": "dag-ml.shared.conformance.v1", "sha256": "<byte-hash of the byte-identical pack>" },
    "parity_oracle": { "oracle_id": "dag-ml.nirs4all.parity_oracle.v1", "canonical_json_sha256": "eb754d832f8c4c059349bbe810683f0afee606b8cab995d85201dd8bf1e83a67" },
    "schemas": {
      "coordinator_data_plan_envelope.v1": "63b0d862bbbf0fd677a59426053a10e0350876943dc437b4a9e16b915956c584",
      "feature_fusion_selector.v1":        "44820d64f6dbc0f5324535135b6806f350518e06e9da63c2b79a8607ba31e84b",
      "coordinator_branch_view.v1":        "2a6780491def139be89428b696051bfd56dab5d4225a3b3092a50624fc27618b",
      "fitted_adapter_ref.v1":             "43001ff6f7a286924ec01ca85b95233c7a50fe9cc8595d67da1eb2a35704dddf",
      "data_output_provenance.v1":         "d90533a9ae7d5a9415a1f8239ea24fbb1e1c37203eba255023e1caadc43494d7"
    },
    "fold_set_fixture_fingerprint": "54d3185d6c628ef0df848828a8d8ae650222a283a78bbd3ab3bc2256f222c05c",
    "required_parity_case_ids": [
      "nirs4all_lite_browser_compile_plan", "repetition_group_leakage_refusal",
      "controller_registry_selector_parity", "branch_merge_oof_refit_replay", "python_wheel_facade_integration"
    ],
    "tolerance_profiles": [
      { "profile_id": "regression.default", "absolute_tolerance": 1e-9, "relative_tolerance": 1e-9 },
      { "profile_id": "classification.default", "absolute_tolerance": 0, "relative_tolerance": 0 }
    ]
  },
  "c_abi": { "data_provider_vtable_abi_version": 2, "data_tensor_f64_abi_version": 1, "data_tensor_f32_abi_version": 1,
             "data_borrowed_tensor_view_abi_version": 1, "data_owned_tensor_abi_version": 1 },
  "aggregation_interop": {                                   // closes A9 Gap-2 (doc-only, unvalidated)
    "mapping_version": "0.2.0",
    "sha256_dag_ml": "<hash of dag-ml/docs/AGGREGATION_INTEROP.md>",
    "sha256_dag_ml_data": "<hash of dag-ml-data/docs/AGGREGATION_INTEROP.md>"
  },
  "equivalence_attestation": {
    "validated": true, "validator_commit": "f58d7bf",
    "checks": ["contracts.schema_and_fixture_equivalence", "headers.include_order",
               "provider.f64_predict_replay", "fold_set.fingerprint_parity"]   // = conformance_pack.cross_repo_conformance
  }
}
```

### 4.4 `release_artifacts` — built outputs (hash-pinned)

Per member, an array of `{ kind, name, ecosystem, version, sha256 }` covering: `wheel`, `sdist`, `crate`, `npm_tarball`, `wasm_pkg`, `r_tarball`, `matlab_toolbox`, `c_header`, `c_lib`, `source_archive`, `sbom`. e.g. `lite` carries the `release-source.yml` outputs (`source_archive` tar+zip, `sbom` CycloneDX, plus the `SHA256SUMS` manifest itself as a pinned artifact). Optional members included in the train still populate this (`REL-P5`).

### 4.5 `verification` — the requested **verification commands**

A reproducible recipe block so a third party (or `nirs4all-cockpit`) re-runs exactly what gated the release. Commands are stored **as data** (no shell authored ad hoc), keyed by member and gate id:

```jsonc
"verification": {
  "lockstep": [
    "DAG_ML_DATA_REPO=../dag-ml-data python3 dag-ml/scripts/validate_contracts.py --require-sibling",
    "DAG_ML_REPO=../dag-ml python3 dag-ml-data/scripts/validate_contracts.py --require-sibling"
  ],
  "members": {
    "dag_ml":  ["python3 scripts/validate_abi_snapshot.py", "python3 scripts/validate_release_metadata.py",
                "python3 scripts/release/check_publish_plan.py --dry-run"],
    "dag_ml_data": ["python3 scripts/validate_abi_snapshot.py", "python3 scripts/validate_release_metadata.py"],
    "methods": ["scripts/bump_version.sh --check", "<abi-check: nm -D | diff cpp/abi/expected_symbols_linux.txt>"],
    "formats": ["VG_STRATEGY=cargo_workspace ... version-guard", "cargo run -p nirs4all-formats-cli -- <conformance>"],
    "lite":    ["scripts/bump_version.sh --check", "python3 scripts/parity/generate_python_oracle.py"]
  },
  "parity_oracle_gates": [ /* the 5 required_case_ids gate commands, copied by reference from parity_oracle.v1.json */ ],
  "lock_self_check": "rel verify --lock aggregation-lock.n4a.lock.json --rederive"
}
```

---

## 5. Conformance-hash consumption map (the heart of `REL-P2`)

Every lock field that *looks like* a hash is shown here with its single upstream producer. **None is authored into the lock; all are re-derivable.**

| Lock field | Upstream producer artifact | Producing repo | Re-derive command (CI) | Re-pinned? |
|---|---|---|---|---|
| `members.dag_ml.schema_digests.*` | `docs/contracts/conformance_pack.v1.json` `contracts.*.normalized_sha256` | dag-ml | `validate_contracts.py` recomputes `normalize_schema` sha256 | **No** (copy of producer value) |
| `lockstep_groups.*.shared_contracts.parity_oracle` | `parity_oracle.v1.json` (canonical-json sha) | dag-ml/dag-ml-data (byte-identical) | recompute `canonical_json_sha256` | No |
| `lockstep_groups.*.shared_contracts.fold_set_fixture_fingerprint` | `parity_oracle.shared` + `SHARED_FOLD_SET_FINGERPRINT` literal | both | `canonical_fold_set_fingerprint` | No |
| `members.*.c_abi` (dagml) | `conformance_pack.c_abi` + `abi_snapshot.v1.json` | dag-ml/data | `validate_abi_snapshot.py` re-hashes header | No |
| `members.methods.c_abi.n4m_abi_version` | `cpp/include/n4m/n4m_version.h` macros | methods | parse header | No |
| `members.methods.c_abi.symbols_sha256.*` | `cpp/abi/expected_symbols_{os}.txt` | methods | `abi-check.yml`: `nm -D | diff` | No |
| `members.*.package_versions.*` | guarded manifest at commit | each | `version-guard`/`version-sync` | No |
| `lockstep_groups.*.aggregation_interop.*` | `docs/AGGREGATION_INTEROP.md` | dag-ml + dag-ml-data | sha256 file (**new** guard, closes Gap-2) | First-pin (doc has no producer hash yet — see §10) |
| `release_artifacts.*.sha256` | built wheel/crate/npm/sbom | each release workflow | `sha256sum` of built artifact | Pin-on-build (no upstream) |

The only values the lock *originates* are: artifact build hashes (no upstream exists until built) and the `aggregation_interop` doc hashes (Gap-2: the doc currently has **no** producer digest). Everything contract-shaped is a consumed reference.

---

## 6. CLI surface (`REL-003..008`)

| Command | Roadmap id | Behavior |
|---|---|---|
| `rel plan` | `REL-003` | read manifest + workspace heads; report drift, missing pins, ABI/API mismatch, lockstep pair skew, version-guard violations, private-member intrusions. No write. |
| `rel lock` | `REL-004` | generate `aggregation-lock.n4a.lock.json`: resolve commits/tags, read guarded versions, **consume** each member's pack/abi-snapshot/parity-oracle digests, build the lockstep attestation, hash built artifacts. Fails if any member is dirty or any consumed digest fails its own producer validator. |
| `rel matrix` | `REL-005` | emit the compat/availability matrix per runtime×package from `members.*.availability` + `parity_oracle` gate coverage (feeds `nirs4all-org`). |
| `rel verify` | (new, `REL-VERIFY`) | §8 — re-derive every consumed hash from the pinned commits and assert equality; the lock's self-check. |
| `rel dry-run-release` | `REL-006` | run `verification.*` commands in a clean checkout matrix; assert gates green; check SBOM/provenance present. |
| `rel export-cockpit` | `REL-007` | read-only projection for `nirs4all-cockpit`. |

Tooling reuses, never forks, the existing per-repo validators (`validate_contracts.py`, `validate_abi_snapshot.py`, `validate_release_metadata.py`, `check_publish_plan.py`, `bump_version.sh --check`, `abi-check`).

---

## 7. How CI validates the lockfile (`REL-VERIFY` job)

A single ecosystem CI job (`contract-aggregation-lock`) that branch protection can require. Algorithm:

1. **Manifest drift.** `sha256(manifest) == lock.manifest_digest`, else fail (lock is stale vs intent).
2. **Checkout matrix.** For each `members.<m>`: shallow-checkout `repo_url@commit`; assert `tag` resolves to `commit` and `tag ≥ package_versions` (mirrors each repo's `version-guard` "manifest never ahead of tag").
3. **Re-derive consumed hashes (`REL-P2` enforcement).** For every entry in the §5 map: recompute from the checked-out member using *that member's own* validator and assert byte-equality with the lock value. Any mismatch ⇒ fail with `{member, field, expected, actual}`. This is what makes "consume not re-pin" mechanically true: the lock cannot drift from the producers without failing.
4. **Lockstep pairs (`REL-P4`).** For each `lockstep_groups`: run both `validate_contracts.py --require-sibling` (the A9 §2.2 guard, so a missing sibling fails loudly instead of green-skipping); assert the byte-identical pack + parity oracle across the pair; assert `equivalence_attestation.checks == conformance_pack.cross_repo_conformance.required_when_sibling_checkout_present`.
5. **Availability honesty.** Each `availability.<lang> ∈ {full,subset}` must have its corresponding gate id present in `verification` and green (no claimed reach without a gate).
6. **Policy.** `policy_assertions`: no `private==true` member (rejects drafts/lab/raw-data, `REL-P6`); if `datasets` present it is pinned; all `required_gates` from the manifest appear green in the lock.
7. **Artifacts.** Every `release_artifacts.*.sha256` matches a built artifact (or, in dry-run, that the producing workflow exists); SBOM + provenance present for the aggregate.

**Determinism note for the generator:** scripts in this environment cannot call wall-clock/RNG; `rel lock` takes `generated_at` from the CI runner and writes it once, but **no hash depends on it** — re-running `rel verify` on a fixed `(manifest, commits)` is bit-stable regardless of timestamp.

---

## 8. How the lockfile gates V1 releases

The lock is the **release gate object**: a V1 train is releasable only when a lock exists that passes `REL-VERIFY` **and** the V1-blocking locks are green for the members it pins.

### 8.1 V1 lock validity predicate

A lock is `release: true` only if all hold:

- `REL-VERIFY` green (§7) — every consumed hash re-derived, every lockstep pair attested.
- For each member with a Python runtime claim: `LOCK-PYREF` green — i.e. `parity_oracle.required_case_ids` all pass **and** the consumer ledger exists. **Currently blocked:** `nirs4all/docs/compatibility.md` is ABSENT (`B-009`; `parity_oracle.consumer_ledger.required_before_bridge=true`). Until it exists, any lock asserting Python parity is `release:false`.
- `LOCK-LOCKSTEP` green for every `lockstep_groups` (A9 §2 hardening: `--require-sibling` + paired-branch).
- `LOCK-CAP` green: `availability`/capability fields reference only frozen `ControllerCapability`/parity ids (no new vocab).
- If the train flips the engine: `LOCK-DROP` green (`EXPECTED_FALLBACK==empty`, native `.n4a` export, `DEFAULT_ENGINE="dag-ml"` suite). Until then a V1 lock is published **legacy-default** (`DEC-DROP-001`: flip last) and records `engine_default:"legacy"`.
- `LOCK-GOV` resolved names: the lock's package names match the accepted naming (`DEC-GOV-002`); `nirs4all-core` clone never appears as a releasable member (`A13`).

### 8.2 Release order the lock enforces (from `RELEASE_DISTRIBUTION_INVENTORY.md` §"Proposed V1 release order")

The lock is generated/validated in dependency order, so a member cannot be pinned before its upstreams:
contracts (`dag-ml`/`dag-ml-data` lockstep) → portable foundations (`formats`, `io`, `methods`, optional `datasets`) → aggregate (`lite`→`core`) → runtime-python (gated by `LOCK-PYREF`) → controller registry/conformance → providers → UI → Studio/Web → cluster → `legacy-DROP` cutover → org docs/SBOM/proof. `rel plan` refuses a lock that pins a downstream member against an unpinned/older upstream.

### 8.3 What "gates V1" means operationally

- **Branch protection** on `nirs4all-ecosystem` requires `contract-aggregation-lock`.
- A member's release workflow (e.g. `lite/release-*.yml`) is allowed to publish a train only if the published `(commit, version, artifact sha256)` matches the train's lock entry — the lock is the authority the publish step checks against, closing the loop with each repo's existing `version-guard`/`version-sync`.
- `nirs4all-cockpit`/`nirs4all-org` render the train from the lock; they never trigger it.

---

## 9. Gaps, blockers, NET-NEW (record, do not fix)

| ID | Sev | Finding | Recommendation |
|---|---|---|---|
| `REL-G1` (=`B-009`) | high | `nirs4all/docs/compatibility.md` ABSENT but `parity_oracle.consumer_ledger.required_before_bridge=true`. Any lock claiming Python parity is invalid until it exists. | L17 must create it before a Python-parity V1 lock; lock encodes `release:false` meanwhile. |
| `REL-G2` (=A9 Gap-2) | med | `AGGREGATION_INTEROP.md` is doc-only, unvalidated, written mirror-perspective; the two copies can silently diverge. Lock has to *originate* its hash (no producer digest exists). | Pin `sha256_dag_ml`/`sha256_dag_ml_data` in the group attestation (§4.3) AND add a `validate_contracts.py` parity check so it becomes a consumed (not originated) value. |
| `REL-G3` (=A9 Gap-4) | high | Paired-PR merge deadlock: sibling checkout uses no `ref:` ⇒ coordinated contract changes can't both go green. Affects any lock regeneration that bumps a shared contract. | Adopt A9 §2.3 paired-branch ref + §3.4 merge protocol before the first multi-member contract bump in a train. |
| `REL-G4` | med | Two independent C-ABI cadences (`dagml vtable_abi=2` vs `n4m ABI 2.0.0`) share the integer "2" by coincidence. | Keep them namespaced in `members.*.c_abi` (done in §4.2); never compare across namespaces. |
| `REL-G5` | low | `LOCK-IO` not frozen ⇒ `DatasetSpec v2`/`DatasetPackage` digests can't yet be consumed for `io`/`datasets` members. | Add `io` schema digests to the consumption map (§5) once `LOCK-IO` lands; until then `io` pins commit/version/artifacts only. |
| `REL-NN` | – | **NET-NEW vs surfaced** (need sign-off): the two-file manifest/lock split, `availability` measured matrix, `lockstep_groups` grouping object, `verification` command block, `policy_assertions`, and `rel verify --rederive`. All *compose* existing producers; none invents a contract digest. | A0 to sign as part of `LOCK-REL`. |

**Open questions for A0/maintainer:**
1. File location: `nirs4all-ecosystem/` (coordination repo, per inventory) vs the future `nirs4all-core` release repo? (Recommend ecosystem; cockpit reads it.)
2. `aggregation_interop` — pin-only now (REL-G2) or block `LOCK-REL` on adding the `validate_contracts.py` mapping check first?
3. Does a V1 train **require** `datasets` excluded (`external`) by default, with inclusion as an explicit per-train opt-in? (`DEC-GOV-002` implies yes.)
4. Naming: lock records names per `REL-NAME-001..004`/`REL-NPM-001`; are those accepted enough to freeze member `packages.*`, or does the lock pin `nirs4all-lite` names and carry `@nirs4all/core` as a reserved alias only?

---

## 10. Sync-board handoff for A0 (NOT applied — report mode)

**Proposed `L3` lane line:**

```
| `L3` Aggregation/release tooling | review | TBD | `nirs4all-ecosystem` | Sign LOCK-REL on SW3_REL_MANIFEST_LOCKFILE_spec.md: two-file manifest/lock that CONSUMES per-repo conformance hashes (§5 map), lockstep pair attestation (A9 §4), REL-VERIFY re-derivation gate (§7), V1 gate predicate (§8). | `LOCK-GOV` (names), `B-009` (compatibility.md for Python-parity claims), `LOCK-IO` (io/datasets digests) |
```

**Proposed worklog entry (append-only):**

```
2026-06-30 | SW3/L3 | review | Drafted LOCK-REL aggregation manifest + ecosystem lockfile schemas in docs/agent_reports/SW3_REL_MANIFEST_LOCKFILE_spec.md. Core principle: lock CONSUMES per-repo conformance hashes (conformance_pack/parity_oracle/abi_snapshot/n4m_version.h/expected_symbols), never re-pins (DEC-REL-001, LOCKSTEP-004). Covered members/commits/tags/package-versions/schema-digests/c_abi(2 namespaces: dagml vtable_abi=2, n4m ABI 2.0.0)/availability/conformance-packs/lockstep-attestation(A9 §4)/release-artifacts/verification-commands; REL-VERIFY re-derivation CI job; V1 gate predicate (PYREF/LOCKSTEP/CAP/DROP/GOV). | read-only: verified dag-ml f58d7bf (pack/oracle/abi_snapshot/validate_release_metadata), dag-ml-data 347c15f (0.2.2, header sha256), methods n4m_version.h (proj 1.0.1, ABI 2.0.0)+expected_symbols, formats 0.2.1, lite 0.2.0+release-source SBOM/Sigstore; confirmed nirs4all/docs/compatibility.md ABSENT (B-009) and AGGREGATION_INTEROP.md doc-only (Gap-2); no aggregation-lock exists yet (net-new). | A0 sign LOCK-REL; REL-G1 blocks Python-parity locks until compatibility.md; REL-G3 (paired-branch) before first multi-member contract bump; add io digests after LOCK-IO.
```

**Cross-lane handoffs:** L20/A9 owns the lockstep `equivalence_attestation` body the lock embeds (§4.3); L1/`LOCK-GOV` owns the names the lock pins; L17 owns `compatibility.md` (REL-G1); L7/`LOCK-IO` will add `io`/`datasets` schema digests to §5; L4 (`nirs4all-lite`→core) **consumes** this lock as its contract-version pin (A9 §4 cross-lane note).

---

## 11. Tests / gates (none run — read-only spec)

Validators this spec wires (all pre-existing, reused not forked):
`dag-ml/scripts/validate_contracts.py [--require-sibling]`, `validate_abi_snapshot.py`, `validate_release_metadata.py`, `scripts/release/check_publish_plan.py --dry-run`; `nirs4all-methods/scripts/bump_version.sh --check` + `abi-check.yml` symbol diff; `nirs4all-formats` `version-guard.yml`/`version-sync.yml` + `conformance.yml`; `nirs4all-lite` `version-guard.yml` (`cargo_package`) + `release-source.yml` (CycloneDX SBOM, SHA256SUMS, Sigstore). New ecosystem job `contract-aggregation-lock` = §7 `rel verify`.
