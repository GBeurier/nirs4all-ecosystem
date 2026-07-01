# W78 report - tools migration completeness

Summary:
W78 advanced `nirs4all-tools` migration completeness for old prediction/native-results sidecars without adding runtime V1 legacy readers. The lowerable single-artifact `native-results-v1` preview now emits runtime-readable workspace-v2 array sidecars from `predictions.parquet`, keeps the original native payload checksummed under `preserved/native-results-v1/`, and verifies every emitted array row through manifest `arrays:<prediction_id>` checksums.

Context read:
- `/home/delete/nirs4all/AGENTS.md`
- `nirs4all-tools` `README.md` and `pyproject.toml`
- `SW4_MIG_CONVERTER_spec.md` migration and verification sections
- Prior tool reports: `W30_TOOLS_MIGRATION.md`, `W39_TOOLS_NATIVE_RESULTS.md`, `W49_TOOLS_RESULTS_LOWERING.md`, `W59_TOOLS_NATIVE_RESULTS_LOWERING.md`
- Current `nirs4all-tools` `main`/`refactor/W78-migration-complete` history through W59 merge

Code changed:
- Refactored the existing runtime Parquet sidecar writer so legacy SQLite arrays and native-results rows share the same normalized workspace-v2 sidecar/checksum path.
- Added native-results array-row normalization that reuses the same deterministic prediction IDs as metadata lowering.
- Extended lowerable native-results migrations to write `arrays/<dataset>.parquet`, manifest file checksums, and `arrays:<prediction_id>` row checksums while preserving the source native payload.
- Strengthened `legacy verify` / `migrate --verify` to check `store.sqlite` integrity/user_version and verify every runtime array sidecar row against manifest row checksums, including metadata prediction-id coverage.
- Added focused tests for native sidecar output and array-row checksum tamper detection.
- Updated README support notes from native metadata-only preview to metadata plus sidecar preview.

Files touched in `nirs4all-tools`:
- `README.md`
- `src/nirs4all_tools/commands.py`
- `src/nirs4all_tools/native_results.py`
- `tests/test_commands.py`

Commit:
- `f7c6d93419212b8c7a0d1ef2e12054fe8d6682d2` (`feat(migration): lower native prediction sidecars`)

Validation:
- `PYTHONPATH=src /home/delete/miniconda3/bin/python3 -m pytest tests/test_commands.py -q` -> 31 passed
- `PYTHONPATH=src /home/delete/miniconda3/bin/python3 -m pytest` -> 73 passed
- `/home/delete/miniconda3/bin/python3 -m ruff check .` -> passed
- `PYTHONPATH=src /home/delete/miniconda3/bin/python3 -m mypy` -> passed
- `PYTHONPATH=src /home/delete/miniconda3/bin/python3 -m py_compile $(rg --files -g '*.py' src tests)` -> passed
- `git diff --check` -> passed

Notes:
- Runtime V1 remains unchanged and receives no legacy/native-results reader.
- Native-results lowering remains bounded to the current single standalone dag-ml native-results directory shape with strict schema/hash preflight.
- Multi-artifact/mixed native-results roots and non-lowerable native payloads still follow the existing strict refusal or best-effort opaque preservation paths.
- `nirs4all-ecosystem` was only updated with this report and was not committed.
