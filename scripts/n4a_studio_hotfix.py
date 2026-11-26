"""Plan a bounded DAG-ML hotfix for a tagged Studio baseline."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

import n4a_release_lock as release_lock
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

SCHEMA = "n4a.studio-hotfix-plan/v1"
COHORT_SCHEMA = "nirs4all.studio.runtime-cohort.v1"
SHA = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"[0-9a-f]{64}")
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
DAG_CRATES = ("dag-ml-core", "dag-ml-results", "dag-ml")
CHANNELS = ("linux-standard", "linux-offline", "windows-standard", "windows-offline", "macos-arm64", "docker")
WHEEL_TARGETS = ("linux-x64", "win32-x64", "darwin-arm64")
NATIVE_PATH = re.compile(r"crates/(?:dag-ml|dag-ml-core|dag-ml-results)/src/.+\.rs")
PYTHON_PATH = re.compile(r"crates/dag-ml-py/(?:python/dag_ml/.+\.pyi?|src/.+\.rs)")


def version(value: str) -> Version:
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        raise ValueError(f"expected a stable X.Y.Z version, got {value!r}")
    return Version(value)


def commit(repo: Path, ref: str) -> str:
    return release_lock.run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], repo)


def source(repo: Path, ref: str, path: str) -> bytes:
    return release_lock.run_bytes(["git", "show", f"{ref}:{path}"], repo)


def toml(repo: Path, ref: str, path: str) -> dict[str, Any]:
    return tomllib.loads(source(repo, ref, path).decode())


def is_doc(path: str) -> bool:
    return path in {"README.md", "CHANGELOG.md", "AGENTS.md", "CLAUDE.md"} or (
        path.startswith("docs/") and path.endswith(".md")
    )


def release_metadata_only(repo: Path, base: str, candidate: str, path: str, old: str, new: str) -> bool:
    """Recognize a lockstep DAG version edit while retaining dependency changes."""
    if old == new or path not in {
        "Cargo.toml",
        "Cargo.lock",
        "crates/dag-ml-py/Cargo.toml",
        "crates/dag-ml-py/Cargo.lock",
        "crates/dag-ml-py/pyproject.toml",
    }:
        return False
    before, after = (toml(repo, ref, path) for ref in (base, candidate))
    if path.endswith("Cargo.lock"):
        owned = {
            package["name"]
            for package in before["package"]
            if "source" not in package and package["name"].startswith("dag-ml") and package["version"] == old
        }
        for package in before["package"]:
            if "source" not in package and package["name"] in owned and package["version"] == old:
                package["version"] = new
            for index, entry in enumerate(package.get("dependencies", [])):
                if any(entry == f"{name} {old}" for name in owned):
                    package["dependencies"][index] = f"{entry.split()[0]} {new}"
    elif path == "crates/dag-ml-py/pyproject.toml":
        if before["project"]["version"] == old:
            before["project"]["version"] = new
    else:
        table = before["workspace"] if path == "Cargo.toml" else before
        if table["package"]["version"] == old:
            table["package"]["version"] = new
        for item in table.get("dependencies", {}).values():
            if isinstance(item, dict) and "path" in item and item.get("version") == old:
                item["version"] = new
    return before == after


def delivery_stages(native: bool, *, freeze_dag: bool) -> dict[str, list[str]]:
    """Return prospective dependencies for the artifact-based workflows."""
    dag_source = ["freeze-dag-release-source"] if freeze_dag else []
    cohort_gate = "qualify-sdk-wheel-in-cohort"
    studio_gate = "qualify-studio-source-cohort"
    stages = {
        "build-dag-wheel": dag_source,
        "qualify-dag-wheel": ["build-dag-wheel"],
        "verify-retained-sdk-wheel": [],
        "publish-dag-pypi": ["qualify-dag-wheel", cohort_gate, studio_gate],
        "verify-dag-pypi": ["publish-dag-pypi"],
    }
    if freeze_dag:
        stages["freeze-dag-release-source"] = []
    assembly_inputs = ["build-dag-wheel"]
    test_inputs = ["qualify-dag-wheel", "verify-retained-sdk-wheel"]
    public_inputs = ["verify-dag-pypi"]
    if native:
        stages.update(
            {
                "qualify-dag-crates": dag_source,
                "freeze-core-release-source": [],
                "build-core-wheel": [*dag_source, "freeze-core-release-source"],
                "qualify-core-wheel": ["build-core-wheel"],
                "prepare-studio-sidecar": dag_source,
                "publish-dag-crates": ["qualify-dag-crates", cohort_gate, studio_gate],
                "verify-dag-crates": ["publish-dag-crates"],
                "publish-core-pypi": ["qualify-core-wheel", cohort_gate, studio_gate, "verify-dag-crates"],
                "verify-core-pypi": ["publish-core-pypi"],
            }
        )
        assembly_inputs += ["build-core-wheel"]
        test_inputs += ["qualify-core-wheel"]
        public_inputs += ["verify-dag-crates", "verify-core-pypi"]
    else:
        stages["verify-retained-core-wheel"] = []
        stages["prepare-studio-sidecar"] = []
        assembly_inputs += ["verify-retained-core-wheel"]
        test_inputs += ["verify-retained-core-wheel"]
    stages[cohort_gate] = test_inputs
    stages[studio_gate] = [cohort_gate, "prepare-studio-sidecar"]
    stages["freeze-studio-release-source"] = assembly_inputs
    for channel in CHANNELS:
        assemble = f"assemble-studio-{channel}"
        candidate = f"qualify-studio-{channel}"
        stages[assemble] = ["freeze-studio-release-source", "prepare-studio-sidecar"]
        stages[candidate] = [assemble, studio_gate]
        if channel == "macos-arm64":
            stages[candidate] += public_inputs  # The installed smoke pulls from the registry.
        stages[f"publish-studio-{channel}"] = [candidate, *public_inputs]
        stages[f"verify-studio-{channel}"] = [f"publish-studio-{channel}"]
    stages["refresh-and-verify-cockpit"] = [f"verify-studio-{channel}" for channel in CHANNELS]
    return stages


def baseline_wheels(studio: Path, ref: str, members: dict[str, Any]) -> dict[str, Any]:
    """Record the selected wheel bytes per Studio target and detect pin drift."""
    wanted = {"dag-ml": members["dag"], "nirs4all-core": members["core"], "nirs4all": members["sdk"]}
    locks = {}
    for target in WHEEL_TARGETS:
        raw = source(studio, ref, f"build/constraints/python-wheels-{target}.json")
        lock = json.loads(raw)
        if lock["schema"] != "nirs4all.studio.python-wheel-lock.v1" or lock["target"] != target:
            raise ValueError(f"unrecognized Studio wheel lock for {target}")
        wheels = [item for item in lock["packages"] if item["name"] in wanted]
        if sorted(wheel["name"] for wheel in wheels) != sorted(wanted):
            raise ValueError(f"Studio wheel lock for {target} has missing or duplicate runtime wheels")
        for wheel in wheels:
            pin = wanted[wheel["name"]]
            if wheel["version"] != pin["version"] or not SHA256.fullmatch(wheel["sha256"]):
                raise ValueError(f"Studio wheel lock for {target} disagrees with {wheel['name']}")
            if wheel["name"] == "nirs4all" and wheel["sha256"] != pin["wheel_sha256"]:
                raise ValueError(f"Studio wheel lock for {target} disagrees with the SDK digest")
        locks[target] = {"lock_digest": release_lock.sha256_bytes(raw), "runtime_wheels": wheels}
    return locks


def draft_plan(
    workspace: Path, studio_tag: str, studio_sha: str, dag_sha: str, target: str, *, compatible_patch: bool
) -> dict[str, Any]:
    """Read only Git objects and report the work required to deliver a candidate."""
    proposed = version(target)
    studio_version = version(studio_tag)
    if not SHA.fullmatch(studio_sha) or not SHA.fullmatch(dag_sha):
        raise ValueError("Studio and DAG-ML require exact 40-character source commits")
    studio, dag, sdk, core = (workspace / name for name in ("nirs4all-studio", "dag-ml", "nirs4all", "nirs4all-core"))
    if commit(studio, f"refs/tags/{studio_tag}") != studio_sha:
        raise ValueError(f"Studio tag {studio_tag} does not resolve to {studio_sha}")
    cohort_bytes = source(studio, studio_sha, "build/runtime-cohort.json")
    cohort = json.loads(cohort_bytes)
    if cohort["schema"] != COHORT_SCHEMA:
        raise ValueError(f"unsupported Studio runtime cohort schema {cohort['schema']!r}")
    config = json.loads(source(studio, studio_sha, "recommended-config.json"))
    pins = {item["name"]: item for item in config["required"]}
    for package, member in (("dag-ml", "dag"), ("nirs4all-core", "core"), ("nirs4all", "sdk")):
        if pins[package]["install"] != cohort[member]["version"]:
            raise ValueError(f"Studio install pin disagrees with the selected {package} version")
    base_version = version(cohort["dag"]["version"])
    base = commit(dag, f"refs/tags/v{base_version}")
    if base != cohort["dag"]["source_sha"]:
        raise ValueError("Studio DAG-ML source does not match its release tag")
    if commit(dag, dag_sha) != dag_sha:
        raise ValueError("DAG-ML candidate must name a commit")
    release_lock.run(["git", "merge-base", "--is-ancestor", base, dag_sha], dag)
    lock_bytes = source(studio, studio_sha, "sidecar/Cargo.lock")
    locked = tomllib.loads(lock_bytes.decode())["package"]
    crates = [item for item in locked if item["name"] in DAG_CRATES]
    if sorted(item["name"] for item in crates) != sorted(DAG_CRATES) or any(
        item["version"] != str(base_version)
        or not item.get("source", "").startswith("registry+")
        or not SHA256.fullmatch(item.get("checksum", ""))
        for item in crates
    ):
        raise ValueError("Studio sidecar lock does not match the supported DAG-ML crate cohort")
    core_lock = [item for item in locked if item["name"] == "nirs4all"]
    if (
        len(core_lock) != 1
        or core_lock[0]["version"] != cohort["core"]["native_version"]
        or not (
            core_lock[0].get("source", "").startswith("registry+")
            and SHA256.fullmatch(core_lock[0].get("checksum", ""))
            and "dag-ml-core" in core_lock[0].get("dependencies", [])
        )
    ):
        raise ValueError("Studio sidecar lock does not match the Core crate cohort")

    raw_paths = release_lock.run_bytes(
        [
            "git",
            "diff",
            "--no-ext-diff",
            "--no-renames",
            "--name-only",
            "-z",
            base,
            dag_sha,
            "--",
        ],
        dag,
    )
    changed = sorted(path.decode() for path in raw_paths.split(b"\0") if path)
    source_version = version(toml(dag, dag_sha, "Cargo.toml")["workspace"]["package"]["version"])
    py_version = version(toml(dag, dag_sha, "crates/dag-ml-py/pyproject.toml")["project"]["version"])
    delta = [
        path
        for path in changed
        if not is_doc(path)
        and not release_metadata_only(dag, base, dag_sha, path, str(base_version), str(source_version))
    ]
    native = any(NATIVE_PATH.fullmatch(path) for path in delta)
    unclassified = [
        path
        for path in delta
        if not (
            NATIVE_PATH.fullmatch(path) or PYTHON_PATH.fullmatch(path) or path.startswith("crates/dag-ml-py/tests/")
        )
    ]
    executable_delta = any(NATIVE_PATH.fullmatch(path) or PYTHON_PATH.fullmatch(path) for path in delta)
    plan = {
        "schema_version": SCHEMA,
        "baseline": {
            "studio_tag": str(studio_version),
            "studio_commit": studio_sha,
            "runtime_cohort_digest": release_lock.sha256_bytes(cohort_bytes),
            "sidecar_lock_digest": release_lock.sha256_bytes(lock_bytes),
            "members": cohort,
            "python_wheel_locks": baseline_wheels(studio, studio_sha, cohort),
        },
        "candidate": {
            "dag_commit": dag_sha,
            "dag_version": target,
            "source_version": str(source_version),
            "python_source_version": str(py_version),
            "changed_paths": changed,
        },
        "status": "no-runtime-change",
        "blockers": [],
        "release_ready": False,
        "artifacts": {},
        "stages": {},
    }
    if not executable_delta and not unclassified:
        return plan
    blockers = plan["blockers"]
    if unclassified:
        blockers.append(f"unclassified source paths require full planning: {', '.join(unclassified)}")
    if not compatible_patch:
        blockers.append("owner patch classification is required for the hotfix route")
    if proposed.release[:2] != base_version.release[:2] or proposed <= base_version:
        blockers.append(f"DAG-ML {target} must be a forward patch of the tested {base_version} series")
    if source_version != py_version or source_version not in (base_version, proposed):
        blockers.append("DAG-ML workspace and Python version must agree with the baseline or target version")

    core_version = version(cohort["core"]["version"])
    core_candidate = (
        f"{core_version.major}.{core_version.minor}.{core_version.micro + 1}" if native else str(core_version)
    )
    targets = {"dag-ml": target, "nirs4all-core": core_candidate}
    sdk_identity = cohort["sdk"]
    if sdk_identity["publication_status"] != "published-registry" or not SHA256.fullmatch(
        sdk_identity["wheel_sha256"]
    ):
        blockers.append("SDK reuse requires the Studio baseline's published wheel digest")
    for identity in (sdk_identity["source_sha"], cohort["core"]["native_source_sha"]):
        if not SHA.fullmatch(identity):
            raise ValueError("SDK and Core identities must contain exact source commits")
    sdk_requirements = [
        Requirement(raw) for raw in toml(sdk, sdk_identity["source_sha"], "pyproject.toml")["project"]["dependencies"]
    ]
    for name, selected in targets.items():
        if selected not in SpecifierSet(pins[name]["range"]):
            blockers.append(f"Studio admission range for {name} excludes {selected}")
        reqs = [
            requirement for requirement in sdk_requirements if requirement.name == name and requirement.marker is None
        ]
        if len(reqs) != 1 or selected not in reqs[0].specifier:
            blockers.append(f"the retained SDK has no unconditional requirement admitting {name} {selected}")
    if native:
        core_deps = toml(core, cohort["core"]["native_source_sha"], "bindings/rust/nirs4all/Cargo.toml")[
            "dependencies"
        ]
        # The current Core contract declares the same bare 0.x series for all three crates.
        expected_series = f"{base_version.major}.{base_version.minor}"
        requirements = {}
        for name, value in core_deps.items():
            package, spec = (
                (value.get("package", name), value.get("version")) if isinstance(value, dict) else (name, value)
            )
            requirements.setdefault(package, []).append(spec)
        for dep in DAG_CRATES:
            if base_version.major != 0 or requirements.get(dep) != [expected_series]:
                blockers.append(f"Core crate dependency {dep} requires explicit version review")
    if blockers:
        plan["status"] = "requires-full-plan"
        return plan

    plan["status"] = "candidate-plan"
    plan["scope"] = "native-runtime" if native else "python-binding"
    freeze_dag = source_version != proposed
    plan["candidate"].update(
        {
            "version_metadata_pending": freeze_dag,
            "dag_release_source_commit": None if freeze_dag else dag_sha,
            "core_release_source_commit": None if native else cohort["core"]["source_sha"],
            "studio_release_source_commit": None,
        }
    )
    plan["artifacts"] = {
        "dag-wheel": {"action": "build", "version": target},
        "sdk-wheel": {
            "action": "reuse-and-requalify",
            "version": sdk_identity["version"],
            "sha256": sdk_identity["wheel_sha256"],
            "url": sdk_identity["wheel_url"],
        },
        "core-wheel": {"action": "build" if native else "retain-installed-version", "version": core_candidate},
        "core-crate": {
            "action": "reuse",
            "version": core_lock[0]["version"],
            "checksum": core_lock[0].get("checksum"),
        },
        "studio-sidecar": {"action": "build" if native else "reuse-if-inputs-match"},
        "studio-deliveries": {"action": "assemble-and-qualify", "channels": list(CHANNELS)},
    }
    if native:
        plan["artifacts"]["dag-crates"] = {"action": "build", "packages": list(DAG_CRATES), "version": target}
    plan["stages"] = delivery_stages(native, freeze_dag=freeze_dag)
    return plan
