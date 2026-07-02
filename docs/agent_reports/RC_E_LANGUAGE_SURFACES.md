# RC-E — Language Package Surfaces (core aggregate)

Date: 2026-07-02
Lane: RC-E (Language package surfaces: Python facade, R, JS/WASM, Rust, MATLAB
contracts inside the core aggregate)
Worktree: `/home/delete/nirs4all/_worktrees/RC-v1-nirs4all-core`
Branch: `rc/v1-full-refactor-core`

## Executive summary

The RC core language-surface story is now concrete and enforced. Before this
lane, the *always-on* static surface gate (`test_cross_language_surface.py`,
pure Python, no R/Node/Octave/cargo needed) only proved surface parity for
**Python / WASM / R** — the **MATLAB and Rust** operator/upstream declarations
could silently drift and the required Python gate would not catch it (Rust's
check needed `cargo`; MATLAB had no static check at all). That hole is closed:
all **five** bindings are now compared in the one gate that always runs.

Capability levels are now declared **honestly and machine-checkably**: a new
`compat/capabilities.toml` records, per language, the capability level of the
portable operator subset using the exact `OPERATORS.md` ladder vocabulary, and a
new test (`test_capability_matrix.py`) fails if any binding over-claims
(`execute-local`+ without a real run symbol, `parity-validated` without a real
parity gate).

**Important cross-lane finding:** RC-A is executing the `nirs4all-lite` →
`nirs4all-core` rename **concurrently in this same shared worktree**. See
§"Coordination / collision" — it is load-bearing for integration.

## Deliverables (files)

Created (solely RC-E owned):

- `compat/capabilities.toml` — machine-readable per-language capability ledger
  for the portable operator subset (`metadata|plan|execute-local|
  execute-remote|parity-validated`, sourced from `docs/OPERATORS.md`). Records
  run symbol, run source, parity gate, and delegation path per binding.
- `bindings/python/tests/test_capability_matrix.py` — honesty gate (9 tests):
  ladder ⇐ OPERATORS.md; declared subset == `PORTABLE_OPERATOR_CLASSES`; every
  executable claim has a real run symbol in source; every `parity-validated`
  claim has a real parity gate file (and, for Rust, the parity test symbol);
  upstream domains only claim `metadata` and exclude `methods`.
- `docs/CAPABILITIES.md` — human-readable honest capability matrix for all five
  bindings, cross-referencing the TOML and enforcement test.

Modified (RC-E edits; some also touched by RC-A's rename sed — see §collision):

- `bindings/python/tests/test_cross_language_surface.py` — **extended the static
  surface gate to MATLAB and Rust.** Added `_matlab_operator_classes`,
  `_matlab_upstreams`, `_rust_operator_classes`, `_rust_upstreams`; the operator
  subset and upstream key+role parity checks now compare Python vs
  {WASM, R, MATLAB, Rust} (+ `compat`).
- `Makefile` — added `test_capability_matrix.py` to `test-python-v1-surfaces`.
- `docs/OPERATORS.md` — pointer from the capability ladder to
  `compat/capabilities.toml` / `CAPABILITIES.md` / the enforcement test.
- `docs/PARITY.md` — new "Static surface parity (no runtime required)" section
  documenting the all-five-language gate + capability gate.

Removed:

- `docs/CORE_RENAME.md` — an RC-E draft rename runbook, removed because (a) RC-A
  has since *executed* the in-repo rename so the doc's "not yet executed"
  framing went stale, and (b) a runbook that must reference the **old** name is
  fragile against RC-A's repo-wide `nirs4all-lite`→`nirs4all-core` sed. Its
  still-valid content (invariants + remaining coordinator/registry steps) is
  preserved in §"lite→core rename" below, which lives here in the ecosystem
  worktree, out of the sed's reach.

## Tests run (exact results)

Run with `PYTHONPATH=bindings/python/src python3 -m unittest` in the core
worktree (system `python3`; no per-repo `.venv` present for this aggregate):

- `test_cross_language_surface.py` — **6 passed** (now covers Python/WASM/R/
  MATLAB/Rust).
- `test_capability_matrix.py` — **9 passed**.
- `make test-python-v1-surfaces` — **53 passed** (release_topology, facade,
  pipeline_contract, upstreams, cross_language_surface, capability_matrix).
- Full `unittest discover -s bindings/python/tests` — **54 passed, 1 skipped**
  (the 1 skip is a pre-existing optional-environment skip).
- `ruff check` on both new/edited test files — **All checks passed** (repo has no
  ruff/mypy config; its Python gate is `unittest`, but ran ruff as a courtesy).
- `py_compile` on new test files — OK.

Teeth verified (mutation probes, in-memory, no repo files touched):

- Rust operator dropped → count guard fires (8 ≠ 9). ✔
- MATLAB operator renamed → set inequality vs Python fires. ✔
- Capability over-claim (nonexistent `run_source`) → honesty test fails. ✔

Not run (deliberately):

- `cargo test` / `npm test` runtime gates. Node/npm and cargo are present; R and
  Octave are absent. I did **not** run the Rust/WASM runtime gates because (a)
  RC-A is concurrently editing `bindings/rust/nirs4all/src/lib.rs` and
  `bindings/wasm/src/index.js`, so a failure would be misattributed, and (b) my
  deliverables are *pure-Python static* gates specifically designed to validate
  the Rust/MATLAB/WASM/R surface declarations **without** those toolchains — that
  is the point. The static gate reads those sources directly and is green.

## Capability-level honesty (RC goal + stop condition)

Honest current state of the aggregate, now encoded and enforced:

- The aggregate executes exactly one operator subset — Kennard-Stone / SNV /
  Savitzky-Golay / PLS — and **delegates all numerics to the `methods` upstream**
  in every binding; it never re-implements a kernel.
- All five bindings expose a real run entry point and a strict parity gate
  against the shared Python oracle, so each is `parity-validated` **conditional
  on `methods` being installed**. Without `methods`, they degrade honestly to the
  `plan` level (parse/inspect works; the run entry point raises a clear
  capability-unavailable error — e.g. MATLAB `nirs4all:MissingMethods`, R "does
  not expose …", the Rust loader error, the `NIRS4ALL_LITE_REQUIRE_METHODS_PARITY`
  strict skip). No binding fakes a local re-implementation.
- The other upstream domains (`formats`, `io`, `datasets`, `dag_ml`,
  `dag_ml_data`) are lazy re-exports only → aggregate capability = `metadata`;
  real execution capability is upstream-provided. Recorded as such, not dressed
  up as aggregate execution.

This reuses the `OPERATORS.md` binding-capability ladder verbatim and does **not**
invent a parallel taxonomy (it is distinct from the dag-ml `ControllerCapability`
/ `portable_level` vocabulary in `CAP_spec.md`, which classifies dag-ml
controllers, not aggregate bindings).

## lite → core rename (state + exact remaining steps)

RC-A owns this rename; RC-E only makes the surface rename-ready and records
steps. Observed state in the shared worktree as of this report:

In-repo (Phase R1) — **already executed by RC-A**:

- `bindings/python/pyproject.toml` `name = "nirs4all-core"`.
- Release-topology manifest schema bumped to `nirs4all-core.release-topology.v2`
  (`_topology.py`).
- Repo-wide `nirs4all-lite`→`nirs4all-core` textual sweep across workflows,
  LICENSES, docs, README, bindings, `compat/upstreams.toml`, and the guard tests
  (`test_release_topology.py`, `test_pipeline_contract.py` updated in lockstep).
- The underscore **import** package `nirs4all_lite/` **still exists** alongside
  `nirs4all_core/` and `n4a/` (all three wheel packages retained).

Invariants — verify these hold before integration:

1. `pip install nirs4all-lite` must keep working after cutover (publish a
   `nirs4all-lite` alias wheel depending on `nirs4all-core`; never yank).
2. The underscore import `nirs4all_lite` must keep resolving — **the entire
   Python test suite imports it** (mine included). It currently does.
3. `nirs4all` stays reserved as a Python import for the full modelling library.
4. Rust/npm/R/MATLAB are unaffected — they already ship the bare `nirs4all`
   name; the rename is Python-distribution-only.

Remaining Phase R2 — **coordinator / GitHub / registry actions (NOT simulated
here)**:

- Rename GitHub repo `GBeurier/nirs4all-lite` → `GBeurier/nirs4all-core`; update
  `[project.urls]`, Rust README/`Cargo.toml` links, and any workflow that
  hard-codes the slug (GitHub keeps a redirect but remotes must be updated).
- Update the `nirs4all-ecosystem` submodule pin/URL for the renamed repo
  (RC-A/coordinator; do not edit the ecosystem worktree from RC-E).
- PyPI: publish `nirs4all-core`; then a final `nirs4all-lite` alias release whose
  only dependency is `nirs4all-core`.
- `nirs4all.org` install snippets (RC-A/coordinator).

Open decision to confirm with RC-A: the manifest `schema` id was bumped to
`…v2`. If any consumer pins the literal `nirs4all-lite.release-topology.v1`
token, that consumer must be updated in the same release; otherwise keeping the
opaque v1 id would have been non-breaking. Flagging, not blocking.

## Coordination / collision (READ FIRST for integration)

**RC-A and RC-E share this one worktree** (`RC-v1-nirs4all-core`) — the control
board lists a single core worktree, and both lanes are pointed at it. During
this session the worktree went from clean → heavily modified by RC-A's rename,
including files RC-E edited:

- Overlapping files: RC-A's sweep rewrote the docstring of
  `test_cross_language_surface.py` and the `nirs4all-lite` strings in
  `docs/OPERATORS.md`, `docs/PARITY.md`, and even the comments of RC-E's new
  `compat/capabilities.toml` and `docs/CAPABILITIES.md`. RC-E's substantive
  additions survived intact; the shared suite is green after both sets of edits.
  (Per tooling notice, RC-A's edits were intentional; RC-E did not revert them.)
- `Makefile` `M` is RC-E's one-line addition only (no RC-A Makefile change).
- One cosmetic artifact of the blunt sed: a `capabilities.toml` comment now reads
  "shipping as `nirs4all-core`, target name `nirs4all-core`" (was "…today as
  nirs4all-lite, target …core"). Harmless (comment); left as-is to avoid a
  tug-of-war.

Coupling RC-A/coordinator must know:

- If the underscore package `nirs4all_lite/` is *ever* renamed to
  `nirs4all_core/`, then `compat/capabilities.toml`'s Python `run_source` paths
  **and** every test that does `import nirs4all_lite` must change in the **same**
  commit. RC-E's capability gate will fail until `capabilities.toml` matches the
  real path — this is intended (it forces a complete, consistent rename).

Suggested integration order: land RC-A's rename commit and RC-E's surface/
capability additions **together** (they are green together now), then run
`make test-python-v1-surfaces`.

## Risks & open questions

- **Shared-worktree concurrency** (above) is the main risk; a wholesale RC-A
  rewrite of `test_cross_language_surface.py` could drop the MATLAB/Rust
  coverage. Mitigation option if desired: move the MATLAB/Rust extractors into a
  separate RC-E-owned test file. Left in place for now since coexistence is the
  intended model and the additions are green.
- Runtime parity for Rust/WASM/R/MATLAB was not executed this lane (toolchain +
  concurrency reasons). The static surface gate does not replace the numeric
  parity gates in `PARITY.md`; those remain a larger integrated step.
- R and Octave are unavailable locally, so `R CMD check` / Octave smoke remain
  `SKIP/RISK` as before (unchanged by this lane).

## Decisions

- Extend the always-on static gate to all five bindings rather than rely on
  per-toolchain gates — closes the MATLAB/Rust hole in the required suite.
- Encode capabilities as machine-readable metadata + an enforcement test using
  the existing `OPERATORS.md` ladder (no new taxonomy) — satisfies "report
  capability levels honestly" with teeth.
- Keep RC-E work name-agnostic (operator classes, upstream keys/roles, run
  symbols) so it survives RC-A's in-flight distribution rename.
- Move the rename runbook into this report (ecosystem worktree) instead of a
  core-worktree doc, to avoid the sed hazard and respect RC-A ownership.
- Do not commit: the working tree also carries RC-A's uncommitted rename; the
  coordinator integrates. (Consistent with the control board's review rule.)

## Follow-up full parity needed?

No new full-parity run is required *for these changes* — they are static surface
+ capability metadata gates with no numerical behavior. A full cross-runtime
numeric parity pass is still owed at the larger integration checkpoint (after
RC-A's rename lands and with methods/libn4m available), per `PARITY.md`.
