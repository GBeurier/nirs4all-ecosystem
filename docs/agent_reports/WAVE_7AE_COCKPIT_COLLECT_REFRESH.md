# WAVE 7AE - Cockpit collect refresh

Date: 2026-07-07

## Scope

- Repositories: `nirs4all-cockpit`, `nirs4all-ecosystem`
- Lane: release/status cockpit after `nirs4all-core` `v0.2.12`
- Constraint: no changes to `nirs4all-ui` or `nirs4all-quality`

## Files modified

- `nirs4all-cockpit` submodule pointer in `nirs4all-ecosystem`
- `docs/agent_reports/WAVE_7AE_COCKPIT_COLLECT_REFRESH.md`

## Upstream cockpit refresh

- Triggered GitHub Actions workflow `collect` manually on `GBeurier/nirs4all-cockpit`
- Resulting cockpit commit: `6c234ef899c0959c4e8100acfd14dbfc5e11efee`
- Pages deploy for the collected snapshot completed successfully

## Snapshot result

- `generated_at`: `2026-07-07T02:52:31.156088+00:00`
- Summary: `green=85`, `stale=3`, `pending=4`, `missing=7`,
  `broken=0`, `unknown=0`, `excluded=1`
- `nirs4all-core` source now resolves to `v0.2.12` at
  `563d3340e4596993a6486f351256f76b7aeaebbf`

## Tests run

In `nirs4all-cockpit` after pulling the collect commit:

- `.venv/bin/python -m pytest -q`
- `.venv/bin/n4a-cockpit validate-targets ops/targets.yaml`
- `.venv/bin/ruff check .`

## Decisions

- The cockpit remains explicit about unresolved external release actions:
  PyPI Trusted Publisher setup for `nirs4all-core`, stale R-universe rebuild,
  and pending CRAN/publication actions.
- No full parity run was launched in this wave.

## Risks

- The `nirs4all-core` PyPI target is still externally blocked by PyPI trusted
  publisher configuration (`invalid-publisher` on the `v0.2.12` tag workflow).
- R-universe for `nirs4all` remains stale until the manual rebuild completes.
