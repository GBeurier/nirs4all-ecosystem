# Wave 9ZW - Patient test monitoring

## Scope

- Repo: `nirs4all-ecosystem`
- Lane: release/readiness orchestration
- Goal addressed: long parity/e2e/release jobs must not be cut by default; stop local monitoring only on obvious failure or obvious stale state.

## Changes

- Added `scripts/monitor_github_run.py`, a read-only GitHub Actions monitor.
- Added `tests/test_monitor_github_run.py` for the monitor decision policy.

## Policy encoded

- Default local wait budget: 6 hours.
- Default poll interval: 120 seconds.
- Default stale threshold: 2 hours without GitHub `updatedAt` movement.
- The script never cancels a GitHub run.
- It exits early only when:
  - the run is terminal;
  - a job is terminal and failed;
  - the run is in progress but stale beyond the configured long threshold;
  - the local wait budget is exceeded.

## Validation

- `python3.11 -m pytest -q tests/test_monitor_github_run.py tests/test_held_transition_readiness.py`
  - Result: `6 passed in 0.01s`
- `python3.11 scripts/monitor_github_run.py --repo GBeurier/nirs4all-ecosystem --run-id 29146667441 --once`
  - Result: detected completed success run.
- `git diff --check`
  - Result: passed.

## Risks

- The monitor depends on `gh run view --json ...`; if GitHub changes field names or `gh` auth is missing, it exits with a local error and does not mutate remote state.
- It is intentionally conservative: slow but healthy jobs continue until terminal completion or the long stale/global budget is reached.
