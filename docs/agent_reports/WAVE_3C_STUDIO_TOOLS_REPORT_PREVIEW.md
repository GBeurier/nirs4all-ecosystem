# Wave 3C - Studio nirs4all-tools Report Preview

Date: 2026-07-01T18:19:01+02:00

## Scope

Lane D/H focused batch in `_worktrees/INT-studio`:

- add a read-only backend endpoint for previewing `nirs4all-tools` legacy migration contract files;
- keep Studio runtime free of `nirs4all_tools` imports and subprocess execution;
- expose only a whitelisted summary, not raw manifest inventory, checksums, source paths, preserved payload lists, or unsupported payload lists;
- keep the existing in-place internal arrays migration separate from the offline `nirs4all-tools` flow.

No full parity run in this batch. This is contract preview only, not migration execution.

## Roadmap Coverage Note

The public `nirs4all` V1 surfaces remain in scope and unchanged by W3C:

- `nirs4all.python.oracle`
- `nirs4all.r.aggregate`
- `nirs4all.browser_wasm.aggregate`

The validated public surface matrix still covers those IDs; W3C does not alter release topology.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Galileo | Studio placement/contract audit | done | Read-only. Recommended placing the endpoint in `router_maintenance`, under `/workspace/migrate/report-preview`, with hard-coded contract constants and no `nirs4all_tools` import. |
| Fermat | W3C reviewer | done | Found two issues in the first patch: nested response leakage and report-only target schema version gap. Both were fixed; follow-up review found no blockers. |

## Decisions

- Endpoint: `POST /api/workspace/migrate/report-preview`.
- Request accepts explicit paths to `migration-report.json` and optional `unsupported-report.json` / `migration-manifest.json`.
- Contract validation is hard-coded in Studio:
  - `legacy_migration_report.v1`
  - `legacy_migration_manifest.v1`
  - `legacy_unsupported_report.v1`
  - target kind `nirs4all-workspace-v2`
  - target schema version `2` when available.
- If neither optional manifest nor unsupported report is provided, Studio validates report `$id`, report schema version, and target kind, then returns a warning that target schema version was not validated.
- If `target_summary.schema_version` is present in the report, it must be `2`.
- `recommended_next_command` is returned as a string only; Studio never parses or executes it.
- Response fields are normalized into typed nested summaries before returning to avoid arbitrary nested JSON leakage.

## Files Changed

`_worktrees/INT-studio`:

- `api/workspace/legacy_migration_report_preview.py`
- `api/workspace/models.py`
- `api/workspace/router_maintenance.py`
- `tests/test_legacy_migration_report_preview.py`

## Gates

- `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-studio /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_legacy_migration_report_preview.py -q --tb=short` - 14 passed.
- `/home/delete/.local/bin/ruff check api/workspace/legacy_migration_report_preview.py api/workspace/models.py api/workspace/router_maintenance.py tests/test_legacy_migration_report_preview.py` - passed.
- `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m py_compile api/workspace/legacy_migration_report_preview.py api/workspace/models.py api/workspace/router_maintenance.py tests/test_legacy_migration_report_preview.py` - passed.
- `git diff --check` - passed.

## Risks

- The endpoint accepts explicit local file paths, so it remains a local-trust backend surface. The response is whitelisted and JSON-size-capped, but callers can still ask Studio to read valid JSON contract files from arbitrary readable paths.
- No UI was added in W3C. This is a backend contract surface only.
- Full Python-reference parity was not run.
