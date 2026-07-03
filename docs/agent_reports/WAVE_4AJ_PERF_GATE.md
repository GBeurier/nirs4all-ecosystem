# Wave 4AJ - Performance Gate and CI Reproducibility

Date: 2026-07-03

Scope:

- `nirs4all` selected RC worktree: `_worktrees/RC-v1-nirs4all-python`
- Python branch: `rc/v1-full-refactor-python`
- Python head: `5071a0b0`
- `nirs4all-benchmarks` selected RC worktree: `_worktrees/RC-v1-benchmarks`
- Benchmarks branch: `rc/v1-full-refactor`
- Benchmarks head: `6e4c630`
- Tag refreshed on both repos: `n4a-v1-rc1-2026.07-refactor`

Files changed:

- Python: `scripts/bench_engine_perf.py`
- Python: `tests/unit/test_bench_engine_perf.py`
- Python: `.github/workflows/CI.yaml`
- Python: `.github/workflows/docs-quality.yml`
- Python: `.github/workflows/docs.yml`
- Python: `examples/user/01_getting_started/U02_basic_regression.py`
- Python: `examples/user/01_getting_started/U03_basic_classification.py`
- Python: `examples/user/04_models/U01_multi_model.py`
- Python: `examples/reference/R04_visualization.py`
- Python: `nirs4all/controllers/data/branch.py`
- Python: `nirs4all/pipeline/dagml/envelope.py`
- Python: `nirs4all/pipeline/dagml/node_runner.py`
- Python: `nirs4all/pipeline/explainer.py`
- Benchmarks: `docs/CLI.md`
- Benchmarks: `docs/PERFORMANCE.md`
- Benchmarks: `src/nirs4all_benchmarks/performance_compare.py`
- Benchmarks: `src/nirs4all_benchmarks/service/app.py`
- Benchmarks: `tests/test_performance_compare.py`
- Benchmarks: `.github/workflows/ci.yml`
- Ecosystem: `docs/contracts/cutover/drop-gates.n4a.json`
- Ecosystem: `docs/contracts/cutover/readiness-matrix.n4a.json`
- Ecosystem: `docs/agent_reports/RC_V1_FULL_REFACTOR_CONTROL.md`

Decision:

- Python direct performance smoke now records engine proof per child run and
  fails a requested `dag-ml` run if the child cannot prove it used native
  dag-ml instead of legacy fallback.
- Benchmarks `perf-compare` keeps fallback disabled for both `python_run` and
  `studio_run`, verifies both surfaces use the same seeded workload, emits JSON
  and Markdown evidence, and enforces ratio assertions.
- The ecosystem cutover contract now requires `perf_cross_engine_compare` with
  conservative RC ceilings: `python_run=1.25`, `studio_run=1.35`.
- Python CI installs the selected dag-ml and dag-ml-data RC GitHub refs before
  resolving `nirs4all` dependencies because the RC wheels are not on PyPI yet.
  This does not change product dependencies or hide test failures.
- Python canonical docs examples now use dag-ml-compatible `_or_` model sweeps
  instead of multiple top-level `{"model": ...}` steps, and avoid a
  `feature_augmentation -> X-transform` shape that dag-ml correctly refuses.
- Python full mypy is green by narrowing runtime types explicitly; the workflow
  remains `mypy nirs4all`.
- Benchmarks CI passes the active matrix Python version to mypy, avoiding the
  Python 3.12 NumPy-stub parser failure caused by forcing `python_version=3.10`.

Local gates:

- Python `python3.11 -m pytest tests/unit/test_bench_engine_perf.py -q`
  -> `6 passed`.
- Python `python3.11 -m ruff check scripts/bench_engine_perf.py tests/unit/test_bench_engine_perf.py`
  -> passed.
- Python YAML parse for `.github/workflows/CI.yaml`,
  `.github/workflows/docs-quality.yml`, and `.github/workflows/docs.yml`
  -> passed.
- Python `python3.11 -m mypy nirs4all`
  -> `Success: no issues found in 439 source files`.
- Python `python3.11 -m ruff check` on the touched examples, dag-ml, branch,
  explainer, benchmark script, and benchmark unit test files
  -> passed.
- Python Docs Quality canonical subset, run from `examples/` with the checkout
  on `PYTHONPATH`, passed all six scripts:
  `U01_hello_world.py`, `U02_basic_regression.py`, `U03_basic_classification.py`,
  `U01_preprocessing_basics.py`, `U01_multi_model.py`, and
  `R04_visualization.py`.
- Python direct smoke:
  `python3.11 scripts/bench_engine_perf.py --cases pls_small --repeats 1 --python python3.11 --max-wall-ratio 3 --max-rss-ratio 2`
  -> legacy wall `0.650s`, dag-ml wall `0.098s`, verified dag-ml, wall ratio
  `0.15x`, RSS ratio `0.96x`, prediction delta `0`.
- Benchmarks `.venv/bin/mypy --python-version 3.12`
  -> passed.
- Benchmarks `.venv/bin/ruff check src tests`
  -> passed.
- Benchmarks `.venv/bin/pytest tests/test_performance_compare.py -q`
  -> `4 passed`.
- Benchmarks full local pytest after the perf test patch:
  `.venv/bin/pytest -q`
  -> `88 passed`.
- Benchmarks cutover perf gate:
  `n4a-benchmarks perf-compare --repeats 3 --assert-max-ratio python_run=1.25 --assert-max-ratio studio_run=1.35`
  -> Python direct run ratio `0.730x`, total ratio `0.771x`; Studio worker run
  ratio `0.707x`, total ratio `0.751x`.
- Ecosystem `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all`
  -> passed.
- Ecosystem `python3 -m pytest -q tests/test_cutover_state_gate.py -p no:cacheprovider`
  -> `5 passed`.

Review:

- Codex coordinator reviewed both diffs and fixed the initial Benchmarks doc
  mismatch: `studio_run` measures `api.pipelines._run_pipeline_task`, not
  `api.runs._execute_pipeline_training`.
- Claude Code read-only review confirmed the pinned dag-ml and dag-ml-data SHAs
  are the remote `rc/v1-full-refactor` tips, the package versions satisfy the
  `>=0.2.1` constraints, the quoted `#subdirectory=` URLs are shell-safe, and
  the Benchmarks mypy matrix increases rather than reduces coverage.
  No file writes were delegated to Claude for this lane.

Risks:

- The full Python parity proof was not rerun in this Wave by design; the last
  full proof remains Python `6a2c720` with `887 passed`, `0 skipped`, and
  `0 xfailed`.
- Python GitHub CI now builds dag-ml/dag-ml-data from selected GitHub refs until
  release wheels are published, so CI duration depends on Rust wheel build time.
- The selected CI refs are pinned by commit SHA while the public RC branches/tags
  also point there. If the dag-ml package floor is raised before wheels are
  published, the workflow pins must move with the release lock.
- The perf ceilings are RC guardrails for this deterministic workload and host
  class; they should be recalibrated if the workload or CI host class changes.
