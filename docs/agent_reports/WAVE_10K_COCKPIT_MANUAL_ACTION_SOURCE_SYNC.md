# Wave 10K - Cockpit manual-action source sync

## Scope

- Synchronized `nirs4all-cockpit` source declarations with the already resolved
  public snapshot state for R-universe core and methods rebuild actions.
- Updated inert coordination tags to the latest existing RC coordination tags:
  `nirs4all-core` to `rc15`, `dag-ml` and `dag-ml-data` to `rc12`.
- Regenerated `data/manual-actions.json` from the current committed
  `data/current.json`.
- Repinned the ecosystem `nirs4all-cockpit` gitlink to the pushed source-sync
  head.

## Files Modified

- `nirs4all-cockpit`: `ops/manual-actions.yaml`, `ops/targets.yaml`,
  `tests/test_targets_topology.py`, `data/manual-actions.json`.
- `nirs4all-ecosystem`: gitlink `nirs4all-cockpit` and this report.

## Tests Run

- `nirs4all-cockpit`: `n4a-cockpit admin actions --current data/current.json --json-out data/manual-actions.json`,
  `n4a-cockpit validate-targets ops/targets.yaml`, `pytest -q`,
  `python3 scripts/smoke_dashboard_dom.py`, `git diff --check`.
- `nirs4all-ecosystem`: release surface matrix and gitmodule/submodule topology
  tests before integration.

## Decisions

- Kept `runiverse-formats-rebuild` and `runiverse-dagml-data-rebuild` as `todo`
  because the committed snapshot still reports those packages stale on
  R-universe.
- Did not regenerate `data/current.json`; the live local collect command had
  previously hung on external endpoints, and no partial snapshot was written.

## Risks

- The public cockpit snapshot is still only as fresh as its last successful
  collect run. The source and manual-action JSON are now internally consistent
  with that snapshot.
