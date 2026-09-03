#!/usr/bin/env python3
"""Validate repository, lane, artifact and handoff ownership for GOV-001."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "docs/contracts/governance/ownership-ledger.v1.json"
SURFACE_MATRIX = ROOT / "docs/contracts/release/public-v1-surface-matrix.n4a.json"
RELEASE_LOCK = ROOT / "docs/contracts/release/aggregation-lock.n4a.lock.json"
WORK_LEDGER = ROOT / "docs/contracts/release/migration-work-ledger.yaml"
LEDGER_SCHEMA = "n4a.ownership-ledger/v1"
HANDOFF_SCHEMA = "n4a.ownership-handoff/v1"
LANE_IDS = set("ABCDEFGH")
ARTIFACT_CLASSES = {"contracts", "schemas", "goldens"}
EXCLUDED_REPOSITORIES = {"nirs4all-lite", "nirs4all-drafts", "nirs4all-lab"}
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


class OwnershipLedgerError(RuntimeError):
    """Ownership contract validation error."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OwnershipLedgerError(message)


def _object(value: Any, path: str) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{path} must be an object")
    return value


def _exact_keys(
    value: dict[str, Any], required: set[str], path: str, *, optional: set[str] | None = None
) -> None:
    optional = optional or set()
    missing = sorted(required - set(value))
    unknown = sorted(set(value) - required - optional)
    _require(not missing, f"{path} is missing required fields: {missing}")
    _require(not unknown, f"{path} has unsupported fields: {unknown}")


def _string(value: Any, path: str) -> str:
    _require(isinstance(value, str) and value.strip(), f"{path} must be a non-empty string")
    return value


def _strings(value: Any, path: str, *, allow_empty: bool = False) -> list[str]:
    _require(isinstance(value, list), f"{path} must be an array")
    _require(bool(value) or allow_empty, f"{path} must not be empty")
    result = [_string(item, f"{path}[{index}]") for index, item in enumerate(value)]
    _require(len(result) == len(set(result)), f"{path} must not contain duplicates")
    return result


def _load_json(path: Path) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            _require(key not in value, f"{path} contains duplicate JSON key {key!r}")
            value[key] = item
        return value

    try:
        payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OwnershipLedgerError(f"cannot read JSON {path}: {exc}") from exc
    return _object(payload, str(path))


def _required_repository_keys() -> set[str]:
    """Derive the closed repository scope from the three governance sources."""
    matrix = _load_json(SURFACE_MATRIX)
    lock = _load_json(RELEASE_LOCK)
    try:
        work_ledger = yaml.safe_load(WORK_LEDGER.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise OwnershipLedgerError(f"cannot read {WORK_LEDGER}: {exc}") from exc
    _require(isinstance(work_ledger, dict), f"{WORK_LEDGER} must be an object")

    repositories = {
        surface["repo_path"]
        for surface in matrix.get("public_v1_surfaces", [])
        if isinstance(surface, dict) and isinstance(surface.get("repo_path"), str)
    }
    repositories.update(
        candidate["repo_path"]
        for candidate in matrix.get("candidate_heads", {}).get("components", [])
        if isinstance(candidate, dict) and isinstance(candidate.get("repo_path"), str)
    )
    repositories.update(
        member["repo_path"]
        for member in lock.get("members", {}).values()
        if isinstance(member, dict) and isinstance(member.get("repo_path"), str)
    )
    for item in work_ledger.get("work_items", []):
        if not isinstance(item, dict):
            continue
        for owned_path in item.get("owned_files", []):
            if not isinstance(owned_path, str):
                continue
            repository = owned_path.split("/", 1)[0]
            if repository == "nirs4all" or repository.startswith(("nirs4all-", "dag-ml")):
                repositories.add(repository)
    repositories.difference_update(EXCLUDED_REPOSITORIES)
    repositories.add("nirs4all-ecosystem")
    return repositories


def _identity_refs(value: Any, path: str, identities: dict[str, dict[str, Any]]) -> list[str]:
    refs = _strings(value, path)
    unknown = sorted(set(refs) - set(identities))
    _require(not unknown, f"{path} contains unknown identities: {unknown}")
    _require(
        all(identities[identity]["can_approve"] is True for identity in refs),
        f"{path} contains an identity that cannot approve",
    )
    return refs


def _validate_codeowners(root: dict[str, Any], identities: dict[str, dict[str, Any]]) -> None:
    governed = _object(root["governed_files"], "governed_files")
    _exact_keys(
        governed,
        {"codeowners", "handoff_template", "validator", "tests"},
        "governed_files",
    )
    codeowners_path = ROOT / _string(governed["codeowners"], "governed_files.codeowners")
    try:
        lines = codeowners_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise OwnershipLedgerError(f"cannot read {codeowners_path}: {exc}") from exc
    rules: dict[str, list[str]] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split()
        _require(len(fields) >= 2, f"invalid CODEOWNERS line: {line!r}")
        rules[fields[0]] = fields[1:]
    required_patterns = {
        "*",
        "/docs/contracts/governance/",
        "/docs/contracts/release/migration-work-ledger.yaml",
        "/scripts/n4a_ownership_ledger.py",
        "/tests/test_ownership_ledger.py",
        "/.github/PULL_REQUEST_TEMPLATE/ownership-handoff.md",
    }
    missing = sorted(required_patterns - set(rules))
    _require(not missing, f"CODEOWNERS misses governed paths: {missing}")
    approved_handles = {identity["handle"] for identity in identities.values() if identity["can_approve"]}
    for pattern in required_patterns:
        _require(set(rules[pattern]) <= approved_handles, f"CODEOWNERS {pattern} has an unregistered owner")
        _require(bool(rules[pattern]), f"CODEOWNERS {pattern} has no owner")

    template_path = ROOT / _string(
        governed["handoff_template"], "governed_files.handoff_template"
    )
    try:
        template = template_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise OwnershipLedgerError(f"cannot read {template_path}: {exc}") from exc
    for field in root["handoff_contract"]["required_fields"]:
        _require(f'"{field}"' in template, f"handoff template misses required field {field!r}")


def validate_ledger(path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    root = _load_json(path)
    _exact_keys(
        root,
        {
            "schema_version",
            "status",
            "scope",
            "authority_sources",
            "identities",
            "remote_authority",
            "release_captain",
            "lanes",
            "repositories",
            "artifact_classes",
            "artifact_overlap_arbitrations",
            "change_policy",
            "handoff_contract",
            "governed_files",
        },
        "ownership ledger",
    )
    _require(root["schema_version"] == LEDGER_SCHEMA, f"schema_version must be {LEDGER_SCHEMA}")
    _require(
        root["status"] == "complete-authoritative-single-approver",
        "status must reflect the authoritative single-approver inventory",
    )

    scope = _object(root["scope"], "scope")
    _exact_keys(
        scope,
        {"exhaustive", "repository_sources", "excluded_repositories", "repository_keys"},
        "scope",
    )
    _require(scope["exhaustive"] is True, "scope.exhaustive must be true")
    _strings(scope["repository_sources"], "scope.repository_sources")
    excluded = _object(scope["excluded_repositories"], "scope.excluded_repositories")
    _require(set(excluded) == EXCLUDED_REPOSITORIES, "scope exclusions must name retired/private repositories")
    for repository, reason in excluded.items():
        _string(reason, f"scope.excluded_repositories.{repository}")
    declared_scope = set(_strings(scope["repository_keys"], "scope.repository_keys"))
    _require(
        declared_scope == _required_repository_keys(),
        "ownership ledger repository scope differs from release surfaces, lock or work ledger",
    )

    authority_sources: dict[str, dict[str, Any]] = {}
    for index, raw_source in enumerate(root["authority_sources"]):
        source = _object(raw_source, f"authority_sources[{index}]")
        _exact_keys(
            source,
            {"id", "kind", "repository_key", "path", "commit", "source_sha256", "claims"},
            f"authority_sources[{index}]",
        )
        source_id = _string(source["id"], f"authority_sources[{index}].id")
        _require(source_id not in authority_sources, f"duplicate authority source {source_id}")
        _require(source["kind"] == "tracked_codeowners", f"{source_id} is not tracked CODEOWNERS evidence")
        _require(source["repository_key"] in declared_scope, f"{source_id} names an unknown repository")
        source_path = _string(source["path"], f"{source_id}.path")
        _require(not Path(source_path).is_absolute() and ".." not in Path(source_path).parts, f"{source_id}.path is unsafe")
        _require(FULL_SHA.fullmatch(_string(source["commit"], f"{source_id}.commit")) is not None, f"{source_id}.commit is not a full SHA")
        _require(SHA256.fullmatch(_string(source["source_sha256"], f"{source_id}.source_sha256")) is not None, f"{source_id}.source_sha256 is invalid")
        _strings(source["claims"], f"{source_id}.claims")
        authority_sources[source_id] = source
    _require(bool(authority_sources), "authority_sources must not be empty")

    identities: dict[str, dict[str, Any]] = {}
    handles: set[str] = set()
    for index, raw_identity in enumerate(root["identities"]):
        identity = _object(raw_identity, f"identities[{index}]")
        _exact_keys(
            identity,
            {"id", "kind", "handle", "can_approve", "can_release_captain", "authority_source_ids"},
            f"identities[{index}]",
        )
        identity_id = _string(identity["id"], f"identities[{index}].id")
        handle = _string(identity["handle"], f"identities[{index}].handle")
        _require(identity_id not in identities, f"duplicate identity {identity_id}")
        _require(handle not in handles, f"duplicate identity handle {handle}")
        _require(identity["kind"] in {"github_user", "github_team"}, f"{identity_id}.kind is invalid")
        _require(identity["can_approve"] is True, f"{identity_id} is not an approving identity")
        _require(isinstance(identity["can_release_captain"], bool), f"{identity_id}.can_release_captain must be boolean")
        source_ids = _strings(identity["authority_source_ids"], f"{identity_id}.authority_source_ids")
        _require(set(source_ids) <= set(authority_sources), f"{identity_id} cites unknown authority evidence")
        identities[identity_id] = identity
        handles.add(handle)
    _require(bool(identities), "identities must not be empty")

    remote = _object(root["remote_authority"], "remote_authority")
    _exact_keys(remote, {"namespace", "kind", "team_slugs", "observation"}, "remote_authority")
    namespace = _string(remote["namespace"], "remote_authority.namespace")
    _require(remote["kind"] == "github_personal_namespace", "remote authority must remain a personal namespace")
    _strings(remote["team_slugs"], "remote_authority.team_slugs", allow_empty=True)
    _string(remote["observation"], "remote_authority.observation")

    captain = _object(root["release_captain"], "release_captain")
    _exact_keys(captain, {"status", "identity_ref", "authority_source_ids", "pending_choice"}, "release_captain")
    _require(captain["status"] == "assigned-existing-authority", "release captain must use an existing authority")
    captain_ref = _string(captain["identity_ref"], "release_captain.identity_ref")
    _require(captain_ref in identities, "release captain identity is absent")
    _require(identities[captain_ref]["can_release_captain"] is True, "release captain identity is not authorized")
    captain_sources = _strings(captain["authority_source_ids"], "release_captain.authority_source_ids")
    _require(set(captain_sources) <= set(identities[captain_ref]["authority_source_ids"]), "release captain evidence is not identity evidence")
    _require(captain["pending_choice"] is None, "assigned release captain cannot retain a pending choice")

    lanes: dict[str, dict[str, Any]] = {}
    for index, raw_lane in enumerate(root["lanes"]):
        lane = _object(raw_lane, f"lanes[{index}]")
        _exact_keys(
            lane,
            {"id", "title", "responsibilities", "accountable_identity_refs", "reviewer_identity_refs", "repository_keys"},
            f"lanes[{index}]",
        )
        lane_id = _string(lane["id"], f"lanes[{index}].id")
        _require(lane_id not in lanes, f"duplicate lane {lane_id}")
        _string(lane["title"], f"lane {lane_id}.title")
        _strings(lane["responsibilities"], f"lane {lane_id}.responsibilities")
        _identity_refs(lane["accountable_identity_refs"], f"lane {lane_id}.accountable_identity_refs", identities)
        _identity_refs(lane["reviewer_identity_refs"], f"lane {lane_id}.reviewer_identity_refs", identities)
        repository_keys = _strings(lane["repository_keys"], f"lane {lane_id}.repository_keys")
        _require(set(repository_keys) <= declared_scope, f"lane {lane_id} names repositories outside scope")
        lanes[lane_id] = lane
    _require(set(lanes) == LANE_IDS, "ownership ledger must contain lanes A-H exactly once")

    repositories: dict[str, dict[str, Any]] = {}
    for index, raw_repository in enumerate(root["repositories"]):
        repository = _object(raw_repository, f"repositories[{index}]")
        _exact_keys(
            repository,
            {"key", "repo_path", "remote", "lanes", "primary_lane", "consulted_lanes", "approver_identity_refs", "arbitration"},
            f"repositories[{index}]",
        )
        key = _string(repository["key"], f"repositories[{index}].key")
        _require(key not in repositories, f"duplicate repository owner row {key}")
        _require(repository["repo_path"] == key, f"repository {key} repo_path must equal its scope key")
        _require(repository["remote"] == f"https://github.com/{namespace}/{key}.git", f"repository {key} remote is outside the inspected namespace")
        repo_lanes = _strings(repository["lanes"], f"repository {key}.lanes")
        _require(set(repo_lanes) <= LANE_IDS, f"repository {key} names an unknown lane")
        primary = _string(repository["primary_lane"], f"repository {key}.primary_lane")
        _require(primary in repo_lanes, f"repository {key} primary lane is not an owner")
        consulted = _strings(repository["consulted_lanes"], f"repository {key}.consulted_lanes", allow_empty=True)
        _require(set(consulted) == set(repo_lanes) - {primary}, f"repository {key} consulted lanes do not arbitrate every overlap")
        _identity_refs(repository["approver_identity_refs"], f"repository {key}.approver_identity_refs", identities)
        arbitration = repository["arbitration"]
        if consulted:
            arbitration = _object(arbitration, f"repository {key}.arbitration")
            _exact_keys(arbitration, {"id", "primary_lane", "consulted_lanes", "rule"}, f"repository {key}.arbitration")
            _string(arbitration["id"], f"repository {key}.arbitration.id")
            _require(arbitration["primary_lane"] == primary, f"repository {key} arbitration primary differs")
            _require(set(_strings(arbitration["consulted_lanes"], f"repository {key}.arbitration.consulted_lanes")) == set(consulted), f"repository {key} arbitration omits consulted lanes")
            _string(arbitration["rule"], f"repository {key}.arbitration.rule")
        else:
            _require(arbitration is None, f"single-lane repository {key} must not invent overlap arbitration")
        repositories[key] = repository
    _require(set(repositories) == declared_scope, "one or more in-scope repositories have no owner row")
    for lane_id, lane in lanes.items():
        inverse = {key for key, repository in repositories.items() if lane_id in repository["lanes"]}
        _require(set(lane["repository_keys"]) == inverse, f"lane {lane_id} repository list differs from repository ownership rows")

    artifact_classes: dict[str, dict[str, Any]] = {}
    for index, raw_artifact in enumerate(root["artifact_classes"]):
        artifact = _object(raw_artifact, f"artifact_classes[{index}]")
        _exact_keys(
            artifact,
            {"id", "path_patterns", "primary_lane", "required_identity_refs", "repository_lane_rule", "change_rule"},
            f"artifact_classes[{index}]",
        )
        artifact_id = _string(artifact["id"], f"artifact_classes[{index}].id")
        _require(artifact_id not in artifact_classes, f"duplicate artifact class {artifact_id}")
        _strings(artifact["path_patterns"], f"artifact {artifact_id}.path_patterns")
        _require(artifact["primary_lane"] in LANE_IDS, f"artifact {artifact_id} has no lane owner")
        _identity_refs(artifact["required_identity_refs"], f"artifact {artifact_id}.required_identity_refs", identities)
        _string(artifact["repository_lane_rule"], f"artifact {artifact_id}.repository_lane_rule")
        _string(artifact["change_rule"], f"artifact {artifact_id}.change_rule")
        artifact_classes[artifact_id] = artifact
    _require(set(artifact_classes) == ARTIFACT_CLASSES, "contracts, schemas and goldens must each have ownership")

    expected_pairs = {frozenset(pair) for pair in ({"contracts", "schemas"}, {"contracts", "goldens"}, {"schemas", "goldens"})}
    observed_pairs: set[frozenset[str]] = set()
    for index, raw_arbitration in enumerate(root["artifact_overlap_arbitrations"]):
        arbitration = _object(raw_arbitration, f"artifact_overlap_arbitrations[{index}]")
        _exact_keys(arbitration, {"class_ids", "precedence", "rule"}, f"artifact_overlap_arbitrations[{index}]")
        classes = _strings(arbitration["class_ids"], f"artifact_overlap_arbitrations[{index}].class_ids")
        _require(len(classes) == 2 and set(classes) <= ARTIFACT_CLASSES, "artifact overlap must name two known classes")
        pair = frozenset(classes)
        _require(pair not in observed_pairs, "duplicate artifact overlap arbitration")
        _require(arbitration["precedence"] in pair, "artifact overlap precedence must be one of its classes")
        _string(arbitration["rule"], f"artifact_overlap_arbitrations[{index}].rule")
        observed_pairs.add(pair)
    _require(observed_pairs == expected_pairs, "artifact class overlap is not fully arbitrated")

    policy = _object(root["change_policy"], "change_policy")
    _exact_keys(policy, {"default_rule", "overlap_rule", "ownership_change_rule", "artifact_rule", "handoff_required_when"}, "change_policy")
    for field in ("default_rule", "overlap_rule", "ownership_change_rule", "artifact_rule"):
        _string(policy[field], f"change_policy.{field}")
    _strings(policy["handoff_required_when"], "change_policy.handoff_required_when")

    handoff = _object(root["handoff_contract"], "handoff_contract")
    _exact_keys(handoff, {"schema_version", "required_fields", "optional_fields", "sha_pattern", "minimum_tests", "rollback_min_length"}, "handoff_contract")
    _require(handoff["schema_version"] == HANDOFF_SCHEMA, f"handoff schema must be {HANDOFF_SCHEMA}")
    required_handoff = set(_strings(handoff["required_fields"], "handoff_contract.required_fields"))
    _require(required_handoff == {"schema_version", "source_lane", "target_lane", "repositories", "from_sha", "to_sha", "tests", "rollback"}, "handoff contract must require SHA, tests and rollback fields")
    _strings(handoff["optional_fields"], "handoff_contract.optional_fields", allow_empty=True)
    _require(handoff["sha_pattern"] == FULL_SHA.pattern, "handoff SHA pattern must require full lowercase SHAs")
    _require(type(handoff["minimum_tests"]) is int and handoff["minimum_tests"] >= 1, "handoff must require tests")
    _require(type(handoff["rollback_min_length"]) is int and handoff["rollback_min_length"] >= 12, "handoff rollback minimum is too weak")

    _validate_codeowners(root, identities)
    return root


def validate_handoff(payload: Any, ledger: dict[str, Any]) -> dict[str, Any]:
    handoff = _object(payload, "handoff")
    contract = _object(ledger["handoff_contract"], "handoff_contract")
    required = set(contract["required_fields"])
    optional = set(contract["optional_fields"])
    _exact_keys(handoff, required, "handoff", optional=optional)
    _require(handoff["schema_version"] == HANDOFF_SCHEMA, f"handoff.schema_version must be {HANDOFF_SCHEMA}")
    lanes = {lane["id"] for lane in ledger["lanes"]}
    source_lane = _string(handoff["source_lane"], "handoff.source_lane")
    target_lane = _string(handoff["target_lane"], "handoff.target_lane")
    _require(source_lane in lanes and target_lane in lanes, "handoff names an unknown lane")
    _require(source_lane != target_lane, "handoff must cross lane ownership")
    repositories = _strings(handoff["repositories"], "handoff.repositories")
    known_repositories = {repository["key"] for repository in ledger["repositories"]}
    _require(set(repositories) <= known_repositories, "handoff names an unknown repository")
    for field in ("from_sha", "to_sha"):
        sha = _string(handoff[field], f"handoff.{field}")
        _require(FULL_SHA.fullmatch(sha) is not None, f"handoff.{field} must be a full lowercase SHA")
    _require(handoff["from_sha"] != handoff["to_sha"], "handoff SHAs must identify a change")
    tests = _strings(handoff["tests"], "handoff.tests")
    _require(len(tests) >= contract["minimum_tests"], "handoff has no test evidence")
    rollback = _string(handoff["rollback"], "handoff.rollback")
    _require(len(rollback) >= contract["rollback_min_length"], "handoff rollback is too short")
    if "artifact_classes" in handoff:
        _require(set(_strings(handoff["artifact_classes"], "handoff.artifact_classes", allow_empty=True)) <= ARTIFACT_CLASSES, "handoff names an unknown artifact class")
    if "arbitration_ids" in handoff:
        known_arbitrations = {
            repository["arbitration"]["id"]
            for repository in ledger["repositories"]
            if repository["arbitration"] is not None
        }
        _require(set(_strings(handoff["arbitration_ids"], "handoff.arbitration_ids", allow_empty=True)) <= known_arbitrations, "handoff names an unknown arbitration")
    if "notes" in handoff:
        _string(handoff["notes"], "handoff.notes")
    return handoff


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("validate", "validate-handoff"), nargs="?", default="validate")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--handoff", type=Path)
    args = parser.parse_args()
    try:
        ledger = validate_ledger(args.ledger)
        if args.action == "validate-handoff":
            _require(args.handoff is not None, "validate-handoff requires --handoff")
            validate_handoff(_load_json(args.handoff), ledger)
    except OwnershipLedgerError as exc:
        parser.error(str(exc))
    print(f"validated {args.ledger}")
    if args.action == "validate-handoff":
        print(f"validated {args.handoff}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
