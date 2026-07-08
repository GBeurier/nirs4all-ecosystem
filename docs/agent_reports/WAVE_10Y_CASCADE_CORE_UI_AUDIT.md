# WAVE 10Y — Cascade Core/UI/Providers Audit

Date: 2026-07-09

## Scope

- Read-only Claude audit of the lite-to-core cascade, `nirs4all-ui` package consumption, `nirs4all-providers`, `nirs4all-org`, and cockpit descriptions.
- No files were modified by the auditor.

## Key Findings

- `nirs4all-core` live naming is clean:
  - Python distribution: `nirs4all-core`.
  - Python imports: `nirs4all_core` and `n4a`.
  - Non-Python packages publish as `nirs4all`.
  - RTD slug and repository URLs point to `nirs4all-core`.
- No live `pyproject`, `Cargo.toml`, `package.json`, CI, or RTD references to `nirs4all-lite` were found outside deliberate history/guard tests.
- `nirs4all-providers` is compliant with the intended role: stdlib-only core, soft-import optional clients, no reverse dependency shipped from other packages.
- `nirs4all-ui` had a real bootstrap risk: consumers import `dist/*`, but `dist/` is ignored and there was no `prepare` script to build it on fresh local installs.
- Follow-up implemented in `nirs4all-ui` commit `a12ae9d fix(package): build dist for local consumers`: `prepare` now runs the existing build lifecycle, and duplicate `prepack` build was removed.
- `nirs4all-ui` source boundary is clean: no fetch/router/storage/WebSocket/global runtime coupling in `src/`.
- `nirs4all-ui` gallery is live, but currently lists some lab/quality components rather than rendering them with sample data.
- `nirs4all-org` is mostly current, but has doc/asset drift:
  - Providers version mismatch between pages.
  - `assets/logos_ecosystem/logo_lite.png` remains unreferenced.
  - License messaging differs between rendered/public policy and repository metadata.
- `nirs4all-studio/package.json` still uses the old package name `nirs4all-webapp`; this remains a held-studio cleanup item, not part of the current non-prod release train.
- Cockpit topology descriptions match the current core/ui/providers/web state and guard against reintroducing a `nirs4all-lite` target.

## Priority Follow-Up

1. Keep the web vendored UI sync gate enforced.
2. Move `nirs4all-studio` package-name cleanup into the held Studio RC lane.
3. Refresh `nirs4all-org` provider version and remove the stale lite logo asset when touching org branding next.
4. Decide whether live `pls4all` dependencies in `nirs4all-core` are intentional compatibility or should be scheduled for retirement.
5. Render quality/lab components with sample data in the `nirs4all-ui` gallery without modifying the quality-owned component APIs.

## Risk

- Fresh clone/package install reliability for `nirs4all-ui` consumers is improved by the `prepare` hook, validated by `npm run build`, `npm test`, and `npm run pack:smoke`.
- No parity or runtime behavior was changed by this audit.
