# RC-M Repository / Benchmarks / Papers

Date: 2026-07-02

Scope: advance `nirs4all-repository`, `nirs4all-benchmarks`, and `nirs4all-papers` as provider/plugin
surfaces without touching provider adapter code or introducing ecosystem write-back.

## Decisions

- `nirs4all-repository` stays the read-side preset/pipeline source, but now exports explicit provider-facing
  aliases over its existing API: `get_pipeline_list`, `list_pipelines`, `get_pipeline`, and `get_bundle`.
- `nirs4all-benchmarks` remains a consumer/test planner only. Its repository bridge now prefers the
  provider-style entry points when available and falls back to the historical `list/get` names.
- `nirs4all-papers` remains a bounded export plugin. Its first-party facade now exposes the pure-read helpers
  that the provider adapter already treats as part of the papers plugin surface: `load_paper`, `citation`,
  and `bibtex`.

## Files Modified

### `nirs4all-repository`

- `README.md`
- `src/nirs4all_repository/__init__.py`
- `tests/test_api.py`

### `nirs4all-benchmarks`

- `README.md`
- `src/nirs4all_benchmarks/ingestion/repository.py`
- `tests/test_repository_bridge.py`

### `nirs4all-papers`

- `README.md`
- `src/nirs4all_papers/provider.py`
- `tests/test_provider_api.py`

## Validation

### `nirs4all-repository`

- `PYTHONPATH=src python3.11 -m pytest tests/test_api.py -q` -> passed (`8 passed`)
- `PYTHONPATH=/tmp/rc_v1_repo_cli:src python3.11 -m pytest tests/test_cli.py -q` -> passed (`6 passed`)
- `python3.11 -m ruff check src/nirs4all_repository/__init__.py tests/test_api.py README.md` -> passed
- `PYTHONPATH=src python3.11 -m mypy src/nirs4all_repository/__init__.py` -> passed

Note: `tests/test_cli.py` required a temporary `/tmp/rc_v1_repo_cli` dependency overlay because `typer`
was not installed in the base shell.

### `nirs4all-benchmarks`

- `PYTHONPATH=/tmp/rc_v1_bench_jsonschema:src python3.11 -m pytest tests/test_repository_bridge.py -q` -> passed (`5 passed`)
- `PYTHONPATH=/tmp/rc_v1_bench_jsonschema:src python3.11 -m pytest tests/test_upload_indexing.py -q` -> passed (`8 passed`)
- `python3.11 -m ruff check src/nirs4all_benchmarks/ingestion/repository.py tests/test_repository_bridge.py README.md` -> passed
- `PYTHONPATH=src python3.11 -m mypy src/nirs4all_benchmarks/ingestion/repository.py` -> passed

Note: the base shell ships `jsonschema 3.2.0`, which lacks `Draft202012Validator`; targeted pytest runs used a
temporary `/tmp/rc_v1_bench_jsonschema` overlay with `jsonschema 4.26.0`.

### `nirs4all-papers`

- `PYTHONPATH=src python3.11 -m pytest tests/test_provider_api.py -q` -> passed (`7 passed`)
- `PYTHONPATH=src python3.11 -m pytest tests/test_build.py tests/test_provenance.py -q` -> passed (`10 passed`)
- `python3.11 -m ruff check src/nirs4all_papers/provider.py tests/test_provider_api.py README.md` -> passed
- `PYTHONPATH=src python3.11 -m mypy src/nirs4all_papers/provider.py` -> passed

## Risks / Remaining Gaps

- Repository aliases are additive; existing `list/get/fetch` callers are unchanged. The provider adapter remains
  the canonical cross-package compatibility layer.
- Benchmarks still depends on the optional `nirs4all-repository` package being installed by the caller. This
  tranche did not add a packaging extra or CLI wrapper.
- Papers still does not execute pipelines; replay remains the existing approximate in-browser reference engine.
- No full cross-repo provider conformance run was executed here. Follow-up can run `nirs4all-providers`
  real-API conformance once the RC integration batch is assembled.

## Follow-Up Recommendation

- Run the `nirs4all-providers` real-API conformance tests against these three RC worktrees after integration so
  the adapter layer verifies the new repository aliases and papers facade additions end to end.
