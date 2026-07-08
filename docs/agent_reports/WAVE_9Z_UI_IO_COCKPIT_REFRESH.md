# WAVE 9Z - UI 0.1.8, IO Web Head, Cockpit Refresh

## Scope

Integrate the now-pushed `nirs4all-ui` and `nirs4all-io` work into the
ecosystem pins, publish the UI package/release, and refresh the cockpit status
after the core/methods registries caught up.

## Modified Files

- `nirs4all-ui`: bumped package metadata to `0.1.8`, tagged `v0.1.8`, published
  npm, and created the GitHub Release so the cockpit latest-release check is
  green.
- `nirs4all-io`: no registry bump; the new Dataset Builder web/demo head
  `9de9b42` is pinned in ecosystem after CI/parity/cross-binding checks passed.
- `nirs4all-cockpit`: refreshed `data/current.json` and
  `data/manual-actions.json`; status is now `96 green`, `1 stale`, `4 pending`,
  `1 excluded`.
- `nirs4all-ecosystem`: advanced `nirs4all-ui`, `nirs4all-io`, and
  `nirs4all-cockpit` submodules; regenerated the aggregation lock for the IO
  member commit.

## Tests And Gates

- `nirs4all-ui`: `npm run ci` with Node 24; includes TypeScript, 113 Vitest
  tests, build, dry-pack, and React 18/19 packed-consumer smoke.
- `nirs4all-ui@90cf1d6`: GitHub CI, Pages, and release-npm are green.
- `nirs4all-io@9de9b42`: GitHub CI, Python/R/WASM bindings, parity oracle,
  cross-binding parity, version-sync, and version-guard are green.
- `nirs4all-cockpit`: `python3.11 -m pytest -q`; dashboard DOM smoke; targets
  validation.
- `nirs4all-ecosystem`: release lock generated, validated, and fetchability
  audited (`7/7`); release-lock/topology/surface/e2e tests passed.

## Decisions

- The IO change is a web/demo component integration after `v0.1.9`, not a
  runtime/API registry release. It is pinned by commit in the ecosystem lock.
- UI needed a real `v0.1.8` GitHub Release in addition to npm publication,
  because the cockpit tracks both npm and latest GitHub Release.
- Full parity remains deferred until a larger batch; this wave used local UI
  gates plus CI-backed IO/methods/core parity and binding checks.

## Risks / Follow-Up

- The only stale cockpit target is `nirs4all-datasets` on CRAN
  (`0.2.0` visible while `0.3.5` is expected). Remaining pending targets are
  manual CRAN submissions: `n4m`, `pls4all`, `nirs4allio`, and core `nirs4all`.
- `nirs4all-cockpit@173d742` GitHub CI/Pages were still running when this
  report was written; local cockpit gates were green.
