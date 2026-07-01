# W89 Providers Pipeline Services

## Summary

Updated `nirs4all-providers` on branch `refactor/W89-pipeline-services` to make pipeline-list access explicit through `get_pipeline_list` while preserving `list_pipelines` compatibility. Repository remains a read-side provider of pipeline lists and pipeline payloads. Benchmarks now has explicit contract coverage for local pipeline planning against dataset tokens. Papers is documented and tested as a potential local export-plugin facade, not a write-side repository.

## Changed Files

- `README.md`
- `src/nirs4all_providers/__init__.py`
- `src/nirs4all_providers/base.py`
- `src/nirs4all_providers/repository.py`
- `src/nirs4all_providers/benchmarks.py`
- `src/nirs4all_providers/papers.py`
- `tests/test_repository_provider.py`
- `tests/test_benchmarks_provider.py`
- `tests/test_papers_provider.py`

## Commit

- `701b5c4 feat(providers): clarify pipeline service contracts`

## Tests Run

- `PYTHONPATH=src pytest -q` - passed
- `PYTHONPATH=src pytest -q -ra` - passed; skipped only optional real-backend conformance imports for absent `nirs4all_datasets`, `nirs4all_repository`, `nirs4all_benchmarks`, and `nirs4all_papers`
- `PYTHONPATH=src ruff check .` - passed
- `PYTHONPATH=src mypy src` - passed

## Failures

- `pytest -q` failed before setting `PYTHONPATH=src` because the local `src` package was not importable in the bare environment.
- `python -m pip install -e .` failed because this shell has no `python` shim.
- `python3 -m pip install -e .` failed because the current setuptools backend configuration does not support editable installs through PEP 660 and there is no `setup.py` or `setup.cfg`.

## Blockers

None. No upload support was added or assumed.
