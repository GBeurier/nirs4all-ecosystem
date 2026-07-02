# Wave 4H - CI gates and full Python parity refresh

Date: 2026-07-02  
Coordinator: Codex

## Scope

Follow-up to Wave 4G. This batch added missing CI/release gates for public
surfaces outside the aggregation lock, refreshed Cockpit's planned RC heads, and
ran the long Python-reference parity gate after the larger integration batch.

## Published code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all-web` | `rc/v1-full-refactor` | `1ccb839` / `n4a-v1-rc1-2026.07-refactor` | `.github/workflows/web-ci.yml`, `studio-lite/package.json` |
| `nirs4all-ui` | `rc/v1-full-refactor` | `8f9f2f6` / `n4a-v1-rc1-2026.07-refactor` | `.github/workflows/ci.yml`, `package.json` |
| `nirs4all-providers` | `rc/v1-full-refactor` | `5146908` / `n4a-v1-rc1-2026.07-refactor` | `.github/workflows/ci.yml`, `scripts/ci_gate.py`, `README.md` |
| `nirs4all-tools` | `rc/v1-full-refactor` | `7c5070f` / `n4a-v1-rc1-2026.07-refactor` | `.github/workflows/ci.yml`, `pyproject.toml` |
| `nirs4all-cockpit` | `rc/v1-full-refactor` | `71786b1` / `n4a-v1-rc1-2026.07-refactor` | `data/current.json` |
| `nirs4all-ecosystem` | `rc/v1-full-refactor` | this report commit | reports, release surface matrix |

## Changes

- Web now has a `web-ci` workflow that checks out the matching
  `nirs4all-ui` sibling ref, then runs `npm ci`, the client-side-only contract,
  typecheck, Vitest, and build. `studio-lite/package.json` exposes
  `npm run test:client-only`.
- `nirs4all-ui` now has a CI workflow and `npm run ci`, covering typecheck,
  Vitest, build, and `npm pack --dry-run`.
- `nirs4all-providers` now has a single local/CI gate script for Ruff, mypy,
  hermetic tests, conformance tests, and neutral contract validation. The CI
  deliberately installs only `.[dev]` so optional backings remain optional.
- `nirs4all-tools` now has a CI workflow that installs `.[dev,parquet]` and
  runs Ruff, mypy, and pytest, so migration/converter goldens exercise Parquet
  support instead of skipping it.
- Cockpit's committed snapshot now records the current planned RC source heads
  for `nirs4all-ui`, `nirs4all-providers`, and `nirs4all-tools`.
- Workspace-local token files were not read; their permissions were tightened
  from `644` to `600`. They are outside valid child repos, but should still move
  to a real secret manager or outside the workspace before packaging/release.

## Agent reports

| Agent | Ownership | Outcome |
| --- | --- | --- |
| Codex worker | `nirs4all-web` only | Added Web CI and `test:client-only`; local Web gate passed. |
| Codex worker | `nirs4all-ui` only | Added UI package CI and `npm run ci`; local package gate passed. |
| Codex worker | `nirs4all-providers` only | Added providers CI/script; neutral contract gate passed. |
| Codex worker | `nirs4all-tools` only | Added tools CI and PEP 660 build-system floor; tools gate passed. |
| Claude Code reviewer | read-only | Returned a partially stale review; useful remaining point is to treat RC refs/tags as the authoritative release tree until main branches are intentionally reconciled. |

## Tests and gates

Python parity:

- Coverage meter precheck:
  `fallback=0`, `native=95`, `xfail_strict=0`, `skip=0`,
  `expected_fallback_target=0`.
- Full gate command:
  `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/RC-v1-dmd/crates/dag-ml-data-py/python:. PATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/target/debug:$PATH /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity/ -m parity -p no:cacheprovider -ra`
- Result:
  `659 passed, 227 deselected, 1530 warnings in 2037.46s (0:33:57)`.
- Interpretation:
  `227 deselected` are tests outside the `parity` marker, not skips. The gate
  reported no skipped, xfailed, or failed tests.

Web:

- `npm run test:client-only` -> 1 file, 2 tests passed.
- `npm run typecheck` -> passed.
- `npm run test` -> 21 files, 134 tests passed.
- `npm run build` -> passed with existing Vite compatibility/chunk warnings.
- `git diff --check` -> passed.

UI:

- `npm run ci` with Node 24 -> passed.
- The CI script covers typecheck, `50` Vitest tests, build, and
  `npm pack --dry-run`.

Providers:

- `python3.11 scripts/ci_gate.py` -> PASS.
- Internal steps: Ruff passed; mypy passed; hermetic tests passed;
  conformance tests `6 passed, 4 skipped`; neutral contracts
  `5 schemas, 5 fixtures` passed.
- `git diff --check` -> passed.

Tools:

- `python3.11 -m pip install -e ".[dev,parquet]"` -> passed.
- `python3.11 -m ruff check .` -> passed.
- `python3.11 -m mypy` -> passed.
- `python3.11 -m pytest -q` -> passed; local worker observed
  `114 passed, 1 warning`.

Cockpit:

- `python3.11 -m cockpit.cli summarize data/current.json` ->
  `green=75 stale=2 pending=5 missing=7 broken=0 unknown=0 excluded=0`.
- `python3.11 -m pytest tests/test_targets_topology.py -q` -> `3 passed`.
- `git diff --check` -> passed.

## Risks and decisions

- RC refs/tags are the authoritative release-candidate tree for this batch.
  Main-branch reconciliation is still a separate release-management action.
- `nirs4all-ui`, `nirs4all-providers`, `nirs4all-tools`, and
  `nirs4all-core` target registry names remain planned/missing until the first
  registry publications are made.
- Web CI depends on the matching `nirs4all-ui` ref being present upstream. That
  is deliberate: RC Web must fail loudly if shared UI is not published at the
  same branch/ref.
- Full Python-reference parity is now green on the selected RC heads, but final
  production cutover still needs the remaining non-Python gates: Studio/Web
  runtime contracts, migration converter goldens, IO/datasets bridge, methods
  language binding environments, release-lock validation, and registry publish
  proof.
