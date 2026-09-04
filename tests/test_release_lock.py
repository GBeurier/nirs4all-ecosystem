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


def _git_output(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.stdout.strip()


def _init_repo(repo: Path) -> None:
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "release-lock-test@example.invalid")
    _git(repo, "config", "user.name", "Release Lock Test")


def _commit_all(repo: Path, message: str = "fixture") -> None:
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", message)


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _write_fetchability_fixture(tmp_path: Path) -> tuple[ModuleType, Path, Path]:
    release_lock = _load_release_lock()
    repo = tmp_path / "remote"
    _init_repo(repo)
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    _commit_all(repo)
    commit = _git_output(repo, "rev-parse", "HEAD")
    repo_url = repo.resolve().as_uri()

    manifest = {
        "schema_version": release_lock.MANIFEST_SCHEMA_VERSION,
        "components": [
            {"key": "ok", "repo_path": "ok-repo", "repo_url": repo_url},
            {"key": "missing", "repo_path": "missing-repo", "repo_url": repo_url},
        ],
    }
    lock = {
        "schema_version": release_lock.LOCK_SCHEMA_VERSION,
        "members": {
            "ok": {"state": {"commit": commit, "branch": "main"}},
            "missing": {"state": {"commit": "0" * 40, "branch": "main"}},
        },
    }
    manifest_path = tmp_path / "manifest.json"
    lock_path = tmp_path / "lock.json"
    _write_json(manifest_path, manifest)
    _write_json(lock_path, lock)
    return release_lock, manifest_path, lock_path


def _write_minimal_manifest(tmp_path: Path) -> tuple[ModuleType, Path, Path]:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_path = manifest_dir / "aggregation-manifest.n4a.json"
    lock_path = manifest_dir / "aggregation-lock.n4a.lock.json"
    manifest_dir.mkdir(parents=True)
    _write_json(
        manifest_path,
        {
            "schema_version": release_lock.MANIFEST_SCHEMA_VERSION,
            "release_train": "test",
            "status": "test",
            "components": [
                {
                    "key": "member",
                    "repo_path": "member",
                    "role": "test fixture",
                    "required_gates": ["release_lock_validation"],
                }
            ],
        },
    )
    return release_lock, manifest_path, lock_path


def test_audit_fetchability_reports_unfetchable_members(tmp_path: Path) -> None:
    release_lock, manifest_path, lock_path = _write_fetchability_fixture(tmp_path)

    report = release_lock.audit_fetchability(
        manifest_path,
        lock_path,
        tmp_path / "checkouts",
    )

    assert report["schema_version"] == release_lock.FETCHABILITY_SCHEMA_VERSION
    assert report["totals"] == {"members": 2, "fetchable": 1, "unfetchable": 1}
    by_key = {row["key"]: row for row in report["members"]}
    assert by_key["ok"]["status"] == "ok"
    assert by_key["missing"]["status"] == "checkout_failed"


def test_validate_lock_mismatch_error_mentions_selected_workspace(tmp_path: Path) -> None:
    release_lock, manifest_path, lock_path = _write_minimal_manifest(tmp_path)
    selected_root = tmp_path / "selected"
    selected_root.mkdir()
    selected_repo = selected_root / "member"
    _init_repo(selected_repo)
    (selected_repo / "README.md").write_text("selected\n", encoding="utf-8")
    _commit_all(selected_repo, "selected")

    live_root = tmp_path / "live"
    live_root.mkdir()
    live_repo = live_root / "member"
    _init_repo(live_repo)
    (live_repo / "README.md").write_text("live\n", encoding="utf-8")
    _commit_all(live_repo, "live")

    _write_json(lock_path, release_lock.generate_lock(manifest_path, selected_root))

    with pytest.raises(release_lock.RelError) as excinfo:
        release_lock.validate_lock(manifest_path, lock_path, live_root)

    message = str(excinfo.value)
    assert f"workspace_root={live_root}" in message
    assert "checkout-members" in message
    assert "--workspace-root <selected-root> validate" in message
    assert "N4A_RELEASE_WORKSPACE_ROOT=<selected-root>" in message
    assert "superseded branches" in message


def test_generate_lock_uses_selected_workspace_path_but_records_canonical_repo_path(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "manifest.json"
    selected_repo = tmp_path / "workspace" / "RC-v1-member"
    selected_repo.parent.mkdir()
    _init_repo(selected_repo)
    _git(selected_repo, "checkout", "-b", "rc/v1-demo")
    (selected_repo / "README.md").write_text("selected\n", encoding="utf-8")
    _commit_all(selected_repo)

    _write_json(
        manifest_path,
        {
            "schema_version": release_lock.MANIFEST_SCHEMA_VERSION,
            "release_train": "test",
            "status": "candidate",
            "components": [
                {
                    "key": "member",
                    "repo_path": "canonical-member",
                    "selected_workspace_path": "RC-v1-member",
                    "selected_branch_patterns": ["rc/v1-*"],
                }
            ],
        },
    )

    lock = release_lock.generate_lock(manifest_path, tmp_path / "workspace")

    member = lock["members"]["member"]
    assert member["repo_path"] == "canonical-member"
    assert member["selected_workspace_path"] == "RC-v1-member"
    assert member["state"]["branch"] == "rc/v1-demo"


def test_generate_lock_reads_python_literal_version_without_execution(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "manifest.json"
    repo = tmp_path / "workspace" / "member"
    repo.parent.mkdir()
    _init_repo(repo)
    (repo / "package.py").write_text(
        '__version__: str = "1.2.3"\nraise RuntimeError("must not execute")\n',
        encoding="utf-8",
    )
    _commit_all(repo)
    _write_json(
        manifest_path,
        {
            "schema_version": release_lock.MANIFEST_SCHEMA_VERSION,
            "components": [
                {
                    "key": "member",
                    "repo_path": "member",
                    "version_sources": [
                        {
                            "key": "python",
                            "kind": "python_literal",
                            "path": "package.py",
                            "field": "__version__",
                        }
                    ],
                }
            ],
        },
    )

    lock = release_lock.generate_lock(manifest_path, tmp_path / "workspace")

    assert lock["members"]["member"]["versions"]["python"] == {
        "value": "1.2.3",
        "source": "package.py",
        "kind": "python_literal",
        "read_from": "tracked_worktree",
    }


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("__version__ = build_version()\n", "is not a literal"),
        ('__version__ = "1"\n__version__ = "2"\n', "ambiguous"),
        ('other = "1"\n', "missing"),
    ],
)
def test_python_literal_version_source_fails_closed(
    tmp_path: Path,
    source: str,
    message: str,
) -> None:
    release_lock = _load_release_lock()
    repo = tmp_path / "member"
    _init_repo(repo)
    (repo / "package.py").write_text(source, encoding="utf-8")
    _commit_all(repo)
    component = {
        "key": "member",
        "version_sources": [
            {
                "key": "python",
                "kind": "python_literal",
                "path": "package.py",
                "field": "__version__",
            }
        ],
    }

    with pytest.raises(release_lock.RelError, match=message):
        release_lock.collect_versions(repo, component)


def test_generate_lock_prefers_manifest_exact_tag_when_multiple_tags_match(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "manifest.json"
    repo = tmp_path / "workspace" / "member"
    repo.parent.mkdir()
    _init_repo(repo)
    (repo / "README.md").write_text("selected\n", encoding="utf-8")
    _commit_all(repo)
    _git(repo, "tag", "n4a-v1-rc8-test")
    _git(repo, "tag", "n4a-v1-rc10-test")

    _write_json(
        manifest_path,
        {
            "schema_version": release_lock.MANIFEST_SCHEMA_VERSION,
            "release_train": "test",
            "status": "candidate",
            "release_selection_policy": {
                "preferred_exact_tag": "n4a-v1-rc10-test",
            },
            "components": [
                {
                    "key": "member",
                    "repo_path": "member",
                }
            ],
        },
    )

    lock = release_lock.generate_lock(manifest_path, tmp_path / "workspace")

    assert lock["members"]["member"]["state"]["exact_tag"] == "n4a-v1-rc10-test"


def test_generate_lock_prefers_component_exact_tag_over_ambiguous_commit_tags(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "manifest.json"
    repo = tmp_path / "workspace" / "member"
    repo.parent.mkdir()
    _init_repo(repo)
    (repo / "README.md").write_text("selected\n", encoding="utf-8")
    _commit_all(repo)
    _git(repo, "tag", "n4a-v1-rc12-test")
    _git(repo, "tag", "v0.3.5")

    _write_json(
        manifest_path,
        {
            "schema_version": release_lock.MANIFEST_SCHEMA_VERSION,
            "release_train": "test",
            "status": "candidate",
            "components": [
                {
                    "key": "member",
                    "repo_path": "member",
                    "preferred_exact_tag": "v0.3.5",
                }
            ],
        },
    )

    lock = release_lock.generate_lock(manifest_path, tmp_path / "workspace")

    assert lock["members"]["member"]["state"]["exact_tag"] == "v0.3.5"


def test_checkout_members_uses_selected_workspace_path_for_validation(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "manifest.json"
    lock_path = manifest_dir / "lock.json"
    selected_repo = tmp_path / "workspace" / "RC-v1-member"
    selected_repo.parent.mkdir()
    _init_repo(selected_repo)
    _git(selected_repo, "checkout", "-b", "rc/v1-demo")
    (selected_repo / "README.md").write_text("selected\n", encoding="utf-8")
    _commit_all(selected_repo)

    _write_json(
        manifest_path,
        {
            "schema_version": release_lock.MANIFEST_SCHEMA_VERSION,
            "release_train": "test",
            "status": "candidate",
            "components": [
                {
                    "key": "member",
                    "repo_path": "canonical-member",
                    "repo_url": selected_repo.resolve().as_uri(),
                    "selected_workspace_path": "RC-v1-member",
                    "selected_branch_patterns": ["rc/v1-*"],
                }
            ],
        },
    )
    _write_json(lock_path, release_lock.generate_lock(manifest_path, tmp_path / "workspace"))

    checkout_root = tmp_path / "external"
    release_lock.checkout_members(manifest_path, lock_path, checkout_root)

    assert (checkout_root / "RC-v1-member" / ".git").exists()
    assert not (checkout_root / "canonical-member").exists()
    release_lock.validate_lock(manifest_path, lock_path, checkout_root)


def test_generate_lock_rejects_selected_workspace_on_non_rc_branch(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "manifest.json"
    selected_repo = tmp_path / "workspace" / "RC-v1-member"
    selected_repo.parent.mkdir()
    _init_repo(selected_repo)
    (selected_repo / "README.md").write_text("selected\n", encoding="utf-8")
    _commit_all(selected_repo)

    _write_json(
        manifest_path,
        {
            "schema_version": release_lock.MANIFEST_SCHEMA_VERSION,
            "release_train": "test",
            "status": "candidate",
            "components": [
                {
                    "key": "member",
                    "repo_path": "canonical-member",
                    "selected_workspace_path": "RC-v1-member",
                    "selected_branch_patterns": ["rc/v1-*"],
                }
            ],
        },
    )

    with pytest.raises(release_lock.RelError, match="does not match selected_branch_patterns"):
        release_lock.generate_lock(manifest_path, tmp_path / "workspace")


def test_generate_lock_rejects_dirty_selected_member(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "manifest.json"
    repo = tmp_path / "workspace" / "member"
    repo.parent.mkdir()
    _init_repo(repo)
    (repo / "README.md").write_text("committed\n", encoding="utf-8")
    _commit_all(repo)
    (repo / "untracked.txt").write_text("not release evidence\n", encoding="utf-8")
    _write_json(
        manifest_path,
        {
            "schema_version": release_lock.MANIFEST_SCHEMA_VERSION,
            "components": [{"key": "member", "repo_path": "member"}],
        },
    )

    with pytest.raises(release_lock.RelError, match="release-lock members must be clean"):
        release_lock.generate_lock(manifest_path, tmp_path / "workspace")


def _minimal_product_train_manifest(release_lock: ModuleType) -> dict:
    components = []
    for key in sorted(release_lock.PRODUCT_TRAIN_COMPONENT_KEYS):
        components.append(
            {
                "key": key,
                "repo_path": key,
                "role": f"{key} role",
                "release_role": f"{key} release role",
                "release_state": "candidate",
                "artifact_receipts_complete": False,
                "qualification_head": {
                    "repository": f"GBeurier/{key}",
                    "ref": f"refs/heads/release/{key}",
                    "head": "1" * 40,
                    "tree": "2" * 40,
                },
            }
        )
    milestones = {
        "r1": {"state": "published", "members": {}},
        "r2": {"state": "candidate", "members": {}},
        "r3": {"state": "candidate", "members": {}},
        "r4": {"state": "not_created", "members": {}},
    }
    gates = [
        {"id": gate_id, "required": True, "state": "passed"}
        for gate_id in sorted(release_lock.PRODUCT_TRAIN_PROMOTION_GATES)
    ]
    projections = [
        {
            "key": key,
            "repo_path": key,
            "role": f"{key} projection",
            "required_for_promotion": True,
            "artifact_receipts_required": False,
            "artifact_receipts_complete": False,
            "state": "candidate",
            "qualification_head": {
                "repository": f"GBeurier/{key}",
                "ref": f"refs/heads/release/{key}",
                "head": "4" * 40,
                "tree": "5" * 40,
            },
        }
        for key in sorted(release_lock.PRODUCT_TRAIN_PROJECTION_KEYS)
    ]
    return {
        "schema_version": release_lock.PRODUCT_TRAIN_MANIFEST_SCHEMA_VERSION,
        "release_train": "test-product-train",
        "status": "candidate",
        "authority": {"ledger_commit": "3" * 40},
        "promotion": {"status": "no_go"},
        "promotion_gates": gates,
        "product_milestones": milestones,
        "projections": projections,
        "components": components,
    }


def test_generate_v2_product_train_lock_uses_remote_identities_without_local_checkouts(
    tmp_path: Path,
) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "product-train.json"
    manifest = _minimal_product_train_manifest(release_lock)
    _write_json(manifest_path, manifest)

    lock = release_lock.generate_lock(manifest_path, tmp_path / "empty-workspace")

    assert lock["schema_version"] == release_lock.PRODUCT_TRAIN_LOCK_SCHEMA_VERSION
    assert set(lock["members"]) == release_lock.PRODUCT_TRAIN_COMPONENT_KEYS
    assert len(lock["remote_identities"]) == (
        len(release_lock.PRODUCT_TRAIN_COMPONENT_KEYS)
        + len(release_lock.PRODUCT_TRAIN_PROJECTION_KEYS)
    )
    assert lock["verification"]["full_product_train_inventory"] is True
    assert lock["verification"]["all_required_gates_passed"] is True
    assert lock["promotion"] == {
        "status": "no_go",
        "eligible": True,
        "blockers": [],
        "gates": {
            gate_id: "passed"
            for gate_id in sorted(release_lock.PRODUCT_TRAIN_PROMOTION_GATES)
        },
    }


def test_v2_milestone_states_are_validated_generically(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "product-train.json"
    manifest = _minimal_product_train_manifest(release_lock)
    manifest["product_milestones"]["r1"]["state"] = "candidate"
    manifest["product_milestones"]["r2"]["state"] = "published"
    _write_json(manifest_path, manifest)

    lock = release_lock.generate_lock(manifest_path, tmp_path / "empty-workspace")

    assert lock["product_milestones"]["r1"]["state"] == "candidate"
    assert lock["product_milestones"]["r2"]["state"] == "published"


def test_v2_final_go_accepts_only_completed_immutable_train(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "product-train.json"
    manifest = _minimal_product_train_manifest(release_lock)
    manifest["status"] = "final"
    manifest["promotion"]["status"] = "go"
    for component in manifest["components"]:
        identity = component.pop("qualification_head")
        identity["ref"] = f"refs/tags/v-{component['key']}^{{}}"
        component["publication_head"] = identity
        component["release_state"] = "published"
        component["artifact_receipts_complete"] = True
        component["artifacts"] = [
            {
                "id": "package",
                "version": "1.0.0",
                "state": "published",
                "sha256": "6" * 64,
            }
        ]
        component["receipts"] = [{"id": "release", "state": "passed"}]
    for projection in manifest["projections"]:
        identity = projection.pop("qualification_head")
        identity["ref"] = f"refs/tags/v-{projection['key']}^{{}}"
        projection["publication_head"] = identity
        projection["state"] = "receipt"
    for milestone in manifest["product_milestones"].values():
        milestone["state"] = "published"
    _write_json(manifest_path, manifest)

    lock = release_lock.generate_lock(manifest_path, tmp_path / "empty-workspace")

    assert lock["status"] == "final"
    assert lock["promotion"]["status"] == "go"
    assert lock["promotion"]["eligible"] is True


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("r4_not_created", "requires published R4"),
        ("candidate_component", "requires published distribution members"),
        ("artifact_receipts", "requires complete artifact receipts"),
        ("artifact_sha", "artifacts without SHA-256"),
        ("mutable_projection", "requires immutable tag identities"),
    ],
)
def test_v2_final_go_fails_closed_on_incomplete_train(
    tmp_path: Path,
    mutation: str,
    message: str,
) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "product-train.json"
    manifest = _minimal_product_train_manifest(release_lock)
    manifest["status"] = "final"
    manifest["promotion"]["status"] = "go"
    for component in manifest["components"]:
        identity = component.pop("qualification_head")
        identity["ref"] = f"refs/tags/v-{component['key']}^{{}}"
        component["publication_head"] = identity
        component["release_state"] = "published"
        component["artifact_receipts_complete"] = True
        component["artifacts"] = [
            {
                "id": "package",
                "version": "1.0.0",
                "state": "published",
                "sha256": "6" * 64,
            }
        ]
        component["receipts"] = [{"id": "release", "state": "passed"}]
    for projection in manifest["projections"]:
        identity = projection.pop("qualification_head")
        identity["ref"] = f"refs/tags/v-{projection['key']}^{{}}"
        projection["publication_head"] = identity
        projection["state"] = "receipt"
    for milestone in manifest["product_milestones"].values():
        milestone["state"] = "published"
    if mutation == "r4_not_created":
        manifest["product_milestones"]["r4"]["state"] = "not_created"
    elif mutation == "candidate_component":
        component = manifest["components"][0]
        component["qualification_head"] = component.pop("publication_head")
        component["qualification_head"]["ref"] = "refs/heads/release/candidate"
        component["release_state"] = "candidate"
    elif mutation == "artifact_receipts":
        manifest["components"][0]["artifact_receipts_complete"] = False
    elif mutation == "artifact_sha":
        manifest["components"][0]["artifacts"][0].pop("sha256")
    else:
        manifest["projections"][0]["publication_head"]["ref"] = "refs/heads/release/projection"
    _write_json(manifest_path, manifest)

    with pytest.raises(release_lock.RelError, match=message):
        release_lock.generate_lock(manifest_path, tmp_path / "empty-workspace")


def test_v2_fetchability_uses_nested_remote_repository(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    remote = tmp_path / "remote"
    _init_repo(remote)
    (remote / "README.md").write_text("v2 remote\n", encoding="utf-8")
    _commit_all(remote)
    commit = _git_output(remote, "rev-parse", "HEAD")
    tree = _git_output(remote, "rev-parse", "HEAD^{tree}")
    branch = _git_output(remote, "branch", "--show-current")

    report = release_lock.audit_member_fetchability(
        "member",
        {
            "repo_path": "member",
            "release_state": "candidate",
            "qualification_head": {"repository": remote.resolve().as_uri()},
        },
        {
            "state": {
                "commit": commit,
                "tree": tree,
                "remote_ref": f"refs/heads/{branch}",
                "branch": None,
            }
        },
        tmp_path / "checkouts",
    )

    assert report["status"] == "ok"
    assert report["repo_url"] == remote.resolve().as_uri()

    bad_ref = release_lock.audit_member_fetchability(
        "member",
        {
            "repo_path": "member-ref-mismatch",
            "release_state": "candidate",
            "qualification_head": {"repository": remote.resolve().as_uri()},
        },
        {
            "state": {
                "commit": "0" * 40,
                "tree": tree,
                "remote_ref": f"refs/heads/{branch}",
                "branch": None,
            }
        },
        tmp_path / "checkouts",
    )
    assert bad_ref["status"] == "ref_mismatch"

    bad_tree = release_lock.audit_member_fetchability(
        "member",
        {
            "repo_path": "member-tree-mismatch",
            "release_state": "candidate",
            "qualification_head": {"repository": remote.resolve().as_uri()},
        },
        {
            "state": {
                "commit": commit,
                "tree": "0" * 40,
                "remote_ref": f"refs/heads/{branch}",
                "branch": None,
            }
        },
        tmp_path / "checkouts",
    )
    assert bad_tree["status"] == "tree_mismatch"


def test_checkout_members_supports_v2_nested_repository_identity(tmp_path: Path) -> None:
    release_lock = _load_release_lock()
    remote = tmp_path / "remote"
    _init_repo(remote)
    (remote / "README.md").write_text("v2 checkout\n", encoding="utf-8")
    _commit_all(remote)
    commit = _git_output(remote, "rev-parse", "HEAD")
    manifest_path = tmp_path / "manifest.json"
    lock_path = tmp_path / "lock.json"
    _write_json(
        manifest_path,
        {
            "components": [
                {
                    "key": "member",
                    "repo_path": "member",
                    "release_state": "candidate",
                    "qualification_head": {"repository": remote.resolve().as_uri()},
                }
            ]
        },
    )
    _write_json(lock_path, {"members": {"member": {"state": {"commit": commit, "branch": None}}}})

    release_lock.checkout_members(manifest_path, lock_path, tmp_path / "external")

    assert _git_output(tmp_path / "external" / "member", "rev-parse", "HEAD") == commit


@pytest.mark.parametrize("blocked_gate", ["signatures", "soak", "product_publication"])
def test_v2_product_train_refuses_go_with_required_evidence_missing(
    tmp_path: Path,
    blocked_gate: str,
) -> None:
    release_lock = _load_release_lock()
    manifest_dir = tmp_path / "ecosystem" / "docs" / "contracts" / "release"
    manifest_dir.mkdir(parents=True)
    manifest_path = manifest_dir / "product-train.json"
    manifest = _minimal_product_train_manifest(release_lock)
    manifest["promotion"]["status"] = "go"
    next(gate for gate in manifest["promotion_gates"] if gate["id"] == blocked_gate)["state"] = "missing"
    _write_json(manifest_path, manifest)

    with pytest.raises(release_lock.RelError, match="promotion refused"):
        release_lock.generate_lock(manifest_path, tmp_path / "empty-workspace")


def test_audit_fetchability_cli_only_fails_when_requested(tmp_path: Path) -> None:
    release_lock, manifest_path, lock_path = _write_fetchability_fixture(tmp_path)
    output_json = tmp_path / "fetchability.json"

    assert (
        release_lock.main(
            [
                "audit-fetchability",
                "--manifest",
                str(manifest_path),
                "--lock",
                str(lock_path),
                "--output-json",
                str(output_json),
            ]
        )
        == 0
    )
    assert json.loads(output_json.read_text(encoding="utf-8"))["totals"]["unfetchable"] == 1

    assert (
        release_lock.main(
            [
                "audit-fetchability",
                "--manifest",
                str(manifest_path),
                "--lock",
                str(lock_path),
                "--fail-on-unfetchable",
            ]
        )
        == 1
    )


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
    topology = repo / "bindings" / "python" / "src" / "nirs4all_core" / "_topology.py"
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
        "path": "bindings/python/src/nirs4all_core/_topology.py",
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


def test_central_manifest_declares_reproducible_methods_and_core_topology_sources() -> None:
    manifest = json.loads(
        (ROOT / "docs" / "contracts" / "release" / "aggregation-manifest.n4a.json").read_text(
            encoding="utf-8"
        )
    )
    components = {component["key"]: component for component in manifest["components"]}
    assert manifest["release_selection_policy"]["workspace_root"] == "/home/delete/nirs4all"
    assert manifest["release_selection_policy"]["selected_branch_patterns"] == ["main"]
    assert manifest["release_selection_policy"]["preferred_exact_tag"] is None
    assert components["core"]["repo_path"] == "nirs4all-core"
    assert components["core"]["repo_url"] == "GBeurier/nirs4all-core"
    assert components["core"]["selected_workspace_path"] == "nirs4all-core"
    assert components["core"]["preferred_exact_tag"] == "v0.3.14"
    assert components["core"]["target_repo_path"] == "nirs4all-core"
    assert components["core"].get("repo_aliases", []) == []
    assert components["formats"]["preferred_exact_tag"] == "v0.2.7"
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

    core_artifacts = {
        artifact["id"]: artifact
        for artifact in components["core"].get("contract_artifacts", [])
    }
    topology = core_artifacts["release_topology_manifest"]
    assert topology["kind"] == "python_function_json"
    assert topology["read_from"] == "git_head"
    assert topology["function"] == "release_topology_manifest"
    assert topology["path"] == "bindings/python/src/nirs4all_core/_topology.py"
    assert topology["include_json"] is True


def test_candidate_v2_manifest_is_exhaustive_current_and_not_promotable() -> None:
    release_lock = _load_release_lock()
    release_dir = ROOT / "docs" / "contracts" / "release"
    manifest_path = release_dir / "aggregation-manifest-candidate.v2.n4a.json"
    lock_path = release_dir / "aggregation-lock-candidate.v2.n4a.lock.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    components = {component["key"]: component for component in manifest["components"]}
    projections = {projection["key"]: projection for projection in manifest["projections"]}

    assert manifest["authority"]["ledger_commit"] == "091b8a0f3069e7a90167f78c81bb9d414c50ade5"
    assert set(components) == release_lock.PRODUCT_TRAIN_COMPONENT_KEYS
    assert set(projections) == release_lock.PRODUCT_TRAIN_PROJECTION_KEYS
    assert not ({"benchmarks", "org", "cockpit"} & set(components))
    assert components["io"]["qualification_head"]["head"] == "e6241571e2714160d2ff769030964b8924f0cbdb"
    assert components["io"]["release_state"] == "published"
    assert lock["members"]["io"]["state"]["commit"] == (
        "df7f2198862c71a24aeeba08ba09ee118524b55d"
    )
    assert components["studio"]["qualification_head"]["head"] == "86d5e5033d62240815e532038b6e769b14b25c2b"
    assert projections["org"]["qualification_head"]["head"] == "28523174bdbceffbb3d5c06e43796fe04073b1f5"
    assert projections["cockpit"]["qualification_head"]["head"] == "972155b9af539a444ede5c585e8d9eb799d35fe0"
    assert projections["benchmarks"]["qualification_head"]["head"] == (
        "17f8196b26457fbd300a46d6520c3d1845d0de05"
    )
    assert projections["repository"]["publication_head"]["tree"] == (
        "1bae2a889fdee52d8c54e19216641e7a99612fd6"
    )
    assert projections["repository"]["qualification_head"]["head"] == (
        "c0ed40ac6d21ab2a9879b8c654a3fa1f0d4fffac"
    )
    assert {
        artifact["id"]: artifact["sha256"]
        for artifact in projections["repository"]["artifacts"]
    } == {
        "python_wheel": "5743d99c70642ecffe9c2c4f92186a706abdb03b5b7cd2d62775ee92f8f389bb",
        "python_sdist": "5f911fefbc3cf7abb7651377e703113ac0c698dfefcd5c3bb9bb7cd31410ae53",
        "public_v1_surface_contract": "613d7008c38023d2d5e94df9bc4c9936e2a321c0d9aa24bcbf7a22cb6ac5b65f",
        "public_v1_surface_checker": "ac8b886c4cecf5c515c7600bc57c79c5ed28bbbf3c6782014d5ce48628095969",
    }
    assert {receipt["id"]: receipt["state"] for receipt in projections["repository"]["receipts"]} == {
        "build_33852742761": "passed",
        "exact_r1_r2_r3_surface_contract": "passed",
        "publication_33854293363": "passed",
    }
    assert components["providers"]["publication_head"]["head"] == "5a03f508374531409919fceb2f2367544c52b94d"
    assert components["providers"]["qualification_head"]["head"] == (
        "15722bd1123c887322f3bc3e0d54b145cffaf948"
    )
    assert lock["members"]["providers"]["state"]["commit"] == (
        "15722bd1123c887322f3bc3e0d54b145cffaf948"
    )
    assert {artifact["id"]: artifact["version"] for artifact in components["methods"]["artifacts"]} == {
        "methods_project": "1.0.15",
        "n4m_c_abi": "2.5.0",
        "n4m_rust_binding": "0.1.4",
    }
    assert {artifact["id"] for artifact in components["core"]["artifacts"]} == {
        "python_nirs4all_core",
        "rust_nirs4all",
        "npm_nirs4all",
        "r_nirs4all",
        "matlab_octave_nirs4all",
    }
    assert {receipt["id"] for receipt in components["core"]["receipts"]} == {
        "ci",
        "npm",
        "r",
        "matlab_octave",
        "source",
        "python",
        "crates",
    }
    io_receipt = components["io"]["receipts"][0]
    assert io_receipt["state"] == "passed"
    assert io_receipt["run"] == 33784472043
    assert io_receipt["report_sha256"] == (
        "sha256:6eb584f2866c84b034200f80522e3ec0035e726c4f512071901054d779c7fb17"
    )
    assert components["datasets"]["dependency_receipts"][0] == {
        "component": "io",
        "resolved_version": "0.1.12",
        "train_version": "0.1.14",
        "disposition": "compatible_published_lag",
    }
    assert components["web"]["dependency_receipts"][0] == {
        "component": "core",
        "resolved_version": "0.3.27",
        "train_version": "0.3.28",
        "disposition": "compatible_published_lag",
    }
    assert components["studio"]["receipts"][0]["state"] == "passed"
    assert components["studio"]["receipts"][0]["github_release_created"] is False
    assert {
        artifact["id"]: artifact["archive_digest"]
        for artifact in components["studio"]["artifacts"]
    } == {
        "pinned_plugin_wheels": "sha256:8149cce1671f4ea1cf5e99f3b4c5ef4412984ad424fa7c6075b898facf02ca6d",
        "windows_x64_installer": "sha256:07fe1d212bb5ce16d6ab15e5250bae79260f714e51db0e6ab2cd6c7a606199df",
        "linux_x64_appimage": "sha256:953a8014891fb80b408c2490ec1b21e10a2f873027805c875491ac215ba7c6e7",
        "macos_x64_dmg": "sha256:ad895bb11ae7337804dd886508620a973cf2707208522923e7564aa4d6b2a050",
        "macos_arm64_dmg": "sha256:1759fec8d37279cf9b20dce36cca8c371abecd01b29d216d9502e24d1b52e3f5",
    }
    assert manifest["product_milestones"]["r1"]["state"] == "published"
    assert manifest["product_milestones"]["r2"]["state"] == "candidate"
    assert manifest["product_milestones"]["r3"]["state"] == "candidate"
    assert manifest["product_milestones"]["r4"]["state"] == "not_created"
    assert manifest["product_milestones"]["r1"]["publication_receipts"] == {
        "python": "pypi_and_ghcr",
        "workflow_run": 33753479548,
        "publication_repair_commit": "e76c834c75157f0c74fcbba7383a69a818ed6b34",
        "publication_repair_tree": "49dadfb76d6995c2ab825d8cb937a864ea773fb9",
    }
    assert manifest["product_milestones"]["r3"]["members"]["studio"]["remote"]["head"] == (
        "86d5e5033d62240815e532038b6e769b14b25c2b"
    )
    assert {gate["id"]: gate["state"] for gate in manifest["promotion_gates"]} == {
        "artifact_receipts": "pending",
        "candidate_ci": "passed",
        "component_publications": "pending",
        "external_matrices": "pending",
        "product_publication": "partial",
        "repository_surface_contract": "pending",
        "signatures": "missing",
        "soak": "missing",
    }
    assert lock == release_lock.generate_lock(manifest_path, ROOT.parent)
    assert lock["promotion"]["status"] == "no_go"
    assert lock["promotion"]["eligible"] is False
    assert lock["verification"]["all_required_gates_passed"] is False
