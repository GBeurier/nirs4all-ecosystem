# W2L Lane B/C/F Parity Runtime Methods

Date: 2026-07-01

## Agent

Codex Lane B/C/F core-runtime-parity-methods post-reset.

## Lane

B/C/F: `nirs4all` parity/runtime audit against Python-reference parity, fallback accounting, by-source stacking, source concat, and methods/native boundary evidence.

## Files modified

- `nirs4all/docs/compatibility.json`
- `nirs4all/nirs4all/pipeline/dagml/detect.py`
- `nirs4all/nirs4all/pipeline/dagml/run_backend.py`
- `nirs4all/nirs4all/pipeline/dagml/run_paths.py`
- `nirs4all/tests/integration/parity/test_conformance_dual_engine.py`
- `nirs4all-ecosystem/docs/agent_reports/W2L_LANE_BCF_PARITY_RUNTIME_METHODS.md`

No edits were made to `dag-ml`, `dag-ml-data`, `nirs4all-methods`, `nirs4all-drafts`, or `nirs4all-lab`. The dirty generated `dag-ml-data` binary was not touched.

## Evidence

Audited the dirty `nirs4all` diff and compared it with `_worktrees/INT-nirs4all` plus W98 evidence. W98 established the strict parity gate and fallback diagnostics discipline; fallback passes are compatibility evidence, not native parity evidence.

Initial dirty diff was not safe as-is:

- `multi_source_sources_concat_then_rf` ran native and passed dual-engine parity.
- `multi_source_per_source_models_stacking` ran native but failed score parity: `rmse` delta `4.770e-02` over tolerance `1.000e-03`.
- The dirty ledger was inconsistent: the test removed both `source_concat` and `by_source` stacking from `EXPECTED_FALLBACK`, while `docs/compatibility.json` removed only the by-source entry and kept `fallback=9`.

Decision implemented:

- Kept the verified `source_concat` native path.
- Removed the incomplete `by_source_stacking` native route/helper from this checkout and kept `multi_source_per_source_models_stacking` as an explicit fallback.
- Updated compatibility accounting from `fallback=10/native=77` to `fallback=9/native=78`, with only `multi_source_sources_concat_then_rf` removed from fallback.

The integration worktree has a broader by-source stacking replay implementation, but it depends on wider projection/layout helpers and should be reviewed/integrated as a unit, not copied blindly into this reset checkout.

## Tests/gates run

- `pytest ...multi_source_per_source_models_stacking...` before fix: boundary passed, dual-engine failed with `rmse` delta `4.770e-02`.
- `pytest ...multi_source_sources_concat_then_rf...`: `2 passed`.
- `pytest test_native_fallback_boundary`: `87 passed`.
- `pytest tests/integration/parity/test_compatibility_ledger.py`: `2 passed`.
- Final targeted gate: source concat + by-source stacking boundary/conformance + compatibility ledger: `6 passed, 4 warnings`.
- `ruff check` on touched Python files: passed.
- `mypy` on touched Python files: passed.
- `git diff --check`: passed.

Warnings observed were existing Polars string-cache deprecation warnings from `index_store.py`.

## Risks

- `multi_source_per_source_models_stacking` remains fallback, not native. This is intentional: the dirty native implementation used ordinary OOF prediction stacking, while legacy behavior is source-layout replay.
- `_worktrees/INT-nirs4all` reports a fuller native-coverage state, but it includes many additional W72/W73/W74/W75/W98 changes beyond this dirty diff.
- No `nirs4all-methods`/`n4m` execution path was added; n4m remains outside the dag-ml runtime path for this lane.

## Decisions needed

- Decide whether to integrate the broader INT by-source stacking replay as a reviewed unit in a later lane, or keep it deferred until the full W2K integration review.
- Keep `EXPECTED_FALLBACK` non-empty before any `DEFAULT_ENGINE="dag-ml"` cutover; `fallback=9` is still a drop blocker.

## Recommended integration steps

1. Integrate this bounded `source_concat` promotion only.
2. Do not integrate the dirty by-source stacking native attempt from the reset checkout.
3. Review the INT by-source stacking replay separately with focused parity evidence before reducing fallback below 9.
4. Re-run the full parity gate before any global fallback-count or default-engine decision.
