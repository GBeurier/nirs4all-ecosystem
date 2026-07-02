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
| Python parity harness | `810 passed, 30 skipped, 11 xfailed` in `_worktrees/INT-nirs4all` | Not production-flip evidence. Xfails/skips must be fixed or explicitly justified. |
| `dag-ml` workspace | `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings` passed | Native runtime baseline is usable for RC work. |
| Studio | `npm run lint:parallel`, `npm run test:parallel`, prior e2e passed | Studio baseline is usable, but dag-ml strict/default workflow evidence still required. |
| Python non-parity tests under strict dag-ml | targeted failures in workspace/session/predict/explain/retrain | Blocks dag-ml production flip. Legacy mode targeted rerun passed. |
| Providers | Ruff, mypy, pytest passed with optional-extra skips | Providers must become neutral contract clients, not a Python-only dependency for core/language packages. |

## Parity Debt To Burn Down

Known parity xfails:

- `concat_transform_pca_svd_plsr`
- `feature_augmentation_replace_three_views`
- `generator_finetune_params_optuna`
- `generator_sample_log_uniform_alpha`
- `rep_to_pp_basic`
- `rep_to_sources_basic`
- `sample_augmentation_after_savgol`
- `sample_augmentation_chained`
- `sample_augmentation_gaussian`

Known legacy-bug xfails:

- `branch_separation_by_tag`
- `branch_separation_by_filter`

Current skip/debt items:

- `aggregation_classification_vote`
- `branch_separation_by_metadata_auto`
- `refit_params_use_all_partitions`
- `exclude_multi_any_y_and_x`

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
| RC-I | Codex/GPT-5.5 `019f2286-ba97-7512-8a9d-88b0995a85dc` | Cluster client/server scheduler, DAG rights, minimal client contracts. | integrated in cluster commit `ac84df7`; security docs follow-up `75e89e7` | `RC_I_CLUSTER_SCHEDULER.md`, `RC_SECURITY_GITGUARDIAN_CLUSTER.md` |
| RC-J | Codex/GPT-5.5 `019f2286-bc1a-70f2-af8f-1122c242f637` | Formats/IO/datasets reference bridge and get/load dataset contracts. | integrated in IO `bf0add5`, datasets `28d08977` | `RC_J_FORMATS_IO_DATASETS.md` |
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
