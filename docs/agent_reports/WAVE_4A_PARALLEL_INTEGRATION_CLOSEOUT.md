# Wave 4A - parallel integration closeout

Date: 2026-07-02  
Coordinator: Codex

## Scope

Integrated the post-reset V1 refactor batch with parallel Claude/Codex reviews.
No work was done in `nirs4all-drafts` or `nirs4all-lab`.

## Published heads

| Repo | Head | Tag / branch |
| --- | --- | --- |
| `dag-ml` | `7f86a9b3db66` | `refactor/L20-lockstep`, `n4a-v1-2026.07-refactor` |
| `dag-ml-data` | `e68168543653` | `refactor/L20-lockstep`, `n4a-v1-2026.07-refactor` |
| `nirs4all-io` | `e2c35f8e3a0` | `refactor/L7-io-dagml-sibling`, `n4a-v1-2026.07-refactor` |
| `nirs4all-lite` | `f204ef4b0263` | `main`, `n4a-v1-2026.07-refactor` |
| `nirs4all-methods` | `cfb670ebb41b` | `main`, `n4a-v1-2026.07-refactor` |
| `nirs4all-cluster` | `766ed435e4a3` | `main`, `n4a-cluster-2026.07-refactor` |
| `nirs4all-tools` | `ea1a278` | `main`, `n4a-tools-2026.07-refactor` |
| `nirs4all-ui` | `ccef03b` | `main`, `n4a-ui-2026.07-refactor` |
| `nirs4all-studio` | `aa50e17` | `main`, `n4a-ui-2026.07-refactor` |
| `nirs4all-web` | `bf8a540` | `main`, `n4a-web-2026.07-refactor` |

## Agent lanes and review outcome

| Lane | Agent / owner | Outcome |
| --- | --- | --- |
| C / `dag-ml` | Claude opus review/fix | Restored missing-validation OOF diagnostic for direct refit without CV. Added regression test. Reviewed and committed by coordinator. |
| D / `nirs4all-tools` | Claude fable worker + coordinator review | Added non-finite runtime array guard so legacy migration exits through documented `UnsupportedInput` instead of raw `ValueError`. Published new repo/tag. |
| E / `nirs4all-lite` | Claude opus review | Reviewed public R/Python/WASM surface gate, no code changes after review, published. |
| F / `nirs4all-methods` | Claude opus review/integration | Merged `origin/main`, reviewed stale ABI README claim fix and guard test, published. |
| G / `nirs4all-io` | Claude audit + coordinator fix | Replaced stale `nirs4all_formats.open_path` call with public `open_recordset()` and stripped provenance metadata before assembly. |
| H / Studio/Web/UI | Coordinator | Shared `nirs4all-ui` repo exists and is consumed by Studio and Web. Studio e2e rerun with correct venv. |
| I / `nirs4all-cluster` | Claude opus review | Reviewed running-task failure requeue via legal `running -> failed -> queued` transitions, published. |
| K / final review | Coordinator + agents | Release lock, fetchability, checkout, surface matrix, targeted parity gates, and full Python-reference parity rerun after the integrated batch. |

## Tests and gates

- `dag-ml`: `cargo test -p dag-ml-core requires_oof_prediction_edge_refit_rejects_missing_validation_predictions -- --nocapture`; `cargo test -p dag-ml-cli --test cli_contracts cli_selects_builds_and_validates_replay_bundle -- --nocapture`; `cargo fmt --check`; `python3 scripts/check_so_freshness.py`; wheel smoke via temporary Python 3.11 venv.
- `nirs4all-io`: `PYTHONPATH=src:../nirs4all-formats/bindings/python/python .venv/bin/python -m pytest -m 'not parity' -q` -> `231 passed, 2 deselected`; targeted vendor tests -> `2 passed`.
- `nirs4all-tools`: `ruff check .`; `mypy`; `python -m pytest -q` -> `111 passed`.
- `nirs4all-lite`: agent review reran `PYTHONPATH=bindings/python/src python3 -m unittest bindings.python.tests.test_cross_language_surface -v` and `make test-python-v1-surfaces` -> green.
- `nirs4all-methods`: agent review reran `test_binding_readme_abi_claims.py` -> `4 passed`; merged remote docs commits cleanly.
- `nirs4all-cluster`: agent review reran scheduler/server targeted suite -> `47 passed`; `ruff check` clean.
- `nirs4all-studio`: `CI=1 PATH=.venv/bin:... npm run test:e2e` -> `63 passed`.
- `nirs4all-web`: previously completed `typecheck`, `test`, `validate:catalog`, `build`, `build:single`, hosted smoke, file smoke.
- Release lock: `generate`, `validate`, `audit-fetchability --fail-on-unfetchable` -> `7/7`, `checkout-members` -> all seven members checked out at locked commits.
- Surface matrix: `python3 scripts/n4a_release_surface_matrix.py validate`; report confirms required `nirs4all` Python, R, and browser/WASM surfaces.
- Full Python-reference parity: `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python:/home/delete/nirs4all/dag-ml-data/crates/dag-ml-data-py/python:$PYTHONPATH /usr/bin/python3.11 -m pytest tests/integration/parity -v` in `_worktrees/INT-nirs4all` -> `810 passed, 30 skipped, 11 xfailed` in `1882.37s`.

## Decisions

- `nirs4all-ui` is now a real shared repo. Studio and Web consume it; this replaces the earlier open decision about whether a shared UI package exists.
- The current Python `nirs4all` library remains the parity oracle. The previous full parity run had a single missing-baseline failure, fixed by adding the two seeded generator baselines; full parity was rerun after the integrated batch and passed.
- `nirs4all-tools` was created/published because the migration CLI is part of public/accounting but was not yet a GitHub repo.
- Existing stale worktrees/branches were not merged wholesale; only reviewed commits/heads above were selected.

## Remaining risks

- The full parity suite still carries its existing documented `30 skipped` and `11 xfailed` cases; no new parity failure remains in this batch.
- `nirs4all-tools` still has documented non-finite score surfaces outside the fixed runtime-array path.
- Release lock covers the seven aggregation members; Studio, Web, UI, Tools, and Cluster remain outside the aggregation lock but are tagged and accounted for in the surface matrix/report.
