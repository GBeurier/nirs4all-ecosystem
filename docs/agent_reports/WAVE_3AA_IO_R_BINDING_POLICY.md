# Wave 3AA - IO R Binding Loading Policy

Date: 2026-07-01

## Scope

Lane E/G public-surface tranche focused on `_worktrees/INT-io`: add R binding smoke coverage that preserves native loading controls (`params.na` and `params.format.columns`) through the current `nio_*` spec-marshalling surface. No full parity was run.

## Commit

- `_worktrees/INT-io` `7e90b4d` - `test(io): cover loading policy in r binding`

## Files Modified

`_worktrees/INT-io`:

- `bindings/r/tests/smoke.R`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Helmholtz the 2nd | W3AA review | go | Confirmed the smoke is appropriate for the current R surface: R has no load/assemble API yet, but `nio_to_spec` / `nio_validate` must preserve loading policy fields used by Python/WASM/native paths. |

## Decisions

- Kept the R gate at spec-marshalling level because the current package exports `n4io_to_spec`, `n4io_infer`, `n4io_validate` and idiomatic `nio_*`, not `load` / `assemble`.
- Mutated a plain list produced from `nio_to_spec(c(xcsv, ycsv))` so the test exercises a fresh JSON roundtrip instead of relying on a stale `.json` attribute from an S3 object.
- Checked both global `params.na` and per-source `params.na` / `params.format.columns`.
- Kept the test corpus-free so it remains compatible with the existing CRAN-safe smoke path.

## Tests Run

`_worktrees/INT-io`:

- `git diff --check` -> passed.
- `Rscript --version` -> failed, `Rscript` not installed.
- `R --version` -> failed, `R` not installed.

Reviewer also ran:

- Static read-only review of the R binding, C ABI, native API and Python reference spec implementation -> GO.

## Risks / Follow-Ups

- The smoke was not executed locally because the environment does not provide R/Rscript.
- This checks preservation of loading controls through the public R spec surface, not materialization behavior. A real R `load` / `assemble` gate remains a future follow-up if that API is added.
- Public `nirs4all` R/Python/WASM surfaces are now all explicitly represented in the W3Y/W3Z/W3AA public-surface gates.
