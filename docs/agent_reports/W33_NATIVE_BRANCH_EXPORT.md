# W33 report - native branch export

Summary:
W33 advanced native `.n4a` export for branch/fusion cases. Native `.n4a` bundles now preserve narrow multi-artifact duplication branch plus mean-fusion shapes by wrapping captured branch refit artifacts instead of falling back to the legacy export surface.

Code changed:
- Added native fusion bundle export support for supported branch refit artifacts.
- Extended native result bundle handling and API result export flow.
- Added bundle tests for the supported branch export shape.

Files touched:
- `nirs4all/api/result.py`
- `nirs4all/pipeline/dagml/native_results.py`
- `tests/integration/parity/test_dagml_native_n4a_bundle.py`

Commits:
- `nirs4all/refactor/W33-native-branch-export` `03fbc1c`
- Integrated into `nirs4all/refactor/integration-nirs4all` before final Wave-2E tip `e6299d52`

Tests run:
- `test_dagml_native_n4a_bundle.py` -> passed.
- `test_cross_engine_export_surface.py` -> passed.
- `test_conformance_n4a_cross_engine.py` -> passed.
- Combined post-merge target: `18 passed`.
- Targeted `py_compile` and Ruff -> passed.

Impact:
Advances `B-011` by moving native branch export away from bridge-only behavior for the supported fusion subset.

Next action:
Extend native export to stacking, by-source, and richer branch merge semantics after their native runtime paths are available.

Sync doc updated: yes
