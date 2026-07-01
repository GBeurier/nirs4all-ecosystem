# Wave 2S Proof Environment Closure

Date: 2026-07-01T15:40:14+02:00

## Scope

Follow-up after W2R. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2R added proof harnesses, but two proof-environment blockers remain:

- `nirs4all` installed-`n4m` proof is green in the default proof venv, but
  `--install-deps` cannot resolve `dag-ml>=0.2.1` from configured indexes.
- Providers local sibling gate verifies all four sibling package layouts, but
  strict import remains blocked in the INT providers venv by missing
  `pydantic` for `nirs4all-datasets` and `yaml` for `nirs4all-repository`.

W2S should improve reproducibility and diagnostics around these blockers. It
must not weaken strict gates or convert missing dependencies into green status.

The public V1 matrix must continue to include:

- `nirs4all.python.oracle`
- `nirs4all.r.aggregate`
- `nirs4all.browser_wasm.aggregate`
- `nirs4all.browser_wasm.methods_scoped`
- `nirs4all.browser_wasm.datasets_scoped`

Full Python-reference parity remains deferred. W2S must not run
`pyref_oracle_full` unless the coordinator explicitly decides otherwise.

## Starting State

- W2R integrated:
  - `nirs4all-ecosystem` `4b1bccf`
  - `_worktrees/INT-nirs4all` `d092085e`
  - `_worktrees/INT-providers` `54330e9d`
  - `_worktrees/INT-cluster` `c710f54e`
- The W2R non-full cutover gate passed with `pyref_oracle_full` skipped.
- Selected release root still validates the aggregation lock.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| C/F | Turing `019f1de9-5cb4-7811-be0c-7165ac04c87e` | `_worktrees/INT-nirs4all` only, read local `dag-ml`/`dag-ml-data` and `nirs4all-methods` | Done in `7ab1ec1e`: installed-`n4m` proof accepts explicit local dag-ml/dag-ml-data inputs and keeps bare resolver failure honest. |
| J/G | Laplace `019f1de9-8630-7282-8bbb-496ba0667121` | `_worktrees/INT-providers` only, read sibling provider repos | Done in `314c8681`: providers local sibling gate accepts explicit dependency paths and reports missing transitive modules/distributions. |
| K | coordinator | `nirs4all-ecosystem` docs/scripts only | Review W2S outcomes and update release accounting; no code changes outside the two lane worktrees. |

## Review Criteria

- Agents must read local instructions before editing.
- No old worktree or branch merges without fresh audit.
- No private repos touched.
- No strict gate weakening, xfail, or silent fallback.
- New proof commands must be bounded and reproducible on the current machine.
- Any dependency resolver change must be explicit and local; do not assume PyPI
  contains unreleased ecosystem packages.

## Expected Gates

- Targeted tests and ruff/mypy/py_compile per changed repo.
- Installed-`n4m` proof default mode remains green.
- Isolated mode either passes through local deps or emits a tighter actionable
  blocker.
- Providers gate either passes with real deps available or reports exact missing
  Python distributions/modules.
- Non-full cutover gate after integration.

## Integration Log

### 2026-07-01T15:52:09+02:00

Lane C/F (`_worktrees/INT-nirs4all`) completed and was reviewed.

- Commit: `7ab1ec1e95ccef3a3d568cf73e736c2260e643db`
  (`fix(proof): support local dag-ml dependency inputs`).
- Files modified:
  - `scripts/prove_installed_n4m.py`
  - `tests/unit/operators/methods/test_installed_n4m_proof.py`
- Decision: `--install-deps` now accepts explicit `--dag-ml-path`,
  `--dag-ml-data-path`, and repeated `--dependency-find-links` inputs. A local
  path must be a wheel, a Python project with the expected `project.name`, or a
  checkout root containing the expected Rust-backed Python project. No
  dependency success is faked.
- Review tests run by the coordinator:
  - `python3.11 scripts/prove_installed_n4m.py` passed.
  - `python3.11 scripts/prove_installed_n4m.py --install-deps --dag-ml-path /home/delete/nirs4all/dag-ml --dag-ml-data-path /home/delete/nirs4all/dag-ml-data` passed.
  - `python3.11 scripts/prove_installed_n4m.py --install-deps` failed as
    expected with `No matching distribution found for dag-ml>=0.2.1` and the
    new local-path diagnostic.
  - `python3.11 -m pytest tests/unit/operators/methods/test_installed_n4m_proof.py -q -rA` passed: 8 passed.
  - `ruff check .` passed.
  - `mypy nirs4all scripts/prove_installed_n4m.py` passed with existing
    informational notes.
  - `python3.11 -m py_compile scripts/prove_installed_n4m.py tests/unit/operators/methods/test_installed_n4m_proof.py` passed.
  - `git diff --check` passed; worktree clean.
- Risk: isolated local mode still depends on real local Rust-backed dag-ml build
  prerequisites. This is intentional and strict.

Lane J/G (`_worktrees/INT-providers`) completed and was reviewed.

- Commit: `314c8681959c205cebe72d03e756b5ef0018229f`
  (`fix(gate): diagnose local sibling dependencies`).
- Files modified:
  - `README.md`
  - `src/nirs4all_providers/local_release_gate.py`
  - `tests/test_local_release_gate.py`
- Decision: the local sibling gate now accepts repeated `--dependency-path`
  inputs and `NIRS4ALL_PROVIDERS_LOCAL_DEPENDENCY_PATHS`; venv roots resolve to
  `site-packages`, local sibling `src` paths stay ahead of dependency paths, and
  transitive import blockers report missing module plus matching pyproject
  requirement when available.
- Review tests run by the coordinator:
  - `./.venv/bin/python -m ruff check .` passed.
  - `./.venv/bin/python -m mypy src` passed.
  - `./.venv/bin/python -m pytest -q -rA` passed: 71 passed, 4 skipped.
  - `./.venv/bin/python -m nirs4all_providers.release_gate --json` failed as
    expected with all four backing modules absent from the providers venv.
  - `./.venv/bin/python -m nirs4all_providers.local_release_gate --workspace-root /home/delete/nirs4all --json` failed as expected with exact blockers:
    `pydantic>=2.0.0` for `nirs4all-datasets` and `pyyaml>=6.0`/`yaml` for
    `nirs4all-repository`.
  - `./.venv/bin/python -m nirs4all_providers.local_release_gate --workspace-root /home/delete/nirs4all --dependency-path /home/delete/nirs4all/nirs4all-datasets/.venv --dependency-path /home/delete/nirs4all/nirs4all-repository/.venv --json` passed.
  - `git diff --check` passed; worktree clean.
- Risk: dependency paths are explicit `sys.path` additions, so incompatible real
  environments still fail at import time. This preserves strict behavior.

`pyref_oracle_full` was not run for W2S because this wave only closes proof
environment reproducibility/diagnostics and does not change runtime numerical
behavior.

### 2026-07-01T15:54:34+02:00

Integration gates passed.

- `python3 scripts/n4a_release_surface_matrix.py validate` passed.
- `python3 scripts/n4a_release_surface_matrix.py report` passed and confirmed
  the required public `nirs4all` surfaces:
  - `nirs4all.python.oracle`
  - `nirs4all.r.aggregate`
  - `nirs4all.browser_wasm.aggregate`
  - `nirs4all.browser_wasm.methods_scoped`
  - `nirs4all.browser_wasm.datasets_scoped`
- `python3 -m pytest tests/test_release_surface_matrix.py tests/test_release_lock.py -q`
  passed: 9 passed.
- Selected release root lock validation passed:
  `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_release_roots/W2L-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`.
- Non-full cutover gate passed:
  `N4A_RELEASE_WORKSPACE_ROOT=/home/delete/nirs4all/_release_roots/W2L-selected python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --skip pyref_oracle_full --json`.
  The report returned `passed: true` with no required gate failures.

Cutover state selected the reviewed W2S heads:

- `_worktrees/INT-nirs4all` on
  `refactor/integration-nirs4all@7ab1ec1e`.
- `_worktrees/INT-providers` on
  `refactor/integration-providers@314c8681`.

`pyref_oracle_full` remains deferred until a larger numerical/runtime parity
batch, per the W2S scope and coordinator instruction.
