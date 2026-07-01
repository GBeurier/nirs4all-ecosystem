# Wave 2L Post-Reset Control Board

Date: 2026-07-01

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Scope

This wave restarts coordination after a user reset. Prior wave reports and
worktrees are audit evidence only. No Claude agent or Claude worktree is a
trusted merge source without explicit review.

Hard constraints:

- use ChatGPT/Codex agents only;
- do not touch `nirs4all-drafts` or `nirs4all-lab`;
- preserve Python `nirs4all` as the parity oracle;
- do not reduce tests, xfail, or fallback semantics to get artificial green;
- review every lane before integration.

## Required Document Audit

Read in this wave:

- `/home/delete/nirs4all/SYNTHESE_MULTIMODALE_NIRS4ALL.md`
- `docs/PARALLEL_REFACTORING_ROADMAP.md`
- `docs/REFACTORING_ROADMAP_CRITICAL_REVIEW.md`
- `docs/PARALLEL_AGENT_PROMPT_PROGRAM.md`
- `docs/agent_reports/WAVE_2K_CONTROL.md`
- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- root `AGENTS.md` and `CLAUDE.md`

Path discrepancy:

- requested `nirs4all-ecosystem/docs/RELEASE_DISTRIBUTION_MATRIX.md` is absent
  locally;
- nearest available reference is
  `/home/delete/nirs4all/RELEASE_DISTRIBUTION_INVENTORY.md`.

## Post-Reset Checkout State

Main checkout audit:

| Repo | Branch | Head | Dirty | Notes |
| --- | --- | ---: | ---: | --- |
| `nirs4all` | `refactor/L17-pyref` | `5e00e40029ab` | 5 | Dirty local native-coverage diff. |
| `dag-ml` | `refactor/L20-lockstep` | `4f0a3b5a7a96` | 0 | Not on integration worktree head. |
| `dag-ml-data` | `refactor/L20-lockstep` | `2214f75aa3c7` | 1 | Dirty generated `_dag_ml_data.abi3.so`. |
| `nirs4all-studio` | `main` | `2ccbf68e03a7` | 0 | Reset away from W2K integration head. |
| `nirs4all-web` | `main` | `745eef89406e` | 0 | Reset away from W2K integration head. |
| `nirs4all-tools` | `main` | `9dc0c628c97d` | 0 | Contains W97/W104 work. |
| `nirs4all-io` | `refactor/L7-io-dagml-sibling` | `5651da51fe74` | 0 | Not on W93 integration head. |
| `nirs4all-lite` | `main` | `0486e1fc255f` | 0 | Initial post-reset audit; later W2L fix committed at `922fdd114231`. |
| `nirs4all-methods` | `main` | `469124855ff1` | 0 | Ahead of origin/main by 2. |
| `nirs4all-datasets` | `main` | `ac455f321144` | 0 | Ahead of origin/main by 3. |
| `nirs4all-ecosystem` | `main` | `cf8f9089876c` | 0 | Ahead of origin/main by 89. |

W2K integration heads still present in `_worktrees/INT-*`:

| Surface | Worktree | Head | Status |
| --- | --- | ---: | --- |
| `nirs4all` | `_worktrees/INT-nirs4all` | `17ed929eeb77` | clean |
| `dag-ml` | `_worktrees/INT-dagml` | `618ffb220b5f` | clean |
| `dag-ml-data` | `_worktrees/INT-dmd` | `818616e9a2c2` | clean |
| `nirs4all-studio` | `_worktrees/INT-studio` | `83aab1c18108` | clean |
| `nirs4all-web` | `_worktrees/INT-web` | `ee8ea7a95946` | clean |
| `nirs4all-io` | `_worktrees/INT-io` | `e52eecd827a0` | clean |
| `nirs4all-lite` | `_worktrees/INT-lite` | `6c08b92bd5f1` | clean |
| `nirs4all-cluster` | `_worktrees/INT-cluster` | `eac4d0b8a62a` | clean |
| `nirs4all-providers` | `_worktrees/INT-providers` | `1e289a9ee96d` | clean |

## Claude Work Review

Observed Claude-related processes are external state and must not be used by
this wave.

Nested Claude worktree audited:

| Worktree | Branch | Head | Audit result |
| --- | --- | ---: | --- |
| `nirs4all/.claude/worktrees/agent-a5af0970d430760ab` | `worktree-agent-a5af0970d430760ab` | `4e9dfe1ca0c0` | Head is already ancestor of `main`, `refactor/integration-nirs4all`, and `refactor/L17-pyref`; it has only untracked parity conformance files. |

The untracked Claude parity harness is stale for the current codebase because it
assumes the `engine=` surface is not wired yet and skips dag-ml legs until the
bridge lands. Current W2K/W98 state already has a stricter integrated parity
gate. Do not merge these untracked files without a new design review.

## Dirty Diffs To Review

`nirs4all/` dirty diff:

- `docs/compatibility.json`
- `nirs4all/pipeline/dagml/detect.py`
- `nirs4all/pipeline/dagml/run_backend.py`
- `nirs4all/pipeline/dagml/run_paths.py`
- `tests/integration/parity/test_conformance_dual_engine.py`

Observed intent: reduce `EXPECTED_FALLBACK` from 10 to 9 by adding native
coverage for source concat and by-source stacking. This is useful but risky; it
needs parity review before integration.

`dag-ml-data/` dirty diff:

- generated binary `crates/dag-ml-data-py/python/dag_ml_data/_dag_ml_data.abi3.so`

Do not commit this binary blindly. Either regenerate in a controlled lane or
discard only with explicit user approval.

## Lane Ownership For Current Codex Agents

| Lane | Owner Agent | Write Scope | Status |
| --- | --- | --- | --- |
| A | Codex `019f1d0a-41c4-7382-9010-661741579d8d` / Ptolemy | `nirs4all-ecosystem`, release manifest/lock docs/scripts | complete: report `W2L_LANE_A_RELEASE_LOCK.md` |
| B/C/F | Codex `019f1d0a-73af-7c42-af24-3f5136bf3b10` / Maxwell | `nirs4all`, `dag-ml`, `dag-ml-data`, `nirs4all-methods` | complete: report `W2L_LANE_BCF_PARITY_RUNTIME_METHODS.md` |
| D/E | Codex `019f1d0a-f22c-7523-b6a3-c638d96ed856` / Raman | `nirs4all-tools`, `nirs4all-lite` | complete: report `W2L_LANE_DE_TOOLS_LITE_NAMESPACES.md` |
| G | Codex `019f1d0a-c73c-7891-b033-ca04b1d2b6d6` / Avicenna | `nirs4all-io`, `nirs4all-datasets`, `nirs4all-formats` | complete: report `W2L_LANE_G_IO_DATASETS_FORMATS.md` |
| H | Codex `019f1d0a-9d6c-7483-9de8-4d3c301cae44` / Poincare | `nirs4all-studio`, `nirs4all-web` | complete: report `W2L_LANE_H_STUDIO_WEB_RUNTIME.md` |
| I/J | Codex `019f1d0b-23c0-7fd1-b2ee-90e71802d0c4` / James | `nirs4all-cluster`, `nirs4all-providers`, `nirs4all-repository`, `nirs4all-benchmarks`, `nirs4all-papers` | complete: report `W2L_LANE_IJ_CLUSTER_PROVIDERS.md` |
| K | coordinator local until an agent slot opens | review-only, no code | pending |

## Immediate Plan

1. Spawn Codex agents for disjoint review/implementation lanes.
2. Ask the parity/native agent to audit the dirty `nirs4all` diff before any
   integration.
3. Ask the release-lock agent to revalidate the lock after reset and propose the
   exact final pins.
4. Ask the UI/runtime and IO/provider agents to compare current main checkouts
   with the preserved W2K integration heads.
5. Integrate only after each lane returns files changed, tests run, risks, and
   decisions.

## Lane Results

### Lane G - IO/Datasets/Formats

Status: complete, no code changes.

Key result: W93 bridge work is present in `_worktrees/INT-io` at `e52eecd` and
datasets main at `ac455f32`, but the primary `nirs4all-io/` checkout is stale at
`5651da5`. Do not generate final release-lock pins from the stale checkout.

Focused gates passed:

- `_worktrees/INT-io`: `tests/test_dataset_package.py` -> 4 passed.
- `nirs4all-datasets`: `tests/test_dataset.py -k "to_io_spec or to_dataset_package or nirs4all_io_load"` -> 4 passed.
- `nirs4all-formats`: `cargo test -p nirs4all-formats-core --lib` -> 9 passed.

### Lane A - Release Lock

Status: complete, no central lock regeneration.

Key result: checked-in aggregation lock is stale. A temporary clean W2K lock was
generated at `/tmp/n4a-w2k.lock.json` and validated successfully, but final
lock regeneration requires explicit clean pin selection and must not use the
dirty current `dag-ml-data/` checkout.

Candidate W2K pins:

- `dag_ml=618ffb220b5f5`
- `dag_ml_data=818616e9a2c2`
- `io=e52eecd827a0`
- `lite=0486e1fc255f` before W2L D/E; use `922fdd114231` if the D/E facade fix is included.
- `methods=469124855ff1`
- `datasets=ac455f321144`
- `formats=89231b2786ef`

Focused gates:

- `pytest -q tests/test_release_lock.py` -> 5 passed.
- checked-in lock validation -> expected stale failure.
- `/tmp/n4a-w2k.lock.json` validation -> passed.

Coordinator integration:

- W2L selected clean root: `/tmp/n4a-w2k-root`, symlinked to `INT-dagml`,
  `INT-dmd`, `INT-io`, and current clean lite/methods/datasets/formats heads.
- After D/E commit, generated `/tmp/n4a-w2l.lock.json` and replaced
  `docs/contracts/release/aggregation-lock.n4a.lock.json`.
- Final selected pins in the checked-in lock:
  `dag_ml=618ffb220b5f`, `dag_ml_data=818616e9a2c2`, `io=e52eecd827a0`,
  `lite=922fdd114231`, `methods=469124855ff1`, `datasets=ac455f321144`,
  `formats=89231b2786ef`.
- Validation against selected root:
  `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-w2k-root validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> passed.
- `pytest -q tests/test_release_lock.py` -> 5 passed.

Cutover-gate follow-up:

- The full `n4a_cutover_gates.py run` was interrupted after it spent over 25
  minutes in `pyref_oracle_full`; reserve that full parity gate for larger
  integration batches.
- `n4a_cutover_gates.py run --skip pyref_oracle_full` passed all selected gates
  except `release_lock_validation` before the Web gate fix. The Web failure was
  a bad gate cwd, not a Web runtime failure.
- Fixed `docs/contracts/cutover/drop-gates.n4a.json` so
  `web_runtime_contract` runs from `_worktrees/INT-web/studio-lite`; rerun of
  `--gate web_runtime_contract` passed.
- Follow-up after the post-reset audit: `release_lock_validation` now supports a
  separate selected member root via `N4A_RELEASE_WORKSPACE_ROOT`, while keeping
  `nirs4all-ecosystem` as the gate cwd. The local durable selected root is
  `/home/delete/nirs4all/_release_roots/W2L-selected`, symlinked to the clean
  release member heads. `N4A_RELEASE_WORKSPACE_ROOT=/home/delete/nirs4all/_release_roots/W2L-selected python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --gate release_lock_validation --json`
  -> passed.
- Current-root lock regeneration remains intentionally disallowed: primary
  checkouts are still reset/stale for several surfaces and `dag-ml-data/` still
  contains a dirty generated `_dag_ml_data.abi3.so`.
- Non-full-parity cutover batch passed after the gate fix:
  `N4A_RELEASE_WORKSPACE_ROOT=/home/delete/nirs4all/_release_roots/W2L-selected python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --skip pyref_oracle_full --json`
  -> passed. This reran contract self-check, post-W2J state, coverage zero,
  native `.n4a` export, Studio runtime routes, Web runtime contract, dag-ml
  lockstep, dag-ml-data lockstep, migration smoke, and release-lock validation.
  Full parity was intentionally not rerun in this small follow-up.

### Lane H - Studio/Web Runtime

Status: complete, no code changes.

Key result: current `nirs4all-studio/main` and `nirs4all-web/main` lack W95/W96/W102
runtime fixes. The diff to `INT-studio` is 76 files and to `INT-web` is 27 files,
so a partial port is too risky. Integrate from the reviewed `INT-*` heads or do
a dedicated full port/review, not cherry-pick fragments.

Focused gates on current reset checkouts:

- Studio backend `tests/test_runs_execution_backend.py` -> 37 passed.
- Studio Vitest targeted launch flow/builders -> 21 passed.
- Web `npm run typecheck` -> passed.
- Web `npm run test` -> 90 passed.

### Lane I/J - Cluster/Providers/Repository/Benchmarks/Papers

Status: complete, no code changes.

Key result: current `nirs4all-cluster/main` and `nirs4all-providers/main` are
clean but behind their reviewed integration heads. W88 cluster and W80/W89
provider work exists in `_worktrees/INT-cluster` and `_worktrees/INT-providers`;
do not treat current `main` as final V1 evidence for those surfaces.

Focused gates:

- `nirs4all-cluster`: `uv run --extra dev pytest tests/test_scheduler.py tests/test_server_api.py -q` -> 39 passed, 1 warning.
- `nirs4all-providers`: `PYTHONPATH=src python3.11 -m pytest -q` -> passed.

### Lane D/E - Tools/Lite Namespaces

Status: complete, one bounded code change in `nirs4all-lite`.

Key result: `nirs4all-tools` W97/W104 goldens are present and realistic after
reset. `nirs4all-lite` needed a small lint-safe facade fix so
`nirs4all_core.__all__` mirrors `nirs4all_lite` dynamically through the
`CORE_FACADE_EXPORTS + TOPOLOGY_EXPORTS` contract.

Code changed and committed:

- `nirs4all-lite/bindings/python/src/nirs4all_core/__init__.py`
- commit `922fdd114231` (`fix(python): mirror core facade exports dynamically`)

Agent gates passed:

- Tools: focused goldens, CLI tests, full pytest 83 tests, Ruff, mypy, CLI
  `--version`, `inspect`, and `migrate --dry-run`.
- Lite: release topology 8 tests, Python suite 34 tests, Ruff, py_compile,
  version sync, Rust tests, Python make gate, npm/WASM 12 tests.
- R/Octave not run: binaries unavailable.

Coordinator rerun:

- `PYTHONPATH=bindings/python/src python3.11 -m ruff check bindings/python/src/nirs4all_core/__init__.py bindings/python/tests/test_release_topology.py` -> passed.
- `PYTHONPATH=bindings/python/src python3.11 -m unittest bindings/python/tests/test_release_topology.py -v` -> 8 passed.
- `nirs4all_core.validate_core_facade(nirs4all_core)` -> no missing core exports and no unexpected execution exports.

### Lane B/C/F - Parity/Runtime/Methods

Status: complete, bounded `nirs4all` diff retained only for source-concat
native promotion.

Key result: initial dirty diff was partly unsafe. `multi_source_sources_concat_then_rf`
passed native parity and remains promoted. `multi_source_per_source_models_stacking`
failed parity as native (`rmse` delta `4.770e-02` > `1e-03`) and remains an
explicit fallback.

Code changed in current `nirs4all/refactor/L17-pyref` checkout and committed:

- `docs/compatibility.json`
- `nirs4all/pipeline/dagml/detect.py`
- `nirs4all/pipeline/dagml/run_backend.py`
- `nirs4all/pipeline/dagml/run_paths.py`
- `tests/integration/parity/test_conformance_dual_engine.py`
- commit `13157d79d378` (`fix(dagml): run source concat merge natively`)

Agent gates passed:

- source concat targeted conformance -> passed.
- by-source stacking remains fallback -> targeted checks passed.
- compatibility ledger -> 2 passed.
- Ruff, mypy, `git diff --check` -> passed.

Coordinator rerun:

- `test_conformance_dual_engine.py -k 'multi_source_sources_concat_then_rf or multi_source_per_source_models_stacking'` -> 4 passed, 4 warnings.
- `test_compatibility_ledger.py` -> 2 passed.
- Ruff touched files -> passed.
- Mypy touched dagml files -> passed.
- `git diff --check` -> passed.

Limit: `test_native_fallback_boundary.py` is absent from this older branch; run
that gate on `_worktrees/INT-nirs4all` or the final selected integration root.

## Post-Reminder Preexisting State Audit

Triggered by the user reminder that the previous conversation had context about
old non-merged Claude/agent work.

Read-only Codex subagents audited branches, worktrees, reports, and `/tmp`
artifacts. No Claude tools were used.

Current authoritative evidence:

- tracked release manifest and lock in `nirs4all-ecosystem/docs/contracts/release/`;
- tracked cutover gate manifest and readiness matrix in
  `nirs4all-ecosystem/docs/contracts/cutover/`;
- W2L post-reset board plus this follow-up;
- W98 historical full parity log `/tmp/w98_full_parity.log`:
  `804 passed, 32 skipped, 11 xfailed` in `1885.90s`.

Stale or lower-authority evidence:

- `/tmp/n4a-current.lock.json` and `/tmp/n4a_release_lock_probe.json` pin
  current dirty/stale checkouts and are not release evidence;
- `/tmp/n4a-w2k.lock.json` is valid but stale because it predates the W2L lite
  fix (`lite=0486e1fc255f`);
- `/tmp/n4a-readiness-main.json`, `/tmp/n4a-readiness-json.txt`, and
  `/tmp/n4a-cutover-list.json` predate later tracked contract fixes;
- `W2L_LANE_K_FINAL_REVIEW.md` is useful historical review but predates later
  W2L commits and the release-lock gate fix.

Preexisting Git state classification:

- `dag-ml-data/refactor/L20-lockstep@2214f75aa3c7` remains dirty only because of
  generated `_dag_ml_data.abi3.so`; do not commit or discard it without an
  explicit controlled decision.
- `nirs4all/.claude/worktrees/agent-a5af0970d430760ab` is an old Claude
  worktree. Its branch head is already an ancestor of the integration head, but
  it has untracked parity/conformance tests. Do not merge those files; they are
  stale against W98.
- `nirs4all/refactor/L17-pyref@13157d79d378` is clean but not the selected final
  core head. Its source-concat native work is already superseded/subsumed by
  `_worktrees/INT-nirs4all@17ed929eeb77`, where `EXPECTED_FALLBACK` is empty and
  `docs/compatibility.json` records `fallback=0`, `native=87`.
- Non-ancestor W/L branches in `nirs4all`, Studio, Web, cluster, providers, and
  lite should be kept for review rather than bulk-deleted. Inspection indicates
  several are intermediate patch-equivalent states superseded by integration
  commits, but they are not safe cleanup targets without an explicit pruning
  pass.
- `nirs4all-tools` W78/W84 are superseded by `main@9dc0c628c97d`: `git log
  --left-right --cherry-pick main...refactor/W78-migration-complete` and the
  W84 equivalent show only newer main-side commits.

## Primary Checkout Alignment Batch

After the selected-root gate fix, four clean primary `main` checkouts were
fast-forwarded to their reviewed integration heads:

| Repo | Previous primary head | New primary head | Integration head | Result |
| --- | ---: | ---: | ---: | --- |
| `nirs4all-studio` | `2ccbf68e03a7` | `83aab1c18108` | `83aab1c18108` | fast-forward, clean |
| `nirs4all-web` | `745eef89406e` | `ee8ea7a95946` | `ee8ea7a95946` | fast-forward, clean |
| `nirs4all-cluster` | `dcced303543e` | `eac4d0b8a62a` | `eac4d0b8a62a` | fast-forward, clean |
| `nirs4all-providers` | `3ecc67915786` | `1e289a9ee96d` | `1e289a9ee96d` | fast-forward, clean |

Review notes:

- Codex read-only reviewers confirmed these were pure fast-forwards with no
  main-only commits lost.
- Remotes were not pushed in this wave.
- `nirs4all-io`, `dag-ml`, and `dag-ml-data` are also ancestors of selected
  integration heads, but they are on refactor branches. `dag-ml-data` remains
  dirty because of the generated `_dag_ml_data.abi3.so`, so it needs a separate
  controlled decision.

Post-fast-forward targeted gates on primary checkouts:

- `nirs4all-studio`: runtime-route pytest selection -> 82 passed, 2 warnings;
  compileall API and Ruff -> passed.
- `nirs4all-web/studio-lite`: typecheck -> passed; `dagml-engine.rt-fallback`
  Vitest -> 6 passed; `npm run build`, `npm run build:single`, and
  `node scripts/run-smokes.mjs rt-fallback` -> passed.
- `nirs4all-cluster`: `uv run --extra dev pytest tests/test_scheduler.py
  tests/test_server_api.py -q` -> 42 passed, 1 warning.
- `nirs4all-providers`: `PYTHONPATH=src python3.11 -m pytest -q` -> 65
  collected with 61 passed and 4 skipped.

Second alignment slice:

| Repo | Previous primary head | New primary head | Integration head | Result |
| --- | ---: | ---: | ---: | --- |
| `dag-ml` | `4f0a3b5a7a96` | `618ffb220b5f` | `618ffb220b5f` | fast-forward, clean |
| `nirs4all-io` | `5651da51fe74` | `e52eecd827a0` | `e52eecd827a0` | fast-forward, clean |

Post-fast-forward targeted gates:

- `dag-ml`: `cargo fmt --all --check`; `cargo clippy -p dag-ml-core -p
  dag-ml-cli --all-targets -- -D warnings`; `cargo test -p dag-ml-core` ->
  446 passed, 2 ignored; `DAG_ML_DATA_REPO=/home/delete/nirs4all/_worktrees/INT-dmd
  python3 scripts/validate_contracts.py` -> passed.
- `nirs4all-io`: `PYTHONPATH=src /home/delete/miniconda3/bin/python -m pytest
  -q tests/test_dataset_package.py` -> 4 passed; `cargo test -p
  nirs4all-io-core --lib` -> 93 passed.
- A first `nirs4all-io` Python test attempt with `python3.11` failed at import
  because that interpreter lacks `numpy`; a second attempt with `python3` failed
  because it is Python 3.10 and lacks `StrEnum`. These were environment
  selection issues, not test failures against the code.

Not aligned:

- `dag-ml-data` remains on `refactor/L20-lockstep@2214f75aa3c7` with the
  preexisting dirty generated `_dag_ml_data.abi3.so`. The selected clean release
  proof continues to use `_worktrees/INT-dmd@818616e9a2c2`.
- `nirs4all` primary remains on `refactor/L17-pyref@13157d79d378`; it is not a
  fast-forward to `_worktrees/INT-nirs4all@17ed929eeb77`.

Final short checks after this alignment batch:

- `python3 scripts/n4a_cutover_gates.py validate --workspace-root
  /home/delete/nirs4all` -> passed.
- `python3 scripts/n4a_cutover_gates.py post-w2j-state --workspace-root
  /home/delete/nirs4all` -> passed.
- `N4A_RELEASE_WORKSPACE_ROOT=/home/delete/nirs4all/_release_roots/W2L-selected
  python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all
  --gate release_lock_validation --json` -> passed.

Full parity was not rerun in this follow-up per the user instruction to reserve
it for large integration batches. The current full-parity evidence remains W98:
`804 passed, 32 skipped, 11 xfailed` from `/tmp/w98_full_parity.log`.
