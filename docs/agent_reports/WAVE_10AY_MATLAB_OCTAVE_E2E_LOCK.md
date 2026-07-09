# Wave 10AY - MATLAB/Octave E2E release gate and core lock repin

Date: 2026-07-09

## Scope

- Revalidated that GitHub CLI is already up to date for release/cockpit work.
- Re-pinned the central aggregation lock to the selected `nirs4all-core` head
  after the docs-only `v0.3.8` follow-up commit.
- Added a strict MATLAB/Octave release-gate artifact to the existing
  formats/IO/datasets/methods language-binding E2E scenario.
- Refreshed the committed runtime evidence ledger from the local artifact set.

## Files Modified

- `docs/CROSS_LANGUAGE_E2E.md`
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/agent_reports/WAVE_10AY_MATLAB_OCTAVE_E2E_LOCK.md`
- `scripts/e2e/verify_core_matlab_octave_release_gate.py`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

Related release coordination:

- `nirs4all-core`: tag `n4a-v1-rc16-2026.07-refactor` points at
  `727fad563b01ddb2e71d74a8ef1be5537207ab99`, a docs-only follow-up above the
  published `v0.3.8` release tag.
- `nirs4all-cockpit`: public dashboard data was refreshed after the R-universe
  manual action URL update; Pages and collect workflows were green.

## Tests Run

- `gh version`
- `python3 scripts/e2e/verify_core_matlab_octave_release_gate.py --workspace-root /home/delete/nirs4all --artifacts-dir .n4a-e2e-artifacts/formats-io-methods`
- `python3 -m py_compile scripts/e2e/verify_core_matlab_octave_release_gate.py scripts/n4a_e2e_scenarios.py`
- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --json`
- `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `python3 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 -m pytest -q tests/test_e2e_scenarios.py`
- `python3 -m pytest -q`
- `python3 -m ruff check scripts/n4a_e2e_scenarios.py scripts/e2e/verify_core_matlab_octave_release_gate.py tests/test_e2e_scenarios.py`

Current evidence result: 11/11 scenarios verified, 71 artifacts, 0 failures.
Full ecosystem pytest result: 170 passed.

## Decisions

- Keep the scenario count at eleven; MATLAB/Octave belongs in the existing
  formats/IO/datasets/methods language-binding scenario rather than as a shallow
  standalone smoke.
- Treat the MATLAB/Octave gate as strict release evidence for the portable
  aggregate archive: the verifier checks the public `v0.3.8` release asset,
  release workflow success, and local workflow/Makefile parity declarations.
- Do not trigger a new package release for the docs-only core head; the
  coordination tag is intentionally outside semver workflow triggers.
- Do not rerun full Python parity in this wave; this batch touches release-lock
  and cross-language E2E evidence metadata, not Python numerical behavior.

## Risks

- The MATLAB/Octave verifier proves the public release gate and declared Octave
  parity workflow, not a fresh local Octave build on this Linux session.
- `python3 -m ruff check .` still traverses sibling project checkouts and archived
  code with pre-existing lint debt; the modified ecosystem scripts/tests pass
  focused Ruff.
- CRAN/R-universe propagation and Studio Windows installer validation remain
  external/manual release items.
