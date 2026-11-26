from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from graphlib import TopologicalSorter
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


def test_published_python_members_default_to_the_versions_studio_ships(tmp_path: Path) -> None:
    # Every Python member published (hosted run 44345001551): no wheel is built, so the
    # environment used to be empty and Studio's end-to-end run found no scientific host.
    # By default the environment reproduces Studio's exact install pins, not the newest admitted release.
    assert cohort.Cohort.consumer_requirements(_env_cohort(tmp_path, {})) == [
        "nirs4all==1.4.20", "nirs4all-core==0.5.1", "nirs4all-methods==1.3.19"]


def test_published_latest_opts_into_the_newest_release_studio_admits(tmp_path: Path) -> None:
    instance = _env_cohort(tmp_path, {"sdk": "published:latest", "core": {"ref": "published:latest"}})
    assert cohort.Cohort.consumer_requirements(instance) == [
        "nirs4all>=1.4.20,<1.5", "nirs4all-core", "nirs4all-methods==1.3.19"]
    assert instance.manifest["members"]["sdk"].published


def test_published_latest_and_an_explicit_version_are_exclusive(tmp_path: Path) -> None:
    with pytest.raises(cohort.CohortError, match="exclusive"):
        _env_cohort(tmp_path, {"sdk": {"ref": "published:latest", "version": "1.4.20"}})


def test_published_member_version_and_cohort_wheels_take_precedence(tmp_path: Path) -> None:
    instance = _env_cohort(tmp_path, {"sdk": {"ref": "published", "version": "1.4.21"}, "core": "2" * 40},
                           wheels={"nirs4all-core": tmp_path / "nirs4all_core-0.6.0-py3-none-any.whl"})
    assert cohort.Cohort.consumer_requirements(instance) == ["nirs4all==1.4.21", "nirs4all-methods==1.3.19"]


def test_studio_requirement_without_an_install_pin_is_refused(tmp_path: Path) -> None:
    instance = _env_cohort(tmp_path, {}, required=[{"name": "nirs4all", "range": ">=1.4.20,<1.5"}])
    with pytest.raises(cohort.CohortError, match="no exact 'install' version for nirs4all"):
        cohort.Cohort.consumer_requirements(instance)


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


@pytest.fixture
def studio_hotfix_baseline(tmp_path: Path) -> tuple[Path, str]:
    dag = tmp_path / "dag-ml"
    dag_base = _repo(dag, {
        "Cargo.toml": '[workspace.package]\nversion = "0.5.0"\n',
        "crates/dag-ml-py/pyproject.toml": '[project]\nname = "dag-ml"\nversion = "0.5.0"\n',
        "crates/dag-ml-core/src/runtime.rs": "fn run() {}\n",
    })
    _git(dag, "tag", "v0.5.0")
    sdk = _repo(tmp_path / "nirs4all", {
        "pyproject.toml": '[project]\ndependencies = ["nirs4all-core>=0.6,<0.7", "dag-ml>=0.5,<0.6"]\n',
    })
    core = _repo(tmp_path / "nirs4all-core", {
        "bindings/rust/nirs4all/Cargo.toml": """[dependencies]
        dag_ml_crate = { package = "dag-ml", version = "0.5" }
        dag-ml-core = "0.5"
        dag_ml_results = { package = "dag-ml-results", version = "0.5" }
        """,
    })
    runtime = {
        "schema": "nirs4all.studio.runtime-cohort.v1",
        "dag": {"version": "0.5.0", "source_sha": dag_base},
        "core": {"source_sha": core, "version": "0.6.1", "native_version": "0.6.1", "native_source_sha": core},
        "sdk": {"version": "1.6.1", "source_sha": sdk, "wheel_sha256": "a" * 64,
                "wheel_url": "https://example.invalid/nirs4all.whl", "publication_status": "published-registry"},
    }
    required = [
        {"name": "dag-ml", "install": "0.5.0", "range": ">=0.5,<0.6"},
        {"name": "nirs4all-core", "install": "0.6.1", "range": ">=0.6,<0.7"},
        {"name": "nirs4all", "install": "1.6.1", "range": ">=1.6,<1.7"},
    ]
    lock = "version = 4\n"
    for name in ("dag-ml", "dag-ml-core", "dag-ml-results", "nirs4all"):
        locked_version = "0.6.1" if name == "nirs4all" else "0.5.0"
        lock += (f'[[package]]\nname = "{name}"\nversion = "{locked_version}"\n'
                 f'source = "registry+https://github.com/rust-lang/crates.io-index"\nchecksum = "{"b" * 64}"\n')
        if name == "nirs4all":
            lock += 'dependencies = ["dag-ml-core"]\n'
    studio = tmp_path / "nirs4all-studio"
    files = {"build/runtime-cohort.json": json.dumps(runtime),
             "recommended-config.json": json.dumps({"required": required}), "sidecar/Cargo.lock": lock}
    for target in ("linux-x64", "win32-x64", "darwin-arm64"):
        files[f"build/constraints/python-wheels-{target}.json"] = json.dumps({
            "schema": "nirs4all.studio.python-wheel-lock.v1",
            "target": target,
            "packages": [{"name": item["name"], "version": item["install"], "sha256": "a" * 64} for item in required],
        })
    sha = _repo(studio, files)
    _git(studio, "tag", "0.19.8")
    return tmp_path, sha


def _studio_hotfix_plan(baseline: tuple[Path, str], changes: dict[str, str], version: str = "0.5.1",
                        approved: bool = True) -> dict:
    from n4a_studio_hotfix import draft_plan

    root, studio = baseline
    dag = _repo(root / "dag-ml", changes)
    return draft_plan(root, "0.19.8", studio, dag, version, compatible_patch=approved)


def test_studio_hotfix_native_starts_independent_builds(studio_hotfix_baseline: tuple[Path, str]) -> None:
    plan = _studio_hotfix_plan(studio_hotfix_baseline, {"crates/dag-ml-core/src/runtime.rs": "fn changed() {}\n"})
    assert plan["status"] == "candidate-plan" and not plan["release_ready"]
    assert plan["scope"] == "native-runtime"
    assert plan["artifacts"]["core-wheel"] == {"action": "build", "version": "0.6.2"}
    assert plan["artifacts"]["core-crate"]["version"] == "0.6.1"
    assert plan["artifacts"]["sdk-wheel"]["sha256"] == "a" * 64
    stages = plan["stages"]
    assert plan["candidate"]["dag_release_source_commit"] is None
    assert stages["freeze-dag-release-source"] == stages["freeze-core-release-source"] == []
    assert stages["build-dag-wheel"] == stages["prepare-studio-sidecar"] == ["freeze-dag-release-source"]
    assert stages["build-core-wheel"] == ["freeze-dag-release-source", "freeze-core-release-source"]
    assert all(dependency in stages for dependencies in stages.values() for dependency in dependencies)
    order = list(TopologicalSorter(stages).static_order())
    for publisher in ("publish-dag-pypi", "publish-dag-crates", "publish-core-pypi"):
        assert "qualify-sdk-wheel-in-cohort" in stages[publisher]
        assert order.index("qualify-studio-source-cohort") < order.index(publisher)
    assert order.index("freeze-studio-release-source") < order.index("assemble-studio-linux-standard")
    assert "verify-dag-pypi" not in stages["freeze-studio-release-source"]
    assert "verify-core-pypi" in stages["qualify-studio-macos-arm64"]
    assert not any("npm" in name for name in stages)
    assert len(stages["refresh-and-verify-cockpit"]) == len(plan["artifacts"]["studio-deliveries"]["channels"]) == 6


def test_studio_hotfix_python_binding_retains_native_closure(studio_hotfix_baseline: tuple[Path, str]) -> None:
    plan = _studio_hotfix_plan(studio_hotfix_baseline, {"crates/dag-ml-py/src/lib.rs": "fn changed() {}\n"})
    assert plan["scope"] == "python-binding"
    assert "dag-crates" not in plan["artifacts"]
    assert plan["artifacts"]["studio-sidecar"]["action"] == "reuse-if-inputs-match"
    assert plan["artifacts"]["core-wheel"]["action"] == "retain-installed-version"
    assert "verify-retained-core-wheel" in plan["stages"]["qualify-sdk-wheel-in-cohort"]


@pytest.mark.parametrize(("path", "version", "approved", "reason"), [
    ("crates/dag-ml-core/src/runtime.rs", "0.6.0", True, "forward patch"),
    ("crates/dag-ml-core/src/runtime.rs", "0.5.1", False, "owner patch classification"),
    ("docs/contracts/artifact.schema.json", "0.5.1", True, "unclassified source paths"),
])
def test_studio_hotfix_requires_full_for_unadmitted_changes(studio_hotfix_baseline, path, version, approved, reason) -> None:
    plan = _studio_hotfix_plan(studio_hotfix_baseline, {path: "changed\n"}, version, approved)
    assert plan["status"] == "requires-full-plan"
    assert any(reason in blocker for blocker in plan["blockers"])
    assert plan["stages"] == {}


def test_studio_hotfix_doc_only_does_not_enqueue_delivery(studio_hotfix_baseline: tuple[Path, str]) -> None:
    plan = _studio_hotfix_plan(studio_hotfix_baseline, {"docs/usage.md": "Docs.\n"}, approved=False)
    assert plan["status"] == "no-runtime-change"
    assert plan["stages"] == {}


def test_studio_hotfix_rename_does_not_hide_removed_runtime_file(studio_hotfix_baseline: tuple[Path, str]) -> None:
    from n4a_studio_hotfix import draft_plan

    root, studio = studio_hotfix_baseline
    dag = root / "dag-ml"
    (dag / "docs").mkdir()
    _git(dag, "mv", "crates/dag-ml-core/src/runtime.rs", "docs/runtime.md")
    _git(dag, "commit", "-qm", "move source into docs")
    plan = draft_plan(root, "0.19.8", studio, _git(dag, "rev-parse", "HEAD"), "0.5.1", compatible_patch=True)
    assert plan["scope"] == "native-runtime"
    assert set(plan["candidate"]["changed_paths"]) == {"crates/dag-ml-core/src/runtime.rs", "docs/runtime.md"}


def test_studio_hotfix_rejects_drift_in_the_retained_sdk_wheel(studio_hotfix_baseline: tuple[Path, str]) -> None:
    from n4a_studio_hotfix import draft_plan

    root, _ = studio_hotfix_baseline
    studio = root / "nirs4all-studio"
    lock_name = "build/constraints/python-wheels-win32-x64.json"
    lock = json.loads((studio / lock_name).read_text())
    sdk = next(wheel for wheel in lock["packages"] if wheel["name"] == "nirs4all")
    sdk["sha256"] = "b" * 64
    studio_sha = _repo(studio, {lock_name: json.dumps(lock)})
    _git(studio, "tag", "0.19.9")
    dag_sha = _repo(root / "dag-ml", {"crates/dag-ml-py/src/lib.rs": "fn changed() {}\n"})
    with pytest.raises(ValueError, match="win32-x64 disagrees with the SDK digest"):
        draft_plan(root, "0.19.9", studio_sha, dag_sha, "0.5.1", compatible_patch=True)


def test_studio_hotfix_distinguishes_version_bump_from_dependency_change(studio_hotfix_baseline: tuple[Path, str]) -> None:
    change = {"Cargo.toml": '[workspace.package]\nversion = "0.5.1"\n',
              "crates/dag-ml-py/pyproject.toml": '[project]\nname = "dag-ml"\nversion = "0.5.1"\n',
              "crates/dag-ml-py/python/dag_ml/__init__.py": "def run():\n    return None\n"}
    plan = _studio_hotfix_plan(studio_hotfix_baseline, change)
    assert plan["status"] == "candidate-plan" and not plan["candidate"]["version_metadata_pending"]
    assert plan["candidate"]["dag_release_source_commit"] == plan["candidate"]["dag_commit"]
    assert plan["stages"]["build-dag-wheel"] == []
    change["Cargo.toml"] += '[workspace.dependencies]\nserde = "2"\n'
    blocked = _studio_hotfix_plan(studio_hotfix_baseline, change)
    assert blocked["status"] == "requires-full-plan"
    assert any("Cargo.toml" in reason for reason in blocked["blockers"])


def test_tagged_source_ref_must_resolve_to_reviewed_commit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    reviewed = _repo(repo, {"file": "reviewed"})
    tag = "refs/tags/v1.0.0"
    _git(repo, "tag", "-a", "-m", "reviewed tag", "v1.0.0", reviewed)
    manager = cohort.SourceManager(tmp_path / "build", tmp_path)
    spec = cohort.parse_member_value("demo", {"ref": tag, "source": str(repo), "expected_commit": reviewed}, tmp_path)
    assert manager.snapshot_commit(_recipe(), spec, tag).commit == reviewed

    different = _repo(repo, {"file": "different"})
    _git(repo, "tag", "-f", "v1.0.0", different)
    with pytest.raises(cohort.CohortError, match=f"resolved to {different}, expected {reviewed}"):
        manager.snapshot_commit(_recipe(), spec, tag)


def test_weekly_source_cohort_declares_tag_and_commit_for_each_supported_member() -> None:
    recipes, _ = cohort.load_recipes(cohort.DEFAULT_MEMBERS)
    path = ROOT / "docs/contracts/release/cohort/friday-tagged.n4a.json"
    manifest = cohort.load_manifest(path, [], recipes)
    assert manifest["tier"] == "full"
    assert manifest["pin_alignment"] == "refuse"
    for key, spec in manifest["members"].items():
        if key == "web":
            assert spec.published
        else:
            assert spec.ref.startswith("refs/tags/"), key
            assert cohort.COMMIT_RE.fullmatch(spec.expected_commit or ""), key
    assert manifest["members"]["methods"].python == "published"
