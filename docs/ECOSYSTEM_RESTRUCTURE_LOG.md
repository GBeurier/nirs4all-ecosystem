# nirs4all Ecosystem Restructure Log

Started: 2026-06-11

## Target Model

- `nirs4all-drafts`: private working area for active manuscripts, reviews, journal scouting, and lab-to-paper drafting material.
- `nirs4all-papers`: public repository for deposited papers, PDFs, and reproducible public code bundles once a draft and its lab work are accepted for publication/release.
- `nirs4all-web`: standalone browser client built from the WASM stack. This is the role currently implemented by the existing `nirs4all-lite` checkout.
- `nirs4all-lite`: canonical low-level aggregate distribution of `dag-ml`, `dag-ml-data`, `nirs4all-formats`, `nirs4all-io`, `nirs4all-datasets`, and `nirs4all-methods`, with native/idiomatic bindings for Rust, Python (`nirs4all-lite` package name), R, MATLAB/Octave, and JavaScript/WASM (`nirs4all` package name outside Python).
- `nirs4all-org`: static website repository for `nirs4all.org`, replacing the ambiguous `nirs4all-webpage` name.

## Visibility Policy

Working assumption for this migration:

- private: `nirs4all-drafts`
- public: `nirs4all-papers`, once it contains only deposited/reproducible material

Note: the initial request also said "`nirs4all-drafts` and `nirs4all-papers` are the only private repositories", but the surrounding paper workflow says deposited papers and reproducibility kits should be public and permanent. Do not publish sensitive draft material into the new public `nirs4all-papers`.

## Initial State Observed

- `GBeurier/nirs4all-drafts` does not currently exist on GitHub.
- Local `nirs4all-drafts/` is not a git repository and only contains `.codegraph/`.
- `GBeurier/nirs4all-papers` exists and is private; local checkout has active uncommitted draft work.
- `GBeurier/nirs4all-lite` exists and is public; local checkout contains the browser app under `studio-lite/`.
- `GBeurier/nirs4all-web` does not exist.
- `GBeurier/nirs4all-webpage` exists and is public; it serves `nirs4all.org`.
- `GBeurier/nirs4all-org` and `GBeurier/nirs4all.org` do not exist.
- `GBeurier/nirs4all-cluster`, `GBeurier/nirs4all-dist`, and `GBeurier/nirs4all-lab` were initially private.

## Remote State After 2026-06-11 Execution

- `GBeurier/nirs4all-papers` was renamed to `GBeurier/nirs4all-drafts` and remains private.
- `GBeurier/nirs4all-lite` was renamed to `GBeurier/nirs4all-web` and remains public.
- `GBeurier/nirs4all-webpage` was renamed to `GBeurier/nirs4all-org` and remains public.
- New public `GBeurier/nirs4all-papers` was created and seeded from local `nirs4all-papers/`.
- New public `GBeurier/nirs4all-lite` was created and seeded from local `nirs4all-lite/`.
- The temporary `GBeurier/GBeurier.github.io` user-site redirect was retired; `https://nirs4all.org/` is the canonical public site.
- `GBeurier/nirs4all-org` Pages is configured with `CNAME=nirs4all.org`, source `main:/`, HTTPS enforced, and status `built`.
- `GBeurier/nirs4all-org` was updated after the split to keep public ecosystem claims conservative (`nirs4all-lite` build scaffold, `nirs4all-cluster` alpha prototype, `nirs4all-arena` browsable benchmark rather than public submission platform) and its Pages workflow now uses the current GitHub Actions majors.
- `GBeurier/nirs4all-cluster` was audited, documented as public alpha, and made public.
- `GBeurier/nirs4all-dist` was audited and deleted: it only contained a placeholder README for a future distribution factory, a role now owned by `nirs4all-lite` release/binding infrastructure.
- `GBeurier/nirs4all-web` was cleaned of the legacy `single-page-WASM` prototype; the active `studio-lite` app passes typecheck, unit tests, catalog validation, served/single-file builds, and browser smokes.
- `GBeurier/nirs4all-lite` was hardened with release/build scaffolding for Rust, Python, npm/WASM, R, and MATLAB/Octave. CI is green across Rust, Python 3.11/3.12, npm, R `R CMD build/check`, and Octave smoke/package zip.
- `GBeurier/nirs4all-lite` CI now uploads downloadable artifacts for every target: Rust crate, Python wheel/sdist, npm tarball, R source tarball, and MATLAB/Octave zip. The final green run produced `r-source/nirs4all_0.0.0.tar.gz`.
- `GBeurier/GBeurier.r-universe.dev` was updated to include `dagmldata`, `nirs4alldatasets`, and the `nirs4all` R aggregate from `nirs4all-lite/bindings/r`.
- `GBeurier/nirs4all-lite` now has a JSON/YAML parser contract for the full Python `nirs4all` definition envelope: direct step lists, `pipeline`, `steps`, JSON/YAML paths, and JSON/YAML text. The shared portable fixtures use the `nirs4all/examples/pipeline_samples` syntax for Kennard-Stone, SNV, Savitzky-Golay, and PLS `_range_`/`param` sweeps. Python, Rust, npm/WASM, R, and MATLAB/Octave expose the contract. CI run `27385368565` is green across Rust, Python 3.11/3.12, npm, R, and MATLAB/Octave; local 2026-06-12 checks revalidated Python, Rust, and npm after adding the extra fixtures.
- 2026-06-12 local follow-up: `nirs4all-datasets` WASM was confirmed to exist and to be browser-scoped (`resolve` + `sha256`). A web-target package was generated with `wasm-pack --target web`, vendored into `nirs4all-web/studio-lite/src/engine/wasm/datasets`, and wired through the `nirs4all-lite` npm aggregate using the real scoped package name `@nirs4all/datasets-wasm`.
- 2026-06-12 local follow-up: `nirs4all-web` now routes datasets through the aggregate shim, removes the active finetuning UI/runtime path, migrates legacy imported `finetune` specs to finite `model.sweeps`, and exposes sweeps on branch/DAG-container operator params as well as model and linear-chain params.
- 2026-06-12 local follow-up: `nirs4all-web` vendors the `nirs4all-lite` npm aggregate under `studio-lite/vendor/nirs4all`, so its GitHub Pages workflow no longer depends on a sibling checkout of `nirs4all-lite`.
- 2026-06-12 local follow-up: `nirs4all-datasets` CI was fixed after the WASM doc change. The workflow now recreates the uv virtualenv idempotently and runs gates with `uv run --no-sync`, avoiding CI attempts to resolve local workspace-only `[tool.uv.sources]` siblings that are absent on GitHub runners.
- 2026-06-12 local follow-up: Claude Opus "fable" completed a read-only review of the lite/web integration. No blocker was found. Residual risks logged: MATLAB/Octave YAML parser is fixture-shaped rather than a full YAML parser, the portable allowlist is duplicated across bindings without a drift gate, R/Octave local checks were not available in this environment, and npm upstream package naming should be normalized later.
- 2026-06-12 local follow-up: `nirs4all-datasets` WASM was rechecked from source. `wasm-pack build` passes for `--target nodejs` and `--target web`, and the Node smoke confirms `resolve`, `sha256`, and `abiVersion`. The README now uses the real package name `@nirs4all/datasets-wasm`.
- 2026-06-12 local follow-up: `nirs4all-methods` JS/WASM now exposes `computeSplitIndices()` in addition to the legacy mask API, preserving the native C ABI train/test order required for strict Kennard-Stone parity. The Savitzky-Golay WASM dispatcher also accepts an explicit mode/cval so lite can request SciPy/nirs4all-compatible `interp`.
- 2026-06-12 local follow-up: `nirs4all-methods` now declares the existing `n4m_config_set_rng_kind` / `n4m_config_get_rng_kind` C ABI functions in the public PLS header, exposes ordered split indices to JS/WASM, accepts explicit Savitzky-Golay mode/cval in WASM, and fixes the CI portability fallout across Linux, macOS, Windows MSVC, MinGW, CUDA, parity, ABI, and cross-binding gates.
- 2026-06-12 local follow-up: `nirs4all-lite` WASM now has an executable portable pipeline runner for the initial subset (Kennard-Stone, SNV, Savitzky-Golay, PLS, and `n_components` sweeps). The new Python oracle covers four shared JSON/YAML fixtures and the WASM test compares split indices, targets, RMSE, predictions, and selected sweep component against full Python `nirs4all`.
- 2026-06-12 local follow-up: `nirs4all-web` now syncs `studio-lite/vendor/nirs4all` from `nirs4all-lite/bindings/wasm` via `scripts/sync-lite-shim.mjs`, checks for drift with `npm run check:lite-shim`, and stages the updated methods WASM that includes ordered split indices. Local typecheck, Vitest, catalog validation, served build, and single-file build pass.
- 2026-06-12 final follow-up: GitHub Actions are green on `nirs4all-datasets` commit `45020ad`, `nirs4all-lite` commit `286ad08`, `nirs4all-web` commit `16b500a`, and `nirs4all-methods` commit `0a1b9a2`. `https://nirs4all.org/` responds with HTTP 200 from GitHub Pages.
- 2026-06-12 continuation: `nirs4all-lite` Python now has an executable portable pipeline runner backed by the existing `nirs4all-methods` Python bindings (`n4m.sklearn` + `pls4all.sklearn`). The strict Python parity gate runs the same four full-`nirs4all` JSON/YAML oracle fixtures as WASM and compares split indices, targets, RMSE, predictions, and selected sweep components.
- 2026-06-12 continuation: `nirs4all-web` now has a Vitest parity check that executes the shared oracle through the vendored `nirs4all-lite` aggregate import, not through independent per-package orchestration. Local web green gate was rerun: typecheck, Vitest, catalog validator, served build, full `tests/*smoke.mjs` Chromium suite, single-file build, and single-file smoke all passed.
- 2026-06-12 continuation: `nirs4all-lite` local package gates were rerun for Python wheel/sdist, npm tarball, Rust crate package verification, and MATLAB/Octave zip. R `CMD build/check` and Octave/MATLAB runtime smoke could not run locally because those toolchains are not installed in this environment; they remain CI/runner checks.
- 2026-06-12 continuation: `nirs4all-lite` CI now has an explicit `strict-parity` job. It checks out `nirs4all-methods`, forces the WASM oracle test via `NIRS4ALL_LITE_REQUIRE_METHODS_PARITY=1`, builds native `libn4m`, and forces the Python oracle test against the compiled methods bindings so missing methods artefacts can no longer produce a silent skip-green.
- 2026-06-12 continuation finalization: `nirs4all-lite` commit `f61d75d` is green on CI run `27392981527`, including the source-built methods WASM + native `libn4m` `strict-parity` job. `nirs4all-web` commit `4c771c2` is green on Pages run `27392548033`. `nirs4all-ecosystem` gitlinks were advanced to `nirs4all-datasets` `45020ad`, `nirs4all-methods` `0a1b9a2`, `nirs4all-lite` `f61d75d`, and `nirs4all-web` `4c771c2`.
- 2026-06-12 final verification: `nirs4all-datasets` commit `0cd44d5` adds an explicit WASM/JS green gate that builds Node and browser packages, runs the Node smoke, and validates the npm tarball contents. The public npm package name is normalized to `@nirs4all/datasets-wasm` across `nirs4all-datasets`, `nirs4all-lite`, `nirs4all-web`, and this ecosystem log; the longer wasm-pack crate-derived name is local/generated only.
- 2026-06-12 final verification: `nirs4all-methods` commit `1c84cd6` keeps the new R preprocessing wrapper in the Windows object list. CI is green for CI, ABI Surface, Coverage, docs, Parity gate, version-sync, Cross-binding parity, and Sanitizers.
- 2026-06-12 final verification: `nirs4all-lite` commit `c0a7774` extends strict portable parity to the R aggregate binding, makes R parity fixtures drift-checked against the shared fixtures, and keeps SNV `ddof = 0` explicit. CI is green for Rust, Python 3.11/3.12, npm, R, MATLAB/Octave, and strict-parity.
- 2026-06-12 final verification: `nirs4all-web` commit `102c370` vendors the updated lite aggregate, aliases `@nirs4all/datasets-wasm`, and passes local `check:lite-shim`, targeted Vitest, typecheck, catalog validation, and build. GitHub Pages deploy is green, and `https://nirs4all.org/` and `https://web.nirs4all.org/` return HTTP 200.
- 2026-06-12 continuation: `nirs4all-lite` Rust now executes the same four full-Python oracle fixtures through a caller-supplied `libn4m` (`run_portable_pipeline_with_library`). The Rust test compares split indices, targets, RMSE, predictions, and selected `n_components`; CI strict-parity invokes it with `NIRS4ALL_METHODS_LIB`.
- 2026-06-12 continuation: `nirs4all-lite` JavaScript/WASM now returns a serialized selected PLS model from `runPortablePipeline()` and exposes `predictPortablePipeline()`. The WASM oracle test reuses the fitted model and checks held-out predictions against the selected run output.
- 2026-06-12 continuation: `nirs4all-web` runtime now has a strict direct path for portable regression pipelines (`KennardStone`, `StandardNormalVariate`, `SavitzkyGolay`, `PLS`, `n_components` range sweep). Compatible runs execute through the vendored `nirs4all-lite` aggregate instead of rebuilding the pipeline from per-package calls; unsupported pipelines stay on `dag-ml + libn4m`.
- 2026-06-12 continuation: MATLAB/Octave execution parity was audited by Claude Opus read-only. Existing `nirs4all-methods` MATLAB APIs cover PLS (`n4m_pls_fit_mex`, `n4m_method_fit_mex`, `n4m_model_fit_mex`, `pls4all.Regression`, `pls4all.pls_fit`), but there are no public MEX shims for `n4m_split_kennard_stone_*`, SNV, or Savitzky-Golay. Required follow-up belongs first in `nirs4all-methods` (`n4m_preprocess_mex.c`, `n4m_split_mex.c`, and `pls4all.snv` / `pls4all.savgol` / `pls4all.kennard_stone` wrappers), then in `nirs4all-lite` (`+nirs4all/executePipeline.m` and parity test).
- 2026-06-12 continuation: Claude Opus "fable" completed the requested read-only final integration review across `nirs4all-lite`, `nirs4all-web`, and this log. It found no blockers. Local validation also reran `nirs4all-lite` WASM strict parity, web `check:lite-shim`, typecheck, Vitest, build, and the full served Chromium `tests/*smoke.mjs` suite successfully.
- 2026-06-12 MATLAB/Octave parity closeout: `nirs4all-methods` commit `288e2a8` adds public `+pls4all` MEX shims/wrappers for SNV, Savitzky-Golay, and Kennard-Stone, and aligns R/MATLAB Savitzky-Golay defaults to full Python `nirs4all` (`polyorder = 3`). CI is green for CI, ABI Surface, Coverage, docs, Parity gate, version-sync, Cross-binding parity, and Sanitizers.
- 2026-06-12 MATLAB/Octave parity closeout: `nirs4all-lite` commit `5894c4a` promotes MATLAB/Octave from parser-only to strict execution parity through `nirs4all.runPortablePipeline()`. The CI `strict-parity` job now builds methods MEX shims and runs WASM, Rust, Python, R, and MATLAB/Octave against the same four full-Python oracle fixtures. CI run `27396764682` is green across Rust, Python 3.11/3.12, npm, R, MATLAB/Octave, and strict-parity.
- 2026-06-12 local closeout: local conda toolchains revalidated `nirs4all-methods` Octave MEX build + `test_parity`, `nirs4all-lite` `make test-matlab-parity`, `make test-r-parity` with a freshly installed local `n4m`, `R CMD check --no-manual bindings/r`, strict Python parity, strict Rust parity, npm/WASM oracle tests, `cargo fmt`, `cargo clippy`, and `cargo test`.

## Local State After Split

- Local checkout `nirs4all-web/` now contains the former `nirs4all-lite` browser/WASM app.
- Local checkout `nirs4all-org/` now contains the former `nirs4all-webpage` static site.
- Local checkout `nirs4all-drafts/` now contains the former private `nirs4all-papers` draft/manuscript repository.
- Local checkout `nirs4all-lite/` is a buildable aggregate repository with Rust, Python, R, MATLAB/Octave, and JS/WASM binding surfaces plus release docs and CI gates.
- Local checkout `nirs4all-papers/` is a new git repository scaffold for public deposited papers and reproducibility kits.
- The old non-git `.codegraph` stub that occupied `nirs4all-drafts/` was moved to `nirs4all-drafts.codegraph-stub-20260611/`.

## Task Log

| Status | Task | Notes |
| --- | --- | --- |
| done | Inventory local repos and GitHub metadata | Used `git status` and `gh repo view --json isPrivate`. |
| done | Plan safe GitHub rename sequence | Keep remote operations separate because repo visibility changes can expose private material. |
| done | Move current `nirs4all-lite` role to `nirs4all-web` locally | Existing app remains browser/WASM client; package/workflow text now says `nirs4all-web`. |
| done | Recreate `nirs4all-lite` as canonical aggregate distribution | Added testable Rust/Python/JS registries, R/MATLAB skeletons, binding docs, parity plan, and CI placeholder. |
| done | Rename `nirs4all-webpage` to `nirs4all-org` locally | Prefer `nirs4all-org` over `nirs4all.org` for tooling compatibility; keep CNAME as `nirs4all.org`. |
| done | Re-home current private `nirs4all-papers` as `nirs4all-drafts` locally | Preserved active draft history and uncommitted work; did not make public. |
| done | Initialize new public `nirs4all-papers` locally | README, safety rules, and reproducibility kit template added; AOM public repro can migrate later. |
| done | Update `nirs4all-ecosystem` submodules/docs | `.gitmodules` and gitlinks reflect the renamed/created repositories; later bumped `cluster`, `web`, and `lite` to the audited commits. |
| done | Update `nirs4all.org` content | Replaced "lite demo" language with `nirs4all-web`; added `nirs4all-lite` and `nirs4all-papers` links. Deployed to Pages successfully. |
| done | Re-audit `nirs4all.org` public claims | Tightened visible wording for `nirs4all-lite`, `nirs4all-cluster`, and `nirs4all-arena`; bumped Pages actions to current majors and redeployed successfully. |
| done | Retire temporary user-site redirect | Deleted `GBeurier.github.io`; `https://nirs4all.org/` remains the canonical public site. |
| done | Push `nirs4all-web` rename commit | Pages deploy succeeded and `https://web.nirs4all.org/` now serves `nirs4all-web` title/OG metadata. |
| done | Push `nirs4all-lite` seed | Remote `main` exists; CI scaffold passed. |
| done | Push `nirs4all-papers` seed | Remote `main` exists; content check passed. |
| done | Publish `nirs4all-cluster` after audit | README and project metadata now mark it as a public alpha/prototype; GitHub visibility is public. |
| done | Retire `nirs4all-dist` | Remote repository deleted after confirming it only contained a placeholder README; submodule removed from `nirs4all-ecosystem`. |
| done | Clean and validate `nirs4all-web` | Removed legacy `single-page-WASM`; fixed smoke defaults; Pages deploy is green and live. |
| done | Harden `nirs4all-lite` bindings/release gates | Added license/package metadata, corrected upstream package candidates, R docs/tests, MATLAB/Octave smoke/package, Makefile, release docs, CI and release workflow. |
| done | Expose `nirs4all-lite` CI artifacts | CI uploads `rust-crate`, `python-*`, `npm-wasm`, `r-source`, and `matlab-octave`; latest green run includes `nirs4all_0.0.0.tar.gz`. |
| done | Configure R-universe registry | `GBeurier.r-universe.dev/packages.json` now tracks `dagmldata`, `nirs4alldatasets`, and `nirs4all` from the relevant subdirectories. |
| done | Add `nirs4all` JSON/YAML parser contract to `nirs4all-lite` | Python, Rust, npm/WASM, R, and MATLAB/Octave parse the portable JSON/YAML fixture and accept `pipeline`, `steps`, and direct step-list envelopes. This is syntax parity only; execution parity remains a separate gate. |
| done | Add initial full-Python execution parity gate to `nirs4all-lite` WASM | Four shared JSON/YAML fixtures compare full Python `nirs4all` operators + sklearn PLS against `runPortablePipeline()` in the npm/WASM binding. |
| done | Add Python execution parity gate to `nirs4all-lite` | Python `run_portable_pipeline()` delegates to `nirs4all-methods` bindings and matches the same four full-Python oracle fixtures as WASM under `NIRS4ALL_LITE_REQUIRE_METHODS_PARITY=1`. |
| done | Make lite execution parity blocking in CI | Added a `strict-parity` job that stages `nirs4all-methods` and runs npm/Python oracle tests with skip disabled. |
| done | Validate web against the direct `nirs4all-lite` aggregate | `studio-lite` Vitest now executes the oracle through the vendored aggregate, and the full browser smoke suite passes on the served build. |
| done | Confirm and wire `nirs4all-datasets` WASM into web | Existing `nirs4all-datasets` WASM is offline/browser-scoped (`resolve`, `sha256`). Added browser artefacts to `nirs4all-web`, aliased `@nirs4all/datasets-wasm`, and updated `nirs4all-lite` npm upstream candidates/locks/docs. |
| done | Replace active web finetuning with sweeps | Removed `FinetunePanel`; legacy imported finetune specs migrate to `model.sweeps`; dag-ml lowering/counting now uses explicit sweeps only. Sweeps are available on model params, linear steps, and DAG branch steps. |
| done | Re-run web/lite validation after datasets+sweeps | Web: typecheck, vitest, catalog validator, served build, single-file build, browser `smoke`, `generators-smoke`, and `dag-ops-smoke` passed. Lite: npm tests, Python unittest, and Rust cargo tests passed. Datasets: node WASM smoke passed. |
| done | Make web Pages build standalone after lite split | Vendored the npm aggregate under `nirs4all-web/studio-lite/vendor/nirs4all`; latest `nirs4all-web` Pages deploy succeeded. |
| done | Fix and revalidate datasets CI after WASM follow-up | Latest `nirs4all-datasets` workflows are green for CI, ABI Surface, Site, version-sync, and the new WASM/JS job on commit `0cd44d5`. |
| done | Fix methods CI regressions after WASM follow-up | Latest `nirs4all-methods` commit `1c84cd6` is green for CI, Parity gate, Cross-binding parity, ABI Surface, Sanitizers, Coverage, docs, and version-sync. |
| done | Promote R execution parity in `nirs4all-lite` | R now executes the shared portable JSON/YAML oracle fixtures in CI alongside WASM and Python; fixture drift is blocked by `make test-r-fixtures` on commit `c0a7774`. |
| done | Normalize datasets WASM package naming | Public references now use `@nirs4all/datasets-wasm` in datasets, lite, web, and ecosystem docs; local wasm-pack generated naming remains an implementation detail. |
| done | Re-audit `nirs4all-datasets` WASM existence | Confirmed `bindings/wasm` exists and builds both Node and browser packages; strengthened the Node smoke so WASM `resolve()` is compared with the `n4ds` CLI oracle, and documented that WASM covers `resolve` + `sha256` rather than filesystem `verify_cached`. |
| done | Promote Rust execution parity in `nirs4all-lite` | Rust now dynamically loads `libn4m` and executes the shared portable oracle fixtures via `run_portable_pipeline_with_library`; strict CI runs the Rust parity test with missing-artifact skips disabled. |
| done | Make `nirs4all-web` use the direct lite aggregate for portable runs | Added a strict web bridge from the UI DSL to the shared nirs4all JSON syntax and a saved-model prediction path through `predictPortablePipeline()`. |
| done | Final integration review and browser smoke | Claude Opus "fable" review found no blockers; served Chromium `tests/*smoke.mjs` all passed against the built preview. |
| done | Promote MATLAB/Octave execution parity | `nirs4all-methods` exposes SNV, Savitzky-Golay, and Kennard-Stone through MEX shims; `nirs4all-lite` runs the same four full-Python oracle fixtures through MATLAB/Octave in strict CI. |
| done | Close fable Savitzky-Golay mode follow-up | `nirs4all-lite` commit `83521db` preserves explicit Savitzky-Golay `mode`/`cval` across Python, Rust, JavaScript/WASM, R, and MATLAB/Octave while keeping `interp` as the full nirs4all default. Local gates passed: Python strict oracle, WASM oracle, Rust clippy/test, R check/parity, and MATLAB/Octave strict parity. GitHub CI run `27397418612` is green, strict-parity included. Claude Opus "fable" follow-up review returned SHIP with no High/Medium findings; remaining notes are scoped to the documented methods-backed extension beyond full Python nirs4all's default-only Savitzky-Golay contract. |
| pending | Audit remaining private non-paper repos before visibility flips | `nirs4all-lab` is still private on GitHub; do not make public without content audit. |

## GitHub Commands Executed

Actual `gh` CLI syntax used `--confirm`, not `--yes`:

```bash
gh repo rename nirs4all-drafts --repo GBeurier/nirs4all-papers --confirm
gh repo rename nirs4all-web --repo GBeurier/nirs4all-lite --confirm
gh repo rename nirs4all-org --repo GBeurier/nirs4all-webpage --confirm

gh repo create GBeurier/nirs4all-papers --public --description "Deposited nirs4all papers and reproducible public code bundles"
gh repo create GBeurier/nirs4all-lite --public --description "Canonical low-level nirs4all aggregate distribution with Rust, Python, R, MATLAB/Octave, and WASM bindings"
gh repo create GBeurier/GBeurier.github.io --public --description "GitHub Pages user-site redirect to nirs4all.org"
```

Local `origin` URLs updated:

```bash
git -C ../nirs4all-drafts remote set-url origin https://github.com/GBeurier/nirs4all-drafts.git
git -C ../nirs4all-web remote set-url origin https://github.com/GBeurier/nirs4all-web.git
git -C ../nirs4all-org remote set-url origin https://github.com/GBeurier/nirs4all-org.git
```

New local seed repositories pushed:

```bash
git -C ../nirs4all-papers remote add origin https://github.com/GBeurier/nirs4all-papers.git
git -C ../nirs4all-papers push -u origin main
git -C ../nirs4all-lite remote add origin https://github.com/GBeurier/nirs4all-lite.git
git -C ../nirs4all-lite push -u origin main
```

Final submodule pointers were updated and pushed after the `cluster`, `web`, and `lite` follow-up commits.

## Remaining Controlled Work

- Audit `nirs4all-lab` before any visibility change.
- Migrate AOM public reproduction material into `nirs4all-papers` only after draft/private content is separated.
- Wait for R-universe to ingest the updated `packages.json`; `https://gbeurier.r-universe.dev/src/contrib/PACKAGES` still showed only the pre-existing packages immediately after the push.
- Add a cross-binding drift gate for the duplicated portable operator allowlist/parser contract.
- Either replace or explicitly scope the MATLAB/Octave YAML mini-parser; it is currently adequate for committed fixtures but not a full YAML implementation.
- Normalize any remaining npm upstream naming conventions later; the datasets WASM package is now consistently referenced as `@nirs4all/datasets-wasm`.
- Replace the temporary vendored `studio-lite/vendor/nirs4all` copy with a published npm tarball/package once the `nirs4all-lite` npm release is available. A local sync/drift-check script now exists for the vendored copy.
- Upgrade GitHub Actions dependencies still warning on Node 20 (`actions/checkout@v4`, `actions/upload-artifact@v4`, `microsoft/setup-msbuild@v2`) before GitHub forces Node 24 by default on 2026-06-16.
