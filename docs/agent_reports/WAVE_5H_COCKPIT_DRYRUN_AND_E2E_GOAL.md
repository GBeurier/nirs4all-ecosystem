# Wave 5H - Cockpit repository dry-run and E2E goal update

Date: 2026-07-04

## Scope

- Cockpit publication topology for `nirs4all-repository`.
- Goal update: keep the ten complex cross-language/multimodal E2E scenarios as an explicit V1 refactor deliverable.

## Changes Integrated

- `GBeurier/nirs4all-cockpit`:
  - `ops/targets.yaml` now models the `nirs4all-repository` PyPI workflow as a gated publisher with `dry_run` defaulting to `"true"`;
  - `ops/manual-actions.yaml` now reruns `nirs4all-repository` publishing with `dry_run=false` after the PyPI Trusted Publisher is created;
  - `tests/test_targets_topology.py` locks the repository action to `dry_run=false` and keeps workflow inputs checked against the target inventory;
  - `tests/test_admin_workflows.py` now guards the `dry_run` string gate against Python truthiness mistakes (`"false"` must publish, `"true"` must not).

## E2E Goal Status

- The active refactor goal includes ten ecosystem E2E scenarios covering R, Python, WASM/Web, datasets/IO, pipelines, repository, papers, saved workspaces, predictions, cluster, and methods bindings.
- Canonical contract: `docs/contracts/e2e/cross-language-scenarios.n4a.json`.
- Runner: `scripts/n4a_e2e_scenarios.py`.
- Current local plan status:
  - `10 ready`;
  - `2 strict` scenarios: converter legacy predictions to Web, cluster DAG rights/core client;
  - `8 hybrid` scenarios with explicit `v1_refactor_contract` gaps and acceptance criteria.

## Tests and Checks

- `nirs4all-cockpit`:
  - `. .venv/bin/activate && pytest -q tests/test_admin_workflows.py tests/test_targets_topology.py` -> `12 passed`;
  - `. .venv/bin/activate && pytest -q` -> `98 passed`;
  - `. .venv/bin/activate && ruff check .` -> pass;
  - `git diff --check` -> pass.
- `nirs4all-ecosystem`:
  - `python3 scripts/n4a_e2e_scenarios.py validate` -> `OK: 10 cross-language E2E scenarios`;
  - `python3 scripts/n4a_e2e_scenarios.py list` lists the ten expected scenarios;
  - `python3 scripts/n4a_e2e_scenarios.py plan --json` -> `Counter({'ready': 10})` in the full local workspace;
  - `pytest -q` -> `63 passed`.

## Review

- Claude Code review was launched on the cockpit diff to audit the target/manual-action/admin guardrails before integration.
- The useful finding was the Python string truthiness risk around `dry_run="false"`; this was addressed by the new `tests/test_admin_workflows.py` assertion.
- `nirs4all-repository/.github/workflows/publish.yml` was checked: the publish job is gated by `github.event_name == 'release' || inputs.dry_run == 'false'`.

## Decisions

- No full parity batch was launched in this wave; parity-heavy runs remain scheduled after larger integration batches.
- No skip, xfail, or fallback was introduced.
- PyPI publication remains blocked by external Trusted Publisher configuration, not by the local build/dry-run gates.
