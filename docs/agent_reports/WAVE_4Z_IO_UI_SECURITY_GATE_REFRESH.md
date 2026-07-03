# Wave 4Z - IO/UI/Security Gate Refresh

Date: 2026-07-03

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Scope

Refresh the remaining ambiguous RC V1 gates without rerunning full Python
parity:

- `nirs4all-io` `DatasetPackage` non-Python/materialization coverage.
- `nirs4all-ui` source package and Web client-side-only gates.
- Cluster GitGuardian alert recheck after the July 2 alert.
- Local R/Octave/MATLAB toolchain reality check.

## Agent Reports

| Agent | Lane | Result |
| --- | --- | --- |
| Turing the 3rd | IO/datasets read-only audit | Confirmed `datasets` non-Python owns resolve/fetch/verify and neutral descriptors, not package assembly. Flagged missing `io-core` payload-variant coverage. |
| Einstein the 3rd | UI/Web read-only audit | Confirmed `nirs4all-ui` is a reusable package and Web `studio-lite` is client-side-only. Noted that UI package surface is intentionally small today. |
| Singer the 3rd | Cluster GitGuardian read-only audit | Confirmed `main`, `rc/v1-full-refactor`, and the RC tag are clean; only immutable merged PR refs still contain placeholder examples such as `--token dev`. |
| Dewey the 3rd | Web/Ecosystem CI audit | Confirmed Web clean-runner failure came from missing vendored `nirs4all-ui` subpath `dist` files and Ecosystem failure came from invalid release-lock CLI argument ordering. |
| Claude Code Fable/Opus | Cluster/Web/Ecosystem read-only audit | Found no high-entropy/live Cluster secret on current heads. Identified the likely GitGuardian trigger as the documentation placeholder `alice:s3cr3t:submitter`, now removed from HEAD but still reachable in history. |

## Integrated Changes

`nirs4all-io` moved from `0d20c80` to `71aaaf5`:

- Added `io-core` tests for inline `SpectralRecordSet` manifest hashing.
- Added `io-core` tests for declared URI-backed variants:
  `SequenceBlock`, `GenotypeMatrix`, `MaskBlock`, and bare `UriBackedPayload`.
- Pushed branch `rc/v1-full-refactor` and retagged
  `n4a-v1-rc1-2026.07-refactor` to `71aaaf5`.
- Regenerated the aggregation lock; only the IO member commit changed.

`nirs4all-web` moved from `85dcd79` to `974f71a`:

- Added the generated vendored `nirs4all-ui` `dist` subpaths used by package
  exports: `components`, `runtime`, and `score`.
- Updated the `nirs4all-ui` sibling GitHub Action to run `npm ci` and
  `npm run build` after checkout so the drift check compares against a clean
  source checkout with built `dist` artifacts.
- Pushed branch `rc/v1-full-refactor` and retagged
  `n4a-v1-rc1-2026.07-refactor` to `974f71a`.

`nirs4all-ecosystem` moved from `13c84c9` to `05da7dc`:

- Fixed the `version-guard` workflow to pass global `--workspace-root` before
  the `validate` subcommand.
- Updated `checkout-members` to clone into `selected_workspace_path` when one is
  declared, making the documented `checkout-members` then `validate` flow
  directly reproducible for RC worktrees.
- Added a regression test that generates a lock from a selected RC workspace,
  checks out members into a clean root, and validates the lock against that root.

No code changes were made in `nirs4all-ui`, `nirs4all-datasets`, or
`nirs4all-cluster`.

## Tests And Audits

`nirs4all-io`:

- `cargo fmt --all --check` -> passed.
- `cargo test -p nirs4all-io-core package --quiet` -> `12 passed`.
- `cargo test -p nirs4all-io-core --quiet` -> `103 passed` plus crate
  integration targets all green.
- `cargo test -p nirs4all-io-dagml --quiet` -> `5 passed` plus `3 passed`.
- `PYTHONPATH=src python3.11 -m pytest -q tests/test_dataset_package.py` ->
  `8 passed`.
- `wasm-pack build bindings/wasm --target nodejs --out-dir pkg` -> passed.
- `node bindings/wasm/tests/node_smoke.cjs` -> passed.
- `node bindings/wasm/tests/idiomatic_smoke.mjs` -> passed.
- `bash tests/cross_binding/verify.sh` with Linux Node in `PATH` -> CLI/WASM
  byte-for-byte agreement.

`nirs4all-ui`:

- `npm run ci` with Linux Node `v22.21.1` -> typecheck, Vitest `52 passed`,
  build, and `npm pack --dry-run` passed.

`nirs4all-web/studio-lite`:

- `tsc --noEmit` -> passed.
- `vitest run --config vitest.config.ts src/app/client-side-only.test.ts` ->
  `2 passed`.
- Full `vitest run` -> `21` files, `134 passed`.
- `node scripts/validate-catalog.mjs` -> catalog/ABI/Studio DAG registry in
  sync.
- `node scripts/sync-ui-shim.mjs --check` and
  `node scripts/sync-lite-shim.mjs --check` -> up to date.
- `npm run build:single` -> passed, producing a single static HTML artifact.
- `npm run build && node scripts/run-smokes.mjs` -> production served build plus
  `23/23` browser smokes passed. The smoke set exercised `dag-ml-wasm`,
  `libn4m`, `dag-ml-data`, Web worker fallback errors, `.n4a` export/import,
  datasets upload, branch/generator DAGs, and prediction/chart flows without JS
  console errors.
- Clean-runner UI vendor reproduction: clone `nirs4all-ui@rc/v1-full-refactor`,
  `npm ci`, `npm run build`, then
  `NIRS4ALL_UI_SHIM_REQUIRED=1 npm run check:ui-shim` from Web -> passed.
- GitHub Actions on `974f71a`: `version-guard` success and `web-ci` success
  (`studio-lite client-only gate` completed).

Cluster GitGuardian:

- Strict active-tip scanner over `main`, `rc/v1-full-refactor`, and
  `n4a-v1-rc1-2026.07-refactor` found no token/secret/password/api-key literal
  value.
- `git ls-remote`/local ref checks still show immutable PR refs exposing only
  placeholder CLI text:
  `PROTOTYPE_DESIGN.md:167` contains `--token dev` on PR refs #1/#2.
- GitHub rejected previous deletion attempts for `refs/pull/*`; residual closure
  is GitGuardian/GitHub-support handling unless GitGuardian reveals a real
  non-placeholder value.
- A second read-only Codex audit checked `origin/main`, `origin/rc/v1-full-refactor`,
  the RC tag, and merged PR refs #1/#2. Current published heads remain clean; PR
  refs only contain placeholder/test values. Local token files at the workspace
  root were not read and are outside a Git repository.
- Claude Code's independent read-only audit found the likely historical trigger:
  `--principal alice:s3cr3t:submitter`. This is a non-secret documentation
  placeholder, not a live credential; current HEAD is cleaned to abstract
  placeholders, but the old placeholder remains reachable in historical commits.
  The practical closure path is GitGuardian dashboard false-positive/remediated
  handling unless GitGuardian discloses an actual non-placeholder value.

Release lock:

- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees generate ...`
  -> wrote lock.
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate ...`
  -> passed.
- `python3 scripts/n4a_release_surface_matrix.py validate` -> passed.
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable`
  -> `7/7` member commits checked out.
- `git ls-remote https://github.com/GBeurier/nirs4all-io.git refs/heads/rc/v1-full-refactor refs/tags/n4a-v1-rc1-2026.07-refactor`
  -> both refs resolve to `71aaaf5`.
- Clean CI reproduction after the workflow/tooling fix:
  `checkout-members --output /tmp/n4a-ecosystem-ci-validate` then
  `--workspace-root /tmp/n4a-ecosystem-ci-validate validate` -> passed across
  all 7 locked members.
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py -p no:cacheprovider`
  -> `17 passed`.
- GitHub Actions on `05da7dc`: `version-guard` success, with
  `release-lock-tooling`, `guard`, and `release-lock-validation` all completed
  successfully.

## Decisions

- `nirs4all-datasets` remains a dataset catalog/acquisition/provider surface.
  Its non-Python bindings resolve, fetch, and verify neutral descriptors; they do
  not assemble `DatasetPackage`. That assembly remains owned by `nirs4all-io`.
- The remaining non-Python `DatasetPackage` risk is no longer “no coverage”.
  Rust `io-core`, `io-dagml`, and WASM smoke/cross-binding coverage exist. The
  unresolved part is final host coverage for R/Octave/MATLAB toolchains and any
  broader non-Python materialization scenarios not represented by the current
  WASM/Rust gates.
- `nirs4all-ui` is a valid shared package, but its current component surface is
  intentionally narrow: one exported React component plus runtime/score helpers.
  A larger design-system migration remains future feature work, not an RC
  blocker for the current shared runtime status use case.
- Windows R 4.3.3 exists under `/mnt/c/Program Files/R/...`, but WSL has no
  Linux `R`/`Rscript`/`octave`/`matlab` in `PATH`. Windows R emits CMD/UNC cwd
  warnings from WSL and is not a substitute for the Linux release binding gates.

## Remaining Risks

- R, Octave, and MATLAB binding release proofs still need suitable host
  toolchains or CI/manual release runners.
- Web `build:single` and served-worker browser smokes both passed locally.
  Keep both in the final Web cutover gate because they exercise different
  engines.
- GitGuardian may keep reporting immutable historical PR refs. Active branch/tag
  heads are clean; close the alert as stale/placeholder unless GitGuardian
  discloses an actual token value.
