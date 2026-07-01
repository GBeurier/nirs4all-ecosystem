# W44 report - Studio compute pushdown slice 3

Summary:
Centralized Studio preprocessing-chain execution behind a shared runtime operator helper so preprocessing routes, spectra/analysis wrappers, and playground preprocessing steps no longer carry separate transformer lookup/fit paths.

Code changed:
yes

Files touched:
- `/home/delete/nirs4all/_worktrees/W44-studio-compute3/api/shared/preprocessing_runtime.py`
- `/home/delete/nirs4all/_worktrees/W44-studio-compute3/api/preprocessing.py`
- `/home/delete/nirs4all/_worktrees/W44-studio-compute3/api/playground/steps.py`
- `/home/delete/nirs4all/_worktrees/W44-studio-compute3/api/spectra.py`
- `/home/delete/nirs4all/_worktrees/W44-studio-compute3/tests/test_preprocessing_runtime.py`
- `/home/delete/nirs4all/nirs4all-ecosystem/docs/agent_reports/W44_STUDIO_COMPUTE_PUSHDOWN3.md`

Commits:
- `13bd36f` - `refactor(api): share preprocessing execution helper`

Tests run:
- `python3 -m py_compile api/shared/preprocessing_runtime.py api/preprocessing.py api/playground/steps.py api/spectra.py tests/test_preprocessing_runtime.py`
- `/home/delete/nirs4all/_worktrees/W36-studio-runtime-adoption/.venv/bin/python -m pytest tests/test_preprocessing_runtime.py -q`
- `/home/delete/nirs4all/_worktrees/W36-studio-runtime-adoption/.venv/bin/python -m pytest tests/test_spectra_perf.py -q`
- `/home/delete/nirs4all/_worktrees/W36-studio-runtime-adoption/.venv/bin/python -m pytest tests/test_playground.py::TestPlaygroundEndpoints::test_execute_single_preprocessing tests/test_playground.py::TestPlaygroundEndpoints::test_execute_multiple_preprocessing tests/test_playground.py::TestPlaygroundEndpoints::test_execute_invalid_operator tests/test_playground.py::TestIntegration::test_preprocessing_chain -q`
- `python3 -m compileall -q api tests/test_preprocessing_runtime.py`
- `python3 -m ruff check .`

Tests not run and why:
Full `npm run lint:parallel` / `npm run test:parallel` were not run because this W44 worktree has no `.venv` and `node` is not installed in the shell. System Python also lacks `pytest`, so targeted pytest used the existing W36 Studio Python 3.11 virtualenv as an interpreter against this worktree.

Blockers:
None.

Impact on blockers/locks:
Advances B-017 by removing another duplicated Studio backend compute path and making preprocessing execution reuse the shared runtime operator resolver. No runtime route metadata, frontend components, or shared sync docs were touched.

Next action:
Continue B-017 by pushing the remaining analysis/chart metric helpers toward library-owned implementations where the core runtime exposes equivalent APIs.

Sync doc updated: no
