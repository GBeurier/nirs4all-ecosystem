# SW2 - LOCK-GOV Validation / Audit (governance, core topology, naming)

Date: 2026-06-30
Agent lane: SW2 (second wave), L1/L4 governance + naming + core topology
Mode: read-only audit + this report only. Sync board and code NOT edited.
Trigger: `LOCK-GOV` was signed by another coordinator (DEC-GOV-001 + DEC-GOV-002,
`ARB-013`/`ARB-014`=A) while SW2 was running. This report validates the signed
claims against the live tree instead of re-drafting the governance spec.

## Verdict: PASS WITH CONCERNS

The four structural GOV claims are technically coherent and verified against the
code. None is contradicted by the tree. But three of them are **target-state,
not shipping-state**, and the sync board currently reads as if they were already
realized. The board needs four short clarifying notes (Section 5) so L4/CORE and
the methods/Studio lanes do not treat "signed" as "implemented". No
decision needs to be reversed.

Heads audited (all clean, identical to A0 pass-2 base; audit base is current):
`nirs4all` e41362b4 · `nirs4all-lite` c14dcca · `nirs4all-methods` 7602eb08 ·
`nirs4all-formats` 89231b2 · `nirs4all-io` 84ab189 · `dag-ml` f58d7bf ·
`dag-ml-data` 347c15f · `nirs4all-studio` 2ccbf68 · `nirs4all-web` 745eef8.

## 1. Claim-by-claim verification

Signed text (sync board `LOCK-GOV` row): "clone `nirs4all-core` RETIRE (aucun
checkout); `nirs4all-lite` -> `nirs4all-core` (aggregate), `datasets`
OPTIONNEL; `nirs4all.*` + distributions explicites + facade `n4a.*` additive,
R packages explicites."

| # | Signed claim | Verdict | Evidence |
|---|---|---|---|
| C1 | Temporary `nirs4all-core` clone retired; no checkout | **PASS** | `ls -ld nirs4all-core` → absent. `git -C nirs4all worktree list` → only `nirs4all` + `.claude/worktrees/agent-a5af0970...`; no `nirs4all-core` worktree. No `name="nirs4all-core"`/`nirs4all_core` in any `pyproject.toml`/`Cargo.toml`/`package.json`/`DESCRIPTION`. Matches A13. |
| C2a | `datasets` optional / out of default aggregate | **PASS** | Python: `nirs4all-lite[datasets]` is a standalone extra, **excluded** from `all`, only in `everything` (`nirs4all-lite/bindings/python/pyproject.toml:31-46`). Rust: `datasets` feature `default = []`, off (`bindings/rust/nirs4all/Cargo.toml`). R: `nirs4alldatasets` in `Suggests` (`bindings/r/DESCRIPTION`). |
| C2b | `nirs4all-lite` → `nirs4all-core` (aggregate) | **CONCERN-1** | Conceptual only. No binding uses `nirs4all-core` today. The aggregate already ships as `nirs4all-lite` (Python, import `nirs4all_lite`) and as the **bare `nirs4all`** crate/npm/R/MATLAB name (see matrix §2). The rename is real work (A13 `CORE-002`), not an alias flip. |
| C3a | Explicit distributions (`nirs4all-methods`, etc.) | **CONCERN-2** | True for formats/io/dag-ml/dag-ml-data. **Not yet true for methods**: primary Python dist is `pls4all` 1.0.1 (`nirs4all-methods/bindings/python/pyproject.toml:11`); Rust crate `pls4all`; R `n4m`+`pls4all`. `nirs4all-methods` exists only as a parallel, not-yet-primary binding (`bindings/python_nirs4all_methods/pyproject.toml:7`, v1.0.0). |
| C3b | `n4a.*` facade additive; `nirs4all.*` compatible | **PASS (CONCERN-3 docs)** | `n4a` Python namespace does not exist yet (0 `import n4a` / no `n4a` dist) → additive, zero migration risk. `nirs4all` full-lib import surface intact (`nirs4all/nirs4all/{operators,pipeline,...}`, 119 files referencing `nirs4all.operators`). Caveat: `n4a` is already an ecosystem token (`.n4a` bundle ext, `n4a-datasets` CLI, A13 `n4a.aggregation-*` schema ids) → docs must disambiguate. |
| C4 | R packages explicit | **PASS** | `nirs4allformats` (+`nirs4allformatslite`), `nirs4allio`, `nirs4alldatasets`, `n4m` (+`pls4all`), `dagmldata`, aggregate `nirs4all`. All explicit, no dotted namespaces. |

## 2. Distribution / import name matrix (observed, not aspirational)

| Domain | Python dist (import) | Rust crate | npm | R pkg | C ABI prefix |
|---|---|---|---|---|---|
| Full library | `nirs4all` (`nirs4all`) | — | — | — (none) | — |
| Aggregate (lite→core) | `nirs4all-lite` (`nirs4all_lite`) | `nirs4all` | `nirs4all` | `nirs4all` | — |
| Methods | **`pls4all`** 1.0.1 (parallel `nirs4all-methods` 1.0.0) | `pls4all` | `@nirs4all/methods-wasm` | `n4m` (+`pls4all`) | `n4m_` |
| Formats | `nirs4all-formats` | `nirs4all-formats[-core/-capi/-cli]` | — | `nirs4allformats(lite)` | `n4fmt_` |
| IO | `nirs4all-io` | `nirs4all-io[-core/-capi/-cli/-dagml]` | — | `nirs4allio` | `n4io_` |
| dag-ml | `dag-ml` | `dag-ml`, `dag-ml-core` | `dag-ml-wasm` | — (none in lite registry) | `dagml_` |
| dag-ml-data | `dag-ml-data` | `dag-ml-data` | `dag-ml-data-wasm` | `dagmldata` | `dagmldata_` |
| Datasets | `nirs4all-datasets` (`nirs4all_datasets`) | — | `@nirs4all/datasets-wasm` | `nirs4alldatasets` | — |

Two structural facts the GOV decision rests on:

1. **The bare `nirs4all` name is consumed asymmetrically.** In Python the full
   library owns `nirs4all`, so the aggregate is forced to `nirs4all-lite`. In
   Rust/npm/R/MATLAB the aggregate already took `nirs4all` (no full library
   there). So "lite → nirs4all-core" cannot mean one literal package name across
   ecosystems — it is a *concept* whose per-language spelling must be pinned by
   `GOV-003` (Python `nirs4all-core` or keep `nirs4all-lite`; Rust stays
   `nirs4all`; npm `@nirs4all/core` vs `nirs4all`; R `nirs4all`; MATLAB
   `+nirs4all`). This matches design-doc §1.5 but is NOT what a literal reading
   of "lite → nirs4all-core" implies.
2. **C ABI prefixes are distinct and stable** (`dagml_`, `dagmldata_`, `n4fmt_`,
   `n4io_`, `n4m_`). No collisions. GOV should freeze these (renaming breaks
   every binding + headers + ABI snapshots); they are out of scope of any
   cosmetic distribution rename.

## 3. Concerns (ranked)

- **CONCERN-2 (highest) — methods naming is mid-flight.** The signed
  "explicit `nirs4all-methods` distribution" is a target. Today methods ships as
  `pls4all` (Python dist + Rust crate), with `n4m` as the low-level R/C-ABI name
  and `nirs4all-methods` only as a not-yet-primary parallel Python binding
  (commit `f6a77c65` "Phase A2-A13: structural renames" is in progress). The
  methods upstream is under active AOM development and on push-hold, so L1 cannot
  drive this rename unilaterally. The A13 namespace row
  (`nirs4all-methods` / import `nirs4all_methods`; compat `n4m`,`pls4all`) is the
  **destination**, not the current state.
- **CONCERN-1 — lite→core is implementation, not a rename.** A13 already flags
  `CORE-002` as real work (lite is a lazy registry/proxy + portable subset, not a
  hard re-export). The GOV sign-off does not unblock L4 by itself; L4 stays gated
  on `LOCK-REL`.
- **CONCERN-3 — `n4a` token overload (docs).** `n4a` will mean three things:
  `.n4a` bundle files (100+ refs in `nirs4all/pipeline/*`), the `n4a-datasets`
  CLI (`nirs4all-datasets/pyproject.toml:83`), and the new `n4a.*` Python facade.
  Semantically consistent (n4a = nirs4all), but `GOV-004` public docs must state
  the distinction or users will conflate a file extension with an import root.
- **CONCERN-4 — license drift in the aggregate (feeds `GOV-005`).** `nirs4all-lite`
  Python declares `license = "CeCILL-2.1 OR AGPL-3.0-or-later"`
  (`bindings/python/pyproject.toml:11`) yet carries a stale
  `"License :: OSI Approved :: MIT License"` classifier (line 18); the R
  `DESCRIPTION` says `License: MIT + file LICENSE`, while Cargo/npm say
  CeCILL/AGPL. The aggregate's effective license must be reconciled before any
  `nirs4all-core` release.
- **CONCERN-5 (minor, GOV-003 input) — product name drift.** Studio frontend npm
  package is still `nirs4all-webapp` (`nirs4all-studio/package.json:2`, v0.9.1)
  though the repo/product is `nirs4all-studio`; the web app ships as
  `nirs4all-web` v0.1.0 from a `studio-lite/` subdirectory
  (`nirs4all-web/studio-lite/package.json`). `nirs4all-io` declares the same dist
  name in two manifests (root + `bindings/python`). None blocks GOV; all belong
  in the `GOV-003` source-of-truth table.

## 4. What the sign-off correctly settles (do not reopen)

- C1 (no `nirs4all-core` checkout) and C4 (R explicit) are fully realized.
- `datasets` optional-by-default (C2a) is already implemented in all three
  ecosystems — no further work.
- `n4a.*` as an *additive* facade is safe: it touches nothing that exists.

## 5. Required sync-board corrections (for A0/L1 — SW2 did not edit the board)

Append to the `LOCK-GOV` impact cell or the worklog:

1. "GOV claims are signed as *direction*; three are target-state: (a) methods
   ships as `pls4all`/`n4m` today, `nirs4all-methods` rename pending methods
   upstream (push-hold); (b) `lite→nirs4all-core` is `CORE-002` implementation,
   not an alias — no binding uses `nirs4all-core`; (c) `n4a.*` facade is net-new
   (0 current usages)."
2. Annotate the A13 namespace table reference: methods primary dist = `pls4all`
   1.0.1 (Rust crate `pls4all`), `nirs4all-methods`/`n4m` = destination names.
3. Add `GOV-004` doc note: disambiguate `.n4a` (bundle) vs `n4a-datasets` (CLI)
   vs `n4a.*` (Python facade).
4. Flag `GOV-005` input: `nirs4all-lite` license metadata is inconsistent
   (MIT classifier + R `License: MIT` vs CeCILL/AGPL elsewhere).

## 6. Next implementation actions

L1 (governance, remaining `GOV-003`/`GOV-004`/`GOV-005`):

- `GOV-003`: publish the per-language source-of-truth table seeded by §2; pin the
  concrete spelling of the aggregate per ecosystem (resolve the asymmetric
  `nirs4all` name) and record product-name drift (CONCERN-5).
- `GOV-004`: alias/deprecation policy — Python `nirs4all-lite` → `nirs4all-core`
  window; methods `pls4all`→`nirs4all-methods` window **coordinated with the
  methods upstream owner** (do not unilaterally rename); `n4a` token doc note.
- `GOV-005`: license matrix; first fix the lite MIT/CeCILL drift (CONCERN-4).

L4 (core aggregate) — stays `blocked` on `LOCK-REL` (correct on board):

- `CORE-001`/`CORE-002` are implementation, not rename. Do not announce a
  `nirs4all-core` package until `LOCK-REL` + the GOV-003 name table land.
- Keep the bare `nirs4all` Rust/npm/R/MATLAB aggregate names; only the Python
  dist name is in question.

## 7. Blockers / dependencies

- Methods rename (`pls4all`→`nirs4all-methods`) blocked on methods upstream
  (active AOM dev / push-hold) — cross-lane coordination, not an L1 edit.
- L4 core promotion blocked on `LOCK-REL` (manifest/lockfile) + `GOV-003` names.
- No new blocker introduced; `LOCK-GOV` may remain `landed` with the §5 notes.

## 8. Method / evidence commands (read-only)

`ls`/`git worktree list`; `rg -n '^name=' …pyproject.toml/Cargo.toml`;
`rg '"name"' …package.json`; `rg '^Package:' …DESCRIPTION`; C ABI headers
(`nirs4all_formats.h:26` `n4fmt_abi_version`, `nirs4all_io.h:49`
`n4io_abi_version`, `dag_ml.h:275` `dagml_version`, `dag_ml_data.h:228`
`dagmldata_version`, `aug_rng_utils.h` `n4m_*`); `.n4a`/`n4a-datasets` greps.
No code or sync-board files were modified.
