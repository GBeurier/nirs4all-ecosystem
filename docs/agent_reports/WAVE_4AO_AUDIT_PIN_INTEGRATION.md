# Wave 4AO - Audit Pin Integration

Date: 2026-07-03

Scope:

- `nirs4all` selected RC worktree: `_worktrees/RC-v1-nirs4all-python`
- Python branch: `rc/v1-full-refactor-python`
- Python head: `6d6d78bc`
- `nirs4all-studio` selected RC worktree: `_worktrees/RC-v1-studio`
- Studio branch: `rc/v1-full-refactor`
- Studio head: `a509888`
- `nirs4all-web` selected RC worktree: `_worktrees/RC-v1-web`
- Web head: `5be833d`
- `nirs4all-org` selected RC worktree: `_worktrees/RC-v1-org`
- Org head: `2d44265`
- `nirs4all-cockpit` selected RC worktree: `_worktrees/RC-v1-cockpit`
- Cockpit head: `6cdc829`
- Ecosystem board and second-opinion reports in `_worktrees/RC-v1-ecosystem`
- Tag refreshed on published repos: `n4a-v1-rc1-2026.07-refactor`

Files changed:

- Python:
  - `nirs4all/controllers/data/merge.py`
  - `tests/unit/api/test_generate.py`
  - `tests/unit/operators/transforms/test_orthogonalization.py`
  - `tests/unit/optimization/test_binary_search_sampler.py`
  - `tests/unit/pipeline/execution/refit/test_p4a_advanced_refit.py`
  - `tests/unit/pipeline/execution/test_parallel_execution.py`
  - `tests/unit/pipeline/execution/test_should_stop.py`
- Studio:
  - `.github/workflows/release-unified.yml`
  - `Dockerfile`
- Web:
  - `studio-lite/vite.config.ts`
- Org:
  - `index.html`
- Cockpit:
  - `ops/targets.yaml`
  - `tests/test_targets_topology.py`
- Ecosystem:
  - `docs/agent_reports/RC_V1_FULL_REFACTOR_CONTROL.md`
  - `docs/agent_reports/WAVE_4AK_UI_WEB_CLIENTSIDE_AUDIT.md`
  - `docs/agent_reports/WAVE_4AL_LANGUAGE_TOPOLOGY_AUDIT.md`
  - `docs/agent_reports/WAVE_4AM_SKIP_XFAIL_PARITY_AUDIT.md`
  - `docs/agent_reports/WAVE_4AN_CLAUDE_RC_GAP_AUDIT.md`
  - `docs/agent_reports/WAVE_4AO_AUDIT_PIN_INTEGRATION.md`

Decisions:

- Keep Python unit tests that exercise legacy-only surfaces explicit with
  `engine="legacy"` instead of weakening strict dag-ml defaults globally.
- Accept both full-dataset and packed-branch snapshots in disjoint feature merge;
  this preserves existing workspace behavior while allowing strict dag-ml unit
  runs to stay deterministic.
- Close Claude's high-severity Studio release gap by pinning bundled runtime
  dependencies to immutable selected RC commit SHAs, not moving branch tarballs.
- Keep Web as a static client-side-only product. The current change is only a
  naming/domain comment fix; runtime guarantees remain owned by the existing
  client-only contract tests.
- Account for MATLAB/Octave in Cockpit as an aggregate release surface carried
  by the core release artifacts, without inventing an asset-level target the
  current collector cannot prove.
- Treat the GitGuardian `nirs4all-cluster` alert as a historical placeholder
  finding unless GitGuardian exposes a real non-placeholder secret value. Active
  Cluster main and RC/tag heads were already checked clean.

Local gates:

- Python targeted macOS-CI reproduction set: `21 passed`.
- Python expanded touched-unit subset: `261 passed`.
- Python `tests/unit/test_bench_engine_perf.py`: `6 passed`.
- Python full unit suite: `6918 passed`, `116 skipped`, `1073 warnings`.
  This is a unit-suite result, not the Python-reference parity proof.
- Python Ruff on touched files: passed.
- Python full `mypy nirs4all`: passed, `439` source files.
- Studio release workflow YAML parse: passed.
- Studio branch-tarball guard on `.github/workflows/release-unified.yml` and
  `Dockerfile`: passed; no `refs/heads/rc/v1-full-refactor*` runtime source URLs
  remain.
- Web `npm run check:ui-shim`: passed.
- Web `npm run test:client-only`: `2 passed`.
- Web `npm run typecheck`: passed.
- Org stale `n4a-web` scan for `index.html`: clean.
- Cockpit `pytest tests/test_targets_topology.py -q`: `4 passed`.
- Cockpit `cockpit.cli validate-targets ops/targets.yaml`: OK, `21 packages`,
  `94 targets`.
- Cockpit Ruff on `tests/test_targets_topology.py`: passed.
- `git diff --check` passed in each touched product worktree before commit.

Parallel agent review:

- Wave 4AK confirmed the separate `nirs4all-ui` package is consumed by Studio
  and Web, and that Web owns a client-side-only contract for `web.nirs4all.org`.
- Wave 4AL confirmed Python, Rust, JavaScript/WASM, R, and MATLAB/Octave are
  represented in Core/Cockpit/Ecosystem release topology; it added Cockpit
  assertions for that accounting.
- Wave 4AM confirmed no active Python parity skip/xfail blocker in the selected
  evidence, but kept the final full parity rerun mandatory because Python moved
  after the `6a2c720` full proof.
- Wave 4AN, the independent Claude Code second-opinion audit, found the Studio
  moving-branch release pin gap. Studio `a509888` closes that high-severity gap.

Risks:

- The last full Python-reference parity proof remains Python `6a2c720`:
  split slow/non-slow total `887 passed`, `0 skipped`, `0 xfailed`, `0 failed`.
  Current Python head `6d6d78bc` has only fast/unit/static/CI evidence so far.
  Final promotion must rerun the long full parity gate on the final Python head.
- Studio release archive/Docker pinning is locally guarded, but the full
  all-in-one release and Docker jobs still need to run on `a509888` before GA.
- R and licensed MATLAB runtime proof remains a release-policy decision:
  either keep them required and make host runtime gates mandatory, or mark them
  preview until those gates are enforceable.
- Studio product/contract skip sites identified by the second-opinion audit
  should be converted to hard failures or explicitly documented as host/toolchain
  gates before GA.
- GitGuardian dashboard closure still requires external confirmation if the
  provider insists the placeholder signature is an active secret.
