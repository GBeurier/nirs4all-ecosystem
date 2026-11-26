#!/usr/bin/env python3
"""Map default-branch changes to one deduplicated ecosystem artifact plan."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from n4a_artifact_graph import DEFAULT_GRAPH, ROOT, load_graph, plan

RULES = ROOT / "docs/contracts/release/artifact-source-paths.json"
SHA = re.compile(r"[a-f0-9]{40}")


def classify(artifacts, rules, repo, paths):
    owned = {key for key, value in artifacts.items() if value["repository"] == repo}
    if not owned:
        raise ValueError(f"unknown repository: {repo}")
    roots = set()
    for path in paths or []:
        matches = {key for prefix, keys in rules.get(repo, {}).items()
                   if path.startswith(prefix) for key in keys}
        if not matches:
            return owned, "repository"
        roots.update(matches)
    if paths is None:
        return owned, "repository"
    return roots, "paths"


def load_rules(artifacts):
    rules = json.loads(RULES.read_text())
    for repo, mapping in rules.items():
        for prefix, keys in mapping.items():
            if (not prefix.endswith("/") or not keys or
                    any(artifacts[k]["repository"] != repo for k in keys)):
                raise ValueError(f"invalid source mapping: {repo}/{prefix}")
    return rules


def repositories():
    rows = subprocess.check_output(
        ["git", "config", "-f", str(ROOT / ".gitmodules"), "--get-regexp", r"^submodule\..*\.url$"],
        text=True,
    )
    result = {"nirs4all-ecosystem": "GBeurier/nirs4all-ecosystem"}
    for row in rows.splitlines():
        key, url = row.split()
        repo = key.removeprefix("submodule.").removesuffix(".url")
        match = re.fullmatch(r"https://github\.com/([\w.-]+/[\w.-]+)\.git", url)
        if not match or match[1].split("/")[1] != repo:
            raise ValueError(f"invalid public origin for {repo}")
        result[repo] = match[1]
    return result


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "n4a-weekday-planner"}
    if token := os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request("https://api.github.com/" + path, headers=headers), timeout=30) as response:
        return json.load(response)


def comparison_paths(comparison):
    # GitHub's compare API caps the changed-file list at 300. A rewritten
    # branch can omit removed material when diffed from its merge base.
    files = comparison.get("files")
    if comparison["status"] != "ahead" or not files or len(files) >= 300:
        return None
    return sorted({name for entry in files
                   for name in [entry["filename"], entry.get("previous_filename")] if name})


def inspect(item, baseline):
    repo, origin = item
    head = api(f"repos/{origin}/commits/HEAD")["sha"]
    base = baseline[repo]
    if not all(SHA.fullmatch(value) for value in (head, base)):
        raise ValueError(f"invalid revision for {repo}")
    if head == base:
        return repo, head, []
    try:
        comparison = api(f"repos/{origin}/compare/{base}...{head}")
    except HTTPError as error:
        if error.code not in {404, 409}:
            raise
        return repo, head, None
    return repo, head, comparison_paths(comparison)


def test_routes(artifacts, ids):
    """Keep a full owner gate for each surface without a qualified narrower suite."""
    routes = {}
    for key in sorted(ids):
        artifact = artifacts[key]
        repo = artifact["repository"]
        if key.endswith(".native-cli"):
            suite = "cargo:" + Path(artifact["evidence"][0]).parent.name
        elif key == "tools.python-wheel":
            suite = "pytest:tools"
        else:
            suite = "owner-gates"
        routes.setdefault(repo, {}).setdefault(suite, []).append(key)
    return routes


def cli_packages(artifacts, origins, heads, selected):
    result = []
    for key in sorted(selected):
        if key.endswith(".native-cli"):
            artifact = artifacts[key]
            repo = artifact["repository"]
            package = Path(artifact["evidence"][0]).parent.name
            if not re.fullmatch(r"[a-z0-9-]+", package) or not SHA.fullmatch(heads[repo]):
                raise ValueError(f"invalid native CLI identity: {key}")
            result.append({"origin": origins[repo], "package": package, "sha": heads[repo]})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--full-cargo-tests", action="store_true", help="Refresh the public Cargo test inventory")
    parser.add_argument("--all-test-routes", action="store_true")
    parser.add_argument("--weekly-cli", action="store_true", help="Select all CLI packages at the pinned gitlinks")
    parser.add_argument("--cursor", type=Path)
    parser.add_argument("--cargo-inventory", type=Path, help="Cache pinned Cargo manifests for public scans")
    parser.add_argument("--repository", help="Use a local Git diff for one repository")
    parser.add_argument("--checkout", type=Path)
    parser.add_argument("--base")
    parser.add_argument("--head")
    args = parser.parse_args()
    artifacts, order = load_graph(DEFAULT_GRAPH)
    rules = load_rules(artifacts)
    baseline = json.loads(DEFAULT_GRAPH.read_text())["reviewed_sources"]
    origins = repositories()
    if args.all_test_routes:
        args.output.write_text(json.dumps(test_routes(artifacts, artifacts), indent=2) + "\n")
        return
    if args.weekly_cli:
        rows = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "HEAD"], text=True).splitlines()
        pins = {row.split()[3]: row.split()[2] for row in rows if row.startswith("160000 commit ")}
        args.output.write_text(json.dumps(cli_packages(artifacts, origins, pins, artifacts)) + "\n")
        return
    if args.repository:
        if not args.checkout or not all(SHA.fullmatch(v or "") for v in (args.base, args.head)):
            parser.error("local selection requires --checkout and two full commit SHAs")
        files = subprocess.check_output(["git", "-C", str(args.checkout), "diff", "--no-renames",
                                         "--name-only", "-z", args.base, args.head, "--"])
        changes = [(args.repository, args.head, os.fsdecode(files).split("\0")[:-1])]
        baseline[args.repository] = args.base
    else:
        if args.checkout or args.head or args.base or not args.cursor:
            parser.error("public scan requires --cursor and no local selection")
        if args.cursor.exists():
            baseline.update(json.loads(args.cursor.read_text()))
        with ThreadPoolExecutor(max_workers=5) as pool:
            changes = list(pool.map(lambda item: inspect(item, baseline), sorted(origins.items())))

    roots, sources, heads, crate_changes = set(), {}, {}, {}
    for repo, head, paths in changes:
        heads[repo] = head
        if baseline[repo] == head:
            continue
        selected, scope = classify(artifacts, rules, repo, paths)
        roots.update(selected)
        crate_changes[repo] = (paths, scope)
        sources[repo] = {"base": baseline[repo], "head": head, "scope": scope, "roots": sorted(selected)}
    result = {
        "schema_version": "n4a.weekday-impact/v1",
        "sources": sources,
        "unwatched_repositories": sorted(set(baseline) - origins.keys()),
        "plan": plan(artifacts, order, roots, set(), full=False) if roots else None,
    }
    result["test_suites"] = test_routes(artifacts, [
        row["artifact"] for row in (result["plan"] or {}).get("qualification", [])
    ])
    if args.cargo_inventory and args.repository:
        parser.error("--cargo-inventory requires a public scan")
    if args.full_cargo_tests and not args.cargo_inventory:
        parser.error("--full-cargo-tests requires --cargo-inventory")
    if args.cargo_inventory and (sources or args.full_cargo_tests):
        from n4a_crate_impact import affected_crates, fetch_manifests

        cache = json.loads(args.cargo_inventory.read_text()) if args.cargo_inventory.exists() else {}
        for repo, sha in heads.items():
            if cache.get(repo, {}).get("sha") != sha:
                cache[repo] = {"sha": sha, "manifests": fetch_manifests(api, origins[repo], sha)}
        inventory = {repo: cache[repo]["manifests"] for repo in heads}
        result["cargo"] = affected_crates(inventory, origins, crate_changes)
        if args.full_cargo_tests:
            result["cargo_test_inventory"] = {
                repo: {"commit": heads[repo], "packages": {
                    path: {"package": m["package"]["name"], "test_targets": m["_test_targets"]}
                    for path, m in manifests.items() if "package" in m
                }} for repo, manifests in inventory.items()
            }
        packages = result["cargo"]["local_workspace_tests"]
        if packages:
            repo = next(iter(sources))
            result["local_cargo_job"] = {"origin": origins[repo], "sha": heads[repo], "packages": packages}
        args.cargo_inventory.parent.mkdir(parents=True, exist_ok=True)
        args.cargo_inventory.write_text(json.dumps(cache))
    if not args.repository:
        # A locked owner build can qualify a CLI-only source change. Mixed
        # candidates require substitution and must not fall back to a registry.
        candidates = [r["artifact"] for r in (result["plan"] or {}).get("builds", [])
                      if not r["candidate_inputs"] and r["artifact"] in roots
                      and sources[r["repository"]]["scope"] == "paths"]
        result["locked_cli_candidates"] = cli_packages(artifacts, origins, heads, candidates)
        if job := result.get("local_cargo_job"):
            windows_packages = {r["package"] for r in result["locked_cli_candidates"]}
            job["packages"] = [p for p in job["packages"] if p not in windows_packages]
            if not job["packages"]:
                del result["local_cargo_job"]
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    if not args.repository:
        args.cursor.parent.mkdir(parents=True, exist_ok=True)
        args.cursor.write_text(json.dumps(heads, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
