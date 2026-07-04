# Wave 4CB - Python Paper Repository E2E

## Scope

- Closed `e2e-python-reopen-paper-repository-refit`.
- Added the missing Python e2e entrypoint on the `nirs4all` RC branch.
- Hardened the paired `nirs4all-papers` export/repository handoff step so it consumes the Python reopen ledger when present.

## Commits Integrated

- `nirs4all`: `be223b4a test(e2e): add paper repository reopen parity` on `refactor/L17-pyref`.
- `nirs4all`: `29dd1f59 test(e2e): expose repository refit recipe` on `refactor/L17-pyref`.
- `nirs4all-papers`: `ed74521 test(e2e): consume python reopen ledger` on `main`.
- `nirs4all-ecosystem`: this report and the manifest Python interpreter fix.

## Manifest Changes

- `python-reopen-rerun` now requires and executes `python3.11`; `python3` resolved to Python 3.10 on this workstation and cannot import the current `nirs4all` package.

## Tests

- `python3.11 -m py_compile tests/e2e/test_pipeline_reopen_paper_repository.py`
- `python3.11 -m ruff check tests/e2e/test_pipeline_reopen_paper_repository.py`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_pipeline_reopen_paper_repository.py::test_reopen_rerun_parity --artifacts-dir=/tmp/n4a-e2e-python-paper-repository-4ca -q`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-python-paper-repository-4cb run e2e-python-reopen-paper-repository-refit --execute`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_repository_refit_export.py --artifacts-dir=/tmp/n4a-papers-standalone-4ce -q`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_repository_refit_export.py --artifacts-dir=/tmp/n4a-e2e-python-paper-repository-4cd -q`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-python-paper-repository-4ce run e2e-python-reopen-paper-repository-refit --execute`
- `python3.11 scripts/n4a_e2e_scenarios.py plan`

## Artifacts

- `/tmp/n4a-e2e-python-paper-repository-4cb/python-paper-repository/reopened-result.json`
- `/tmp/n4a-e2e-python-paper-repository-4cb/python-paper-repository/reopened-refit.n4a`
- `/tmp/n4a-e2e-python-paper-repository-4cb/python-paper-repository/saved-pipeline.json`
- `/tmp/n4a-e2e-python-paper-repository-4cb/python-paper-repository/paper-export.zip`
- `/tmp/n4a-e2e-python-paper-repository-4cb/python-paper-repository/repository-best-pipeline.json`
- `/tmp/n4a-e2e-python-paper-repository-4ce/python-paper-repository/reopened-result.json`
- `/tmp/n4a-e2e-python-paper-repository-4ce/python-paper-repository/repository-best-pipeline.json`

## Result Snapshot

- Python legacy vs dag-ml `best_rmse_abs`: `0.0`.
- Python legacy vs dag-ml best prediction delta: `0.0` across `59` rows.
- Python legacy vs dag-ml final/refit prediction delta: `0.0` across `130` rows.
- Reopened `.n4a` bundle prediction delta vs legacy final/refit: `0.0`.
- dag-ml native result artifacts were present and no legacy fallback warning was accepted.
- Repository handoff pipeline id: `paper_pls_nirs_refit`; publication blockers: `[]`.
- Papers consumed `repository_refit_recipe` from the Python ledger, not the old paper-demo fallback.
- Descriptor provenance includes `python_reopened_result_sha256`; batch 4CE consumed Python git head `29dd1f59f36e`.

## Risks

- The papers step intentionally validates export and repository handoff only, but now refuses a bad Python ledger and carries its provenance into the repository descriptor.
- The saved pipeline descriptor is reopened into idiomatic Python operator instances. Reopening it as raw `{"class": ...}` dictionaries currently causes a dag-ml fallback and must not be used as proof of native parity.
