# Wave 3AH - Tools Legacy Runs Preview

Date: 2026-07-01
Lane: D - legacy saves / predictions / pipelines / workspaces converter
Scope: `nirs4all-tools`

## Decision

GO for a bounded semantic lowering of one legacy `runs/*/*/manifest.yaml`
payload when it references one complete `*_predictions.json` payload and the
manifest metadata matches the prediction JSON.

NO-GO remains for DuckDB semantic reading and `.n4a` semantic lowering in this
batch. DuckDB fixture coverage is still sentinel/preservation-only, and `.n4a`
would require bundle/joblib/export contracts outside this tranche.

No release-lock refresh was performed. `nirs4all-tools` is tracked as a public
accounting surface, outside the aggregation lock.

## Commit

- `nirs4all-tools` `0dde216` - `feat(legacy): lower single runs manifest predictions`

## Agents

- Heisenberg the 2nd: read-only Lane D audit. Recommended the bounded
  `runs/manifest.yaml` to loose-predictions lowering and explicitly rejected
  DuckDB/`.n4a` semantic work for this batch.
- Kepler the 2nd: review. Initial NO-GO found two issues:
  - extra top-level `*_predictions.json` files could be silently accepted;
  - dry-run unsupported counts could diverge from best-effort opaque
    preservation counts.
  Both were fixed and the final review verdict was GO.

## Files Modified

`nirs4all-tools`:

- `src/nirs4all_tools/legacy_runs.py`
  - New strict preview module for one legacy `runs/*/*/manifest.yaml`.
  - Parses only the small supported YAML subset, without adding a runtime YAML
    dependency.
  - Requires exactly one run manifest.
  - Requires `predictions.file` to remain under the source root and reference one
    `*_predictions.json`.
  - Validates `run_id`, `pipeline_id`, dataset, model class/name, completed
    status, and preprocessing against the referenced predictions JSON.
  - Rejects additional detected `*_predictions.json` files as mixed loose
    predictions.
- `src/nirs4all_tools/commands.py`
  - Routes the standalone legacy-runs shape before generic loose-prediction
    lowering.
  - Reuses the existing loose-predictions workspace-v2 lowering and runtime
    array sidecar writer.
  - Preserves the manifest tree and referenced prediction/metadata payloads with
    checksums.
  - Keeps mixed workspaces, DuckDB, `.n4a`, `.n4a.py`, and non-lowerable runs on
    the existing opaque preservation path.
  - Aligns dry-run unsupported entries with real best-effort preservation.
- `tests/test_real_golden_fixtures.py`
  - Adds golden coverage for strict success, lowerable dry-run, mismatch strict
    refusal, extra prediction strict refusal, extra prediction best-effort
    preservation, pyarrow-missing dry-run/best-effort alignment, and mismatch
    dry-run/best-effort alignment.
- `README.md`
  - Documents the new narrow legacy-runs preview and the remaining out-of-scope
    shapes.

## Tests Run

`nirs4all-tools`:

- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 pytest tests/test_real_golden_fixtures.py::test_golden_legacy_runs_extra_prediction_json_refuses_strict_without_output tests/test_real_golden_fixtures.py::test_golden_legacy_runs_extra_prediction_json_best_effort_preserves_all tests/test_real_golden_fixtures.py::test_golden_legacy_runs_missing_parquet_dry_run_matches_best_effort tests/test_real_golden_fixtures.py::test_golden_legacy_runs_manifest_mismatch_best_effort_matches_dry_run -q -p no:cacheprovider`
  - Result: 4 passed.
- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 pytest tests/test_real_golden_fixtures.py tests/test_commands.py tests/test_detect.py -q -p no:cacheprovider`
  - Result: passed, 68 tests.
- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider`
  - Result: passed, full local tools suite.
- `PYTHONPATH=src ruff check src/nirs4all_tools/legacy_runs.py src/nirs4all_tools/commands.py tests/test_real_golden_fixtures.py`
  - Result: passed.
- `PYTHONPATH=src mypy src/nirs4all_tools`
  - Result: passed.
- `python3 -m py_compile src/nirs4all_tools/legacy_runs.py src/nirs4all_tools/commands.py tests/test_real_golden_fixtures.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

`nirs4all-ecosystem`:

- `python3 scripts/n4a_release_surface_matrix.py validate`
  - Result: passed.
- `python3 scripts/n4a_release_surface_matrix.py report | rg 'nirs4all\.(python|r|browser_wasm|tools)|required nirs4all V1|public/accounting' -n`
  - Result: confirmed Python/R/WASM public NIRS4ALL surfaces and
    `nirs4all.tools.migration` accounting surface.

Full Python-reference parity was not run; this was an offline converter tranche
and the expensive parity gate remains reserved for larger integrated batches.

## Risks And Follow-Ups

- This is not a general YAML reader. It accepts only the tested scalar/list
  subset needed by the reduced legacy fixture.
- Non-top-level prediction references are handled by the code path but are not
  yet covered by a dedicated golden.
- DuckDB semantic reading and `.n4a` semantic lowering remain future work.
- Converter output remains a one-way offline migration; the runtime still does
  not import or execute legacy readers.
