# IMP-L18 - `nirs4all-tools` standalone migration toolbox scaffold

**Lane:** L18 tools / legacy migration. **Decision:** `DEC-MIG-001` / `LOCK-MIG`.
**Repo:** `/home/delete/nirs4all/nirs4all-tools` (new sibling git repo, branch `main`).
**Status:** scaffold implemented, validated, staged in its own repo; no commit yet.

## What landed

Created the standalone `nirs4all-tools` Python project that keeps legacy readers
and conversion helpers out of the V1 runtime. The first tool family is:

```text
nirs4all-tools legacy inspect <input>
nirs4all-tools legacy migrate <input> --output DIR --target nirs4all-workspace-v2
nirs4all-tools legacy verify <output-dir> --manifest PATH
```

The scaffold implements the contract-critical pieces now:

- no-in-place safety policy: disjoint output, source snapshot before/after every
  command, report/manifest path outside source, immutable read-only SQLite URI;
- stat-first legacy detection for SQLite workspaces, legacy prediction arrays,
  `.n4a` / `.n4a.py`, native-results directories, filesystem runs, loose
  prediction files, and forward-version refusal;
- stable CLI exit codes (`0`, `10`, `20`, `30`, `40`, `70`);
- JSON contract builders for `legacy_migration_manifest.v1`,
  `legacy_migration_report.v1`, and `legacy_id_map.v1`;
- `--dry-run` preview and `--copy-only` safety hatch with SHA-256 checksums;
- manifest-based `verify` for copy-only outputs;
- typed package (`py.typed`) with optional extras for later DuckDB, Parquet, and
  target-runtime work.

The real schema-transform engine from legacy stores to workspace v2 is
intentionally a marked stub. It returns `unsupported_capability` until the gated
legacy readers and target writer are wired.

## Files staged in `nirs4all-tools`

- `.gitignore`, `LICENSE`, `README.md`, `pyproject.toml`
- `src/nirs4all_tools/__init__.py`, `__main__.py`, `cli.py`
- `src/nirs4all_tools/checksums.py`, `commands.py`, `contracts.py`,
  `detect.py`, `errors.py`, `exit_codes.py`, `policy.py`, `vocab.py`,
  `py.typed`
- `tests/conftest.py`, `tests/test_cli.py`, `tests/test_commands.py`,
  `tests/test_contracts.py`, `tests/test_detect.py`, `tests/test_policy.py`

The repo was initialized locally with `git init -b main`; no remote is
configured and nothing was committed.

## Validation

Run from `/home/delete/nirs4all/nirs4all-tools`:

```bash
ruff check .
PYTHONPATH=src /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest -q
PYTHONPATH=src /home/delete/nirs4all/nirs4all/.venv/bin/python -m compileall -q src tests
PYTHONPATH=src /home/delete/nirs4all/nirs4all/.venv/bin/python -m mypy src/nirs4all_tools
PYTHONPATH=src /home/delete/nirs4all/nirs4all/.venv/bin/python -m nirs4all_tools --version
PYTHONPATH=src /home/delete/nirs4all/nirs4all/.venv/bin/python -m nirs4all_tools legacy inspect . --format json | /home/delete/nirs4all/nirs4all/.venv/bin/python -m json.tool
```

Results:

- `ruff check .` -> all checks passed.
- `pytest -q` -> 57 passed.
- `compileall` -> exit 0.
- `mypy src/nirs4all_tools` -> success, 11 source files.
- CLI version smoke -> `nirs4all-tools 0.0.1`.
- CLI inspect JSON smoke -> valid JSON.
- Manual copy/verify smoke on a synthetic SQLite workspace -> migrate
  `--copy-only` exit 0 and `legacy verify` exit 0.
- `git diff --cached --check` in the new repo -> clean.

## Fixes applied by supervisor

The Claude L18 session hit `maxTurns` before writing a report. Supervisor audit
found a valid but unfinished scaffold plus local lint/test blockers:

- missing `_unknown()` detector helper;
- `tests/test_detect.py` imported `tests.conftest` although `tests/` is not a
  package;
- long lines/import-order Ruff issues;
- generated Ruff/pytest/mypy caches.

These were corrected locally. The scaffold was then revalidated and staged.

## Residual risks / next slice

- The transform engine is not implemented yet; only `inspect`, `--dry-run`,
  `--copy-only`, and `verify` are real.
- The CLI uses a Python 3.11+ runtime; the system `python3` in this shell is
  Python 3.10 and should not be used for validation.
- No remote exists yet for the new repo. Create/push the real GitHub repository
  before treating this as a releasable package.
- Next implementation slice: import/adapt the legacy readers from
  `nirs4all.pipeline.storage.migration`, write workspace-v2 output, and add
  fixture-based migration golden tests.
