# WAVE 4BA — Release cockpit, UI npm workflow, tools RC release

Date: 2026-07-04

## Scope

- Finalized the public release/cockpit state after core/ui/providers/papers/tools RC work.
- Kept `nirs4all` Python and `nirs4all-studio` production out of release changes.
- Did not touch `nirs4all-drafts` or `nirs4all-lab`.

## Agents

- Codex main agent: implementation, publication checks, commits, pushes, GitHub Actions monitoring.
- Codex explorer agent `019f2a47-85fb-7340-a996-98e4575392d1`: read-only cockpit/org publication audit.
- Claude Code `fable` requested, fell back to Opus: read-only pre-release/cockpit/e2e audit. No edits.

## Repos / files changed

- `nirs4all-cockpit`
  - `cockpit/collect/github.py`
  - `data/current.json`
  - `ops/manual-actions.yaml`
  - `ops/targets.yaml`
  - `tests/test_stats.py`
  - `tests/test_targets_topology.py`
  - `web/app.js`
- `nirs4all-org`
  - `index.html`
- `nirs4all-ui`
  - `.github/workflows/release-npm.yml`
- `nirs4all-tools`
  - `.github/workflows/publish.yml`

## Decisions

- `nirs4all-core`, `nirs4all-providers`, and `nirs4all-tools` PyPI targets are now `tracked`, not `planned`: workflows exist and the registry gap is a real release blocker.
- PyPI blockers are explicitly manual-actioned as Trusted Publisher setup tasks.
- `nirs4all-ui` npm is tracked and has an automated publish workflow for future tags/dispatch.
- Cockpit GitHub collector now resists stale local GitHub tokens and falls back to `gh api` for release/pages probes where direct HTTP is unauthenticated/rate-limited.
- `nirs4all-org` no longer advertises `pip install nirs4all-core` while PyPI returns 404; npm now lists `nirs4all-ui`.

## Publications / external state

- `nirs4all` npm: `0.2.3`.
- `nirs4all-ui` npm: `0.1.1`; GitHub Pages enabled and deployed.
- `nirs4all-papers` PyPI: `0.2.1`.
- `nirs4all-tools` GitHub Release: `v0.0.1`; PyPI publish attempted and failed with `invalid-publisher`.
- `nirs4all-core` PyPI: still HTTP 404, blocked by Trusted Publisher.
- `nirs4all-providers` PyPI: still HTTP 404, blocked by Trusted Publisher.

## Tests / gates run

- `nirs4all-cockpit`: `pytest -q` (91 passed), `ruff check .`, `cockpit.cli validate-targets ops/targets.yaml`, `python -m build --wheel`, network `cockpit.cli collect`.
- `nirs4all-ui`: `npm run ci` with Node 24 Linux npm (52 tests, typecheck, build, pack smoke).
- `nirs4all-tools`: `pytest -q` (114 passed), `ruff check .`, `mypy`, `python -m build`, `twine check`.
- `nirs4all-org`: HTML parser smoke check and content checks for npm/PyPI install text.
- GitHub Actions observed green: `nirs4all-ui` CI + Pages, `nirs4all-cockpit` version-guard + Pages, `nirs4all-org` version-guard + Pages, `nirs4all-tools` CI.

## Remaining risks / blockers

- PyPI Trusted Publishers must be created for:
  - `nirs4all-core` / `.github/workflows/release-python.yml` / env `pypi`
  - `nirs4all-providers` / `.github/workflows/publish.yml` / env `pypi`
  - `nirs4all-tools` / `.github/workflows/publish.yml` / env `pypi`
- `nirs4all-tools` PyPI publish failed exactly with `invalid-publisher`; this is expected until the PyPI project/publisher is configured.
- Cross-language e2e scenario contracts remain honest planning gates; real executable entrypoints are still a separate implementation step.
