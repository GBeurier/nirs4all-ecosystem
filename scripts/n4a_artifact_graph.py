#!/usr/bin/env python3
"""Plan ecosystem candidate builds and qualification by artifact identity."""

import argparse
import json
import re
import subprocess
import sys
from graphlib import TopologicalSorter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH = ROOT / "docs/contracts/release/artifact-graph.n4a.json"
ACTIONS = {"prepare", "build", "assemble", "qualify", "refresh"}
MATERIAL = {"compile", "bundle"}
TEST_INPUTS = MATERIAL | {"runtime"}
RELATIONS = TEST_INPUTS | {"review", "observe"}


def load_graph(path: Path) -> tuple[dict, list[str]]:
    graph = json.loads(path.read_text(encoding="utf-8"))
    if graph["schema_version"] != "n4a.artifact-graph/v1":
        raise ValueError("unsupported artifact graph schema")
    artifacts = graph["artifacts"]
    if not artifacts:
        raise ValueError("artifact graph is empty")
    sources = graph["reviewed_sources"]
    if set(sources) != {artifact["repository"] for artifact in artifacts.values()} or any(
        not re.fullmatch(r"[0-9a-f]{40}", revision) for revision in sources.values()
    ):
        raise ValueError("expected a reviewed source commit for each repository")
    for artifact_id, artifact in artifacts.items():
        if artifact["action"] not in ACTIONS or not artifact["evidence"]:
            raise ValueError(f"{artifact_id}: expected a known action and source evidence")
        for dependency, relation in artifact["inputs"].items():
            if dependency not in artifacts or relation not in RELATIONS or dependency == artifact_id:
                raise ValueError(f"{artifact_id}: invalid input {dependency} ({relation})")
            if (artifact["action"] == "refresh") != (relation == "observe"):
                raise ValueError(f"{artifact_id}: observation edges belong to refresh nodes")
            if artifacts[dependency]["action"] in {"refresh", "qualify"}:
                raise ValueError(f"{artifact_id}: cannot consume an observation or gate as an artifact")
            if artifact["action"] == "qualify" and relation != "runtime":
                raise ValueError(f"{artifact_id}: qualification gates only declare test inputs")
    order = list(TopologicalSorter({
        artifact_id: sorted(
            dependency for dependency, relation in artifact["inputs"].items() if relation in MATERIAL
        )
        for artifact_id, artifact in sorted(artifacts.items())
    }).static_order())
    return artifacts, order


def plan(
    artifacts: dict, order: list[str], changed: set[str], repositories: set[str], *, full: bool
) -> dict:
    """Calculate candidate and baseline inputs without resolving registry versions."""
    by_repository: dict[str, set[str]] = {}
    for artifact_id, artifact in artifacts.items():
        by_repository.setdefault(artifact["repository"], set()).add(artifact_id)

    unknown = (changed - artifacts.keys()) | (repositories - by_repository.keys())
    if unknown:
        raise ValueError(f"unknown artifact or repository: {', '.join(sorted(unknown))}")
    roots = changed | {artifact_id for repo in repositories for artifact_id in by_repository[repo]}
    if full:
        roots = set(artifacts)
    elif not roots:
        raise ValueError("select at least one artifact, repository or a full qualification")

    candidates: set[str] = set()
    builds = []
    for artifact_id in order:
        artifact = artifacts[artifact_id]
        if artifact["action"] in {"refresh", "qualify"}:
            continue
        material = {dependency for dependency, relation in artifact["inputs"].items() if relation in MATERIAL}
        changed_inputs = material & candidates
        if artifact_id in roots or changed_inputs:
            candidates.add(artifact_id)
            builds.append({
                "artifact": artifact_id,
                "repository": artifact["repository"],
                "action": artifact["action"],
                "candidate_inputs": sorted(changed_inputs),
                "baseline_inputs": sorted(material - candidates),
            })

    # Test runtime profiles after staging candidate bytes. Runtime substitution
    # stops at a material boundary, where the producer has fixed the input bytes.
    qualification = []
    reviews = []
    refresh = []
    for artifact_id in order:
        artifact = artifacts[artifact_id]
        if artifact["action"] == "refresh":
            observed = set(artifact["inputs"]) & candidates
            if artifact_id in roots or observed:
                refresh.append({"artifact": artifact_id, "if_promoted": sorted(observed)})
            continue
        for dependency, relation in artifact["inputs"].items():
            if relation == "review" and dependency in candidates:
                reviews.append({"consumer": artifact_id, "candidate": dependency})
        pending = [(artifact_id, True)]
        visited = set()
        while pending:
            current, runtime_allowed = pending.pop()
            if (current, runtime_allowed) in visited:
                continue
            visited.add((current, runtime_allowed))
            for dependency, relation in artifacts[current]["inputs"].items():
                if relation in MATERIAL or (runtime_allowed and relation == "runtime"):
                    pending.append((dependency, relation == "runtime"))
        closure = {dependency for dependency, _ in visited}
        if artifact["action"] == "qualify":
            closure.remove(artifact_id)
        if artifact_id in roots or closure & candidates:
            qualification.append({
                "artifact": artifact_id,
                "candidate_inputs": sorted(closure & candidates),
                "baseline_inputs": sorted(closure - candidates),
            })

    return {
        "schema_version": "n4a.artifact-plan/v1",
        "mode": "full" if full else "affected",
        "scope": "declared-surfaces",
        "roots": sorted(roots),
        "builds": builds,
        "qualification": qualification,
        "admission_review": reviews,
        "refresh_after_promotion": refresh,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--artifact", action="append", default=[])
    selection.add_argument("--repository", action="append", default=[])
    selection.add_argument("--full", action="store_true")
    args = parser.parse_args()

    try:
        artifacts, order = load_graph(args.graph)
        if args.graph == DEFAULT_GRAPH:
            paths = subprocess.check_output(
                ["git", "config", "--file", str(ROOT / ".gitmodules"), "--get-regexp", r"^submodule\..*\.path$"],
                text=True,
            )
            declared = {artifact["repository"] for artifact in artifacts.values()}
            missing = {line.split(maxsplit=1)[1] for line in paths.splitlines()} - declared
            if missing:
                raise ValueError(f"no graph artifact for: {', '.join(sorted(missing))}")
        result = plan(artifacts, order, set(args.artifact), set(args.repository), full=args.full)
    except (KeyError, TypeError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"{parser.prog}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
