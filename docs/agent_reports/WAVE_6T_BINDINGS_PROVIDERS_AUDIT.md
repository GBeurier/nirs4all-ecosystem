# Wave 6T - Bindings And Providers Audit

Date: 2026-07-06

## Scope

- Repos: `nirs4all-core`, `nirs4all-providers`, `nirs4all-datasets`, `nirs4all-io`,
  `nirs4all-formats`, `nirs4all-methods`
- Mode: read-only audit

## Naming State

- Python full library keeps the public `nirs4all` distribution and import.
- Python core uses `nirs4all-core` as the distribution, with compatibility imports such as
  `nirs4all_lite`, `n4a`, and `nirs4all_core`.
- R core package is `nirs4all`.
- WASM core package is npm `nirs4all`.
- Rust core crate is `nirs4all`.
- MATLAB/Octave namespace is `+nirs4all`.

This matches the requested rule: core publications are named `nirs4all` where the Python full
package does not already own that name.

## Providers Role

`nirs4all-providers` is a Python-only, dependency-light, read/discovery client. It soft-imports
optional backing packages and must not become the universal runtime layer. R/WASM/Rust should consume
portable provider contracts, indexes, and component bindings directly rather than importing
`nirs4all_providers`.

## Incoherences To Fix

- WASM component package names are not fully aligned with what `nirs4all-core` imports. Core expects
  scoped names such as `@nirs4all/formats-wasm`, `@nirs4all/io-wasm`, and
  `@nirs4all/datasets-wasm`, while some component packages still publish or stage older names.
- `nirs4all-core[methods]` appears incomplete because the Python runner can import
  `pls4all.sklearn.PLSRegression`, while the extra currently covers `nirs4all-methods`.
- `compat/upstreams.toml` still mentions candidates that do not match the generated package/import
  surface cleanly.
- `nirs4all-io` still documents copied tabular logic from full `nirs4all`.
- `nirs4all-datasets` has a local ECOSTRESS Rust recipe that is an explicit exception to the
  datasets/no-IO boundary.
- `nirs4all-io` has two Python packaging surfaces with the same `nirs4all-io` name; publication
  ownership needs to be explicit.

## Decision

Keep providers outside core runtime. Fix package naming and extras through targeted release train
changes instead of moving provider logic into R/WASM/Rust bindings.
