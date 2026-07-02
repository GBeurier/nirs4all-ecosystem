# Wave 4E - Web client-only, UI surface, IO/R datasets bridge, lock refresh

Date: 2026-07-02  
Coordinator: Codex

## Scope

Follow-up to Wave 4D. This batch integrates two parallel agent outputs plus
local review/fixes. Full Python parity was not rerun; this is still reserved for
a larger integration batch.

## Published code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all-web` | `rc/v1-full-refactor` | `c722233` / `n4a-v1-rc1-2026.07-refactor` | `studio-lite/src/app/client-side-only.test.ts` |
| `nirs4all-io` | `rc/v1-full-refactor` | `c064ecf` / `n4a-v1-rc1-2026.07-refactor` | C ABI, R binding/docs/smoke, ABI snapshots |
| `nirs4all-datasets` | `rc/v1-full-refactor` | `d9cbd995` / `n4a-v1-rc1-2026.07-refactor` | `bindings/r/nirs4alldatasets/tests/smoke.R` |
| `nirs4all-ecosystem` | `rc/v1-full-refactor` | this report commit | surface matrix, release lock, release-surface tests, this report |

## Changes

- Web client-only contract now rejects remote runtime `<link>` resources such as
  `stylesheet`, `preconnect`, `dns-prefetch`, `preload`, and `modulepreload`.
  SEO/document metadata such as canonical, sitemap, OpenGraph, Twitter image,
  JSON-LD, and noscript anchors remain allowed because they are not runtime
  resource loads.
- `nirs4all-ui` is now accounted for in the public V1 surface matrix as a
  shared React/TypeScript component and view-model package outside the
  aggregation lock.
- `nirs4all-io` exposes a bytes-free assembled summary path to R:
  `n4io_load_summary()` at C/R JSON level and `nio_load()` at the idiomatic R
  level. The C ABI version moved from `0.1.0` to `0.2.0`.
- `nirs4all-datasets` R smoke now builds an offline mini catalog/cache, resolves
  and verifies it through `n4ds_*`, then calls `nirs4allio::nio_load()` on a
  generated `DatasetSpec`.
- The aggregation lock was regenerated after selecting the new locked heads:
  `io=c064ecf9f301f5ec60af996299eaf4c42db0b1e8` and
  `datasets=d9cbd995a2e990d7a9481b02c8f8a59ece9d5d8b`.

## Agent reports

| Agent | Ownership | Outcome |
| --- | --- | --- |
| Codex worker | `nirs4all-ecosystem` release surface matrix | Added `nirs4all.ui.package` and tests. Integrated after validation. |
| Codex worker | `nirs4all-io` + `nirs4all-datasets` R bridge | Added R IO load summary and datasets→IO smoke. Integrated after ABI review and Rust gates. |

## Tests and gates

Web:

- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run test -- src/app/client-side-only.test.ts` -> `2 passed`.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run typecheck` -> clean.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run build` -> passed; Vite still reports expected large WASM chunks and browser-compatible externalization for staged `n4m.js`.

IO:

- `cargo fmt --all --check` -> clean.
- `cargo clippy --workspace --all-targets -- -D warnings` -> clean.
- `cargo test --workspace` -> passed.
- `cargo build --workspace --no-default-features` -> passed.
- `cargo test -p nirs4all-io-capi` after the version-script comment fix -> `18 passed` across ABI tests and surface snapshots.
- `git diff --check` -> clean.

Datasets:

- `git diff --check` -> clean.
- Offline SHA-256 constants in the R smoke were checked against the generated
  fixture bytes.
- R smokes were not run locally because `R`/`Rscript` are not installed in this
  environment.

Ecosystem:

- `python3 scripts/n4a_release_surface_matrix.py validate` -> valid.
- `python3 -m pytest tests/test_release_surface_matrix.py -q` -> `6 passed`.
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees generate ...` -> regenerated lock.
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> valid.
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable` -> `7/7 member commits checked out`.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all` -> manifest/readiness OK.
- `python3 -m pytest tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -q` -> `20 passed`.

## Risks and decisions

- `nirs4all-ui` is intentionally outside the aggregation lock. It is now
  visible in the public surface matrix, but it is not pinned by the lock until
  the release process decides to include UI package publication as a locked
  reproducible member.
- R now has a no-array materialization summary, not full array/SpectroDataset
  parity. That is deliberate for this ABI slice; array/table handles remain
  deferred.
- The datasets R smoke skips if `nirs4allio` or `jsonlite` is unavailable. That
  is acceptable for local environments without R, but release CI must install
  both packages and execute the smoke before claiming R datasets parity.
- Full Python parity remains pending for the next larger batch.
