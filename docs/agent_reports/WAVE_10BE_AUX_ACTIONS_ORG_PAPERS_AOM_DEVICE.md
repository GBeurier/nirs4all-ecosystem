# WAVE 10BE - Auxiliary Actions modernization

Date: 2026-07-09T19:09:58Z

Lane: release/status hygiene for auxiliary public surfaces.

## Scope

This batch modernized GitHub Actions usage for four auxiliary top-level
repositories without changing runtime, package, or application logic.

Production-held repositories stayed out of scope:

- `nirs4all`
- `nirs4all-studio`

The shared UI package also stayed out of this batch to avoid interfering with
the concurrent `nirs4all-quality` work.

## Repositories and commits

| Repository | Commit | Files |
| --- | --- | --- |
| `nirs4all-org` | `0db2b02 ci(actions): modernize org version guard` | `.github/workflows/version-guard.yml` |
| `nirs4all-papers` | `d1e14f6 ci(actions): modernize papers workflows` | `.github/workflows/ci.yml`, `.github/workflows/content-check.yml`, `.github/workflows/publish.yml`, `.github/workflows/site.yml`, `.github/workflows/version-guard.yml` |
| `nirs4all-aom` | `533e13f ci(actions): modernize aom workflows` | `.github/workflows/publish-pypi.yml`, `.github/workflows/version-guard.yml` |
| `nirs4all-device` | `103defc ci(actions): modernize device workflows` | `.github/workflows/android.yml`, `.github/workflows/ci.yml`, `.github/workflows/pages.yml` |

## Local validation

- Batch workflow scan: no remaining old action references in the selected repos.
- `git diff --check`: clean for all four repositories.
- Workflow YAML parse: clean for all four repositories.
- `nirs4all-org`: workflow pin assertion passed.
- `nirs4all-papers`: `python3 -m pytest -q` -> 50 passed, 2 skipped.
- `nirs4all-aom`: `python3 -m build` and `python3 -m twine check dist/*` passed.
- `nirs4all-device`: `npm test -- --run` -> 22 passed; `npm run typecheck` passed; `npm run build` passed.

Notes:

- `nirs4all-aom` emitted setuptools license-table deprecation warnings only.
- `nirs4all-device` emitted existing Vite browser-externalization warnings only.
- No full Python parity run was triggered in this small workflow-only batch.

## GitHub status

All workflows triggered by the pushed commits completed successfully:

- `nirs4all-org`: `version-guard`, Pages, dependency update check.
- `nirs4all-papers`: CI, Pages, content check, `version-guard`, dependency update check.
- `nirs4all-aom`: `version-guard`.
- `nirs4all-device`: CI, Pages, Android APK.

## Decisions

- Worktrees, nested checkouts, and `_selected` copies were treated as non-canonical
  inventory and were not edited.
- Core/data/runtime release workflow modernization remains for separate batches.
- Manual/external blockers remain outside this batch: Studio Windows RC smoke,
  CRAN submission work, Google Search Console credentials, and Studio Sentry
  project cleanup.
