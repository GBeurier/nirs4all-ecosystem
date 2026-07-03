# Wave 4AC - Non-Python Gates, Release Packaging, Security Refresh

Date: 2026-07-03

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Scope

This batch keeps production heads intact and updates only selected RC branches
and tags. Full Python parity was not rerun in this batch; the latest full proof
remains Python `6a2c720` with `887 passed`, `0 skipped`, `0 xfailed`, and
`0 failed`.

## Integrated Changes

### Studio

Commits:

- `15f70e3 ci(studio): bake rc dag runtimes in releases`
- `5907639 ci(studio): fix release docker build args context`

Files modified:

- `.github/workflows/release-unified.yml`
- `Dockerfile`
- `scripts/bake-standalone-backend.cjs`
- `scripts/build-archive-standalone.cjs`
- `scripts/setup-python-env.cjs`

Decisions:

- All-in-one release archive jobs now checkout selected RC sources for Python
  `nirs4all`, `dag-ml`, and `dag-ml-data`, then install those local sources
  before packaging.
- Docker release builds now use selected RC source archives for the same Python
  runtime stack instead of hard-pinning the old published `nirs4all` package.
- Workflow matrix expressions were normalized so GitHub Actions accepts the
  release workflow on `rc/**`.

Tests:

- YAML parse of `.github/workflows/release-unified.yml` -> PASS.
- `node --check scripts/setup-python-env.cjs scripts/bake-standalone-backend.cjs scripts/build-archive-standalone.cjs` -> PASS.
- Parser smoke for the new local `dag-ml` / `dag-ml-data` archive options -> PASS.
- `npm run lint:parallel` -> PASS.
- `npm run test:parallel` -> Vitest `517` files / `3709` tests passed; backend
  pytest `2335 passed`, `330 warnings`.
- GitHub Actions on `5907639`: `CI` -> success; `Playwright E2E Tests` -> success.

### Cluster / GitGuardian

Commits:

- `eaf79a0 docs(security): avoid cluster CLI option metavars` on `main`
- `ffeaf4b docs(security): avoid cluster CLI option metavars` on
  `rc/v1-full-refactor`

Files modified:

- `docs/cli-reference.md`
- `docs/rest-api.md`
- `nirs4all_cluster/cli.py`

Decisions:

- The active heads no longer expose secret-shaped CLI option examples such as
  `--principal NAME:TOKEN:ROLES` or `--principal <principal-spec>`.
- Parser behavior is unchanged; only docs/help metavar text was neutralized for
  scanner hygiene.
- The remaining GitGuardian risk is historical/stale refs or hidden PR refs. If
  GitGuardian shows a real non-placeholder value, rotate it out of band; current
  active branch/tag evidence does not show a real credential.

Tests:

- Active remote refs scan for inline `--principal` / `--token` secret-shaped
  values over `origin/main`, `origin/rc/v1-full-refactor`, and
  `n4a-v1-rc1-2026.07-refactor` -> `0` candidates.
- `ruff check docs/cli-reference.md docs/rest-api.md nirs4all_cluster/cli.py`
  -> PASS on both main and RC worktrees.
- `pytest tests/test_rbac.py -q` -> `24 passed` on both main and RC worktrees.
- GitHub Actions on `eaf79a0`: `CI` and `version-guard` -> success.
- GitHub Actions on `ffeaf4b`: `CI` and `version-guard` -> success.

### Datasets R Bridge

Commit:

- `7b1b805 test(r): cover datasets io bridge delimiter`

Files modified:

- `bindings/r/nirs4alldatasets/tests/smoke.R`

Decision:

- The datasets R smoke writes comma-delimited CSV fixtures and then exercises the
  optional `nirs4allio` bridge. It must therefore declare
  `params = list(delimiter = ",")` on both source specs.
- This removes a real gap: when `nirs4allio` is installed, the bridge now runs
  instead of failing behind an optional-environment skip.
- Coverage for IO's default semicolon behavior remains in IO-owned loader tests.

Tests:

- `R_LIBS_USER=/tmp/tmp.XATBhR4fVI conda run -n p4a-r Rscript bindings/r/nirs4alldatasets/tests/smoke.R` -> `R binding smoke OK`.
- Combined fresh R gate with one install library:
  - install/run `nirs4allio` R package -> `R binding smoke OK`;
  - install/run `nirs4alldatasets` R package -> `R binding smoke OK`;
  - final package check -> `combined R IO+datasets packages OK`.
- `PYTHONPATH=src python3.11 -m pytest -q tests/test_loaders.py::test_read_csv_semicolon_with_header tests/test_loaders.py::test_read_csv_comma_decimal tests/test_loaders.py::test_effective_params_source_wins -p no:cacheprovider` in `RC-v1-io` -> `3 passed`.
- `git diff --check` -> PASS.

Review:

- Codex subagent `019f266e-3b1f-7553-bb45-9b5218edc994` reviewed the R smoke
  diff read-only and confirmed the delimiter fix is appropriate for this
  gate, with the caveat that semicolon-default coverage should remain in IO
  tests. The coordinator reran those IO tests successfully.

### Ecosystem

Files modified:

- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/agent_reports/RC_SECURITY_GITGUARDIAN_CLUSTER.md`
- `docs/agent_reports/RC_V1_FULL_REFACTOR_CONTROL.md`
- `docs/agent_reports/WAVE_4AC_NONPY_GATES_SECURITY.md`

Decisions:

- The aggregation lock was regenerated after moving datasets to `7b1b805`.
- Full Python parity remains intentionally deferred until the next large
  integrated batch.

Tests:

- `python3 scripts/n4a_release_surface_matrix.py validate` -> PASS.
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> PASS.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all` -> PASS.
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -p no:cacheprovider` -> `22 passed`.
- `python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --skip pyref_oracle_full --json` -> PASS. Required gates passed; `pyref_oracle_full` was the only intentionally skipped gate.

### Non-Python Binding Gates

Additional local gate evidence collected before this report:

- Core strict WASM parity:
  `make test-wasm-parity-strict NIRS4ALL_METHODS_ROOT=/home/delete/nirs4all/_worktrees/RC-v1-methods`
  -> Node TAP `15` tests, `0` skipped.
- Core R V1 public surface:
  `conda run -n p4a-r make test-r-v1-surfaces` -> PASS.
- Core R strict portable parity:
  `conda run -n p4a-r make test-r-parity NIRS4ALL_METHODS_ROOT=/home/delete/nirs4all/_worktrees/RC-v1-methods`
  -> PASS with `n4m` installed from the selected Methods RC and
  `NIRS4ALL_LITE_REQUIRE_METHODS_PARITY=1`.
- IO WASM:
  `wasm-pack build bindings/wasm --target nodejs --out-dir pkg` plus
  `node bindings/wasm/tests/node_smoke.cjs` -> `wasm node smoke OK`.
- IO Octave/MATLAB preview:
  `conda run -n pls4all_r bash bindings/matlab/build_and_test.sh` ->
  `matlab/octave binding smoke OK`.
- IO R:
  `conda run -n p4a-r bash bindings/r/build_and_test.sh` -> PASS.
- Datasets WASM:
  node smoke -> `wasm node smoke OK`; web build -> PASS; `npm pack --dry-run`
  from the generated package directory -> PASS.
- Datasets R:
  standalone R package smoke -> PASS; combined R IO+datasets gate above removes
  the optional bridge skip for this environment.

## Publication

- `nirs4all-studio` branch `rc/v1-full-refactor` and tag
  `n4a-v1-rc1-2026.07-refactor` point to `5907639`.
- `nirs4all-cluster` branch `rc/v1-full-refactor` and tag
  `n4a-v1-rc1-2026.07-refactor` point to `ffeaf4b`; `main` points to `eaf79a0`.
- `nirs4all-datasets` branch `rc/v1-full-refactor` and tag
  `n4a-v1-rc1-2026.07-refactor` point to `7b1b805`.
- The aggregation lock now pins datasets `7b1b805`.

## Workspace Notes

Running the datasets Rust dependency helper moved two dependency worktrees during
the gate sweep. Rescue branches were created before accepting that movement:

- `_worktrees/nirs4all-formats`: `rescue/2026-07-03-pre-ensure-deps-86218e6`
  points to `86218e6`.
- `_worktrees/nirs4all-io`: `rescue/2026-07-03-pre-ensure-deps-dac4841`
  points to `dac4841`.

These rescue refs are local audit anchors only; selected RC worktrees remain the
source of release evidence.

## Remaining Risks

- Full Python parity was intentionally not rerun in this batch.
- R evidence now covers core public surface, core strict portable parity,
  IO package smoke, datasets package smoke, and combined IO+datasets package
  usage. This is still not a claim that every R surface is feature-complete.
- Current Octave/MATLAB evidence is an IO smoke gate, not full MATLAB/Octave
  feature parity across every release surface.
- Historical GitHub objects or hidden PR refs can still trigger stale
  GitGuardian findings even when selected branch/tag heads scan clean.
