# Wave 8A — Core/Providers Packaging Architecture Audit

Date: 2026-07-07

## Scope

- Audited only `nirs4all-core` and `nirs4all-providers`.
- Did not touch `nirs4all-ui`, `nirs4all-quality`, `nirs4all-drafts`, `nirs4all-lab`, `nirs4all-cockpit`, or `nirs4all-org`.
- Added this report in `nirs4all-ecosystem/docs/agent_reports/` because the audit resulted in wording changes.

## Findings

- `nirs4all-core` already described the Python rename and the aggregate boundary well, but the release-facing docs did not say plainly enough that the non-Python publications named `nirs4all` are still bindings of the same `nirs4all-core` aggregate rather than separate host-language implementations.
- `nirs4all-providers` already described itself as a soft-import client layer, but it did not state explicitly enough that it is not a second `nirs4all` runtime and that cross-language `nirs4all` packages should consume `nirs4all-core` / `nirs4all-methods`, using only the neutral provider contracts when they need datasets or repository read access.

## Changes

- `nirs4all-core`
  - Updated `README.md` to call the repo the portable aggregate publication, and to state that Rust/npm/R/MATLAB artifacts named `nirs4all` are release identities for that same aggregate.
  - Updated `docs/PUBLISHING.md` to require release notes and packaging language to describe the non-Python `nirs4all` artifacts as aggregate bindings over shared upstream packages and `nirs4all-methods`.
  - Updated `docs/RELEASE.md` to restate that those `nirs4all` artifacts are delegating target-language releases, not reimplementations.
- `nirs4all-providers`
  - Updated `README.md` to state explicitly that the package is not a second full Python `nirs4all` implementation.
  - Added explicit architecture wording that non-Python clients should port the neutral provider contracts and plug them into their own target-language `nirs4all` / `nirs4all-methods` stacks.
  - Updated `pyproject.toml` description to reflect that this is a Python soft-import client package, not a runtime substitute.

## Checks

- `nirs4all-core`
  - Parsed `bindings/python/pyproject.toml`, `bindings/rust/nirs4all/Cargo.toml`, and `bindings/wasm/package.json` successfully with local metadata checks.
- `nirs4all-providers`
  - Parsed `pyproject.toml` successfully with a local metadata check.
  - Ran `PYTHONPATH=src pytest -q tests/test_repository_health.py tests/test_version_sync.py` -> passed.

## Decisions

- Kept edits narrowly in release/packaging docs and package metadata wording. No code, version, dependency, or workflow behavior changed.
- Left binding implementation files untouched because the architectural behavior was already consistent; the gap was in release-facing wording.

## Risks

- This was a docs/metadata audit only. I did not run broader conformance, parity, or multi-language build/publish workflows.
