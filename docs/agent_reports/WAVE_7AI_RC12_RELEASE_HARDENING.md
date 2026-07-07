# WAVE 7AI — RC12 release hardening

Date: 2026-07-07

## Scope

- Lane: release lock / publication fallback / cockpit-org consistency.
- Ownership: `dag-ml`, `dag-ml-data`, `nirs4all-providers`, `nirs4all-tools`, `nirs4all-org`, `nirs4all-ecosystem`.
- Explicitly out of scope: `nirs4all-ui`, `nirs4all-quality`, `nirs4all`, `nirs4all-studio`, `nirs4all-drafts`, `nirs4all-lab`.

## Files and repos modified

- `dag-ml`: hardened `.github/workflows/release-python.yml` with unique artifact labels, Trusted Publisher tuple preflight, and GitHub Release fallback attachment job.
- `dag-ml-data`: same Python release hardening as `dag-ml`.
- `nirs4all-providers`: raised setuptools build backend floor to a PEP 639-capable version.
- `nirs4all-tools`: aligned `CITATION.cff` to v0.0.3 and refreshed GitHub Release fallback assets.
- `nirs4all-org`: added `nirs4all-tools` and `nirs4all-aom` to the public NIRS tools hub.
- `nirs4all-ecosystem`: repinned `dag-ml`, `dag-ml-data`, `nirs4all-providers`, `nirs4all-tools`, `nirs4all-org`; advanced the release selection tag to `n4a-v1-rc12-2026.07-refactor`; regenerated the aggregation lock.

## Publications and tags

- Published GitHub Release fallback assets for `dag-ml` v0.2.3 and `dag-ml-data` v0.2.4 from successful CI artifacts.
- Refreshed GitHub Release fallback assets for `nirs4all-providers` v0.2.6 and `nirs4all-tools` v0.0.3.
- Tagged all aggregation-lock members with `n4a-v1-rc12-2026.07-refactor`.
- Fast-forwarded `dag-ml` and `dag-ml-data` `rc/v1-full-refactor` to the selected RC12 heads.

## Tests and checks

- `nirs4all-providers`: `pytest -q`, build, `twine check`.
- `nirs4all-tools`: `pytest -q`, build, `twine check`.
- `dag-ml` / `dag-ml-data`: wheel metadata smoke against downloaded CI artifacts; release-python dry-runs with `publish=false`.
- `nirs4all-org`: HTML parser smoke and `git diff --check`.
- `nirs4all-ecosystem`: release lock validate against a clean selected workspace, release surface matrix validate, E2E scenario manifest validate, and targeted pytest release/topology suite.
- `nirs4all-cockpit`: local target validation and offline pytest passed; GitHub `collect` workflow was triggered for a fresh public snapshot.

## Decisions

- Did not merge or clean the dirty local `_worktrees/RC-v1-dmd`; it contains staged historical work and was bypassed with a fresh selected workspace.
- Did not edit `nirs4all-ui` because another agent is actively working there for `nirs4all-quality`.
- Kept PyPI failures classified as external Trusted Publisher configuration blockers where CI builds and metadata checks are otherwise green.

## Risks / remaining actions

- PyPI Trusted Publisher must still be configured for `dag-ml`, `dag-ml-data`, `nirs4all-core`, `nirs4all-providers`, `nirs4all-tools`, and `nirs4all-benchmarks`.
- R-universe remains stale for published IO/datasets surfaces until its upstream refresh completes.
- Full Python-reference parity was not rerun in this lane; per operating constraint, it should run only after a larger code batch.
- Cockpit GitHub collect/pages completion must be repolled and, if it commits, the ecosystem cockpit submodule should be repinned.
