# Wave 4DA - Topology and E2E Audit Follow-up

Date: 2026-07-04

## Inputs

- Codex topology audit: remaining visible `nirs4all-lite` / `nirs4all-core`
  inconsistencies across root docs, cockpit, org, providers, and core comments.
- Codex E2E audit: the 10 cross-language scenarios exist, but several scenario
  titles/evidence labels overclaimed the proof actually executed by current
  tests.

## Integrated fixes

| Repo | Commit | Scope |
| --- | --- | --- |
| `nirs4all-cockpit` | `6af0a24` | Align package inventory and CRAN tarball fetcher with `nirs4all-core` GitHub releases. |
| `nirs4all-org` | `098f3df` | Demote `nirs4all-lite` from first-level nav/download UI to compatibility-alias text under `nirs4all-core`. |
| `nirs4all-providers` | `3b625ce` | Remove stale `nirs4all-lite` dependency-boundary wording. |
| `nirs4all-core` | `f6b1574` | Align version-sync script comments with `nirs4all-core`. |
| `nirs4all-ecosystem` | this batch | Pin those heads and make E2E semantic gaps explicit in the manifest/tests. |

Root workspace files `CLAUDE.md` and `RELEASE_DISTRIBUTION_INVENTORY.md` were
also updated locally because `/home/delete/nirs4all` is a sibling-checkout
workspace, not a normal release repository.

## E2E contract changes

- `e2e-python-reopen-paper-repository-refit` is now `hybrid`, not `strict`:
  reopen/rerun parity remains strict, but the papers/repository step currently
  emits a best-refit handoff descriptor with `executed=false`; it does not yet
  execute a repository best-pipeline refit.
- `e2e-wasm-open-repo-pipeline-alt-dataset` now declares both missing pieces:
  no Python-vs-WASM numeric oracle, and no alternative catalog dataset execution.
- `e2e-multimodal-python-r-wasm-roundtrip` is now `hybrid`: current parity is a
  dense fused-matrix proxy, not native multimodal runtime plus Web/Studio
  roundtrip.
- `tests/test_e2e_scenarios.py` now asserts those known semantic gaps directly
  so the manifest cannot silently regress to overclaiming strict proof.

## Checks

- `nirs4all-cockpit`: `python3.11 -m pytest -q` -> `93 passed`.
- `nirs4all-cockpit`: `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
  -> `OK: ops/targets.yaml - 21 packages, 99 targets`.
- `nirs4all-cockpit`: `python3.11 -m ruff check .` -> `All checks passed`.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py validate` ->
  `OK: 10 cross-language E2E scenarios`.
- `nirs4all-ecosystem`: `pytest -q tests/test_e2e_scenarios.py` -> `29 passed`.
- `git diff --check` passed for touched repos.

## Remaining implementation gaps

- Execute a real repository best-pipeline refit instead of only exporting the
  handoff descriptor.
- Add Web/WASM execution on an alternative catalog dataset and compare against a
  Python oracle.
- Replace the multimodal dense-proxy evidence with native multimodal runtime
  parity and a Web/Studio roundtrip step.
- Add vector-level native prediction parity for multisource once
  `predictions.parquet` persists arrays per sample.
