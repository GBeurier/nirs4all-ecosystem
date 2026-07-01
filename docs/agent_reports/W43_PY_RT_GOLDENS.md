# W43 report - Python runtime goldens

Summary:
Added Python-side `RtResult`/`RtError` golden fixtures for B-018, aligned with the Web W37 runtime-envelope semantics: success envelopes have top-level `schema_version`, fallback envelopes carry explicit diagnostics, and serialized `RtError` payloads omit detail/schema-version fields.

Code changed:
- Added fixture-based parity coverage for deterministic Python `RunResult.to_rt_result()` success and legacy-fallback projections.
- Added `RtError` golden fixtures for scheduler fallback, strict scheduler refusal, and Python unsupported-shape fallback diagnostics.
- Added schema validation for all new runtime fixtures against the current ecosystem runtime schemas and dag-ml ScoreSet/selection schemas when sibling contracts are present.

Files touched:
- `tests/integration/parity/test_rt_goldens.py`
- `tests/integration/parity/fixtures/runtime/rt_result.success.v1.json`
- `tests/integration/parity/fixtures/runtime/rt_result.legacy_fallback.v1.json`
- `tests/integration/parity/fixtures/runtime/rt_error.scheduler_fallback.v1.json`
- `tests/integration/parity/fixtures/runtime/rt_error.strict_scheduler_refusal.v1.json`
- `tests/integration/parity/fixtures/runtime/rt_error.unsupported_shape.v1.json`

Commits:
- `nirs4all/refactor/W43-rt-goldens` `379ede0a` (`test(parity): add Python runtime goldens`)

Tests run:
- `/home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity/test_rt_goldens.py -q` -> 10 passed.
- `/home/delete/nirs4all/nirs4all/.venv/bin/python -m json.tool ...` for all new runtime JSON fixtures -> passed.
- `/home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity/test_rt_fallback_strict.py tests/integration/parity/test_compatibility_ledger.py -q` -> 10 passed.
- `/home/delete/nirs4all/nirs4all/.venv/bin/python -m py_compile nirs4all/pipeline/dagml/rt.py nirs4all/pipeline/dagml/result.py tests/integration/parity/test_rt_fallback_strict.py tests/integration/parity/test_rt_goldens.py` -> passed.
- `/home/delete/nirs4all/nirs4all/.venv/bin/ruff check nirs4all/pipeline/dagml/rt.py nirs4all/pipeline/dagml/result.py tests/integration/parity/test_rt_fallback_strict.py tests/integration/parity/test_rt_goldens.py` -> passed.

Tests not run and why:
- Full repository test suite not run; W43 scope requested targeted RT/parity gates.

Blockers:
- None.

Impact on blockers/locks:
- Advances B-018 by adding Python-consumable runtime fixture goldens that Studio/Web can compare against for `RtResult`/`RtError` drift.
- Does not change numerical parity, export behavior, runtime projection code, or fallback allowlists.

Next action:
- Have Web/Studio consumers load these Python fixtures alongside the existing Web W37 fixtures to enforce cross-runtime field drift checks.

Sync doc updated: no
