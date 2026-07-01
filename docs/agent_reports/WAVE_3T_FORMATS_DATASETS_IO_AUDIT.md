# Wave 3T - Formats, Datasets, IO Bridge Audit

Date: 2026-07-01

## Scope

Lane G read-only audit of `nirs4all-formats`, `nirs4all-datasets`, and `_worktrees/INT-io` after W3K. No files were changed.

## Repository State

| Repo | State | Delta |
| --- | --- | --- |
| `nirs4all-formats` | clean, behind 1 | `86218e6 fix(demo): add crawl discovery metadata`, demo only. |
| `nirs4all-datasets` | clean, ahead 4 / behind 1 | behind `a0040275 fix(site): add canonical dataset SEO metadata`, site only. |
| `_worktrees/INT-io` | clean `refactor/integration-io` | authoritative IO integration checkout for W3K. |

No remote merge, fetch, push, or release-lock update was performed.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Epicurus the 2nd | Lane G read-only audit | done | Recommended no patch in formats/datasets; the next safe implementation belongs in `nirs4all-io`. |

## Findings

- `nirs4all-formats` owns the spectral Parquet reader, but that reader emits `SpectralRecord` and is not the right path for dataset canonical `variables.parquet` / split semantics.
- `nirs4all-datasets` already exposes the reference bridge through `NirsDataset.to_io_spec()` / `to_dataset_package()` guards.
- `_worktrees/INT-io` Python MVP can read Parquet via pandas, but the PyO3/native binding currently refuses `.parquet` with an actionable error.
- The native IO Rust loader is still CSV/bytes oriented. The safe next functional patch is IO-owned native Parquet loading, not a formats or datasets workaround.

## Tests Run

None. This was a read-only audit.

## Recommended Next Tranche

Implement in `_worktrees/INT-io`:

- Add an IO-owned native Parquet loader that converts canonical dataset tables into the IO `Frame` representation while preserving column/type semantics.
- Replace the PyO3 `.parquet` guard with a success path once the native loader is present.
- Then run `bindings/python/tests/test_idiomatic.py` and the `nirs4all-datasets` reference bridge test without skip.

## Risks / Follow-Ups

- `nirs4all-datasets[io]` still advertises `nirs4all-io>=0.1`, which is too broad for promising canonical Parquet package loading until the IO release carrying that bridge exists.
- Do not route dataset canonical Parquet through the spectral `nirs4all-formats` reader.
