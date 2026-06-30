# RV9 — Release / Lockstep / IO Gate Review

**Reviewer:** RV9 (read-only cross-repo reviewer)
**Date:** 2026-07-01
**Scope:** Already-staged work across four repos —
- **L3** release-lock tooling — `nirs4all-ecosystem`
- **L20** dag-ml / dag-ml-data shared-contract lockstep CI — `dag-ml`, `dag-ml-data`
- **L7** nirs4all-io ↔ dag-ml-data sibling cross-CLI conformance — `nirs4all-io`

**Mandate:** CI feasibility, path assumptions, branch-pair logic, stale docs, and whether contract
validators really protect shared changes. **Read-only** — no edits, no staging, no commits. Only
cheap read-only checks were run.

**Branches under review:** `dag-ml` & `dag-ml-data` on `refactor/L20-lockstep`; `nirs4all-io` on
`refactor/L7-io-dagml-sibling`; `nirs4all-ecosystem` on `main`. No unstaged drift in any reviewed
code/CI/JSON path (working tree == index for the reviewed files).

---

## Final disposition

**APPROVE — ship-ready, with non-blocking follow-ups.**

The three gates are **feasible** and the cross-repo contract validator **genuinely enforces
byte-equality** of the shared artifacts (not mere presence). I verified the single most load-bearing
fact for L3 — the committed lockfile's `manifest_digest` equals the SHA-256 of the committed
manifest's canonical JSON — and that all seven pinned member commits are reachable on their
`origin/main`. No ship-blocking defect was found in the staged changes themselves.

Recommended before/after merge (all low-effort or planning items): fix the **dead function** in the
release-lock script (repo "no dead code" rule), update the **one stale doc** (`COMPAT.md`), and
**document the coordinated-merge choreography** for breaking shared-contract changes (the lockstep
job alone does not dissolve the vs-`main` merge deadlock that the other CI jobs impose).

---

## What each change actually is (verified from `git diff --cached` + staged blobs)

### L3 — `nirs4all-ecosystem` (new tooling, all-additions)
- `scripts/n4a_release_lock.py` (487 lines, new): `generate` / `validate` / `checkout-members`
  sub-commands. Walks manifest components, hashes contract artifacts + version sources, builds
  per-group **lockstep attestations** (raw + canonical-JSON equality), and round-trips a
  deterministic lockfile.
- `.github/workflows/version-guard.yml` (new): three jobs — `guard` (manifest VERSION must not be
  ahead of latest tag), `release-lock-tooling` (py_compile + `--help` + JSON syntax), and
  `release-lock-validation` (`checkout-members` 7 repos → `validate`).
- `docs/contracts/release/aggregation-manifest.n4a.json` + `aggregation-lock.n4a.lock.json` (new):
  7 components (dag_ml, dag_ml_data, methods, formats, io, lite, datasets), one lockstep group
  `dagml-pair`.
- ~17.5k lines of accompanying `docs/` specs and agent reports (design-time artifacts, not gate code).

### L20 — `dag-ml` & `dag-ml-data` (symmetric, minimal, additive)
Raw diff confirms **only two changes per repo**:
1. A new `contract-lockstep` job (branch-pairing + `validate_contracts.py --require-sibling`).
2. The existing `rust` job's "Shared contract" step hardened from
   `python scripts/validate_contracts.py` → `… --require-sibling --sibling-root external/dag-ml[-data]`.

The `@v6` action pins, the `DAG_ML_DATA_REPO`/`DAG_ML_REPO` env, and the peer-checkout steps in
`msrv`/`rust`/`python-bindings`/`wasm` are **pre-existing** (unchanged lines), not introduced here.

`scripts/validate_contracts.py` (both repos): adds `argparse` with `--require-sibling` /
`--sibling-root`, threads an explicit root through `candidate_sibling_roots`/`sibling_root`, and
raises when a required sibling is missing.

### L7 — `nirs4all-io` (conformance hardening + doc sync)
- `.github/workflows/dag-ml-data-conformance.yml`: siblings now cloned **non-optionally**
  (`--filter=blob:none --depth 1`, no `|| true`) and run with `NIRS4ALL_REQUIRE_DAGML_SIBLINGS=1`.
- `tests/dag_ml_data/verify_cross_cli.sh`: hard-fails (not skip) when required; builds the emit crate
  with `--config "patch.crates-io.dag-ml-data.path='${dmd}/crates/dag-ml-data'"` (and threads the same
  patch into `cargo metadata`).
- `crates/nirs4all-io-dagml/src/lib.rs`, `crates/nirs4all-io-cli/src/main.rs`,
  `crates/nirs4all-io-cli/tests/cli.rs`, `CLAUDE.md`, `docs/STATUS.md`, `tests/dag_ml_data/README.md`:
  doc/message updates migrating "workspace-excluded" → "workspace member + Cargo patch".

---

## Validation evidence (read-only checks actually run)

| # | Check | Result |
|---|---|---|
| V1 | `manifest_digest` in lock == `sha256(canonical_json(manifest))` | **MATCH** (`sha256:84b2150a14…54ae6f`) — `release-lock-validation` clears its first gate |
| V2 | 7 pinned member commits reachable on `origin/main` | **All present**: dag_ml `f58d7bf` (tag `dagml-adr17-complete-2026-06-30`), dag_ml_data `347c15f`, methods `7602eb08`, formats `89231b2` (`v0.2.1`), io `84ab189`, lite `c14dcca`, datasets `ae41496` (`v0.3.0`) — each `== origin/main` HEAD |
| V3 | methods push-hold (memory) vs pinned commit | Lock pins `7602eb08` = methods `origin/main`; the held AOM commits are *ahead/elsewhere*, so the lock pins **published** state — no unreachable-commit risk |
| V4 | Lockfile member states | All members `branch=main`, `dirty=False` — lock is pinned to clean released `main`, **decoupled from the dirty feature branches under review** (correct for CI reproducibility) |
| V5 | Lockstep attestation in committed lock | `dagml-pair valid=True`; `conformance_pack` & `parity_oracle` both `raw_equal=True`, `canonical_json_equal=True` across dag_ml + dag_ml_data |
| V6 | Validator really compares (not just presence) | `validate_contracts.py` L5570-71: `require(local_pack == sibling_pack, …)` and `require(local_parity_oracle == sibling_parity_oracle, …)` — **full parsed-JSON equality** of the shared artifacts |
| V7 | dag-ml-data CI symmetry | Mirror of dag-ml: `contract-lockstep` pairing job + `rust`/`msrv`/`python`/`wasm` peer-checkout + `--require-sibling --sibling-root external/dag-ml`; the job that runs `--require-sibling` **does** check out the sibling first (no missing-checkout) |
| V8 | L7 Cargo-patch version compatibility | io workspace requires `dag-ml-data = "0.2.2"`; sibling `main` is `[workspace.package] version = "0.2.2"` → patch **satisfies** `^0.2.2`. Feasible today |
| V9 | L7 sibling path assumptions | `verify_cross_cli.sh` resolves `dmd=${io_root}/../dag-ml-data`, `dml=${io_root}/../dag-ml`; workflow clones into `../dag-ml-data` / `../dag-ml` → **paths match** |
| V10 | version-guard arithmetic | VERSION=`0.1.0`, only ecosystem tag is `v0.1.0` → `0.1.0 > 0.1.0` is False → **"OK, not ahead"** (passes) |
| V11 | release-lock CLI smoke (what CI runs) | `py_compile` OK, `--help` OK, both JSONs valid via `json.tool` → `release-lock-tooling` job feasible |
| V12 | Determinism of `validate` regen | Lock is order-insensitive under `==` (dicts), and all lists are sorted or file-derived; regen from a clean clone at the pinned commit reproduces hashes/tags/branch/dirty → byte-stable |
| V13 | Owner consistency | Manifest `repo_url`s and CI hardcoded `peer_repo` both use `GBeurier/…` — consistent |

---

## Findings (severity-ranked)

### F1 — [Medium] L20 lockstep is necessary but not sufficient: vs-`main` jobs still deadlock a coordinated breaking change
The new `contract-lockstep` job is the **only** job that uses the paired branch
(`ref: ${{ steps.peer.outputs.ref }}`). The pre-existing `rust`/`msrv`/`python-bindings`/`wasm` jobs
check out the peer with **no `ref:`** (default branch = `main`) and validate/build against it. Because
`validate_contracts.py` enforces byte-equality (`require(local_pack == sibling_pack)`), a *coordinated
breaking* shared-contract change on paired branches behaves as:

- `contract-lockstep` (dag-ml): peer branch present → compares NEW pack vs NEW pack → **PASS**.
- `rust` (dag-ml): peer **main** (OLD pack) → compares NEW vs OLD → **FAIL**.
- Symmetric on dag-ml-data → both PRs red against each other's `main` → **merge deadlock**.

This is **largely pre-existing** (the `rust` job already validated against peer-`main` via the
`DAG_ML_DATA_REPO` env, before `--require-sibling` was added), and the staged change *hardens* it
(`--require-sibling` now fails closed). The new pairing job improves UX (clear "needs a paired
branch" error) but does **not** resolve the deadlock. *Recommendation:* either (a) thread
`steps.peer.outputs.ref` into **all** peer checkouts so paired branches are used consistently, gated
by a final "both green on `main`" merge queue; or (b) document the coordinated-merge choreography
(temporary `continue-on-error`/admin-merge of both, then `main` reconverges). At minimum, write the
choreography down — today it is implicit.

### F2 — [Low] Dead code: `repo_identity()` in `n4a_release_lock.py`
`repo_identity()` (lines 87-97) strips the dirty bit so the ecosystem repo's own identity wouldn't
self-invalidate the lock — but it is **never called**. `generate_lock` records only
`generated_from.ecosystem_repo: "nirs4all-ecosystem"` (a string) and no git state for the ecosystem
repo. The function is a vestige of an abandoned design and violates the repo-wide "no dead code"
rule. *Recommendation:* delete it, or wire it in if recording the producer's identity was intended.

### F3 — [Low] Stale doc: `COMPAT.md:38` still calls io-dagml "workspace-excluded"
The L7 change correctly updated `CLAUDE.md`, `docs/STATUS.md`, `tests/dag_ml_data/README.md`,
`lib.rs`, `main.rs`, and `cli.rs` from "workspace-excluded" to "workspace member + Cargo patch", but
`COMPAT.md` (**not staged**) still reads: *"bails with a pointer to the workspace-excluded ecosystem
crate `crates/nirs4all-io-dagml` … which carries the `dag-ml-data` sibling dependency."* Both clauses
are now inaccurate (it's a member; default dep is crates.io, patched only in conformance).
*Recommendation:* update `COMPAT.md:36-40` in the same change set.

### F4 — [Low] L7 version coupling has no pin/pairing — a future dag-ml-data `0.3` silently breaks conformance
`dag-ml-data-conformance.yml` clones dag-ml-data **`main` at `--depth 1`** and patches it against io's
`dag-ml-data = "0.2.2"` (`^0.2.2`). Compatible today (V8). But there is **no branch-pairing and no
pin**: the day dag-ml-data `main` bumps to `0.3.x` (or any `>=0.3.0`), the path patch will no longer
satisfy `^0.2.2` → `cargo` hard-errors on a version mismatch → conformance goes red with no signal
until io bumps its requirement. Separately, since io-dagml is now a **non-optional workspace member**
with `dag-ml-data.workspace = true`, the standalone io workspace build *and* the `main.rs`
discoverability command both require `dag-ml-data 0.2.2` to be **published on crates.io** (not
verified here; the patch only covers the conformance job). *Recommendation:* note the version
coupling in the conformance workflow, and confirm `dag-ml-data 0.2.2` is actually on crates.io (or
the standalone `cargo build --workspace` / the suggested `cargo run --manifest-path …` will fail
outside the patched harness).

### F5 — [Low] `version-guard` crashes (not skips) if the manifest file is missing
`read_manifest()` does `open(path)` with no `FileNotFoundError` guard; the intended graceful
`::warning:: … skipping` path only triggers when the read returns falsy. VERSION exists today
(`0.1.0`), so this is latent — but deleting/renaming the manifest file would fail the job with a raw
traceback instead of the designed skip. *Recommendation:* wrap the read so a missing file degrades to
the warning/skip path.

### F6 — [Info] Branch-pair change detection and fork PRs
- Change detection uses two-dot `git diff --name-only FETCH_HEAD HEAD`. This is correct under
  `actions/checkout`'s default PR **merge-ref** checkout (HEAD already includes base), so it
  approximates the PR's net change set. It would become fragile (conflating base-side edits) only if a
  future change pins the checkout to the head SHA. Acceptable as written.
- The paired branch is looked up on the **canonical** peer (`GBeurier/…`), so **fork-PR** contributors
  cannot create a paired branch and their shared-contract PRs would always trip the gate. Acceptable
  for a single-owner workflow; worth a comment.

### F7 — [Info] Scope boundary: the release lock does not attest io↔dag-ml-data conformance
The `io` manifest component declares **no `contract_artifacts`** and is **not** in any lockstep group;
only `dagml-pair` (dag_ml + dag_ml_data) is attested. The io↔dag-ml-data envelope conformance is
enforced **solely** by io's own `dag-ml-data-conformance.yml` (vs sibling `main`). That is a
reasonable split, but means the aggregation lock gives **no** cross-repo guarantee for the io emit —
worth stating so it isn't assumed.

### F8 — [Info] Hardcoded `GBeurier/…` owner in CI + manifest
Consistent across both CI workflows and the manifest today. If/when these repos migrate to a
`nirs4all` org, the CI `peer_repo` strings, the manifest `repo_url`s, and the io conformance clone
URLs must all move together.

---

## Residual risks (for `release-lock-validation` to stay green in CI)

1. **Remote reachability of pins.** All 7 pins are on `origin/main` now (V2). A force-push that GCs a
   pinned commit, or a member repo flipping to **private** (anonymous clone fails; `generate_lock`
   also refuses `private:true` members), would break `checkout-members`.
2. **Clean-tree determinism.** `validate` reproduces the lock only from a **tracked-only** clean
   clone. The single glob artifact (`methods: cpp/abi/expected_symbols_*.txt`) is narrow, but
   `collect_glob_artifacts` walks the **entire** repo (including `.git/`, `target/`) — any future
   broad glob, or untracked files present at generation time, would make local-vs-CI hashes diverge.
3. **Lock staleness after this wave merges.** The lock pins **pre-L20/L7** `main` commits. Once the
   L20/L7 branches merge to their `main`s, the lock must be regenerated or it will pin contracts that
   predate the merged lockstep state. (Not a defect — an operational reminder.)
4. **No deps installed in `release-lock-validation`.** Fine: the script is stdlib-only on Python 3.11
   (`tomllib` is stdlib); confirmed via py_compile/`--help`.

---

## Notes on what was **not** exhaustively reviewed
- The ~17.5k lines of `docs/` specs and agent reports were treated as design-time artifacts; I did not
  reconcile every spec (e.g. `SW3_REL_MANIFEST_LOCKFILE_spec.md`, `A9_A9-lockstep.md`) against the
  final tooling surface. The tooling is internally consistent and CI-smoke-passing.
- `validate_contracts.py` is 5k+ lines; I confirmed the **shared-artifact equality** path (the
  load-bearing one for this review) and the new argparse wiring, not the full body.
- I did **not** run network operations (no clone of the 7 members, no crates.io lookup). Reachability
  was checked offline via local `origin/*` refs; crates.io publication of `dag-ml-data 0.2.2` (F4)
  remains unverified.
