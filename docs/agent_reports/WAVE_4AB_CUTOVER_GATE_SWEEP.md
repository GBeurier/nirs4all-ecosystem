# Wave 4AB - Cutover Gate Sweep, UI Shim Gate, Methods Claims

Date: 2026-07-03

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Scope

This batch keeps production heads intact and moves only selected RC branches/tags.
Full Python parity was not rerun; the latest full proof remains Python
`6a2c720` with `887 passed`, `0 skipped`, `0 xfailed`, `0 failed` across the
split slow/non-slow run.

## Integrated Changes

### Studio

Commit: `fcc44c86 ci(studio): gate shared ui vendor drift`

Files modified:

- `.github/actions/nirs4all-ui-sibling/action.yml`
- `.github/workflows/ci.yml`
- `package.json`
- `vendor/nirs4all-ui/dist/**`

Decisions:

- Studio CI now fails on vendored `nirs4all-ui` drift through
  `NIRS4ALL_UI_SHIM_REQUIRED=1 npm run check:ui-shim`.
- `npm run lint:parallel` now includes the UI shim gate.
- The sibling action builds `nirs4all-ui` before comparison so `dist` is
  available on clean CI runners.
- Generated `vendor/nirs4all-ui/dist` is tracked deliberately, matching the
  clean-runner requirement already enforced in Web.

Tests:

- `NIRS4ALL_UI_SHIM_REQUIRED=1 npm run check:ui-shim` -> PASS
- `npm run lint:parallel` -> PASS
- `git diff --cached --check` -> PASS

### Methods

Commit: `64731c6d ci(methods): run parity gates on rc branches`

Files modified:

- `.github/workflows/cross-binding-parity.yml`
- `.github/workflows/parity-gate.yml`

Decisions:

- Methods parity workflows now run on `rc/**` branches as well as `main`.
- The aggregation manifest now requires `methods_cross_binding_parity`.
- The Methods R availability claim is `subset`, not `full`, because the current
  R binding is a real package with tests but not a complete C ABI surface.

Tests:

- `git diff --check` -> PASS

### Ecosystem

Files modified:

- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/agent_reports/RC_V1_FULL_REFACTOR_CONTROL.md`
- `docs/agent_reports/WAVE_4AB_CUTOVER_GATE_SWEEP.md`

Decisions:

- Lock now pins Methods `64731c6d` and marks Methods R availability as
  `subset`.
- `methods_cross_binding_parity` is part of the release required-gates list.
- Full cutover gate sweep was run after the Wave 4AA repairs, excluding only
  `pyref_oracle_full` because the user asked to reserve full parity for large
  batches.

Tests:

- `python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --skip pyref_oracle_full --json` -> PASS
- `python3 scripts/n4a_release_surface_matrix.py validate` -> PASS
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> PASS
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all` -> PASS
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -p no:cacheprovider` -> `22 passed`
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable` -> `7/7`

## Agent Reports

### Claude Code - Language Surface Audit

Session: `ca6b8f17-ecbd-4735-ade1-254ed2ef3961`

Files modified: none.

Result:

- Python plus native C ABI/Rust core are the strongest RC surfaces.
- Rust aggregate is credible but still depends on publication/pin freshness.
- WASM has real topology and CI evidence, but local non-strict tests can pass
  without methods-backed numeric execution.
- R and MATLAB/Octave must remain preview/partial language surfaces until R and
  Octave gates execute on final heads.
- Providers should remain described as Python client plus neutral schemas, not
  cross-language provider clients.

Coordinator action:

- Accepted the over-declaration finding for Methods R and changed the lock from
  `r: "full"` to `r: "subset"`.
- Added the missing RC trigger for Methods cross-binding workflows and required
  `methods_cross_binding_parity` in the aggregation manifest.

### Claude Code - Studio/Web UI Shim Audit

Session: `77ed4d18-c4ea-4e16-a1d8-e4c732b8ebfe`

Files modified: none by the agent; coordinator implemented the reviewed fix.

Result:

- Web already gates client-only, UI shim, core shim, typecheck, build, and smoke
  paths.
- Studio had a `check:ui-shim` script but did not run it in CI or
  `lint:parallel`.
- Studio's sibling action did not build `nirs4all-ui`, so clean CI comparison
  could miss `dist`.

Coordinator action:

- Integrated the Studio CI/lint/action fix and tracked the vendored UI `dist`.

### GitGuardian Follow-Up

Alert received by user:

- Repository: `GBeurier/nirs4all-cluster`
- Secret type: Generic CLI Option Secret
- Pushed date: 2026-07-02 09:41:03 UTC

Audit:

- `git fetch origin --tags --prune` removed stale local PR refs.
- Visible remote refs are now `origin/main` and `origin/rc/v1-full-refactor`.
- Active published refs remain clean for concrete CLI-option secret values:
  `main` `16b4a2a`, `rc/v1-full-refactor` `19384e2`, tag
  `n4a-v1-rc1-2026.07-refactor` `19384e2`.
- Current docs still contain placeholder syntax such as `NAME:TOKEN:ROLES`;
  targeted scans found no `--token value` or `--principal value:value:roles`
  on active published refs.

Decision:

- Treat the alert as stale/remediated placeholder exposure unless GitGuardian
  discloses a non-placeholder secret value. No rotation is indicated from the
  accessible evidence.

## Publication

- `nirs4all-methods` branch `rc/v1-full-refactor` and tag
  `n4a-v1-rc1-2026.07-refactor` were moved to `64731c6d`.
- `nirs4all-studio` branch `rc/v1-full-refactor` and tag
  `n4a-v1-rc1-2026.07-refactor` were moved to `fcc44c86`.
- `nirs4all-ecosystem` will publish this report plus the refreshed aggregation
  manifest/lock after final validation.

## Remaining Risks

- R/Rscript and Octave are still unavailable in this local environment, so R and
  MATLAB/Octave remain CI/toolchain gates rather than local proof.
- Full Python parity was intentionally not rerun in this batch.
- GitHub Actions for the newly pushed Studio/Methods heads should be monitored
  after publication.
