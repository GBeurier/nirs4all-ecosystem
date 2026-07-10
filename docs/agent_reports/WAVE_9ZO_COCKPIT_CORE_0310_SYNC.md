# WAVE 9ZO - Cockpit core 0.3.10 sync

Date: 2026-07-10

## Scope

- Repo: `nirs4all-cockpit`
- Lane: release topology/cockpit
- Change: updated cockpit release tracking after `nirs4all-core v0.3.10`.

## Decisions

- `nirs4all-core` PyPI, npm, crates.io, GitHub Release, and Read the Docs are
  tracked as green `0.3.10` targets.
- `nirs4all-core` R-universe is now explicit manual follow-up because the
  live `r-universe/gbeurier` mirror still points to `nirs4all-core v0.3.9`,
  and this runner lacks permission to merge or dispatch that repository.
- Prepared fork branch:
  `GBeurier:gbeurier/update-nirs4all-core-0.3.10`, updating the R-universe
  `nirs4all` gitlink to `cc06b45862230a6d70a7c92a2cf7fa16020fa13c`.

## Tests and validation

- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_targets_topology.py tests/test_reconcile.py tests/test_collect_parsing.py`
- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m cockpit.cli validate-targets ops/targets.yaml`
- GitHub Actions `nirs4all-cockpit`:
  - `ci` success on `89ac7ff`
  - `version-guard` success on `89ac7ff`
  - `collect` success, producing `564bccb`
  - `pages` success on `564bccb`

## Public cockpit evidence

- `https://cockpit.nirs4all.org/data/current.json`
- Summary after collect:
  `96 green, 0 stale, 0 pending, 0 missing, 0 broken, 0 unknown, 1 excluded`.
- `nirs4all-core` rollup is green at manifest/tag `0.3.10`.

## Risks

- R-universe `nirs4all` remains manual until the prepared fork branch is merged
  into `r-universe/gbeurier` and the universe rebuild completes.
