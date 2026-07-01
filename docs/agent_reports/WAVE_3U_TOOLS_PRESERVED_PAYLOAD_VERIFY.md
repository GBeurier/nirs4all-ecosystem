# Wave 3U - Tools Preserved Payload Verify

Date: 2026-07-01

## Scope

Lane D tranche focused on `nirs4all-tools` verification of preserved opaque payloads. No semantic `.n4a`, DuckDB, or legacy `runs/` YAML conversion was added, and no full parity was run.

## Commit

- `nirs4all-tools` `b34eb21` - `fix(legacy): verify preserved payload checksums`

## Files Modified

`nirs4all-tools`:

- `src/nirs4all_tools/commands.py`
- `tests/test_commands.py`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Zeno the 2nd | Lane D implementation | done | Added preserved opaque payload verification to `legacy verify`. |
| Franklin the 2nd | Review | fixed | Found that removing or emptying `preserved_opaque` could neutralize the new check while preserved unsupported payloads still existed. The check now requires a ledger when `unsupported` contains preserved opaque entries. |

## Decisions

- `verify` now includes `preserved_payload_coverage` in the verification summary.
- Preserved opaque file and directory checksums are verified against the manifest.
- Duplicate paths, invalid ledger entries, paths outside `preserved/`, missing payload checksums, and checksum mismatches fail verification.
- If `unsupported` records preserved opaque payloads, `preserved_opaque` must be a non-empty list with matching coverage.
- Provenance payloads copied under `preserved/` after a successful semantic lowering are not falsely treated as opaque preservation unless the unsupported ledger marks them as preserved.

## Tests Run

`nirs4all-tools`:

- `PYTHONPATH=src pytest -q` -> 102 passed, 1 external `pytz` deprecation warning.
- `PYTHONPATH=src pytest tests/test_commands.py::test_verify_detects_preserved_opaque_file_checksum_mismatch tests/test_commands.py::test_verify_detects_preserved_opaque_directory_checksum_mismatch tests/test_commands.py::test_verify_requires_preserved_opaque_ledger_when_opaque_payloads_exist tests/test_commands.py::test_verify_requires_preserved_opaque_key_when_opaque_payloads_exist tests/test_commands.py::test_verify_rejects_invalid_preserved_opaque_ledger tests/test_commands.py::test_verify_rejects_duplicate_preserved_opaque_paths tests/test_commands.py::test_verify_rejects_preserved_opaque_paths_outside_preserved -q` -> 7 passed.
- `ruff check src/nirs4all_tools/commands.py tests/test_commands.py` -> passed.
- `mypy` -> passed.
- `python3 -m py_compile src/nirs4all_tools/commands.py tests/test_commands.py` -> passed.
- `git diff --check` -> passed.

## Risks / Follow-Ups

- `verify` remains a manifest/output self-consistency check, not a cryptographic proof against a fully rewritten manifest and output tree.
- Full semantic conversion for `.n4a`, DuckDB, and legacy `runs/` YAML remains out of scope.
