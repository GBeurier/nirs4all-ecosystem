# W76 - Studio Runtime Bypass

Status: complete.

## Scope

Advanced Studio runtime adoption / bypass parity for L12/B-011/B-017 with a bounded backend contract fix.

Inspected before editing:
- Current INT-studio head: `b427a22` (`refactor/integration-studio`, merged W55).
- W44 evidence: preprocessing execution centralized through the shared runtime operator helper.
- W45 evidence: UI runtime/result status display helpers extracted.
- W55 evidence: route-level quick-run and aggregated-predictions parity gate added.

## Change

Studio's `api.runtime_engine` now accepts a `RunResult.to_rt_result()` envelope shaped either as Python objects or as JSON/native mappings.

Before W76, Studio only read `.manifest` and `.diagnostics` attributes. A native/REST-shaped `RtResult` dictionary with `{"manifest": {"engine": ...}, "diagnostics": [...]}` would be ignored, causing the run record to fall back to warning-based engine heuristics. W76 normalizes runtime fields through a mapping-or-attribute accessor so structured native result contracts remain authoritative.

Added a focused regression test proving a mapping-shaped `RtResult` wins over a simultaneous transparent fallback warning and preserves the structured diagnostics.

## Files touched

- `/home/delete/nirs4all/_worktrees/W76-studio-runtime-bypass/api/runtime_engine.py`
- `/home/delete/nirs4all/_worktrees/W76-studio-runtime-bypass/tests/test_runtime_engine.py`
- `/home/delete/nirs4all/nirs4all-ecosystem/docs/agent_reports/W76_STUDIO_RUNTIME_BYPASS.md`

## Commit

- `10f35e7` - `fix(runs): accept mapping runtime result envelopes`

## Verification

Run from `/home/delete/nirs4all/_worktrees/W76-studio-runtime-bypass`:

```bash
rtk /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runtime_engine.py -q
rtk /home/delete/.local/bin/ruff check api/runtime_engine.py tests/test_runtime_engine.py
rtk /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runs_engine_routing.py -q
rtk git diff --check
```

Results:
- `tests/test_runtime_engine.py`: `12 passed, 5 warnings`.
- Ruff: passed.
- `tests/test_runs_engine_routing.py`: `14 passed, 2 warnings`.
- `git diff --check`: passed.

Notes:
- The W76 worktree has no local `.venv`, so pytest used the existing Studio virtualenv at `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python`, matching the W55 approach.
- The warning counts are the existing transparent-fallback warning fixtures plus the new mapping-contract warning case.

## Blockers

None.

## Sync

Shared sync board was not edited.
