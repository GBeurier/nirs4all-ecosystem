from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load_release_lock() -> ModuleType:
    path = ROOT / "scripts" / "n4a_release_lock.py"
    spec = importlib.util.spec_from_file_location("n4a_release_lock", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _init_repo(repo: Path) -> None:
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "release-lock-test@example.invalid")
    _git(repo, "config", "user.name", "Release Lock Test")


def _commit_all(repo: Path, message: str = "fixture") -> None:
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", message)


def test_collect_versions_rejects_ignored_generated_package_source(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / ".gitignore").write_text("generated/\n", encoding="utf-8")
    (repo / "tracked.toml").write_text('[project]\nversion = "1.0.1"\n', encoding="utf-8")
    (repo / "generated").mkdir()
    (repo / "generated" / "pyproject.toml").write_text(
        '[project]\nversion = "1.0.0"\n',
        encoding="utf-8",
    )
    _commit_all(repo)

    component = {
        "key": "methods",
        "version_sources": [
            {
                "key": "python_generated",
                "kind": "toml",
                "path": "generated/pyproject.toml",
                "field": "project.version",
            }
        ],
    }

    with pytest.raises(release_lock.RelError, match="path is not tracked by git"):
        release_lock.collect_versions(repo, component)


def test_collect_versions_records_tracked_generated_metadata_annotations(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    repo = tmp_path / "repo"
    _init_repo(repo)
    pyproject = repo / "bindings" / "python" / "pyproject.toml"
    pyproject.parent.mkdir(parents=True)
    pyproject.write_text('[project]\nversion = "1.0.1"\n', encoding="utf-8")
    _commit_all(repo)

    component = {
        "key": "methods",
        "version_sources": [
            {
                "key": "python_nirs4all_methods",
                "kind": "toml",
                "path": "bindings/python/pyproject.toml",
                "field": "project.version",
                "distribution": "nirs4all-methods",
                "module": "n4m",
                "generated_by": "bindings/python/scripts/make_python_package.py",
                "generated_output_path": "bindings/python_nirs4all_methods/pyproject.toml",
                "metadata_source": "tracked source metadata for generated package",
            }
        ],
    }

    versions = release_lock.collect_versions(repo, component)

    assert versions["python_nirs4all_methods"] == {
        "distribution": "nirs4all-methods",
        "generated_by": "bindings/python/scripts/make_python_package.py",
        "generated_output_path": "bindings/python_nirs4all_methods/pyproject.toml",
        "kind": "toml",
        "metadata_source": "tracked source metadata for generated package",
        "module": "n4m",
        "read_from": "tracked_worktree",
        "source": "bindings/python/pyproject.toml",
        "value": "1.0.1",
    }


def test_python_function_json_artifact_reads_git_head_not_dirty_worktree(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    repo = tmp_path / "repo"
    _init_repo(repo)
    topology = repo / "bindings" / "python" / "src" / "nirs4all_lite" / "_topology.py"
    topology.parent.mkdir(parents=True)
    topology.write_text(
        """
from copy import deepcopy

_MANIFEST = {"schema": "demo.release-topology.v1", "value": "committed"}


def release_topology_manifest():
    return deepcopy(_MANIFEST)
""",
        encoding="utf-8",
    )
    _commit_all(repo)
    topology.write_text(
        """
from copy import deepcopy

_MANIFEST = {"schema": "demo.release-topology.v1", "value": "dirty"}


def release_topology_manifest():
    return deepcopy(_MANIFEST)
""",
        encoding="utf-8",
    )

    artifact = {
        "id": "release_topology_manifest",
        "kind": "python_function_json",
        "path": "bindings/python/src/nirs4all_lite/_topology.py",
        "function": "release_topology_manifest",
        "read_from": "git_head",
        "allowed_imports": ["copy"],
        "include_json": True,
    }

    collected = release_lock.collect_contract_artifact(repo, artifact)

    assert collected["read_from"] == "git_head"
    assert collected["source_ref"] == "HEAD"
    assert collected["json"] == {
        "schema": "demo.release-topology.v1",
        "value": "committed",
    }
    assert collected["json_schema"] == "demo.release-topology.v1"


def test_python_function_json_artifact_rejects_unapproved_imports(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    repo = tmp_path / "repo"
    _init_repo(repo)
    topology = repo / "topology.py"
    topology.write_text(
        """
import os


def release_topology_manifest():
    return {"schema": "demo"}
""",
        encoding="utf-8",
    )
    _commit_all(repo)

    artifact = {
        "id": "release_topology_manifest",
        "kind": "python_function_json",
        "path": "topology.py",
        "function": "release_topology_manifest",
        "allowed_imports": [],
    }

    with pytest.raises(release_lock.RelError, match="imports \\['os'\\]"):
        release_lock.collect_contract_artifact(repo, artifact)


def test_central_manifest_declares_reproducible_methods_and_lite_topology_sources() -> None:
    manifest = json.loads(
        (ROOT / "docs" / "contracts" / "release" / "aggregation-manifest.n4a.json").read_text(
            encoding="utf-8"
        )
    )
    components = {component["key"]: component for component in manifest["components"]}
    methods_sources = {
        source["key"]: source for source in components["methods"]["version_sources"]
    }

    for key, distribution, module, generated_path in (
        (
            "python_nirs4all_methods",
            "nirs4all-methods",
            "n4m",
            "bindings/python_nirs4all_methods/pyproject.toml",
        ),
        (
            "python_pls4all",
            "pls4all",
            "pls4all",
            "bindings/python_pls4all/pyproject.toml",
        ),
    ):
        source = methods_sources[key]
        assert source["path"] == "bindings/python/pyproject.toml"
        assert source["field"] == "project.version"
        assert source["distribution"] == distribution
        assert source["module"] == module
        assert source["generated_output_path"] == generated_path

    lite_artifacts = {
        artifact["id"]: artifact
        for artifact in components["lite"].get("contract_artifacts", [])
    }
    topology = lite_artifacts["release_topology_manifest"]
    assert topology["kind"] == "python_function_json"
    assert topology["read_from"] == "git_head"
    assert topology["function"] == "release_topology_manifest"
    assert topology["include_json"] is True
