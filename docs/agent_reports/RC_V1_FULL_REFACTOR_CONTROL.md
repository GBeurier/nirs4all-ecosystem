# RC V1 Full Refactor Control Board

Date: 2026-07-03

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Objective

Produce release-candidate heads for the NIRS4ALL V1 full refactor while keeping
current production heads intact. RC work happens in isolated worktrees and
branches until the gates below provide enough evidence to publish/tag selected
heads and later switch production to `dag-ml`.

This is not a temporary cut. The target is the final project topology:

- `nirs4all-core`: portable aggregate over the low-level stack, evolved from
  `nirs4all-lite`.
- `nirs4all-python`: Python language surface with idiomatic controllers,
  operators, workspace tools, migration tooling integration, and strong parity
  coverage against the current Python `nirs4all` oracle.
- `nirs4all` language packages: R, JS/WASM, Rust, MATLAB surfaces aligned with
  the same contracts rather than Python-only implementations.
- `nirs4all-ui`: reusable graphical components consumed by Studio and Web.
- `web.nirs4all.org`: client-side-only browser app using WASM/runtime contracts;
  no server backend.

## Non-Negotiables

- Do not touch `nirs4all-drafts` or `nirs4all-lab`.
- Do not merge old W*/INT* branches or worktrees without a fresh audit. Many
  were superseded by later integration heads or resets.
- Production heads remain usable until RC heads are selected, converter release
  is available, and non-regression/performance evidence is recorded.
- The current Python `nirs4all` library remains the oracle until a specific
  divergence is proven to be a legacy bug and documented.
- Default decision for parity divergence: fix it. Only keep a divergence when
  the justification is explicit, tested, and recorded in compatibility docs.
- Skips are release blockers unless they are real optional-environment skips or
  are replaced by local fixtures/contracts that cover the behavior.
- Do not reduce tests, add broad xfails, or introduce fallback paths to obtain
  green CI artificially.
- Full parity is expensive. Run targeted gates during development and only run
  full parity after large integrated batches.
- Add performance comparison for Python `nirs4all` and `nirs4all-studio` with
  and without `dag-ml` backend before production flip.

## Selected RC Worktrees

| Surface | Worktree | Branch | Base |
| --- | --- | --- | --- |
| Python surface | `_worktrees/RC-v1-nirs4all-python` | `rc/v1-full-refactor-python` | `refactor/integration-nirs4all` |
| Native runtime | `_worktrees/RC-v1-dagml` | `rc/v1-full-refactor` | `refactor/L20-lockstep` |
| Native data runtime | `_worktrees/RC-v1-dmd` | `rc/v1-full-refactor` | `refactor/L20-lockstep` |
| Core aggregate | `_worktrees/RC-v1-nirs4all-core` | `rc/v1-full-refactor-core` | `nirs4all-lite/main` |
| Studio | `_worktrees/RC-v1-studio` | `rc/v1-full-refactor` | `nirs4all-studio/main` |
| Web | `_worktrees/RC-v1-web` | `rc/v1-full-refactor` | `nirs4all-web/main` |
| Shared UI | `_worktrees/RC-v1-ui` | `rc/v1-full-refactor` | `nirs4all-ui/main` |
| Cockpit | `_worktrees/RC-v1-cockpit` | `rc/v1-full-refactor` | `nirs4all-cockpit/main` |
| Public site | `_worktrees/RC-v1-org` | `rc/v1-full-refactor` | `nirs4all-org/main` |
| Ecosystem docs/locks | `_worktrees/RC-v1-ecosystem` | `rc/v1-full-refactor` | `nirs4all-ecosystem/main` |
| Providers/contracts | `_worktrees/RC-v1-providers` | `rc/v1-full-refactor` | `nirs4all-providers/main` |
| Migration tools | `_worktrees/RC-v1-tools` | `rc/v1-full-refactor` | `nirs4all-tools/main` |
| Cluster | `_worktrees/RC-v1-cluster` | `rc/v1-full-refactor` | `refactor/integration-cluster` |
| Formats | `_worktrees/RC-v1-formats` | `rc/v1-full-refactor` | `nirs4all-formats/main` |
| IO | `_worktrees/RC-v1-io` | `rc/v1-full-refactor` | `refactor/integration-io` |
| Datasets | `_worktrees/RC-v1-datasets` | `rc/v1-full-refactor` | `nirs4all-datasets/main` |
| Methods | `_worktrees/RC-v1-methods` | `rc/v1-full-refactor` | `nirs4all-methods/main` |
| Repository | `_worktrees/RC-v1-repository` | `rc/v1-full-refactor` | `nirs4all-repository/main` |
| Benchmarks | `_worktrees/RC-v1-benchmarks` | `rc/v1-full-refactor` | `refactor/integration-benchmarks-repository` |
| Papers | `_worktrees/RC-v1-papers` | `rc/v1-full-refactor` | `refactor/integration-papers-provider` |

## Current Evidence

| Gate | Latest evidence | Release interpretation |
| --- | --- | --- |
| Python parity harness | Current Python head `6a2c720` has full split parity green on the selected RC stack with `NIRS4ALL_REQUIRE_N4M=1`, RC `dag-ml`/`dag-ml-data` paths, and SHAP installed: non-slow split `444 passed, 443 deselected, 510 warnings` in `550.90s`; slow split `443 passed, 444 deselected, 1309 warnings` in `1843.08s`; combined interpretation `887 passed`, `0 skipped`, `0 xfailed`, `0 failed`. The same head also passed strict dag-ml public API/native bundle targeted gates: `test_module_api.py`, `test_predict_explain_retrain_happy_path.py`, and `test_dagml_native_retrain_roundtrip.py` -> `28 passed`. Native `.n4a` export/predict/explain/retrain is covered, including direct `_DagmlExportedModel` explain. | Python parity skip/xfail debt is closed for the selected RC head. Remaining release blockers are environment/language host gates and final cutover proofs, not Python parity accounting. |
| `dag-ml` workspace | `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings` passed | Native runtime baseline is usable for RC work. |
| Studio | Operator-definition fixture gate now has 0 skips: `445 passed`. Runtime/operator/quick-run RC stack gate after import-precedence fix: `464 passed`. Wave 4W full backend pytest on Studio head `75f511b`: `2335 passed, 301 warnings`, `0 skipped`. Targeted skip burn-down checks passed (`65 passed`, Ruff, ESLint, and portable-paths Vitest `4 passed`). Wave 4Y full frontend Vitest reports `517` Studio test files and `3709` tests passed; this covers Studio `src/**` and `electron/**`, not vendored `vendor/nirs4all-ui` source tests. | Studio backend and frontend local skip debt is gone on the Linux RC environment. Shared UI source behavior remains owned by the `nirs4all-ui` repo gate plus Studio/Web shim drift checks. Windows host behavior remains a real host gate where only simulated path normalization was tested locally. |
| Web | After `8a5dcff`, deploy Pages and RC CI gates both require `npm ci`, client-side-only contract `2 passed`, typecheck, Vitest `134 passed`, strict `validate:catalog` against `nirs4all-methods` ABI and Studio canonical DAG registry, strict `check:lite-shim`, `build:single`, `build`, and browser smoke `rt-fallback`. Wave 4Z reran local Web gates with Linux Node `v22.21.1`: `tsc --noEmit`, client-only `2 passed`, full Vitest `134 passed`, catalog validation, UI/core shim checks, `build:single`, production `build`, and `23/23` served browser smokes passed. Web head `974f71a` then fixed the clean-runner vendored `nirs4all-ui` subpath exports and makes the CI sibling action build `nirs4all-ui` before shim comparison; GitHub Actions `version-guard` and `web-ci` are green on `974f71a`. | Web RC is a static/browser-only app with no backend runtime and no intentional third-party runtime requests; ABI/catalog/Studio DAG drift, vendored `nirs4all-core` shim drift, and vendored `nirs4all-ui` package drift are blocking gates. Served-worker and single-file paths are both locally green and should both stay in final cutover validation. |
| IO/datasets bridge | Wave 4R on `RC-v1-io` `dac4841` proved the pyo3 IO `DatasetPackage` bridge. Wave 4W moves datasets to `259d1445`: Python/Rust tests pin `catalog/index.json -> n4ds_resolve -> descriptor-rich resolved contract -> nirs4all-io DatasetSpec` without Python provider objects; WASM/R smoke sources now reference the same descriptor-rich contract shape. Wave 4Z moves IO to `71aaaf5` and adds `io-core` tests for `SpectralRecordSet`, `SequenceBlock`, `GenotypeMatrix`, `MaskBlock`, and bare `UriBackedPayload`; local gates passed `cargo test -p nirs4all-io-core`, `cargo test -p nirs4all-io-dagml`, Python `tests/test_dataset_package.py`, WASM smokes, and CLI/WASM cross-binding byte identity. Wave 4AA moves datasets to `60658035` and fixes the access-policy test fake so the non-network CI suite cannot fall through to the native Dataverse fetch after earlier imports. `python3.11 -m pytest -q -m "not network"` reports `226 passed`, `6 skipped`. | Datasets non-Python consumers use neutral catalog/index/descriptor plus IO contracts by design; `datasets` does not assemble `DatasetPackage`. IO owns materialization. Remaining risk is host/toolchain coverage for R/Octave/MATLAB and broader non-Python materialization scenarios beyond the current Rust/WASM gates, not absence of a Python provider package. |
| Python non-parity tests under strict dag-ml | Wave 4W strict public API batch passed `28 passed`: `workspace_path` and `Session` are explicitly legacy-mode tests, while strict native uses `results_path`; native `.n4a` predict/explain/retrain now passes targeted coverage. | The targeted strict API blocker is closed. This is not a full production flip proof until full parity and wider RC-D release proof are rerun. |
| Providers | Wave 4P on `RC-v1-providers` `7c7c6e9` added the canonical contract gate. Wave 4U moves providers to `bb87f35`: Ruff passed, `tests/test_contracts.py` -> `21 passed`, and `scripts/validate_contracts.py` -> `provider contracts gate: PASS (5 schemas, 5 fixtures)`. Wave 4AA moves providers to `2cfcca6`: the CI gate lints only provider-owned `src`, `tests`, and `scripts`, and Ruff excludes the checked-out `nirs4all-ecosystem` contracts sibling. `python3.11 scripts/ci_gate.py` passes. | Providers remain an optional Python client surface over neutral contracts; R/WASM/native consumers must use the schemas/fixtures plus native IO/materialization without a Python runtime dependency. |
| Performance comparison | `n4a-benchmarks perf-compare --repeats 3 --assert-max-ratio python_run=1.0 --assert-max-ratio studio_run=1.0` after `45f4cf7`: Python `dag-ml/legacy` run ratio `0.762x` and total ratio `0.806x`; Studio run ratio `0.702x` and total ratio `0.753x`. | RC harness evidence with fallback disabled, child Python `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python`, RC Python root `_worktrees/RC-v1-nirs4all-python`; JSON/Markdown saved under `/tmp/n4a_perf_compare_rc_gate_20260702.*`. |
| Core language surfaces | Wave 4K on `RC-v1-nirs4all-core` `29d6d04`: Rust fmt/clippy/tests passed; Python binding tests `54 run, 1 skipped`; WASM tests passed with Linux Node 24 (`13 passed, 2 skipped` full WASM; V1 surface `13 passed, 1 skipped`); V1 Python surface tests `53 passed`; strict core Python parity and Rust parity passed. Wave 4Y moves Core to `2b0d18a`: Methods JS/WASM `make test-js-wasm` passes on EMSDK (`emcc 5.0.7`, Node `22.16.0`), stages `index.js`, `n4m.js`, and `n4m.wasm`; Core `make test-wasm-parity-strict NIRS4ALL_METHODS_ROOT=../RC-v1-methods` passes `15` WASM tests plus TypeScript typecheck; release topology unittest reports `12 tests OK`. | Core WASM/Methods strict parity is closed locally with a staged Methods JS/WASM dist. R/Rscript and Octave are unavailable locally, so R and MATLAB/Octave execution remain environment gates. |
| Cockpit release accounting | Wave 4P on `RC-v1-cockpit` `8b8e1a4`: `data/current.json` now marks `dag-ml-data` crates as stale against `v0.2.2`/RC head instead of green. `json.tool`, `n4a-cockpit validate-targets`, and offline pytest passed (`84 passed`). | Cockpit is an accounting snapshot, not product release proof; stale registry cells are intentionally visible rather than hidden. |

## Coordination Update - 2026-07-02

- Python `nirs4all` RC head now includes `8b69fd4f fix(dagml): accept canonical studio pipeline steps`, covering Studio/editor canonical strings and dict class refs on the dag-ml default path.
- Python `nirs4all` RC head now includes `1234db31 fix(parity): remove registry skip debt`; the four registry-skip cases are live and covered by targeted parity gates.
- Python `nirs4all` RC head now includes `99d57b7e fix(parity): burn down native xfail debt`; strict xfails are reduced from 11 to 6 while preserving `concat_transform_pca_svd_plsr`, `generator_sample_log_uniform_alpha`, `rep_to_sources_basic`, `rep_to_pp_basic`, and the two branch separation native-boundary cases as explicit debt.
- Python `nirs4all` RC head previously reached `a103fd2 docs(parity): refresh rc compatibility ledger`; Wave 4U later moves it to `884a196` with RC-aware `dag-ml` CLI resolution. The previous full parity proof remains `3d568ab` with `659 passed, 227 deselected, 1530 warnings` in `2037.46s`; no parity tests were skipped or xfailed. The Wave 4U proof reruns the gate on `884a196` in split form: slow parity `443 passed, 444 deselected`; non-slow parity `316 passed, 1 methods-env skip, 570 deselected`; the methods skip is closed by the installed `nirs4all-methods` proof harness, which reran the same non-slow pytest args under `NIRS4ALL_REQUIRE_N4M=1` and returned `status: OK`.
- Studio RC head now includes `0653ee0 test(runtime): align Studio default engine contract`; targeted backend runtime/native/quick-run checks passed with RC dag-ml and dag-ml-data on `PYTHONPATH`.
- Studio RC head now includes `fd06d94 ci(studio): run gates on rc branches`; CI/Playwright now run on `rc/**` and select the RC Python library checkout on RC branch runs. Earlier `9190ccc`, `1d1ded5`, and `8141e2e` fixed operator fixtures, RC import precedence, and shared-UI badge reuse.
- Web RC head now includes `8a5dcff ci(web): require upstream catalog siblings`; the public `web.nirs4all.org` build remains GitHub Pages/static/WASM-only and both RC CI and Pages deploy now run client-only, typecheck, Vitest, strict methods ABI + Studio DAG registry catalog validation, strict lite/core shim, build, single-file build, and one browser smoke gate.
- `nirs4all-ui` RC head now includes `8f9f2f6 ci(ui): add package release gate`; CI runs typecheck, Vitest, build, and `npm pack --dry-run` through `npm run ci`.
- Studio backend full pytest on the latest Wave 4W Studio head passed with
  `2335 passed`, `0 skipped`, and `301 warnings`; previous `2324 passed,
  6 skipped` evidence is superseded for backend skip accounting.
- Benchmarks RC head now includes `45f4cf7 fix(benchmarks): keep perf harness lint-clean`; `n4a-benchmarks perf-compare` records both Python legacy-vs-dag-ml and Studio legacy-vs-dag-ml timings with fallback disabled.
- Methods RC head now includes `44cc9489 test(bindings): add methods release gate entrypoints`; local ABI freshness, wheel install smoke, Python installed smoke, shell syntax, and Makefile help passed. JS/WASM/R/Octave/MATLAB remain environment gates because Emscripten/R/Octave/MATLAB are unavailable locally.
- Core RC head is now `cdba11e ci(core): pin methods strict parity checkout`; this is a CI-only movement from the Wave 4K functional evidence head `29d6d04`, and the aggregation lock now pins `cdba11e`. Rust/Python/WASM topology gates and strict Python/Rust core parity remain the latest functional evidence; R and Octave execution remain unavailable in this local environment.
- `nirs4all-providers` RC head now includes `7c7c6e9 ci(providers): require canonical contract gate`; the gate runs Ruff, mypy, hermetic tests, conformance tests, and canonical neutral contract byte-identity without forcing optional provider backings into base install.
- `nirs4all-tools` RC head now includes `7c5070f ci(tools): gate migration converter checks`; CI installs `.[dev,parquet]` so migration/converter goldens run with Parquet support, then runs Ruff, mypy, and pytest.
- `nirs4all-cockpit` RC head now includes `8b8e1a4 chore(data): mark dag-ml-data rc stale targets`; planned RC surfaces include `nirs4all-ui` `8f9f2f6`, `nirs4all-providers` `7c7c6e9`, `nirs4all-tools` `7c5070f`, plus planned Python/WASM/R binding targets for `dag-ml` and `dag-ml-data`.
- `nirs4all-io` RC head now includes `dac4841 feat(python): expose dataset package bridge`; the pyo3 binding exposes `to_dataset_package`, `describe_dataset_package`, `load(..., target="dataset_package"|"package")`, and `nirs4all_io.materialize` package re-exports with canonical JSON and metadata dtype hashing aligned to the MVP/Rust package contract.
- `nirs4all-datasets` RC head now includes `cac8742 ci(datasets): resolve rc sibling deps`; `ensure_rust_deps.sh` understands `rc/**` sibling refs and local `RC-v1-*` worktrees, normal datasets CI/version/ABI gates cover `rc/**`, and the Python binding lock is refreshed for the selected IO RC dependency graph.
- Wave 4S covered normal `rc/**` CI triggers across the remaining selected
  repos without widening release/manual/pages/scheduled/long parity workflows.
  The aggregate lock now pins CI-only heads for `dag-ml` `a8f6cb3`,
  `dag-ml-data` `95e56a7`, `nirs4all-formats` `32fc87f`,
  `nirs4all-io` `0d20c80`, `nirs4all-methods` `d918c5e`, and
  `nirs4all-core` `0a516e2`.
- Web/Studio clean-runner UI dependency resolution is fixed after Wave 4S.
  `nirs4all-web` now vendors `nirs4all-ui` and validates fresh Linux
  `npm ci --ignore-scripts`, `check:ui-shim`, typecheck, and client-only
  Vitest (`2 passed`) at `cdb43cc`. `nirs4all-studio` now vendors
  `nirs4all-ui`, sets `install-links=true` for deterministic local package
  installs, and validates fresh Linux `npm ci --ignore-scripts`,
  `check:ui-shim`, and `lint:tsc` at `0d8b3cb`.
- Wave 4T documents methods binding scope without overclaiming archived PoCs:
  `nirs4all-methods` `6f6a3fa` now treats Julia, JNI/Android, Go, Rust,
  .NET, Ruby, Lua, and Nim as archived/on-hold under `bindings/_archive/`.
  `nirs4all-datasets` `93e9f39` now documents the Rust acquisition core/C ABI
  as the non-Python surface and the Python package as an optional binding over
  that core.
- Wave 4T expands shared runtime UI ownership: `nirs4all-ui` `69501bd`
  centralizes runtime engine badge title/default/fallback rendering, Studio
  consumes that shared status rendering at `f1eba56`, and Web syncs its vendored
  shared UI package at `6924da5`. Validation used Linux Node `v22.21.1` with
  fresh installs for UI/Web/Studio.
- Wave 4U moves the selected RC batch to Python `884a196`, datasets `59b34f5`,
  providers `bb87f35`, Studio `bd7de4b`, core `5067cab`, and methods tag
  `6f6a3fa`. Targeted parity/native gates are green, datasets/providers use the
  neutral descriptor/contract path, Studio has a focused runtime overhead gate,
  and core strict-parity pins no longer drift from the selected methods head.
  Full Python-reference parity was then run after the batch in split form; the
  sole base-interpreter methods skip was closed by the installed-methods proof
  harness rather than accepted as release debt.
- Wave 4V moves the selected Studio/Web/Core/Methods/Org heads to Studio
  `e9fa4cf`, Web `85dcd79`, Core `8dcf2af`, Methods `a24b06b`, and Org
  `fd4634d`, with branch and tag `n4a-v1-rc1-2026.07-refactor` published for
  each. Studio full Playwright e2e passed `63 passed (13.8m)` after the settings
  locator fix; final Studio runtime/venv targeted tests passed `7 passed` after
  the pip nonzero-cache refinement. Web audit/shim/smoke gates remain green,
  Core Python V1 surface reports `53 tests OK`, Core WASM reports `13 passed,
  2 skipped`, Methods now fails fast on missing JS parity fixture, and Org
  wording no longer overclaims R/MATLAB/full aggregate status.
- Wave 4V reran the GitGuardian cluster alert audit against the current
  published refs and hidden PR refs. Current published heads remain clean:
  cluster `main` `97b2b38`, cluster RC `9d6ab34`. Hidden merged PR refs #1/#2
  still expose placeholder CLI examples such as `--token dev`, not a discovered
  real token. If GitGuardian shows a non-placeholder value, rotate it out of
  band; otherwise close the alert as stale/placeholder PR-ref exposure because
  GitHub rejects normal deletion of hidden PR refs.
- Wave 4W moves Python to `6a2c720`, Core to `f120c28`, Studio to `75f511b`,
  and Datasets to `259d1445`, with branch/tag publication refreshed for all
  four repos. Python strict dag-ml targeted API/native bundle gates passed
  `28 passed`; Studio backend full pytest now reports `2335 passed` and
  `0 skipped`; Core WASM keeps `13 passed, 2 skipped` in non-strict mode but
  strict Methods artifact preflight now fails explicitly until `index.js`,
  `n4m.js`, and `n4m.wasm` are staged; Datasets pins the non-Python
  descriptor-to-IO-spec bridge with Python/Rust goldens. `WAVE_4W` records the
  agent reports, review decisions, tests, and remaining risks. Wave 4X then ran
  full Python parity on the selected head: non-slow `444 passed, 443 deselected`
  and slow `443 passed, 444 deselected`, with no skipped or xfailed parity tests.
- Wave 4X also closed the release-lock fetchability gap flagged by a Claude
  read-only audit. Core `f120c28` branch/tag now resolves on both
  `GBeurier/nirs4all-lite` and `GBeurier/nirs4all-core`, and a `git ls-remote`
  audit confirms all seven aggregation-lock members resolve branch and tag to
  their locked commits.
- Wave 4Y moves Core to `2b0d18a` with a Makefile-only fix that resolves the
  staged Methods JS/WASM dist path absolutely when `NIRS4ALL_METHODS_ROOT` is
  passed relative. Methods JS/WASM `make test-js-wasm` passed, Core strict WASM
  parity passed `15` tests with no skips, Studio full frontend Vitest passed
  `3709` tests, and the aggregation lock was regenerated plus fetchability
  rechecked at `7/7`.
- Wave 4Z moves IO to `71aaaf5` with additional `DatasetPackage`
  payload-variant coverage and retags `nirs4all-io` RC. `nirs4all-ui` source
  `npm run ci` passed (`52` tests plus typecheck/build/pack dry-run), Web
  client-only/full Vitest/catalog/shim/single-file build plus production build
  and `23/23` served browser smokes passed, and
  cluster strict active-head secret scans remain empty. The aggregation lock now
  pins IO `71aaaf5`.
- Wave 4Z follow-up moves Web to `974f71a` and Ecosystem to `05da7dc`.
  Web now commits the generated vendored `nirs4all-ui` `dist` subpaths required
  by clean `npm ci`, and its sibling action builds `nirs4all-ui` before the
  strict shim drift check. Ecosystem fixes release-lock CI by passing
  `--workspace-root` as a global argument and making `checkout-members` clone into
  `selected_workspace_path`, matching the selected RC lock semantics. GitHub
  Actions are green on both heads: Web `version-guard` + `web-ci`, Ecosystem
  `version-guard` including `release-lock-validation`.
- Claude Code separation review confirmed the target split is coherent but
  warned against overclaiming R or native datasets/providers. Current release
  language should treat R as a methods portable subset/preview until
  `dag-ml` R coordination and `DatasetPackage` materialization gates exist.
- Ecosystem RC head now includes `cb1a0bd docs(release): lock selected rc topology`; lock generation validates selected `rc/v1-*` worktrees while preserving canonical public repo paths and nirs4all-core aliases.
- Ecosystem RC head now includes `89e8c63 docs(release): tighten topology accounting`; release surface validation documents `nirs4all-core`, `nirs4all-python`, R/JS-WASM/Rust/MATLAB language surfaces, `nirs4all-ui`, client-side-only Web, providers/cockpit/org, and the narrower aggregate lock boundary.
- Cluster GitGuardian remediation cleaned the published active heads and was
  refreshed after the latest alert. Wave 4X removed the active-head
  secret-shaped documentation example `--principal alice:s3cr3t:submitter`.
  Wave 4AC then removed scanner-sensitive principal metavars from active
  docs/help. Published branch/tag refs now point to clean heads: `main`
  `eaf79a0`, `rc/v1-full-refactor` `ffeaf4b`, tag
  `n4a-v1-rc1-2026.07-refactor` `ffeaf4b`. Strict scanner-pattern checks over
  the active branch/tag refs are empty; the focused RBAC gate is `24 passed` on
  both main and RC worktrees, and GitHub Actions are green for both heads.
  GitHub/history may still expose old placeholder examples on hidden PR refs;
  residual alert closure is a GitGuardian/GitHub-support dashboard action unless
  GitGuardian discloses an actual non-placeholder value.
- RC branches and tag `n4a-v1-rc1-2026.07-refactor` are published for the 20 selected worktrees. `WAVE_4Q_RC_PUBLICATION_REAUDIT.md` rechecked the post-4P heads after repairing missing tags on Studio/UI/Org/Tools/IO/Datasets; Wave 4R then moved Studio/IO/Datasets and regenerated the aggregation lock for IO/Datasets.
- Latest pushed/tagged heads after the Wave 4AD surface/topology batch: Python `6a2c720`,
  dag-ml `a8f6cb3`, dag-ml-data `95e56a7`, Core `1b505e9`,
  Studio `5907639`, Web `974f71a`, UI `69501bd`, Cockpit `f06f7b4`,
  Org `fd4634d`, Ecosystem uses the current board HEAD, Providers `2cfcca6`,
  Tools `7c5070f`, Cluster `ffeaf4b`, Formats `32fc87f`, IO `71aaaf5`,
  Datasets `7b1b805`, Methods `cb9159dd`, Repository `ced219f`,
  Benchmarks `06d4146`, Papers `f1d84f4`.
- Wave 4AA moves Datasets to `60658035` and Providers to `2cfcca6`, with branch
  and tag `n4a-v1-rc1-2026.07-refactor` published for both. Datasets fixes the
  non-network access-policy test fake so prior native `_acquire` imports cannot
  fall through to `dv.example`; local non-network pytest is `226 passed`,
  `6 skipped`. Providers fixes the RC CI false negative by preventing Ruff from
  scanning the checked-out `nirs4all-ecosystem` contracts sibling; local
  `python3.11 scripts/ci_gate.py` passes. The aggregation lock now pins Datasets
  `60658035` and `audit-fetchability` reports `7/7`.
- Wave 4AA also migrates cutover gates away from stale `INT-*` and root-main
  paths to selected `_worktrees/RC-v1-*` paths. `post-w2j-state` now proves
  Python `6a2c720`, Studio `75f511b`, Web `974f71a`, Tools `7c5070f`, Cluster
  `19384e2`, and Providers `2cfcca6` on the selected RC branches. The new
  `cluster_dag_advisory` gate passes `3` distributed parity tests plus Ruff.
- Wave 4AA GitGuardian follow-up with a read-only Claude Code security audit
  confirms the `nirs4all-cluster` alert is a placeholder false positive:
  `alice:s3cr3t`, `--token dev`, and environment-variable examples are not real
  credentials, and current active heads contain no real secret hits. Old
  placeholder strings can remain in pushed history/PR refs because remediation
  was additive rather than a purge; close as false positive/remediated unless
  GitGuardian discloses a non-placeholder value.
- `aggregation-lock` remains limited to the aggregate core/runtime members. Studio/Web/UI/tools/providers/benchmarks/papers/cluster are tracked by the surface matrix, cutover gates, and agent reports rather than forced into the aggregate lock without an ownership contract.
- Wave 4AB moves Studio to `028e3c0` and Methods to `64731c6d`, with branch and
  tag `n4a-v1-rc1-2026.07-refactor` published for both. Studio now runs the
  vendored `nirs4all-ui` shim gate in CI and `lint:parallel`, builds the
  sibling UI package before clean-runner comparison, and tracks the required
  vendored `dist`. Studio RC CI also installs local `dag-ml` and `dag-ml-data`
  runtime wheels from the selected RC branches before installing Python
  `nirs4all`, and Ruff lints only Studio-owned Python paths. Methods
  cross-binding and parity workflows now run on `rc/**`; the aggregation
  manifest requires `methods_cross_binding_parity` and records Methods R
  availability as `subset`, not `full`.
- GitHub Actions are green on Studio `028e3c0`: `CI` and `Playwright E2E Tests`
  both completed with success. Methods `64731c6d` is green on `CI`,
  `Sanitizers`, `version-guard`, `Cross-binding parity`, `version-sync`,
  `ABI Surface`, `Coverage`, and `Parity gate`. Ecosystem `3cf421a` passed
  `version-guard`.
- Wave 4AB cutover gate sweep passed with `pyref_oracle_full` intentionally
  skipped for batch-cost control. The run covered release-lock validation,
  fetchability, native `.n4a` export, Studio runtime routes, Web runtime
  contract, providers sibling release, dag-ml/dag-ml-data lockstep, migration
  smoke, core/lite V1 surfaces, and cluster DAG advisory. Full Python parity was
  not rerun; the last full proof remains `887 passed`, `0 skipped`, `0 xfailed`.
- The 2026-07-02 GitGuardian alert on `GBeurier/nirs4all-cluster` was rechecked
  after `git fetch --prune`: visible remote refs are only `origin/main` and
  `origin/rc/v1-full-refactor`, and targeted active-ref scans found no concrete
  CLI-option secret values. Treat it as stale/remediated placeholder exposure
  unless GitGuardian provides a non-placeholder value.
- Wave 4AC moves Studio to `5907639`, Cluster RC to `ffeaf4b` (`main`
  `eaf79a0`), and Datasets to `7b1b805`, with branch and tag
  `n4a-v1-rc1-2026.07-refactor` published for the selected RC heads. Studio
  release packaging now bakes selected RC `nirs4all`, `dag-ml`, and
  `dag-ml-data` sources into all-in-one release archives and Docker builds;
  GitHub Actions are green (`CI` and Playwright). Cluster active refs now have
  zero inline CLI-option secret candidates after neutralizing principal
  metavars; GitHub Actions are green on both main and RC. Datasets R bridge now
  runs the optional `nirs4allio` micro-gate in a combined fresh R library instead
  of failing behind a skip; IO loader tests preserve semicolon-default coverage.
- Wave 4AC also closes several non-Python local gates: Core strict WASM parity
  (`15` tests, `0` skipped), Core R V1 public surface, Core R strict portable
  parity against `RC-v1-methods`, Methods R binding parity, Methods Octave/MEX
  parity, Methods JS/WASM smoke/parity/pack dry-run, IO WASM smoke, IO R smoke,
  IO Octave/MATLAB smoke, Datasets WASM node/web/package dry-run, Datasets R
  smoke, and combined R IO+datasets package verification. Full Python parity was
  intentionally not rerun in this batch.
- Wave 4AD moves Core to `1b505e9` and regenerates the aggregation lock so the
  machine-readable Core topology lists all V1 language surfaces: Python,
  JavaScript/WASM, Rust, R, and MATLAB/Octave. Local Core gates passed for Rust,
  Python, WASM, R, and Octave parity; Web passed the client-side-only gate,
  static/single-file builds, and all browser smokes; IO and Datasets received
  additional workspace/catalog/bridge coverage; Methods ABI freshness is current.
  IO cross-binding parity still needs a multi-toolchain shell/CI environment.
  Full Python parity was still deferred for batch-cost control.
- Wave 4AE moves Methods to `cb9159dd`, publishes the RC branch/tag there, and
  regenerates/validates the aggregation lock; fetchability audit reports `7/7`
  member commits checked out. The patch closes stale Methods release docs and JS
  fixture provenance without changing runtime code. Gates passed:
  `scripts/bump_version.sh --check`, `make test-abi-freshness
  PRESET=dev-release`, C++ `n4m_tests` + `n4m_internal_tests` via ctest, and
  `make test-js-wasm` including npm test and pack dry-run. GitHub Actions on
  `cb9159dd` are green for `CI`, `Cross-binding parity`, `Parity gate`,
  `ABI Surface`, `Coverage`, `Sanitizers`, `version-sync`, and `version-guard`.
  Full Python parity was not rerun in this docs-only Methods batch.
- Wave 4AE also reaudits the July 3 GitGuardian cluster alert. Active remote refs
  are still only `origin/main`, `origin/rc/v1-full-refactor`, and the RC tag;
  targeted active-head scans find no concrete CLI-option secret values. The
  remaining alert source is historical reachable documentation examples/metavars
  or GitGuardian stale state, not a current head secret. If GitGuardian requires
  the alert to disappear rather than be closed as false-positive/remediated, that
  requires history rewrite of active branches, not merely deleting superseded refs.
- Skip/xfail audit is recorded in `RC_SKIP_XFAIL_AUDIT.md`: Studio operator
  skips and Python registry skips have been burned down; Python full parity on
  current head `6a2c720` reports `887 passed`, `0 skipped`, and `0 xfailed`
  across the split slow/non-slow run. Remaining skip risk is outside this gate:
  R and Octave/MATLAB language binding environments without their release
  toolchains, plus final host proof for non-Python DatasetPackage surfaces
  beyond the current Rust/WASM local gates.

## Parity Debt To Burn Down

Current Python-reference parity debt for the selected head is zero in the last
full proof: split slow/non-slow parity on Python `6a2c720` totals `887 passed`,
`0 skipped`, `0 xfailed`, and `0 failed`.

Historical xfail/skip lists in earlier Wave 4 notes are superseded by the
Wave 4X full proof. New parity skips or xfails are release blockers unless they
are optional-environment skips outside the Python parity oracle and are recorded
with a replacement contract or local fixture.

Remaining non-Python proof debt is broader release-environment coverage, not
accepted Python parity debt:

- Broader R/Rscript feature-completeness beyond the Wave 4AC/4AD Methods/Core/
  IO/datasets R gates.
- Licensed MATLAB runtime proof remains manual/outside the Linux Octave proofs;
  Octave/MEX parity has passed for Methods and Core, and IO Octave smoke passed.
- Datasets remote `get(id)` for every catalog entry must not be claimed until
  canonical hosting/DOI/file-id routes are complete; current proof covers the
  catalog, software bridge, and raw retrieval contracts.
- Methods runtime gates are current for ABI, JS/WASM, R, and Octave/MEX, and the
  stale RC-readiness docs/JS fixture provenance were corrected on `cb9159dd`.
  Release-distribution debt remains for CRAN external checks,
  `nirs4all-methods` sdist/post-publish smoke, broader R/Octave surface coverage,
  and full-registry/multi-shape parity dashboards.
- Full Python parity must be rerun after the next large integration batch before
  RC promotion.

## Parallel Lanes

Note: this lane table preserves the original orchestration record. Current RC
selection is governed by the published worktree/tag audit above; historical
Claude sessions labelled `running` here must not be treated as active release
blockers without checking their lane reports and the selected RC heads.

| Lane | Owner | Scope | Status | Report |
| --- | --- | --- | --- | --- |
| RC-A | Claude/Fable `42f5077a-5f84-4c2b-90ff-8afa1657f236` | Release topology, lock, naming, `nirs4all-lite` to `nirs4all-core`, cockpit/org updates. | running | `RC_A_TOPOLOGY_NAMING.md` |
| RC-B | Claude/Opus `2994b539-f7c6-4d47-8c5a-6ac80e3311e0` | Python parity ledger, strict gate, compatibility docs, xfail/skip accounting. | running | `RC_B_PARITY_LEDGER.md` |
| RC-C | Claude/Fable `fd1fbc9b-c112-48e0-afce-760289f21347` | Fix parity divergences/skips/legacy bugs in Python/native bridge. | running | `RC_C_PARITY_FIXES.md` |
| RC-D | Claude/Fable `4f6c35ae-2973-4ed4-bb36-23a5ef5f8c55` | `dag-ml` native workspace/session/predict/retrain blockers and performance probes. | running | `RC_D_RUNTIME_PERF.md` |
| RC-E | Claude/Opus `055b8a5f-29a8-4268-8920-096db8c13f63` | Language package surfaces: Python `nirs4all-python`, R, JS/WASM, Rust, MATLAB contracts. | running | `RC_E_LANGUAGE_SURFACES.md` |
| RC-F | Claude/Opus `1ab19061-a59c-4b98-b37a-03f0d7b32502` | Providers as neutral contracts and per-language client semantics. | running; coordinator providers facade fix `3de0042` after RC-M conformance | `RC_F_PROVIDERS_CONTRACTS.md` |
| RC-G | Claude/Fable `fcce9360-9b1f-470c-9ab3-42518a659f68` | Studio/Web/UI runtime UX, client-side-only Web, shared component consumption. | running | `RC_G_STUDIO_WEB_UI.md` |
| RC-H | Claude/Opus `a8c5b19c-aeba-4985-b073-b28b8bfa66db` | Migration converter release proof and legacy/native result performance comparisons. | running | `RC_H_MIGRATION_CONVERTER.md` |
| RC-I | Codex/GPT-5.5 `019f2286-ba97-7512-8a9d-88b0995a85dc` | Cluster client/server scheduler, DAG rights, minimal client contracts. | integrated in rewritten cluster RC head `e843073`; GitGuardian history rewrite and token-shaped CLI example cleanup complete for published refs | `RC_I_CLUSTER_SCHEDULER.md`, `RC_SECURITY_GITGUARDIAN_CLUSTER.md` |
| RC-J | Codex/GPT-5.5 `019f2286-bc1a-70f2-af8f-1122c242f637` | Formats/IO/datasets reference bridge and get/load dataset contracts. | integrated and refreshed in IO `dac4841`, datasets `cac8742` | `RC_J_FORMATS_IO_DATASETS.md`, `WAVE_4R_IO_DATASETS_BRIDGE_RC_CI.md` |
| RC-K | Claude/Fable `c742c1c9-6848-4631-8ff4-dcbe94de9691` | Final reviewer/parity auditor. No code ownership. | running | read-only result |
| RC-L | Codex/GPT-5.4 `019f2286-bd52-7283-998d-13f6dcbda7b0` | Methods engine and bindings parity surface. | integrated in methods commit `09adf881` | `RC_L_METHODS_BINDINGS.md` |
| RC-M | Codex/GPT-5.4 `019f2286-bee1-7790-bc5c-56e6c4a1da86` | Repository/benchmarks/papers as providers/plugins. | integrated in repository `534c907`, benchmarks `ae37bd5`, papers `acde191` | `RC_M_REPO_BENCHMARKS_PAPERS.md` |
| RC-N | Claude/Opus `24483f0d-1b71-4e5b-8d65-6e98850fc9fe` | Read-only audit of old W*/INT* worktrees and superseded branch heads. | running | read-only result |

## Integration Rules

Each lane must provide a short report:

- files modified;
- tests run and exact result;
- risks and open questions;
- decisions made;
- whether follow-up full parity is needed.

Coordinator reviews diffs before integration. RC integration is allowed only when
the touched repo has a clean status, focused tests pass, and the lane report is
updated. Full parity runs only after substantial batches.

## Final Gates

- Python reference parity: no unexplained xfail/skip debt.
- `dag-ml`/native parity gates.
- Migration/converter golden tests.
- Studio/Web runtime contract tests, with Web remaining client-side-only.
- IO/datasets reference bridge tests.
- Methods binding parity tests.
- Release-lock validation.
- Release-lock fetchability audit.
- Topology/release distribution matrix coherent across cockpit/org/ecosystem.
- Performance comparison: Python legacy vs `dag-ml`; Studio legacy vs `dag-ml`.
- Final report with selected commits/tags, tests, risks, and remaining decisions.
