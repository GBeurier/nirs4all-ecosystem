# Wave 4AU Cutover Language Gate Refresh

Date: 2026-07-03

## Scope

Refresh the final non-full cutover proof after Wave 4AT made the Python
reference parity proof current on Python `bf242e48`. This wave focuses on the
previous cutover blocker: required R and MATLAB/Octave aggregate language
surfaces in `nirs4all-core`.

## Environment

- Ecosystem head: `cb095bf3`
- Python head: `bf242e4854693ccb048b7f0ffc5f3fdd2380315a`
- Core head: `ba959a15`
- Methods head: `115077ae`
- Linux Node/npm: `/home/delete/.nvm/versions/node/v22.21.1/bin`
- R runtime: `/home/delete/miniconda3/envs/p4a-r/bin`
- Octave runtime: `/home/delete/miniconda3/envs/pls4all_r/bin`
- `OCTAVE_HOME=/home/delete/miniconda3/envs/pls4all_r`
- `NIRS4ALL_METHODS_ROOT=/home/delete/nirs4all/_worktrees/RC-v1-methods`

## Commands

Targeted language gate:

```bash
env "PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/miniconda3/envs/p4a-r/bin:/home/delete/miniconda3/envs/pls4all_r/bin:$PATH" "OCTAVE_HOME=/home/delete/miniconda3/envs/pls4all_r" "NIRS4ALL_METHODS_ROOT=/home/delete/nirs4all/_worktrees/RC-v1-methods" make test-v1-surfaces test-r-parity test-matlab-parity
```

Non-full cutover sweep:

```bash
env "PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/miniconda3/envs/p4a-r/bin:/home/delete/miniconda3/envs/pls4all_r/bin:$PATH" "OCTAVE_HOME=/home/delete/miniconda3/envs/pls4all_r" "NIRS4ALL_METHODS_ROOT=/home/delete/nirs4all/_worktrees/RC-v1-methods" python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --skip pyref_oracle_full --json
```

Full log:

- `/tmp/n4a_cutover_nonfull_cb095bf_20260703.log`

## Results

- Targeted `nirs4all-core` gate passed:
  - Rust fmt/clippy/workspace tests
  - Python V1 surface unittest: `53 tests OK`
  - WASM V1 surface: `14` Node tests passed plus TypeScript typecheck
  - R package install and strict R portable parity passed
  - MATLAB/Octave strict parity passed under Octave
- Cutover sweep result: `passed: true`, `failed_required: []`.
- Required gate durations from the sweep:
  - `installed_n4m_proof`: `84.422s`
  - `native_n4a_export`: `53.026s`
  - `studio_runtime_routes`: `4.758s`
  - `web_runtime_contract`: `24.914s`
  - `dagml_lockstep`: `37.529s`
  - `dagml_data_lockstep`: `15.495s`
  - `migration_tool_smoke`: `5.424s`
  - `release_lock_fetchability_audit`: `56.968s`
  - `lite_v1_surfaces`: `6.468s`
  - `perf_cross_engine_compare`: `28.247s`
  - `cluster_dag_advisory`: `3.544s`
- Performance gate from the sweep:
  - Python direct `dag-ml/legacy` run ratio: `0.748x`, total ratio: `0.786x`
  - Studio worker `dag-ml/legacy` run ratio: `0.680x`, total ratio: `0.736x`

`pyref_oracle_full` was intentionally skipped in the cutover sweep because Wave
4AT already ran the full split Python parity proof on the same selected Python,
`dag-ml`, and `dag-ml-data` heads: `887 passed`, `0 skipped`, `0 xfailed`,
`0 failed`.

## Decisions

- The previous `lite_v1_surfaces` blocker was environmental, not product
  parity debt. The first failed local attempt used Windows `npm` from PATH
  inside WSL; the accepted proof pins Linux nvm `node/npm` first.
- Required R and Octave runtime parity is now recorded locally for the selected
  RC core/methods heads. Missing R/Octave execution is no longer an accepted
  skip on this RC batch.
- Licensed MATLAB host proof remains distinct from Linux Octave proof and must
  be recorded explicitly before any GA claim that depends on licensed MATLAB.

## Risks

- Studio all-in-one and Docker release jobs remain release-environment proof,
  although Studio CI and Playwright are green on `1508242`.
- Dataset remote hosting/DOI routes and every-catalog-entry retrieval remain
  promotion-path items outside this cutover sweep.
- R/Octave proof depends on local conda runtimes being selected explicitly; CI
  release jobs must provision equivalent runtimes rather than falling back to
  if-available skips.
