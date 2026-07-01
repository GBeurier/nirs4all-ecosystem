# Wave 3P/3Q/3R - Coordination Board

Date: 2026-07-01

## Batch Scope

This batch keeps full parity deferred until a larger integrated run. It targets three independent lanes with disjoint ownership:

- `W3P` / Lane E: `nirs4all-lite` public V1 Python/R/WASM surface gate.
- `W3Q` / Lane I: `nirs4all-cluster` targeted release/e2e proof gap.
- `W3R` / Lane J: `nirs4all-repository`, `nirs4all-benchmarks`, and `nirs4all-papers` provider/plugin/export audit.

Private repositories `nirs4all-drafts` and `nirs4all-lab` remain out of scope.

## Current State

| Repo | State Before Batch | Notes |
| --- | --- | --- |
| `nirs4all-lite` | `main`, ahead 12 | Public `nirs4all` Python/R/WASM accounting is present; R execution may be toolchain-dependent. |
| `nirs4all-cluster` | `main`, ahead 13 | Unit/API coverage exists; remaining gap is a release/e2e proof that respects the runner-only `nirs4all` import invariant. |
| `nirs4all-repository` | `main`, behind 1 | Audit only; do not merge remote state without separate review. |
| `nirs4all-benchmarks` | `main`, behind 1 | Audit only; benchmarks must consume/test pipelines without writing into the ecosystem. |
| `nirs4all-papers` | `main`, behind 1 | Audit only; public archive/export surface, not drafts or private materials. |

## Agent Board

| Wave | Agent | Ownership | Status | Output |
| --- | --- | --- | --- | --- |
| W3P | Feynman | `nirs4all-lite` public Python/R/WASM surface gate | integrated | Commit `786688d`; Python and WASM public `nirs4all` surfaces are required by `make test-v1-surfaces`; R remains risk/skip only when the runtime is unavailable. |
| W3Q | Locke | `nirs4all-cluster` release proof gap | integrated | Commit `7628433`; installed wheel/CLI/server/worker smoke added as an opt-in release test. |
| W3R | Dirac the 2nd | repo/benchmarks/papers audit | read-only | No patch. All three repos are clean but behind origin by one metadata commit; recommended next patch is a benchmarks-only optional repository recipe consumer after base refresh. |
| W3P/W3Q | Hume the 2nd / Sartre the 2nd | Mandatory reviews | fixed | Both initial reviews found blocking issues; fixes were applied and commits amended before report integration. |

## Gates Policy

- Do not run full Python-reference parity during this small batch.
- If a public surface changes, run the closest binding smoke/gate for that surface.
- Missing R or external browser/toolchain execution is recorded as risk, not as a green proof.
- Release-lock regeneration is not part of this batch unless a locked member commit is intentionally changed and reviewed.

## Integration Checklist

- [x] Review W3P diff and tests before integrating.
- [x] Review W3Q diff and tests before integrating.
- [x] Convert W3R audit into a concrete next action or leave read-only.
- [x] Add per-wave reports with files, tests, risks, decisions.
- [x] Re-run targeted gates after integration.
