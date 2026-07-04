# Wave 5P - Datasets R-universe vendor fix

Date: 2026-07-04

## Scope

- Fix the stale `nirs4alldatasets` R-universe publication path without changing the datasets API.
- Preserve the architecture boundary: `nirs4all-datasets` consumes `nirs4all-formats` and `nirs4all-io`; it does not duplicate reader logic.
- Keep Python `nirs4all` and `nirs4all-studio` production releases untouched.

## Changes Integrated

- `GBeurier/nirs4all-datasets`:
  - commit `8806fe59` updates `bindings/r/nirs4alldatasets/configure` so R vendoring can fetch missing sibling reader workspaces from GitHub using the exact versions declared in the root `Cargo.toml`;
  - the same commit updates `.prepare` to document the real R-universe flow: R-universe clones `nirs4all-datasets`, then `configure` fetches `nirs4all-formats` / `nirs4all-io` only when sibling checkouts are absent.
  - commit `4a69474c` hardens the fallback clone path by removing any partial clone directory before retrying from the default branch.
  - commit `b053c67b` fixes the cleanup path for R-universe fetch worktrees by avoiding command substitution around the repository resolver; the `EXIT` trap now sees the temporary fetch root and removes it.

## Verified Checks

- Local packaging gates:
  - `sh -n bindings/r/nirs4alldatasets/configure && sh -n bindings/r/nirs4alldatasets/.prepare` -> pass;
  - `N4DS_FORMATS_REPO=/tmp/n4ds-missing-formats N4DS_IO_REPO=/tmp/n4ds-missing-io N4DS_R_VENDOR=1 ./configure` -> pass; fetched `nirs4all-formats` `v0.2.2` and `nirs4all-io` `v0.1.6`, then produced a self-contained `vendor.tar.xz`;
  - `PATH=/home/delete/miniconda3/envs/pls4all_r44/bin:$PATH R CMD build bindings/r/nirs4alldatasets` -> pass, built `nirs4alldatasets_0.3.3.tar.gz`;
  - `CARGO_NET_OFFLINE=true PATH=/home/delete/miniconda3/envs/pls4all_r44/bin:$PATH R CMD INSTALL -l /tmp/n4ds-r-lib nirs4alldatasets_0.3.3.tar.gz` -> pass; install used bundled vendored Rust tree and `cargo build --offline`;
  - `Rscript -e '.libPaths(c("/tmp/n4ds-r-lib", .libPaths())); library(nirs4alldatasets); packageVersion("nirs4alldatasets")'` -> `0.3.3`;
  - `./scripts/bump_version.sh --check` -> pass;
  - `git diff --check` -> pass.
- GitHub gates on `8806fe59`:
  - `version-sync` -> success;
  - `version-guard` -> success;
  - `CI` -> success;
  - `Site (GitHub Pages)` -> success after rerun of a transient GitHub Pages deploy failure.
  - `ABI Surface` -> success on Windows, macOS, and Linux.
- Additional checks after `4a69474c`:
  - `sh -n bindings/r/nirs4alldatasets/configure && sh -n bindings/r/nirs4alldatasets/.prepare` -> pass;
  - `N4DS_FORMATS_REPO=/tmp/n4ds-missing-formats N4DS_IO_REPO=/tmp/n4ds-missing-io N4DS_R_VENDOR=1 ./configure` -> pass after the fallback-clone hardening;
  - `./scripts/bump_version.sh --check` -> pass;
  - `git diff --check` -> pass.
- Additional checks after `b053c67b`:
  - `sh -n bindings/r/nirs4alldatasets/configure && sh -n bindings/r/nirs4alldatasets/.prepare` -> pass;
  - `N4DS_FORMATS_REPO=/tmp/n4ds-missing-formats N4DS_IO_REPO=/tmp/n4ds-missing-io N4DS_R_VENDOR=1 ./configure` -> pass with `nirs4all-formats` `v0.2.2` and `nirs4all-io` `v0.1.6` fetched from tags;
  - `find /tmp -maxdepth 1 -type d -name 'n4ds-r-vendor.*' -print` after the forced fallback configure -> empty;
  - `./scripts/bump_version.sh --check` -> pass;
  - `git diff --check` -> pass.

## Review

- Claude Code read-only review (`opus`, max effort) found no blocking issue in the R-universe vendoring approach.
- The review did identify the temporary-worktree cleanup bug caused by shell command substitution; this is fixed in `b053c67b`.
- Remaining review suggestions are non-blocking hardening items: add a dedicated shell harness for all fallback branches, keep the install path covered by an explicit no-network assertion, and future-proof the dependency-pin parser if the manifest format changes.

## Publication Status

- R-universe still serves `nirs4alldatasets` `0.2.3` at the time of this report.
- The current R-universe failure record is still the previous `0.3.3` build from commit `8551c9f0`, which failed because the R package could not find sibling `nirs4all-formats` / `nirs4all-io` workspaces during vendoring.
- The source registry `GBeurier/GBeurier.r-universe.dev` is not commit-pinned: `nirs4alldatasets` points to `https://github.com/GBeurier/nirs4all-datasets` with subdir `bindings/r/nirs4alldatasets`.
- Manual `Update universe` dispatch on `r-universe/gbeurier` failed with HTTP 403 for the available GitHub token, so the external refresh is waiting for the normal R-universe sync/build cycle.

## Decisions

- The fix fetches version-tagged upstream workspaces only in `N4DS_R_VENDOR=1` mode and validates the fetched workspace versions against `nirs4all-datasets/Cargo.toml`.
- The installed source package path remains offline: users and R-universe install from the tarball using the bundled vendored Rust tree, not network or adjacent worktrees.
- No tests were skipped, xfailed, or weakened.

## Risk Notes

- R-universe publication is not yet confirmed green after the new commits because the external sync has not picked up `b053c67b`.
- The local offline install is a strong reproduction of the failing source-install path, but the final public gate remains the next R-universe `nirs4alldatasets 0.3.3` run.
