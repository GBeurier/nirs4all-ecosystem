# RC V1 Release Candidate Final Report

Date: 2026-07-03

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Status

The selected NIRS4ALL V1 full-refactor release-candidate heads are integrated,
published on their RC branches, tagged with `n4a-v1-rc1-2026.07-refactor`, and
verified by the current local and GitHub gates listed below.

This report does not claim that production has been switched. Current production
heads remain intact until the converter is distributed and the remaining
release-environment risks are accepted or closed.

## Published Heads

All worktrees were clean at the final audit. For each row, the remote RC branch
and the remote tag both resolve to the listed commit.

| Surface | Worktree | Branch | Head |
| --- | --- | --- | --- |
| Python oracle/surface | `RC-v1-nirs4all-python` | `rc/v1-full-refactor-python` | `bf242e48` |
| Native runtime | `RC-v1-dagml` | `rc/v1-full-refactor` | `a8f6cb38` |
| Native data runtime | `RC-v1-dmd` | `rc/v1-full-refactor` | `616f3e5f` |
| Core aggregate | `RC-v1-nirs4all-core` | `rc/v1-full-refactor-core` | `ba959a15` |
| Studio | `RC-v1-studio` | `rc/v1-full-refactor` | `15082420` |
| Web | `RC-v1-web` | `rc/v1-full-refactor` | `5be833d0` |
| Shared UI | `RC-v1-ui` | `rc/v1-full-refactor` | `69501bdd` |
| Cockpit | `RC-v1-cockpit` | `rc/v1-full-refactor` | `6cdc829e` |
| Public site | `RC-v1-org` | `rc/v1-full-refactor` | `2d442659` |
| Ecosystem docs/contracts | `RC-v1-ecosystem` | `rc/v1-full-refactor` | `00576616` |
| Providers/contracts | `RC-v1-providers` | `rc/v1-full-refactor` | `2cfcca6c` |
| Migration tools | `RC-v1-tools` | `rc/v1-full-refactor` | `7c5070f5` |
| Cluster | `RC-v1-cluster` | `rc/v1-full-refactor` | `96434605` |
| Formats | `RC-v1-formats` | `rc/v1-full-refactor` | `32fc87f5` |
| IO | `RC-v1-io` | `rc/v1-full-refactor` | `26963d5b` |
| Datasets | `RC-v1-datasets` | `rc/v1-full-refactor` | `7b1b805a` |
| Methods | `RC-v1-methods` | `rc/v1-full-refactor` | `115077ae` |
| Repository | `RC-v1-repository` | `rc/v1-full-refactor` | `ced219ff` |
| Benchmarks | `RC-v1-benchmarks` | `rc/v1-full-refactor` | `6e4c6306` |
| Papers | `RC-v1-papers` | `rc/v1-full-refactor` | `f1d84f4c` |

## Gate Evidence

- Full Python-reference parity on Python `bf242e48`: split run totals
  `887 passed`, `0 skipped`, `0 xfailed`, `0 failed`.
- Non-full cutover sweep on ecosystem `00576616`: `passed: true`,
  `failed_required: []`.
- Strict core language gate: Rust, Python, WASM, R, and Octave parity all pass
  on selected Core `ba959a15` with Methods `115077ae`.
- Native/export parity: `native_n4a_export` passed `19` integration tests.
- Studio runtime route gate: `82 passed`, Ruff clean; GitHub Studio `CI` and
  `Playwright E2E Tests` are green on `15082420`.
- Web client-side-only/runtime contract gate: typecheck, Vitest runtime test,
  production build, single-file build, and served browser smoke passed on
  `5be833d0`.
- Migration/converter gate: tools full pytest is `114 passed`; cutover
  `migration_tool_smoke` passed.
- Providers local sibling release: passed against datasets, repository,
  benchmarks, and papers providers without writing ecosystem state.
- Release-lock validation and fetchability: local and GitHub validation passed;
  cutover fetchability reports `7/7` aggregation members checked out.
- Performance comparison: `perf_cross_engine_compare` passed with Python
  direct `dag-ml/legacy` run ratio `0.748x` and Studio worker run ratio
  `0.680x`, both below required ceilings.
- Cluster DAG advisory: `3 passed`, Ruff clean.
- Cluster GitGuardian hardening: active branch/tag refs are clean under the
  committed scanner guard; GitHub `CI` and `version-guard` are green for the
  selected RC and hardened `main`.

## GitHub Checks

- Ecosystem `00576616`: `version-guard`, release-lock tooling, and
  release-lock validation completed successfully.
- Python `bf242e48`: `CI`, `CodeQL`, `Documentation`, `Docs Quality`, and
  `version-guard` completed successfully.
- `dag-ml-data` `616f3e5f`: `CI` and `version-guard` completed successfully.
- Studio `15082420`: `CI` and `Playwright E2E Tests` completed successfully.
- Cluster `96434605` and hardened `main` `aec2a10`: `CI` and `version-guard`
  completed successfully.

## Decisions

- The current Python `nirs4all` library remains the behavioral oracle. Any
  future parity divergence is fixed unless explicitly documented as a legacy bug
  and covered by tests.
- `nirs4all-core` is the target aggregate/core identity. The locked member still
  uses the current `nirs4all-lite` remote until the GitHub repo rename is
  executed; the public matrix records `nirs4all-core` as the alias/target.
- `nirs4all-python` remains represented by the current `nirs4all` repo and RC
  branch until the fork/rename step is performed. Production is not switched by
  this RC tag.
- `nirs4all-ui` is the shared UI package consumed by Studio and Web. It is not
  part of the aggregation lock because it is not a runtime/parser/ML member.
- `web.nirs4all.org` remains client-side-only. The selected Web proof builds a
  static/WASM browser product, not a Python backend.
- Providers are optional Python clients over neutral contracts. R/WASM/native
  consumers use schemas/fixtures and IO/materialization contracts rather than
  depending on a Python provider runtime.
- Missing R/Octave runtimes are not accepted release-green skips on this RC.
  The selected heads have strict local R and Octave parity proof.

## Remaining Risks

- Licensed MATLAB host execution is still distinct from Linux Octave proof and
  must be recorded before any GA claim that depends on licensed MATLAB.
- Studio all-in-one and Docker release jobs still need release-environment proof,
  although their source pins are immutable SHAs and Studio CI/Playwright are
  green.
- Dataset remote hosting, DOI/file-id routes, and every-catalog-entry retrieval
  remain promotion-path items; current proof covers catalog/contracts/bridges.
- GitGuardian may still display old placeholder CLI examples from historical or
  hidden PR refs in `nirs4all-cluster`. Active branch/tag heads are guarded and
  clean; rotate only if GitGuardian exposes a concrete non-placeholder value.
- Run full Python-reference parity again after any later movement of Python,
  `dag-ml`, `dag-ml-data`, Methods, or parity oracle fixtures.

## Local Validation For This Final Report

- `python3 -m json.tool` on updated cutover and public-surface matrices.
- `python3 scripts/n4a_release_surface_matrix.py validate`.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all`.
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`.
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -p no:cacheprovider` -> `22 passed`.
- `git diff --check`.
- Remote branch/tag audit over all 20 selected RC worktrees -> all branch refs
  and tag refs resolve to the selected commits.
