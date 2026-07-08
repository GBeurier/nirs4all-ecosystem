# Wave 9ZA - Formats / dag-ml-data release refresh

## Scope

- Repinned `dag-ml-data` from `v0.2.7` to `v0.2.8`.
- Repinned `nirs4all-formats` from `v0.2.5` to `v0.2.6`.
- Regenerated the aggregation lock from the canonical sibling checkouts.
- Repinned ecosystem submodules for `dag-ml-data`, `nirs4all-formats`, and `nirs4all-cockpit`.

## Files Modified

- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `tests/test_release_lock.py`
- gitlinks: `dag-ml-data`, `nirs4all-formats`, `nirs4all-cockpit`
- companion cockpit commit: `GBeurier/nirs4all-cockpit@6b2335a`

## Tests Run

- `python3 scripts/n4a_release_lock.py generate --manifest docs/contracts/release/aggregation-manifest.n4a.json --output docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 -m pytest -q`
- `git diff --check`

## Decisions

- Kept `dag-ml` pinned at `v0.2.7`; only `dag-ml-data` moved to `v0.2.8`.
- Kept R-universe rebuild actions manual because the available GitHub identity has only `READ` on `r-universe/gbeurier`.
- Kept CRAN manual actions pending/stale rather than forcing artificial green.

## Risks

- R-universe still reports `nirs4allformats 0.2.5` and `dagmldata 0.2.7` until a universe sync/rebuild runs with write access.
- CRAN statuses remain manual/pending by policy.
