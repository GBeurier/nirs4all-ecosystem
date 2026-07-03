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
| Claude Code Opus | Cluster GitGuardian read-only audit | Hit max-turns before a final report, but the logged commands found no high-entropy/live secret and mapped residual `--token dev` exposure to immutable PR refs. |

## Integrated Changes

`nirs4all-io` moved from `0d20c80` to `71aaaf5`:

- Added `io-core` tests for inline `SpectralRecordSet` manifest hashing.
- Added `io-core` tests for declared URI-backed variants:
  `SequenceBlock`, `GenotypeMatrix`, `MaskBlock`, and bare `UriBackedPayload`.
- Pushed branch `rc/v1-full-refactor` and retagged
  `n4a-v1-rc1-2026.07-refactor` to `71aaaf5`.
- Regenerated the aggregation lock; only the IO member commit changed.

No code changes were made in `nirs4all-ui`, `nirs4all-web`, `nirs4all-datasets`,
or `nirs4all-cluster`.

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
