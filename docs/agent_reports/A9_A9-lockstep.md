# A9 — L20 Lockstep `dag-ml` ↔ `dag-ml-data`

**Agent:** A9 (L20 lockstep), read-only audit/spec mode
**Date:** 2026-06-30
**Lane:** `L20` dag-ml/dag-ml-data lockstep · Lock `LOCK-LOCKSTEP` · Decision `DEC-LOCKSTEP-001` · Blocker `B-008`
**Audit baseline (heads, tree clean for `docs/contracts` + `scripts/validate_contracts.py`):**

| Repo | HEAD | Branch |
|---|---|---|
| `dag-ml` | `f58d7bf` | main |
| `dag-ml-data` | `347c15f` | main |
| `nirs4all-ecosystem` | `d55ed18` | main |

**Evidence / gates executed (read-only, validators write nothing):**

```
DAG_ML_DATA_REPO=…/dag-ml-data  python3 dag-ml/scripts/validate_contracts.py        → exit 0
DAG_ML_REPO=…/dag-ml            python3 dag-ml-data/scripts/validate_contracts.py   → exit 0
(control) unset DAG_ML_DATA_REPO python3 dag-ml/scripts/validate_contracts.py       → exit 0  *still auto-found ../dag-ml-data*
```

**Bottom line:** the lockstep machinery already **exists and is wired into both CIs and currently GREEN**. This is *not* greenfield. The remaining L20 work is (a) closing three concrete enforcement gaps, (b) solving the paired-PR **merge deadlock**, and (c) specifying the release/aggregation lockfile fields. No cross-repo contract is changed by this report.

---

## 0. How lockstep is enforced today (verified mechanism)

Each repo ships `scripts/validate_contracts.py` (dag-ml: 5554 LOC; dag-ml-data: 1031 LOC), stdlib-only. Mechanism:

1. **Sibling discovery** — `candidate_sibling_roots()` tries, first-existing-wins:
   `$DAG_ML_DATA_REPO`/`$DAG_ML_REPO` → `../dag-ml-data` (sibling-workspace) → `./external/dag-ml-data` (CI layout). (dag-ml `validate_contracts.py:5233`, dag-ml-data `:854`.)
   - env var **set but missing** → hard `ContractError`.
   - env var **unset and no candidate on disk** → returns `None` → equivalence **silently skipped, exit 0**.
2. **`$id` normalization** — `normalize_schema()` deep-copies and pops `$id` before hashing (dag-ml-data `:528`). Schema **bodies** are compared; the `$id` URL (which embeds the repo name) is allowed to diverge.
3. **Digest pinning** — `conformance_pack.v1.json` stores `normalized_sha256` per shared schema and `canonical_json_sha256` for the parity oracle. Each side recomputes its local artifact's digest and asserts it equals the pinned value (`validate_conformance_pack`, dag-ml-data `:555`).
4. **Direct sibling comparison** (only when sibling present) — `normalize_schema(local)==normalize_schema(sibling)` for the two coordinator/fusion schemas, raw JSON equality for the two shared fixtures, `canonical_fold_set_fingerprint` equality for the fold set, and full equality of the pack and parity oracle (dag-ml `:5523-5545`, dag-ml-data `:1000-1022`).
5. **CI wiring** — both `ci.yml` files `actions/checkout` the sibling into `external/<sibling>` and export the env var, then run the validator (dag-ml `ci.yml:50-66`, dag-ml-data `ci.yml:47-58`). The sibling checkout has **no `ref:`** → it is always the sibling's **default branch**.

Documented intent matches the code: `dag-ml/docs/contracts/README.md:45-49,73-74,96-97,107` ("normalized SHA-256 with `$id` stripped is pinned identically in both repos"); both `CLAUDE.md` "Shared Contracts" tables.

---

## 1. LOCKSTEP matrix (deliverable 1)

Shared surface = the intersection of `docs/contracts/` + the cross-compared fixtures/headers/source. Equivalence **classes** define *what must match* and *what may diverge*. "Verdict" = state at the audit baseline.

### 1.1 Hash-pinned contract artifacts

| Artifact | dag-ml path | dag-ml-data path | Equivalence rule | Enforced by | May diverge | Verdict |
|---|---|---|---|---|---|---|
| **conformance pack** | `docs/contracts/conformance_pack.v1.json` | same | **Whole file byte/JSON-identical** | `local_pack==sibling_pack` + digest self-check | nothing | ✅ identical (`da08bbd1…`) |
| **parity oracle** | `docs/contracts/parity_oracle.v1.json` | same | **Whole file byte/JSON-identical** | `local_parity_oracle==sibling_parity_oracle` | nothing | ✅ identical (`c3e2fa3e…`) |
| coordinator_data_plan_envelope schema | `docs/contracts/coordinator_data_plan_envelope.schema.json` | same | **Body identical**, `$id` differs | direct `normalize_schema==` + pack digest `63b0d862…` | `$id` only | ✅ body-equal, `$id` differs (by design) |
| feature_fusion_selector schema | `docs/contracts/feature_fusion_selector.schema.json` | same | **Body identical**, `$id` differs | direct `normalize_schema==` + pack digest `44820d64…` | `$id` only | ✅ body-equal |
| coordinator_branch_view schema | `docs/contracts/coordinator_branch_view.schema.json` | same | **Body identical**, `$id` differs | **pack digest only** `2a678049…` (no direct sibling compare) | `$id` only | ✅ body-equal |
| fitted_adapter_ref schema | `docs/contracts/fitted_adapter_ref.schema.json` | same | **Body identical**, `$id` differs | **pack digest only** `43001ff6…` | `$id` only | ✅ body-equal |
| data_output_provenance schema | `docs/contracts/data_output_provenance.schema.json` | **absent** | dag-ml-owned; digest advertised in shared pack `d90533a9…` | pack digest checked **only on dag-ml side**; data side relies on byte-identical pack | whole schema (data side has none) | ⚠️ single-owner asymmetry (see Gap-1) |

### 1.2 Shared fixtures

| Fixture | dag-ml path | dag-ml-data path | Rule | Enforced by | May diverge | Verdict |
|---|---|---|---|---|---|---|
| envelope fixture | `examples/fixtures/data/coordinator_data_plan_envelope_nir.json` | `examples/fixtures/oof_campaign/coordinator_data_plan_envelope_nir.json` | **Content JSON-identical** | `local_fixture==sibling_fixture` + pack `canonical_json_sha256 420a01e4…` | **relative path** | ✅ content-equal, paths differ (by design) |
| fusion-selector fixture | `examples/fixtures/data/feature_fusion_selector_nir_chem.json` | `examples/fixtures/oof_campaign/feature_fusion_selector_nir_chem.json` | **Content JSON-identical** | direct equality + pack `aee68b20…` | relative path | ✅ content-equal |
| **fold set** | `examples/fixtures/shared/fold_set_cv_partition.json` | same path | **Canonical fingerprint identical** (sorted sample_ids/folds) | `canonical_fold_set_fingerprint==` + literal `SHARED_FOLD_SET_FINGERPRINT` in **both** validators + `parity_oracle.shared.fold_set_fixture_fingerprint` | raw row order | ✅ all three pin `54d3185d…` |
| pack-tracked fixtures (envelope nir, multisource, fusion, data_output_provenance, oof uc6, oof uc11) | `examples/fixtures/**` | partial | `canonical_json_sha256` pinned in pack | self-check vs pack | — | ✅ |

### 1.3 C ABI / header / source surfaces

| Surface | dag-ml | dag-ml-data | Rule | Enforced by | Verdict |
|---|---|---|---|---|---|
| C header file | `crates/dag-ml-capi/include/dag_ml.h` | `crates/dag-ml-data-capi/include/dag_ml_data.h` | **Different files**; must declare required vtable/tensor symbols + include in either order | `validate_data_provider_header` / `validate_dag_ml_data_tensor_header`; cross-header `cc -fsyntax-only` smoke | ✅ |
| C ABI versions + required symbols | `conformance_pack.c_abi` block (byte-identical pack) | same | vtable_abi=2, tensor f64/f32=1, borrowed/owned tensor=1; symbol allow-list | pinned in pack | ✅ |
| relative-URI rule (source) | `crates/dag-ml-core/src/runtime/prediction_store.rs` | — | dag-ml-data extracts dag-ml's fn body, asserts fragments | `validate_relative_uri_rule_parity` (**one-directional**, data→ml) | ✅ |
| parity case corpus | `parity_oracle.cases` + `required_case_ids` | same (byte-identical) | identical set; 5 required ids | pack/oracle equality + `REQUIRED_PARITY_CASE_IDS` | ✅ |

### 1.4 Intentionally per-repo (NOT in the equivalence set)

| Artifact | Why it diverges | Guard |
|---|---|---|
| `docs/contracts/README.md` | repo-specific prose (21.4K vs 5.1K) | none (doc) |
| `docs/contracts/abi_snapshot.v1.json` | own crate / `package_version` (0.2.1 vs 0.2.2) / own header sha256 | within-repo `validate_abi_snapshot.py` |
| schema `$id` URL | embeds repo name (`/dag-ml/` vs `/dag-ml-data/`) | normalized away before compare |
| fixture relative paths | each repo files fixtures under its own tree | content compared, path not |
| `AGGREGATION_INTEROP.md` | **mirror-perspective prose**, intentionally written from each side | ⚠️ none — doc-only, **not validated** (see Gap-2) |
| Cargo package names/versions | independent crates & release cadence | version-guard workflow |

**Divergence-allowed fields, consolidated (deliverable 5 — see also §4):** `$id`; fixture **relative path**; fold-set **raw row order**; C-header **filename + repo-local symbols**; `README.md`; `abi_snapshot` (crate/version/own-header hash); Cargo **package name/version**. **Everything else in §1.1–§1.3 must be byte/canonical-identical.**

---

## 2. CI contract-equivalence proposal (deliverable 2)

The equivalence job already runs in both repos. Three hardening changes make it deadlock-free and skip-proof. **No schema change required.**

### 2.1 Canonical command (runnable identically from either repo)

```bash
# from dag-ml/         (sibling auto-found at ../dag-ml-data, or override)
DAG_ML_DATA_REPO=../dag-ml-data python3 scripts/validate_contracts.py
# from dag-ml-data/
DAG_ML_REPO=../dag-ml             python3 scripts/validate_contracts.py
```

### 2.2 Add a `--require-sibling` guard (closes Gap-3, the silent-skip)

Today, env-var-unset + no sibling on disk ⇒ exit 0 with equivalence **skipped**. The lockstep CI job must *fail* if it did not actually compare. Minimal, additive (no contract impact):

```python
# main(): after sibling = sibling_root()
if "--require-sibling" in sys.argv and sibling is None:
    raise ContractError("lockstep equivalence required but no sibling checkout found")
```

CI step becomes `python3 scripts/validate_contracts.py --require-sibling`. Defense-in-depth so a future workflow refactor that drops the sibling checkout fails loudly instead of green-passing.

### 2.3 Compare against the **paired branch**, not the sibling's `main` (breaks the deadlock)

Both `ci.yml` checkout the sibling with no `ref:` ⇒ always `main`. Make the sibling checkout follow a same-named paired branch when one exists, falling back to `main`:

```yaml
- name: Resolve sibling ref (paired branch or main)
  id: peer
  run: |
    git ls-remote --exit-code --heads https://github.com/GBeurier/dag-ml-data \
      "${{ github.head_ref }}" >/dev/null 2>&1 \
      && echo "ref=${{ github.head_ref }}" >> "$GITHUB_OUTPUT" \
      || echo "ref=main" >> "$GITHUB_OUTPUT"
- uses: actions/checkout@v6
  with:
    repository: GBeurier/dag-ml-data
    ref: ${{ steps.peer.outputs.ref }}
    path: external/dag-ml-data
```

Convention: **a coordinated shared-contract change uses the same branch name in both repos.** Each PR's CI then compares against its partner branch and both go green *before* either merges. (Mirror the symmetric block into `dag-ml-data/ci.yml`.)

### 2.4 Optional: dedicated `lockstep` job + reusable workflow

Split the equivalence assertions into a named `contract-lockstep` job (so branch protection can require exactly it), and factor the checkout+validate steps into a `workflow_call` reusable workflow shared by both repos to prevent the two CIs from drifting.

---

## 3. Paired-PR policy draft (deliverable 3) — feeds `DEC-LOCKSTEP-001`

**Trigger:** any change under `docs/contracts/` (shared schemas, pack, parity oracle), the shared fixtures, the fold set, the C-ABI version macros/required symbols, or `prediction_store.rs` relative-URI rule.

### 3.1 Paired commits

- One logical change ⇒ **two PRs, identical branch name** in `dag-ml` and `dag-ml-data`.
- Each PR carries the matching edit to **both repos' copies** of every shared artifact in §1.1–§1.2 (the body, the pinned digests, the fixtures).
- PR descriptions cross-link (`Pairs-With: GBeurier/<repo>#<n>`). Neither merges until **both** are green against each other (via §2.3).

### 3.2 Expected hash changes (must be reviewed, not rubber-stamped)

| If you change… | …these pinned values change, identically in **both** repos |
|---|---|
| a shared schema body | `conformance_pack.contracts.<name>.normalized_sha256` |
| a shared fixture content | `conformance_pack.fixtures.<name>.canonical_json_sha256` |
| the fold set | `parity_oracle.shared.fold_set_fixture_fingerprint` **and** `SHARED_FOLD_SET_FINGERPRINT` literal in **both** `validate_contracts.py` |
| the parity corpus | `parity_oracle.cases` + `required_case_ids` (+ `REQUIRED_PARITY_CASE_IDS`) |
| a shared schema `$id` | **only** the local `$id` (normalized away — must NOT touch digests) |
| the C header | local `abi_snapshot.v1.json` header `sha256` (per-repo); cross-header include smoke must still pass; bump `*_ABI_VERSION` macro + pack `c_abi` if the wire/symbol surface changes |

### 3.3 Reviewer checklist (paste into PR template)

- [ ] Same branch name exists in the sibling repo; PRs cross-link (`Pairs-With`).
- [ ] Every §1.1/§1.2 artifact edited in **both** repos; schema bodies differ **only** by `$id`.
- [ ] `normalized_sha256` / `canonical_json_sha256` in `conformance_pack.v1.json` updated to match, **and identical** across repos.
- [ ] Fold-set change ⇒ all **three** fingerprint locations updated to the same value.
- [ ] `conformance_pack.v1.json` and `parity_oracle.v1.json` are **byte-identical** across repos (`diff` clean).
- [ ] `python3 scripts/validate_contracts.py --require-sibling` green **in both** repos against the partner branch.
- [ ] Wire-shape change ⇒ schema `schema_version` / ABI version macro bumped per each `CLAUDE.md` "When Touching… Schemas".
- [ ] `docs/STATUS.md` / `ROADMAP.md` updated on the data side when the envelope/vtable/schema changed.

### 3.4 Merge protocol (deadlock resolution)

1. Open both paired PRs (same branch name). §2.3 makes each compare against the other ⇒ both reach green.
2. Merge **owner repo first** per ownership (data-shape contracts → `dag-ml-data`; coordinator/runtime contracts → `dag-ml`), then the sibling within the same merge window.
3. Branch protection: require the `contract-lockstep` job. **Do not** use admin-override to land one side alone — that re-introduces drift the other repo's `main` CI will then fail on.
4. **Durable end-state (recommended):** designate a **single canonical owner** per shared artifact and **generate** the mirror copy via a committed sync script (`scripts/sync_shared_contracts.py --check` in CI). A bot opens the mirror PR. This turns "two humans edit two copies" into "one edit + a mechanical mirror," eliminating hand-desync. Track as a follow-up to `DEC-LOCKSTEP-001`.

### 3.5 Release lockfile (paired releases)

A `dag-ml`/`dag-ml-data` release pair is valid only if their shared contract set is equivalent. The release train (L3 / `LOCK-REL`) must pin both repos together using the **aggregation-lock fields** in §4. A release of one repo that changes a shared contract **requires a matching release of the other**; the lockfile records the proof.

---

## 4. Aggregation-lock fields needed (deliverable 4) — feeds `LOCK-REL` / `DEC-REL-001` (owner L3)

The aggregation manifest/lockfile (ecosystem "source de verite release", watchlist row "Aggregation manifest/lockfile") must pin a coherent `(dag-ml, dag-ml-data)` pair so `nirs4all-lite` and downstream can depend on a single attested contract version. Required fields:

```jsonc
{
  "aggregation_lock_version": 1,
  "members": {
    "dag-ml":      { "commit": "f58d7bf…", "tag": "v0.2.1", "package_version": "0.2.1",
                     "header_sha256": "96914365…" },          // from abi_snapshot.v1.json (per-repo)
    "dag-ml-data": { "commit": "347c15f…", "tag": "v0.2.2", "package_version": "0.2.2",
                     "header_sha256": "ca5d3426…" }
  },
  "shared_contracts": {
    "conformance_pack": { "pack_id": "dag-ml.shared.conformance.v1", "sha256": "<byte-hash of the byte-identical pack>" },
    "parity_oracle":    { "oracle_id": "dag-ml.nirs4all.parity_oracle.v1", "canonical_json_sha256": "eb754d83…" },
    "schemas": {                                              // normalized_sha256 (== values in the pack)
      "coordinator_data_plan_envelope.v1": "63b0d862…",
      "feature_fusion_selector.v1":        "44820d64…",
      "coordinator_branch_view.v1":        "2a678049…",
      "fitted_adapter_ref.v1":             "43001ff6…",
      "data_output_provenance.v1":         "d90533a9…"        // single-owner: dag-ml; advertised in pack
    },
    "fold_set_fixture_fingerprint": "54d3185d…",
    "required_parity_case_ids": [ "nirs4all_lite_browser_compile_plan", "repetition_group_leakage_refusal",
      "controller_registry_selector_parity", "branch_merge_oof_refit_replay", "python_wheel_facade_integration" ]
  },
  "c_abi": {                                                  // from conformance_pack.c_abi
    "data_provider_vtable_abi_version": 2,
    "data_tensor_f64_abi_version": 1, "data_tensor_f32_abi_version": 1,
    "data_borrowed_tensor_view_abi_version": 1, "data_owned_tensor_abi_version": 1
  },
  "aggregation_interop": {                                    // closes Gap-2: pin the doc-only mapping
    "mapping_version": "0.2.0",
    "sha256_dag_ml": "<hash of dag-ml/docs/AGGREGATION_INTEROP.md>",
    "sha256_dag_ml_data": "<hash of dag-ml-data/docs/AGGREGATION_INTEROP.md>"
  },
  "equivalence_attestation": {
    "validated": true,
    "validator_commit": "f58d7bf…",
    "checks": [ "contracts.schema_and_fixture_equivalence", "headers.include_order",
                "provider.f64_predict_replay", "fold_set.fingerprint_parity" ]   // = pack.cross_repo_conformance
  }
}
```

Field rationale: `members.*` pin the exact source/release; `shared_contracts.*` are the *identity* of the contract version (so a consumer can detect drift without checking out both repos); `c_abi` pins binary compatibility for the lite/WASM aggregate; `aggregation_interop` pins the otherwise-unenforced method-vocabulary mapping; `equivalence_attestation` records that the lockstep gate actually ran (mirrors `conformance_pack.cross_repo_conformance.required_when_sibling_checkout_present`).

---

## 5. Findings / gaps / blockers (record, do not fix — per session mode)

| ID | Severity | Finding | Recommendation |
|---|---|---|---|
| **Gap-1** | low | `data_output_provenance.v1` is dag-ml-owned, advertised in the shared pack, but **has no schema copy in dag-ml-data** and is recomputed only on the dag-ml side. Its data-side integrity rests solely on the pack being byte-identical. | Document as a deliberate single-owner contract, or mirror a copy so both sides recompute. Decide under `DEC-LOCKSTEP-001`. |
| **Gap-2** | medium | `AGGREGATION_INTEROP.md` is a **paired contract written in mirror perspective**, **doc-only and not validated** — the two files can silently disagree. | Pin both files' hashes in the aggregation lock (§4) and/or add a `validate_contracts.py` parity check on the mapping table. |
| **Gap-3** | medium | Equivalence is **silently skipped (exit 0)** when no sibling is on disk and the env var is unset. CI is currently safe (env var always set), but nothing asserts the comparison ran. | Add `--require-sibling` (§2.2) to the lockstep CI step. |
| **Gap-4** | high | Sibling checkout uses **no `ref:`** ⇒ paired PRs compare against the other repo's `main` ⇒ **two-repo merge deadlock** for any coordinated shared-contract change. | Paired-branch ref resolution (§2.3) + merge protocol (§3.4). |
| **Gap-5** | low | `branch_view` and `fitted_adapter_ref` schemas are pinned **only transitively** via the pack digest (no direct sibling compare like the envelope/fusion schemas). Sound today, but asymmetric. | Optional: add direct `normalize_schema==` for symmetry, or document the pack-digest-only path. |

**Blocked-on (lane blockers):** `LOCK-REL` (the §4 lockfile is owned by L3) and `LOCK-IO` (`DatasetSpec v2`/`DatasetPackage` will add shared surface to lockstep). The CI/PR-policy work in §2–§3 is **not** blocked and can land independently of those locks.

---

## 6. Sync-board handoff for A0 (I did NOT edit `PARALLEL_REFACTORING_SYNC.md` — session mode)

**Lane line replacement (`L20`):**

```
| `L20` dag-ml/dag-ml-data lockstep | review | TBD | `dag-ml`, `dag-ml-data` | Land §2 CI hardening (require-sibling + paired-branch ref) and §3 paired-PR policy; §4 lockfile fields handed to L3. | `LOCK-REL`, `LOCK-IO` |
```

**Worklog entry (append):**

```
2026-06-30 | Claude/A9-L20 | review | Audited dag-ml↔dag-ml-data lockstep at dag-ml f58d7bf / dag-ml-data 347c15f. Produced LOCKSTEP matrix, CI proposal, paired-PR policy, aggregation-lock fields in docs/agent_reports/A9_A9-lockstep.md. | Both validate_contracts.py green cross-repo (exit 0); confirmed $id-normalized equivalence + byte-identical pack/parity-oracle; found 5 gaps (silent-skip, paired-PR deadlock, doc-only interop, single-owner data_output_provenance, transitive-only branch_view/fitted_adapter). | Gap-4 (merge deadlock) needs §2.3 before any coordinated schema change; §4 lockfile fields belong to L3/LOCK-REL.
```

**Proposed status moves (for A0/maintainer to ratify):**

- `DEC-LOCKSTEP-001` — refine `Decision` text to: *"Shared `docs/contracts/` schemas (bodies, `$id` excepted), the byte-identical conformance pack + parity oracle, shared fixtures (content, path excepted), and the fold-set fingerprint change in paired same-named branches; CI compares against the partner branch with `--require-sibling`; releases are pinned together by the aggregation lock (§4)."* Keep status `proposed` until maintainer accepts.
- `LOCK-LOCKSTEP` — keep `review`; can move to `ready` once `DEC-LOCKSTEP-001` is `accepted` (rule 4: a lock activates only on an accepted decision).
- `B-008` — annotate: mechanism exists + green; residual = release lockfile (`LOCK-REL`) + Gap-4 merge protocol. Do not close until `LOCK-REL` lands the §4 fields.
- Interface watchlist row "`dag-ml`/`dag-ml-data` mirrored contracts" — extend coverage note to include `AGGREGATION_INTEROP.md` (Gap-2) and `parity_oracle.v1.json`.

**Cross-lane notes:** L3 (`LOCK-REL`) owns the §4 aggregation-lock fields — hand them over. L6 (dag-ml-data providers) and L5 (dag-ml runtime) must route any envelope/vtable/schema edit through this paired-PR policy. L4 (`nirs4all-lite` aggregate) consumes the §4 lockfile as its contract-version pin.
