#!/usr/bin/env python3
"""Measure pytest test-to-source edges and run impacted tests at an exact revision."""

import argparse
import ast
import hashlib
from importlib.metadata import distributions
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
from xml.etree import ElementTree


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def environment():
    versions = sorted((d.metadata.get("Name", "").lower(), d.version) for d in distributions())
    return {"python": platform.python_version(), "platform": sys.platform, "machine": platform.machine(),
            "packages": hashlib.sha256(json.dumps(versions).encode()).hexdigest()}


def measure(repo, source):
    from coverage import CoverageData

    with tempfile.TemporaryDirectory() as tmp:
        data_file = Path(tmp) / ".coverage"
        junit = Path(tmp) / "tests.xml"
        env = {**os.environ, "COVERAGE_FILE": str(data_file)}
        subprocess.run([sys.executable, "-m", "pytest", "-q", f"--cov={source}", "--cov-context=test",
                        "--cov-report=", f"--junitxml={junit}"], cwd=repo, env=env, check=True)
        cases = ElementTree.parse(junit).findall(".//testcase")
        counts = {"collected": len(cases), "skipped": sum(c.find("skipped") is not None for c in cases)}
        data = CoverageData(basename=str(data_file))
        data.read()
        tracked = set(os.fsdecode(git(repo, "ls-files", "-z")).split("\0"))
        files = {}
        groups = {}
        for filename in sorted(data.measured_files()):
            path = (repo / filename).resolve()
            if not path.is_relative_to(repo / source):
                continue
            rel = path.relative_to(repo).as_posix()
            if rel not in tracked:
                continue
            # Fixture, import and teardown contexts cannot be attributed to one
            # test: later tests may reuse the resulting module or session state.
            lines = {}
            for line, contexts in data.contexts_by_lineno(filename).items():
                if all(c.endswith("|run") for c in contexts) and contexts:
                    group = tuple(sorted({c.rsplit("|", 1)[0] for c in contexts}))
                    lines[str(line)] = groups.setdefault(group, len(groups))
            files[rel] = lines
    return {"schema": "n4a.pytest-impact/v2", "commit": git(repo, "rev-parse", "HEAD").decode().strip(),
            "source": source, "environment": environment(), "files": files,
            "groups": list(groups), "suite": counts}


def function_lines(text):
    """Only ordinary function bodies are eligible for historical test selection."""
    result = set()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for statement in node.body:
                result.update(range(statement.lineno, statement.end_lineno + 1))
    return result


def selection(repo, base, snapshot, source):
    all_tests = lambda reason: {"scope": "suite", "reason": reason, "tests": []}
    if (snapshot.get("schema") != "n4a.pytest-impact/v2" or snapshot.get("commit") != base or
            snapshot.get("source") != source or snapshot.get("environment") != environment()):
        return all_tests("missing matching coverage for this base and environment")
    raw = git(repo, "diff", "--no-renames", "--name-only", "-z", base, "HEAD", "--")
    files = [p for p in os.fsdecode(raw).split("\0") if p]
    selected = set()
    for path in files:
        edges = snapshot["files"].get(path)
        if not edges or not (repo / path).is_file():
            return all_tests("changed configuration, tests, fixtures or unmeasured source")
        before = git(repo, "show", f"{base}:{path}").decode()
        old_body = function_lines(before)
        new_body = function_lines((repo / path).read_text())
        diff = git(repo, "diff", "--unified=0", "--no-ext-diff", base, "HEAD", "--", path).decode()
        hunks = re.findall(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", diff, re.M)
        if not hunks:
            return all_tests("no comparable source lines")
        for old, nold, new, nnew in hunks:
            old_lines = range(int(old), int(old) + int(nold or 1))
            new_lines = range(int(new), int(new) + int(nnew or 1))
            if (not old_lines or not new_lines or not set(old_lines) <= old_body or
                    not set(new_lines) <= new_body or any(str(i) not in edges for i in old_lines)):
                return all_tests("new, removed, shared or unmeasured lines")
            for line in old_lines:
                selected.update(snapshot["groups"][edges[str(line)]])
    if not selected:
        return all_tests("no measured tests for the diff")
    return {"scope": "tests", "reason": "executed changed lines at the qualified base", "tests": sorted(selected)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["measure", "run"])
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--source", default="src")
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--base")
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    repo = args.checkout.resolve()
    if not (repo / args.source).resolve().is_relative_to(repo) or not (repo / args.source).is_dir():
        parser.error("source must be a directory in the checkout")
    if git(repo, "status", "--porcelain", "--untracked-files=normal"):
        parser.error("coverage requires a clean source checkout")
    decision = {"scope": "suite", "reason": "refresh from a full successful suite", "tests": []}
    if args.mode == "run":
        if not re.fullmatch(r"[0-9a-f]{40}", args.base or ""):
            parser.error("run requires the full base commit")
        graph = json.loads(args.graph.read_text()) if args.graph.exists() else {}
        decision = selection(repo, args.base, graph, args.source)
    if decision["scope"] == "suite":
        graph = measure(repo, args.source)
        args.graph.write_text(json.dumps(graph, sort_keys=True) + "\n")
        decision["suite"] = graph["suite"]
    else:
        subprocess.run([sys.executable, "-m", "pytest", "-q", "--", *decision["tests"]], cwd=repo, check=True)
    decision.update({"base": args.base, "head": git(repo, "rev-parse", "HEAD").decode().strip()})
    args.receipt.write_text(json.dumps(decision, indent=2) + "\n")


if __name__ == "__main__":
    main()
