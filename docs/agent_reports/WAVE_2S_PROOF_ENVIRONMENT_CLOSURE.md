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
| C/F | pending | `_worktrees/INT-nirs4all` only, read local `dag-ml`/`dag-ml-data` and `nirs4all-methods` | Make the installed-`n4m` proof's isolated dependency mode actionable with local dag-ml inputs, or document the exact remaining package blocker in-machine. |
| J/G | pending | `_worktrees/INT-providers` only, read sibling provider repos | Make providers local sibling gate optionally run with local dependency paths/venv extras if already available, or sharpen dependency diagnostics without weakening strict gate. |
| K | pending | `nirs4all-ecosystem` docs/scripts only | Review W2S outcomes and update release accounting; do not code until C/F and J/G complete. |

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

Pending.
