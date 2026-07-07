# Wave 7AQ - Release documentation drift cleanup

Date: 2026-07-07

Scope:
- `dag-ml`: active release/status docs aligned from stale `0.2.0` wording to the `0.2.x` RC line and current `0.2.5` manifests.
- `dag-ml-data`: same `0.2.x` / `0.2.5` cleanup plus provider binding wording that no longer claims a currently published PyPI package when the repo only owns the PyO3 package target.
- `nirs4all-formats`: public install/status/release docs aligned to `0.2.4`, automated crates/npm/R release workflows, and R-universe lag caveat.
- `nirs4all-io`: public install/release/version docs aligned to `0.1.9`; R vendored configure template pinned to `0.1.9`.

Files changed:
- `dag-ml/README.md`
- `dag-ml/docs/{SUPPORTED.md,PERFORMANCE.md,AGGREGATION_INTEROP.md}`
- `dag-ml/docs/adr/ADR-10-release-train.md`
- `dag-ml/docs/migration-nirs4all/{README.md,WORKING_STRATEGY.md}`
- `dag-ml-data/README.md`
- `dag-ml-data/docs/{STATUS.md,ROADMAP.md,SUPPORTED.md,PERFORMANCE.md,AGGREGATION_INTEROP.md}`
- `dag-ml-data/crates/dag-ml-data-capi/bindings/python/README.md`
- `nirs4all-formats/README.md`
- `nirs4all-formats/docs/{STATUS.md,RELEASE.md,installation.md,bindings/wasm.md,dev/release_process.md,maintenance/release_checklist.md}`
- `nirs4all-io/{README.md,pyproject.toml}`
- `nirs4all-io/docs/{installation.md,VERSIONING.md,dev/release_process.md}`
- `nirs4all-io/bindings/r/configure`

Reviews:
- Codex explorer `Turing the 2nd` audited `dag-ml` / `dag-ml-data` release-doc drift.
- Codex explorer `Popper the 2nd` audited `nirs4all-formats` / `nirs4all-io` release-doc drift.

Validation:
- `dag-ml`: `git diff --check`; `python3.11 scripts/validate_release_metadata.py`; `python3.11 scripts/release/check_publish_plan.py --dry-run`.
- `dag-ml-data`: `git diff --check`; `python3.11 scripts/validate_release_metadata.py`; `python3.11 scripts/release/check_publish_plan.py --dry-run`.
- `nirs4all-formats`: `git diff --check`; `scripts/bump_version.sh --check`.
- `nirs4all-io`: `git diff --check`; `scripts/bump_version.sh --check`.

Risks:
- R-universe remains known-stale until its from-Git rebuild catches up; docs now call this out instead of presenting R-universe as exact-current.
- PyPI for `dag-ml` / `dag-ml-data` remains a configured target rather than a confirmed published package in docs that describe those bindings.
- `dag-ml/docs/STATUS.md` and `dag-ml/docs/ROADMAP.md` are `.gitignore`d local-only docs; they were inspected and adjusted on disk but are not part of the pushed commit.
- No `nirs4all-ui` or `nirs4all-quality` files were touched.
