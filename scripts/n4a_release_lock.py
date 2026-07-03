#!/usr/bin/env python3
"""Generate and validate NIRS4ALL ecosystem aggregation lockfiles.

This is the first implementation slice for LOCK-REL. The manifest is reviewed
by humans; the lockfile is generated from the current sibling repositories and
consumes the contract/ABI artifacts those repositories already own.

Release version sources are read only from git-tracked files unless the manifest
explicitly opts out with ``allow_untracked``. This prevents stale ignored package
outputs from entering the lock. Python function contract artifacts are read from
the committed ``HEAD:<path>`` source, then executed with an import allow-list, so
dirty working-tree code is not imported as release evidence.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 in the current workspace.
    import tomli as tomllib  # type: ignore[no-redef]
from pathlib import Path, PurePosixPath
from typing import Any


LOCK_SCHEMA_VERSION = "n4a.aggregation-lock/v1"
MANIFEST_SCHEMA_VERSION = "n4a.aggregation-manifest/v1"
FETCHABILITY_SCHEMA_VERSION = "n4a.release-lock-fetchability/v1"


class RelError(RuntimeError):
    """Release lock generation/validation error."""


def canonical_json(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=True, indent=2, sort_keys=True)
        handle.write("\n")


def run(cmd: list[str], cwd: Path, allow_fail: bool = False) -> str | None:
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        if allow_fail:
            return None
        raise RelError(f"command failed in {cwd}: {' '.join(cmd)}\n{proc.stderr.strip()}")
    return proc.stdout.strip()


def run_bytes(cmd: list[str], cwd: Path, allow_fail: bool = False) -> bytes | None:
    proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        if allow_fail:
            return None
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RelError(f"command failed in {cwd}: {' '.join(cmd)}\n{stderr}")
    return proc.stdout


def git_url(repo_url: str) -> str:
    if "://" in repo_url or repo_url.startswith("git@"):
        return repo_url
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo_url):
        raise RelError(f"unsupported repository URL: {repo_url}")
    return f"https://github.com/{repo_url}.git"


def repo_state(repo_path: Path) -> dict[str, Any]:
    if not (repo_path / ".git").exists():
        raise RelError(f"not a git repository: {repo_path}")
    return {
        "commit": run(["git", "rev-parse", "HEAD"], repo_path),
        "branch": run(["git", "branch", "--show-current"], repo_path),
        "exact_tag": run(["git", "describe", "--tags", "--exact-match"], repo_path, allow_fail=True),
        "dirty": bool(run(["git", "status", "--porcelain"], repo_path)),
    }


def matches_any_pattern(value: str | None, patterns: list[str]) -> bool:
    if value is None:
        return False
    return any(fnmatch.fnmatch(value, pattern) for pattern in patterns)


def repo_identity(repo_path: Path) -> dict[str, Any]:
    """Stable git identity for the repo producing the lockfile.

    The ecosystem repo is dirty by definition while regenerating the lockfile,
    so recording its dirty bit would make validation self-invalidating. Member
    repos still record their dirty bit through repo_state().
    """

    state = repo_state(repo_path)
    state.pop("dirty", None)
    return state


def get_nested(data: Any, dotted: str) -> Any:
    current = data
    for part in dotted.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise RelError(f"missing field {dotted!r}")
    return current


def repo_relative_path(path: str) -> str:
    rel = PurePosixPath(path)
    if rel.is_absolute() or not rel.parts or any(part == ".." for part in rel.parts):
        raise RelError(f"repository-relative path required: {path!r}")
    return rel.as_posix()


def git_tracked_path(repo_path: Path, rel_path: str) -> bool:
    rel_path = repo_relative_path(rel_path)
    return (
        run(["git", "ls-files", "--error-unmatch", "--", rel_path], repo_path, allow_fail=True)
        is not None
    )


def require_tracked_source(repo_path: Path, rel_path: str, label: str) -> str:
    rel_path = repo_relative_path(rel_path)
    if git_tracked_path(repo_path, rel_path):
        return rel_path
    ignored_by = run(
        ["git", "check-ignore", "-v", "--", rel_path],
        repo_path,
        allow_fail=True,
    )
    ignored_hint = f"; ignored by {ignored_by}" if ignored_by else ""
    raise RelError(f"{label} path is not tracked by git: {rel_path}{ignored_hint}")


def git_head_file_bytes(repo_path: Path, rel_path: str) -> bytes | None:
    rel_path = repo_relative_path(rel_path)
    return run_bytes(["git", "show", f"HEAD:{rel_path}"], repo_path, allow_fail=True)


def read_toml_version(path: Path, field: str) -> Any:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return get_nested(data, field)


def read_description(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        if raw_line[0].isspace() and current_key:
            values[current_key] += " " + raw_line.strip()
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        current_key = key.strip()
        values[current_key] = value.strip()
    return values


def version_metadata(source: dict[str, Any], path: str, kind: str, value: Any) -> dict[str, Any]:
    entry = {
        "value": value,
        "source": path,
        "kind": kind,
        "read_from": "tracked_worktree",
    }
    for optional_key in (
        "distribution",
        "module",
        "generated_by",
        "generated_output_path",
        "metadata_source",
    ):
        if optional_key in source:
            entry[optional_key] = source[optional_key]
    return entry


def parse_c_header_macros(path: Path) -> dict[str, Any]:
    macros: dict[str, str] = {}
    pattern = re.compile(r"^#define\s+([A-Z0-9_]+)\s+(.+?)\s*(?:/\*.*)?$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        name, value = match.groups()
        macros[name] = value.strip()

    def int_macro(name: str) -> int:
        value = macros[name]
        return int(value.rstrip("uU"))

    project = ".".join(
        str(int_macro(name))
        for name in (
            "N4M_PROJECT_VERSION_MAJOR",
            "N4M_PROJECT_VERSION_MINOR",
            "N4M_PROJECT_VERSION_PATCH",
        )
    )
    abi = ".".join(
        str(int_macro(name))
        for name in (
            "N4M_ABI_VERSION_MAJOR",
            "N4M_ABI_VERSION_MINOR",
            "N4M_ABI_VERSION_PATCH",
        )
    )
    return {
        "project_version": macros.get("N4M_PROJECT_VERSION_STRING", f'"{project}"').strip('"'),
        "abi_version": abi,
        "abi_version_int": int_macro("N4M_ABI_VERSION_INT") if macros.get("N4M_ABI_VERSION_INT", "").isdigit() else None,
        "serialization_magic": macros.get("N4M_SERIALIZATION_MAGIC", "").strip('"'),
        "serialization_format_version": int_macro("N4M_SERIALIZATION_FORMAT_VERSION"),
        "source_sha256": sha256_file(path),
    }


def collect_versions(repo_path: Path, component: dict[str, Any]) -> dict[str, Any]:
    versions: dict[str, Any] = {}
    for source in component.get("version_sources", []):
        key = source["key"]
        rel_path = source["path"]
        if not source.get("allow_untracked", False):
            rel_path = require_tracked_source(
                repo_path,
                rel_path,
                f"{component['key']}.{key} version source",
            )
        else:
            rel_path = repo_relative_path(rel_path)
        path = repo_path / rel_path
        if not path.exists():
            versions[key] = {"missing": rel_path}
            continue
        kind = source["kind"]
        try:
            if kind == "toml":
                versions[key] = version_metadata(
                    source,
                    rel_path,
                    kind,
                    read_toml_version(path, source["field"]),
                )
            elif kind == "description":
                versions[key] = version_metadata(
                    source,
                    rel_path,
                    kind,
                    read_description(path).get(source.get("field", "Version")),
                )
            elif kind == "json":
                versions[key] = version_metadata(
                    source,
                    rel_path,
                    kind,
                    get_nested(load_json(path), source["field"]),
                )
            elif kind == "c_header_macros":
                versions[key] = version_metadata(
                    source,
                    rel_path,
                    kind,
                    parse_c_header_macros(path),
                )
            else:
                raise RelError(f"unsupported version source kind: {kind}")
        except RelError as exc:
            raise RelError(
                f"{component['key']}.{key} version source failed "
                f"({rel_path}): {exc}"
            ) from exc
    return versions


def validate_python_imports(
    source_text: str,
    *,
    rel_path: str,
    allowed_imports: set[str],
) -> None:
    tree = ast.parse(source_text, filename=f"HEAD:{rel_path}")
    allowed_imports = set(allowed_imports)
    allowed_imports.add("__future__")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports = [alias.name.split(".", 1)[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise RelError(
                    f"{rel_path} uses a relative import; "
                    "python_function_json artifacts forbid that"
                )
            imports = [((node.module or "").split(".", 1)[0])]
        else:
            continue
        blocked = sorted(
            name for name in imports if name and name not in allowed_imports
        )
        if blocked:
            raise RelError(
                f"{rel_path} imports {blocked}; allowed_imports is {sorted(allowed_imports)}"
            )


def collect_python_function_json_artifact(
    repo_path: Path,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    rel_path = repo_relative_path(artifact["path"])
    function_name = artifact["function"]
    read_from = artifact.get("read_from", "git_head")
    if read_from != "git_head":
        raise RelError(
            f"python_function_json artifact {artifact['id']} must read_from git_head"
        )

    base: dict[str, Any] = {
        "id": artifact["id"],
        "kind": artifact["kind"],
        "path": rel_path,
        "function": function_name,
        "read_from": read_from,
        "source_ref": "HEAD",
    }
    source_bytes = git_head_file_bytes(repo_path, rel_path)
    if source_bytes is None:
        return {**base, "missing": True}

    source_text = source_bytes.decode("utf-8")
    allowed_imports = set(artifact.get("allowed_imports", []))
    validate_python_imports(source_text, rel_path=rel_path, allowed_imports=allowed_imports)
    namespace: dict[str, Any] = {
        "__name__": "_n4a_release_contract",
        "__file__": f"HEAD:{rel_path}",
    }
    exec(compile(source_text, f"HEAD:{rel_path}", "exec"), namespace)
    function = namespace.get(function_name)
    if not callable(function):
        raise RelError(f"{rel_path} does not define callable {function_name}()")
    data = function()
    canonical = canonical_json(data)
    base.update(
        {
            "raw_sha256": sha256_bytes(source_bytes),
            "canonical_json_sha256": sha256_bytes(canonical),
            "json_schema": data.get("schema") if isinstance(data, dict) else None,
        }
    )
    if artifact.get("include_json", False):
        base["json"] = data
    return base


def collect_contract_artifact(repo_path: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    if artifact["kind"] == "python_function_json":
        return collect_python_function_json_artifact(repo_path, artifact)

    path = repo_path / artifact["path"]
    if not path.exists():
        return {"id": artifact["id"], "kind": artifact["kind"], "path": artifact["path"], "missing": True}

    kind = artifact["kind"]
    base: dict[str, Any] = {
        "id": artifact["id"],
        "kind": kind,
        "path": artifact["path"],
        "raw_sha256": sha256_file(path),
    }
    if kind in {"conformance_pack", "parity_oracle", "abi_snapshot", "json"}:
        data = load_json(path)
        base["canonical_json_sha256"] = sha256_bytes(canonical_json(data))
        if kind == "conformance_pack":
            base["pack_id"] = data.get("pack_id")
            base["contracts"] = {
                key: {
                    digest_key: value[digest_key]
                    for digest_key in ("normalized_sha256", "canonical_json_sha256")
                    if digest_key in value
                }
                for key, value in data.get("contracts", {}).items()
            }
        elif kind == "parity_oracle":
            base["oracle_id"] = data.get("oracle_id")
            base["required_case_ids"] = data.get("required_case_ids", [])
            base["required_case_count"] = len(data.get("required_case_ids", []))
        elif kind == "abi_snapshot":
            base["crate"] = data.get("crate")
            base["package_version"] = data.get("package_version")
            base["headers"] = data.get("headers", [])
        return base
    if kind == "text":
        return base
    raise RelError(f"unsupported artifact kind: {kind}")


def collect_glob_artifacts(repo_path: Path, pattern: str) -> dict[str, str]:
    matches: dict[str, str] = {}
    for root, _, filenames in os.walk(repo_path):
        root_path = Path(root)
        for filename in filenames:
            rel = (root_path / filename).relative_to(repo_path).as_posix()
            if fnmatch.fnmatch(rel, pattern):
                matches[rel] = sha256_file(repo_path / rel)
    return dict(sorted(matches.items()))


def collect_member(workspace_root: Path, component: dict[str, Any]) -> dict[str, Any]:
    selected_workspace_path = component.get("selected_workspace_path") or component["repo_path"]
    repo_path = (workspace_root / selected_workspace_path).resolve()
    state = repo_state(repo_path)
    branch_patterns = component.get("selected_branch_patterns", [])
    if branch_patterns and not matches_any_pattern(state.get("branch"), branch_patterns):
        raise RelError(
            f"{component['key']} selected workspace {selected_workspace_path!r} "
            f"is on branch {state.get('branch')!r}, which does not match "
            f"selected_branch_patterns={branch_patterns}"
        )
    artifacts = [
        collect_contract_artifact(repo_path, artifact)
        for artifact in component.get("contract_artifacts", [])
    ]
    glob_artifacts = {
        item["id"]: collect_glob_artifacts(repo_path, item["pattern"])
        for item in component.get("glob_artifacts", [])
    }
    return {
        "repo_path": component["repo_path"],
        "selected_workspace_path": selected_workspace_path,
        "repo_aliases": component.get("repo_aliases", []),
        "repo_url": component.get("repo_url"),
        "target_repo_url": component.get("target_repo_url"),
        "target_repo_path": component.get("target_repo_path"),
        "role": component.get("role"),
        "owner_boundary": component.get("owner_boundary"),
        "default_inclusion": component.get("default_inclusion"),
        "optional": component.get("optional", False),
        "private": component.get("private", False),
        "state": state,
        "license_expression": component.get("license_expression"),
        "packages": component.get("packages", {}),
        "availability": component.get("availability", {}),
        "required_gates": component.get("required_gates", []),
        "selected_branch_patterns": branch_patterns,
        "versions": collect_versions(repo_path, component),
        "contract_artifacts": artifacts,
        "glob_artifacts": glob_artifacts,
    }


def artifact_by_id(member: dict[str, Any], artifact_id: str) -> dict[str, Any] | None:
    for artifact in member.get("contract_artifacts", []):
        if artifact.get("id") == artifact_id:
            return artifact
    return None


def build_lockstep_attestations(manifest: dict[str, Any], members: dict[str, Any]) -> list[dict[str, Any]]:
    attestations: list[dict[str, Any]] = []
    for group in manifest.get("lockstep_groups", []):
        group_members = group["members"]
        shared: dict[str, Any] = {}
        errors: list[str] = []
        for artifact_id in group.get("shared_artifact_ids", []):
            values = []
            for member_key in group_members:
                artifact = artifact_by_id(members[member_key], artifact_id)
                if not artifact:
                    errors.append(f"{member_key} missing shared artifact {artifact_id}")
                    continue
                values.append(
                    {
                        "member": member_key,
                        "raw_sha256": artifact.get("raw_sha256"),
                        "canonical_json_sha256": artifact.get("canonical_json_sha256"),
                    }
                )
            raw_set = {value.get("raw_sha256") for value in values}
            canonical_set = {value.get("canonical_json_sha256") for value in values}
            shared[artifact_id] = {
                "members": values,
                "raw_equal": len(raw_set) == 1,
                "canonical_json_equal": len(canonical_set) == 1,
            }
            if len(raw_set) != 1 and len(canonical_set) != 1:
                errors.append(f"shared artifact {artifact_id} is not equivalent")
        attestations.append(
            {
                "id": group["id"],
                "members": group_members,
                "equivalence": group.get("equivalence"),
                "shared_artifacts": shared,
                "valid": not errors,
                "errors": errors,
            }
        )
    return attestations


def generate_lock(manifest_path: Path, workspace_root: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise RelError(f"unexpected manifest schema_version: {manifest.get('schema_version')!r}")
    if any(component.get("private") for component in manifest.get("components", [])):
        private = [component["key"] for component in manifest["components"] if component.get("private")]
        raise RelError(f"private repos are not allowed in aggregation manifest: {private}")

    members = {
        component["key"]: collect_member(workspace_root, component)
        for component in manifest.get("components", [])
    }
    lockstep_groups = build_lockstep_attestations(manifest, members)
    required_gates = sorted(
        {
            gate
            for component in manifest.get("components", [])
            for gate in component.get("required_gates", [])
        }
    )
    ecosystem_repo = manifest_path.parents[3]
    manifest_rel = manifest_path.relative_to(ecosystem_repo).as_posix()
    lock = {
        "schema_version": LOCK_SCHEMA_VERSION,
        "aggregation_lock_version": 1,
        "manifest_digest": sha256_bytes(canonical_json(manifest)),
        "release_train": manifest.get("release_train"),
        "status": manifest.get("status"),
        "compatibility_policy": manifest.get("compatibility_policy", {}),
        "release_selection_policy": manifest.get("release_selection_policy", {}),
        "generated_from": {
            "ecosystem_repo": "nirs4all-ecosystem",
            "manifest_path": manifest_rel,
            "tool": "scripts/n4a_release_lock.py",
        },
        "members": members,
        "lockstep_groups": lockstep_groups,
        "verification": {
            "required_gates": required_gates,
            "commands": manifest.get("verification_commands", []),
            "all_lockstep_groups_valid": all(group["valid"] for group in lockstep_groups),
            "private_repos_present": False,
        },
    }
    return lock


def validate_lock(manifest_path: Path, lock_path: Path, workspace_root: Path) -> None:
    expected = generate_lock(manifest_path, workspace_root)
    actual = load_json(lock_path)
    if actual != expected:
        raise RelError(
            "lockfile is stale or inconsistent for "
            f"workspace_root={workspace_root}. "
            "If the live sibling workspace contains reset or superseded branches, "
            "validate the lock against a selected-member workspace instead: "
            f"{Path(sys.argv[0]).name} checkout-members --manifest {manifest_path} "
            f"--lock {lock_path} --output <selected-root>; then rerun "
            f"{Path(sys.argv[0]).name} --workspace-root <selected-root> validate "
            f"--manifest {manifest_path} --lock {lock_path}. "
            "Cutover gate runs may keep their main --workspace-root and set "
            "N4A_RELEASE_WORKSPACE_ROOT=<selected-root> for release_lock_validation. "
            "Regenerate the lock only after intentionally selecting new member commits."
        )
    if not expected["verification"]["all_lockstep_groups_valid"]:
        raise RelError("one or more lockstep groups are invalid")


def checkout_members(manifest_path: Path, lock_path: Path, output_root: Path) -> None:
    manifest = load_json(manifest_path)
    lock = load_json(lock_path)
    members = lock.get("members", {})
    output_root.mkdir(parents=True, exist_ok=True)
    by_key = {component["key"]: component for component in manifest.get("components", [])}

    for key, member in members.items():
        component = by_key.get(key)
        if component is None:
            raise RelError(f"lock member {key!r} is absent from manifest")
        repo_url = component.get("repo_url")
        if not repo_url:
            raise RelError(f"manifest component {key!r} has no repo_url")
        selected_workspace_path = component.get("selected_workspace_path") or component["repo_path"]
        target = output_root / selected_workspace_path
        if target.exists():
            raise RelError(f"checkout target already exists: {target}")
        state = member.get("state", {})
        commit = state.get("commit")
        if not commit:
            raise RelError(f"lock member {key!r} has no commit")
        branch = state.get("branch")

        run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", git_url(repo_url), str(target)],
            output_root,
        )
        if branch:
            run(["git", "checkout", "-B", branch, commit], target)
        else:
            run(["git", "checkout", "--detach", commit], target)
        print(f"checked out {key} at {commit}")


def run_audit_command(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    message = "\n".join(part for part in (proc.stdout.strip(), proc.stderr.strip()) if part)
    return proc.returncode, message[-4000:]


def audit_member_fetchability(
    key: str,
    component: dict[str, Any] | None,
    member: dict[str, Any],
    checkout_root: Path,
) -> dict[str, Any]:
    state = member.get("state", {})
    commit = state.get("commit")
    branch = state.get("branch")
    report: dict[str, Any] = {
        "key": key,
        "commit": commit,
        "branch": branch,
    }
    if component is None:
        return {
            **report,
            "status": "missing_manifest_component",
            "message": "member is absent from manifest",
        }
    repo_path = component.get("repo_path")
    repo_url = component.get("repo_url")
    report.update(
        {
            "repo_path": repo_path,
            "repo_url": repo_url,
        }
    )
    if not repo_path:
        return {
            **report,
            "status": "missing_repo_path",
            "message": "manifest component has no repo_path",
        }
    if not repo_url:
        return {
            **report,
            "status": "missing_repo_url",
            "message": "manifest component has no repo_url",
        }
    if not commit:
        return {**report, "status": "missing_commit", "message": "lock member has no state.commit"}
    try:
        resolved_url = git_url(repo_url)
    except RelError as exc:
        return {**report, "status": "invalid_repo_url", "message": str(exc)}
    report["resolved_url"] = resolved_url

    target = checkout_root / repo_path
    report["checkout_path"] = str(target)
    if target.exists():
        return {
            **report,
            "status": "target_exists",
            "message": f"checkout target already exists: {target}",
        }
    target.parent.mkdir(parents=True, exist_ok=True)
    code, message = run_audit_command(
        ["git", "clone", "--filter=blob:none", "--no-checkout", resolved_url, str(target)],
        checkout_root,
    )
    if code != 0:
        return {**report, "status": "clone_failed", "message": message}
    checkout_cmd = (
        ["git", "checkout", "-B", branch, commit]
        if branch
        else ["git", "checkout", "--detach", commit]
    )
    code, message = run_audit_command(checkout_cmd, target)
    if code != 0:
        return {**report, "status": "checkout_failed", "message": message}
    return {**report, "status": "ok", "message": "checked out locked commit"}


def build_fetchability_report(
    manifest_path: Path,
    lock_path: Path,
    checkout_root: Path,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    lock = load_json(lock_path)
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise RelError(f"unexpected manifest schema_version: {manifest.get('schema_version')!r}")
    if lock.get("schema_version") != LOCK_SCHEMA_VERSION:
        raise RelError(f"unexpected lock schema_version: {lock.get('schema_version')!r}")
    members = lock.get("members", {})
    if not isinstance(members, dict) or not members:
        raise RelError("lock must contain a non-empty members object")
    by_key = {component["key"]: component for component in manifest.get("components", [])}
    checkout_root.mkdir(parents=True, exist_ok=True)
    rows = [
        audit_member_fetchability(key, by_key.get(key), member, checkout_root)
        for key, member in members.items()
    ]
    fetchable = sum(1 for row in rows if row["status"] == "ok")
    return {
        "schema_version": FETCHABILITY_SCHEMA_VERSION,
        "manifest_path": str(manifest_path),
        "lock_path": str(lock_path),
        "checkout_root": str(checkout_root),
        "totals": {
            "members": len(rows),
            "fetchable": fetchable,
            "unfetchable": len(rows) - fetchable,
        },
        "members": rows,
    }


def audit_fetchability(
    manifest_path: Path,
    lock_path: Path,
    checkout_root: Path | None = None,
) -> dict[str, Any]:
    if checkout_root is not None:
        return build_fetchability_report(manifest_path, lock_path, checkout_root)
    with tempfile.TemporaryDirectory(prefix="n4a-release-lock-fetch-") as tmp:
        return build_fetchability_report(manifest_path, lock_path, Path(tmp))


def print_fetchability_summary(report: dict[str, Any]) -> None:
    totals = report["totals"]
    print(
        "fetchability: "
        f"{totals['fetchable']}/{totals['members']} member commits checked out "
        f"({totals['unfetchable']} unfetchable)"
    )
    for row in report["members"]:
        if row["status"] == "ok":
            continue
        message = row.get("message") or ""
        first_line = message.splitlines()[0] if message else row["status"]
        print(f"{row['key']}: {row['status']}: {first_line}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Sibling workspace root (default: parent of nirs4all-ecosystem).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate an aggregation lockfile.")
    gen.add_argument("--manifest", type=Path, required=True)
    gen.add_argument("--output", type=Path, required=True)

    val = sub.add_parser("validate", help="Validate an aggregation lockfile against the current workspace.")
    val.add_argument("--manifest", type=Path, required=True)
    val.add_argument("--lock", type=Path, required=True)

    checkout = sub.add_parser("checkout-members", help="Clone lockfile members at their pinned commits.")
    checkout.add_argument("--manifest", type=Path, required=True)
    checkout.add_argument("--lock", type=Path, required=True)
    checkout.add_argument("--output", type=Path, required=True)

    audit = sub.add_parser(
        "audit-fetchability",
        help="Audit that every lockfile member commit can be cloned from its configured repo_url.",
    )
    audit.add_argument("--manifest", type=Path, required=True)
    audit.add_argument("--lock", type=Path, required=True)
    audit.add_argument(
        "--checkout-root",
        type=Path,
        help="Optional root for temporary member clones. If omitted, clones are deleted after the audit.",
    )
    audit.add_argument("--output-json", type=Path, help="Write the full audit report to JSON.")
    audit.add_argument(
        "--fail-on-unfetchable",
        action="store_true",
        help="Return a non-zero status when any locked commit is not fetchable.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    workspace_root = args.workspace_root.resolve()
    try:
        if args.command == "generate":
            lock = generate_lock(args.manifest.resolve(), workspace_root)
            write_json(args.output.resolve(), lock)
            print(f"wrote {args.output}")
            return 0
        if args.command == "validate":
            validate_lock(args.manifest.resolve(), args.lock.resolve(), workspace_root)
            print(f"validated {args.lock}")
            return 0
        if args.command == "checkout-members":
            checkout_members(args.manifest.resolve(), args.lock.resolve(), args.output.resolve())
            return 0
        if args.command == "audit-fetchability":
            checkout_root = args.checkout_root.resolve() if args.checkout_root else None
            report = audit_fetchability(args.manifest.resolve(), args.lock.resolve(), checkout_root)
            if args.output_json:
                write_json(args.output_json.resolve(), report)
                print(f"wrote {args.output_json}")
            print_fetchability_summary(report)
            if args.fail_on_unfetchable and report["totals"]["unfetchable"]:
                return 1
            return 0
    except RelError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
