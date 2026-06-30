# RV10 — Next-wave implementation plan (Wave-2B)

**Agent:** RV10 (planning reviewer) · **Date:** 2026-07-01 · **Mode:** read-only audit → next-wave plan. **This file is the only write.** No source edited, nothing staged/unstaged/committed.
**Scope:** the implementation wave *after* the currently staged Wave-2A lanes. Plans concrete agents + cwd/worktree strategy + prompts + prerequisites + validation gates for `B-010`, `B-011`, `B-014`, `B-017`, `B-018` and the `L4`/`L14`/`L19` dependencies.
**Method:** direct `git worktree list`/`status`/`log`, `Read`/`Grep` on live heads + the sync board (`PARALLEL_REFACTORING_SYNC.md`) and the prior reports (`A2`, `A3`, `SW5`, `SW8`, `IMP_L6`, `IMP_L12`, `IMP_L14`, `IMP_L16`). Not CodeGraph-only. Every `path:line` is inherited from a report that verified it in-tree or re-checked here.

---

## 0. TL;DR

1. **The staged Wave-2A work is uncommitted.** Every lane branch tip still equals its base commit (`nirs4all refactor/L17-pyref` → `e41362b4`; `dag-ml refactor/{L16,L20}` → `f58d7bf`; `dag-ml-data refactor/{L6,L20}` → `347c15f`). The slices live only in each checkout's **index/working tree**. A worktree branched today would therefore **miss** the staged work. → **PRE-W2a (commit the staged slices) is the single load-bearing prerequisite of this wave.**
2. **Wave-2B = 10 fresh worktrees, never the occupied checkouts.** Each agent gets `_worktrees/W<n>-<repo>` on a new `refactor/W<n>-*` branch off the *committed* base lane branch. No agent touches `nirs4all/`, `dag-ml/`, `dag-ml-data/`, `nirs4all-io/` (staged main checkouts) or the existing `_worktrees/L*` (staged slices).
3. **The wave closes the `LOCK-DROP`/`L19` critical path:** `B-010` (EXPECTED_FALLBACK→0, 3 agents), `B-011` (LOCK-PYREF final sign, 1), `B-018` (explicit RtError, 3), `B-017` (Studio engine routing + manifests, folded into the L12 agent), `B-014` (representation lockstep + data_requirements, 2). Plus `L14` providers (1, independent) and `L4` lite→core as the optional bench lane. `L19` itself is the **terminal gate**, not an agent.
4. **Three shared files force section-ownership discipline** (the only real overlap hazards): `nirs4all/docs/compatibility.json` (W1/W2/W4 own disjoint keys), `nirs4all/api/result.py` (W3 export methods vs W7 `to_rt_result`), `dag-ml/scripts/validate_contracts.py` (single-owner = W5). Matrix in §6.

---

## 1. Current-state ground truth (the staged diffs to avoid)

Heads re-verified 2026-07-01 (`git worktree list` / `status --short` / `log -1`):

| Repo / checkout | Branch | Committed tip | Staged (uncommitted) diff | Wave-2A lane |
|---|---|---|---|---|
| `nirs4all/` (main checkout) | `refactor/L17-pyref` | `e41362b4` (== `main`, tag `dagml-adr17-complete-2026-06-30`) | 8 files: `compatibility.{md,json}`, `_authority.py`, `test_compatibility_ledger.py`, `test_conformance_export_roundtrip.py`, `pyproject.toml` (+matplotlib), `methods-installed.yml`, `test_n4m_ops.py` | L17 (B-009/B-013/B-015 + B-011 export slice) |
| `dag-ml/` (main checkout) | `refactor/L20-lockstep` | `f58d7bf` | `ci.yml`, `scripts/validate_contracts.py` | L20 lockstep |
| `dag-ml-data/` (main checkout) | `refactor/L20-lockstep` | `347c15f` | `ci.yml`, `scripts/validate_contracts.py` | L20 lockstep |
| `nirs4all-io/` (main checkout) | `refactor/L7-io-dagml-sibling` | `84ab189` | 8 files (cli, dagml crate, CI, docs) | L7 |
| `_worktrees/L6-dmd-registry` | `refactor/L6-dmd-registry` | `347c15f` | `representation_registry.{rs,v1.json}`, `lib.rs`, cli `main.rs`, docs | L6 (B-014 slice 1) |
| `_worktrees/L11-studio-ui` | `refactor/L11-ui-vm` | `2ccbf68` | `src/ui/score/*` | L11 |
| `_worktrees/L12-studio-runtime` | `refactor/L12-runtime-routes` | `2ccbf68` | `api/runtime_errors.py`, `execution_driver.py`, `runs.py`, tests | L12 (B-018 RtError envelope) |
| `_worktrees/L13-web-rt` | `refactor/L13-web-rt` | `745eef8` | web `RtError` TS, engine tests | L13 (B-018 web) |
| `_worktrees/L15-cluster-rbac` | `refactor/L15-rbac` | `dcced30` | RBAC | L15 |
| `_worktrees/L16-dagml-controllers` | `refactor/L16-controller-manifests` | `f58d7bf` | `controller_adapter.rs`, `lib.rs` | L16 (B-014 adapter foundation) |

Clean (pristine) checkouts available as fresh bases: `nirs4all-studio/ main 2ccbf68`, `nirs4all-web/ main 745eef8`, `nirs4all-lite/ main`, `nirs4all-cluster/ main dcced30`, `nirs4all-tools/ main`.

**Consequence for branching (verified):** `git log -1 refactor/L17-pyref` == `e41362b4` and `git log -1 refactor/L20-lockstep` == `f58d7bf`/`347c15f` — i.e. the committed tip is the base; the slice is index-only. `git worktree add <new> refactor/L17-pyref` would check out `e41362b4` **without** `compatibility.json`/`_authority.py`/the matplotlib pin. The staged `pyproject.toml` (verified: `+"matplotlib>=3.7.0"`) is the B-013 collection fix — a Wave-2B nirs4all agent only inherits a *collectable* parity suite if it branches from a **committed** L17.

---

## 2. Per-blocker remaining work + next actions

### B-010 — EXPECTED_FALLBACK elimination (LOCK-DROP D1). Owner L5.
**State:** `EXPECTED_FALLBACK` = 11 exact cases (`test_conformance_dual_engine.py:310-326`): 4 `branch_dup_*`, 4 `multi_source_*`, 3 `preprocessing_*` (`A3` §"Current Expected Legacy Fallbacks"). `run(engine="dag-ml")` is opt-in; only `DagMlUnavailable/Unsupported/NotImplementedError` fall back (`run.py:570-620`). The **Rust `dag-ml-core` runtime already owns** scheduler/folds/OOF/merge/scoring/selection and even `proba_mean` reducers; the gap is the **Python host bridge serialization** in `pipeline/dagml/{detect,run_paths,run_backend}.py` (`A3` §Coverage matrix). `.n4a` export still delegates to a legacy refit bridge (`A3` §8 / `api/result.py`).
**Next actions (A3 work-breakdown):** DML-003 coverage meter (measure the count per PR); DML-002 native lowering of the 3 families; DML-008 native `.n4a` export. → **W1 (meter), W2 (lowering), W3 (export).**

### B-011 — workspace/artifact + Studio-bypass parity (LOCK-PYREF final sign). Owner L17 (+L5/L9/L12).
**State:** L17 slice landed locally (staged): `RunResult.export()` refuses `source=`/`chain_id=` on dag-ml + `NotImplementedError` for no-workspace export (`test_conformance_export_roundtrip.py`). **Remaining (SW5 §6):** (a) `.n4a` cross-engine round-trip `test_conformance_n4a_cross_engine.py` (band `cross_impl_ypred` 1e-3); (b) workspace cross-engine read/predict test (legacy workspace inspectable via runtime path; native triple → same `RtResult`); (c) error-parity `test_conformance_error_parity.py` (same invalid pipeline → both engines raise; dag-ml maps to stable `RtError.cause`); (d) Studio rides the oracle (engine-record + dual smoke — the Studio half is W8). Plus G3 one-entry command, G8 nirs4all-side `.so`/wheel freshness gate, ledger `§D` rows. → **W4** (nirs4all parity tests + freshness + bands), Studio half → **W8**.

### B-014 — representation registry lockstep + L16 data_requirements. Owner L6/L7/L20 + L16.
**State:** `representation_registry.v1.json` (26 frozen IDs, 8 emitted + 4 image `landed_pending_emit`) published + drift-tested in the L6 worktree (`IMP_L6`), **staged, not committed**. Deliberately **not** wired into `conformance_pack.v1.json`/`validate_contracts.py` (that is a lockstep change needing a simultaneous `dag-ml` edit — `IMP_L6` §5). L16 `controller_adapter.rs` accepts a `data_requirements` JSON override but ports stay coarse `tabular_numeric` (`IMP_L16` §7, blocked on B-014). → **W5** (conformance-pack lockstep wiring across `dag-ml`+`dag-ml-data`), **W6** (L16 ports → frozen representation strings).

### B-017 — Studio compute push-down. Owner L12 (+L5/L16).
**State:** compute trapped in Studio FastAPI: `analysis.py` (31.6K, 100% trapped PCA/tSNE/UMAP/perm-importance), `metrics_computer.py` (29.1K, ~80% descriptors), `playground/*`, `predict.py` metric re-roll, `transfer.py` (hand-chained SNV/MSC/SG). **SW8 splits this:** V1 = route run/predict (thread+record `engine=`) + kill `predict.py:114-122` metric re-roll (→`eval_multi`) + `GET /api/operators/manifests`; the **deep math push-down is Wave-4** (`SW8` §4.B, couples L5/L16/north-star) — *out of scope for Wave-2B*. → **W8** does the V1 routable half; the deep push-down is explicitly deferred (§10).

### B-018 — remaining Python/runtime schema/golden pieces. Owner L10 (+L12/L13).
**State:** L12 (staged) + L13 (staged) already expose `RtError` envelopes at the Studio-driver and Web layers (`IMP_L12`, `IMP_L13`). **Remaining (SW8 §2/§5/§7):** the runtime envelopes proper — new `nirs4all/pipeline/dagml/rt.py` (`RtResult`/`RtRunRequest`/`RtError` + `from_native_dir`/`from_run_result`/`from_dagml_error`), additive `RunResult.to_rt_result()`, ecosystem `docs/contracts/runtime/*.schema.json` (dir does **not** exist yet — only `docs/contracts/release/`), Python `run.py` warn+fallback → structured `RtError` diagnostic + `allow_fallback=False` raise, and the shared/golden schema tests. → **W7** (runtime envelopes + Python fallback + ecosystem schema), with Web smoke completion in **W9**.

### L4 — core aggregate (lite→`nirs4all-core`). `review`, owner TBD.
**State:** `LOCK-GOV` + `LOCK-REL` landed (unblocked); `nirs4all-lite` clean, **no `nirs4all-core`/`n4a.*` refs yet** (re-grepped: 0). Implement the `lite → nirs4all-core` aggregate + additive `n4a.*` facade + explicit distributions (`DEC-GOV-002`). **Independent of the cutover critical path.** → optional bench lane **W11** (or defer to Wave-2C).

### L14 — providers/plugins. `review`, owner SW6/IMP-L14. `DEC-PROV-001` still **proposed**.
**State:** all 4 provider repos clean; no provider class/registry anywhere (`IMP_L14` §0). Slice-1 read adapters need **no decision** and no `LOCK-IO`/`RT`/`UI` dep (`IMP_L14` §0/§3c). Hazard: a client layer hard-depending on providers creates an install cycle → standalone dependency-light `nirs4all-providers` package, soft-imports (`IMP_L14` §1, decision D1). → **W10** (scaffold + datasets/repository read adapters). `to_dataset_package`/publish/benchmark-runner stay deferred.

### L19 — cutover legacy-DROP. `blocked`. **Terminal gate — not staffed this wave.**
Flip `DEFAULT_ENGINE="dag-ml"` only when **all** of: `coverage_meter.fallback==0` (B-010/W1+W2), native `.n4a` export (DML-008/W3), 3-tier oracle green **on main** incl. cross-engine (B-011/W4), Studio+Web on runtime route w/ explicit fallback (B-017/B-018/W7+W8+W9), migration tool preview (L18, landed). Wave-2B *feeds* this gate; L19 executes after a green PYREF-on-main (A2 §8 D8). Criteria restated in §11.

---

## 3. Prerequisites & gating decisions

| ID | Prerequisite | Why / blocks | Owner |
|---|---|---|---|
| **PRE-W2a** | **Commit each staged Wave-2A slice** on its lane branch (the 4 main checkouts + 6 worktrees in §1). | Worktrees branch from *committed* tips; uncommitted index work is invisible to a new worktree. Hard blocker for W2/W3/W4/W7 (need L17 ledger+matplotlib), W5 (needs L6 manifest + L20 validator), W6 (needs L16 adapter), W8 (needs L12 envelope), W9 (needs L13). | maintainer |
| **PRE-W2b** | Confirm each base `.venv`/toolchain: nirs4all `.venv` has `matplotlib` (rides committed L17 `pyproject.toml`); studio `.venv` has fastapi/pydantic (`IMP_L12` §4); dag-ml rust toolchain + maturin for `.so` rebuild. | Parity suite collection (B-013), studio backend tests, `.so` freshness. | maintainer/agents |
| **PRE-W2c** | CAP-004 cause/mitigation/`portable_level` vocab frozen enough to consume (drafted in `CAP_spec.md` §5; carried by L12/L13 staged). | W7/W8/W9 *carry* the vocab, never invent it. | L2/CAP |
| DEC-PROV-001 | Still `proposed`. Slice-1 read adapters proceed **without** it (read-only, no write path). Full provider sign waits. | gates W10 *full* completion, not slice-1. | maintainer |
| LOCK-LOCKSTEP | Active. Any `dag-ml`↔`dag-ml-data` shared-contract change = paired branch + `validate_contracts.py --require-sibling` green both sides. | governs W5 (and any dag-ml contract W6 touches). | L20 |
| B-016 (UI primitive a-vs-c) | Open, but Wave-0/1 UI is independent (`A6`); **does not block** any Wave-2B agent. | n/a this wave. | maintainer |

---

## 4. Next-wave agent roster (10 agents)

Naming: `W<n>`. Each runs in its **own** worktree, edits its **owned files only** (§6), ends on its repo's **green gate** (§9), and writes one report `docs/agent_reports/W<n>_*.md` (never edits the board or another report). Default agent model: Opus, effort high for the heavy lowering/export/lockstep lanes (W2/W3/W5), medium otherwise.

| # | Lane | Blocker | Repo(s) | Base branch (committed) | Worktree | Weight |
|---|---|---|---|---|---|---|
| **W1** | L5 meter | B-010 (DML-003) | `nirs4all` | `refactor/L17-pyref` | `_worktrees/W1-nirs4all` | S |
| **W2** | L5 native lowering | B-010 (DML-002) | `nirs4all` | `refactor/L17-pyref` | `_worktrees/W2-nirs4all` | **XL** |
| **W3** | L5 native export | B-010 (DML-008) | `nirs4all` + `dag-ml` | `refactor/L17-pyref` / `f58d7bf` | `_worktrees/W3-nirs4all`, `_worktrees/W3-dagml` | **L** |
| **W4** | L17 cross-engine | B-011 | `nirs4all` | `refactor/L17-pyref` | `_worktrees/W4-nirs4all` | L |
| **W5** | L6+L20 contracts | B-014a | `dag-ml-data` + `dag-ml` | `refactor/L6-dmd-registry` / `refactor/L20-lockstep` | `_worktrees/W5-dmd`, `_worktrees/W5-dagml` | L |
| **W6** | L16 data_requirements | B-014b | `dag-ml` | `refactor/L16-controller-manifests` | `_worktrees/W6-dagml` | M |
| **W7** | L10 runtime envelopes | B-018 | `nirs4all` + `nirs4all-ecosystem` | `refactor/L17-pyref` / ecosystem `docs/` | `_worktrees/W7-nirs4all` | L |
| **W8** | L12 Studio routing | B-017(V1)+B-018 | `nirs4all-studio` | `refactor/L12-runtime-routes` | `_worktrees/W8-studio` | L |
| **W9** | L13 Web RtError | B-018 | `nirs4all-web` | `refactor/L13-web-rt` | `_worktrees/W9-web` | M |
| **W10** | L14 providers | (L14) | `nirs4all-providers` (new pkg) | new repo `main` | n/a (fresh repo) | M |
| *W11 (bench)* | L4 aggregate | (L4) | `nirs4all-lite` | `main` | `_worktrees/W11-lite` | M |

### Prompt sketches

> **W1 — fallback coverage meter (DML-003).** cwd `_worktrees/W1-nirs4all` (branch `refactor/W1-fallback-meter` off committed `refactor/L17-pyref`). Build the PYREF native-vs-fallback **meter** per `A3` §DML-003 + `SW5` §5: a runner that classifies each parity case (native / Python-expanded / Python-pre-materialized / legacy-fallback / xfail / skip) and emits machine-readable JSON + a short markdown summary (total/runnable/native/fallback/expected-fallback/unexpected). Populate **only** `compatibility.json.coverage_meter` (your owned key). Keep `test_native_fallback_boundary` green; make the fallback count visible in CI. ONLY add new files under `tests/integration/parity/` + the `coverage_meter` key; do NOT touch `detect.py`/`run_paths.py`/lowering or other ledger sections. Gate: `pytest tests/integration/parity/test_native_fallback_boundary.py -q` + your meter test + ruff. Report `W1_meter.md`.

> **W2 — native fallback coverage (DML-002, the 11 cases).** cwd `_worktrees/W2-nirs4all` (branch `refactor/W2-fallback-native` off committed `refactor/L17-pyref`). Migrate the host-bridge serialization so the 11 `EXPECTED_FALLBACK` shapes run **native** dag-ml instead of legacy: 4 `branch_dup_*` (merge predictions/features, named+metamodel, merge-all), 4 `multi_source_*` (by-source shared/distinct preproc, per-source stacking, sources-concat→rf), 3 `preprocessing_*` (explicit keyword, fit_on_all, force_layout_2d). Own `nirs4all/pipeline/dagml/{detect.py,run_paths.py,run_backend.py}` lowering + the `EXPECTED_FALLBACK` allowlist + `compatibility.json.expected_fallback` rows (your owned key). The Rust runtime already supports the mechanics (`A3` matrix: merge reassembly, `proba_mean` reducers exist) — your job is Python lowering/dispatch. If a genuine dag-ml-core gap appears, STOP and file a DEC for a dag-ml worktree (coordinate W3/W6) — do NOT edit `dag-ml` from here. Each shrink of the frozenset must mirror into `compatibility.json.expected_fallback` (the `test_compatibility_ledger` snapshot enforces equality). Gate: full `pytest tests/integration/parity/ -m parity -q` (XPASS on strict-xfail = RED; boundary green) + ruff. Report `W2_native_fallback.md`.

> **W3 — native `.n4a` export (DML-008).** cwds `_worktrees/W3-nirs4all` (off committed `refactor/L17-pyref`) + `_worktrees/W3-dagml` (off `dag-ml` `f58d7bf`). Replace the legacy-refit `.n4a` bridge with a **native** bundle export from `ScoreSet` + selected variant + graph/DSL + fold set + manifest + captured artifact refs (`A3` §DML-008): support multi-artifact (branches/stacking), content-fingerprint replay validation, keep legacy export only as explicit compat mode. Own nirs4all `api/result.py` **export/export_model methods only** (NOT `to_rt_result` — that is W7) + `pipeline/dagml/native_results.py` export side + the dag-ml native bundle export surface (`crates/dag-ml-core`, new module). Rebuild + commit `_dag_ml.abi3.so` at landing (B-L16-1 gotcha). Gate: nirs4all `pytest tests/integration/parity/test_conformance_export_roundtrip.py tests/integration/parity/test_dagml_native_export_model.py -q`; dag-ml `cargo fmt --check && clippy -D warnings && cargo test --workspace && check_so_freshness.py`. Coordinate `api/result.py` method-level ownership with W7. Report `W3_native_export.md`.

> **W4 — cross-engine parity + freshness (B-011).** cwd `_worktrees/W4-nirs4all` (off committed `refactor/L17-pyref`). Add the three missing cross-engine surfaces (`SW5` §6): `test_conformance_n4a_cross_engine.py` (legacy-written `.n4a` predicts via runtime path & reverse, band `cross_impl_ypred`), workspace cross-engine test (legacy workspace inspectable via runtime; native triple → same `RtResult` projection), `test_conformance_error_parity.py` (same invalid pipeline → both engines raise; dag-ml refusal → stable `RtError.cause`, vocab from CAP-004 / consume W7's classifier). Add the nirs4all-side wheel/`.so` freshness gate under `scripts/` (assert installed `dag_ml`/`n4m` satisfy pins; invoke sibling `check_so_freshness.py` when present) + a one-entry `make parity` command (G3). Own `compatibility.json` **`tolerance_bands[]` + `authority[]` + cross-engine `§D`** keys + `compatibility.md` band tables + `_authority.py` bands. Do NOT touch `expected_fallback`/`coverage_meter` (W1/W2). Gate: the 3 new tests + `test_compatibility_ledger` + ruff. Report `W4_cross_engine.md`. (The paired `dag-ml/parity_oracle.v1.json` tolerance-profile amendment is W5's, reading your band names.)

> **W5 — representation-registry + parity-profile lockstep (B-014a).** cwds `_worktrees/W5-dmd` (off committed `refactor/L6-dmd-registry`) + `_worktrees/W5-dagml` (off committed `refactor/L20-lockstep`). Two paired-contract slices, both LOCK-LOCKSTEP: (1) wire `representation_registry.v1.json` into the `dag-ml`↔`dag-ml-data` `conformance_pack` + `validate_contracts.py` digest path so the frozen 26-ID list is a CI-gated shared contract (`IMP_L6` §5); (2) amend `dag-ml/docs/contracts/parity_oracle.v1.json` to replace the mislabeled `1e-9` default with explicit profiles (`regression.cross_impl`=1e-3, `regression.kernel`=1e-9, `regression.native_export`=1e-6, `classification.default`=0) and extend `validate_contracts.py` to assert `parity_oracle profiles ⊆ nirs4all compatibility.json.tolerance_bands` (`SW5` §3b/§9a tier-4 — read W4's band names; do not invent). **Single-owner of `dag-ml/scripts/validate_contracts.py` this wave.** Commit/push the paired branch in BOTH repos; gate: `validate_contracts.py --require-sibling --sibling-root ../<sibling>` green both sides + `cargo test --workspace`. Report `W5_contracts_lockstep.md`. (Slice 2 soft-depends on W4 bands; slice 1 only on committed L6.)

> **W6 — L16 `data_requirements` ports (B-014b).** cwd `_worktrees/W6-dagml` (off committed `refactor/L16-controller-manifests`). Wire `ControllerManifest` data/target ports from coarse `tabular_numeric` to the **frozen representation strings** now published by the registry (`IMP_L16` §7, B-014). Extend `manifest_kind_template` / `HostControllerSpec.derive()` so `data_requirements` carries real representation IDs validated as `ModelInputSpec`; keep the 6 existing parity mappings green. Own `crates/dag-ml-core/src/controller_adapter.rs` only (NOT `validate_contracts.py` — W5; NOT export — W3). Rebuild+commit `.so` at landing. Soft-depends on W5 slice-1 (the shared registry contract). Gate: `cargo fmt --check && clippy -D warnings && cargo test -p dag-ml-core controller_adapter && cargo test --workspace && validate_contracts.py && check_so_freshness.py`. Report `W6_data_requirements.md`.

> **W7 — runtime envelopes + explicit Python fallback (B-018/L10).** cwd `_worktrees/W7-nirs4all` (off committed `refactor/L17-pyref`) + ecosystem `docs/`. Build the runtime envelope per `SW8` §2/§5: new `nirs4all/pipeline/dagml/rt.py` (`RtResult`/`RtRunRequest`/`RtError` + `from_native_dir`/`from_run_result`/`from_dagml_error` classifier, pure projection, no recompute); additive `RunResult.to_rt_result()` in `api/result.py` (**method-level coordinate with W3**) + public `nirs4all.runtime.list_controller_manifests()` accessor over `dagml_bridge.controller_manifests()` (so W8/Studio never imports the private bridge); `api/run.py` warn+fallback (`:606-618`) → attach structured `RtError` diagnostic + add `allow_fallback=False` that RAISES `RtError` (opt-in; legacy stays default per LOCK-DROP); ecosystem **new** `docs/contracts/runtime/{rt_result,rt_run_request,rt_error}.v1.schema.json` (`$ref` dag-ml `score_set`/`selection_decision`; cause vocab = CAP-004). No `RunResult`/native-format/`.n4a` change. Gate: rt.py unit tests + `allow_fallback=False` raises on each of the 11 EXPECTED_FALLBACK fixtures + schema `json.tool` + ruff. Report `W7_rt_envelopes.md`.

> **W8 — Studio engine routing + manifests + metric reroute (B-017 V1 + B-018).** cwd `_worktrees/W8-studio` (off committed `refactor/L12-runtime-routes`). Per `SW8` §3+§4.A: thread `engine=` through `runs.py:1431`/`training.py:466`/`automl.py:903`/`predict.py:81,89` and **persist the engine that actually ran** (incl. fallback) on the run record + surface it + `RtResult.diagnostics` on the read models; reroute `predict.py:114-122` metric re-roll → `nirs4all.core.metrics.eval_multi`; add thin `GET /api/operators/manifests` over W7's `nirs4all.runtime.list_controller_manifests()` (+ no-drift test vs `controller_manifest.v1.schema.json`); node-registry overlay keyed by `controller_id`. **Do NOT** attempt the deep `analysis.py`/`metrics_computer.py` push-down (Wave-4). Keep `execution_backend` orthogonal to `engine`. Soft-depends W7 (manifest accessor) — until W7 lands, stub the accessor import behind a feature guard. Gate: studio dual-engine route-parity test + engine-recorded assertion + manifest-no-drift + `predict` metrics==`eval_multi` + `npm run validate:nodes` + tsc + targeted pytest (studio `.venv`). Report `W8_studio_routing.md`.

> **W9 — Web RtError surfacing + forced-failure smoke (B-018).** cwd `_worktrees/W9-web` (off committed `refactor/L13-web-rt`). Finish the Web half: convert the silent campaign-phase catch (`dagml-engine.ts:520-534`) into an emitted `RtError` (UI-surfaced) with fallback behind an explicit `allowFallback` opt-in mirroring W7; wrap `guard.ts:44-49`/`orchestrate.ts:316-322` swallows in `RtError` diagnostics; add the browser smoke that forces a scheduler failure and asserts the `RtError` chip + offline JS-orchestrator diagnostics. Own `nirs4all-web/studio-lite/src/engine/*` only. Gate: `engine.test.ts`/`dagml.test.ts` RtError cases + full unit suite + typecheck + build + browser smoke. Report `W9_web_rt.md`.

> **W10 — providers scaffold + read adapters (L14).** Create the standalone dependency-light `nirs4all-providers` package (new sibling repo/pkg, like `nirs4all-tools`) per `IMP_L14` §1/§3/§4: `base.py` (`ProviderPlugin` Protocol), `registry.py` (soft-import discovery), `datasets.py` (`DatasetProvider`: `list_datasets`/`card`/`get_dataset`/`to_spectro_dataset`), `repository.py` (`PipelineProvider`: `list_pipelines`/`card`/`get_pipeline`/`get_bundle`/`verify`), `_softimport.py`. Soft-import each provider as an optional extra; degrade to `health()=unavailable` when absent; NO write path, NO `to_dataset_package`/publish/benchmark-runner (deferred, gated). Gate: `ruff check . && mypy src && pytest -q`. Report `W10_providers.md`.

> **W11 (bench/optional) — lite→core aggregate (L4).** cwd `_worktrees/W11-lite` (off `nirs4all-lite` main). Implement `nirs4all-lite → nirs4all-core` aggregate + additive `n4a.*` facade + explicit distributions per `DEC-GOV-002`/`LOCK-REL`. Off the cutover critical path — run only if capacity frees. Gate: lite build + R/py parity smokes. Report `W11_lite_core.md`.

---

## 5. Worktree / cwd strategy (exact)

**Rule 0 — never operate in an occupied checkout.** Forbidden cwds: `nirs4all/`, `dag-ml/`, `dag-ml-data/`, `nirs4all-io/` (staged main checkouts) and `_worktrees/L{6,11,12,13,15,16}-*` (staged slices). Every Wave-2B agent runs in a fresh `_worktrees/W*`.

**Step A — PRE-W2a, maintainer (NOT RV10, NOT the agents):** commit each staged slice on its lane branch so the tip advances past the base:
```bash
# main checkouts (already on the lane branch with the slice staged):
cd ~/nirs4all/nirs4all       && git commit -m "L17 slice: compatibility ledger + methods gate + export refusals"
cd ~/nirs4all/dag-ml         && git commit -m "L20 slice: lockstep validator + CI"
cd ~/nirs4all/dag-ml-data    && git commit -m "L20 slice: lockstep validator + CI"
# worktrees (already on their lane branch with the slice staged):
cd ~/nirs4all/_worktrees/L6-dmd-registry      && git commit -m "L6 slice: representation registry freeze/publish"
cd ~/nirs4all/_worktrees/L12-studio-runtime   && git commit -m "L12 slice: RtError envelope"
cd ~/nirs4all/_worktrees/L13-web-rt           && git commit -m "L13 slice: web RtError"
cd ~/nirs4all/_worktrees/L16-dagml-controllers&& git commit -m "L16 slice: controller_adapter foundation"
# (L11/L15 commit too if their Wave-2B consumers appear; not required by W1-W10)
```
After this, `git log -1 refactor/L17-pyref` advances past `e41362b4` and carries `compatibility.json`/`_authority.py`/the matplotlib pin — which every nirs4all Wave-2B worktree then inherits.

**Step B — create each Wave-2B worktree** from the *committed* base lane branch:
```bash
# nirs4all lanes (W1/W2/W3/W4/W7) — all off the committed L17 tip:
cd ~/nirs4all/nirs4all
git worktree add -b refactor/W1-fallback-meter   ~/nirs4all/_worktrees/W1-nirs4all  refactor/L17-pyref
git worktree add -b refactor/W2-fallback-native   ~/nirs4all/_worktrees/W2-nirs4all  refactor/L17-pyref
git worktree add -b refactor/W3-native-export     ~/nirs4all/_worktrees/W3-nirs4all  refactor/L17-pyref
git worktree add -b refactor/W4-cross-engine      ~/nirs4all/_worktrees/W4-nirs4all  refactor/L17-pyref
git worktree add -b refactor/W7-rt-envelopes      ~/nirs4all/_worktrees/W7-nirs4all  refactor/L17-pyref
# dag-ml lanes (W3/W5/W6) — distinct base branches:
cd ~/nirs4all/dag-ml
git worktree add -b refactor/W3-native-export-dagml ~/nirs4all/_worktrees/W3-dagml  f58d7bf
git worktree add -b refactor/W5-contracts-dagml     ~/nirs4all/_worktrees/W5-dagml  refactor/L20-lockstep
git worktree add -b refactor/W6-data-requirements   ~/nirs4all/_worktrees/W6-dagml  refactor/L16-controller-manifests
# dag-ml-data (W5):
cd ~/nirs4all/dag-ml-data
git worktree add -b refactor/W5-contracts-dmd       ~/nirs4all/_worktrees/W5-dmd    refactor/L6-dmd-registry
# studio / web / lite:
cd ~/nirs4all/nirs4all-studio && git worktree add -b refactor/W8-studio-routing ~/nirs4all/_worktrees/W8-studio refactor/L12-runtime-routes
cd ~/nirs4all/nirs4all-web    && git worktree add -b refactor/W9-web-rt         ~/nirs4all/_worktrees/W9-web    refactor/L13-web-rt
cd ~/nirs4all/nirs4all-lite   && git worktree add -b refactor/W11-lite-core     ~/nirs4all/_worktrees/W11-lite  main
# W10: fresh repo, no worktree (scaffold nirs4all-providers like nirs4all-tools).
```
Note: `git worktree add` reads refs/objects, not the source checkout's index — it works even though the main checkouts hold staged changes. The staged work is only *visible to the new worktree* because Step A committed it.

**Landing / lockstep order:**
- W5 is a **paired** commit/push (dag-ml + dag-ml-data) — land together, `validate_contracts.py --require-sibling` green both sides.
- dag-ml has 3 tenants (W3-dagml, W5-dagml, W6-dagml) on disjoint files but a single tracked `_dag_ml.abi3.so`: serialize their **landing** (rebuild+commit `.so` on whichever merges, re-rebuild on the next).
- nirs4all has 5 tenants (W1/W2/W3/W4/W7) sharing `compatibility.json` (section-partitioned) + `api/result.py` (W3/W7 method-partitioned): land W1 (coverage_meter) and W7 (rt seam) early, then W2/W4 (which co-edit the ledger), reconcile via `test_compatibility_ledger`.

---

## 6. Anti-overlap file-ownership matrix

Disjoint by file (or, for the 3 shared files, by section/method). The snapshot/contract tests are the safety net on the shared ledger.

| File / surface | Owner | Co-tenant rule |
|---|---|---|
| `nirs4all tests/integration/parity/` meter runner (new files) | W1 | new files only |
| `nirs4all pipeline/dagml/{detect,run_paths,run_backend}.py` + `EXPECTED_FALLBACK` allowlist | W2 | sole |
| `nirs4all api/result.py` **export/export_model** + `pipeline/dagml/native_results.py` (export) | W3 | method-partitioned vs W7 |
| `nirs4all tests/.../test_conformance_{n4a_cross_engine,error_parity}.py` + workspace test + `scripts/<freshness>.py` | W4 | new files |
| `nirs4all docs/compatibility.json` → `coverage_meter` | **W1** | section-owned |
| `nirs4all docs/compatibility.json` → `expected_fallback[]` | **W2** | section-owned (mirrors allowlist) |
| `nirs4all docs/compatibility.json` → `tolerance_bands[]`/`authority[]`/`§D` + `compatibility.md` + `_authority.py` bands | **W4** | section-owned |
| `nirs4all pipeline/dagml/rt.py` (new) + `api/run.py` fallback + `api/result.py` **to_rt_result** + `nirs4all.runtime` accessor | W7 | method-partitioned vs W3 |
| `nirs4all-ecosystem docs/contracts/runtime/*.schema.json` (new dir) | W7 | new |
| `dag-ml crates/dag-ml-core` **native bundle export** (new module) | W3 | disjoint from W6 |
| `dag-ml crates/dag-ml-core/src/controller_adapter.rs` | W6 | disjoint from W3 |
| `dag-ml scripts/validate_contracts.py` + `docs/contracts/{conformance_pack,parity_oracle}.v1.json` | **W5** | single-owner |
| `dag-ml-data` conformance-pack/registry wiring | W5 | sole |
| `dag-ml _dag_ml.abi3.so` | W3/W6 | serialize landing |
| `nirs4all-studio api/{runs,training,automl,predict}.py` + `/api/operators/manifests` + node registry | W8 | sole (consumes W7 accessor) |
| `nirs4all-web studio-lite/src/engine/*` | W9 | sole |
| `nirs4all-providers/*` (new pkg) | W10 | sole |
| `nirs4all-lite` aggregate | W11 | sole |

---

## 7. Dependency DAG / sequencing

```
PRE-W2a (commit staged slices)  ──►  PRE-W2b (envs)  ──►  all worktrees creatable
        │
        ├─ W1 (meter) ───────────────┐
        ├─ W2 (native lowering) ──────┼──► shrinks fallback ──► feeds L19 D1 (coverage_meter.fallback==0)
        ├─ W3 (native export) ────────┼──► feeds L19 D2 (native .n4a)
        ├─ W7 (rt.py + accessor + RtError classifier)
        │      └─ accessor ─► W8 (manifests)   └─ RtError.cause ─► W4 (error-parity)
        ├─ W4 (cross-engine tests + bands) ──► band names ─► W5 slice-2 (parity_oracle profiles)
        ├─ W5 slice-1 (repr registry lockstep, off committed L6) ──► shared contract ─► W6 (data_requirements)
        ├─ W6 (L16 ports)
        ├─ W8 (Studio engine record + dual smoke) ──► feeds B-011 §6d + L19 (Studio on route)
        ├─ W9 (Web RtError) ──► feeds L19 (Web on route)
        ├─ W10 (providers, independent)
        └─ W11 (lite→core, independent/bench)
                                   ▼
   LOCK-PYREF final sign (W2 mirror + W4 §6 + W8 §6d green on main)
                                   ▼
   L19 cutover gate (ALL of: fallback==0, native export, oracle green on main, Studio+Web on route, migration preview)
```
Hard deps: W6←W5(slice-1); W5(slice-2)←W4(bands); W8(manifests)←W7(accessor); W4(error-parity cause)←W7(classifier). Everything else parallel. W2 and W4 co-edit `compatibility.json` (different sections) — reconcile at land via the snapshot test.

---

## 8. Validation gates (per repo, run from the agent's worktree)

| Repo | Green gate |
|---|---|
| `nirs4all` | `.venv/bin/ruff check nirs4all tests` · `mypy` (changed) · targeted `pytest tests/integration/parity/... -p no:cacheprovider` · full `pytest tests/integration/parity/ -m parity -q` for W2/W4 (XPASS=RED; `test_native_fallback_boundary` green) |
| `dag-ml` / `dag-ml-data` | `cargo fmt --all --check` · `cargo clippy --workspace --all-targets -- -D warnings` · `cargo test --workspace` · `validate-graph examples/minimal_graph.json` · `python3 scripts/validate_contracts.py` (W5: `--require-sibling --sibling-root ../<sibling>`) · `python3 scripts/check_so_freshness.py` (W3/W6 after `.so` rebuild) |
| `nirs4all-studio` | `npm run validate:nodes` · `tsc --noEmit` · `vitest` (touched) · studio `.venv` `pytest` (targeted: dual-engine route parity, engine-recorded, manifest-no-drift, `predict`==`eval_multi`) · `ruff` |
| `nirs4all-web` | `tsc` · `vitest` (engine RtError) · `build` · browser forced-failure smoke |
| `nirs4all-providers` | `ruff check .` · `mypy src` · `pytest -q` |
| `nirs4all-lite` | lite build + R/py parity smokes |

Cross-cutting LOCK-PYREF sign (after W2/W4/W8 land, **on main** not `core/dagml`): SW5 §9b G1–G9 green; `LOCK-PYREF review→landed`. Cross-cutting LOCK-DROP: §11.

---

## 9. Risks & coordination notes

1. **PRE-W2a is non-negotiable.** Skipping it means W2/W3/W4/W7 silently branch from a *pre-ledger* nirs4all (no `compatibility.json`, parity suite uncollectable — matplotlib pin missing) and W5/W6 from a *pre-registry* dag-ml. The whole wave depends on it. RV10 cannot commit; flag to maintainer first.
2. **`compatibility.json` is a 3-tenant ledger** (W1/W2/W4). Section-ownership (`coverage_meter`/`expected_fallback`/`bands+authority+§D`) + `test_compatibility_ledger` snapshot is the guard. If the maintainer prefers serialization, land W1→W7→W2→W4.
3. **`api/result.py` 2-tenant** (W3 export vs W7 `to_rt_result`): different methods, but recommend W7 lands the additive seam first so W3 rebases onto it.
4. **dag-ml `.so` is a single tracked binary** across W3/W6: serialize landing + rebuild (B-L16-1). W5 is scripts/contracts-only (likely no `.so` touch).
5. **W2 must not edit dag-ml.** A3 says the Rust mechanics exist; if a real core gap surfaces (e.g. a merge variant truly unsupported), W2 files a DEC and hands a dag-ml worktree rather than reaching across the boundary (cross-cutting rule: lower layer is SoT, contracts via DEC).
6. **B-017 deep push-down is explicitly Wave-4, not here.** W8 does only the V1 routable half (engine thread/record + `predict` metric reroute + manifests). Do not let it expand into `analysis.py`/`metrics_computer.py` migration — that needs library homes that don't exist yet (`SW8` §4.B, A6 §7-8).
7. **DEC-PROV-001 still proposed** — W10 ships slice-1 read adapters only (no write/`to_dataset_package`); full provider sign waits on the maintainer.
8. **LOCK-LOCKSTEP** governs W5: paired branch in BOTH `dag-ml` and `dag-ml-data`, pushed together, `validate_contracts.py --require-sibling` green — else the contract-lockstep CI job fails the PR (`B-012` mechanism).
9. **Studio `engine` vs `execution_backend`** stay orthogonal (engine = ML engine legacy/dag-ml; backend = local-python/cluster/wasm-local). W8 must not overload one onto the other (`SW8` §1).

---

## 10. Explicitly out of scope this wave (deferred)

- **Wave-4 compute push-down (B-017 deep):** `analysis.py` (PCA/tSNE/UMAP/perm-importance), `metrics_computer.py` descriptors, `playground/*` mini-step-runner, `transfer.py` chains → migrate *down* into `nirs4all`/`dag-ml`/`io`, then expose as `analysis`/`inspect` RT verbs. Couples L5/L16/north-star; unblocks WASM portability.
- **CTRL-000 full adapter:** replace the static 5 kind-level manifests with the two-layer `OperatorController→ControllerManifest` per-operator projection (`A4` §2). W6 only enriches the *kind templates'* representation ports.
- **Published contracts package / `nirs4all/runtime/` namespace** → GOV/`LOCK-REL` (W7 ships ecosystem-schema + per-runtime mirrors only).
- **Providers write path / `to_dataset_package` / benchmark runner** → gated `LOCK-IO`/`LOCK-RT`/`DEC-PROV-001`.
- **L19 cutover execution** (next section).

---

## 11. L19 terminal gate (fed by this wave, executed after)

`DEFAULT_ENGINE="dag-ml"` flips only when ALL hold (`DEC-DROP-001`, `A2` §8, `SW5` §9):
1. `coverage_meter.fallback == 0` — `EXPECTED_FALLBACK` empty (**W1**+**W2**, B-010).
2. Native `.n4a` export (no legacy refit on the export path) — **W3** (DML-008).
3. 3-tier oracle green **on main** incl. the cross-engine surfaces (`.n4a`/workspace/error parity) — **W4** + `LOCK-PYREF` signed (B-011/B-013).
4. Studio + Web on the runtime route with explicit `RtError`/`allow_fallback` (no silent fallback) — **W7**+**W8**+**W9** (B-018), engine recorded (B-011 §6d).
5. Migration tool preview available — L18 `nirs4all-tools` (landed).
6. Cutover is a **paired** event: a nirs4all cutover tag succeeding `dagml-adr17-complete-2026-06-30` + the already-pushed dag-ml/dag-ml-data lockstep (sync board "Plan de merge par lane").

When 1–6 are green on main, L19 flips `DEFAULT_ENGINE` and removes the implicit `_run_legacy` fallback (or makes `allow_fallback=False` the default), then the dual-engine oracle layer is retired (A2 §8 D8).

---

### Evidence (read-only; only this file written)
Sync board `PARALLEL_REFACTORING_SYNC.md` (rows L4/L5/L6/L7/L10/L12/L13/L14/L16/L17/L19/L20; blockers B-010/B-011/B-014/B-016/B-017/B-018; locks). Reports `A2_A2-pyref.md`, `A3_A3-dagml.md`, `SW5_PYREF_COMPATIBILITY_LEDGER_spec.md`, `SW8_RT_STUDIO_IMPL_spec.md`, `IMP_L6_DMD_REGISTRY.md`, `IMP_L12_STUDIO_RUNTIME.md`, `IMP_L14_PROVIDERS_IMPL_PLAN.md`, `IMP_L16_CONTROLLER_MANIFESTS.md`. Live git: `git worktree list`/`status --short`/`log -1` on all repos (2026-07-01); `git diff --cached --stat` on nirs4all (8-file L17 slice incl. `+matplotlib>=3.7.0`); `ls docs/contracts/` (only `release/`, no `runtime/`); `ls nirs4all/scripts/`, `nirs4all/pipeline/dagml/` (no `rt.py`/`runtime/` yet); studio `api/{analysis,predict,transfer}.py`+`shared/metrics_computer.py` sizes (B-017 targets); `nirs4all-lite` (no `nirs4all-core`/`n4a.*` refs). Memory: parallel-refactoring-{p0-ratified,pyref,ctrl,a6-ui}.
