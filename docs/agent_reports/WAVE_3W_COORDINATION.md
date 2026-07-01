# Wave 3W - Coordination Board

Date: 2026-07-01

## Batch Scope

This batch keeps full parity deferred and closes the W3V follow-up: Rust IO now applies the Python MVP NA policy for native CSV/Parquet materialization paths.

## Agent Board

| Wave | Agent | Ownership | Status | Output |
| --- | --- | --- | --- | --- |
| W3W | Euclid the 2nd | `_worktrees/INT-io` implementation seed | integrated | Commit `789c3e5`; native NA policy skeleton and Parquet raw/public split. |
| W3W | Aristotle the 2nd | Python MVP oracle audit | done | Read-only; documented `apply_na_policy` behavior and required Rust insertion points. |
| W3W | Huygens the 2nd | reviewer/parity audit | go | Confirmed policy parity and Parquet source-param ordering; no blocking findings. |

## Gates Policy

- Full Python-reference parity was intentionally not run in this small batch.
- Long dag-ml/native parity gates remain reserved for a larger integrated batch.
- Public `nirs4all` R/Python/WASM surfaces remain explicit final-gate scope via W3P; this batch changes IO internals and native materialization behavior only.
- Architecture boundaries preserved: `io-core` stays filesystem-free, `io` owns filesystem/Parquet decoding, and source-effective loading params are applied in the shared core before role split.
