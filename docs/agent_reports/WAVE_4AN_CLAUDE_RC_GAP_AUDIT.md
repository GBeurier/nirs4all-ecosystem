# WAVE 4AN — Independent Claude Code RC Gap Audit (second opinion)

Date: 2026-07-03
Auditor: Claude Code, independent read-only second-opinion pass (local workspace only).
Scope: the six second-opinion gaps named in the brief — (1) naming
`nirs4all-core`/`-python`/`-lite`, (2) R/Python/JS-WASM/Rust/MATLAB inclusion,
(3) providers as an *optional* Python client surface, (4) Web client-side-only,
(5) skips/xfails, (6) Studio release archive/Docker runtime pins.

Ground rules honored: local workspace only; **no** `nirs4all-drafts` / `nirs4all-lab`
touched; **no** full parity run; **no** heavy suite executed; **no** edits made to any
sibling worktree (concurrent agents are active — nothing reverted). This report is the
only artifact written.

This is a *second opinion*: I did not trust the lane reports at face value — I verified
each claim against the actual manifests, workflows, `pyproject.toml` files, tests, and the
lock file. Where the first-opinion reports are correct I say so; where an artifact
contradicts or under-covers a claim I flag it with `file:line` evidence.

---

## Verdict summary

| # | Focus area | Verdict | Severity | Headline |
|---|---|---|---|---|
| 6 | Studio release archive / Docker pins | **Gap** | **High** | All-in-one + Docker bundle `nirs4all`/`dag-ml`/`dag-ml-data` from **moving branch heads**, bypassing the fetchability-audited aggregation-lock commits — even on a tagged release. |
| 5 | Skips / xfails | **Partial** | Medium | Python *parity* is genuinely 0-skip/0-xfail in its proof env, but several **green-by-skip** patterns can silently drop coverage in a differently-provisioned CI (notably Studio `test_run_errors` skipping when run *creation* fails, and export-roundtrip skipping on dag-ml legacy fallback). |
| 2 | R/Py/WASM/Rust/MATLAB inclusion | **Partial** | Medium | Surface *declarations* are honest and statically gated, but `nirs4all.r.aggregate` and `nirs4all.matlab_octave.aggregate` are marked `required_for_nirs4all_v1: true` while their runtime proof is preview/subset (MATLAB has **zero** runtime proof). "Required" ≠ "proven". |
| 3 | Providers optional Python client | **OK** | Low | `dependencies = []`, never imports/pins `nirs4all`, not a dep of core/python, neutral schemas are the source of truth. Residual: contract byte-identity has no CI watcher. |
| 1 | Naming core/python/lite | **OK (with warts)** | Low | Names are coherent; transition debt = three aggregate import packages retained + `nirs4all-core` repo is an un-annotated alias in the surface matrix + North-Star layering not yet realized. |
| 4 | Web client-side-only | **OK (strong)** | Low | `client-side-only.test.ts` genuinely enforces no-backend/no-Node/no-third-party; fonts are local. Residual: one stale doc line + a couple of scan blind spots. |

Severity legend: High = release-integrity/reproducibility blocker to resolve before promotion;
Medium = fix or explicitly accept-with-rationale before RC → GA; Low = doc/convergence tidy-up.

---

## Finding 6 (High) — Studio all-in-one + Docker bundle deps from moving branch heads, bypassing the lock

**This is the sharpest gap in the RC and the one the brief flagged.** The whole RC is
built around a reproducible aggregation-lock with a `git ls-remote` fetchability audit
(control board: "audit-fetchability reports 7/7"). The *product that actually ships to
users* — the Studio all-in-one archive and Docker image — does **not** consume that lock.
It pulls the three runtime dependencies from **branch refs**, so it is neither reproducible
nor reconciled with the audited pins.

Evidence (verified):

- `nirs4all-studio/.github/workflows/release-unified.yml`
  - lines 37–39: `NIRS4ALL_LIBRARY_REF: rc/v1-full-refactor-python`, `DAG_ML_REF: rc/v1-full-refactor`, `DAG_ML_DATA_REF: rc/v1-full-refactor` — **branch names, not commits/tags.**
  - lines 40–42: `*_SOURCE_URL: https://github.com/GBeurier/<repo>/archive/refs/heads/rc/...tar.gz` — **branch-head tarballs.**
  - These refs feed `actions/checkout` for the archive/PyInstaller path (lines 682–697, 809–824, 944–958, 1155–1169) and the `*_SOURCE_URL` values are passed straight into the Docker build (lines 1388–1390).
- `nirs4all-studio/Dockerfile`
  - lines 15–17 and 44–46: same branch-head tarball ARG defaults.
  - lines 101–104: `pip install "dag-ml-data @ ${…}" "dag-ml @ ${…}"` then `pip install "${NIRS4ALL_SOURCE_URL}"` — installs whatever those branch heads resolve to at build time.
- Contrast: Studio's *own* source is pinned intelligently. `release-unified.yml` computes
  `checkout_ref` (lines 100–124): a tag push builds the triggering tag; a dispatch against
  an existing tag builds that tag. That good hygiene is applied to the Studio repo but **not**
  to the three bundled runtime deps.

Why it matters:

1. **Non-reproducible.** Two runs of the same release job at different times bundle
   different `nirs4all`/`dag-ml`/`dag-ml-data`. A re-cut or hotfix of tag
   `n4a-v1-rc1-2026.07-refactor` silently changes the numerical/runtime stack inside the
   shipped archive and image.
2. **Bypasses the aggregation-lock.** The lock pins (verified in
   `docs/contracts/release/aggregation-lock.n4a.lock.json`):
   `dag_ml` `a8f6cb3845fcb19f81450b4776094f21978cf2b7`,
   `dag_ml_data` `95e56a7fa3d82ea00fda7ecfcd950a22ab526d21`,
   `lite`/core `1b505e9974390a946415e3b8c57f0803b4ce1532`,
   `methods` `115077ae…`. These branches are under active migration, so the Studio bundle's
   `rc/v1-full-refactor` head can (and over time will) be **ahead of** the audited lock
   commit — the product ships an un-audited dag-ml with no reconciliation step.
3. **`nirs4all-python` isn't even a lock member.** The surface matrix lists
   `nirs4all.python.oracle` as `outside_aggregation_lock`, so the branch head the Studio
   bundle pulls (`rc/v1-full-refactor-python`) is governed by *nothing* — not the lock, not a
   tag.
4. **No integrity check.** The tarballs are fetched over HTTPS with no checksum/signature;
   there is no build-time assertion that the bundled commit equals the lock commit.

Recommendation (coordinator/release decision — I did **not** edit the workflow because
choosing the canonical pin target is a release-policy call and this is a 67 KB load-bearing
file under concurrent ownership):

- Set `NIRS4ALL_LIBRARY_REF` / `DAG_ML_REF` / `DAG_ML_DATA_REF` and the three `*_SOURCE_URL`
  to the RC **tag** `n4a-v1-rc1-2026.07-refactor` (all three repos carry it, per the control
  board) or to the exact lock commit SHAs (`archive/<sha>.tar.gz` is valid and immutable).
- Add a one-line reconciliation gate in the release job: assert the resolved bundled commit
  == the `aggregation-lock.n4a.lock.json` commit for `dag_ml`/`dag_ml_data`/`lite`, and fail
  closed on drift (mirrors the existing `audit-fetchability` philosophy).
- Optionally record the resolved SHAs into `build_info.json` (Dockerfile lines 120–124
  already write build info) so a shipped image is self-describing.

---

## Finding 5 (Medium) — "0 skipped" is scoped to the Python parity gate; several green-by-skip patterns remain

The control board headline ("`887 passed`, `0 skipped`, `0 xfailed`") is **credible for the
Python parity suite in its proof environment** (`NIRS4ALL_REQUIRE_N4M=1`, methods + RC
dag-ml/dag-ml-data present, fallback meter `fallback=0`). I am not disputing that number.
The second-opinion concern is the *skip patterns that survive in the code* and go green — not
red — when the environment differs. `tests/integration/parity` alone carries **147**
skip/xfail-related lines.

Patterns that mask rather than gate (verified):

- **Export coverage depends on an out-of-band meter, not the test.**
  `nirs4all-python/tests/integration/parity/test_conformance_export_roundtrip.py:152,154,190`
  `pytest.skip("… dag-ml ran legacy fallback on this build; native export N/A")`. If dag-ml
  ever falls back to legacy (stale/missing `.so`, wrong env), these native-export cases
  **skip** — they do not fail. The only thing catching that is the *separate* coverage meter
  (`fallback=0`). Couple them, or the "0 skipped" result is contingent on a check outside the
  suite.
- **Studio masks real backend failures as skips.**
  `nirs4all-studio/tests/integration/test_run_errors.py:253,288,365,464`
  `pytest.skip("Quick run creation failed: …")` / `"Experiment creation failed: …"`. A
  regression that breaks run/experiment *creation* is exactly what these error-path tests
  should catch, yet they self-skip on it. This is not an "optional-environment" skip.
- **Studio↔dag-ml manifest contract can silently not run.**
  `nirs4all-studio/tests/test_operators_manifests.py:73,83`
  `pytest.skip("nirs4all.runtime accessor unavailable (W7 not landed)")` /
  `"dag-ml controller_manifest schema not available")`. The controller-manifest projection is
  load-bearing for the dag-ml cutover; if the schema is absent the contract test disappears.
- **Runtime-envelope schema conformance skips without the sibling repo.**
  `nirs4all-python/tests/unit/pipeline/test_rt_envelopes.py:360`
  `pytest.skip("sibling nirs4all-ecosystem runtime schemas not checked out")`. The
  `rt_error.v1` envelope is the Studio/Web contract; in an isolated checkout this validation
  is silently gone.

Legitimate optional-env skips (no action): TabPFN weights, no Parquet engine, optional
synthetic domains/instruments, SQLite `DROP COLUMN` capability, Windows-only POSIX-symlink
skips, `conftest.py:181` guarded `nirs4all` import, core `test_execution_parity.py:29`
methods skip, the 2 non-strict WASM skips.

Recommendation: (a) confirm the four masking cases above actually **execute** (not skip) in
the canonical CI that produced `2335 passed, 0 skipped` and the parity proof — a "0 skipped"
line does not distinguish "ran and passed" from "condition happened to be false"; (b) convert
the *product/contract* skips (`test_run_errors` creation-failed; `test_operators_manifests`
schema-unavailable) to hard failures, since per the RC non-negotiable "skips are release
blockers unless they are real optional-environment skips" these are neither; (c) make the
export-roundtrip fallback-skip a strict co-gate with the coverage meter.

---

## Finding 2 (Medium) — R and MATLAB/Octave aggregate surfaces are marked *required* while proof is preview/subset

RC-E's static surface + capability-honesty gates are genuinely good work: all five bindings
are compared in one always-on Python test, and `compat/capabilities.toml` +
`test_capability_matrix.py` prevent a binding from *over-claiming* its capability level. No
dispute there.

The gap is at the **release-matrix** level, not the declaration level. In
`docs/contracts/release/public-v1-surface-matrix.n4a.json`:

- `nirs4all.r.aggregate` (lines 123–134): `required_for_nirs4all_v1: true`, but
  `proof_boundary` = "local R execution may still be skipped if R is unavailable and must be
  reported as risk."
- `nirs4all.matlab_octave.aggregate` (lines 188–199): `required_for_nirs4all_v1: true`, but
  `proof_boundary` = "local execution remains subset evidence until release infrastructure
  runs it."

The matrix validator (`scripts/n4a_release_surface_matrix.py`, per RC-O) only checks **package
topology + presence of required ids** — it does not assert any runtime proof. So "required for
V1" is a *declaration* that is satisfied by a package existing, not by R or MATLAB actually
running. Concretely:

- MATLAB: **zero** MATLAB-runtime proof exists anywhere in the evidence — only Octave/MEX
  (control board Wave 4AC; Parity-Debt section: "Licensed MATLAB runtime proof remains
  manual/outside the Linux Octave proofs").
- R: proof is local-conda subset runs (Wave 4AC), and the control board itself records a
  Claude review that "warned against overclaiming R … treat R as a methods portable
  subset/preview until dag-ml R coordination and DatasetPackage materialization gates exist."

Marking these `required_for_nirs4all_v1: true` while (a) the validator can't prove them and
(b) the project's own review says "preview" is an internal contradiction that will read as an
overclaim if V1 ships advertising R/MATLAB parity.

Recommendation: either downgrade `nirs4all.r.aggregate` and `nirs4all.matlab_octave.aggregate`
to `required_for_nirs4all_v1: false` (preview) until real R + licensed-MATLAB runtime gates
exist, **or** keep them required and make the release gate fail without those runtime proofs.
Do not leave "required" decoupled from any enforceable proof. (JS/WASM and Rust are fine —
they have real local execution gates.)

---

## Finding 3 (Low) — Providers is a clean optional Python client; one drift residual

Verified good, no action needed on the core boundary:

- `nirs4all-providers/pyproject.toml`: `dependencies = []` (line 36); siblings are
  `optional-dependencies` only (lines 40–55); explicit comment "This package never imports
  nirs4all itself and must not pin it." (line 49).
- Not referenced as a dependency by core or the Python oracle (grep of both
  `pyproject.toml`s returns nothing).
- Surface matrix `nirs4all.providers.contracts` (lines 240–251): ecosystem
  `optional_python_client`, `required_for_nirs4all_v1: false`, and the proof boundary
  correctly states the **neutral schemas** in `docs/contracts/providers` are the canonical
  contract and must stay consumable by R/WASM/native "without a Python dependency". RC-F's
  R/WASM/native gaps are filed as honest TODO gates (`GATE-PROV-R/-WASM/-NATIVE`), not shimmed.

Residual (RC-F's own risk, still open): the canonical neutral contracts live under the
ecosystem repo's **gitignored + force-added** `docs/contracts/providers/`, and byte-identity
between the canonical copy and the vendored copy in the providers package is only checked when
`validate_contracts.py --canonical` is run **manually** — "No automated CI yet wires the two
repos." So the contract source-of-truth can drift silently. Recommendation: wire the
`--canonical` byte-identity check into providers CI (submodule or pinned path) before GA.

---

## Finding 1 (Low) — Naming is coherent; transition warts to converge

Verified:

- Core `bindings/python/pyproject.toml`: `name = "nirs4all-core"`.
- Python oracle `pyproject.toml`: `name = "nirs4all"`.
- Providers: `name = "nirs4all-providers"`.
- Surface matrix cleanly separates `nirs4all.python.oracle` (dist `nirs4all`, namespace
  `nirs4all.*`, target repo `nirs4all-python`) from `nirs4all.python.core` (dist
  `nirs4all-core`, namespace `nirs4all_core`).

Warts (low severity, mostly doc/convergence):

- **Three aggregate import packages coexist** in the core wheel:
  `bindings/python/src/{n4a,nirs4all_core,nirs4all_lite}/`. `nirs4all_lite` is retained
  because the whole core test suite still imports it (RC-E). Fine as a transition, but V1
  should not ship three parallel aggregate import names indefinitely — track convergence.
- **`nirs4all-core` is an un-annotated alias in the surface matrix.** The lock member `lite`
  documents "repo_path stays nirs4all-lite until the GitHub repo rename; nirs4all-core is an
  explicit public alias." But the surface-matrix entry `nirs4all.python.core` (lines 110–121)
  carries `repo_path: "nirs4all-core"` with **no** `selected_workspace_path` and **no**
  alias/pending-rename note — unlike `nirs4all.python.oracle`, which carries both
  `selected_workspace_path` and `target_repo_path`. A reader of the matrix alone would assume
  `GBeurier/nirs4all-core` is a live standalone repo. Add the alias annotation for symmetry.
- **North-Star layering not yet realized.** Both `nirs4all` (oracle) and `nirs4all-core` are
  `required_for_nirs4all_v1: true` and ship in parallel; the ecosystem North Star
  ("`nirs4all` = the `nirs4all-lite` skeleton + Python controllers") means the oracle should
  eventually be *built on* the core skeleton, but today they are independent distributions.
  Expected mid-RC — just make sure release messaging doesn't imply the layering already holds.

---

## Finding 4 (Low) — Web client-side-only is strongly enforced; minor residuals

Verified strong. `nirs4all-web/studio-lite/src/app/client-side-only.test.ts`:

- Scans all app `src/**` `.ts(x)` (excluding tests/`.d.ts`/the staged `wasm/` glue) and
  forbids `fetch(`, `XMLHttpRequest`, `new WebSocket(`, `EventSource(`, `process.env`,
  `node:` imports, `require(`, `'/api/'`, and hardcoded `localhost/127.0.0.1/[::1]` origins
  (lines 49–59). Also asserts no plain `.js` escapes the typchecker (lines 71–72).
- Separately asserts `index.html` loads no remote `<script>`/runtime `<link>` and that
  `src/styles/*.css` has no remote `@import` (lines 88–123).
- Fonts are genuinely local/system: `src/styles/fonts.css` uses system stacks with the
  explicit comment "The public Web app must not make third-party runtime requests, so fonts
  use local/system stacks instead of remote imports." No `fonts.googleapis`/`gstatic`
  anywhere. The client-side-only contract holds.

Residuals (low):

- **Stale doc.** `nirs4all-web/studio-lite/CLAUDE.md` still says "Webfonts come from a Google
  Fonts `@import` (served); offline falls back to the system stack." That contradicts the
  actual `fonts.css` and the client-side-only contract. Recommend a one-line doc correction
  (I did not edit it — concurrent web work is possible and it is outside the ecosystem
  worktree).
- **Scan blind spots.** The `FORBIDDEN` list catches network *clients* but not an arbitrary
  remote origin used as, e.g., an `<img src>`/CSS-`url()`/dynamically-built asset URL inside a
  `.tsx` (only `localhost` origins and `/api/` are pattern-matched in TS; the remote-`https://`
  check is limited to `index.html` and `src/styles/*.css`). Low probability, but a hardcoded
  third-party asset URL in a component would pass. Consider extending the remote-URL scan to
  TS string literals if you want the "no third-party runtime requests" claim airtight.

---

## What I verified vs. did not

Verified directly (local files): Studio `Dockerfile` + `release-unified.yml` ref/URL wiring;
`aggregation-lock.n4a.lock.json` pinned commits; `public-v1-surface-matrix.n4a.json` required
ids + proof boundaries; core/python/providers `pyproject.toml` names + deps; the three core
import packages on disk; `client-side-only.test.ts` + `fonts.css`; actual skip/xfail markers
across RC python/core/studio/web test trees.

Did **not** do (out of scope / per brief): full parity; any heavy suite execution (Studio
pytest, Vitest, Playwright, cargo, WASM, R/Octave); network fetchability probes; any edit to a
sibling worktree. I therefore cannot independently confirm that the four masking skips in
Finding 5 *executed* (vs. were condition-false) in the runs that produced "0 skipped" — that
is exactly the confirmation I recommend the coordinator obtain.

## Risks

- **Release integrity (High):** shipped Studio archive/Docker can diverge from the
  fetchability-audited lock and from itself across rebuilds (Finding 6). This undermines the
  reproducibility the entire RC lock apparatus exists to provide.
- **Silent coverage loss (Medium):** the masking skips (Finding 5) mean a differently
  provisioned CI could report green while native-export, run-error, and manifest-contract
  coverage quietly vanish.
- **Overclaim (Medium):** advertising R/MATLAB as required V1 surfaces without enforceable
  runtime proof (Finding 2) is a credibility risk if surfaced in release notes/marketing.
- **Contract drift (Low):** un-watched provider-contract byte-identity (Finding 3).

## Decisions I made

- Treated the lane reports as claims to verify, not facts; cited `file:line` for every finding.
- Made **no** code/doc edits: the top gap (Finding 6) is a release-policy pin decision on a
  load-bearing file under concurrent ownership, and the remaining items are doc/annotation
  changes in sibling worktrees where concurrent agents are active. Reporting precise,
  ready-to-apply recommendations is the correct second-opinion deliverable and avoids
  collisions.
- Scoped the audit to the six named gaps; did not re-litigate parity numerics, security/
  GitGuardian, cluster, or migration-converter lanes (covered by other lanes).

## Final answer (brief)

- **Files modified:** none except this report
  (`docs/agent_reports/WAVE_4AN_CLAUDE_RC_GAP_AUDIT.md`). No sibling worktree touched; no
  concurrent change reverted; `nirs4all-drafts`/`nirs4all-lab` untouched.
- **Tests run:** none (per brief — no full parity, no heavy suites). Verification was static
  (reads/greps of manifests, workflows, `pyproject.toml`, tests, lock file).
- **Top risk:** Finding 6 — Studio all-in-one/Docker bundle `nirs4all`/`dag-ml`/`dag-ml-data`
  from moving branch heads, bypassing the aggregation-lock; not reproducible.
- **Decisions needed from coordinator:**
  1. Pin the Studio release deps to the RC tag or lock commit SHAs + add a lock-reconciliation
     gate (Finding 6).
  2. Confirm the four masking skips execute in the canonical CI and harden the two
     product/contract ones to fail closed (Finding 5).
  3. Decide required-vs-preview for R and MATLAB/Octave aggregate surfaces and align the
     matrix + gate accordingly (Finding 2).
  4. Wire providers contract byte-identity into CI (Finding 3); add the `nirs4all-core` alias
     annotation to the surface matrix and correct the stale Web fonts doc line (Findings 1, 4).
