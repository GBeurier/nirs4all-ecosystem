# Wave 4AV - Main Promotion Except Python And Studio

Date: 2026-07-03

## Scope

Promoted the V1 RC train to `main` for every public repository except the two
production-sensitive surfaces:

- `nirs4all`: Python production remains on its previous `main`; the RC remains
  available on `rc/v1-full-refactor` and the RC tag for manual parity review.
- `nirs4all-studio`: production `main` remains unchanged; a Windows RC
  installer was built and attached to the RC prerelease for local manual tests.

## Published Heads

The promoted repositories have `main`, `rc/v1-full-refactor`, and
`n4a-v1-rc1-2026.07-refactor` aligned. The final post-gate correction moved
`dag-ml` to `7c4946ef` to fix release CI:

- `dag-ml`: `7c4946ef`
- `nirs4all-datasets`: `6f55834d`
- `nirs4all-formats`: `181946f1`
- `nirs4all-io`: `bce32efb`
- `nirs4all-benchmarks`, `nirs4all-cluster`, `nirs4all-cockpit`,
  `dag-ml-data`, `nirs4all-methods`, `nirs4all-lite`, `nirs4all-org`,
  `nirs4all-papers`, `nirs4all-providers`, `nirs4all-repository`,
  `nirs4all-tools`, `nirs4all-ui`, and `nirs4all-web` were already aligned by
  the main-promotion pass.

## Files Modified

- `docs/contracts/release/aggregation-lock.n4a.lock.json`: refreshed to the
  promoted heads for `dag-ml`, `nirs4all-datasets`, `nirs4all-formats`, and
  `nirs4all-io`.
- `docs/agent_reports/WAVE_4AV_MAIN_PROMOTION_EXCEPT_PYTHON_STUDIO.md`: this
  coordination record.

## Validation

Ecosystem gates:

- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all`

`dag-ml` post-gate correction:

- `sphinx-build -W --keep-going -b html docs docs/_build/html`
- `cargo audit --deny warnings`
- `cargo fmt --all --check`
- `cargo test --workspace`

## Decisions

- No full Python parity rerun was launched for this publication batch; it stays
  reserved for the larger Python/Studio validation window because it is long.
- MATLAB remains unvalidated by the maintainer; Octave/R/native/WASM gates stay
  the practical proof surfaces.
- `nirs4all-datasets` is promoted with the known temporary gap of 7 absent
  catalog datasets pending the Dataverse collection.
- `web.nirs4all.org` is still a client-side-only Studio-lite surface. It uses
  shared components from `nirs4all-ui`, but it is not a full export of the
  Studio desktop/frontend application.

## Risks

- `nirs4all` Python and `nirs4all-studio` remain RC-held by design. Their
  production switch still requires manual validation, full parity, and Studio
  workflow testing.
- Two Pages deployments (`nirs4all-benchmarks`, `nirs4all-papers`) previously
  failed at the GitHub `deploy-pages` step after artifact creation; both were
  rerun as transient infrastructure failures.
