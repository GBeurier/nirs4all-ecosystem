# Wave 2R Methods Providers Cluster Proofs

Date: 2026-07-01T15:25:07+02:00

## Scope

Follow-up after W2Q. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2Q produced three useful diagnostics but not all release proofs:

- `nirs4all` can now report installed `n4m` binding status, but the local
  `INT-nirs4all` environment lacks `n4m`, so installed-binding parity is not
  green there.
- `nirs4all-providers` now has a strict release gate, but the local providers
  environment lacks the four sibling extras, so the gate correctly reports
  missing backings.
- Cluster has a release e2e scheduler proof, but the long-running worker agent
  loop remains outside that test.

The public V1 surface matrix must continue to include `nirs4all` Python, R, and
browser/WASM surfaces:

- `nirs4all.python.oracle`
- `nirs4all.r.aggregate`
- `nirs4all.browser_wasm.aggregate`
- `nirs4all.browser_wasm.methods_scoped`
- `nirs4all.browser_wasm.datasets_scoped`

Full Python-reference parity remains deferred until a large enough core/native
batch or final `LOCK-DROP` proof. W2R targets repeatable proof harnesses and
gaps; it must not claim full parity unless that long gate is explicitly run.

## Starting State

- W2Q integrated:
  - `nirs4all-ecosystem` `c13e7ba`
  - `_worktrees/INT-nirs4all` `27da2c80`
  - `_worktrees/INT-cluster` `2da60953`
  - `_worktrees/INT-providers` `7a9839b5`
- The selected release root validates the aggregation lock.
- The final W2Q non-full cutover gate passed with `pyref_oracle_full` skipped.
- Historical `W*` worktrees and Claude-era trees remain audit inputs only, not
  merge sources.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| C/F | pending | `_worktrees/INT-nirs4all` only, read `nirs4all-methods` | Build a repeatable installed-`n4m` proof path for `nirs4all` or report a precise blocker; do not move numerical logic into Python. |
| J/G | pending | `_worktrees/INT-providers` only, read sibling provider repos | Make the providers release gate runnable against local sibling packages or document the exact packaging blockers without weakening the gate. |
| I | pending | `_worktrees/INT-cluster` only | Add a bounded worker-agent loop proof or document the minimal blocker; keep cluster as scheduler/client/server, not core logic. |
| K | pending | `nirs4all-ecosystem` docs/scripts only | Final W2R reviewer after lanes finish; do not code until C/F, J/G, and I are ready for audit. |

## Review Criteria

- Agents must read local `AGENTS.md` / `CLAUDE.md` before editing.
- No agent may touch `nirs4all-drafts` or `nirs4all-lab`.
- No agent may merge or cherry-pick historical `W*` worktrees without fresh
  diff audit and coordinator review.
- Any pipeline, prediction, runtime, binding, or provider-execution change must
  preserve or test parity against the current Python `nirs4all` oracle.
- No tests may be weakened, hidden behind silent passes, xfailed, or skipped to
  manufacture green status. Optional missing dependencies must be explicit
  diagnostics, and strict release modes must fail when proof prerequisites are
  missing.
- R unavailable locally is a risk, not a release proof.

## Expected Gates

- Targeted tests per changed repo.
- Providers gate must either pass with real local siblings or fail with a precise
  blocker that can be acted on.
- Installed `n4m` proof must either pass in a reproducible harness or fail with
  a precise environment/package blocker.
- Cluster worker-agent proof must be bounded and deterministic.
- Release lock regeneration only if a lock member commit changes.
- Non-full cutover gate after integration.
- No full `pyref_oracle_full` unless the coordinator explicitly decides the
  accumulated changes justify the long run.

## Integration Log

### Lane I - Cluster bounded WorkerAgent loop proof

- Agent: Zeno `019f1ddb-fcfd-7d21-be1b-a4f8970950f0`.
- Integrated commit in `_worktrees/INT-cluster`:
  `c710f54 test(cluster): prove worker agent loop completion`.
- Files changed:
  - `tests/test_distributed_parity.py`
- Review:
  - Added a bounded test around the real `WorkerAgent.serve()` lease loop,
    using the existing loopback cluster fixture and fake subprocess-visible
    `nirs4all` module.
  - The test covers register, lease, execute, result upload, job completion,
    provenance, artifact link, and task workspace cleanup.
  - Cluster architecture boundary remains intact: only
    `nirs4all_cluster/runners/nirs4all_run.py` imports real `nirs4all`.
- Validation:
  - `uv run pytest tests/test_distributed_parity.py::test_worker_agent_loop_runs_one_fake_job_to_completion -q -rA`
  - `uv run pytest tests/test_worker.py tests/test_distributed_parity.py -q -rA`
  - `uv run ruff check .`
  - `uv run mypy nirs4all_cluster`
  - `uv run pytest -q -rA` (`135 passed, 1 skipped`)
  - `rg -n "^[[:space:]]*(import nirs4all|from nirs4all)" nirs4all_cluster -g '*.py'`

### Lane C/F - nirs4all installed n4m proof

- Agent: Archimedes `019f1ddb-9b65-72d1-8e94-0fc1086ae543`.
- Integrated commit in `_worktrees/INT-nirs4all`:
  `d092085 test(methods): add installed n4m proof harness`.
- Files changed:
  - `scripts/prove_installed_n4m.py`
  - `tests/unit/operators/methods/test_installed_n4m_proof.py`
- Review:
  - The proof builds a real local `nirs4all-methods` wheel from the sibling
    `nirs4all-methods` checkout using its installed-wheel smoke.
  - It installs that wheel into a temporary proof venv and verifies that
    `nirs4all.operators.methods` consumes `n4m` plus `libn4m` from the installed
    proof venv, not from `PYTHONPATH`, `N4M_LIB_PATH`, or `PLS4ALL_LIB_PATH`.
  - The proof is a packaging/loadability and focused SNV/PLS consumption proof,
    not a full Python-reference parity run.
- Validation:
  - `python3.11 scripts/prove_installed_n4m.py`
    (passed; reported `NIRS4ALL_INSTALLED_N4M_OK`, ABI `2.0.0`, and installed
    `n4m/lib/libn4m.so.2.0.0` under the proof venv)
  - `python3.11 -m pytest tests/unit/operators/methods/test_installed_n4m_proof.py -q -rA`
    (`5 passed`)
  - `python3.11 -m pytest tests/unit/operators/methods -q -rA`
    (`6 passed, 11 skipped`; skips remain explicit for the ambient env without
    `n4m`)
  - `python3.11 -m py_compile scripts/prove_installed_n4m.py tests/unit/operators/methods/test_installed_n4m_proof.py`
  - `python3.11 -m ruff check .`
  - `python3.11 -m mypy nirs4all`
  - `git diff --check`
- Remaining risk:
  - `python3.11 scripts/prove_installed_n4m.py --install-deps` fails in a fully
    isolated install because the configured package indexes cannot resolve
    `dag-ml>=0.2.1`. The default proof therefore uses system site packages plus
    `--no-deps` for the `nirs4all` checkout, while still proving that `n4m` and
    `libn4m` come from the installed wheel.

### Lane J/G - providers local sibling gate

- Agent: Harvey `019f1ddb-cd6f-72a3-a34a-f6fdc574ef2c`.
- Integrated commit in `_worktrees/INT-providers`:
  `54330e9 test(providers): add local sibling release gate harness`.
- Files changed:
  - `src/nirs4all_providers/local_release_gate.py`
  - `tests/test_local_release_gate.py`
  - `pyproject.toml`
  - `README.md`
- Review:
  - Added `python -m nirs4all_providers.local_release_gate` and the
    `nirs4all-providers-local-release-gate` console script.
  - The harness verifies local sibling source-package layouts, prepends only
    verified `src` paths, clears cached sibling modules, and delegates to the
    same strict release gate.
  - It does not fake packages, install dependencies, or weaken strict gate
    failures.
- Validation:
  - `.venv/bin/ruff check .`
  - `.venv/bin/mypy src`
  - `.venv/bin/pytest -q -rA` (`68 passed, 4 skipped`)
  - `.venv/bin/python -m nirs4all_providers.release_gate --json`
    (exit `2`, expected without local paths: all four sibling modules absent)
  - `.venv/bin/python -m nirs4all_providers.local_release_gate --workspace-root /home/delete/nirs4all --json`
    (exit `2`, expected: local sibling layouts pass, strict gate remains
    blocked by real import dependencies)
  - `git diff --check`
- Current blocker:
  - `nirs4all-datasets` local package import fails on missing `pydantic`.
  - `nirs4all-repository` local package import fails on missing `yaml`.
  - `nirs4all-benchmarks` and `nirs4all-papers` import via local sibling paths;
    `benchmarks` reports missing `arena.sqlite` as reachability detail, not the
    blocking release diagnostic.

## Final W2R Gates

- Release surface matrix:
  - `python3 scripts/n4a_release_surface_matrix.py validate`
  - `python3 -m pytest tests/test_release_surface_matrix.py tests/test_release_lock.py -q`
    (`9 passed`)
- Selected-root release lock:
  - `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_release_roots/W2L-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- Non-full cutover gate:
  - `N4A_RELEASE_WORKSPACE_ROOT=/home/delete/nirs4all/_release_roots/W2L-selected python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --skip pyref_oracle_full --json`
  - Final result: passed.
  - Confirmed post state includes:
    - `INT-nirs4all@d092085e`
    - `INT-cluster@c710f54e`
    - `INT-providers@54330e9d`
    - `INT-studio@17dfe69c`
    - `INT-web@ee8ea7a9`
  - Included gates: coverage fallback zero, native `.n4a` export parity subset
    (`19 passed`), Studio runtime routes (`82 passed, 2 warnings`), Web runtime
    contract and smoke, dag-ml lockstep (`446 passed, 2 ignored`), dag-ml-data
    lockstep (`206 passed, 2 ignored`), migration tool smoke, and release-lock
    validation.

Full Python-reference parity (`pyref_oracle_full`) was intentionally not run in
W2R. The wave adds proof harnesses and diagnostics, but does not by itself
constitute the next large numerical parity batch.
