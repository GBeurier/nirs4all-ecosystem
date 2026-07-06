# WAVE 6M language surface matrix

Date: 2026-07-06

## Scope

This is a concise V1 release-readiness view of the public language surfaces that
matter right now. It intentionally centers the current release topology:

- `nirs4all-core` is the portable aggregate.
- `nirs4all-methods` owns the native kernels and idiomatic non-browser bindings.
- `nirs4all-io` and `nirs4all-datasets` are real multi-language repos, but their
  end-user surfaces are not equally mature across languages.
- `nirs4all-providers` is Python-only and read-slice only.
- `nirs4all` remains the full Python oracle/compatibility surface and should stay
  held back from the portable V1 story.

Status meanings:

- `Ready`: real public surface aligned with the V1 role.
- `Partial`: real public surface exists, but naming/runtime/coverage still blocks
  a clean release claim.
- `Hold`: do not position this as a V1 public release surface yet.

## Matrix

| Language | Repo | Surface | Status | Gap to V1 |
| --- | --- | --- | --- | --- |
| Python | `nirs4all-core` | Portable aggregate package (`nirs4all-core`; imports stay `nirs4all_lite` with additive `n4a` / `nirs4all_core` facades) | Partial | PyPI publisher is still blocked, and runtime is only as real as the upstream bindings installed under it. |
| JS/WASM | `nirs4all-core` | Portable aggregate package (`nirs4all`) | Partial | Aggregate exists, but it is still a portability shell over upstream packages; browser/runtime coverage is narrower than the six-domain metadata story. |
| R | `nirs4all-core` | Aggregate package (`nirs4all`) | Partial | Real package target exists, but only upstream R domains with real bindings execute; `dag_ml` is still metadata-only. |
| MATLAB/Octave | `nirs4all-core` | Aggregate namespace (`+nirs4all`) | Partial | Only the `methods` path is a real runtime candidate; the other domains remain metadata-only. |
| Rust | `nirs4all-core` | Aggregate crate (`nirs4all`) | Ready | Keep the claim narrow: portable aggregate crate, not proof that every upstream domain has a symmetric Rust runtime. |
| Python | `nirs4all-methods` | Idiomatic binding (`n4m`, `pls4all`, experimental `nirs4all-methods`) | Partial | Strong runtime exists, but public naming is still split across package lines and needs one release-facing recommendation. |
| R | `nirs4all-methods` | Idiomatic package (`n4m` with formula/S3 and compat wrappers) | Partial | Runtime is real, but package naming remains unresolved for public docs (`n4m` vs `nirs4allmethods`). |
| MATLAB/Octave | `nirs4all-methods` | Idiomatic `+pls4all` MEX/classdef surface | Partial | Octave is CI-gated, but MATLAB release/runtime validation remains manual. |
| JS/WASM | `nirs4all-methods` | Portable function library (`@nirs4all/methods-wasm`) | Partial | Intentional low-level surface only; idiomatic browser ergonomics are deferred to `nirs4all-core`, not methods itself. |
| Rust | `nirs4all-methods` | Binding surface | Hold | No active Rust binding: `bindings/_archive/rust` exists, but Rust is explicitly archived here. |
| Python | `nirs4all-io` | Full dataset assembly and `SpectroDataset` materialization | Ready | Python is the only surface that builds the full `SpectroDataset`; keep that asymmetry explicit in release notes. |
| R | `nirs4all-io` | Thin binding over the canonical JSON/C ABI contract | Partial | Real binding exists, but the richer Python materialization surface does not carry over 1:1. |
| MATLAB/Octave | `nirs4all-io` | Thin MEX binding | Partial | Same contract path exists, but this is not an equal replacement for the Python authoring/materialization workflow. |
| JS/WASM | `nirs4all-io` | Thin fs-free WASM binding | Partial | Good for portable assembly subsets, not for parity with the Python end-user workflow. |
| Python | `nirs4all-datasets` | Catalog + acquisition + high-level package/binding | Partial | Strongest user-facing surface today, but the repo is still pre-1.0 and the high-level API is richer in Python than elsewhere. |
| Rust | `nirs4all-datasets` | Native acquisition core | Ready | This is the clean cross-language foundation; keep it framed as acquisition/descriptor infrastructure, not as the high-level modeling surface. |
| R | `nirs4all-datasets` | Acquisition binding (`nirs4alldatasets`) | Partial | Built/tested, but consumer ergonomics still trail the Python package and depend on the neutral catalog contract. |
| JS/WASM | `nirs4all-datasets` | `@nirs4all/datasets-wasm` for metadata + small public datasets | Partial | Scope is intentionally reduced; do not over-claim full catalog parity in browser release messaging. |
| MATLAB/Octave | `nirs4all-datasets` | MEX acquisition binding | Partial | Built/tested, but this stays a lower-level access path rather than a full analyst workflow. |
| Python | `nirs4all-providers` | Soft-import provider client, read slice only | Partial | Only Python exists, publication is still pending, and the repo must stay out of the portable aggregate dependency path. |
| R | `nirs4all-providers` | Provider client | Hold | No R client package; only neutral provider schemas and future gates exist. |
| JS/WASM | `nirs4all-providers` | Provider client | Hold | No JS/WASM client package; only neutral provider schemas and future gates exist. |
| Rust | `nirs4all-providers` | Provider client | Hold | No Rust client package; only neutral provider schemas and future gates exist. |
| Python | `nirs4all` | Full library, behavioral oracle, compatibility API | Hold | Keep it stable and authoritative, but do not market it as the portable V1 release surface; it is the oracle that the portable line must match. |
| JS/WASM | `nirs4all-web` | Standalone browser app using vendored aggregate/runtime pieces | Partial | Good public app surface, but it is an application, not the canonical package surface for release topology decisions. |

## Release call

- Make `nirs4all-core` the headline cross-language V1 package family.
- Present `nirs4all-methods` as the kernel owner with idiomatic Python/R/MATLAB
  bindings and a portable JS/WASM binding; do not claim active Rust there.
- Describe `nirs4all-io` and `nirs4all-datasets` as multi-language, but uneven:
  Python remains the richest end-user surface.
- Keep `nirs4all-providers` in the Python ecosystem lane only.
- Keep `nirs4all` as the held-back Python oracle and compatibility anchor until
  the portable line is ready to claim default behavior parity.

## Notes

- I did not create `docs/LANGUAGE_SURFACE_MATRIX.md`. It does not currently
  exist, and `docs/RELEASE_DISTRIBUTION_MATRIX.md` already points away from
  duplicating canonical release inventories inside `docs/`.
- `nirs4all-ecosystem/docs/` is gitignored for most files. If this report needs
  to be committed, force-add it:

```bash
git -C /home/delete/nirs4all/nirs4all-ecosystem add -f docs/agent_reports/WAVE_6M_LANGUAGE_SURFACE_MATRIX.md
```
