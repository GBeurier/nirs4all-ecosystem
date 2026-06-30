# INTEGRATION DIGEST for A0 — 8 prior-run reports

**Author:** INTEGRATION-DIGEST agent (read-only) · **Date:** 2026-06-30
**Scope:** digest of `A1, A2, A3, A4, A5, A8, A9, A13` under `docs/agent_reports/` so A0 can
integrate them into `PARALLEL_REFACTORING_SYNC.md` without re-reading them.
**Verification baseline (re-checked):** nirs4all `e41362b4`, dag-ml `f58d7bf`, dag-ml-data `347c15f` — **all match**.
**Not covered by any report (confirmed):** `LOCK-CAP`, `LOCK-RT`, `LOCK-IO`, `LOCK-UI`, `L14` PROV, `L15` cluster-hardening, `DEC-PROOF-001`.
**Reports NOT in this set:** A6 (studio-ui) FAILED (empty); A7 (cluster) absent.

---

## Table 1 — Par lock

| Lock | Report source | Verdict | Top blocker | Action to sign |
|---|---|---|---|---|
| `LOCK-GOV` | A13 (L1/L3/L4) | **blocked — direction drafted, awaits maintainer P1.** A13 wrote DEC-GOV-001 (temp `nirs4all-core` clone = integration vehicle only, no public identity) + DEC-GOV-002 (lite→core staged). Confirmed: no named `nirs4all-core` worktree exists. | Maintainer P1 (`ARB-013/014`) not answered → `DEC-GOV-001/002` stay `proposed`. | Maintainer accepts DEC-GOV-001 then DEC-GOV-002; until then `L1` review / `L4` blocked. |
| `LOCK-CAP` | **none** | **uncovered** — no CAP-SPEC report in this set (A0 noted CAP agent in-flight, not duplicated). | n/a | Run/await the CAP-SPEC report (derive capabilities from controller enum per DEC-CAP-001). |
| `LOCK-PYREF` | A2 (primary) · A1 (evidence) · A3 (DROP side) · A5 (methods gate) | **direction OK but final sign blocked.** Oracle exists at 95 cases / dual-engine; 3-tier registry `PYREF-000` drafted (A2 §2). | **`B-009` valid (verified):** `nirs4all/docs/compatibility.md` MISSING; `parity_oracle.v1.json` pins it `required_before_bridge:true` @ tol `1e-9` while enforced is `1e-3`. | Author `compatibility.md` (reconcile 1e-9/1e-3/per-case); land G1–G9 (A2 §7). |
| `LOCK-MIG` | A8 (L18) | **direction OK, spec to finish.** DEC-MIG-001 accepted; A8 specs `nirs4all-tools` no-in-place CLI + manifest/report/checksum/id-map contract + fixtures. | Target schema + manifest/report/checksum/id-map vocab NOT accepted (A8 §"LOCK-MIG Blockers", 10 items). | Accept DEC-MIG target (Phase1 `nirs4all-workspace-v2`); ratify manifest/checksum/id-map vocab; Phase2 native gated on LOCK-REL. |
| `LOCK-DROP` | A3 (primary, L5/L19) · A2 (D1–D8 gates) | **criterion frozen, blocked.** Flip stays last. | **`B-010` valid (verified):** `EXPECTED_FALLBACK` = 11 exact (4 `branch_dup_*` + 4 `multi_source_*` + 3 `preprocessing_*`). Owner = **L5/A3** (host-bridge serialization, not dag-ml-core). | Shrink `EXPECTED_FALLBACK`→empty (D1) + native `.n4a` export (D2/DML-008) + Studio records engine (D5); D1–D8 in A2 §8. |
| `LOCK-LOCKSTEP` | A9 (L20) | **landed mechanism GREEN both sides (verified present), but 2 residual gaps before any coordinated schema change.** | **Gap-4 (high):** sibling CI checkout has no `ref:` → paired PRs compare vs `main` → 2-repo merge deadlock. **Gap-3:** silent-skip exit 0 when no sibling. | Add `--require-sibling` + paired-branch ref (A9 §2.2/§2.3); refine DEC-LOCKSTEP-001 text (A9 §6); §4 lockfile → L3. |
| `LOCK-REL` | A13 (manifest+lockfile fields) · A9 §4 (aggregation-lock fields) | **direction OK, schema to finish.** Two concrete field schemas delivered (A13 `aggregation-manifest/lock`; A9 `aggregation_lock_version`). Consistent with "consume conformance-pack hashes". | `DEC-REL-001` schema not drafted into an artifact; GOV-gated. | Turn A13+A9 fields into the DEC-REL-001 schema; pin `(dag-ml,dag-ml-data)` pair via A9 §4. |
| `LOCK-IO` | **none** | **uncovered** — no IO-SPEC report. A9 flags it as downstream lockstep surface (`DatasetSpec v2` adds shared contracts). | n/a | Run/await IO-SPEC (extend existing `io→dag-ml-data` bridge `84ab189`, net-new SCHEMA_VERSION). |
| `LOCK-RT` | **none** | **uncovered** — no RT-SPEC report (A0 noted RT agent in-flight). A4 §4.3 needs the `GET /api/operators/manifests` route from LOCK-RT. | n/a | Run/await RT-SPEC; it unblocks L10/L12/L16 implementation + Studio manifest endpoint. |
| `LOCK-UI` | **none** | **uncovered** — A6-studio-ui FAILED (empty log/no `.md`). | n/a | Re-run the UI/studio agent; LOCK-UI depends on LOCK-CAP/LOCK-RT. |

*(CTRL is not a lock; it rides `DEC-CTRL-001` + `L16` — covered by A4, see Table 2.)*

---

## Table 2 — Par lane (lanes touched by a report)

| Lane | Report | Proposed status | Suggested owner | Next action |
|---|---|---|---|---|
| `L1` Governance | A13 | review | A13/L1 | Convert A13 draft → DEC-GOV-001/002 to maintainer. |
| `L3` Aggregation/release | A13 + A9 §4 | review | REL-SPEC / A13 | Turn manifest+lockfile fields into DEC-REL-001 schema. |
| `L4` Core aggregate | A13 | blocked | A13/L4 | Stay blocked on GOV/REL; A13 scope-matrix done (lite=facade+portable subset, no kernels). |
| `L5` dag-ml runtime | A3 | review | A3/L5 | DML-002 (migrate `detect.py`/`run_paths.py` shape-grammar DOWN), DML-003 (coverage meter), DML-008 (native export). Owns `B-010`. |
| `L9` methods/parity | A5 (+A2 PYREF-010) | review | A5/L9 | V1 = sklearn-host controller + **mandatory methods-installed CI gate**; defer direct n4m C-ABI controller to V1.1/V2 (ARB-003=A). |
| `L12` Studio reassembly | A2 (PYREF-008) + A8 | review | A2↔L12 / A8 | Extract 4 backend re-implementations (transfer/predict/analysis) into nirs4all; Studio records engine; replace in-process migration with non-mutating `GET /workspace/legacy-status`. |
| `L16` Controllers/bindings | A4 (+A5 §5.3) | review | A4/L16 | Ratify ARB-004=A + DEC-CTRL-002..007; implement two-layer adapter extending `dagml_bridge.controller_manifests()`. |
| `L17` Oracle parity Python | A2 (+A1) | review | A2/L17 | Land `PYREF-000` `_authority.py` + `compatibility.md`; close G5–G9 gaps. Owns `B-009`. |
| `L18` Tools/migration | A8 | blocked | A8/L18 | Accept DEC-MIG target + manifest/checksum/id-map vocab; build `nirs4all-tools`. |
| `L19` Cutover DROP | A3 + A2 | blocked | A0/L19 | Sequenced last; gated on `B-010` empty + D1–D8. |
| `L20` lockstep | A9 | review | A9/L20 | Land §2 CI hardening + §3 paired-PR policy; §4 → L3. |
| `L15` Cluster | A1 (existence only) | review (unchanged) | TBD | A1 verified client/server/lease/versioning exist; **no hardening report** — needs the cluster agent (A7 missing). |
| `L2`,`L6`,`L7`,`L8`,`L10`,`L11`,`L13`,`L14` | — | unchanged | CAP/IO/RT/UI/PROV specs | Not covered by this report set (see Uncovered). |

---

## Uncovered (no report in this set addresses these — confirmed)

- **`LOCK-CAP` / `L2` / `L10`** — capability vocabulary spec. Prereq for L10/L11/L12/L13 + the manifest `capabilities` enum A4 depends on. **No report.**
- **`LOCK-RT` / `L10`** — common runtime API. A4 (Studio endpoint) and L12/L15 wait on it. **No report.**
- **`LOCK-IO` / `L6` / `L7` / `L8`** — `DatasetSpec v2`/`DatasetPackage`; formats/readers MVP. A4 `data_requirements` ports + A9 lockstep surface both blocked on it. **No report** (A9 only flags it as a dependency).
- **`LOCK-UI` / `L11` / `L13`** — Studio-first UI taxonomy + Web/WASM subset. **A6 FAILED**; A4 §5.2 notes the WASM controller gap but does not spec UI.
- **`L14` PROV / `DEC-PROV-001`** — datasets/repository/benchmarks/papers provider contracts. **No report.**
- **`L15` cluster hardening** — only existence verified (A1); RBAC/distributed==local parity unspecced. **A7 absent.**
- **`DEC-PROOF-001`** — first public multimodal reproducible case. **No report.**
- **`LOCK-GOV` acceptance, `LOCK-REL` schema** — drafted (A13/A9) but not ratifiable until maintainer P1.

---

## Recommended board changes for A0

1. **`LOCK-PYREF` keep `in_progress`; `B-009` CONFIRMED valid** (verified at `e41362b4`: `nirs4all/docs/compatibility.md` absent; `parity_oracle.v1.json` pins it `required_before_bridge:true` @ `1e-9`, enforced `_DEFAULT_SCORE_TOL/_YPRED_TOL = 1e-3`). Attach A2 §7 G1–G9 as sign conditions; `B-009`/BLK-PYREF-1 (ledger) is the gating one.
2. **Register new L17 sub-gaps as blockers** (A2 §9): `.n4a`+workspace cross-engine read/predict unproven, error/refusal parity unproven, methods-installed lane silently skips, Studio bypasses oracle. All `med`, owners L17+{L5,L9,L12}.
3. **`LOCK-DROP` keep `in_progress`; `B-010` CONFIRMED valid** — `EXPECTED_FALLBACK` is exactly 11 (4 `branch_dup_*`, 4 `multi_source_*`, 3 `preprocessing_*`, verified lines 310–326). Both A2 and A3 agree owner = **L5/A3** (host-bridge serialization). Add D1–D8 sequence (A2 §8) as the cutover gate.
4. **RETIRE `B-CTRL-1` — STALE.** A4 was written when `A3_A3-dagml.md` was empty; A3 now exists (18 KB) with the runtime/coverage matrix and agrees with A4 on the 11-case native/fallback boundary. Mark A4↔A3 reconciled; do not register B-CTRL-1.
5. **Register `B-CTRL-2`** (A4): representation IDs absent (`dag-ml-data`/L6/L7) block manifest `data_requirements` ports beyond `tabular_numeric`.
6. **`L16`/DEC-CTRL: add proposed `DEC-CTRL-002..007`** (A4 §6): kind-level generic controllers + selector specializations; keyword→`operator_kind` decided at COMPILE (lowering, not selector); `transport`/`runtime_requirements`/`conformance_fixtures` = versioned **sidecar** (no schema bump); hard-error ambiguity via `metadata.controller_id`; author-declared `rng_policy`/`artifact_policy`; Studio = manifest + product-overlay. Verified: `controller_manifests()` is 5 hand-authored dict manifests, no `OperatorController→ControllerManifest` class adapter yet.
7. **`L9` methods: add a methods-installed CI gate blocker** — verified `test_n4m_ops.py:29` is `importorskip("n4m")` and nirs4all has **no** `nirs4all-methods` dep in `requirements-test.txt`/`pyproject.toml`, so methods parity silently skips. Adopt A5 recommendation: V1 sklearn-host + required methods-installed job; direct n4m controller = V1.1/V2 (ARB-003=A already accepted).
8. **`LOCK-LOCKSTEP` keep `landed` but record residual gaps** (A9): Gap-4 (paired-PR merge deadlock — sibling checkout no `ref:`) is **high** and must be fixed before any coordinated `docs/contracts/` change; Gap-3 (silent-skip). Add `--require-sibling` + paired-branch CI; refine DEC-LOCKSTEP-001 text per A9 §6. `B-008` stays resolved; residual = §4 release lockfile (L3).
9. **`L3`/`LOCK-REL`: adopt A13 + A9 §4 field schemas** into a DEC-REL-001 draft (members commit/tag/version/header_sha256; shared_contracts normalized digests; `c_abi` block; `equivalence_attestation`; pin `AGGREGATION_INTEROP.md` hashes to close A9 Gap-2). Consumes conformance-pack hashes — matches accepted direction.
10. **`L1`/`L4`/`LOCK-GOV`: keep blocked on maintainer P1.** A13 delivered DEC-GOV-001/002 drafts; confirmed no `nirs4all-core` checkout exists. Apply A13's `RELEASE_DISTRIBUTION_INVENTORY.md` diff (lite 0.2.0 surface; "temporary integration clone, non-releaseable").
11. **`L18`/`LOCK-MIG` keep blocked.** DEC-MIG-001 accepted but A8's 10 sub-blockers (target schema, manifest/report/checksum/id-map vocab, score mapping, pipeline lowering) are unaccepted. Adopt A8's no-in-place CLI + Studio non-mutating `GET /workspace/legacy-status` detector (stop in-process migration).
12. **`L12` Studio: add BACKEND_RULES-violation extraction targets** (A2 PYREF-008): `api/transfer.py`, `api/predict.py` (metrics + CSV/Excel read), `api/analysis.py` re-implement nirs4all logic outside the oracle; Studio never passes/records `engine=`. Tag as L17↔L12 overlap + DROP-D5 gap.
13. **Fix board self-inconsistency:** PRE-3 row (line 40) still reads "LOCK-PYREF signe" while the Locks table + worklog correctly downgraded it to `in_progress` with `B-009`. Reconcile the PRE-3 note.
14. **Add an oracle-green caveat:** the "273/0 dual-engine green / 11 xfail" numbers are ADR-17's on branch `core/dagml`, **not** re-verified on `main@e41362b4` (suite won't collect — `tests/conftest.py` imports `matplotlib`, absent in `.venv`; confirmed by A2 §10 and A5). Add `matplotlib` to `.venv` and re-run full PYREF on `main` before treating oracle-green as fact for L17/L19 claims.
15. **Confirm Uncovered → schedule spec agents:** `LOCK-CAP`, `LOCK-RT`, `LOCK-IO`, `LOCK-UI`, `L14` PROV, `L15` cluster-hardening, `DEC-PROOF-001` have **no report**. CAP+RT+IO+UI are the prereqs that unblock most impl lanes — prioritize.
16. **PRE gates: A1 ratifies all 6 critical claims** at current heads (no new blockers); adopt A1 §"Gates to ratify" as the PRE-1/2/3 re-ratification command set.

---

## Stale claims (light verification)

- **A4 premise "`A3_A3-dagml.md` is empty (Codex `gpt-5-codex` failure)" — STALE.** A3 now exists (18,360 bytes) with the L5 runtime flow + coverage/fallback matrix; A4's `B-CTRL-1` blocker is therefore resolved. A3 and A4 independently agree on the 11 `EXPECTED_FALLBACK` cases.
- **A2-reported stale doc:** dag-ml `docs/migration-nirs4all/PARITY_AND_PERF_HARNESS.md` still says "~35 cases"; actual corpus is 95 (A2 §1). A2's flag, file-anchored; not board-blocking.
- **Board internal staleness (not a report claim):** PRE-3 note "LOCK-PYREF signe" contradicts the in_progress lock state + B-009 (see rec #13).
- **Everything else verified TRUE at current heads:** repo heads (3/3 match), `DEFAULT_ENGINE="legacy"` (engine.py:29), `compatibility.md` missing, `parity_oracle.v1.json` `1e-9`/ledger pins, `1e-3` enforced tolerances, `EXPECTED_FALLBACK`=11, `importorskip("n4m")` + no methods CI dep, `controller_manifests()` 5 dict manifests / no class adapter, `validate_contracts.py` present both sides.
- **Caveat (unverified, not stale):** oracle "all-green" numbers are ADR-17/`core/dagml`, not re-run on `main` (rec #14).
