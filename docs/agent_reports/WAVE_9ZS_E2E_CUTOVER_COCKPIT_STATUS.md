# WAVE 9ZS - E2E, cutover, and cockpit status

Date: 2026-07-10

## Scope

- Closed the CI regression that made the Web/WASM repository-refit scenario fail on a vendored `nirs4all-ui` shim drift.
- Re-ran the selected Web/Python/native scenario and then the full ready cross-language E2E suite.
- Updated cutover gate metadata to target the current `nirs4all-web/web-app` layout instead of the retired `studio-lite` path.
- Rechecked the public cockpit and R-universe state after the datasets 0.3.6 release, diagnosed the R-universe failures, and published the datasets 0.3.7 then 0.3.8 fixes.

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
- Fresh GitHub workflow-dispatch ready runtime suite:
  workflow `Cross-language E2E scenarios` run `29093521760` passed on `2d86bc8acfb4c1424b43e48e57d91b8b6239ca0f`.
  The run installed executed E2E dependencies, built strict methods runtime artifacts, installed strict R runtime dependencies, executed ready scenarios, verified ready artifacts, and checked the committed runtime evidence ledger.
- GitHub cutover tooling:
  workflow `cutover-gates` validate run `29089122983` passed on `2880712ffae326022f846a96effbbe1fe239ada2`.
- Local contract checks:
  `python3.11 -m pytest -q tests/test_e2e_scenarios.py tests/test_cutover_state_gate.py` passed (`141 passed`).
  `python3.11 scripts/n4a_e2e_scenarios.py validate` passed (`OK: 11 cross-language E2E scenarios`).
- Read-only E2E audit confirmed 11 strict/ready scenarios in `docs/contracts/e2e/cross-language-scenarios.n4a.json` and `latest-runtime-evidence-ledger.n4a.json`; the committed ledger records `11/11` scenarios, `70` artifacts, and `0` failures. Current local artifact freshness is weaker (`2/11` still within the 4-hour window), so the authoritative runtime proof remains CI run `29088345220` until a fresh local execute batch is run.
- Read-only UI audit confirmed `nirs4all-ui` `v0.1.12` exports shared `score`, `runtime`, `dataset`, `components`, `brand`, `styles`, `lab`, `datasetBuilder`, and `assets/*` surfaces; public Pages serves the component/assets site and brand/style/motion assets. `nirs4all-web` and `nirs4all-studio` consume the shared UI without importing the quality/lab surfaces used by `nirs4all-quality`.
- Read-only core/lite audit confirmed `nirs4all-core` is canonical across repo metadata, submodules, cockpit, PyPI, npm, crates, R-universe, and GitHub Release `v0.3.11`; `nirs4all-lite` remains public only as retired audit/history. The audit found stale ReadTheDocs content, so RTD build `33530873` was triggered and completed successfully on core commit `325f6b9`; the refreshed public HTML no longer contains `nirs4all_lite` or `nirs4all-lite`.
- `nirs4all-lite` local guidance was tightened in commit `2448915`: `AGENTS.md` now describes the checkout as retired audit material only and removes the previous alias/transition wording. GitHub `version-guard` `29093498347` and full `CI` `29093498304` passed, including strict parity, Rust, Python 3.11/3.12, R package, npm/WASM, and Octave/MATLAB smoke jobs.

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
- Manual dispatch attempts against both `r-universe/gbeurier` `Update universe` and `r-universe-org/control-room` `Sync all universes` returned GitHub `403 Resource not accessible by personal access token`; the remaining path is R-universe's own scheduled sync or an authorized maintainer dispatch.
- A third config change was pushed to `GBeurier/GBeurier.r-universe.dev` (`bca4cdb`) to pin `nirs4alldatasets` directly to tag `v0.3.7`; R-universe supports branch/tag names in the `branch` field, so this removes the `*release` lookup as a possible source of delay.
- R-universe run `29094507046` was triggered from that explicit tag pin and published `nirs4alldatasets` `0.3.7` at `RemoteSha` `784c2872662204e820c8cf6b58d01bc4788148c0`; the public API now serves `0.3.7`.
- The same R-universe run ended with global `failure` because the `Build R-release for Wasm` matrix leg failed. Source, Linux x86_64/arm64, macOS arm64, macOS x86_64, and Windows legs completed successfully; the Wasm log shows `configure` found `/opt/R/4.6.0/lib/R/library/rwasm/bin/cargo` but could not read its version, then rejected the build as missing `Cargo >= 1.85.0`.
- The cockpit was refreshed in `nirs4all-cockpit` commit `fdc13a9`: `nirs4all-datasets` now shows source/tag/release/PyPI/npm/crates/GitHub Release at `0.3.7`, while the R-universe target remains honestly `stale` at `0.3.5` and the CRAN target remains manual `pending`.
- Cockpit validation for `fdc13a9` is green: local `pytest -q` (`146 passed`), `ruff check .`, Chrome dashboard smoke, plus GitHub `ci` `29091568141`, `pages` `29091568648`, and `version-guard` `29091567452`.
- Cockpit manual action metadata was refreshed in `nirs4all-cockpit` commit `cc6ec1d`: `runiverse-datasets-rebuild` now points at `nirs4all-datasets@784c2872662204e820c8cf6b58d01bc4788148c0` and `GBeurier/GBeurier.r-universe.dev@743ebe47da7e3b9be16a7c4f1216ce4125a6c3a0`; GitHub `ci` `29093186189`, `pages` `29093186188`, and `version-guard` `29093187017` passed.
- Cockpit manual action metadata was refreshed again in `nirs4all-cockpit` commit `d3636e2`: `runiverse-datasets-rebuild` now points at `GBeurier/GBeurier.r-universe.dev@bca4cdb0a5084abe09a88a86a3856233805dfcdc`; local `pytest -q` passed (`146 passed`) and `ruff check .` passed.
- Cockpit snapshot/manual actions were refreshed in `nirs4all-cockpit` commit `35c7635`: `nirs4all-datasets` rollup is now `green`, R-universe `nirs4alldatasets` is `0.3.7`, global stale count is `0`, and `runiverse-datasets-rebuild` is auto-resolved. Local cockpit validation passed with `pytest -q` (`146 passed`) and `ruff check .`.
- `nirs4all-datasets` commit `2b074472` and tag `v0.3.8` fix the R-universe WebAssembly failure by accepting `rwasm` Cargo/rustc wrappers only during Wasm configure/build contexts; native source installs still require readable Cargo/rustc versions.
- Datasets 0.3.8 local validation passed with `scripts/bump_version.sh --check`, `ruff check .`, `python3.11 -m pytest -q` (`234 passed, 3 skipped`), `cargo fmt --all --check`, `cargo test --workspace --offline`, targeted R Wasm configure tests (`3 passed`), `sh -n bindings/r/nirs4alldatasets/configure`, and a Unix `Makevars` clean dry-run.
- Datasets 0.3.8 release validation is green on GitHub: `CI`, `ABI Surface`, `version-sync`, `version-guard`, `Site`, `release-python`, `release-npm`, `release-crates`, `release-r`, `release-matlab`, and `release-source` completed successfully. The `release-r` matrix passed Linux release/devel, macOS arm64 release, Windows release, built `nirs4alldatasets_0.3.8.tar.gz`, and attached it to GitHub Release `v0.3.8`.
- Published datasets registries report `0.3.8` for PyPI, npm, `nirs4all-datasets-core`, `nirs4all-datasets-capi`, and `nirs4all-datasets-cli`; GitHub Release `v0.3.8` includes the R tarball, source archives, C-ABI artifacts, Python wheels/sdist, MATLAB/Octave zip, SBOM, and checksums.
- `GBeurier/GBeurier.r-universe.dev` commit `9d7341a` pins `nirs4alldatasets` to tag `v0.3.8`. Empty retrigger commit `5511c44` was also pushed after no generated R-universe 0.3.8 run appeared; direct dispatch of `r-universe/gbeurier` `Update universe` still returns GitHub `403 Resource not accessible by personal access token`.
- R-universe has not yet triggered the 0.3.8 rebuild; the public API still serves `RemoteRef` `v0.3.7`, `RemoteSha` `784c2872662204e820c8cf6b58d01bc4788148c0`, and version `0.3.7`.
- Cockpit snapshot/manual actions were refreshed after the 0.3.8 release: `nirs4all-datasets` source/tag/release/PyPI/npm/crates/GitHub Release are `0.3.8`, the R-universe target is honestly `stale` at `0.3.7`, the CRAN target remains manual `pending`, and global summary is `green=96`, `stale=1`, `pending=5`, `excluded=1`. Local cockpit validation passed with `pytest -q` (`146 passed`), `ruff check .`, and `validate-targets`.
- `nirs4all-org` was refreshed in commit `0520cbd` to make the offline fallback badge for `nirs4all-ui` match `v0.1.12`; GitHub `version-guard` `29092357404` and Pages deployment `29092355995` passed.

## CRAN submission kit

- Prepared a local CRAN submission kit at `/home/delete/nirs4all/cran-submission-kit/2026-07-10` without committing binary tarballs to Git.
- Included release tarballs, SHA-256 checksums, release metadata, and copy/paste CRAN form text for `n4m` `1.0.9`, `pls4all` `1.0.9`, `nirs4allio` `0.1.11`, `nirs4alldatasets` `0.3.8`, and the aggregate `nirs4all` `0.3.11`; `nirs4allformats` is intentionally excluded.
- The kit records that this WSL host has no local `R` binary, so no local `R CMD check --as-cran` was run here; it provides the exact commands to run before upload.
- CRAN currently reports `nirs4alldatasets` as removed/archived on `2026-07-04` because issues were not corrected in time. The archived `2026-07-03` checks show macOS installation errors for `0.2.0`, with the visible BDR log reporting missing `cargo`. The kit flags macOS Cargo/rustc availability as a pre-upload blocker for `nirs4alldatasets` `0.3.8`.
- The kit now contains `nirs4alldatasets_0.3.8.tar.gz` from GitHub Release `v0.3.8`; `sha256sum -c checksums/SHA256SUMS` passes for all five tarballs.

## Decisions

- The failed older E2E runs are superseded by run `29093521760`; the only newer ecosystem commit after that run is report-only (`36b8e82`), with push validation green.
- The full Python-reference parity batch was not relaunched in this wave; the user asked to reserve full parity for large batches, and the current batch's runtime gate is the cross-language E2E layer.
- Strict cutover execution remains a prepared-workspace gate. GitHub `validate` proves the runner/manifest contract, while `strict` still requires the selected RC worktrees to exist at the expected release workspace paths.

## Risks / follow-up

- R-universe still serves `nirs4alldatasets` `0.3.7` while the config repo is pinned to `v0.3.8` and retriggered at `5511c44`; wait for the generated universe rebuild and then refresh the cockpit when the public API serves `0.3.8`.
- If a production cutover decision is requested, run the strict cutover gate in a prepared RC workspace or update the cutover manifest to a new release workspace topology before treating strict GitHub execution as authoritative.
- Studio Windows RC manual smoke, CRAN submissions, and a fresh selected-head strict cutover run remain outside the automated proof set.
