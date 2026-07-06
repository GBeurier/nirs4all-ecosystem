from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]


def _load_repin() -> ModuleType:
    path = ROOT / "scripts" / "n4a_submodule_repin.py"
    spec = importlib.util.spec_from_file_location("n4a_submodule_repin", path)
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
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "submodule-repin-test@example.invalid")
    _git(repo, "config", "user.name", "Submodule Repin Test")


def _commit_file(repo: Path, rel_path: str, text: str, message: str) -> str:
    path = repo / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    _git(repo, "add", rel_path)
    _git(repo, "commit", "-m", message)
    return _git_output(repo, "rev-parse", "HEAD")


def _write_gitmodules(root: Path, *, url: str) -> None:
    (root / ".gitmodules").write_text(
        f"""[submodule "member"]
\tpath = member
\turl = {url}
\tbranch = main
""",
        encoding="utf-8",
    )


def test_repin_plan_detects_fast_forward_head_without_touching_release_lock(tmp_path: Path) -> None:
    repin = _load_repin()

    remote = tmp_path / "remote-member"
    _init_repo(remote)
    first = _commit_file(remote, "README.md", "one\n", "first")
    second = _commit_file(remote, "README.md", "two\n", "second")

    root = tmp_path / "ecosystem"
    _init_repo(root)
    (root / "docs" / "contracts" / "release").mkdir(parents=True)
    (root / "docs" / "contracts" / "release" / "aggregation-lock.n4a.lock.json").write_text(
        "{}\n",
        encoding="utf-8",
    )
    _write_gitmodules(root, url=str(remote))
    _git(root, "clone", str(remote), "member")
    _git(root / "member", "checkout", first)
    _git(root, "add", ".gitmodules", "docs/contracts/release/aggregation-lock.n4a.lock.json", "member")
    _git(root, "commit", "-m", "pin member")

    plan = repin.build_repin_plan(root, fetch=False)

    assert plan["protected_paths"] == {
        "docs/contracts/release/aggregation-lock.n4a.lock.json": "clean"
    }
    assert plan["totals"]["fast_forward"] == 1
    assert plan["totals"]["manual_review"] == 0
    [member] = plan["submodules"]
    assert member["path"] == "member"
    assert member["current"] == first
    assert member["remote_head"] == second
    assert member["relation"] == "fast_forward"
    assert member["recommended_action"] == "checkout_remote_head"


def test_repin_apply_updates_only_gitlink_and_reports_updated_path(tmp_path: Path) -> None:
    repin = _load_repin()

    remote = tmp_path / "remote-member"
    _init_repo(remote)
    first = _commit_file(remote, "README.md", "one\n", "first")
    second = _commit_file(remote, "README.md", "two\n", "second")

    root = tmp_path / "ecosystem"
    _init_repo(root)
    _write_gitmodules(root, url=str(remote))
    _git(root, "clone", str(remote), "member")
    _git(root / "member", "checkout", first)
    _git(root, "add", ".gitmodules", "member")
    _git(root, "commit", "-m", "pin member")

    plan = repin.build_repin_plan(root, fetch=False)
    assert repin.apply_repin_plan(root, plan) == ["member"]

    staged = _git_output(root, "diff", "--cached", "--submodule=short")
    assert first[:12] in staged
    assert second[:12] in staged


def test_repin_plan_cli_emits_json(tmp_path: Path, capsys) -> None:
    repin = _load_repin()

    remote = tmp_path / "remote-member"
    _init_repo(remote)
    commit = _commit_file(remote, "README.md", "one\n", "first")

    root = tmp_path / "ecosystem"
    _init_repo(root)
    _write_gitmodules(root, url=str(remote))
    _git(root, "clone", str(remote), "member")
    _git(root / "member", "checkout", commit)
    _git(root, "add", ".gitmodules", "member")
    _git(root, "commit", "-m", "pin member")

    assert repin.main(["plan", "--repo-root", str(root), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "n4a.submodule-repin-plan/v1"
    assert payload["totals"]["up_to_date"] == 1
