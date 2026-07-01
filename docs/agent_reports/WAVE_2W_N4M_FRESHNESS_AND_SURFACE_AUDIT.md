# Wave 2W N4M Freshness and Surface Audit

Date: 2026-07-01T16:45:00+02:00

## Scope

Follow-up after W2V. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2W closes a small, targeted release/parity gap without running the long
`pyref_oracle_full` gate:

- Add a consumer-side `nirs4all` proof that the `libn4m` loaded from the proof
  venv is exactly the library staged into the freshly built `nirs4all-methods`
  wheel.
- Keep source-to-binary build freshness responsibility in `nirs4all-methods`;
  `nirs4all` must not duplicate the native engine's build graph.
- Re-check that the release roadmap and lock surfaces include `nirs4all` Python,
  R, and WASM.
- Audit the remaining Studio-oracle gap read-only for the next batch.

## Starting State

- Ecosystem head: `4fa4c36`.
- `_worktrees/INT-nirs4all` head: `7ab1ec1e`.
- `nirs4all-lite` head: `272e07f`.
- W2U/W2V found Claude-era artifacts and old worktrees superseded; do not merge
  or copy them.

## Integrated Commits

- `_worktrees/INT-nirs4all`: `122ef5d1 test(methods): prove installed n4m artifact freshness`
- `nirs4all-ecosystem`: this report is committed in the current ecosystem head.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| C/F | coordinator | `_worktrees/INT-nirs4all` only | Done: added the installed-`n4m` wheel/lib freshness proof, unit tests, and compatibility ledger update. |
| H/K | Volta `019f1e12-2038-7511-855b-d8b76b09c657` | read-only `_worktrees/INT-studio`, `_worktrees/INT-nirs4all`, ecosystem reports | Done: audited the Studio-oracle gap and produced a next-batch plan; no edits. |
| A/E/K | Ramanujan `019f1e12-3743-7cc2-9e50-8a6e78bff3f2` | read-only `nirs4all-ecosystem`, `nirs4all-lite`, release matrix/lock | Done: verified release topology includes `nirs4all` Python/R/WASM surfaces; no edits. |
| K | Sagan `019f1e14-a147-7ad2-bab2-ccfb0239d3b1` | read-only W2W diffs after implementation | Done: reviewed W2W diff; GO after minor ledger/test corrections. |

## Gates

Planned targeted gates only:

- `python3.11 -m pytest tests/unit/operators/methods/test_installed_n4m_proof.py -q`
- `python3.11 scripts/prove_installed_n4m.py`
- `python3 -m pytest tests/test_release_surface_matrix.py tests/test_release_lock.py tests/test_cutover_state_gate.py -q`
- `python3 scripts/n4a_release_surface_matrix.py validate`

`pyref_oracle_full` is intentionally deferred until a larger batch.

## Integration Log

### 2026-07-01T17:20:00+02:00

Coordinator implemented the C/F patch in `_worktrees/INT-nirs4all`:

- `scripts/prove_installed_n4m.py`
  - Adds SHA-256 verification for the `libn4m` binary reported by the
    `nirs4all-methods` smoke.
  - Verifies identity across the source library, the staged package library, the
    wheel payload under `n4m/lib`, the smoke-installed library, and the proof
    venv loaded library.
  - Emits `artifact_freshness.status = N4M_WHEEL_ARTIFACT_FRESH`.
- `tests/unit/operators/methods/test_installed_n4m_proof.py`
  - Adds synthetic wheel/hash tests for the success path and mismatch failures:
    missing bundled library, stale wheel payload, stale staged library, stale
    proof library, and stale methods-smoke installed library.
- `docs/compatibility.md` / `docs/compatibility.json`
  - Moves `methods_installed` from partial to exists.
  - Records `nirs4all_methods_artifact_freshness` as the consumer-side
    PYREF-011 proof.
  - Keeps source-to-binary build freshness owned by `nirs4all-methods`.

Sagan review:

- No high/medium findings.
- Low finding fixed: machine-readable ledger now includes both
  `kernel_snv` and `kernel_pls` via `tolerance_bands` while retaining the
  historic `tolerance_band` field.
- Suggested negative tests were added.

Ramanujan surface audit:

- Roadmap, public V1 surface matrix, manifest, lock, and lite topology all
  include the requested `nirs4all` surfaces:
  - `nirs4all.python.oracle`
  - `nirs4all.r.aggregate`
  - `nirs4all.browser_wasm.aggregate`
  - scoped WASM providers for methods and datasets.
- `python3 scripts/n4a_release_surface_matrix.py validate` passed.
- `python3 scripts/n4a_release_surface_matrix.py report` confirmed the surfaces.
- `python3 -m pytest tests/test_release_surface_matrix.py tests/test_release_lock.py -q` passed.
- `PYTHONPATH=bindings/python/src python3.11 -m unittest bindings/python/tests/test_release_topology.py -v` passed in `nirs4all-lite`.
- Strict lock validation against the raw workspace remains stale/inconsistent;
  this does not contradict the selected-root release gate.

Volta Studio audit:

- `api/runs.py` is no longer the primary gap: it passes/records engine,
  diagnostics, fallback policy, runtime manifest, and native refs.
- Remaining no-engine routes for a future batch:
  - `_worktrees/INT-studio/api/training.py`
  - `_worktrees/INT-studio/api/automl.py`
  - `_worktrees/INT-studio/api/pipelines.py`
- Recommended next patch: add a shared `run_with_runtime_record` helper (or
  equivalent) and migrate only those three routes first, with backend tests that
  assert `engine`, `allow_fallback=False`, diagnostics/refusals, and recording.
- Secondary bypasses to treat later: `predictions.py` / `models.py` metrics,
  then `transfer.py`.

Targeted coordinator gates:

- `python3.11 -m ruff check scripts/prove_installed_n4m.py tests/unit/operators/methods/test_installed_n4m_proof.py` passed.
- `python3.11 -m pytest tests/unit/operators/methods/test_installed_n4m_proof.py -q` passed: 14 tests.
- `python3.11 -m json.tool docs/compatibility.json` passed.
- `python3.11 -m py_compile scripts/prove_installed_n4m.py` passed.
- `python3.11 scripts/prove_installed_n4m.py` passed.
- `timeout 1800 python3.11 scripts/prove_installed_n4m.py --install-deps --dag-ml-path /home/delete/nirs4all/dag-ml --dag-ml-data-path /home/delete/nirs4all/dag-ml-data` passed.
- Ecosystem release surface matrix validation passed.
- Ecosystem release lock/unit tests passed: 13 tests.
- Selected-root release lock validation passed.
- `python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --gate installed_n4m_proof --skip pyref_oracle_full --timeout 2400 --json` passed:
  - gate `installed_n4m_proof`
  - duration `59.154s`
  - `artifact_freshness.status = N4M_WHEEL_ARTIFACT_FRESH`
  - `input_lib_sha256 = proof_library_sha256 = 78f8e0f0abcf19c4ccfa069e425c6fe56e49fab78c681e6111e17e1369afe9a2`

`pyref_oracle_full` was not run.
