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

## Cockpit and R-universe status

- Public cockpit snapshot timestamp: `2026-07-10T10:03:45.403130+00:00`.
- Public cockpit still reports `nirs4all-datasets` rollup `stale`.
- R-universe build run `29085264823` failed for `nirs4alldatasets 0.3.6` because `bindings/r/nirs4alldatasets/src/Makevars` assumed `TMPDIR` was always set by R:
  `nirs4alldatasets: ERROR - TMPDIR is not set by R; cannot create build-local Cargo directories`.
- `nirs4all-datasets` commit `784c2872` and tag `v0.3.7` fix the Unix Makevars temp root fallback (`TMPDIR` -> `TEMP` -> `TMP` -> `/tmp`) and bump every synced manifest to `0.3.7`.
- Datasets 0.3.7 release validation is green:
  `CI` `29089671011`, `ABI Surface` `29089671013`, `version-sync` `29089670940`, `version-guard` `29089671001`, `Site` `29089670999`, `release-python` `29089672317`, `release-npm` `29089672354`, `release-crates` `29089672766`, `release-r` `29089672465`, `release-matlab` `29089673448`, and `release-source` `29089673333`.
- Published datasets registries now report `0.3.7` for PyPI, npm, `nirs4all-datasets-core`, `nirs4all-datasets-capi`, and `nirs4all-datasets-cli`; GitHub Release `v0.3.7` includes source, C-ABI, Python wheels/sdist, R tarball, MATLAB/Octave zip, SBOM, and checksums.
- R-universe still serves `nirs4alldatasets` `0.3.5` at `RemoteSha` `67d47c557bcb8770506409d2c688cb3b60384c18` until its generated universe repo resynchronizes.
- A config-repo trigger commit was pushed to `GBeurier/GBeurier.r-universe.dev` (`c230d53`), but direct `r-universe/gbeurier` workflow dispatch is not available with the current auth. The cockpit manual action for `runiverse-datasets-rebuild` remains valid; no cockpit refresh was pushed because R-universe still has not changed.

## Decisions

- The failed older E2E runs are superseded by run `29088345220` on the current head.
- The full Python-reference parity batch was not relaunched in this wave; the user asked to reserve full parity for large batches, and the current batch's runtime gate is the cross-language E2E layer.
- Strict cutover execution remains a prepared-workspace gate. GitHub `validate` proves the runner/manifest contract, while `strict` still requires the selected RC worktrees to exist at the expected release workspace paths.

## Risks / follow-up

- R-universe is the only observed external publication lag for `nirs4all-datasets`; recheck and refresh cockpit once it serves `0.3.7`.
- If a production cutover decision is requested, run the strict cutover gate in a prepared RC workspace or update the cutover manifest to a new release workspace topology before treating strict GitHub execution as authoritative.
