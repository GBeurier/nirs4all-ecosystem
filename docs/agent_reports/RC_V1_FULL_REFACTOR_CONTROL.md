# RC V1 Full Refactor Control Board

Date: 2026-07-02

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
| Python parity harness | Python runtime proof head `3d568ab` has full `pyref_oracle_full` green on the selected RC stack (`dag-ml` `7f86a9b`, `dag-ml-data` `e681685`): `659 passed, 227 deselected, 1530 warnings` in `2037.46s`; no parity tests skipped or xfailed. The current pushed Python head `a103fd2` is a docs-only compatibility-ledger refresh. Marker audit still reports classified skip call sites by AST, not realized parity skips. | Full numerical parity is clean on the runtime code head. Rerun full parity before final production cutover or after the next material runtime batch. |
| `dag-ml` workspace | `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings` passed | Native runtime baseline is usable for RC work. |
| Studio | Operator-definition fixture gate now has 0 skips: `445 passed`. Runtime/operator/quick-run RC stack gate after import-precedence fix: `464 passed`. Full backend pytest after current Python/Web batch: `2324 passed, 6 skipped` in `1465.99s`. | Studio RC default `dag-ml` route is covered by focused tests; the old operator skip debt is gone from the full backend gate. |
| Web | After `8a5dcff`, deploy Pages and RC CI gates both require `npm ci`, client-side-only contract `2 passed`, typecheck, Vitest `134 passed`, strict `validate:catalog` against `nirs4all-methods` ABI and Studio canonical DAG registry, strict `check:lite-shim`, `build:single`, `build`, and browser smoke `rt-fallback`. | Web RC is a static/browser-only app with no backend runtime and no intentional third-party runtime requests; ABI/catalog/Studio DAG drift and vendored `nirs4all-core` shim drift are now blocking gates. |
| IO/datasets bridge | Wave 4R on `RC-v1-io` `dac4841` and `RC-v1-datasets` `cac8742`: pyo3 binding tests passed (`25 passed`), datasets/providers editable install against the RC sibling topology passed, datasets bridge tests passed (`3 passed`), and providers bridge tests passed (`2 passed`). | The Python datasets/providers bridge now has a real pyo3 IO `DatasetPackage` surface. Non-Python provider clients remain future work against neutral contracts. |
| Python non-parity tests under strict dag-ml | targeted failures in workspace/session/predict/explain/retrain | Blocks dag-ml production flip. Legacy mode targeted rerun passed. |
| Providers | Wave 4P on `RC-v1-providers` `7c7c6e9`: Ruff, mypy, hermetic tests, conformance `......ssss`, and canonical provider contract byte-identity all passed. CI now checks out `nirs4all-ecosystem` and fails if the neutral contracts drift. | Providers remain an optional Python client surface over neutral contracts; R/WASM/native consumers must use the schemas/fixtures without a Python runtime dependency. |
| Performance comparison | `n4a-benchmarks perf-compare --repeats 3 --assert-max-ratio python_run=1.0 --assert-max-ratio studio_run=1.0` after `45f4cf7`: Python `dag-ml/legacy` run ratio `0.762x` and total ratio `0.806x`; Studio run ratio `0.702x` and total ratio `0.753x`. | RC harness evidence with fallback disabled, child Python `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python`, RC Python root `_worktrees/RC-v1-nirs4all-python`; JSON/Markdown saved under `/tmp/n4a_perf_compare_rc_gate_20260702.*`. |
| Core language surfaces | Wave 4K on `RC-v1-nirs4all-core` `29d6d04`: Rust fmt/clippy/tests passed; Python binding tests `54 run, 1 skipped`; WASM tests passed with Linux Node 24 (`13 passed, 2 skipped` full WASM; V1 surface `13 passed, 1 skipped`); V1 Python surface tests `53 passed`; strict core Python parity and Rust parity passed against `RC-v1-methods` dev-release `libn4m.so.2.0.0`. Wave 4P moved the published core head to `cdba11e` with a CI-only strict-parity checkout pin to `nirs4all-methods` `44cc948`; the aggregation lock now pins `cdba11e`. | R/Rscript and Octave are unavailable locally, so R and MATLAB/Octave execution remain environment gates. WASM methods execution skips remain until the local methods JS/WASM package is built or CI runs that environment. |
| Cockpit release accounting | Wave 4P on `RC-v1-cockpit` `8b8e1a4`: `data/current.json` now marks `dag-ml-data` crates as stale against `v0.2.2`/RC head instead of green. `json.tool`, `n4a-cockpit validate-targets`, and offline pytest passed (`84 passed`). | Cockpit is an accounting snapshot, not product release proof; stale registry cells are intentionally visible rather than hidden. |

## Coordination Update - 2026-07-02

- Python `nirs4all` RC head now includes `8b69fd4f fix(dagml): accept canonical studio pipeline steps`, covering Studio/editor canonical strings and dict class refs on the dag-ml default path.
- Python `nirs4all` RC head now includes `1234db31 fix(parity): remove registry skip debt`; the four registry-skip cases are live and covered by targeted parity gates.
- Python `nirs4all` RC head now includes `99d57b7e fix(parity): burn down native xfail debt`; strict xfails are reduced from 11 to 6 while preserving `concat_transform_pca_svd_plsr`, `generator_sample_log_uniform_alpha`, `rep_to_sources_basic`, `rep_to_pp_basic`, and the two branch separation native-boundary cases as explicit debt.
- Python `nirs4all` RC head is now `a103fd2 docs(parity): refresh rc compatibility ledger`. The current full parity proof remains the runtime code head `3d568ab`: on the selected RC stack (`dag-ml` `7f86a9b`, `dag-ml-data` `e681685`), `pyref_oracle_full` passed with `659 passed, 227 deselected, 1530 warnings` in `2037.46s`; no parity tests were skipped or xfailed. The preceding `42448821` result with `14 skipped / 6 xfailed` is superseded.
- Studio RC head now includes `0653ee0 test(runtime): align Studio default engine contract`; targeted backend runtime/native/quick-run checks passed with RC dag-ml and dag-ml-data on `PYTHONPATH`.
- Studio RC head now includes `fd06d94 ci(studio): run gates on rc branches`; CI/Playwright now run on `rc/**` and select the RC Python library checkout on RC branch runs. Earlier `9190ccc`, `1d1ded5`, and `8141e2e` fixed operator fixtures, RC import precedence, and shared-UI badge reuse.
- Web RC head now includes `8a5dcff ci(web): require upstream catalog siblings`; the public `web.nirs4all.org` build remains GitHub Pages/static/WASM-only and both RC CI and Pages deploy now run client-only, typecheck, Vitest, strict methods ABI + Studio DAG registry catalog validation, strict lite/core shim, build, single-file build, and one browser smoke gate.
- `nirs4all-ui` RC head now includes `8f9f2f6 ci(ui): add package release gate`; CI runs typecheck, Vitest, build, and `npm pack --dry-run` through `npm run ci`.
- Studio backend full pytest passed with the current RC Python/dag-ml/dag-ml-data stack: `2324 passed, 6 skipped` in `1465.99s`. Remaining skips are Windows-only/env/example-access categories rather than operator fixture debt.
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
- Ecosystem RC head now includes `cb1a0bd docs(release): lock selected rc topology`; lock generation validates selected `rc/v1-*` worktrees while preserving canonical public repo paths and nirs4all-core aliases.
- Ecosystem RC head now includes `89e8c63 docs(release): tighten topology accounting`; release surface validation documents `nirs4all-core`, `nirs4all-python`, R/JS-WASM/Rust/MATLAB language surfaces, `nirs4all-ui`, client-side-only Web, providers/cockpit/org, and the narrower aggregate lock boundary.
- Cluster GitGuardian remediation was upgraded from tip cleanup to a targeted history rewrite and refreshed after the latest alert. Published branch/tag refs now point to rewritten clean history: `main` `97b2b38`, `rc/v1-full-refactor` `e843073`, tag `n4a-v1-rc1-2026.07-refactor` `60c1b5a` peeled to `e843073`. Strict scanner-pattern checks over the branch/tag refs are empty; cluster gates are `142 passed, 1 skipped, 1 deselected` on `main` and `145 passed, 1 skipped, 1 deselected` on the RC worktree. GitHub still exposes merged hidden PR refs #1/#2 from 2026-06-04; a read-only Claude audit confirmed that the GitGuardian secret is not present there and only deterministic unit-test token literals remain. Source branches are gone and deleting hidden PR refs is rejected by GitHub, so residual alert closure is a GitGuardian/GitHub-support action after token rotation if the value was ever real.
- RC branches and tag `n4a-v1-rc1-2026.07-refactor` are published for the 20 selected worktrees. `WAVE_4Q_RC_PUBLICATION_REAUDIT.md` rechecked the post-4P heads after repairing missing tags on Studio/UI/Org/Tools/IO/Datasets; Wave 4R then moved Studio/IO/Datasets and regenerated the aggregation lock for IO/Datasets.
- Latest pushed/tagged heads after the Wave 4S CI/Web/Studio refresh: Python
  `1fd3f7b`, dag-ml `a8f6cb3`, dag-ml-data `95e56a7`, Core `0a516e2`,
  Studio `0d8b3cb`, Web `cdb43cc`, UI `8f9f2f6`, Cockpit `f06f7b4`,
  Org `61074ff`, Ecosystem uses the current board HEAD, Providers `7c7c6e9`,
  Tools `7c5070f`, Cluster `9d6ab34`, Formats `32fc87f`, IO `0d20c80`,
  Datasets `cac8742`, Methods `d918c5e`, Repository `ced219f`,
  Benchmarks `06d4146`, Papers `f1d84f4`.
- `aggregation-lock` remains limited to the aggregate core/runtime members. Studio/Web/UI/tools/providers/benchmarks/papers/cluster are tracked by the surface matrix, cutover gates, and agent reports rather than forced into the aggregate lock without an ownership contract.
- Skip/xfail audit is recorded in `RC_SKIP_XFAIL_AUDIT.md`: Studio operator skips and Python registry skips have been burned down; Python full parity on runtime head `3d568ab` now reports no skipped or xfailed parity tests. The current Python head `a103fd2` is docs-only and did not rerun full parity. Remaining skip risk is outside this gate: Studio optional/environment categories and methods/language binding environments.

## Parity Debt To Burn Down

Known parity xfails to fix:

- `concat_transform_pca_svd_plsr`

Known parity xfails to justify or replace with a non-equivalence contract:

- `generator_sample_log_uniform_alpha` (unseeded `_sample_` nondeterminism)
- `rep_to_pp_basic` (documented legacy double-count/aggregation semantic divergence)
- `rep_to_sources_basic` (same legacy double-count/aggregation semantic divergence)

Known legacy-bug xfails:

- `branch_separation_by_tag`
- `branch_separation_by_filter`

Cleared live PipelineCase skip/debt items in `1234db31`:

- `aggregation_classification_vote`
- `branch_separation_by_metadata_auto`
- `refit_params_use_all_partitions`
- `exclude_multi_any_y_and_x`

Remaining targeted skip classes after the broader gate:

- missing local `n4m` binding for methods-backed operators;
- legacy-bug skips for `branch_separation_by_tag` and `branch_separation_by_filter`;
- optional dependency skip for SHAP when absent from the local environment;
- optional dependency skip for `referencing` when absent from the local environment;
- empty-sentinel skip for lockdrop/fallback-boundary markers when no expected fallback cases remain.

Tolerance overrides to review:

- `generator_cartesian_pick`
- `generator_cartesian_stages`
- `generator_cartesian_with_param_range`
- `generator_or_pick_mutex3`
- `generator_or_pick_requires`
- `generator_or_with_pick`

Exact-count parity notes:

- `generator_or_models_pls_ridge`
- `generator_chain_model_configs`

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
- Topology/release distribution matrix coherent across cockpit/org/ecosystem.
- Performance comparison: Python legacy vs `dag-ml`; Studio legacy vs `dag-ml`.
- Final report with selected commits/tags, tests, risks, and remaining decisions.
