# Wave 5M - Cluster GitGuardian follow-up

Date: 2026-07-04

## Scope

- Follow up the GitGuardian alert reported for `GBeurier/nirs4all-cluster`.
- Audit without printing token values.
- Harden the repo against future Generic CLI Option Secret examples.

## Audit

- Loaded local token files for comparison without printing values:
  - `cratesio_token`;
  - `github_token`;
  - `goatcounter_token`;
  - `npm_token`;
  - `rtd_token`;
  - `sentryio_token`;
  - `zenodo_token`.
- Scanned all local `nirs4all-cluster` commits for those exact token values: no hits.
- Scanned the current tracked tree for CLI-option style secret patterns: no hits.
- Confirmed prior remediation commits already existed on July 2-3 for token-shaped docs/examples.

## Changes Integrated

- `GBeurier/nirs4all-cluster`:
  - commit `a0571e6` extends `scripts/secret_shape_guard.py` to reject long literal `--token` examples and literal `N4CLUSTER_TOKEN=...` examples;
  - commit `53d689c` updates the guard tests so their synthetic secrets are assembled at runtime and do not trip repository-wide static scanning;
  - new `tests/test_secret_shape_guard.py` covers placeholders/variables, literal CLI token rejection, literal env token rejection, and value redaction in guard diagnostics.

## Verified Checks

- `python3 scripts/secret_shape_guard.py` -> pass.
- `git ls-files -z | xargs -0 uvx --from detect-secrets detect-secrets-hook --baseline .secrets.baseline` -> pass.
- `ruff check .` -> pass.
- `MYPYPATH=. mypy nirs4all_cluster` -> pass.
- `PYTHONPATH=. pytest -q` -> `150 passed`, `1 skipped`, `1 deselected`.
- GitHub `version-guard` on `53d689c` -> success.
- GitHub `CI` on `53d689c` -> success, including `secret scan`, docs, build, and Python 3.11/3.12/3.13 tests.

## Risk Notes

- If GitGuardian identified a token value that is not one of the seven local token files, it still needs provider-side rotation/revocation by the owner.
- The repo-side guard now blocks the documented CLI-option shape from reappearing in tracked files, but it cannot purge historical GitHub/GitGuardian records.
