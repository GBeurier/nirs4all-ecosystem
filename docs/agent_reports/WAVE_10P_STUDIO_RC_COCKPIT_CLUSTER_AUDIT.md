# WAVE 10P - Studio RC, Cockpit Ordering, and Cluster Security Audit

Date: 2026-07-08

## Scope

Prepare the held-back `nirs4all-studio` Windows RC path without publishing
Studio production, verify cockpit manual blockers remain at the bottom, and
audit the GitGuardian signal reported for `GBeurier/nirs4all-cluster`.

## Files Modified

- `nirs4all-studio/CLAUDE.md`
- `nirs4all-studio/README.md`
- `nirs4all-studio/docs/PUBLISHING_GUIDE.md`
- `nirs4all-studio/docs/user-guide/source/getting-started/installation.md`
- `nirs4all-ecosystem/docs/agent_reports/WAVE_10P_STUDIO_RC_COCKPIT_CLUSTER_AUDIT.md`

## Tests And Gates

- `nirs4all-studio`:
  - `bash -lc 'source "$HOME/.nvm/nvm.sh" && nvm use 24 >/dev/null && node scripts/build-local-windows-rc.cjs --help'`
  - `bash -lc 'source "$HOME/.nvm/nvm.sh" && nvm use 24 >/dev/null && npm run smoke:nirs4all-ui-package'`
  - `bash -lc 'source "$HOME/.nvm/nvm.sh" && nvm use 24 >/dev/null && npm run lint:storage'`
  - `git diff --check`
- `nirs4all-cluster`:
  - `python3 scripts/secret_shape_guard.py`
  - redacted current-tree CLI secret shape scan
  - redacted all-history CLI secret shape scan after `git fetch --all --prune --tags`
- `nirs4all-cockpit` read-only audit:
  - inspected `web/app.js`, `cockpit/manual_actions.py`, `ops/manual-actions.yaml`, and `data/manual-actions.json`
  - verified the dashboard ordering ranks `important`, then `info`, then `blocker`, so manual blockers render at the bottom.

## Decisions

- Keep Studio production held: no tag, no GitHub Release, no production
  publication was created for Studio.
- Document the local Windows RC path as the supported test path:
  `npm run release:windows-rc -- --version 1.0.0-rc.1` from a native Windows
  checkout, not WSL or a `\\wsl...` path.
- Align Studio documentation with the current packaging model:
  installers ship app/backend source and use a writable managed runtime;
  all-in-one archives embed the locked V1 CPU runtime.
- Treat `nirs4all-quality`'s previous direct source alias risk as closed:
  Quality now consumes public `nirs4all-ui/lab` and `nirs4all-ui/assets/*`
  package exports.

## Cluster Security Audit

- Current `nirs4all-cluster` HEAD passes `scripts/secret_shape_guard.py`.
- The current tracked tree has no live secret-bearing CLI option values outside
  the guard implementation and its tests.
- After fetching all refs/tags, the redacted history scan found one
  concrete-shaped CLI token occurrence, located in
  `tests/test_secret_shape_guard.py` in commit `a0571e6b`, which intentionally
  validates the guard and was committed after the reported July 2 GitGuardian
  push time.
- The local commit window around July 2, 2026 09:41:03 UTC maps to
  `1027e64 fix(cluster): requeue running-task failures through failed state`,
  which touches scheduler/API/database test code, not docs or CLI examples.

## Risks / Follow-Up

- If the GitGuardian incident references a concrete value visible only in the
  GitGuardian UI or in a superseded remote ref not fetched locally, rotate that
  credential anyway and mark the incident resolved after confirming the
  scanner's exact evidence.
- The Windows RC installer still needs to be built manually on native Windows;
  WSL can validate docs and helper parsing only.
- Studio/Web component convergence remains partial: Web and Quality consume the
  shared `nirs4all-ui` package, but Studio still has local feature components to
  factor in later waves.
