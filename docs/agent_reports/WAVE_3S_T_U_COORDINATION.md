# Wave 3S/3T/3U - Coordination Board

Date: 2026-07-01

## Batch Scope

This batch keeps full parity deferred. It targets three independent lanes:

- `W3S` / Lane F: `nirs4all-methods` binding parity and ABI/cross-binding audit.
- `W3T` / Lane G: `nirs4all-formats`, `nirs4all-datasets`, and `_worktrees/INT-io` bridge freshness audit.
- `W3U` / Lane D: `nirs4all-tools` converter/golden gap, with implementation allowed only for a bounded safety/test gap.

## Current State

| Repo | State Before Batch | Notes |
| --- | --- | --- |
| `nirs4all-methods` | `main`, ahead 4, behind 1 | Audit first; do not merge remote metadata delta during this batch. |
| `nirs4all-formats` | `main`, behind 1 | Audit first; no remote merge without review. |
| `nirs4all-datasets` | `main`, ahead 4, behind 1 | Audit first; current W3K bridge remains integrated locally. |
| `_worktrees/INT-io` | `refactor/integration-io` | Authoritative IO integration checkout for W3K. |
| `nirs4all-tools` | `main`, clean | Implementation allowed only for bounded converter/golden safety gaps. |

## Agent Board

| Wave | Agent | Ownership | Status | Output |
| --- | --- | --- | --- | --- |
| W3S | Peirce the 2nd | methods binding parity/cross-binding audit | read-only | No patch. ABI/catalog checks passed; remaining gap is documenting/codifying that JS/WASM is covered by npm, not the cross-binding parity harness. |
| W3T | Epicurus the 2nd | formats/datasets/IO bridge freshness audit | read-only | No patch. Formats/datasets are fresh enough for their owned boundaries; the safe next patch is IO-owned native Parquet loading in `_worktrees/INT-io`. |
| W3U | Zeno the 2nd | tools converter/golden gap | integrated | Commit `b34eb21`; `verify` now checks preserved opaque payload ledger/checksum coverage. |
| W3U | Franklin the 2nd | tools review | fixed | Found a blocker where removing `preserved_opaque` could neutralize the new check; fixed before report integration. |

## Gates Policy

- Do not run full Python-reference parity or global native parity in this batch.
- Treat behind-origin repos as audit-first; no merge/fetch/push or patch based on stale assumptions.
- If `nirs4all-tools` changes, run its targeted pytest/ruff/mypy gate and do not weaken strict failure behavior.
- Preserve architecture boundaries: methods owns kernels, formats owns parsers, IO owns assembly, datasets owns catalog, tools owns migration/conversion.
