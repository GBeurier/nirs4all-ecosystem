# Wave 10BH - Official Actions Patch Refresh

Date: 2026-07-09

## Scope

Refreshed official GitHub Actions pins on non-held repos with disjoint ownership:

- `nirs4all-core`: official action patch tags in CI/release/version workflows.
- `nirs4all-io`: official action patch tags, explicit `setup-node` cache opt-out, Cargo lock sync, Clippy compatibility fix.
- `nirs4all-methods`: official action patch tags in CI/release/docs/parity workflows.
- `nirs4all-formats`: official action patch tags, explicit `setup-node` cache opt-out, Cargo lock sync, Clippy compatibility fix.

`nirs4all` Python and `nirs4all-studio` were not touched.

## Commits

- `nirs4all-core`
  - `569ef08` `ci(actions): update official workflow actions`
  - `f37daaa` `test(release): accept pinned checkout action versions`
- `nirs4all-io`
  - `43013c2` `ci(actions): update official workflow actions`
  - `8f95a26` `fix(rust): satisfy byte delimiter clippy`
  - `684be73` `chore(release): sync cargo lock version`
- `nirs4all-methods`
  - `7149d7db` `ci(actions): update official workflow actions`
- `nirs4all-formats`
  - `b88fd55` `ci(actions): update official workflow actions`
  - `ba19c95` `fix(jcamp): satisfy clippy question-mark lint`
  - `548d049` `chore(release): sync cargo lock version`

## Validation

Local:

- Workflow YAML parse: 54 files OK.
- `git diff --check`: OK for `nirs4all-core`, `nirs4all-io`, `nirs4all-methods`, `nirs4all-formats`.
- Official-action stale/corrupt-ref scan: OK.
- `setup-node@v6.4.0` cache opt-out scan: OK.
- `nirs4all-core`: `PYTHONPATH=bindings/python/src python3 -m unittest discover -s bindings/python/tests` -> 70 tests OK, 1 existing skip.
- `nirs4all-io`: `cargo fmt --all --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace && cargo build --workspace --no-default-features` -> OK.
- `nirs4all-formats`: `cargo fmt --all --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace` -> OK.

GitHub Actions on final HEADs:

- `nirs4all-core@f37daaa`: 2/2 success.
- `nirs4all-io@684be73`: 11/11 success.
- `nirs4all-methods@7149d7db`: 11/11 success.
- `nirs4all-formats@548d049`: 3/3 success.

## Decisions

- Updated official actions to explicit patch tags instead of keeping old major aliases.
- Added `package-manager-cache: false` on every `setup-node@v6.4.0` step touched in this wave to avoid implicit npm cache behavior changes.
- Fixed new Rust stable Clippy findings in code instead of weakening gates or adding allows.
- Synced Cargo lock workspace package versions after local cargo validation exposed stale lock entries.

## Remaining Risks

- Third-party action SHA hardening remains a separate pass.
- `actionlint` was not available locally; syntax was covered by YAML parse and live GitHub Actions runs.
- Full Python parity was not launched in this wave; this was an actions/CI hygiene batch.
