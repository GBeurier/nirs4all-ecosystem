#!/usr/bin/env python3
"""List or run the non-mutating gates for the NIRS4ALL dag-ml cutover.

The gate manifest is intentionally data-only. This runner expands workspace
paths, prints the exact commands in dry-run/list mode, and can execute selected
gates when the caller explicitly passes ``run``.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = Path("docs/contracts/cutover/drop-gates.n4a.json")


class GateError(RuntimeError):
    """Cutover gate configuration or execution error."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_workspace_root() -> Path:
    env_root = os.environ.get("N4A_WORKSPACE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    root = repo_root()
    if root.parent.name == "_worktrees":
        return root.parent.parent.resolve()
    return root.parent.resolve()


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise GateError(f"cannot read manifest {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise GateError(f"invalid JSON manifest {path}: {exc}") from exc
    if data.get("schema_version") != "n4a.cutover-gates/v1":
        raise GateError(f"unsupported manifest schema: {data.get('schema_version')!r}")
    gates = data.get("gates")
    if not isinstance(gates, list) or not gates:
        raise GateError("manifest must contain a non-empty gates list")
    seen: set[str] = set()
    for gate in gates:
        gate_id = gate.get("id")
        if not isinstance(gate_id, str) or not gate_id:
            raise GateError("each gate needs a non-empty id")
        if gate_id in seen:
            raise GateError(f"duplicate gate id: {gate_id}")
        seen.add(gate_id)
        if not isinstance(gate.get("command"), list) or not gate["command"]:
            raise GateError(f"{gate_id}: command must be a non-empty list")
        if not isinstance(gate.get("cwd"), str) or not gate["cwd"]:
            raise GateError(f"{gate_id}: cwd must be a non-empty string")
    return data


def format_value(value: Any, workspace_root: Path) -> Any:
    if isinstance(value, str):
        return value.format(workspace_root=str(workspace_root))
    if isinstance(value, list):
        return [format_value(item, workspace_root) for item in value]
    if isinstance(value, dict):
        return {key: format_value(item, workspace_root) for key, item in value.items()}
    return value


def gate_cwd(gate: dict[str, Any], workspace_root: Path) -> Path:
    raw = format_value(gate["cwd"], workspace_root)
    path = Path(raw)
    if not path.is_absolute():
        path = workspace_root / path
    return path.resolve()


def selected_gates(manifest: dict[str, Any], include: set[str] | None, skip: set[str]) -> list[dict[str, Any]]:
    gates = list(manifest["gates"])
    known = {gate["id"] for gate in gates}
    if include:
        missing = include - known
        if missing:
            raise GateError(f"unknown gate id(s): {', '.join(sorted(missing))}")
        gates = [gate for gate in gates if gate["id"] in include]
    missing_skip = skip - known
    if missing_skip:
        raise GateError(f"unknown skipped gate id(s): {', '.join(sorted(missing_skip))}")
    return [gate for gate in gates if gate["id"] not in skip]


def command_for(gate: dict[str, Any], workspace_root: Path) -> list[str]:
    return [str(part) for part in format_value(gate["command"], workspace_root)]


def gate_summary(gate: dict[str, Any], workspace_root: Path) -> dict[str, Any]:
    return {
        "id": gate["id"],
        "title": gate.get("title", gate["id"]),
        "lane": gate.get("lane"),
        "required": bool(gate.get("required", True)),
        "cwd": str(gate_cwd(gate, workspace_root)),
        "command": command_for(gate, workspace_root),
        "evidence": gate.get("evidence", []),
    }


def list_gates(gates: list[dict[str, Any]], workspace_root: Path, json_out: bool) -> int:
    rows = [gate_summary(gate, workspace_root) for gate in gates]
    if json_out:
        json.dump({"gates": rows}, sys.stdout, ensure_ascii=True, indent=2)
        sys.stdout.write("\n")
        return 0
    for row in rows:
        required = "required" if row["required"] else "optional"
        print(f"[{required}] {row['id']} - {row['title']}")
        print(f"  cwd: {row['cwd']}")
        print(f"  cmd: {' '.join(row['command'])}")
    return 0


def run_gate(gate: dict[str, Any], workspace_root: Path, timeout: int | None) -> dict[str, Any]:
    cwd = gate_cwd(gate, workspace_root)
    cmd = command_for(gate, workspace_root)
    if not cwd.exists():
        return {
            "id": gate["id"],
            "status": "error",
            "returncode": None,
            "duration_s": 0.0,
            "cwd": str(cwd),
            "command": cmd,
            "stderr": f"cwd does not exist: {cwd}",
        }
    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        status = "passed" if proc.returncode == 0 else "failed"
        return {
            "id": gate["id"],
            "status": status,
            "returncode": proc.returncode,
            "duration_s": round(time.monotonic() - started, 3),
            "cwd": str(cwd),
            "command": cmd,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "id": gate["id"],
            "status": "timeout",
            "returncode": None,
            "duration_s": round(time.monotonic() - started, 3),
            "cwd": str(cwd),
            "command": cmd,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"timed out after {timeout}s",
        }


def run_gates(gates: list[dict[str, Any]], workspace_root: Path, timeout: int | None, json_out: bool) -> int:
    results = [run_gate(gate, workspace_root, timeout) for gate in gates]
    failed_required = {
        result["id"]
        for result, gate in zip(results, gates, strict=True)
        if gate.get("required", True) and result["status"] != "passed"
    }
    report = {
        "schema_version": "n4a.cutover-gate-report/v1",
        "workspace_root": str(workspace_root),
        "passed": not failed_required,
        "failed_required": sorted(failed_required),
        "results": results,
    }
    if json_out:
        json.dump(report, sys.stdout, ensure_ascii=True, indent=2)
        sys.stdout.write("\n")
    else:
        for result in results:
            print(f"{result['status']}: {result['id']} ({result['duration_s']}s)")
            if result["status"] != "passed":
                stderr = str(result.get("stderr") or "").strip()
                if stderr:
                    print(stderr[-2000:])
        print(f"required gates passed: {not failed_required}")
    return 0 if not failed_required else 1


def _add_common_options(parser: argparse.ArgumentParser, *, suppress_defaults: bool = False) -> None:
    default: Any = argparse.SUPPRESS if suppress_defaults else None
    manifest_default: Any = argparse.SUPPRESS if suppress_defaults else DEFAULT_MANIFEST
    workspace_default: Any = argparse.SUPPRESS if suppress_defaults else default_workspace_root()
    parser.add_argument("--manifest", type=Path, default=manifest_default)
    parser.add_argument("--workspace-root", type=Path, default=workspace_default)
    parser.add_argument(
        "--gate",
        action="append",
        default=default,
        help="Gate id to include. Repeatable. Defaults to all gates.",
    )
    parser.add_argument("--skip", action="append", default=default, help="Gate id to skip. Repeatable.")
    parser.add_argument("--json", action="store_true", default=default, help="Emit JSON output.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    _add_common_options(parser)
    sub = parser.add_subparsers(dest="command")
    list_parser = sub.add_parser("list", help="List selected gates without executing them.")
    _add_common_options(list_parser, suppress_defaults=True)
    validate = sub.add_parser("validate", help="Validate the manifest and selected gate ids.")
    _add_common_options(validate, suppress_defaults=True)
    validate.set_defaults(validate_only=True)
    run = sub.add_parser("run", help="Execute selected gates. This can be slow.")
    _add_common_options(run, suppress_defaults=True)
    run.add_argument("--timeout", type=int, default=None, help="Per-gate timeout in seconds.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        manifest_path = args.manifest
        if not manifest_path.is_absolute():
            manifest_path = repo_root() / manifest_path
        manifest = load_manifest(manifest_path)
        workspace_root = args.workspace_root.expanduser().resolve()
        gates = selected_gates(manifest, set(args.gate) if args.gate else None, set(args.skip or []))
        command = args.command or "list"
        if command == "validate":
            if args.json:
                json.dump({"valid": True, "selected_gates": [gate["id"] for gate in gates]}, sys.stdout, indent=2)
                sys.stdout.write("\n")
            else:
                print(f"manifest OK: {manifest_path}")
                print(f"selected gates: {', '.join(gate['id'] for gate in gates)}")
            return 0
        if command == "run":
            return run_gates(gates, workspace_root, args.timeout, args.json)
        return list_gates(gates, workspace_root, args.json)
    except GateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
