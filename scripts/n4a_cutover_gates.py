#!/usr/bin/env python3
"""List or run the non-mutating gates for the NIRS4ALL dag-ml cutover.

The gate manifest is intentionally data-only. This runner expands workspace
paths, prints the exact commands in dry-run/list mode, and can execute selected
gates when the caller explicitly passes ``run``.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = Path("docs/contracts/cutover/drop-gates.n4a.json")
DEFAULT_READINESS_MATRIX = Path("docs/contracts/cutover/readiness-matrix.n4a.json")
READINESS_STATUSES = {"blocked", "expected-fail", "ready", "advisory", "passed"}
POST_W2J_STATE_SCHEMA = "n4a.post-w2j-cutover-state/v1"


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


def load_readiness_matrix(path: Path, known_gate_ids: set[str]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise GateError(f"cannot read readiness matrix {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise GateError(f"invalid JSON readiness matrix {path}: {exc}") from exc
    if data.get("schema_version") != "n4a.cutover-readiness/v1":
        raise GateError(f"unsupported readiness matrix schema: {data.get('schema_version')!r}")
    blockers = data.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        raise GateError("readiness matrix must contain a non-empty blockers list")
    seen: set[str] = set()
    for blocker in blockers:
        blocker_id = blocker.get("id")
        if not isinstance(blocker_id, str) or not blocker_id:
            raise GateError("each readiness blocker needs a non-empty id")
        if blocker_id in seen:
            raise GateError(f"duplicate readiness blocker id: {blocker_id}")
        seen.add(blocker_id)
        for field in ("title", "lane", "owner_repo", "status", "missing_contract"):
            if not isinstance(blocker.get(field), str) or not blocker[field]:
                raise GateError(f"{blocker_id}: {field} must be a non-empty string")
        if blocker["status"] not in READINESS_STATUSES:
            raise GateError(f"{blocker_id}: unsupported status {blocker['status']!r}")
        evidence = blocker.get("expected_evidence")
        if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
            raise GateError(f"{blocker_id}: expected_evidence must be a list of strings")
        gate_ids = blocker.get("gate_ids", [])
        if not isinstance(gate_ids, list) or not all(isinstance(item, str) for item in gate_ids):
            raise GateError(f"{blocker_id}: gate_ids must be a list of strings")
        unknown = sorted(set(gate_ids) - known_gate_ids)
        if unknown:
            raise GateError(f"{blocker_id}: unknown gate id(s): {', '.join(unknown)}")
        primary_gate_id = blocker.get("primary_gate_id")
        command = blocker.get("command")
        cwd = blocker.get("cwd")
        if primary_gate_id is not None:
            if primary_gate_id not in known_gate_ids:
                raise GateError(f"{blocker_id}: unknown primary_gate_id {primary_gate_id!r}")
        elif not isinstance(command, list) or not command or not isinstance(cwd, str) or not cwd:
            raise GateError(f"{blocker_id}: needs primary_gate_id or cwd plus command")
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


def _check(checks: list[dict[str, Any]], check_id: str, passed: bool, evidence: str, detail: str | None = None) -> None:
    row: dict[str, Any] = {
        "id": check_id,
        "status": "passed" if passed else "failed",
        "evidence": evidence,
    }
    if detail:
        row["detail"] = detail
    checks.append(row)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise GateError(f"cannot read {path}: {exc}") from exc


def _parse_python(path: Path) -> ast.Module:
    try:
        return ast.parse(_read_text(path), filename=str(path))
    except SyntaxError as exc:
        raise GateError(f"cannot parse Python source {path}: {exc}") from exc


def _literal_assignment(module: ast.Module, name: str) -> Any:
    for node in module.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            value = node.value
        elif isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            value = node.value
        else:
            continue
        if isinstance(value, ast.Constant):
            return value.value
        return None
    return None


def _find_function(nodes: list[ast.stmt], name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _find_class(module: ast.Module, name: str) -> ast.ClassDef | None:
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _argument_default(function: ast.FunctionDef | ast.AsyncFunctionDef, name: str) -> ast.expr | None:
    args = [*function.args.posonlyargs, *function.args.args]
    defaults: list[ast.expr | None] = [None] * (len(args) - len(function.args.defaults)) + list(function.args.defaults)
    for arg, default in zip(args, defaults, strict=True):
        if arg.arg == name:
            return default
    for arg, default in zip(function.args.kwonlyargs, function.args.kw_defaults, strict=True):
        if arg.arg == name:
            return default
    return None


def _is_literal(value: ast.expr | None, expected: Any) -> bool:
    return isinstance(value, ast.Constant) and value.value == expected


def _is_not_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not) and isinstance(node.operand, ast.Name) and node.operand.id == name


def _is_call_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name


def _is_self_method_call(node: ast.AST, method: str) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == method
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "self"
    )


def _body_contains_raise(body: list[ast.stmt]) -> bool:
    return any(isinstance(node, ast.Raise) for stmt in body for node in ast.walk(stmt))


def _test_mentions_name(node: ast.AST, name: str) -> bool:
    return any(isinstance(child, ast.Name) and child.id == name for child in ast.walk(node))


def _delegate_calls_are_guarded(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    violations: list[ast.Call] = []

    def visit(node: ast.AST, guarded: bool) -> None:
        if isinstance(node, ast.If):
            body_guarded = guarded or _test_mentions_name(node.test, "legacy_refit_compatibility")
            for child in node.body:
                visit(child, body_guarded)
            for child in node.orelse:
                visit(child, guarded)
            return
        if _is_self_method_call(node, "_dagml_export_delegate") and not guarded:
            violations.append(node)
        for child in ast.iter_child_nodes(node):
            visit(child, guarded)

    for stmt in function.body:
        visit(stmt, False)
    return not violations


def _git_output(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise GateError(f"git -C {repo} {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _check_repo_branch_and_head(
    checks: list[dict[str, Any]],
    check_id: str,
    repo: Path,
    expected_branch: str,
) -> str:
    branch = _git_output(repo, "branch", "--show-current")
    head = _git_output(repo, "rev-parse", "--short=8", "HEAD")
    _check(
        checks,
        f"{check_id}.branch",
        branch == expected_branch,
        f"{repo.name} is on {branch or '<detached>'}@{head}",
        None if branch == expected_branch else f"expected branch {expected_branch!r}",
    )
    return head


def _check_required_source_patterns(
    checks: list[dict[str, Any]],
    check_id: str,
    repo: Path,
    patterns: dict[str, list[str]],
) -> None:
    missing: list[str] = []
    for rel, needles in patterns.items():
        path = repo / rel
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            missing.append(f"{rel}: cannot read ({exc})")
            continue
        for needle in needles:
            if needle not in text:
                missing.append(f"{rel}: missing {needle!r}")
    _check(
        checks,
        f"{check_id}.source",
        not missing,
        f"{repo.name} contains the Wave 2J source/test markers required for L19 accounting",
        "; ".join(missing) if missing else None,
    )


def _check_nirs4all_cutover_state(nirs4all_root: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    engine_module = _parse_python(nirs4all_root / "nirs4all" / "pipeline" / "engine.py")
    default_engine = _literal_assignment(engine_module, "DEFAULT_ENGINE")
    _check(
        checks,
        "nirs4all.default_engine",
        default_engine == "dag-ml",
        f"DEFAULT_ENGINE literal is {default_engine!r}",
        None if default_engine == "dag-ml" else "expected 'dag-ml'",
    )

    run_module = _parse_python(nirs4all_root / "nirs4all" / "api" / "run.py")
    run_function = _find_function(run_module.body, "run")
    allow_default = _argument_default(run_function, "allow_fallback") if run_function else None
    _check(
        checks,
        "nirs4all.run.allow_fallback_default",
        run_function is not None and _is_literal(allow_default, False),
        "nirs4all.api.run.run has allow_fallback default False",
        None if run_function is not None and _is_literal(allow_default, False) else "expected allow_fallback=False",
    )

    fallback_function = None
    if run_function is not None:
        fallback_function = next(
            (
                node
                for node in ast.walk(run_function)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_fallback"
            ),
            None,
        )
    strict_raise = False
    legacy_call_count = 0
    if fallback_function is not None:
        strict_raise = any(
            isinstance(node, ast.If) and _is_not_name(node.test, "allow_fallback") and _body_contains_raise(node.body)
            for node in ast.walk(fallback_function)
        )
        legacy_call_count = sum(1 for node in ast.walk(fallback_function) if _is_call_name(node, "_run_legacy"))
    _check(
        checks,
        "nirs4all.fallback_explicit_opt_in",
        fallback_function is not None and strict_raise and legacy_call_count == 1,
        "dag-ml fallback helper raises when allow_fallback is false and calls legacy only in that explicit fallback helper",
        None
        if fallback_function is not None and strict_raise and legacy_call_count == 1
        else f"_fallback={fallback_function is not None}, strict_raise={strict_raise}, legacy_call_count={legacy_call_count}",
    )

    result_module = _parse_python(nirs4all_root / "nirs4all" / "api" / "result.py")
    compat_literal = _literal_assignment(result_module, "_DAGML_LEGACY_REFIT_COMPATIBILITY")
    result_class = _find_class(result_module, "RunResult")
    export_function = _find_function(result_class.body, "export") if result_class else None
    export_model_function = _find_function(result_class.body, "export_model") if result_class else None
    _check(
        checks,
        "nirs4all.export.compatibility_literal",
        compat_literal == "legacy-refit",
        f"legacy-refit compatibility literal is {compat_literal!r}",
        None if compat_literal == "legacy-refit" else "expected 'legacy-refit'",
    )
    for name, function in (("export", export_function), ("export_model", export_model_function)):
        default = _argument_default(function, "compatibility") if function else None
        _check(
            checks,
            f"nirs4all.{name}.compatibility_default",
            function is not None and _is_literal(default, None),
            f"RunResult.{name} compatibility default is None",
            None if function is not None and _is_literal(default, None) else "expected compatibility=None",
        )
        _check(
            checks,
            f"nirs4all.{name}.legacy_refit_guard",
            function is not None and _delegate_calls_are_guarded(function),
            f"RunResult.{name} reaches _dagml_export_delegate only below the legacy_refit_compatibility guard",
            None if function is not None and _delegate_calls_are_guarded(function) else "unguarded _dagml_export_delegate call found",
        )

    try:
        compatibility = json.loads((nirs4all_root / "docs" / "compatibility.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _check(checks, "nirs4all.coverage_meter", False, "docs/compatibility.json is readable JSON", str(exc))
    else:
        coverage_meter = compatibility.get("coverage_meter", {})
        expected_fallback = compatibility.get("expected_fallback", [])
        fallback = coverage_meter.get("fallback")
        target = coverage_meter.get("expected_fallback_target")
        _check(
            checks,
            "nirs4all.coverage_meter.fallback_zero",
            fallback == 0 and target == 0 and expected_fallback == [],
            f"coverage_meter fallback={fallback!r}, target={target!r}, expected_fallback entries={len(expected_fallback) if isinstance(expected_fallback, list) else 'non-list'}",
            None if fallback == 0 and target == 0 and expected_fallback == [] else "expected fallback=0, target=0, expected_fallback=[]",
        )

    return checks


def check_post_w2j_state(workspace_root: Path) -> dict[str, Any]:
    workspace_root = workspace_root.expanduser().resolve()
    checks: list[dict[str, Any]] = []
    heads: dict[str, str] = {}

    nirs4all_root = workspace_root / "_worktrees" / "RC-v1-nirs4all-python"
    heads["nirs4all"] = _check_repo_branch_and_head(
        checks,
        "nirs4all",
        nirs4all_root,
        "rc/v1-full-refactor-python",
    )
    checks.extend(_check_nirs4all_cutover_state(nirs4all_root))

    product_repos = [
        (
            "studio",
            workspace_root / "_worktrees" / "RC-v1-studio",
            "rc/v1-full-refactor",
            {
                "api/runtime_errors.py": ["class RtError", "unsupported_capability", "unavailable_backend"],
                "tests/test_runs_engine_routing.py": ["allow_fallback is False", "fallback_policy", "structured refusal"],
                "src/types/runs.ts": ["runtime_result"],
            },
        ),
        (
            "web",
            workspace_root / "_worktrees" / "RC-v1-web",
            "rc/v1-full-refactor",
            {
                "studio-lite/src/engine/main-engine.runtime-v1.test.ts": [
                    "without silently running the direct pipeline",
                    "RtErrorException",
                ],
                "studio-lite/src/engine/worker.ts": ["rtResult", "rtErrorToWire"],
                "studio-lite/tests/rt-fallback-smoke.mjs": ["allowFallback:false", "typed RtErrorException"],
            },
        ),
        (
            "tools",
            workspace_root / "_worktrees" / "RC-v1-tools",
            "rc/v1-full-refactor",
            {
                "README.md": ["no-in-place", "native-results-v1", "unsupported-report.json"],
                "src/nirs4all_tools/commands.py": ["legacy {inspect,migrate,verify}", "strict", "native-results-v1"],
            },
        ),
        (
            "cluster",
            workspace_root / "_worktrees" / "RC-v1-cluster",
            "rc/v1-full-refactor",
            {
                "tests/test_rbac.py": ["dag_shaped_whole_run", "server_attested_worker_report", "executor_principal"],
                "tests/test_scheduler.py": ["dead_worker_tasks_requeue", "worker lost"],
                "tests/test_distributed_parity.py": ["DAG-shaped inline pipeline", "dag_trace"],
            },
        ),
        (
            "providers",
            workspace_root / "_worktrees" / "RC-v1-providers",
            "rc/v1-full-refactor",
            {
                "src/nirs4all_providers/repository.py": ["get_pipeline_list", "list_pipelines", "get_pipeline"],
                "src/nirs4all_providers/benchmarks.py": ["get_pipeline_list", "get_pipeline", "queue_pipeline_test"],
            },
        ),
    ]
    for repo_id, repo_path, branch, patterns in product_repos:
        heads[repo_id] = _check_repo_branch_and_head(checks, repo_id, repo_path, branch)
        _check_required_source_patterns(checks, repo_id, repo_path, patterns)

    passed = all(check["status"] == "passed" for check in checks)
    return {
        "schema_version": POST_W2J_STATE_SCHEMA,
        "workspace_root": str(workspace_root),
        "passed": passed,
        "heads": heads,
        "checks": checks,
    }


def post_w2j_state(workspace_root: Path, json_out: bool) -> int:
    report = check_post_w2j_state(workspace_root)
    if json_out:
        json.dump(report, sys.stdout, ensure_ascii=True, indent=2)
        sys.stdout.write("\n")
    else:
        for row in report["checks"]:
            print(f"{row['status']}: {row['id']} - {row['evidence']}")
            if row["status"] != "passed" and row.get("detail"):
                print(f"  {row['detail']}")
        print(f"post-W2J cutover state passed: {report['passed']}")
    return 0 if report["passed"] else 1


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


def readiness_summary(
    blocker: dict[str, Any],
    gates_by_id: dict[str, dict[str, Any]],
    workspace_root: Path,
) -> dict[str, Any]:
    primary_gate_id = blocker.get("primary_gate_id")
    if primary_gate_id:
        gate = gates_by_id[primary_gate_id]
        cwd = str(gate_cwd(gate, workspace_root))
        command = command_for(gate, workspace_root)
    else:
        cwd = str(gate_cwd(blocker, workspace_root))
        command = command_for(blocker, workspace_root)
    return {
        "id": blocker["id"],
        "title": blocker["title"],
        "lane": blocker["lane"],
        "owner_repo": blocker["owner_repo"],
        "status": blocker["status"],
        "required_for_cutover": bool(blocker.get("required_for_cutover", True)),
        "primary_gate_id": primary_gate_id,
        "gate_ids": blocker.get("gate_ids", []),
        "cwd": cwd,
        "command": command,
        "expected_evidence": blocker["expected_evidence"],
        "missing_contract": blocker["missing_contract"],
        "next_owner_action": blocker.get("next_owner_action"),
        "depends_on": blocker.get("depends_on", []),
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


def list_readiness(
    blockers: list[dict[str, Any]],
    gates_by_id: dict[str, dict[str, Any]],
    workspace_root: Path,
    json_out: bool,
) -> int:
    rows = [readiness_summary(blocker, gates_by_id, workspace_root) for blocker in blockers]
    if json_out:
        json.dump({"blockers": rows}, sys.stdout, ensure_ascii=True, indent=2)
        sys.stdout.write("\n")
        return 0
    for row in rows:
        required = "required" if row["required_for_cutover"] else "advisory"
        print(f"[{required}/{row['status']}] {row['id']} - {row['title']}")
        print(f"  owner: {row['owner_repo']} ({row['lane']})")
        print(f"  cwd: {row['cwd']}")
        print(f"  cmd: {' '.join(row['command'])}")
        print(f"  missing: {row['missing_contract']}")
    return 0


def run_gate(gate: dict[str, Any], workspace_root: Path, timeout: int | None, missing_cwd: str = "error") -> dict[str, Any]:
    cwd = gate_cwd(gate, workspace_root)
    cmd = command_for(gate, workspace_root)
    if not cwd.exists():
        if missing_cwd == "skip":
            return {
                "id": gate["id"],
                "status": "skipped",
                "returncode": None,
                "duration_s": 0.0,
                "cwd": str(cwd),
                "command": cmd,
                "stderr": f"cwd does not exist: {cwd}",
            }
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


def run_gates(gates: list[dict[str, Any]], workspace_root: Path, timeout: int | None, json_out: bool, missing_cwd: str, advisory: bool) -> int:
    results = [run_gate(gate, workspace_root, timeout, missing_cwd) for gate in gates]
    failed_required = {
        result["id"]
        for result, gate in zip(results, gates, strict=True)
        if gate.get("required", True) and result["status"] != "passed"
    }
    report = {
        "schema_version": "n4a.cutover-gate-report/v1",
        "workspace_root": str(workspace_root),
        "advisory": advisory,
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
        if advisory and failed_required:
            print("advisory mode: failures are reported but do not fail this command")
    return 0 if advisory or not failed_required else 1


def _add_common_options(parser: argparse.ArgumentParser, *, suppress_defaults: bool = False) -> None:
    default: Any = argparse.SUPPRESS if suppress_defaults else None
    manifest_default: Any = argparse.SUPPRESS if suppress_defaults else DEFAULT_MANIFEST
    readiness_default: Any = argparse.SUPPRESS if suppress_defaults else DEFAULT_READINESS_MATRIX
    workspace_default: Any = argparse.SUPPRESS if suppress_defaults else default_workspace_root()
    parser.add_argument("--manifest", type=Path, default=manifest_default)
    parser.add_argument("--readiness-matrix", type=Path, default=readiness_default)
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
    readiness = sub.add_parser("readiness", help="List cutover blockers with owners and evidence commands.")
    _add_common_options(readiness, suppress_defaults=True)
    post_w2j = sub.add_parser("post-w2j-state", help="Assert the directly-inspected post-Wave-2J cutover state.")
    _add_common_options(post_w2j, suppress_defaults=True)
    run = sub.add_parser("run", help="Execute selected gates. This can be slow.")
    _add_common_options(run, suppress_defaults=True)
    run.add_argument("--timeout", type=int, default=None, help="Per-gate timeout in seconds.")
    run.add_argument(
        "--missing-cwd",
        choices=("error", "skip"),
        default="error",
        help="How to handle a selected gate whose cwd is absent.",
    )
    run.add_argument(
        "--advisory",
        action="store_true",
        help="Report required-gate failures but exit 0. Intended for non-blocking CI visibility before cutover.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        manifest_path = args.manifest
        if not manifest_path.is_absolute():
            manifest_path = repo_root() / manifest_path
        manifest = load_manifest(manifest_path)
        readiness_path = args.readiness_matrix
        if not readiness_path.is_absolute():
            readiness_path = repo_root() / readiness_path
        gates_by_id = {gate["id"]: gate for gate in manifest["gates"]}
        readiness_matrix = load_readiness_matrix(readiness_path, set(gates_by_id))
        workspace_root = args.workspace_root.expanduser().resolve()
        gates = selected_gates(manifest, set(args.gate) if args.gate else None, set(args.skip or []))
        command = args.command or "list"
        if command == "validate":
            if args.json:
                json.dump(
                    {
                        "valid": True,
                        "selected_gates": [gate["id"] for gate in gates],
                        "readiness_blockers": [blocker["id"] for blocker in readiness_matrix["blockers"]],
                    },
                    sys.stdout,
                    indent=2,
                )
                sys.stdout.write("\n")
            else:
                print(f"manifest OK: {manifest_path}")
                print(f"readiness matrix OK: {readiness_path}")
                print(f"selected gates: {', '.join(gate['id'] for gate in gates)}")
            return 0
        if command == "readiness":
            selected_gate_ids = {gate["id"] for gate in gates}
            blockers = [
                blocker
                for blocker in readiness_matrix["blockers"]
                if not args.gate or set(blocker.get("gate_ids", [])) & selected_gate_ids
            ]
            return list_readiness(blockers, gates_by_id, workspace_root, args.json)
        if command == "post-w2j-state":
            return post_w2j_state(workspace_root, args.json)
        if command == "run":
            return run_gates(gates, workspace_root, args.timeout, args.json, args.missing_cwd, args.advisory)
        return list_gates(gates, workspace_root, args.json)
    except GateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
