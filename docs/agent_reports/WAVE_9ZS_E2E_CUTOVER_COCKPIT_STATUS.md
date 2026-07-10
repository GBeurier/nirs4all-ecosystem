# WAVE 9ZS - E2E, cutover, and cockpit status

Date: 2026-07-10

## Scope

- Closed the CI regression that made the Web/WASM repository-refit scenario fail on a vendored `nirs4all-ui` shim drift.
- Re-ran the selected Web/Python/native scenario and then the full ready cross-language E2E suite.
- Updated cutover gate metadata to target the current `nirs4all-web/web-app` layout instead of the retired `studio-lite` path.
- Rechecked the public cockpit and R-universe state after the datasets 0.3.6 release, diagnosed the R-universe failure, and published the datasets 0.3.7 fix.

## Files changed

- `nirs4all-ui` gitlink advanced to `1450b5a` so the ecosystem checkout matches the Web shim source used by `nirs4all-web`.
- `.github/workflows/cross-language-e2e.yml` now skips R setup for selected non-R scenarios and filters only the workspace-wide readiness tests that require R in plan/non-R selected runs.
- `docs/contracts/cutover/drop-gates.n4a.json` now uses `_worktrees/RC-v1-web/web-app` for `web_runtime_contract`.
- `tests/test_e2e_scenarios.py` and `tests/test_cutover_state_gate.py` were updated to lock those workflow and cutover expectations.

## Validation

- Local selected scenario:
  `python3.11 scripts/n4a_e2e_scenarios.py run e2e-python-reopen-paper-repository-refit --execute`
  passed, including Web/WASM import of the repository best-pipeline handoff with max delta `3.0233593406592263e-12`.
- GitHub selected scenario:
  workflow `Cross-language E2E scenarios` run `29087738513` passed on `main`.
- GitHub full ready runtime suite:
  workflow `Cross-language E2E scenarios` run `29088345220` passed on `2880712ffae326022f846a96effbbe1fe239ada2`.
  The run executed ready scenarios, verified ready scenario artifacts, and checked the committed runtime evidence ledger.
- GitHub cutover tooling:
  workflow `cutover-gates` validate run `29089122983` passed on `2880712ffae326022f846a96effbbe1fe239ada2`.
- Local contract checks:
  `python3.11 -m pytest -q tests/test_e2e_scenarios.py tests/test_cutover_state_gate.py` passed (`141 passed`).
  `python3.11 scripts/n4a_e2e_scenarios.py validate` passed (`OK: 11 cross-language E2E scenarios`).
- Read-only E2E audit confirmed 11 strict/ready scenarios in `docs/contracts/e2e/cross-language-scenarios.n4a.json` and `latest-runtime-evidence-ledger.n4a.json`; the committed ledger records `11/11` scenarios, `70` artifacts, and `0` failures. Current local artifact freshness is weaker (`2/11` still within the 4-hour window), so the authoritative runtime proof remains CI run `29088345220` until a fresh local execute batch is run.
- Read-only UI audit confirmed `nirs4all-ui` `v0.1.12` exports shared `score`, `runtime`, `dataset`, `components`, `brand`, `styles`, `lab`, `datasetBuilder`, and `assets/*` surfaces; public Pages serves the component/assets site and brand/style/motion assets. `nirs4all-web` and `nirs4all-studio` consume the shared UI without importing the quality/lab surfaces used by `nirs4all-quality`.
- Read-only core/lite audit confirmed `nirs4all-core` is canonical across repo metadata, submodules, cockpit, PyPI, npm, crates, R-universe, and GitHub Release `v0.3.11`; `nirs4all-lite` remains public only as retired audit/history. The audit found stale ReadTheDocs content, so RTD build `33530873` was triggered and completed successfully on core commit `325f6b9`; the refreshed public HTML no longer contains `nirs4all_lite` or `nirs4all-lite`.

## Cockpit and R-universe status

- Public cockpit snapshot timestamp: `2026-07-10T12:02:58.271015+00:00`.
- Public cockpit still reports `nirs4all-datasets` rollup `stale`, specifically because R-universe still serves `0.3.5`.
- R-universe build run `29085264823` failed for `nirs4alldatasets 0.3.6` because `bindings/r/nirs4alldatasets/src/Makevars` assumed `TMPDIR` was always set by R:
  `nirs4alldatasets: ERROR - TMPDIR is not set by R; cannot create build-local Cargo directories`.
- `nirs4all-datasets` commit `784c2872` and tag `v0.3.7` fix the Unix Makevars temp root fallback (`TMPDIR` -> `TEMP` -> `TMP` -> `/tmp`) and bump every synced manifest to `0.3.7`.
- Datasets 0.3.7 release validation is green:
  `CI` `29089671011`, `ABI Surface` `29089671013`, `version-sync` `29089670940`, `version-guard` `29089671001`, `Site` `29089670999`, `release-python` `29089672317`, `release-npm` `29089672354`, `release-crates` `29089672766`, `release-r` `29089672465`, `release-matlab` `29089673448`, and `release-source` `29089673333`.
- Published datasets registries now report `0.3.7` for PyPI, npm, `nirs4all-datasets-core`, `nirs4all-datasets-capi`, and `nirs4all-datasets-cli`; GitHub Release `v0.3.7` includes source, C-ABI, Python wheels/sdist, R tarball, MATLAB/Octave zip, SBOM, and checksums.
- R-universe still serves `nirs4alldatasets` `0.3.5` at `RemoteSha` `67d47c557bcb8770506409d2c688cb3b60384c18` until its generated universe repo resynchronizes.
- A config-repo trigger commit was pushed to `GBeurier/GBeurier.r-universe.dev` (`c230d53`), but direct `r-universe/gbeurier` workflow dispatch is not available with the current auth.
- A second config change was pushed to `GBeurier/GBeurier.r-universe.dev` (`743ebe4`) to track `nirs4alldatasets` from the latest GitHub Release via `branch: "*release"` instead of the floating `main` branch.
- The cockpit was refreshed in `nirs4all-cockpit` commit `fdc13a9`: `nirs4all-datasets` now shows source/tag/release/PyPI/npm/crates/GitHub Release at `0.3.7`, while the R-universe target remains honestly `stale` at `0.3.5` and the CRAN target remains manual `pending`.
- Cockpit validation for `fdc13a9` is green: local `pytest -q` (`146 passed`), `ruff check .`, Chrome dashboard smoke, plus GitHub `ci` `29091568141`, `pages` `29091568648`, and `version-guard` `29091567452`.
- `nirs4all-org` was refreshed in commit `0520cbd` to make the offline fallback badge for `nirs4all-ui` match `v0.1.12`; GitHub `version-guard` `29092357404` and Pages deployment `29092355995` passed.

## Decisions

- The failed older E2E runs are superseded by run `29088345220` on the current head.
- The full Python-reference parity batch was not relaunched in this wave; the user asked to reserve full parity for large batches, and the current batch's runtime gate is the cross-language E2E layer.
- Strict cutover execution remains a prepared-workspace gate. GitHub `validate` proves the runner/manifest contract, while `strict` still requires the selected RC worktrees to exist at the expected release workspace paths.

## Risks / follow-up

- R-universe is the only observed external publication lag for `nirs4all-datasets`; recheck and refresh cockpit once it serves `0.3.7`.
- If a production cutover decision is requested, run the strict cutover gate in a prepared RC workspace or update the cutover manifest to a new release workspace topology before treating strict GitHub execution as authoritative.
- Studio Windows RC manual smoke, CRAN submissions, and a fresh selected-head strict cutover run remain outside the automated proof set.
