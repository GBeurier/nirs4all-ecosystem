# WAVE 10BF - Actions refresh and E2E strictness audit

Date: 2026-07-09T19:23:25Z

Lane: release/status hygiene plus independent audit of remaining V1 proof gaps.

## Scope

This wave continued the non-production release hygiene work by modernizing a
small central batch of GitHub Actions workflows and refreshing the public
cockpit snapshot afterward.

Production-held repositories stayed out of release scope:

- `nirs4all`
- `nirs4all-studio`

No full Python parity run was launched in this workflow-only batch.

## Repositories and commits

| Repository | Commit | Notes |
| --- | --- | --- |
| `dag-ml` | `366ca8b ci(actions): modernize dag-ml workflows` | Updated checkout/setup/artifact actions and release npm Node runtime. |
| `dag-ml-data` | `4aaef0a ci(actions): modernize dag-ml-data workflows` | Same action refresh pattern as `dag-ml`. |
| `nirs4all-providers` | `d771c0d ci(actions): modernize providers workflows` | Updated CI, Pages, publish, and version guard actions. |
| `nirs4all-cockpit` | `1a0f235 ci(actions): modernize cockpit workflows` | Updated CI, collect, Pages, and version guard actions. |
| `nirs4all-cockpit` | `2a60801 chore(collect): refresh data/current.json` | GitHub collect refresh after the workflow updates. |
| `nirs4all-cockpit` | `7cfaf49 fix(dashboard): hide release channels from public snapshot` | Removed public `channel` metadata and cache-busted the dashboard assets so old `rc` / `production-held` capsules cannot reappear. |
| `nirs4all-cockpit` | `0497dbf feat(targets): track device pages surface` | Added `nirs4all-device` as a Pages-only public app surface. |
| `nirs4all-ecosystem` | this report commit | Added `nirs4all-device` as a public submodule and documented the inventory/audit decision. |
| `nirs4all-ecosystem` | this follow-up commit | Updated standard `actions/checkout` and `actions/upload-artifact` pins in cross-language, cutover, and version-guard workflows. |

## Local validation

- Workflow YAML parse: passed for the four edited repositories.
- `git diff --check`: passed for the four edited repositories.
- Selected action major pin check: passed for the four edited repositories.
- `dag-ml`: `cargo fmt --all --check`; `python3 scripts/validate_contracts.py`.
- `dag-ml-data`: `cargo fmt --all --check`; `DAG_ML_REPO=../dag-ml python3 scripts/validate_contracts.py`.
- `nirs4all-providers`: `.venv/bin/python -m pytest -q`; `.venv/bin/python scripts/ci_gate.py`.
- `nirs4all-cockpit`: `.venv/bin/python -m pytest -q`; `.venv/bin/python -m ruff check .`; `.venv/bin/python -m cockpit.cli validate-targets ops/targets.yaml`.
- `nirs4all-cockpit` dashboard cleanup: `.venv/bin/python -m pytest -q`; `.venv/bin/python -m ruff check .`; `.venv/bin/python -m cockpit.cli validate-targets ops/targets.yaml`; live `cockpit.nirs4all.org` HTML/JS/JSON checks.
- `nirs4all-cockpit` device inventory: `.venv/bin/python -m pytest tests/test_targets_topology.py -q`; `.venv/bin/python -m pytest -q`; `.venv/bin/python -m ruff check .`; `.venv/bin/python -m cockpit.cli validate-targets ops/targets.yaml`.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py validate`; `python3 -m pytest tests/test_e2e_scenarios.py -q`.
- `nirs4all-ecosystem` action refresh: workflow YAML parse; `git diff --check`;
  `python3 scripts/n4a_e2e_scenarios.py validate`; `python3 -m pytest tests/test_e2e_scenarios.py -q`.

Notes:

- An initial `python3` run failed in `nirs4all-providers` because system
  `python3` is Python 3.10 and the package requires Python 3.11+.
- An initial `python3` run failed in `nirs4all-cockpit` because the system
  environment lacked cockpit test dependencies. Re-running through the local
  `.venv` passed.

## GitHub validation

All observed workflows triggered by the pushed commits completed successfully:

| Repository | Workflows |
| --- | --- |
| `dag-ml` | CI, `version-guard`, Dependabot Actions update check |
| `dag-ml-data` | CI, `version-guard`, Dependabot Actions update check |
| `nirs4all-providers` | Providers CI, Pages, `version-guard` |
| `nirs4all-cockpit` | CI, Pages, `version-guard` |
| `nirs4all-cockpit` collect refresh | collect, Pages |
| `nirs4all-cockpit` dashboard cleanup | CI, Pages, `version-guard` |
| `nirs4all-cockpit` device inventory | pending at report-write time |

The refreshed cockpit snapshot was generated at
`2026-07-09T19:26:46.727434+00:00` with summary:

- green: 96
- stale: 1
- pending: 4
- missing: 0
- broken: 0
- unknown: 0
- excluded: 1

## Parallel audit results

Three read-only Claude Code agents were launched in parallel in the first pass.
All three completed and no audit agent changed repository files. A second pass
used three read-only Codex explorer agents for the remaining Actions, E2E, and
inventory questions.

### Release/cockpit/status hygiene

Verdict: the public release/status surface is close to clean, but a few manual
and inventory gaps remain.

Evidence found by the audit:

- The cockpit snapshot was refreshed at `2026-07-09T19:26:46.727434+00:00`
  and the public dashboard now omits both release bundles and channel capsules.
- All cockpit-tracked release workflows observed in this batch were green.
- All 10 public subdomains checked by the audit returned HTTP 200 for root,
  `robots.txt`, and `sitemap.xml`.
- GoatCounter and Sentry public aggregate signals were live; Search Console
  remained unavailable without the token.
- Registry publication gaps were manual rather than code-side: five CRAN
  submissions plus the held Studio Windows RC smoke-test action.

Main remaining gaps:

- `nirs4all` has a scheduled `Verify Examples` workflow failing repeatedly; it
  is production-held and not part of the release rollup, but it should be
  tracked or fixed before claiming the Python line is fully quiet.
- The next action-modernization batch should prioritize `nirs4all-core`,
  `nirs4all-io`, and `nirs4all-methods`; smaller drift remains in
  `nirs4all-ecosystem`, `nirs4all-quality`, and some GitHub Release actions.

Follow-up Codex inventory audit:

- `nirs4all-aom` was already correctly tracked in cockpit.
- The core/ui/providers split is consistent across cockpit README,
  `ops/targets.yaml`, and the ecosystem README.
- `nirs4all-device` was the main missing public surface: it has a Pages
  workflow, custom domain `device.nirs4all.org`, and an Android debug APK
  artifact, but was absent from the ecosystem parent and cockpit inventory.
- Decision: track `nirs4all-device` as a Pages app surface only. The Android APK
  remains a CI artifact, not a registry or production-store release target.

### Core + UI custom app host

Verdict: the current core+UI custom-app-host target is real and enforced.

Evidence found by the audit:

- `nirs4all-web` has a standalone `examples/custom-app-host` app importing
  public `nirs4all` and `nirs4all-ui` surfaces.
- `nirs4all-web` has in-repo custom-host contract tests and published-package
  smoke tooling.
- `nirs4all-ui` exposes reusable assets/styles/brand generators and a showcase
  site.
- `nirs4all-studio` consumes `nirs4all-ui`, but only partially through an
  incremental bridge.

Main remaining gaps:

- Studio still duplicates some dataset preview/view-model behavior instead of
  consuming all relevant `nirs4all-ui` exports.
- Studio needs a stronger `nirs4all-ui` drift/version gate.
- `nirs4all-ui` would benefit from an explicit dist-freshness and binary asset
  publication guard.

### Cross-language E2E strictness

Verdict: the ecosystem has 11 declared complex scenarios, but automatic CI is
mostly manifest/schema/evidence-shape validation, not automatic fresh runtime
parity execution.

Evidence found by the audit:

- The scenarios cover the requested declared surfaces: Python, R, WASM/Web,
  datasets/io, pipelines, repository, papers, saves/predictions, multimodal,
  and multisource.
- The push/PR gate runs validation, pytest, coverage, and plan paths.
- Runtime `--execute` paths are manual or local; evidence verification trusts
  JSON artifacts emitted by the scenario commands and does not recompute an
  independent numeric oracle in-process.
- Tests exercise verifier strictness with synthetic/fabricated passing payloads.

Main remaining gaps:

- Add at least one license-free real runtime execution to automatic CI.
- Add an independent in-process oracle recomputation for at least one scenario.
- Bind evidence freshness to current repo/submodule SHAs.
- Replace MATLAB string/asset checks with an Octave runtime leg where possible.
- Add a real-data/vendor-format scenario once datasets are available.

Follow-up Codex E2E audit:

- Normal push/PR CI runs `validate`, `pytest`, and `coverage`, but does not set
  `execute=true`, so scenario commands are not executed on the default path.
- `coverage` reports the current gate honestly as
  `coverage_gate=manifest_contract_only`.
- The smallest useful runtime proof is a scheduled or dispatch smoke that runs
  one representative scenario such as
  `e2e-dataset-provider-repository-roundtrip`, then verifies evidence freshness
  with `--max-age-seconds`.

### Remaining GitHub Actions drift

Verdict: workflow drift is concentrated and can be handled in bounded batches.

Follow-up Codex Actions audit:

- `nirs4all-core`: 9 remaining mutable action refs, mostly release-source,
  release-R, and release-MATLAB upload/release/SBOM actions.
- `nirs4all-io`: 14 remaining mutable refs, including Pages deploy, release
  artifact transfer, source/R/MATLAB releases, and wasm-pack.
- `nirs4all-methods`: 29 remaining mutable refs, including CI artifacts,
  parity gates, docs Pages, wheels, R/source/MATLAB/Python releases, and
  specialized toolchains.
- `nirs4all-formats`: 1 remaining mutable ref
  (`dtolnay/rust-toolchain@stable` in demo Pages).
- `nirs4all-datasets` and `nirs4all-quality`: no mutable workflow `uses:` refs
  found in the scanned workflows.
- `nirs4all-ecosystem`: 6 remaining mutable refs in `cutover-gates.yml` and
  `cross-language-e2e.yml`.

Follow-up integration:

- `actions/checkout` was moved to `v7` in `cutover-gates.yml`,
  `cross-language-e2e.yml`, and `version-guard.yml`; `actions/upload-artifact`
  was moved to `v7` in `cutover-gates.yml` and `cross-language-e2e.yml`.
- The specialized R/Rust/emsdk refs remain unchanged in this batch.

Recommended ordering:

- First batch: GitHub-owned and shared release actions in `nirs4all-core`,
  `nirs4all-io`, `nirs4all-methods`, and `nirs4all-ecosystem`.
- Second batch: specialized toolchain actions such as CUDA, codecov,
  cibuildwheel, PyPI publish, MSVC/MSYS2, wasm-pack, and Rust toolchain pins.

## Decisions

- `nirs4all-lite` and old worktrees remain excluded from canonical release
  hygiene. They are inventory/history only.
- Node 20 entries in CI compatibility matrices were left alone; only release
  npm jobs using Node 20 were moved to Node 24.
- No changes were made to `nirs4all-ui` components, preserving the concurrent
  `nirs4all-quality` work boundary.
- `nirs4all-device` is now treated as a public product surface outside the
  aggregate lock and outside package registry release tracking.

## Remaining follow-up candidates

- Modernize the larger action batches still concentrated in `nirs4all-core`,
  `nirs4all-io`, `nirs4all-methods`, `nirs4all-formats`, and
  `nirs4all-datasets`.
- Turn the E2E audit findings into actual runtime CI improvements, starting
  with a small license-free Python/WASM or Python/Node scenario.
- Keep `nirs4all-device` in cockpit/ecosystem as Pages-only unless a signed
  Android/iOS release channel is intentionally introduced.
