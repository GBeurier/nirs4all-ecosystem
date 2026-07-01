# Wave 3X - Coordination Board

Date: 2026-07-01

## Batch Scope

This batch keeps full parity deferred and closes the W3W Parquet projection follow-up: native assembly can now avoid unsupported unselected Parquet columns when every use explicitly requests columns.

## Agent Board

| Wave | Agent | Ownership | Status | Output |
| --- | --- | --- | --- | --- |
| W3X | Mendel the 2nd | `_worktrees/INT-io` implementation | integrated | Commit `9bb4e4a`; per-path Parquet projection union and tests. |
| W3X | Lovelace the 2nd | projection design audit | done | Read-only; clarified source/variation/global effective param handling and fallback rules. |
| W3X | Chandrasekhar the 2nd | reviewer/parity audit | go | Confirmed projection union and raw/no-NA reader behavior; no blocking findings. |

## Gates Policy

- Full Python-reference parity was intentionally not run in this small batch.
- Long dag-ml/native parity gates remain reserved for a larger integrated batch.
- Architecture boundaries preserved: `io-core` stays filesystem-free, and `io` owns filesystem/Parquet decoding and projection planning.
