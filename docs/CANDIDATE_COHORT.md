# Candidate cohorts: test the chain before releasing it

A *candidate cohort* names, for each member of the dependency chain, the source
to test: a commit, a branch, a local working tree, or the published release.
`scripts/n4a_cohort.py` assembles that cohort from source without publishing
anything and runs the chain's gates in one go, from cheap to expensive, then
says which layer broke first. Once a cohort is green, `release-plan` prints the
ordered release of exactly the tested commits.

Chain order (the order of the summary and of releases): Methods, Formats,
DAG-ML-Data, IO, DAG-ML, Core, SDK, Studio, Web.

## Files

| File | Role |
| --- | --- |
| `scripts/n4a_cohort.py` | `init`, `run`, `summary`, `release-plan`. |
| `scripts/n4a_cohort_studio_e2e.py` | One real Studio run on the cohort (called by the Studio gate). |
| `docs/contracts/release/cohort/members.n4a.json` | Reviewed recipes (`n4a.cohort-members/v1`): per member its Python projects, native build, published packages, release tags and gates. Version sources come from `aggregation-manifest.n4a.json` for its components. |
| `docs/contracts/release/cohort/*.n4a.json` | Reviewed cohort manifests (`n4a.candidate-cohort/v1`), such as `acceptance-20261118.n4a.json`. |
| `.github/workflows/candidate-cohort.yml` | The same run on a hosted Linux runner. |

## Manifest

```json
{
  "schema_version": "n4a.candidate-cohort/v1",
  "cohort_id": "io-fix",
  "python": "3.11",
  "tier": "fast",
  "pin_alignment": "refuse",
  "members": {
    "io": "path:../_worktrees/2026-11-18-io-partial-targets",
    "dag_ml": {"ref": "fix/standard-scale-ddof-20261118"},
    "core": {"ref": "cbef8977ec7381e96d7611602783a308f6eaa94e", "note": "PR #26"},
    "methods": {"ref": "published", "native_ref": "50b307dd2fc76c0a04ff06e83c316d408c19fc68"}
  }
}
```

- A member is `published` unless listed. `ref` is a 40-hex commit, a branch or
  tag (resolved once and recorded), or `path:<dir>` (a working tree, including
  uncommitted files; relative to the manifest). `source` optionally names the
  repository to read commits from; the default is the sibling checkout, then
  GitHub. Sources are read with `git ls-tree`/`git cat-file` and copied into
  the build root, so member checkouts are never modified.
- Published Methods still provides the native library to Rust consumers:
  `native_ref` names its runtime commit (default: the cohort Core's
  `compat/upstreams.toml`). Methods Python wheels are not built from source;
  a Methods source ref must say `"python": "published"` explicitly.
- `pin_alignment`: Cargo's `[patch]` applies only when the cohort version
  satisfies the consumer's requirement. With `refuse` (default) the run stops
  and lists every requirement that would make Cargo silently keep the registry
  version. With `align`, those requirements are rewritten to the cohort version
  in the build root only and reported; a release plan then refuses until the
  consumers commit those pin updates. After every Cargo gate the consumer's
  lockfile is checked: a cohort crate still resolved from crates.io fails the
  gate with `PATCH IGNORED`.

## Local loop

```bash
cd nirs4all-ecosystem
# Everything published except the IO working tree you are editing:
python3 scripts/n4a_cohort.py run --set io=path:../_worktrees/my-io-fix --set core=path:../_worktrees/my-core
# A reviewed cohort:
python3 scripts/n4a_cohort.py run --manifest docs/contracts/release/cohort/acceptance-20261118.n4a.json
# Start a manifest from sibling working trees:
python3 scripts/n4a_cohort.py init --out /tmp/cohort.json --from-siblings io core
python3 scripts/n4a_cohort.py summary            # reprint the latest summary
```

Everything lands in one build root (`--build-root`, `N4A_COHORT_BUILD_ROOT`,
default `<workspace>/_cohort-build`): `src/<repository>` snapshots laid out like
the workspace (with this runner as `src/nirs4all-ecosystem`, so member tooling
that looks for sibling checkouts finds the cohort, never other working trees), one
`.cargo/config.toml` holding the generated `[patch.crates-io]`, one shared
`target/` (dev profile with line tables only), `wheels/`, a uv cache, one
CPython 3.11 environment `env/` and `runs/<id>/` with `report.json` and a log
per step. The tool stops a large build when less than 15 GB is free
(`N4A_COHORT_MIN_FREE_GB`). Delete the build root to reclaim the space.

Steps:

1. Sources: only files whose content changed are rewritten, so Cargo and the
   wheel builds recompile only what changed.
2. Pins: requirement check, patch generation, optional alignment.
3. Native: `cmake --preset dev-release --target n4m_c` for libn4m, then an ABI
   check against the n4m crate in the graph and Studio's
   `scripts/native-runtime-contract.cjs`.
4. Wheels: `uv build --wheel` of each cohort Python project with its declared
   backend (maturin builds see the patch set); rebuilt only when the member, an
   upstream member or the patch set changed.
5. Environment: `uv` installs the cohort wheels by direct-file override (a
   cohort member never comes from PyPI), the SDK's declared test cohort with its
   CPU torch, and third-party packages from PyPI. Installed chain versions and
   any Python requirement that refuses a cohort version are reported.
6. Gates, in chain order: owner Rust suites, DAG-ML Python binding tests, Core
   Rust tests and wheel check, the SDK pull-request pytest selection, Studio
   sidecar tests and build, then one Studio end-to-end run (cohort sidecar,
   cohort environment, staged document adapters: import a three-target dataset
   with missing values, train one target to completion). `--tier full` adds
   the SDK nightly shards (with the cohort's `dag-ml-cli` and installed SDK, as
   `tests-full.yml` provides them; they need DAG-ML as a source member). A gate whose inputs are unchanged since it last
   passed is reported `CACHED`; `--no-cache` reruns it, `--only`/`--skip` pick
   gates, `--stop-after pins|native|wheels|env` stops before the gates.

## Reading the summary

One block per layer in chain order: the tested commit, then every step with
`PASS`, `FAIL`, `BLOCK` (a prerequisite failed), `CACHED` or `SKIP`, its
duration and a one-line result (the pytest or `cargo test` summary). Pytest
`XPASS(strict)`/`FAILED` lines and ignored patches are listed under their gate.
The last line names the **first broken layer**. Per-step logs are under
`runs/<id>/logs/`.

## Hosted run

Dispatch **Candidate cohort** (`candidate-cohort.yml`) with a manifest path
and/or one ref per member. It runs the same command on `ubuntu-latest`,
fetching every member from GitHub (only pushed commits can be tested; `path:`
refs are refused), uploads the report, logs and the release plan, and writes
the summary to the job page. The token is read-only and no step tags,
publishes or deploys. A pull request that changes the runner, its workflow or
the cohort contracts runs it on `docs/contracts/release/cohort/hosted-check.n4a.json`. Windows and macOS legs are not wired: they need the
Methods presets `ci-windows-msvc-release`/`ci-macos-clang-release` in the
native step, `Scripts\python.exe` and `.exe` paths, and a process-group-free
shutdown in the Studio driver.

## Release plan

```bash
python3 scripts/n4a_cohort.py release-plan --report <build-root>/latest-report.json
```

For each source member, in chain order: the tested commit, version and tag,
the workflows that tag (or, for the SDK, the published GitHub release) fires,
the registry packages to wait for and their current state, then the consumer
pin updates that follow. It is **blocked** when the run did not pass, when pins
were aligned, when a version is already published (bump, then re-test), when a
tag exists on another commit, when a member was tested from a dirty tree, or
when the tested commit is not on the default branch.

`--execute --confirm <first 16 hex of the manifest digest>` is for the
maintainer only: it requires `GH_TOKEN` for the `GBeurier` account, creates
each tag (or GitHub release) on the tested commit only, then waits until every
package of that member is on its registry before the next member. Rerunning it
skips tags that already point at the tested commit and refuses any other.

## Known limits

- Web vendors published npm bytes pinned by hash; testing cohort WASM there
  needs a Web owner capability. Datasets, Formats and DAG-ML-Data are
  buildable members, but Methods Python wheels are not built from source.
- The Studio end-to-end run uses the dev-profile sidecar binary, not a packaged
  Electron application.
