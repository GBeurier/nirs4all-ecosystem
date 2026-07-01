# Wave 2N Controller And Binding Surfaces

Date: 2026-07-01T13:37:15+02:00

## Scope

Follow-up batch after W2M. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

## Starting State

- W2M integrated `dag-ml` binding-facing controller manifest derivation through
  `a428926cf8b4`.
- W2M integrated an opt-in `n4m` SNV route in `_worktrees/INT-nirs4all` through
  `06b574cf6239`.
- The selected release root validates the aggregation lock.
- Full Python-reference parity is intentionally deferred until a larger
  core/runtime/native batch.
- The public roadmap now requires `nirs4all` V1 release accounting for Python,
  R, and WASM/browser surfaces, not Python only.

## Active Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| B/H | `019f1d77-ddeb-7de2-a8fe-07a130ab5652` / Pauli | `_worktrees/INT-nirs4all` only | derive controller manifests through the public `dag_ml` helper while preserving the runtime accessor |
| E/R/WASM | `019f1d77-fc4a-72a2-81e4-e65596419e00` / Bernoulli | `nirs4all-lite` only | verify or patch Python/R/WASM release-surface gates for the aggregate |

## Review Criteria

Lane B/H must not weaken the existing kind-level manifest output. It should keep
`nirs4all.runtime.list_controller_manifests()` as the Studio-facing accessor and
must remain compatible with environments where the new `dag_ml` helper is not
importable.

Lane E/R/WASM must not add parser, methods, dataset, or orchestration logic to
`nirs4all-lite`. It may only improve release-surface visibility, tests, or docs
for Python/R/WASM aggregate bindings.

## Expected Gates

- No full parity in this batch.
- Targeted `nirs4all` runtime/manifest tests and Studio operator manifest tests.
- Targeted Python/R/WASM `nirs4all-lite` checks matching touched files.
- Release lock regeneration only if a release member commit changes.
