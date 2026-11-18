from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("n4a_cohort", ROOT / "scripts" / "n4a_cohort.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["n4a_cohort"] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


cohort = _load()


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def _repo(path: Path, files: dict[str, str]) -> str:
    path.mkdir(parents=True, exist_ok=True)
    if not (path / ".git").exists():
        _git(path, "init", "-q")
        _git(path, "config", "user.email", "test@example.invalid")
        _git(path, "config", "user.name", "test")
    for rel, body in files.items():
        target = path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body)
    _git(path, "add", "-A")
    _git(path, "commit", "-q", "-m", "fixture", "--allow-empty")
    return _git(path, "rev-parse", "HEAD")


@pytest.mark.parametrize(
    ("requirement", "version", "expected"),
    [
        ("=0.4.2", "0.4.3", False),
        ("=0.4.3", "0.4.3", True),
        ("0.4", "0.4.3", True),
        ("0.4.2", "0.4.3", True),
        ("^0.4.2", "0.4.1", False),
        ("0.3", "0.4.0", False),
        ("~0.3.1", "0.3.6", True),
        ("~0.3.1", "0.4.0", False),
        (">=0.2.16, <0.3", "0.2.17", True),
        (">=0.2.16, <0.3", "0.3.0", False),
        ("1", "1.9.0", True),
        ("0.0.3", "0.0.4", False),
        ("*", "9.9.9", True),
        ("=0.4", "0.4.9", True),
        ("0.4.*", "0.4.9", True),
    ],
)
def test_cargo_requirement_matching(requirement: str, version: str, expected: bool) -> None:
    assert cohort.cargo_req_matches(requirement, version) is expected


def test_rewrite_requirement_keeps_layout_for_every_declaration_style() -> None:
    text = (
        "[package]\nname = \"c\"\nversion = \"0.1.0\"\n\n"
        "[dependencies]\n"
        "dag_ml_crate = { package = \"dag-ml\", version = \"=0.4.2\" }  # pinned\n"
        "nirs4all-io-core = \"=0.3.5\"\n\n"
        "[dependencies.n4m]\nversion = \"=0.4.2\"\nfeatures = [\"dynamic\"]\n\n"
        "[target.'cfg(unix)'.dependencies]\nnix = \"0.29\"\nnirs4all = \"=0.5.0\"\n"
    )
    out = cohort.rewrite_requirement(text, "dependencies", "dag_ml_crate", "=0.4.3")
    out = cohort.rewrite_requirement(out, "dependencies", "nirs4all-io-core", "=0.3.6")
    out = cohort.rewrite_requirement(out, "dependencies", "n4m", "=0.4.3")
    out = cohort.rewrite_requirement(out, "target.cfg(unix).dependencies", "nirs4all", "=0.5.1")
    assert 'dag_ml_crate = { package = "dag-ml", version = "=0.4.3" }  # pinned' in out
    assert 'nirs4all-io-core = "=0.3.6"' in out
    assert '[dependencies.n4m]\nversion = "=0.4.3"' in out
    assert 'nirs4all = "=0.5.1"' in out and 'nix = "0.29"' in out
    with pytest.raises(cohort.CohortError):
        cohort.rewrite_requirement(text, "dependencies", "absent", "=1.0.0")


def test_iter_dependencies_names_renamed_and_target_tables() -> None:
    data = cohort.tomllib.loads(
        "[dependencies]\na = { package = \"dag-ml\", version = \"=0.4.2\" }\nb = { workspace = true }\nlocal = { path = \"x\" }\n"
        "[target.'cfg(windows)'.dev-dependencies]\nc = \"1\"\n[workspace.dependencies]\nd = { path = \"d\", version = \"0.3.5\" }\n"
    )
    found = {(table, key, crate, req, has_path) for table, key, crate, req, has_path in cohort.iter_dependencies(data)}
    assert ("dependencies", "a", "dag-ml", "=0.4.2", False) in found
    assert ("dependencies", "local", "local", None, True) in found
    assert ("target.cfg(windows).dev-dependencies", "c", "c", "1", False) in found
    assert ("workspace.dependencies", "d", "d", "0.3.5", True) in found
    assert not any(key == "b" for _, key, *_ in found)


def test_recipes_cover_the_chain_with_unique_gates() -> None:
    recipes, _ = cohort.load_recipes(cohort.DEFAULT_MEMBERS)
    assert list(recipes) == ["methods", "formats", "dag_ml_data", "io", "dag_ml", "core", "sdk", "studio", "web"]
    ids = [g["id"] for r in recipes.values() for g in r.data.get("gates", [])]
    assert len(ids) == len(set(ids))
    for recipe in recipes.values():
        assert recipe.data.get("version_sources"), recipe.key
        for gate in recipe.data.get("gates", []):
            assert gate.get("tier", "fast") in ("fast", "full")
            assert set(gate.get("needs", [])) <= {"env", "libn4m", "node"}


def test_manifest_defaults_published_and_rejects_unknown_members(tmp_path: Path) -> None:
    recipes, _ = cohort.load_recipes(cohort.DEFAULT_MEMBERS)
    manifest = cohort.load_manifest(None, ["io=path:relative/io"], recipes)
    assert manifest["members"]["core"].published
    assert manifest["members"]["io"].ref == "path:" + str((Path.cwd() / "relative/io").resolve())
    with pytest.raises(cohort.CohortError, match="unknown cohort members"):
        cohort.load_manifest(None, ["lite=published"], recipes)
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"schema_version": cohort.MANIFEST_SCHEMA, "pin_alignment": "maybe", "members": {}}))
    with pytest.raises(cohort.CohortError, match="pin_alignment"):
        cohort.load_manifest(bad, [], recipes)


@pytest.mark.parametrize("name", ["acceptance-20261118.n4a.json", "hosted-check.n4a.json"])
def test_reviewed_manifests_pin_full_commits(name: str) -> None:
    recipes, _ = cohort.load_recipes(cohort.DEFAULT_MEMBERS)
    manifest = cohort.load_manifest(ROOT / "docs/contracts/release/cohort" / name, [], recipes)
    for key, spec in manifest["members"].items():
        assert spec.published or cohort.COMMIT_RE.fullmatch(spec.ref), key
        assert spec.native_ref is None or cohort.COMMIT_RE.fullmatch(spec.native_ref), key


def _recipe(key: str = "demo") -> object:
    return cohort.Recipe(key, {"key": key, "repo": "example/demo", "sibling": "demo"}, 0)


def test_commit_snapshot_writes_only_changed_files_and_keeps_build_outputs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    first = _repo(repo, {"a.txt": "one", "dir/b.txt": "two", "gone.txt": "x"})
    manager = cohort.SourceManager(tmp_path / "build", tmp_path)
    spec = cohort.MemberSpec("demo", first, source=str(repo))
    snap = manager.snapshot_commit(_recipe(), spec, first)
    assert snap.changed == 3 and (snap.root / "dir/b.txt").read_text() == "two"
    (snap.root / "target-output.bin").write_text("built")
    assert manager.snapshot_commit(_recipe(), spec, first).changed == 0
    (repo / "gone.txt").unlink()
    second = _repo(repo, {"a.txt": "changed"})
    snap = manager.snapshot_commit(_recipe(), cohort.MemberSpec("demo", second, source=str(repo)), second)
    assert snap.changed == 1
    assert not (snap.root / "gone.txt").exists()
    assert (snap.root / "target-output.bin").exists()
    assert snap.original_text("a.txt") == "changed"


def test_path_snapshot_tracks_dirty_working_tree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _repo(repo, {"a.txt": "one"})
    manager = cohort.SourceManager(tmp_path / "build", tmp_path)
    spec = cohort.MemberSpec("demo", f"path:{repo}")
    snap = manager.snapshot_path(_recipe(), spec)
    assert not snap.dirty and snap.changed == 1
    (repo / "new.txt").write_text("untracked")
    snap2 = manager.snapshot_path(_recipe(), spec)
    assert snap2.dirty and snap2.changed == 1 and snap2.digest != snap.digest
    assert (snap2.root / "new.txt").read_text() == "untracked"


def test_lock_check_reports_registry_copies_of_cohort_crates(tmp_path: Path) -> None:
    lock = tmp_path / "Cargo.lock"
    lock.write_text(
        "[[package]]\nname = \"dag-ml\"\nversion = \"0.4.2\"\nsource = \"registry+https://github.com/rust-lang/crates.io-index\"\n\n"
        "[[package]]\nname = \"nirs4all-io\"\nversion = \"0.3.6\"\n"
    )
    instance = object.__new__(cohort.Cohort)
    instance.crates = {"dag-ml": {"version": "0.4.3"}, "nirs4all-io": {"version": "0.3.6"}}
    problems = cohort.Cohort.lock_check(instance, "core", lock)
    assert len(problems) == 1 and problems[0].startswith("dag-ml 0.4.2 still resolved from crates.io")


STUDIO_REQUIRED = [
    {"name": "nirs4all", "range": ">=1.4.20,<1.5", "install": "1.4.20"},
    {"name": "nirs4all-core", "range": "", "install": "0.5.1"},
    {"name": "nirs4all-methods", "range": ">=1.3,<2", "install": "1.3.19"},
]


def _env_cohort(tmp_path: Path, members: dict, wheels: dict[str, Path] | None = None, required: list | None = None) -> object:
    """A cohort whose Studio is a source member and every other member is as given (published by default)."""
    recipes, _ = cohort.load_recipes(cohort.DEFAULT_MEMBERS)
    manifest_path = tmp_path / "cohort.json"
    manifest_path.write_text(json.dumps({"schema_version": cohort.MANIFEST_SCHEMA, "members": {"studio": "1" * 40, **members}}))
    studio = tmp_path / "studio"
    studio.mkdir()
    (studio / "recommended-config.json").write_text(json.dumps({"required": STUDIO_REQUIRED if required is None else required}))
    instance = object.__new__(cohort.Cohort)
    instance.recipes = recipes
    instance.manifest = cohort.load_manifest(manifest_path, [], recipes)
    instance.snapshots = {"studio": cohort.Snapshot("studio", "commit", studio, "1" * 40, None, False, "d", {}, "src")}
    instance.wheels = wheels or {}
    return instance


def test_published_python_members_are_installed_for_the_studio_consumer(tmp_path: Path) -> None:
    # Every Python member published (hosted run 44345001551): no wheel is built, so the
    # environment used to be empty and Studio's end-to-end run found no scientific host.
    assert cohort.Cohort.consumer_requirements(_env_cohort(tmp_path, {})) == [
        "nirs4all>=1.4.20,<1.5", "nirs4all-core", "nirs4all-methods>=1.3,<2"]


def test_published_member_version_and_cohort_wheels_take_precedence(tmp_path: Path) -> None:
    instance = _env_cohort(tmp_path, {"sdk": {"ref": "published", "version": "1.4.20"}, "core": "2" * 40},
                           wheels={"nirs4all-core": tmp_path / "nirs4all_core-0.6.0-py3-none-any.whl"})
    assert cohort.Cohort.consumer_requirements(instance) == ["nirs4all==1.4.20", "nirs4all-methods>=1.3,<2"]


def test_studio_without_declared_requirements_is_refused(tmp_path: Path) -> None:
    with pytest.raises(cohort.CohortError, match="declares no 'required' Python requirements"):
        cohort.Cohort.consumer_requirements(_env_cohort(tmp_path, {}, required=[]))


def test_an_environment_with_nothing_to_install_is_refused(tmp_path: Path) -> None:
    instance = _env_cohort(tmp_path, {})
    instance.snapshots = {}
    instance.build = instance.cargo_target = instance.run_dir = tmp_path
    with pytest.raises(cohort.CohortError, match="nothing to install"):
        cohort.Cohort.build_env(instance)


def _report(**overrides: object) -> dict:
    report = {
        "schema_version": cohort.REPORT_SCHEMA, "cohort_id": "t", "run_id": "r", "manifest_digest": "ab" * 32,
        "tier": "fast", "result": "passed", "first_failure": None, "alignments": [], "requirements": [],
        "python_requirement_mismatches": [],
        "members": {"io": {"ref": "x", "published": False, "kind": "commit", "commit": "1" * 40, "dirty": False,
                           "versions": {"sources": {"rust_workspace": "0.3.6", "python": "0.3.6"}, "crates": {"nirs4all-io": "0.3.6"}}},
                    "core": {"ref": "published", "published": True}},
    }
    report.update(overrides)
    return report


def _plan_args(tmp_path: Path, report: dict, **extra: object) -> argparse.Namespace:
    path = tmp_path / "report.json"
    path.write_text(json.dumps(report))
    values = {"report": str(path), "members": str(cohort.DEFAULT_MEMBERS), "workspace_root": str(tmp_path),
              "offline": True, "json_out": str(tmp_path / "plan.json"), "execute": False, "confirm": "",
              "expected_login": "GBeurier", "wait_minutes": 1}
    values.update(extra)
    return argparse.Namespace(**values)


def test_release_plan_refuses_failed_runs_and_aligned_pins(tmp_path: Path) -> None:
    alignment = {"consumer": "core", "manifest": "Cargo.toml", "crate": "nirs4all-io", "requirement": "=0.3.5", "cohort_version": "0.3.6"}
    report = _report(result="failed", first_failure={"layer": "core", "name": "core-cargo-test"}, alignments=[alignment])
    assert cohort.release_plan(_plan_args(tmp_path, report)) == 2
    plan = json.loads((tmp_path / "plan.json").read_text())
    text = "\n".join(plan["blockers"])
    assert "failed, not passed" in text and "pins were aligned" in text
    assert any("must require nirs4all-io 0.3.6" in line for line in plan["consumer_pin_updates"])


def test_release_plan_orders_members_and_requires_confirmation(tmp_path: Path) -> None:
    report = _report()
    assert cohort.release_plan(_plan_args(tmp_path, report)) == 2  # commit is absent from the (empty) sibling
    plan = json.loads((tmp_path / "plan.json").read_text())
    assert [item["member"] for item in plan["plan"]] == ["io"]
    assert plan["plan"][0]["tags"] == ["v0.3.6"]
    assert cohort.release_plan(_plan_args(tmp_path, report, execute=True)) == 2


def test_workflow_triggers_read_the_tested_commit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    commit = _repo(repo, {
        ".github/workflows/release.yml": "on:\n  push:\n    tags: ['v[0-9]*']\njobs: {}\n",
        ".github/workflows/publish.yml": "on:\n  release:\n    types: [published]\njobs: {}\n",
        ".github/workflows/ci.yml": "on: [push]\njobs: {}\n",
    })
    tags, releases = cohort.workflow_triggers(repo, commit)
    assert tags == ["release.yml (tags v[0-9]*)"] and releases == ["publish.yml"]
