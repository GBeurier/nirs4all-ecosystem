# Wave 8N - RC Tags And Prerelease Filters

Date: 2026-07-07

## Scope

- Published GitHub prerelease tags for the selected non-production V1 RC heads,
  excluding the production-held `nirs4all` Python repo and `nirs4all-studio`.
- Hardened release automation so coordination prereleases do not trigger heavy
  or destructive publish paths.
- Updated ecosystem submodule pins for the resulting core/providers workflow
  filter fixes.

## Published RC13 Prereleases

Tag: `n4a-v1-rc13-2026.07-refactor`

- `nirs4all-ui`: `210217f62cd58975b1372fd8a097a5b1d915667d`
- `nirs4all-web`: `964b8f5a014726c26719fedd2c54d905b6c464fd`
- `nirs4all-org`: `01a401a6bbb6d7d084321fcfcb9b42a1551bca25`
- `nirs4all-cockpit`: `f8d033fbf7a92707d6af9a78ccddded2c873e697`
- `nirs4all-ecosystem`: `1ed4f3367faf875731daa38d4df7519bae1e9d62`
- `nirs4all-core`: `a64c6f1a1d3ec0135cbd6ca857b26ec2d989db22`
- `nirs4all-providers`: `d7c1c6715d6b25f6cabfd9dd17f97e3df8676a05`

## Follow-up Workflow Fixes

- `nirs4all-core`: `e31a24825fd369810e2b66f6425df457cb38e8d6`
  narrows `CI` tag triggers to semantic `vX.Y.Z` tags plus main/rc branches,
  so coordination `n4a-*` tags do not start the full parity-heavy CI.
- `nirs4all-providers`: `bb85204b00f572e0254bd0b5acbc528dab262b1c`
  skips the PyPI release build and publish jobs for GitHub prereleases.

## Decisions

- RC coordination tags are GitHub prereleases, not package-registry releases.
- The cancelled `nirs4all-core` RC13 tag CI and `nirs4all-providers` RC13 PyPI
  publish runs were intentional containment after discovering overly broad
  triggers.
- PyPI Trusted Publisher blockers remain unresolved external actions; workflow
  filters must not hide those missing package publications in the cockpit.

## Tests

- `nirs4all-core`: YAML syntax validation for `.github/workflows/ci.yml`.
- `nirs4all-providers`: YAML syntax validation for
  `.github/workflows/publish.yml`.
- `nirs4all-ecosystem`: release surface validation, E2E scenario validation,
  E2E coverage, release-lock fetchability audit, and `git diff --check`.

## Risks

- RC13 core/providers prereleases point to the heads before the workflow filter
  fixes; the ecosystem pin intentionally advances to the fixed heads.
- A later RC14 coordination tag should be cut after the fixed core/providers
  heads and ecosystem repin are validated.
