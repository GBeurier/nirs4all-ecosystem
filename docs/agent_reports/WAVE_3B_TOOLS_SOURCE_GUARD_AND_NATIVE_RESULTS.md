# Wave 3B - Tools Source Guard and Native Results Converter

Date: 2026-07-01T18:02:13+02:00

## Scope

Lane D focused batch in `nirs4all-tools`:

- tighten the offline/no-in-place source integrity guard;
- align native-results optional array lowering with runtime workspace-v2 sidecars;
- refuse native-results `y_true`/`y_pred` shapes that workspace-v2 cannot reconstruct;
- keep non-lowerable native payloads on the existing best-effort opaque preservation path.

No full parity run in this batch. Per user instruction, full parity gates stay deferred until larger integrated batches.

## Roadmap Coverage Note

The current roadmap and public V1 surface matrix already include the three public `nirs4all` surfaces:

- `nirs4all.python.oracle`
- `nirs4all.r.aggregate`
- `nirs4all.browser_wasm.aggregate`

Verified in `docs/PARALLEL_REFACTORING_ROADMAP.md` and `docs/contracts/release/public-v1-surface-matrix.n4a.json`. W3B does not alter release topology.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Dirac | `nirs4all-tools` no-in-place policy | done | Read-only. Found source snapshots used only size+mtime and could miss same-size byte changes with restored mtime. |
| Dalton | Python runtime workspace/native-results contracts vs tools | done | Read-only. Confirmed workspace-v2 DDL/sidecars are aligned; found native optional empty arrays and multi-dimensional shape risks. |
| Arendt | Studio migration/workspace surfaces vs tools contracts | done | Read-only. Confirmed Studio migration is an in-place internal arrays migration, not the offline `nirs4all-tools` flow; proposed future read-only report preview surface. |
| Copernicus | W3B reviewer | done | Found blocking issue after the first patch: multi-dimensional native-results refusal happened too late and bypassed best-effort opaque preservation. Fixed by moving the check into native preview validation and adding command-path tests. Follow-up review: no blocking findings. |

## Decisions

- Make `TreeSnapshot` signatures include SHA-256 content hashes, not only `(size, mtime_ns)`.
- Reuse snapshot hashes in the source fingerprint instead of recomputing them from a second tree walk.
- Preserve runtime semantics for optional native array fields: empty `y_proba`, `y_proba_shape`, `sample_indices`, and `weights` lower to `None`.
- Treat native `y_true_shape`/`y_pred_shape` with more than one dimension as non-lowerable for workspace-v2 sidecars.
- Validate non-lowerable native shapes in `load_native_results_preview()` so dry-run, strict migration, and non-strict opaque preservation share the same decision.
- Do not add Studio report-preview UI/API in W3B; keep this as a future lane because it crosses into Studio product surface.

## Files Changed

`nirs4all-tools`:

- `src/nirs4all_tools/policy.py`
- `src/nirs4all_tools/commands.py`
- `src/nirs4all_tools/native_results.py`
- `tests/test_policy.py`
- `tests/test_commands.py`
- `tests/test_native_results.py`

## Gates

- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_policy.py tests/test_native_results.py tests/test_commands.py tests/test_real_golden_fixtures.py` - 62 passed, 1 unrelated `pytz` deprecation warning.
- `ruff check src/nirs4all_tools/policy.py src/nirs4all_tools/commands.py src/nirs4all_tools/native_results.py tests/test_policy.py tests/test_commands.py tests/test_native_results.py` - passed.
- `python3 -m py_compile src/nirs4all_tools/policy.py src/nirs4all_tools/commands.py src/nirs4all_tools/native_results.py tests/test_policy.py tests/test_commands.py tests/test_native_results.py` - passed.
- `git diff --check` - passed.
- `python3 scripts/n4a_release_surface_matrix.py validate` in `nirs4all-ecosystem` - passed.

## Risks

- Full Python-reference parity was not run in W3B.
- Native-results lowering remains intentionally limited: model artifacts are preserved opaque and are not replay/export proof.
- Studio still has no read-only preview for `legacy_migration_report.v1`; users must link a converted workspace explicitly after running `nirs4all-tools`.
