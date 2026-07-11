# Wave 9ZZ - Cockpit Manual Actions Alignment

Date: 2026-07-11

## Scope

- Repository: `nirs4all-cockpit`
- Commit: `67d6215f5a14ac3598c69ac834e7c6cb5b098b39`
- Change: marked `runiverse-datasets-rebuild` as `done` in the source manual-action ledger after the cockpit auto-check had already verified `r-universe:nirs4alldatasets` green at `0.3.8`.

## Files Modified

- `ops/manual-actions.yaml`
- `data/manual-actions.json`
- `tests/test_targets_topology.py`

## Validation

- Local: `python3.11 -m pytest -q tests/test_targets_topology.py` -> `32 passed`
- Local: `python3.11 -m pytest -q` -> `146 passed`
- GitHub `nirs4all-cockpit/main@67d6215`:
  - `ci` run `29148118616` -> success
  - `pages` run `29148118603` -> success
  - `version-guard` run `29148118606` -> success

## Decisions

- No old worktree or superseded branch was merged.
- The remaining cockpit manual actions are intentionally manual: Studio Windows RC smoke and CRAN web submissions.
- Long GitHub jobs are monitored with patient polling; they are not cancelled unless failure or stale state is explicit.

## Risks

- CRAN submissions and native Windows smoke evidence remain outside automation by design.
