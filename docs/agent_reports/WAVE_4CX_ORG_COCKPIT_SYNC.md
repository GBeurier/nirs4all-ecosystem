# Wave 4CX - Org and Cockpit Sync

Date: 2026-07-04

## Scope

Short coordination closeout for the public org page refresh and cockpit snapshot
refresh after the V1 RC publication/cockpit blocker updates.

## Files modified

- `nirs4all-org/index.html`
  - Updated `nirs4all-formats` fallback version to `v0.2.1`.
  - Updated `nirs4all-web` fallback version to `v0.1.1`.
  - Replaced the obsolete `nirs4all-lite` GitHub release link with the legacy
    PyPI alias link for `nirs4all-lite==0.2.0`.
- `nirs4all-ecosystem/nirs4all-cockpit`
  - Advanced the submodule pointer from `757e737` to cockpit collect snapshot
    `6ec3592`.
- `nirs4all-ecosystem/nirs4all-org`
  - Advanced the submodule pointer from `ed8075a` to org page update `e4dea6b`.
  - Confirmed `nirs4all-tools` is visible on the org page with source release
    and PyPI-pending status, and aligned offline Studio/Python fallbacks.
- `nirs4all-ecosystem/README.md`
  - Aligned the referenced-project table with the actual V1 RC submodules:
    `nirs4all-core`, `nirs4all-providers`, `nirs4all-tools`, `nirs4all-ui`,
    `nirs4all-cockpit`, and the `main` Studio branch.
- Root workspace docs, not a Git repository:
  - Marked the old release inventory / lite convergence notes as historical and
    aligned them with the `nirs4all-core` V1 RC topology.

## Tests and checks

- `nirs4all-org`: `git diff --check`.
- `nirs4all-org`: GitHub `version-guard` passed on `5059439`.
- `nirs4all-cockpit`: GitHub `version-guard`, `collect`, and `pages` passed on
  the latest cockpit line, with collect producing `6ec3592`.

## Risks

- GitHub Pages deployment for `nirs4all-org` initially failed with the transient
  GitHub message `Deployment failed, try again later`; the run was rerun.
- `nirs4all-core` PyPI remains blocked by Trusted Publisher configuration, so
  public docs still describe PyPI as pending and keep the `nirs4all-lite` alias
  visible only as a legacy installation path.

## Decisions

- Do not regenerate cockpit data locally without GitHub secrets; use the CI
  collect artifact instead.
- Keep `nirs4all-lite` references only where they are explicitly marked as
  legacy compatibility during cutover.
