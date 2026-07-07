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

## Published RC14 Prereleases

Tag: `n4a-v1-rc14-2026.07-refactor`

- `nirs4all-ui`: `210217f62cd58975b1372fd8a097a5b1d915667d`
- `nirs4all-web`: `964b8f5a014726c26719fedd2c54d905b6c464fd`
- `nirs4all-org`: `01a401a6bbb6d7d084321fcfcb9b42a1551bca25`
- `nirs4all-cockpit`: `f8d033fbf7a92707d6af9a78ccddded2c873e697`
- `nirs4all-core`: `e31a24825fd369810e2b66f6425df457cb38e8d6`
- `nirs4all-providers`: `bb85204b00f572e0254bd0b5acbc528dab262b1c`
- `nirs4all-ecosystem`: `d72c1cb98518e70167caa2efec47b13ac286116b`

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
- RC14 supersedes RC13 for coordination purposes because it includes the fixed
  core/providers workflow filters and the final ecosystem submodule repin.
- PyPI Trusted Publisher blockers remain unresolved external actions; workflow
  filters must not hide those missing package publications in the cockpit.

## Tests

- `nirs4all-core`: YAML syntax validation for `.github/workflows/ci.yml`.
- `nirs4all-providers`: YAML syntax validation for
  `.github/workflows/publish.yml`.
- `nirs4all-ecosystem`: release surface validation, E2E scenario validation,
  E2E coverage, release-lock fetchability audit, and `git diff --check`.
- GitHub Actions after the filter fixes:
  - `nirs4all-core` main `CI` and `version-guard` passed on `e31a248`.
  - `nirs4all-providers` main `Providers CI` and `Pages` passed on `bb85204`.
  - `nirs4all-providers` RC14 `Publish to PyPI` was skipped as intended.
  - `nirs4all-ecosystem` main `version-guard` and Cross-language E2E scenarios
    passed on `d72c1cb`.

## Risks

- RC13 core/providers prereleases remain published but are superseded by RC14.
- The PyPI package surfaces still require Trusted Publisher setup or deliberate
  token-based publication; RC prerelease filtering does not publish them.
