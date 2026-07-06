#!/usr/bin/env python3
"""Plan and apply public submodule repins without regenerating release locks."""

from __future__ import annotations

import argparse
import configparser
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PROTECTED_LOCK_PATHS = (
    "docs/contracts/release/aggregation-lock.n4a.lock.json",
)


class SubmoduleRepinError(RuntimeError):
    """Submodule repin planning or application failed."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_git(repo: Path, *args: str, allow_fail: bool = False) -> str | None:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        if allow_fail:
            return None
        raise SubmoduleRepinError(
            f"git {' '.join(args)} failed in {repo}:\n{proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def read_gitmodules(root: Path) -> dict[str, dict[str, str]]:
    parser = configparser.ConfigParser()
    if not parser.read(root / ".gitmodules", encoding="utf-8"):
        raise SubmoduleRepinError(f"cannot read {root / '.gitmodules'}")

    submodules: dict[str, dict[str, str]] = {}
    for section in parser.sections():
        if not section.startswith("submodule "):
            continue
        name = section.split('"', 2)[1]
        values = parser[section]
        submodules[name] = {
            "name": name,
            "path": values["path"],
            "url": values["url"],
            "branch": values.get("branch", "main"),
        }
    return submodules


def gitlinks(root: Path) -> dict[str, str]:
    output = run_git(root, "ls-files", "-s")
    assert output is not None
    links: dict[str, str] = {}
    for line in output.splitlines():
        if not line.startswith("160000 "):
            continue
        meta, path = line.split("\t", 1)
        _mode, oid, _stage = meta.split()
        links[path] = oid
    return links


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    return (
        run_git(repo, "merge-base", "--is-ancestor", ancestor, descendant, allow_fail=True)
        == ""
    )


def protected_path_status(root: Path) -> dict[str, str]:
    status: dict[str, str] = {}
    for path in PROTECTED_LOCK_PATHS:
        value = run_git(root, "status", "--short", "--", path, allow_fail=True)
        status[path] = value or "clean"
    return status


def submodule_status(root: Path, rel_path: str) -> str:
    return run_git(root / rel_path, "status", "--porcelain") or ""


def remote_head(root: Path, rel_path: str, branch: str, *, fetch: bool) -> str:
    submodule = root / rel_path
    if not (submodule / ".git").exists():
        raise SubmoduleRepinError(f"submodule checkout is missing: {rel_path}")
    if fetch:
        run_git(submodule, "fetch", "origin", branch, "--tags", "--prune")
    head = run_git(submodule, "rev-parse", f"refs/remotes/origin/{branch}", allow_fail=True)
    if not head:
        raise SubmoduleRepinError(f"{rel_path}: cannot resolve origin/{branch}")
    return head


def relation(repo: Path, current: str, target: str) -> str:
    if current == target:
        return "up_to_date"
    if is_ancestor(repo, current, target):
        return "fast_forward"
    if is_ancestor(repo, target, current):
        return "ahead_of_remote"
    return "diverged"


def build_repin_plan(root: Path, *, fetch: bool = False) -> dict[str, Any]:
    root = root.resolve()
    modules = read_gitmodules(root)
    links = gitlinks(root)
    missing_gitlinks = sorted(set(item["path"] for item in modules.values()) - set(links))
    extra_gitlinks = sorted(set(links) - set(item["path"] for item in modules.values()))
    if missing_gitlinks or extra_gitlinks:
        raise SubmoduleRepinError(
            "gitlink/.gitmodules mismatch: "
            f"missing={missing_gitlinks}, extra={extra_gitlinks}"
        )

    entries: list[dict[str, Any]] = []
    for name in sorted(modules):
        module = modules[name]
        path = module["path"]
        current = links[path]
        target = remote_head(root, path, module["branch"], fetch=fetch)
        worktree_status = submodule_status(root, path)
        state = relation(root / path, current, target)
        entries.append(
            {
                "name": name,
                "path": path,
                "url": module["url"],
                "branch": module["branch"],
                "current": current,
                "remote_head": target,
                "relation": state,
                "dirty": bool(worktree_status),
                "recommended_action": (
                    "checkout_remote_head"
                    if state == "fast_forward" and not worktree_status
                    else "none"
                    if state == "up_to_date"
                    else "manual_review"
                ),
            }
        )

    return {
        "schema_version": "n4a.submodule-repin-plan/v1",
        "repo": str(root),
        "fetch": fetch,
        "protected_paths": protected_path_status(root),
        "totals": {
            "submodules": len(entries),
            "up_to_date": sum(1 for item in entries if item["relation"] == "up_to_date"),
            "fast_forward": sum(1 for item in entries if item["relation"] == "fast_forward"),
            "manual_review": sum(1 for item in entries if item["recommended_action"] == "manual_review"),
            "dirty": sum(1 for item in entries if item["dirty"]),
        },
        "submodules": entries,
    }


def apply_repin_plan(root: Path, plan: dict[str, Any]) -> list[str]:
    updated: list[str] = []
    for item in plan["submodules"]:
        if item["recommended_action"] != "checkout_remote_head":
            continue
        run_git(root / item["path"], "checkout", item["remote_head"])
        run_git(root, "add", item["path"])
        updated.append(item["path"])
    return updated


def print_text_plan(plan: dict[str, Any]) -> None:
    print(
        "submodules={submodules} up_to_date={up_to_date} "
        "fast_forward={fast_forward} manual_review={manual_review} dirty={dirty}".format(
            **plan["totals"]
        )
    )
    for path, status in plan["protected_paths"].items():
        print(f"protected {path}: {status}")
    for item in plan["submodules"]:
        if item["relation"] != "up_to_date" or item["dirty"]:
            print(
                f"{item['path']}: {item['relation']} "
                f"{item['current'][:12]} -> {item['remote_head'][:12]} "
                f"action={item['recommended_action']}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "apply"), nargs="?", default="plan")
    parser.add_argument("--repo-root", type=Path, default=repo_root())
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    try:
        plan = build_repin_plan(args.repo_root, fetch=args.fetch)
        if args.action == "apply":
            updated = apply_repin_plan(args.repo_root.resolve(), plan)
            plan["updated"] = updated
        if args.as_json:
            print(json.dumps(plan, ensure_ascii=True, indent=2, sort_keys=True))
        else:
            print_text_plan(plan)
        return 0
    except SubmoduleRepinError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
