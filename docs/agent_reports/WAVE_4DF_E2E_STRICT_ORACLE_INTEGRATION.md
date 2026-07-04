# Wave 4DF - E2E Strict Oracle Integration

Date: 2026-07-04

## Integrated heads

- `dag-ml@00d20c3` - rustdoc warning cleanup plus freshness gate handling for comment/doc-only Rust commits.
- `nirs4all@7edf6042` - Python paper/repository E2E ledger now records dataset hash and dimensions.
- `nirs4all-papers@5686c02` - paper handoff evidence now carries Python-backed refit proof, `force_best_refit=true`, selected pipeline id, hashes, RMSE, and prediction count.
- `nirs4all-web@a1bbcd9` - repository Web/WASM smoke now requires a Python nirs4all/sklearn oracle over browser-emitted dag-ml folds.

## Contract updates

- Added the V1 refactor phase matrix to the cross-language E2E manifest.
- Promoted Web/WASM repository fixture Python parity from gap to strict.
- Kept repository forced best-refit as `contract`: the descriptor is produced and Python-backed refit evidence is strict, but `nirs4all-repository` still has no independent runtime.

## Validation

- `python3 scripts/n4a_e2e_scenarios.py validate` -> OK, 10 scenarios.
- `python3 -m pytest -q tests/test_e2e_scenarios.py` -> 32 passed.
- `git diff --check` -> OK.
- Paired Python/papers E2E was run before integration:
  - `nirs4all` reopen/rerun parity -> 1 passed.
  - `nirs4all-papers` repository refit export -> 1 passed.
- Web repository smoke was run before integration:
  - `npm run build` -> passed.
  - `node scripts/run-smokes.mjs pipeline-repository` -> passed, Python oracle max delta `1.7763568394002505e-14`.

## Remaining risks

- Full parity was not relaunched in this wave; keep it for a larger batch.
- The Web strict oracle uses a deterministic non-demo fixture materialized through dag-ml-data, not an external catalog/dataverse dataset.
- Repository forced best-refit still needs a future independent `nirs4all-repository` runtime to move from `contract` to `strict`.
