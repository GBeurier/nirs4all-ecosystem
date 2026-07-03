# Wave 4AA - Cutover RC Gates, CI Repairs, Security Audit

Date: 2026-07-03

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Scope

This batch keeps the production heads intact and refreshes selected RC heads only.
No full Python parity run was started in this batch; the last full parity proof
remains Python `6a2c720` with `887 passed`, `0 skipped`, `0 xfailed`.

## Integrated Changes

### Ecosystem

Files modified:

- `docs/contracts/cutover/drop-gates.n4a.json`
- `docs/contracts/cutover/readiness-matrix.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `scripts/n4a_cutover_gates.py`
- `tests/test_cutover_state_gate.py`
- `docs/agent_reports/RC_V1_FULL_REFACTOR_CONTROL.md`
- `docs/agent_reports/WAVE_4AA_CUTOVER_CI_SECURITY.md`

Decisions:

- Cutover gates now target the selected `_worktrees/RC-v1-*` worktrees, not the
  stale `INT-*` worktrees or main checkout paths.
- `release_lock_validation` defaults to `{workspace_root}/_worktrees` so the
  selected workspace paths are validated exactly as the lock was generated.
- `providers_local_sibling_release` runs against a temporary sibling workspace
  built from selected RC worktrees and the selected `nirs4all-io` source path.
- `cluster_dag_advisory` is recorded as an advisory gate instead of inline
  readiness text.
- The aggregation lock was regenerated after moving `nirs4all-datasets` to
  `60658035`.

Tests:

- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 -m pytest -q tests/test_cutover_state_gate.py tests/test_release_lock.py tests/test_release_surface_matrix.py -p no:cacheprovider` -> `22 passed`
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all`
- `python3 scripts/n4a_cutover_gates.py post-w2j-state --workspace-root /home/delete/nirs4all`
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable` -> `7/7`
- `cluster_dag_advisory` -> `3 passed`, Ruff OK

### Datasets

Commit: `60658035 test(access): keep acquire stub hermetic`

Files modified:

- `tests/test_access.py`

Decision:

- The CI failure was a real test isolation bug. In the full suite,
  `tests/test_acquire.py` can import the native `_acquire` module before
  `tests/test_access.py`; replacing only `sys.modules` is insufficient because
  the package attribute can still point at the real native module. The helper now
  replaces both `sys.modules["nirs4all_datasets._acquire"]` and
  `nirs4all_datasets._acquire`.

Tests:

- `python3.11 -m ruff check .`
- `python3.11 -m pytest -q tests/test_acquire.py tests/test_access.py tests/test_catalog.py -p no:cacheprovider` -> `28 passed`, `1 skipped`
- `python3.11 -m pytest -q -m "not network" -p no:cacheprovider` -> `226 passed`, `6 skipped`

Risk:

- The six remaining skips are pre-existing optional dataset/environment skips,
  not new release-debt skips introduced by this fix.

### Providers

Commit: `2cfcca6 ci(providers): scope lint to package tree`

Files modified:

- `pyproject.toml`
- `scripts/ci_gate.py`

Decision:

- The failed CI linted the `nirs4all-ecosystem/` checkout placed inside the
  providers working tree for the canonical contract comparison. That sibling
  checkout is not provider-owned code. The CI gate now lints `src`, `tests`, and
  `scripts`, and Ruff excludes the `nirs4all-ecosystem` checkout for manual
  `ruff check .` runs.

Tests:

- `python3.11 scripts/ci_gate.py` -> PASS

Risk:

- Provider conformance still has optional real-API skips when optional backing
  packages are not installed; this batch did not broaden provider semantics.

## Agent Reports

### Claude Code - Cluster Security

Session: `312a7e4a-4241-447e-96e3-06a492f3e434`

Ownership: read-only `RC-v1-cluster`.

Files modified: none.

Commands/tests: git ref/reflog/history scans, `git grep` secret-pattern scans,
pickaxe scans for token/password/secret patterns and known key formats.

Result:

- GitGuardian "Generic CLI Option Secret" is a false positive against placeholder
  CLI examples and fixtures (`alice:s3cr3t`, `--token dev`, environment variable
  examples).
- Current active heads remain clean for real secrets.
- Historical placeholders can still exist in pushed history and PR refs because
  the remediation was additive, not a history purge.

Decision:

- Close the alert as false positive/remediated unless GitGuardian discloses a
  non-placeholder value. No credential rotation is indicated from the accessible
  evidence.

### Claude Code - Providers CI

Session: `0ec4f937-9ced-473f-887b-84079101e96f`

Ownership: `RC-v1-providers`.

Files modified: `pyproject.toml` and `scripts/ci_gate.py` in providers.

Result:

- Confirmed the CI failure was Ruff scanning the sibling `nirs4all-ecosystem`
  checkout, not provider source.
- Session was cancelled after the parent reviewed and validated the final diff
  to prevent overlapping edits during publication.

### Claude Code - Datasets CI

Session: `ab03cde8-06a1-41e2-a670-636cdca26088`

Ownership: `RC-v1-datasets`.

Files modified: `tests/test_access.py` in datasets.

Result:

- Confirmed the failing test reached the real Rust acquisition core and tried to
  resolve `dv.example` because the fake `_acquire` module was not hermetic after
  prior imports.
- Session was cancelled after the parent reviewed and validated the final diff
  to prevent overlapping edits during publication.

## Publication

- `nirs4all-datasets` branch `rc/v1-full-refactor` and tag
  `n4a-v1-rc1-2026.07-refactor` were moved to `60658035`.
- `nirs4all-providers` branch `rc/v1-full-refactor` and tag
  `n4a-v1-rc1-2026.07-refactor` were moved to `2cfcca6`.
- `nirs4all-ecosystem` is expected to publish this report, the cutover gate
  migration, and the refreshed aggregation lock after final validation.

