#!/usr/bin/env python3
"""Prove that unsupported legacy semantic conversion fails before writing output.

The nirs4all-tools public CLI deliberately refuses V1 semantic lowering until
the owned writer/runtime contract exists.  This E2E producer records that
boundary without substituting a reconstructed Python run for conversion proof.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


SCENARIO_ID = "e2e-converter-legacy-save-predictions-web"
FIXTURE_RELATIVE_PATH = Path("tests/fixtures/legacy/old_workspace_mixed")
LOWERABLE_INPUTS = (
    Path("runs"),
    Path("run_predictions.json"),
    Path("sample.meta.parquet"),
)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fixture_inventory(tools_root: Path) -> tuple[Path, list[dict[str, str]]]:
    fixture_root = tools_root / FIXTURE_RELATIVE_PATH
    entries: list[dict[str, str]] = []
    for relative_path in LOWERABLE_INPUTS:
        source = fixture_root / relative_path
        if not source.exists():
            raise RuntimeError(f"required legacy fixture input is missing: {source}")
        if source.is_file():
            entries.append(
                {
                    "path": relative_path.as_posix(),
                    "kind": "file",
                    "sha256": _sha256(source),
                }
            )
            continue
        for child in sorted(path for path in source.rglob("*") if path.is_file()):
            entries.append(
                {
                    "path": child.relative_to(fixture_root).as_posix(),
                    "kind": "file",
                    "sha256": _sha256(child),
                }
            )
    if not entries:
        raise RuntimeError(f"legacy fixture contains no lowerable inputs: {fixture_root}")
    return fixture_root, entries


def _input_payload(tools_root: Path) -> dict[str, Any]:
    fixture_root, entries = _fixture_inventory(tools_root)
    return {
        "schema": "n4a.e2e.legacy_conversion_input.v1",
        "scenario_id": SCENARIO_ID,
        "status": "passed",
        "fixture_relative_path": FIXTURE_RELATIVE_PATH.as_posix(),
        "fixture_path": str(fixture_root),
        "input_files": entries,
        "input_file_count": len(entries),
        "semantic_execution_claimed": False,
    }


def _copy_lowerable_input(fixture_root: Path, staging_root: Path) -> Path:
    source = staging_root / "legacy-save"
    shutil.copytree(fixture_root / "runs", source / "runs")
    shutil.copy2(fixture_root / "run_predictions.json", source / "run_predictions.json")
    shutil.copy2(fixture_root / "sample.meta.parquet", source / "sample.meta.parquet")
    return source


def _run_refusal(tools_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    fixture_root, entries = _fixture_inventory(tools_root)
    source_root = tools_root / "src"
    if not source_root.is_dir():
        raise RuntimeError(f"nirs4all-tools source package is missing: {source_root}")
    sys.path.insert(0, str(source_root))
    try:
        from nirs4all_tools.cli import main
        from nirs4all_tools.exit_codes import ExitCode

        with tempfile.TemporaryDirectory(prefix="n4a-legacy-refusal-") as temporary_dir:
            staging_root = Path(temporary_dir)
            source = _copy_lowerable_input(fixture_root, staging_root)
            output = staging_root / "converted-workspace-v2"
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main(
                    [
                        "legacy",
                        "migrate",
                        str(source),
                        "--output",
                        str(output),
                        "--strict",
                        "--verify",
                    ]
                )
            expected_exit_code = int(ExitCode.UNSUPPORTED_INPUT)
            if exit_code != expected_exit_code:
                raise RuntimeError(
                    f"semantic conversion returned {exit_code}, expected {expected_exit_code}"
                )
            if output.exists():
                raise RuntimeError(f"semantic conversion created output before refusal: {output}")
            try:
                error_payload = json.loads(stderr.getvalue())
                error = error_payload["error"]
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                raise RuntimeError("semantic conversion did not emit a structured CLI error") from exc
            if error.get("exit_code") != expected_exit_code or error.get("code") != "UNSUPPORTED_INPUT":
                raise RuntimeError(f"unexpected structured refusal: {error!r}")
    finally:
        sys.path.remove(str(source_root))

    refusal = {
        "schema": "n4a.e2e.legacy_conversion_refusal.v1",
        "scenario_id": SCENARIO_ID,
        "status": "passed",
        "result": "refused_before_write",
        "exit_code": expected_exit_code,
        "expected_exit_code": expected_exit_code,
        "error": error,
        "input_file_count": len(entries),
        "semantic_execution_claimed": False,
        "writer_runtime_contract": "unavailable",
    }
    output_absence = {
        "schema": "n4a.e2e.legacy_conversion_output_absence.v1",
        "scenario_id": SCENARIO_ID,
        "status": "passed",
        "output_created": False,
        "migration_artifact_count": 0,
        "semantic_execution_claimed": False,
        "result": "no_output_after_refusal",
    }
    return refusal, output_absence


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools-root", type=Path, required=True)
    parser.add_argument("--artifacts-dir", type=Path, required=True)
    parser.add_argument("--inspect-input", action="store_true")
    parser.add_argument("--verify-refusal", action="store_true")
    args = parser.parse_args(argv)
    if args.inspect_input == args.verify_refusal:
        parser.error("select exactly one of --inspect-input or --verify-refusal")
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    tools_root = args.tools_root.resolve()
    artifacts_dir = args.artifacts_dir.resolve()
    if args.inspect_input:
        _write_json(artifacts_dir / "legacy-input.json", _input_payload(tools_root))
        return 0
    refusal, output_absence = _run_refusal(tools_root)
    _write_json(artifacts_dir / "conversion-refusal.json", refusal)
    _write_json(artifacts_dir / "output-absence.json", output_absence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
