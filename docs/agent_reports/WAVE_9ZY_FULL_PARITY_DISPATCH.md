# Wave 9ZY - Full parity dispatch

## Scope

- Repos: `nirs4all`, `dag-ml`, `dag-ml-data`, `nirs4all-ecosystem`
- Lane: held transition and runtime parity validation

## GitHub validations launched

- `GBeurier/nirs4all` `Pre-Publish Check`, branch `refactor/L17-pyref`, run `29146982675`
  - Result: success
  - Head: `f6c201153b3921c0f214cd63a992beb29e10b7bc`
  - Covered: ruff, mypy, docs, build/install, examples, full pytest+coverage on Ubuntu 3.11/3.13, Windows 3.11/3.13, macOS 3.13.
- `GBeurier/dag-ml` `CI`, branch `main`, run `29146982653`
  - Result: success
- `GBeurier/dag-ml-data` `CI`, branch `main`, run `29146982510`
  - Result: success

## Ecosystem follow-up

- Refreshed `held-transition-readiness.n4a.json` so the Python transition gate points at the fresh pre-publish run `29146982675`.
- The production switch remains blocked by the manual gates only:
  - `STUDIO-WINDOWS-RC4-SMOKE`
  - `HELD-PROJECT-PUBLISH-DECISION`

## Monitoring policy

All runs were monitored with `scripts/monitor_github_run.py` using a 6-hour local wait budget, 120-second polling, and a 2-hour stale threshold. No GitHub run was cancelled.
