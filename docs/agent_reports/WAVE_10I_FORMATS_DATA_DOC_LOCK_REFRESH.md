# Wave 10I - Formats / dag-ml-data docs and R lock refresh

## Scope

- Follow-up after the `nirs4all-formats v0.2.6` and `dag-ml-data v0.2.8`
  publications.
- Removed stale active version references in `nirs4all-formats` docs and
  citation metadata.
- Refreshed the `dag-ml-data` R binding `Cargo.lock` from `0.2.5` to `0.2.8`.
- Repinned the ecosystem gitlinks for `nirs4all-formats` and `dag-ml-data` to
  the pushed source-fix heads.
- Read-only UI/Web/Studio audit confirmed `nirs4all-ui` exposes styles, assets,
  brand generation, and the GitHub Pages showcase; `nirs4all-web` remains
  client-side only at runtime.

## Files Modified

- `nirs4all-formats`: `CITATION.cff`, `README.md`, `docs/STATUS.md`,
  `docs/installation.md`, `docs/bindings/wasm.md`,
  `docs/dev/release_process.md`, and maintenance docs front matter for strict
  Sphinx builds.
- `dag-ml-data`: `docs/STATUS.md`,
  `crates/dag-ml-data-r/src/rust/Cargo.lock`.
- `nirs4all`: `pyproject.toml`, `CHANGELOG.md` wording only on
  `refactor/L17-pyref`; no Python production release.
- `nirs4all-ecosystem`: gitlinks `nirs4all-formats`, `dag-ml-data`, this report,
  and the agent-report ignore exception for Wave 10 reports.

## Tests Run

- `nirs4all-formats`: `./scripts/bump_version.sh --check`,
  `sphinx-build -W -b html docs docs/_build/html`, `git diff --check`.
- `dag-ml-data`: `python3.11 scripts/validate_release_metadata.py`,
  `python3.11 scripts/release/check_publish_plan.py --dry-run`,
  `cargo fmt --all --check`, `cargo test --workspace`,
  `cargo run -p dag-ml-data-cli -- fingerprint-schema examples/minimal_schema.json`,
  `DAG_ML_REPO=../dag-ml python3.11 scripts/validate_contracts.py`,
  `git diff --check`.
- `nirs4all-ui`: `nvm use 24`, `npm run ci`, `npm run site:build`.
- `nirs4all`: `python3.11` TOML parse for `pyproject.toml`, `git diff --check`.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_release_surface_matrix.py validate`,
  `python3.11 -m pytest -q tests/test_gitmodules_topology.py tests/test_submodule_repin_plan.py tests/test_release_surface_matrix.py tests/test_release_lock.py`,
  selected-root lock validation with
  `scripts/n4a_release_lock.py checkout-members ...` followed by
  `scripts/n4a_release_lock.py --workspace-root <selected-root> validate ...`,
  `git diff --check`.

## Decisions

- Did not tag new `nirs4all-formats` or `dag-ml-data` releases: the changes are
  docs/source-lock hygiene after already published registry versions, not runtime
  or package API changes.
- Did not release `nirs4all` Python production. The branch-only wording fix keeps
  the no-legacy-alias decision aligned without changing production state.
- Kept the aggregation release lock pinned to release artifacts; these gitlink
  repins are source/doc visibility updates and do not redefine the lock.
- Direct release-lock validation against `/home/delete/nirs4all` still reports
  live-workspace drift by design; selected-root validation is the authoritative
  evidence for the unchanged lock.

## Risks

- R-universe still needs a maintainer-triggered rebuild with write access; the
  current token only has `READ` on `r-universe/gbeurier`.
- Studio/Web still consume `nirs4all-ui` partially; the shared package is ready,
  but further app-level component migration remains separate work.
