# W59 report - Tools native-results semantic lowering preview

Summary:
Implemented a narrow native-results-v1 semantic lowering preview in nirs4all-tools. One standalone current dag-ml native results directory now passes a strict schema/hash preflight and lowers run, pipeline, chain, prediction, and artifact metadata into a workspace-v2 `store.sqlite`; the original native payload is retained as checksummed audit provenance. Non-lowerable native payloads keep the best-effort opaque preservation path, but their manifest now records the concrete schema/preflight reason.

Code changed:
- Added tools-local native-results validation/lowering helpers; no runtime imports or runtime legacy readers.
- Routed a single lowerable native-results-v1 artifact through the preview transform before generic opaque preservation.
- Raised the detector's supported native manifest ceiling to current schema v3.
- Added lowerable native-results fixtures and tests for strict success, strict schema refusal, best-effort fallback, and detection.
- Updated README support notes for the native-results metadata preview and Parquet extra.

Files touched:
- README.md
- src/nirs4all_tools/commands.py
- src/nirs4all_tools/detect.py
- src/nirs4all_tools/native_results.py
- tests/conftest.py
- tests/test_commands.py
- tests/test_detect.py

Commits:
- cbdff68 feat(migrate): lower native results metadata preview

Tests run:
- `PYTHONPATH=src /home/delete/miniconda3/bin/python3 -m pytest` — 72 passed
- `/home/delete/miniconda3/bin/python3 -m ruff check .` — passed
- `PYTHONPATH=src /home/delete/miniconda3/bin/python3 -m mypy` — passed
- `PYTHONPATH=src /home/delete/miniconda3/bin/python3 -m py_compile $(rg --files -g '*.py' src tests)` — passed
- Module CLI smoke: generated a lowerable native-results fixture, ran `python -m nirs4all_tools.cli legacy migrate ... --strict --verify`, then `python -m nirs4all_tools.cli legacy verify ...` — passed

Tests not run and why:
- The installed `nirs4all-tools` console script was not on PATH in this worktree environment; the CLI smoke used `python -m nirs4all_tools.cli` with `PYTHONPATH=src`.

Blockers:
- This is metadata-only preview lowering. Native prediction arrays remain in the preserved source `predictions.parquet`; no workspace-v2 runtime array sidecar is emitted from native rows yet.
- Multi-artifact/mixed native-results inputs remain best-effort opaque unless run with `--strict`, where they are refused with a machine-checkable unsupported capability cause.

Impact on blockers/locks:
- Advances LOCK-MIG beyond W49 by turning one previously opaque native-results-v1 payload shape into runtime-readable workspace-v2 metadata.
- Makes remaining native semantic blockers explicit through strict schema/hash/parquet-column preflight and best-effort manifest reasons.

Next action:
- Extend the preview to emit runtime array sidecars from native prediction rows, then cover multi-run/native-results roots once the desired workspace grouping contract is fixed.

Sync doc updated: no
