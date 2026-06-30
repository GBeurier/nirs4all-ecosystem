# FIX-RV7 - L18 nirs4all-tools follow-up

**Date:** 2026-06-30
**Owner:** Codex supervisor
**Repo:** `nirs4all-tools` (`main`, staged)
**Input review:** `RV7_L18_TOOLS_SCAFFOLD_REVIEW.md`

## Changes

Addressed the three medium RV7 findings in the staged scaffold:

- `migrate --copy-only --verify` now runs the manifest self-consistency verifier
  and records `verification_summary.ran=true` / `passed=true` in the migration
  report.
- `source.fingerprint` is now a stable SHA-256 content fingerprint over the
  source file/tree inventory, instead of `null`.
- `input_inventory` and `output_inventory` now expose the contract fields from
  `legacy_migration_manifest.v1` (`tables`, `row_counts`,
  `discovered_manifests`, `discovered_bundles`, `generated_manifests`) without
  the ad hoc `file_count` field.

Also closed the inert-flag issue:

- `--trusted-load-joblib` is explicitly refused until the schema-transform
  engine exists.
- `--strict` is explicitly refused with `--dry-run` or `--copy-only`, where it
  cannot affect behavior.

## Validation

- `uv run --extra dev pytest -q` -> 62 passed.
- `uv run --extra dev ruff check .` -> passed.
- `uv run --extra dev mypy` -> passed.
- `python3 -m compileall -q src tests` -> passed.
- `git diff --cached --check` -> clean.

## Remaining L18 Scope

The scaffold is still not a V1 migration release. Remaining work is the real
legacy reader to `nirs4all-workspace-v2` transform, golden fixtures, validated
`--resume`, and the later native-results target once dag-ml native schemas are
ready.
