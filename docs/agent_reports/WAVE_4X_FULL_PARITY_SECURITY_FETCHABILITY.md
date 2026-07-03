# Wave 4X - Full Parity, Security, Fetchability Follow-Up

Date: 2026-07-03

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Scope

Wave 4X is the post-Wave 4W verification pass. It does not add product code to
the aggregate lock members; it runs the deferred full Python parity gate after
the 4W batch, closes the Core lock fetchability audit that a read-only reviewer
flagged, and refreshes the GitGuardian cluster remediation after the repeated
alert.

## Agents And Reviews

- Claude Code read-only review session `2f3bba5d-1feb-44b0-8e53-d3b04346ccdd`
  audited the published Wave 4W heads and correctly flagged that Core was not
  yet pushed to the canonical `GBeurier/nirs4all-lite` remote at the time of
  its scan.
- Codex coordinator fixed the Core publication gap by pushing `f120c281` to
  both `GBeurier/nirs4all-lite` and `GBeurier/nirs4all-core`.
- Codex coordinator handled the repeated GitGuardian cluster alert and removed
  the remaining secret-shaped `--principal alice:s3cr3t:submitter` example from
  the active cluster heads.

## Integrated Or Verified Heads

- `nirs4all` Python remains `6a2c7200`.
- Core `f120c281` is published on both:
  - `GBeurier/nirs4all-lite` `rc/v1-full-refactor-core`
  - `GBeurier/nirs4all-core` `rc/v1-full-refactor-core`
  - tag `n4a-v1-rc1-2026.07-refactor` on both remotes.
- `nirs4all-cluster`:
  - `main` -> `16b4a2a docs(security): avoid secret-shaped principal examples`
  - `rc/v1-full-refactor` -> `19384e2 docs(security): avoid secret-shaped principal examples`
  - tag `n4a-v1-rc1-2026.07-refactor` -> `19384e2`.

## Tests Run

Python full parity on current head `6a2c7200`, with
`NIRS4ALL_REQUIRE_N4M=1`, RC `dag-ml`/`dag-ml-data` on `PYTHONPATH`, and
`shap` installed in the Python oracle venv:

- Non-slow split:
  - `pytest tests/integration/parity -m "not slow" -q --tb=short -p no:cacheprovider`
  - `444 passed, 443 deselected, 510 warnings in 550.90s`
- Slow split:
  - `pytest tests/integration/parity -m "slow" -q --tb=short -p no:cacheprovider`
  - `443 passed, 444 deselected, 1309 warnings in 1843.08s`

Combined interpretation: `887 passed`, `0 skipped`, `0 xfailed`, `0 failed` on
the selected Python RC head and selected RC native/data runtime paths.

Cluster security hardening:

- `ruff check nirs4all_cluster/cli.py`: passed.
- `PYTHONPATH=. pytest -q` from cluster `main`: `142 passed, 1 skipped, 1 deselected, 3 warnings`.
- `ruff check nirs4all_cluster/cli.py` from cluster RC: passed.
- `PYTHONPATH=. pytest -q` from cluster RC: `145 passed, 1 skipped, 1 deselected, 3 warnings`.
- Post-push scan of active heads found no concrete `--token VALUE` or
  `--principal VALUE` examples on `origin/main` or `origin/rc/v1-full-refactor`.

Release-lock fetchability:

- `git ls-remote` against each aggregation-lock member's public `repo_url`
  confirmed both branch and tag resolve to the locked commit for `dag_ml`,
  `dag_ml_data`, `datasets`, `formats`, `io`, `lite`, and `methods`.
- Core/lite specifically now resolves `rc/v1-full-refactor-core` and
  `n4a-v1-rc1-2026.07-refactor` to `f120c28100642ac64d706a5b8404ce76770a5269`
  on the canonical `GBeurier/nirs4all-lite` remote.

## Decisions

- The old `810 passed, 30 skipped, 11 xfailed` class of evidence is superseded
  for Python parity accounting by the current split full parity run above.
- Hidden GitHub PR refs for cluster still expose only historical placeholder
  `--token dev` examples. They are not selected branch/tag heads and cannot be
  deleted by normal branch/tag pushes; if GitGuardian shows a non-placeholder
  value, rotate it externally and request GitGuardian/GitHub support review.
- The Core publication issue found by Claude was real when scanned, but is now
  corrected and verified by remote branch/tag resolution.

## Remaining Risks

- Core WASM/Methods strict parity still requires staged Methods JS/WASM artifacts
  (`index.js`, `n4m.js`, `n4m.wasm`).
- R, Octave/MATLAB, and full non-Python DatasetPackage materialization remain
  environment/toolchain gates.
- Studio frontend full Vitest was not rerun in this follow-up; backend full
  pytest remains `2335 passed, 0 skipped` from Wave 4W.
