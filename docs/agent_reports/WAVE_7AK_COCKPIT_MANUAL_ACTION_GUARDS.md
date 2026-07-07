# WAVE 7AK - Cockpit manual-action guards

Date: 2026-07-07

Scope:
- `nirs4all-cockpit` implementation/docs.
- `nirs4all-ecosystem` report only.
- `nirs4all-ui`, `nirs4all-quality`, `nirs4all-drafts`, and `nirs4all-lab` untouched.

Changes:
- Added a `n4a-cockpit collect --only` guard so partial package collection cannot overwrite the public `data/current.json`. Partial collection must now write to an explicit scratch `--out` path.
- Tightened CRAN manual-action auto-checks for RC R surfaces (`nirs4allio`, `nirs4alldatasets`, `nirs4all`) from `expect: published` to `expect: green`, so stale CRAN publications no longer close the action.
- Updated cockpit README and ROADMAP for RC16/core 0.2.12, `nirs4all-tools` 0.0.3, dag-ml PyPI blocker status, and scratch-only partial collects.

Review:
- Read-only cockpit agent found a false-positive manual action: `cran-submit-nirs4alldatasets` could be marked resolved while CRAN was stale at `0.2.0` against current datasets.
- Read-only core/providers agent initially listed a final retired-name publish
  among possible blockers. Later no-legacy-alias decisions removed that blocker:
  the current V1 RC target keeps no public `nirs4all-lite` release alias.

Tests run:
- `python -m compileall -q cockpit` -> OK.
- `ruff check .` -> OK.
- `n4a-cockpit validate-targets ops/targets.yaml` -> OK, 21 packages / 101 targets.
- `python -m pytest -q` -> 116 passed.
- `n4a-cockpit collect --only nirs4all-cockpit --offline` -> expected failure, refuses partial public snapshot.
- `n4a-cockpit collect --only nirs4all-cockpit --offline --out /tmp/n4a-cockpit-partial.json` -> OK, scratch snapshot with 1 package.

Known risks / debt:
- Full public collect was not committed in this batch; an attempted full collect was too slow locally and was interrupted without output.
- `nirs4all-cockpit/data/current.json` remains a complete snapshot from `2026-07-07T04:38:58Z`, not a refreshed snapshot after the latest ecosystem E2E hardening commit.
- Cockpit still lacks dependency/upstream cascade rollups for `nirs4all-core` and `nirs4all-web`.
- `nirs4all-ecosystem` still has internal `lite` / `lite_*` release-lock vocabulary for the core member; this remains a next non-UI cleanup candidate.
