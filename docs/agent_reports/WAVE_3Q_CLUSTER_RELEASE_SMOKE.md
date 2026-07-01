# Wave 3Q - Cluster Installed Release Smoke

Date: 2026-07-01

## Scope

Lane I tranche focused on a targeted `nirs4all-cluster` release proof. This validates the installed wheel and CLI/server/worker surface without running `nirs4all.run` and without replacing the heavier parity/validation harness.

## Commit

- `nirs4all-cluster` `7628433` - `test(release): add installed wheel smoke`

## Files Modified

`nirs4all-cluster`:

- `README.md`
- `pyproject.toml`
- `tests/conftest.py`
- `tests/test_release_smoke.py`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Locke | Lane I implementation | done | Added an installed wheel smoke covering import source, console script, server, `/healthz`, `/ui`, auth, worker registration, `workers`, `run`, and `jobs`. |
| Sartre the 2nd | Review | fixed | Found the smoke was collected by default and too fragile for the light unit/API gate. It is now opt-in by marker/explicit path, with longer startup deadlines. |

## Decisions

- Add `tests/test_release_smoke.py` as a release packaging smoke, not a default unit/API test.
- Keep `pytest -q tests/test_release_smoke.py` as the explicit command; also support `--run-release-smoke`.
- Mark the smoke `release_smoke` and deselect it during default collection.
- Preserve the invariant that only `nirs4all_cluster/runners/nirs4all_run.py` imports `nirs4all` inside the package.
- Do not claim metric parity from this smoke; it intentionally submits a queued job without executing the runner.

## Tests Run

`nirs4all-cluster`:

- `uv run pytest -q` -> 135 passed, 1 skipped, 1 deselected, 3 warnings.
- `uv run pytest -q tests/test_release_smoke.py` -> 1 passed.
- `uv run pytest -q --run-release-smoke tests/test_release_smoke.py` -> 1 passed.
- `uv run ruff check tests/conftest.py tests/test_release_smoke.py` -> passed.
- `uv run pytest -q tests/test_cli.py tests/test_release_smoke.py` -> 3 passed before the opt-in correction.
- `git diff --check` -> passed.
- Import audit: `nirs4all_cluster/` package imports `nirs4all` only in `nirs4all_cluster/runners/nirs4all_run.py`.

## Risks / Follow-Ups

- The release smoke depends on `uv`.
- Full cluster metric parity remains owned by `/home/delete/nirs4all/nirs4all/.venv/bin/python scripts/validation.py`, which was not run in this small batch.
- The smoke validates installed API/entrypoints and queue behavior, not a successful `nirs4all.run` task.
