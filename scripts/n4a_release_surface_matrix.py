#!/usr/bin/env python3
"""Validate and report the public V1 release surface matrix.

This is intentionally narrower than release proof. It checks objective
consistency between the public-surface matrix, the aggregation manifest, and the
aggregation lock. It does not claim that parity, product e2e, or local R/WASM
gates have passed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MATRIX_SCHEMA_VERSION = "n4a.public-v1-surface-matrix/v1"
MANIFEST_SCHEMA_VERSION = "n4a.aggregation-manifest/v1"
LOCK_SCHEMA_VERSION = "n4a.aggregation-lock/v1"

DEFAULT_MATRIX = Path("docs/contracts/release/public-v1-surface-matrix.n4a.json")
DEFAULT_MANIFEST = Path("docs/contracts/release/aggregation-manifest.n4a.json")
DEFAULT_LOCK = Path("docs/contracts/release/aggregation-lock.n4a.lock.json")

LOCK_RELATIONS = {
    "locked_member",
    "covered_by_locked_member",
    "outside_aggregation_lock",
}

ROADMAP_REQUIRED_V1_SURFACES = {
    "nirs4all.studio.product": "nirs4all-studio",
    "nirs4all.ui.package": "nirs4all-ui",
    "nirs4all.web.product": "nirs4all-web",
    "nirs4all.tools.migration": "nirs4all-tools",
    "nirs4all.providers.contracts": "nirs4all-providers",
    "nirs4all.cockpit.product": "nirs4all-cockpit",
    "nirs4all.org.site": "nirs4all-org",
}

PACKAGE_ECOSYSTEM_KEYS = {
    "python": ("python", "distribution"),
    "r": ("r", "packages"),
    "npm_wasm": ("npm", "packages"),
    "javascript_wasm": ("npm", "packages"),
    "rust": ("rust", "crates"),
    "matlab_octave": ("matlab", "archives"),
}


class SurfaceMatrixError(RuntimeError):
    """Public release surface matrix validation error."""


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        raise SurfaceMatrixError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SurfaceMatrixError(f"invalid JSON {path}: {exc}") from exc


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SurfaceMatrixError(message)


def _component_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {component["key"]: component for component in manifest.get("components", [])}


def _validate_scope(matrix: dict[str, Any]) -> None:
    scope = matrix.get("scope")
    _require(isinstance(scope, dict), "matrix.scope must be an object")
    _require(
        set(scope) == {"authority", "coverage", "exhaustive", "omission_semantics"},
        "matrix.scope must contain authority, coverage, exhaustive and omission_semantics",
    )
    for field in ("authority", "coverage", "omission_semantics"):
        _require(
            isinstance(scope.get(field), str) and bool(scope[field].strip()),
            f"matrix.scope.{field} must be a non-empty string",
        )
    _require(
        scope.get("exhaustive") is False,
        "matrix.scope.exhaustive must be false; this evidence-bound matrix is not a capability inventory",
    )


def _member_packages(member: dict[str, Any], ecosystem: str) -> list[str]:
    package_key = PACKAGE_ECOSYSTEM_KEYS.get(ecosystem)
    if not package_key:
        return []
    section_key, field = package_key
    section = member.get("packages", {}).get(section_key)
    if not isinstance(section, dict):
        return []
    if field == "distribution":
        value = section.get("distribution")
        return [value] if isinstance(value, str) else []
    values = section.get(field, [])
    return [value for value in values if isinstance(value, str)]


def _validate_lock_member_list(
    matrix: dict[str, Any],
    manifest: dict[str, Any],
    lock: dict[str, Any],
) -> None:
    components = _component_map(manifest)
    manifest_keys = set(components)
    lock_members = lock.get("members", {})
    _require(isinstance(lock_members, dict), "lock.members must be an object")
    lock_keys = set(lock_members)
    matrix_members = matrix.get("aggregation_lock_members")
    _require(
        isinstance(matrix_members, list) and matrix_members,
        "matrix.aggregation_lock_members must be a non-empty list",
    )
    matrix_by_key = {
        member.get("key"): member
        for member in matrix_members
        if isinstance(member, dict)
    }
    matrix_keys = set(matrix_by_key)

    _require(
        manifest_keys == lock_keys,
        f"manifest components and lock members differ: manifest={sorted(manifest_keys)} lock={sorted(lock_keys)}",
    )
    _require(
        matrix_keys == lock_keys,
        f"matrix aggregation members differ from lock: matrix={sorted(matrix_keys)} lock={sorted(lock_keys)}",
    )
    for key, matrix_member in matrix_by_key.items():
        member = lock_members[key]
        repo_path = matrix_member.get("repo_path")
        _require(
            repo_path == member.get("repo_path"),
            f"matrix aggregation member {key} repo_path={repo_path!r} does not match lock repo_path={member.get('repo_path')!r}",
        )


def _validate_public_surfaces(matrix: dict[str, Any], lock: dict[str, Any]) -> None:
    surfaces = matrix.get("public_v1_surfaces")
    _require(
        isinstance(surfaces, list) and surfaces,
        "matrix.public_v1_surfaces must be a non-empty list",
    )
    lock_members = lock["members"]
    lock_repo_paths: set[str] = set()
    for member in lock_members.values():
        if not isinstance(member, dict):
            continue
        for value in (
            member.get("repo_path"),
            member.get("target_repo_path"),
            *member.get("repo_aliases", []),
        ):
            if isinstance(value, str) and value:
                lock_repo_paths.add(value)
    seen_ids: set[str] = set()
    for surface in surfaces:
        _require(isinstance(surface, dict), "each public_v1_surfaces entry must be an object")
        surface_id = surface.get("id")
        _require(isinstance(surface_id, str) and surface_id, "each public surface needs a non-empty id")
        _require(surface_id not in seen_ids, f"duplicate public surface id: {surface_id}")
        seen_ids.add(surface_id)

        for field in ("ecosystem", "distribution", "repo_path", "lock_relation"):
            _require(
                isinstance(surface.get(field), str) and surface[field],
                f"{surface_id}: {field} must be a non-empty string",
            )
        relation = surface["lock_relation"]
        _require(
            relation in LOCK_RELATIONS,
            f"{surface_id}: unsupported lock_relation {relation!r}",
        )
        member_key = surface.get("lock_member_key")

        if relation in {"locked_member", "covered_by_locked_member"}:
            _require(
                isinstance(member_key, str) and member_key,
                f"{surface_id}: {relation} requires lock_member_key",
            )
            _require(member_key in lock_members, f"{surface_id}: unknown lock_member_key {member_key!r}")
            member = lock_members[member_key]
            member_repo_paths = {
                value
                for value in (
                    member.get("repo_path"),
                    member.get("target_repo_path"),
                    *member.get("repo_aliases", []),
                )
                if isinstance(value, str) and value
            }
            _require(
                surface["repo_path"] in member_repo_paths,
                f"{surface_id}: repo_path={surface['repo_path']!r} does not match lock member {member_key} repo paths={sorted(member_repo_paths)}",
            )
            packages = _member_packages(member, surface["ecosystem"])
            if packages:
                _require(
                    surface["distribution"] in packages,
                    f"{surface_id}: distribution {surface['distribution']!r} is not declared by lock member {member_key} for ecosystem {surface['ecosystem']!r}; declared={packages}",
                )
        else:
            _require(
                member_key is None,
                f"{surface_id}: outside_aggregation_lock must use lock_member_key=null",
            )
            _require(
                surface["repo_path"] not in lock_repo_paths,
                f"{surface_id}: repo_path {surface['repo_path']!r} is a lock member; use covered_by_locked_member or locked_member",
            )

    required_ids = matrix.get("required_nirs4all_v1_surface_ids")
    _require(
        isinstance(required_ids, list) and required_ids,
        "matrix.required_nirs4all_v1_surface_ids must be a non-empty list",
    )
    _require(
        len(required_ids) == len(set(required_ids)),
        "matrix.required_nirs4all_v1_surface_ids must not contain duplicates",
    )
    missing = sorted(set(required_ids) - seen_ids)
    _require(not missing, f"required nirs4all V1 surface ids are missing: {missing}")
    by_id = {surface["id"]: surface for surface in surfaces}
    for surface_id in required_ids:
        _require(
            by_id[surface_id].get("required_for_nirs4all_v1") is True,
            f"{surface_id}: required_nirs4all_v1_surface_ids entries must set required_for_nirs4all_v1=true",
        )
    missing_roadmap_surfaces = sorted(set(ROADMAP_REQUIRED_V1_SURFACES) - set(required_ids))
    _require(
        not missing_roadmap_surfaces,
        f"roadmap-required V1 surfaces are missing from required accounting: {missing_roadmap_surfaces}",
    )
    for surface_id, repo_path in ROADMAP_REQUIRED_V1_SURFACES.items():
        surface = by_id[surface_id]
        _require(
            surface.get("repo_path") == repo_path,
            f"{surface_id}: roadmap-required V1 surface must map to {repo_path!r}",
        )
        _require(
            surface.get("lock_relation") == "outside_aggregation_lock",
            f"{surface_id}: current roadmap-required product/support surface remains outside the aggregate lock",
        )

    required_shapes = [
        ("python", "nirs4all", None),
        ("python", "nirs4all-core", None),
        ("r", "nirs4all", None),
        ("javascript_wasm", "nirs4all", None),
        ("javascript_wasm", None, "@nirs4all/"),
        ("rust", "nirs4all", None),
        ("matlab_octave", "nirs4all-matlab-octave", None),
    ]
    required_surfaces = [
        surface
        for surface in surfaces
        if surface.get("required_for_nirs4all_v1") is True
    ]
    for ecosystem, distribution, prefix in required_shapes:
        found = False
        for surface in required_surfaces:
            if surface.get("ecosystem") != ecosystem:
                continue
            value = surface.get("distribution")
            if distribution is not None and value == distribution:
                found = True
            if prefix is not None and isinstance(value, str) and value.startswith(prefix):
                found = True
        label = distribution if distribution is not None else f"{prefix}*"
        _require(
            found,
            f"required nirs4all V1 accounting is missing {ecosystem}:{label}",
        )


def _validate_release_batch_semantics(matrix: dict[str, Any]) -> None:
    semantics = matrix.get("release_batch_semantics")
    _require(
        isinstance(semantics, dict),
        "matrix.release_batch_semantics must be an object",
    )
    surfaces = {
        surface["id"]: surface
        for surface in matrix.get("public_v1_surfaces", [])
        if isinstance(surface, dict) and isinstance(surface.get("id"), str)
    }
    for field in ("held_surface_ids", "custom_app_host_surface_ids"):
        values = semantics.get(field)
        _require(
            isinstance(values, list) and values,
            f"release_batch_semantics.{field} must be a non-empty list",
        )
        missing = sorted(surface_id for surface_id in values if surface_id not in surfaces)
        _require(
            not missing,
            f"release_batch_semantics.{field} references unknown surfaces: {missing}",
        )

    for surface_id, role in (
        ("nirs4all.python.oracle", "required_parity_oracle_held"),
        ("nirs4all.studio.product", "required_product_held"),
    ):
        surface = surfaces.get(surface_id)
        _require(surface is not None, f"release batch semantics require {surface_id}")
        _require(
            surface_id in semantics["held_surface_ids"],
            f"{surface_id}: held production surface must be listed in release_batch_semantics.held_surface_ids",
        )
        _require(
            surface.get("release_batch_role") == role,
            f"{surface_id}: release_batch_role must be {role!r}",
        )
        _require(
            surface.get("lock_relation") == "outside_aggregation_lock",
            f"{surface_id}: held production surface must stay outside the aggregation lock",
        )

    oracle = surfaces["nirs4all.python.oracle"]
    _require(
        oracle.get("required_for_nirs4all_v1") is True,
        "nirs4all.python.oracle must remain required as a parity/accounting gate",
    )
    studio = surfaces["nirs4all.studio.product"]
    _require(
        studio.get("required_for_nirs4all_v1") is True,
        "nirs4all.studio.product is required V1 scope even while its release remains held",
    )
    for surface_id in (
        "nirs4all.javascript_wasm.aggregate",
        "nirs4all.ui.package",
        "nirs4all.web.product",
    ):
        _require(
            surface_id in semantics["custom_app_host_surface_ids"],
            f"{surface_id}: custom app host surface missing from release_batch_semantics",
        )
    policy = semantics.get("python_name_policy")
    _require(
        isinstance(policy, str)
        and "nirs4all-core" in policy
        and "bare Python/PyPI nirs4all" in policy
        and "R, Rust, JavaScript/WASM" in policy,
        "release_batch_semantics.python_name_policy must explain Python/core and non-Python nirs4all naming",
    )


def validate_surface_matrix(matrix_path: Path, manifest_path: Path, lock_path: Path) -> dict[str, Any]:
    matrix = load_json(matrix_path)
    manifest = load_json(manifest_path)
    lock = load_json(lock_path)

    _require(
        matrix.get("schema_version") == MATRIX_SCHEMA_VERSION,
        f"unsupported matrix schema_version: {matrix.get('schema_version')!r}",
    )
    _require(
        manifest.get("schema_version") == MANIFEST_SCHEMA_VERSION,
        f"unsupported manifest schema_version: {manifest.get('schema_version')!r}",
    )
    _require(
        lock.get("schema_version") == LOCK_SCHEMA_VERSION,
        f"unsupported lock schema_version: {lock.get('schema_version')!r}",
    )
    for data, name in ((manifest, "manifest"), (lock, "lock")):
        _require(
            data.get("release_train") == matrix.get("release_train"),
            f"{name}.release_train={data.get('release_train')!r} does not match matrix.release_train={matrix.get('release_train')!r}",
        )

    _validate_scope(matrix)
    _validate_lock_member_list(matrix, manifest, lock)
    _validate_public_surfaces(matrix, lock)
    _validate_release_batch_semantics(matrix)
    return {"matrix": matrix, "manifest": manifest, "lock": lock}


def render_report(matrix: dict[str, Any], lock: dict[str, Any]) -> str:
    lines = [
        f"Public V1 release surface matrix: {matrix['release_train']} ({matrix.get('status', 'unknown')})",
        "",
        "Aggregation lock members:",
    ]
    for member in matrix["aggregation_lock_members"]:
        lock_member = lock["members"][member["key"]]
        state = lock_member.get("state", {})
        commit = str(state.get("commit", ""))[:12] or "unknown"
        lines.append(f"- {member['key']}: {member['repo_path']} @ {commit}")

    lines.extend(["", "Public V1 surfaces:"])
    for surface in matrix["public_v1_surfaces"]:
        required = "required nirs4all V1" if surface.get("required_for_nirs4all_v1") else "public/accounting"
        member = surface.get("lock_member_key") or "none"
        role = surface.get("release_batch_role") or "unspecified"
        lines.append(
            f"- {surface['id']}: {surface['ecosystem']} {surface['distribution']} "
            f"[{surface['lock_relation']}; member={member}; {required}; role={role}]"
        )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="Validate matrix/manifest/lock consistency.")
    report = sub.add_parser("report", help="Print a bounded public surface report.")
    report.add_argument("--json", action="store_true", help="Emit the validated matrix JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        validated = validate_surface_matrix(
            args.matrix.resolve(),
            args.manifest.resolve(),
            args.lock.resolve(),
        )
        if args.command == "validate":
            print(f"validated {args.matrix}")
            return 0
        if args.command == "report":
            if args.json:
                print(json.dumps(validated["matrix"], ensure_ascii=True, indent=2, sort_keys=True))
            else:
                print(render_report(validated["matrix"], validated["lock"]))
            return 0
    except SurfaceMatrixError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
