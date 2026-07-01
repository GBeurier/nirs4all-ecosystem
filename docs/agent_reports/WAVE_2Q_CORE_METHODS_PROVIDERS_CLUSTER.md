# Wave 2Q Core Methods Providers Cluster

Date: 2026-07-01T15:00:45+02:00

## Scope

Follow-up after W2P. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

Full Python-reference parity remains deferred until a core/native behavior batch
or final `LOCK-DROP` proof. This wave targets smaller blockers that W2P left
explicit:

- `n4m` installed binding evidence exists in `nirs4all-methods`, but
  `nirs4all` still needs a targeted installed-methods proof or a clear remaining
  route blocker.
- Cluster has RBAC/client coverage but still lacks a release e2e proof.
- Providers/repo/benchmarks/papers now have a read-slice provider layer, but no
  end-to-end reproducible execution gate.
- W98 full parity remains the last full Python-reference proof; post-W2P needs a
  delta ledger before any release claim.

## Starting State

- W2P integrated:
  - `nirs4all-ecosystem` `021f33d`
  - `_worktrees/INT-io` `eae8263`
  - `nirs4all-methods` `00ca8467`
  - `_worktrees/INT-studio` `17dfe69`
- The selected release root validates the aggregation lock.
- The current workspace root still differs from selected-root for release-lock
  validation and must not be used as the proof root.
- Historical `W*` worktrees and the Claude-era `.claude/worktrees/agent-*` tree
  are audit inputs only. They are not merge sources for this wave.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| C/F | Helmholtz `019f1dc5-8e51-7db2-9a50-7c86d81f8818` | `_worktrees/INT-nirs4all` only | Add targeted proof around installed `n4m` methods binding consumption from `nirs4all`, without broad parity or duplicating methods logic. |
| I | Leibniz `019f1dc5-8ef3-7f22-8f4a-0dfad1309e3a` | `_worktrees/INT-cluster` only | Add or harden minimal cluster e2e proof for scheduler/client/server behavior under release boundaries. |
| J | Wegener `019f1dc5-8fed-7d81-8bbf-b52aecdff2d6` | `nirs4all-providers` only, read siblings | Turn provider read-slice status into a concrete conformance/release gate or a precise blocker report. |
| K | Cicero `019f1dc5-90ee-7781-ab37-a2639b3cb351` | `nirs4all-ecosystem` docs/scripts only | Publish a W98 -> post-W2P delta ledger without claiming full parity rerun. |

## Review Criteria

- Agents must read local `AGENTS.md` / `CLAUDE.md` for their touched repo before
  editing.
- No agent may touch `nirs4all-drafts` or `nirs4all-lab`.
- No agent may merge or cherry-pick historical `W*` worktrees without fresh
  diff audit and explicit review.
- Any pipeline, prediction, save/export, converter, runtime, or binding change
  must preserve or test parity with the current Python `nirs4all` oracle.
- No tests may be weakened, skipped, xfailed, or hidden behind fallbacks to make
  the wave green.
- R unavailable locally is a risk, not a green release proof.

## Expected Gates

- Targeted tests per changed repo.
- Release lock regeneration only if a lock member commit changes.
- Non-full cutover gate after integration.
- No full `pyref_oracle_full` in this wave unless the coordinator explicitly
  decides the accumulated core/native changes justify the long run.

## Integration Log

### Lane K - W98 to post-W2P delta ledger

- Agent: Cicero `019f1dc5-90ee-7781-ab37-a2639b3cb351`.
- Integrated commit: `c76d8a7 docs(release): add W98 post-W2P delta ledger`.
- Files changed:
  - `docs/agent_reports/W98_TO_POST_W2P_DELTA_LEDGER.md`
- Review:
  - The ledger explicitly keeps W98 as the last full Python-reference proof and
    lists post-W2P deltas without claiming a full parity rerun.
  - It retains the selected-root/current-root distinction for release-lock
    validation.
- Validation:
  - `git diff --check`
  - `python3 scripts/n4a_release_surface_matrix.py validate`

### Lane I - Cluster release e2e scheduler proof

- Agent: Leibniz `019f1dc5-8ef3-7f22-8f4a-0dfad1309e3a`.
- Integrated commit in `_worktrees/INT-cluster`:
  `2da6095 test(cluster): prove scheduler in release e2e`.
- Files changed:
  - `tests/test_distributed_parity.py`
- Review:
  - The existing live client/server e2e now submits a constrained job,
    rejects three ineligible workers, accepts an eligible worker, runs the
    subprocess executor path, and checks provenance plus aggregate result.
  - Package boundary remains intact: the only runtime `import nirs4all` inside
    package code is still the dedicated runner path.
- Validation:
  - `.venv/bin/python -m pytest -q tests/test_distributed_parity.py`
  - `.venv/bin/python -m ruff check tests/test_distributed_parity.py`
  - `.venv/bin/python -m pytest -q`
  - `.venv/bin/python -m ruff check .`
  - `.venv/bin/python -m mypy nirs4all_cluster`
  - `git diff --check`

### Lane C/F - nirs4all methods consumption proof

- Agent: Helmholtz `019f1dc5-8e51-7db2-9a50-7c86d81f8818`.
- Integrated commit in `_worktrees/INT-nirs4all`:
  `27da2c80 test(methods): prove n4m binding consumption diagnostics`.
- Files changed:
  - `nirs4all/operators/methods/n4m_ops.py`
  - `nirs4all/operators/methods/__init__.py`
  - `tests/unit/operators/methods/test_n4m_ops.py`
  - `tests/unit/pipeline/test_dagml_operator_routing.py`
- Review:
  - Added `methods_binding_status()` so `nirs4all` exposes a
    JSON-serializable installed-`n4m` diagnostic without importing or
    reimplementing methods numerical logic elsewhere.
  - `MethodsSNV` and `MethodsPLS` now raise the diagnostic when the binding is
    absent or not loadable, while importing the module remains safe.
  - Automatic `PLSRegression` -> `MethodsPLS` routing is intentionally not
    enabled; a new test locks the short alias to sklearn until a dedicated
    pipeline parity gate covers shape, scaling, folds, and native component
    selection.
  - Coordinator review amended the initial agent commit so unavailable-`n4m`
    parity/execution proofs are explicit skips instead of being counted as
    passed tests. The only local pass without `n4m` is the diagnostic proof.
- Validation:
  - `python3.11 -m pytest tests/unit/operators/methods/test_n4m_ops.py tests/unit/pipeline/test_dagml_operator_routing.py -q -rA`
    (`5 passed, 11 skipped`; skips are the explicit unavailable-`n4m` parity
    proofs)
  - `python3.11 -m ruff check .`
  - `python3.11 -m mypy nirs4all`
  - `python3.11 -m py_compile nirs4all/operators/methods/n4m_ops.py nirs4all/operators/methods/__init__.py tests/unit/operators/methods/test_n4m_ops.py tests/unit/pipeline/test_dagml_operator_routing.py`
  - `git diff --check`
  - `NIRS4ALL_REQUIRE_N4M=1 python3.11 -m pytest tests/unit/operators/methods/test_n4m_ops.py::TestPackaging::test_binding_status_consumes_installed_n4m_or_reports_blocker -q -rA`
    (expected local failure: `n4m` is not installed in this Python
    environment)
- Remaining risk:
  - Installed-binding parity is now a strict, runnable proof, but it was not
    green locally because `n4m` is absent from the `INT-nirs4all` environment.
    The W2P `nirs4all-methods` installed-wheel smoke remains the current proof
    that the wheel can load in its own environment.

### Lane J - Providers conformance/release gate

- Agent: Wegener `019f1dc5-8fed-7d81-8bbf-b52aecdff2d6`.
- Integrated commit in `nirs4all-providers` and fast-forwarded into
  `_worktrees/INT-providers`:
  `7a9839b test(providers): add release boundary gate`.
- Files changed:
  - `src/nirs4all_providers/release_gate.py`
  - `src/nirs4all_providers/registry.py`
  - `src/nirs4all_providers/__init__.py`
  - `tests/test_release_gate.py`
  - `tests/test_registry.py`
  - `pyproject.toml`
  - `README.md`
- Review:
  - Added `provider_capabilities()` so capability claims remain inspectable
    without optional siblings installed.
  - Added `nirs4all-providers-release-gate` and
    `python -m nirs4all_providers.release_gate --json`.
  - The gate fails if a provider claims runtime execution and fails if backing
    siblings are absent, converting skipped conformance into a release
    diagnostic instead of a false green.
  - The provider boundary remains serve / plan / export metadata only; no
    adapter imports or reimplements `nirs4all` execution.
- Validation:
  - `python3 -m ruff check .`
  - `python3.11 -m mypy src`
  - `PYTHONPATH=src python3.11 -m pytest -q -rA`
    (`66 passed, 4 skipped`; skips are the existing real-sibling conformance
    tests with absent optional extras)
  - `PYTHONPATH=src python3.11 -m nirs4all_providers.release_gate --json`
    (exit `2` expected locally; diagnostics list missing `datasets`,
    `repository`, `benchmarks`, and `papers` extras)
  - `git diff --check`
- Remaining risk:
  - This is a release boundary gate, not an execution reproducibility proof.
    Runtime execution remains owned by runtime-python/cluster/parity gates.

## Final W2Q Gates

- Release surface matrix:
  - `python3 scripts/n4a_release_surface_matrix.py validate`
  - `python3 -m pytest tests/test_release_surface_matrix.py tests/test_release_lock.py -q`
    (`9 passed`)
- Selected-root release lock:
  - `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_release_roots/W2L-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- Providers integration worktree:
  - `_worktrees/INT-providers` fast-forwarded from `1e289a9` to `7a9839b`.
  - `python3 -m ruff check .`
  - `python3.11 -m mypy src`
  - `PYTHONPATH=src python3.11 -m pytest -q -rA`
    (`66 passed, 4 skipped`)
  - `PYTHONPATH=src python3.11 -m nirs4all_providers.release_gate --json`
    (exit `2` expected locally; missing optional sibling extras are now a
    release diagnostic)
- Non-full cutover gate:
  - `N4A_RELEASE_WORKSPACE_ROOT=/home/delete/nirs4all/_release_roots/W2L-selected python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --skip pyref_oracle_full --json`
  - Final result: passed.
  - Confirmed post state includes:
    - `INT-nirs4all@27da2c80`
    - `INT-cluster@2da60953`
    - `INT-providers@7a9839b5`
    - `INT-studio@17dfe69c`
    - `INT-web@ee8ea7a9`
  - Included gates: coverage fallback zero, native `.n4a` export parity subset
    (`19 passed`), Studio runtime routes (`82 passed, 2 warnings`), Web runtime
    contract and smoke, dag-ml lockstep (`446 passed, 2 ignored`), dag-ml-data
    lockstep (`206 passed, 2 ignored`), migration tool smoke, and release-lock
    validation.

Full Python-reference parity (`pyref_oracle_full`) was intentionally not run in
W2Q; W98 remains the last full proof and the W98-to-post-W2P delta ledger stays
the active accounting document for this gap.
