# WAVE 10AU - Cockpit provenance, CRAN helper, and E2E audit

Date: 2026-07-09

## Scope

- Verify the current cross-language E2E suite against the V1 custom app host
  and runtime-mixing goal.
- Close the remaining cockpit audit gaps found after the Python parity skip
  hardening batch.
- Refresh the cockpit snapshot after the latest `nirs4all` and
  `nirs4all-ecosystem` heads.

## Agents and review

- Codex explorer `019f46ea-72dc-7901-acc1-d89dfbbb16c3`: read-only E2E audit.
  - Result: 11 scenarios, 70 verified artifacts, 0 failures.
  - Coverage: Python 11, JavaScript/WASM 8, native 6, R 5, Web 5, Rust archive
    evidence 1.
  - Main limitation: several scenarios intentionally use deterministic
    synthetic fixtures until larger external corpora such as Dataverse are
    available.
- Codex explorer `019f46ea-8b8e-7c60-9ef1-455c8855044e`: read-only cockpit and
  publication audit.
  - Result: cockpit topology and non-prod publication state are aligned.
  - Gaps found: CRAN helper still documented `nirs4allformats.lite`/formats
    CRAN submission guidance; public snapshot provenance had `run_id: null`.

## Files changed

- `nirs4all-cockpit/cockpit/cli.py`
  - Records `GITHUB_RUN_ID` into the snapshot generator block.
- `nirs4all-cockpit/scripts/fetch-cran-tarballs.sh`
  - Removes `nirs4all-formats`, `nirs4allformats`, and
    `nirs4allformats.lite` from the CRAN submission helper.
  - Documents `nirs4allformats` as R-universe-only for the current train.
- `nirs4all-cockpit/tests/test_cli.py`
  - Adds regression coverage for `generator.run_id`.
- `nirs4all-cockpit/tests/test_targets_topology.py`
  - Guards the CRAN helper against reintroducing formats/lite submission
    guidance.

Commits:

- `nirs4all-cockpit` `7f2f94c fix(cockpit): align cran helper and collect provenance`
- `nirs4all-cockpit` `36c3559 chore(collect): refresh data/current.json`

## Tests and gates

- `nirs4all-ecosystem`
  - `python3 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
    - 11/11 ready, 0 blocked, full strict ready.
  - `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --max-age-seconds 14400 --json`
    - 11 scenarios, 70 artifacts, 0 failures.
  - `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
    - 11/11 scenarios verified, 70 artifacts, 0 failures.
  - GitHub Actions on `6ea9bce`:
    - Cross-language E2E scenarios: success.
    - version-guard rerun: success.
- `nirs4all-cockpit`
  - `.venv/bin/pytest -q tests/test_cli.py tests/test_targets_topology.py`
    - 36 passed.
  - `.venv/bin/pytest -q`
    - 134 passed.
  - `.venv/bin/ruff check cockpit/cli.py tests/test_cli.py tests/test_targets_topology.py`
    - Passed.
  - `bash -n scripts/fetch-cran-tarballs.sh`
    - Passed.
  - `python3 scripts/smoke_dashboard_dom.py --timeout 90`
    - Passed before this patch batch.
  - GitHub Actions on `7f2f94c`:
    - CI: success.
    - version-guard: success.
  - Collect `29020120306`:
    - success, produced `36c3559`.
    - Snapshot generator now records `run_id: "29020120306"`.
  - Pages rerun `29020578511`:
    - success on `36c3559`.
    - Public `current.json` and `manual-actions.json` hashes match local.
    - Public `current.json` exposes `generator.run_id: "29020120306"`.

## Cockpit state after collect

- Local `data/current.json` generated at `2026-07-09T13:07:04.949731+00:00`.
- Summary: `green=96`, `stale=1`, `pending=4`, `missing=0`, `broken=0`,
  `unknown=0`, `excluded=1`.
- Non-green tracked targets remain manual CRAN states:
  - `n4m` pending.
  - `pls4all` pending.
  - `nirs4allio` pending.
  - `nirs4alldatasets` stale at 0.2.0.
  - `nirs4all` CRAN aggregate pending.
- Public manual actions remain 6 pending:
  - 1 blocker: manual smoke-test of the Studio Windows RC installer.
  - 5 important CRAN submission/review actions.

## Remaining risks

- The E2E evidence is strict and fresh for the current artifact set, but several
  scenarios remain deterministic-fixture based until larger external reference
  corpora are available.
- Full Python-reference parity was intentionally not launched in this batch.
