# Wave 9D — no legacy alias releases

Date: 2026-07-08

## Scope

- Removed active release wording around legacy `nirs4all-lite` aliases and the retired `list_pipelines` compatibility surface.
- Published/validated patch releases for the canonical V1 RC aggregate and repository provider API.
- Refreshed cockpit and ecosystem locks after publication.

## Files / repos touched

- `nirs4all-core`: published `v0.3.1`; canonical aggregate packages are `nirs4all-core` on PyPI and `nirs4all` on crates.io/npm/GitHub/R tarball surfaces.
- `nirs4all-repository`: published `v0.1.8`; public API remains `get_pipeline_list`, `get_pipeline`, `get_bundle`; no `list_pipelines` alias.
- `nirs4all-providers`: kept published `v0.2.8`; provider clients consume neutral repository/dataset contracts without reintroducing the old alias.
- `nirs4all-cockpit`: refreshed release inventory, manual actions and public snapshot for core `0.3.1`, repository `0.1.8`, providers `0.2.8`, tools `0.0.4`.
- `nirs4all-ecosystem`: repinned submodules and aggregation lock to the current release heads.

## Tests / gates run

- `nirs4all-core`: `scripts/bump_version.sh --check`; Python release/cross-language unittests; `cargo test --workspace`; WASM `npm test`.
- `nirs4all-repository`: `python3.11 -m pytest -q`; `python3.11 -m ruff check .`.
- `nirs4all-cockpit`: `python3.11 -m pytest -q`; `python3.11 -m cockpit.cli validate-targets`; `python3.11 scripts/smoke_dashboard_dom.py`.
- `nirs4all-ecosystem`: release-lock generation and targeted lock/topology/e2e tests before this report; full validation is rerun after this submodule repin.

## Review notes

- Claude Code read-only audit confirmed no release-blocking legacy alias remains in the active release surfaces.
- `list_pipelines` is intentionally absent and guarded in repository tests/contracts.
- Historical changelog entries and negative tests mentioning `nirs4all-lite` remain factual guards, not active compatibility.

## Remaining risks / decisions

- R-universe still reports `nirs4all` `0.3.0` while the `0.3.1` R tarball is on the GitHub Release; cockpit tracks this as a stale manual rebuild, not a PyPI blocker.
- CRAN targets remain manual/pending by policy.
- Old `rc/v1-full-refactor*` and superseded refactor branches are branch-hygiene debt only; they were not merged without audit.
