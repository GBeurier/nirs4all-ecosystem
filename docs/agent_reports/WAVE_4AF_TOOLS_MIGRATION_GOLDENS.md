# Wave 4AF - Tools Migration Golden Proof

Date: 2026-07-03

Scope:

- `nirs4all-tools` selected RC worktree: `_worktrees/RC-v1-tools`
- Branch: `rc/v1-full-refactor`
- Head: `7c5070f`

Purpose:

- Close the migration/converter golden-test evidence gap for the current RC
  without changing runtime code.
- Verify the standalone no-in-place converter, manifest/report/id-map contracts,
  opaque preservation, workspace-v2 lowering, and verify/tamper coverage.

Local gates:

- `PYTHONPATH=src python3.11 -m pytest -q tests/test_real_golden_fixtures.py tests/test_cli.py tests/test_commands.py tests/test_detect.py tests/test_contracts.py tests/test_policy.py -p no:cacheprovider`
  -> `110 passed`, one external `pytz` deprecation warning.
- `PYTHONPATH=src python3.11 -m pytest -q -p no:cacheprovider`
  -> `114 passed`, one external `pytz` deprecation warning.
- `PYTHONPATH=src python3.11 -m nirs4all_tools --version`
  -> `nirs4all-tools 0.0.1`.
- CLI golden smoke:
  `PYTHONPATH=src python3.11 -m nirs4all_tools legacy migrate tests/fixtures/legacy/old_workspace_mixed --output <tmp>/out --verify`
  -> exit `10` (`MIGRATED_WITH_WARNINGS`), expected for mixed legacy input with
  unsupported payloads preserved opaque.
- Follow-up verify:
  `PYTHONPATH=src python3.11 -m nirs4all_tools legacy verify <tmp>/out --manifest <tmp>/out/migration-manifest.json`
  -> exit `0`; verification summary passed, SQLite integrity passed, preserved
  payload coverage passed for `3` opaque payload groups.

Review:

- The first local run with default `python3` failed on Python 3.10 because
  `datetime.UTC` is Python 3.11+. This matches `pyproject.toml`
  `requires-python = ">=3.11"` and is not a code failure.
- The checked-in golden tests copy fixture inputs to temporary directories before
  migration and assert source snapshots stay unchanged.
- The tests cover dry-run without output, best-effort opaque preservation,
  strict lowering of loose predictions and SQLite legacy arrays, workspace-v2
  shape, manifest/report/id-map shape, verify-only, tamper detection, preserved
  payload checksum coverage, and native-results preview lowering/preservation.

Decision:

- Migration/converter golden tests are current on the selected Tools RC head.
- No Tools code change was needed in this batch.
- Remaining migration release work is product/process integration: publish the
  converter artifact with the RC, keep Studio on external-command guidance for
  legacy workspaces, and avoid claiming replayable dag-ml bundles for legacy
  outputs unless the required graph/fingerprint contracts are present.
