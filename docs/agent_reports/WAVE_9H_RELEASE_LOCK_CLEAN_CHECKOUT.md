# WAVE 9H - Release lock clean checkout

## Scope

- Lane A: release-lock validation after multisource vector parity promotion.
- Repository: `nirs4all-ecosystem`.

## Files modified

- `docs/contracts/release/aggregation-lock.n4a.lock.json`

## Changes

- Regenerated the aggregation lock from the pinned clean checkout workspace instead of the live sibling workspace.
- Removed the accidental `members.io.state.dirty=true` capture caused by concurrent local `nirs4all-io` work that is outside this lane.

## Tests run

- `python3.11 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-release-external validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable`

## Decisions

- Kept the lock evidence tied to selected member commits and clean reproducible checkouts.
- Did not touch the concurrent `nirs4all-io` workspace changes.

## Risks

- Full parity was not rerun for this lock-only correction.
