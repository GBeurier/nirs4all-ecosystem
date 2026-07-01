# Wave 3V - Coordination Board

Date: 2026-07-01

## Batch Scope

This batch keeps full parity deferred and closes the W3T follow-up: IO-owned native Parquet loading for canonical datasets and pyo3 binding materialization.

## Agent Board

| Wave | Agent | Ownership | Status | Output |
| --- | --- | --- | --- | --- |
| W3V | Parfit the 2nd | `_worktrees/INT-io` implementation | integrated | Commit `734acd3`; native Parquet loader, pyo3 surface, bool cell support, zstd canonical bridge. |
| W3V | Fermat the 2nd | datasets bridge audit | done | Read-only; identified generated `canonical_dataset` as the reliable cross-repo smoke and confirmed canonical Parquet is IO-owned, not formats-owned. |
| W3V | Rawls the 2nd | reviewer/parity audit | go | Initial NO-GO for shared-input param caching; fixed and re-reviewed GO. |

## Gates Policy

- Full Python-reference parity was intentionally not run in this small batch.
- The public `nirs4all` Python/R/WASM surfaces remain covered by the existing W3P lite surface gate; this W3V lane only changes IO and the pyo3 IO binding.
- Architecture boundaries preserved: `datasets` produces canonical Parquet, `io` owns dataset assembly and Parquet tabular loading, `formats` remains for vendor/SpectralRecord parsing.
