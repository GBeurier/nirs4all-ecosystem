# WAVE 10W - nirs4all Web Dataset Repin

Date: 2026-07-09

## Scope

Repin the `nirs4all` submodule after the full E2E dispatch exposed that
`e2e-python-reopen-paper-repository-refit` declared Web upload dataset CSVs
before the pinned Python test produced them.

## CI Evidence

- Failed run: `28981246655`
- Failed step: `Execute ready scenarios`
- First command passed: `test_reopen_rerun_parity`
- Failure cause: post-step artifact validation found missing
  `repository_X_train.csv`, `repository_y_train.csv`, and
  `repository_metadata.csv`.

## Resolution

The remote `nirs4all` refactor branch already contained
`0d0e3067 test(e2e): export repository dataset for web parity`. The ecosystem
submodule is repinned to `9cb8f98d`, which includes that producer-side fix and
keeps the manifest artifact contract intact.

## Follow-Up

Re-dispatch the full `execute=true` run after this repin lands.
