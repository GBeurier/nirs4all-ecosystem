# Release Distribution Matrix

The bounded, machine-readable surface matrix records current owner and product
source accounting for `2026.11-owner-cohort`, independently of publication and
operation/platform qualification:

`docs/contracts/release/public-v1-surface-matrix.n4a.json`

The aggregate release-member intent and exact selected lock are tracked in:

- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`

CI materializes the active lock-selected commits and validates them against the
manifest, surface matrix and evidence-bound native ledger. Parent gitlinks remain
source references; runtime dependency artifacts are selected by each owner's
manifests and exact pins. In particular, Core 0.5.0 retains Rust IO 0.3.1 even when
the parent references the IO 0.3.2 source, and its pinned Methods runtime source
remains distinct from a later Methods source/test successor.

Core's R binding is retired; the R product lives in `nirs4all-r`. Source-supported
operations do not imply numerical parity or every host route. The native ledger's
current executed claim is limited to the named Windows Rust synthetic storage
write fixture. Other source operations and unsupported storage prediction remain
explicitly distinct; no full Python/R/WASM support statement follows.

The exact previous manifest, lock, matrix and native ledger are preserved under
`docs/contracts/release/history/2026.07-refactor/`. They are provenance, not active
defaults. The WAVE 10O audit dated 8 July 2026 and the October README snapshot retain
their own evidence scope and are not a November qualification.

The release-lock tool's checkout, fetchability-audit, and full-validation
commands first bind the lock to the exact canonical digest of the supplied
manifest, require the manifest and lock member sets and paths to match, and
require full 40-character Git commit identities. Changes to that envelope fail
before any clone or checkout. Full lock validation against the selected member
workspace is still required to attest that each commit SHA is the intended one.

Validate it with:

```bash
python3 scripts/n4a_release_surface_matrix.py validate
```

This pointer exists because some orchestration prompts and control boards refer
to `nirs4all-ecosystem/docs/RELEASE_DISTRIBUTION_MATRIX.md`. Do not point it at
workspace-local scratch files. Update the tracked public surface matrix and
release contracts first, then replace this pointer with a generated matrix when
the topology is finalized.
