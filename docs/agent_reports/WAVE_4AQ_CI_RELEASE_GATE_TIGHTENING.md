# Wave 4AQ - CI and Release Gate Tightening

Date: 2026-07-03

Scope:

- Python selected RC worktree: `_worktrees/RC-v1-nirs4all-python`
- Python branch: `rc/v1-full-refactor-python`
- Python head: `5e7a0e4b`
- Core selected RC worktree: `_worktrees/RC-v1-nirs4all-core`
- Core branch: `rc/v1-full-refactor-core`
- Core head: `ba959a1`
- Studio selected RC worktree: `_worktrees/RC-v1-studio`
- Studio branch: `rc/v1-full-refactor`
- Studio head: `6b57a90`
- Ecosystem selected RC worktree: `_worktrees/RC-v1-ecosystem`
- Tag refreshed on touched repos: `n4a-v1-rc1-2026.07-refactor`

Files changed:

- Python:
  - `tests/integration/pipeline/test_classification_integration.py`
  - `tests/integration/pipeline/test_exclude_migration.py`
  - `tests/integration/pipeline/test_merge_auto_detect.py`
  - `tests/integration/pipeline/test_merge_strategies.py`
  - `tests/unit/operators/methods/test_installed_n4m_proof.py`
- Core:
  - `.github/workflows/release-matlab.yml`
  - `bindings/python/tests/test_release_topology.py`
  - `docs/PUBLISHING.md`
- Studio:
  - `.github/workflows/release-unified.yml`
  - `Dockerfile`
- Ecosystem:
  - `docs/contracts/release/public-v1-surface-matrix.n4a.json`
  - `docs/contracts/release/aggregation-lock.n4a.lock.json`
  - `docs/contracts/cutover/drop-gates.n4a.json`
  - `docs/contracts/cutover/readiness-matrix.n4a.json`
  - `docs/agent_reports/RC_V1_FULL_REFACTOR_CONTROL.md`
  - `docs/agent_reports/WAVE_4AQ_CI_RELEASE_GATE_TIGHTENING.md`

Decisions:

- Keep R and MATLAB/Octave in the required V1 surface list.
- Stop accepting if-available R/MATLAB execution as release proof. The required
  cutover gate now calls `make test-r-parity` and `make test-matlab-parity`
  alongside the aggregate surface topology gate.
- Make MATLAB/Octave release packaging block on strict parity against the pinned
  `nirs4all-methods` ref, matching the existing strict R release pattern.
- Keep Python integration tests that exercise legacy-only shapes explicit with
  `engine="legacy"` instead of treating dag-ml unsupported-shape errors as
  product parity failures.
- Normalize the installed n4m proof env path assertion for Windows.
- Repin Studio all-in-one/Docker bundled Python runtime deps from `6d6d78bc` to
  Python `5e7a0e4b`.

Local gates:

- Python targeted CI reproduction subset:
  `17 passed`, `19 warnings`.
- Python touched-file pytest:
  `58 passed`, `2 skipped`, `51 warnings`.
  The two skips are pre-existing TensorFlow optional tests in
  `test_classification_integration.py`.
- Python Ruff on touched files: passed.
- Python `git diff --check`: passed.
- Core workflow YAML parse over `.github/workflows/*.yml`: passed.
- Core release topology and capability tests:
  `21 tests OK`.
- Core `make -n test-matlab-parity`: dry-run confirms
  `NIRS4ALL_LITE_REQUIRE_METHODS_PARITY=1`.
- Core `git diff --check`: passed.
- Studio release workflow YAML parse: passed.
- Studio branch-tarball/old-Python-SHA guard: passed.
- Studio `git diff --check`: passed.

Review:

- Codex worker `019f2703-dbd8-7442-a444-299fd3fce717` implemented the Core
  MATLAB release gate hardening and reported the same lightweight validations.
- Codex explorer `019f26fe-25bd-7622-b678-e77b881d73cd` confirmed the old
  inconsistency: R/MATLAB were required in the matrix while release gates still
  allowed if-available evidence. The chosen fix is required+strict, not preview.

Risks:

- The long Python full parity gate was not rerun. Last full proof remains
  Python `6a2c720` with `887 passed`, `0 skipped`, and `0 xfailed`.
- GitHub CI for Python `5e7a0e4b`, Studio `6b57a90`, Core `ba959a1`, and the
  next ecosystem head must still complete.
- `make test-matlab-parity` was only dry-run locally; real Octave/MATLAB host
  execution remains a release infrastructure gate.
- Licensed MATLAB proof is still not equivalent to Linux Octave proof. If GA
  claims licensed MATLAB support, that host proof must be recorded explicitly.
