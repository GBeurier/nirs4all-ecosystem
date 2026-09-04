#!/usr/bin/env python3
"""Validate and resolve the exhaustive candidate V1 promise ledger.

The ledger inventories public V1 promises rather than every implementation. It
binds each promise to a disposition, strict preflight and immutable candidate
evidence without promoting the candidate heads into the published release lock.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
try:  # Python 3.11+; keep the CLI usable by the release tooling's 3.10 host.
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - depends on the invoking interpreter
    import tomli as tomllib
from pathlib import Path
from typing import Any, Iterable


LEDGER_SCHEMA_VERSION = "n4a.native-capability-ledger/v1"
DEFAULT_LEDGER = Path("docs/contracts/release/native-capability-ledger.v1.json")
DEFAULT_MANIFEST = Path("docs/contracts/release/aggregation-manifest.n4a.json")
DEFAULT_LOCK = Path("docs/contracts/release/aggregation-lock.n4a.lock.json")
DEFAULT_SURFACE_MATRIX = Path("docs/contracts/release/public-v1-surface-matrix.n4a.json")
MAX_LEDGER_BYTES = 128 * 1024
MAX_CAPABILITIES = 128

KINDS = {"api", "model", "operator", "format"}
DISPOSITIONS = {"native", "plugin", "refused", "not-promised"}
ERROR_CODES = {"unknown", "refused", "not-promised", "plugin_missing"}
PREFLIGHT_DECISIONS = {
    "native": "allow_native",
    "plugin": "require_plugin",
    "refused": "refuse",
    "not-promised": "refuse",
}
PREFLIGHT_BOUNDARIES = {
    "scientific_data_access",
    "result_write",
    "meaningful_compute",
}
INPUT_NAMES = {
    "aggregation_manifest": DEFAULT_MANIFEST,
    "aggregation_lock": DEFAULT_LOCK,
    "surface_matrix": DEFAULT_SURFACE_MATRIX,
}
V1_REQUIRED_GATE_COMPONENT_KEYS = {
    "core",
    "dag_ml",
    "dag_ml_data",
    "datasets",
    "formats",
    "io",
    "methods",
}
EXTENSION_NAMESPACE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)+$")
STABLE_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$")
PLS_OPERATOR_ALIASES = {
    "sklearn.cross_decomposition.PLSRegression",
    "sklearn.cross_decomposition._pls.PLSRegression",
}
RUNTIME_AVAILABILITY = {"executable", "metadata"}
ROLLBACK_PROFILE = "rollback-capable"
LEGACY_ORACLE_CAPABILITY = "nirs4all.python.oracle.legacy-backend"
LEGACY_ENGINE_SOURCES = {
    "nirs4all/pipeline/engine.py",
    "nirs4all/api/run.py",
}
PORTABLE_CONTROLLER_KINDS = {
    "split.kennard_stone": "operator",
    "preprocess.snv": "operator",
    "preprocess.savgol": "operator",
    "model.pls_regression": "model",
    "pipeline.portable_methods": "api",
}
ROADMAP_REQUIRED_SURFACE_IDS = {
    "nirs4all.studio.product",
    "nirs4all.ui.package",
    "nirs4all.web.product",
    "nirs4all.tools.migration",
    "nirs4all.providers.contracts",
    "nirs4all.repository.catalog",
    "nirs4all.cockpit.product",
    "nirs4all.org.site",
}
V1_SURFACE_SCOPE_EXTENSION = "nirs4all.v1_surface_scope"


class CapabilityLedgerError(RuntimeError):
    """A machine-readable contract refusal or validation error."""

    def __init__(self, message: str, *, code: str = "invalid_ledger") -> None:
        self.code = code
        super().__init__(f"[{code}] {message}")


def _require(condition: bool, message: str, *, code: str = "invalid_ledger") -> None:
    if not condition:
        raise CapabilityLedgerError(message, code=code)


def _compat_object(value: Any, path: str, required: set[str], *, optional: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CapabilityLedgerError(f"{path} must be an object", code="compatibility_type")
    optional = optional or set()
    missing = sorted(required - set(value))
    unknown = sorted(set(value) - required - optional)
    if missing:
        raise CapabilityLedgerError(f"{path} is missing V1 core fields: {missing}", code="compatibility_missing_field")
    if unknown:
        raise CapabilityLedgerError(f"{path} has unsupported V1 core fields: {unknown}", code="compatibility_unknown_field")
    return value


def _compat_string(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise CapabilityLedgerError(f"{path} must be a string", code="compatibility_type")
    return value


def _compat_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise CapabilityLedgerError(f"{path} must be an array", code="compatibility_type")
    return value


def _compat_string_list(value: Any, path: str) -> list[str]:
    items = _compat_list(value, path)
    for index, item in enumerate(items):
        _compat_string(item, f"{path}[{index}]")
    return items


def _compat_extensions(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CapabilityLedgerError(f"{path} must be an object", code="compatibility_type")
    extensions = value
    for namespace, payload in extensions.items():
        if not isinstance(namespace, str) or EXTENSION_NAMESPACE.fullmatch(namespace) is None:
            raise CapabilityLedgerError(
                f"{path} has an invalid V1 extension namespace: {namespace!r}",
                code="compatibility_type",
            )
        if not isinstance(payload, dict):
            raise CapabilityLedgerError(
                f"{path}.{namespace} must be an object",
                code="compatibility_type",
            )
    return extensions


def _object(value: Any, path: str) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{path} must be an object")
    return value


def _non_empty_string(value: Any, path: str) -> str:
    _require(isinstance(value, str) and value.strip(), f"{path} must be a non-empty string")
    return value


def _string_list(value: Any, path: str, *, non_empty: bool = True) -> list[str]:
    _require(isinstance(value, list) and (bool(value) or not non_empty), f"{path} must be a non-empty list")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_non_empty_string(item, f"{path}[{index}]"))
    _require(len(result) == len(set(result)), f"{path} must not contain duplicates")
    return result


def _list(value: Any, path: str, *, non_empty: bool = True) -> list[Any]:
    _require(isinstance(value, list) and (bool(value) or not non_empty), f"{path} must be a non-empty list")
    return value


def _exact_keys(value: dict[str, Any], required: set[str], path: str, *, optional: set[str] | None = None) -> None:
    optional = optional or set()
    missing = sorted(required - set(value))
    unknown = sorted(set(value) - required - optional)
    _require(not missing, f"{path} is missing required fields: {missing}")
    _require(not unknown, f"{path} has unsupported fields: {unknown}")


def canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _strict_json_loads(raw: bytes, label: str) -> Any:
    """Decode contract JSON without silently accepting ambiguous values."""
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise CapabilityLedgerError(
                    f"invalid JSON {label}: duplicate object key {key!r}",
                    code="invalid_json",
                )
            value[key] = item
        return value

    def reject_non_finite(token: str) -> None:
        raise CapabilityLedgerError(
            f"invalid JSON {label}: non-finite constant {token!r} is not permitted",
            code="invalid_json",
        )

    try:
        return json.loads(
            raw,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_non_finite,
        )
    except CapabilityLedgerError:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise CapabilityLedgerError(f"invalid JSON {label}: {exc}", code="invalid_json") from exc


def _load_json(path: Path, label: str) -> Any:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CapabilityLedgerError(f"cannot read {label} {path}: {exc}") from exc
    return _strict_json_loads(raw, f"{label} {path}")


def _extensions(value: Any, path: str) -> None:
    extensions = _object(value, path)
    for namespace, payload in extensions.items():
        _require(
            isinstance(namespace, str) and EXTENSION_NAMESPACE.fullmatch(namespace) is not None,
            f"{path} extension namespace must be dotted, dashed, or underscored: {namespace!r}",
        )
        _object(payload, f"{path}.{namespace}")


def _preflight_before(value: Any, path: str) -> None:
    names = _string_list(value, path)
    _require(set(names) == PREFLIGHT_BOUNDARIES, f"{path} must name every strict preflight boundary exactly once")


def _release_lock_module() -> Any:
    """Load the release-lock implementation that owns selected-member semantics."""
    path = Path(__file__).resolve().with_name("n4a_release_lock.py")
    try:
        spec = importlib.util.spec_from_file_location("n4a_release_lock_for_capabilities", path)
        _require(spec is not None and spec.loader is not None, "cannot load release-lock validator")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except (OSError, ImportError) as exc:
        raise CapabilityLedgerError(f"cannot load release-lock validator: {exc}") from exc


def _validate_release_lock(release_lock: Any, ecosystem_root: Path, workspace_root: Path) -> None:
    """Delegate selected-workspace verification to the canonical release-lock gate."""
    manifest_path = ecosystem_root / DEFAULT_MANIFEST
    lock_path = ecosystem_root / DEFAULT_LOCK
    try:
        release_lock.validate_lock(manifest_path, lock_path, workspace_root)
    except release_lock.RelError as exc:
        raise CapabilityLedgerError(
            "release-lock validation failed for selected-member workspace "
            f"{workspace_root}: {exc}"
        ) from exc


def _selected_members(manifest: dict[str, Any], lock: dict[str, Any], workspace_root: Path) -> dict[str, dict[str, Any]]:
    manifest_components = _list(manifest.get("components"), "aggregation manifest components")
    manifest_by_key: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(manifest_components):
        component = _object(item, f"aggregation manifest components[{index}]")
        key = _non_empty_string(component.get("key"), f"aggregation manifest components[{index}].key")
        _require(key not in manifest_by_key, f"aggregation manifest has duplicate component key: {key}")
        manifest_by_key[key] = component
    lock_members = _object(lock.get("members"), "release lock members")
    selected: dict[str, dict[str, Any]] = {}
    for key, item in lock_members.items():
        _non_empty_string(key, "release lock member key")
        member = _object(item, f"release lock members.{key}")
        _require(key in manifest_by_key, f"release lock member {key!r} is absent from the aggregation manifest")
        selected_path = _non_empty_string(member.get("selected_workspace_path"), f"release lock members.{key}.selected_workspace_path")
        _require(selected_path == _non_empty_string(manifest_by_key[key].get("selected_workspace_path"), f"aggregation manifest component {key}.selected_workspace_path"), f"release lock member {key!r} selected workspace does not match manifest")
        _require(not Path(selected_path).is_absolute() and ".." not in Path(selected_path).parts, f"release lock member {key!r} selected workspace path is unsafe")
        state = _object(member.get("state"), f"release lock members.{key}.state")
        commit = _non_empty_string(state.get("commit"), f"release lock members.{key}.state.commit")
        _require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, f"release lock members.{key}.state.commit must be a full git SHA")
        component_root = (workspace_root / selected_path).resolve()
        _require(component_root.is_relative_to(workspace_root), f"release lock member {key!r} resolves outside workspace root")
        _require(component_root.is_dir(), f"selected workspace for lock member {key!r} does not exist: {component_root}")
        selected[key] = {"root": component_root, "member": member, "commit": commit}
    return selected


def _validate_evidence(
    value: Any,
    path: str,
    selected_members: dict[str, dict[str, Any]],
    matrix: dict[str, Any],
    ecosystem_root: Path,
    release_lock: Any,
) -> list[dict[str, Any]]:
    _list(value, path)
    evidence_rows: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        evidence = _object(item, f"{path}[{index}]")
        has_component = "component_key" in evidence
        has_outside_surface = "outside_lock_surface_id" in evidence
        has_candidate = "candidate_key" in evidence
        _require(
            sum((has_component, has_outside_surface, has_candidate)) == 1,
            f"{path}[{index}] must bind one lock member, outside-lock surface, or candidate head",
        )
        if has_component:
            expected = {"source", "claim", "component_key"}
        elif has_outside_surface:
            expected = {"source", "claim", "outside_lock_surface_id", "commit"}
        else:
            expected = {"source", "claim", "candidate_key", "commit", "source_sha256"}
        _exact_keys(evidence, expected, f"{path}[{index}]")
        source = _non_empty_string(evidence["source"], f"{path}[{index}].source")
        _non_empty_string(evidence["claim"], f"{path}[{index}].claim")
        _require(not Path(source).is_absolute() and ".." not in Path(source).parts, f"{path}[{index}].source escapes selected checkout")
        if has_candidate:
            candidates = {
                candidate.get("key"): candidate
                for candidate in _object(matrix.get("candidate_heads"), "surface matrix candidate_heads").get(
                    "components", []
                )
                if isinstance(candidate, dict)
            }
            candidate_key = _non_empty_string(evidence["candidate_key"], f"{path}[{index}].candidate_key")
            candidate = _object(candidates.get(candidate_key), f"{path}[{index}].candidate_key")
            commit = _non_empty_string(evidence["commit"], f"{path}[{index}].commit")
            _require(commit == candidate.get("commit"), f"{path}[{index}].commit does not match candidate head")
            digest = _non_empty_string(evidence["source_sha256"], f"{path}[{index}].source_sha256")
            _require(
                re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is not None,
                f"{path}[{index}].source_sha256 is invalid",
            )
            evidence_rows.append(evidence)
            continue
        if has_component:
            component_key = _non_empty_string(evidence["component_key"], f"{path}[{index}].component_key")
            _require(component_key in selected_members, f"{path}[{index}].component_key is not a selected lock member: {component_key}")
            component_root = selected_members[component_key]["root"]
            label = f"{path}[{index}].component_key"
        else:
            surface_id = _non_empty_string(evidence["outside_lock_surface_id"], f"{path}[{index}].outside_lock_surface_id")
            commit = _non_empty_string(evidence["commit"], f"{path}[{index}].commit")
            _require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, f"{path}[{index}].commit must be a full git SHA")
            surfaces = {
                surface.get("id"): surface
                for surface in _list(matrix.get("public_v1_surfaces"), "surface matrix public_v1_surfaces")
                if isinstance(surface, dict) and isinstance(surface.get("id"), str)
            }
            surface = _object(surfaces.get(surface_id), f"{path}[{index}].outside_lock_surface_id")
            _require(surface.get("lock_relation") == "outside_aggregation_lock", f"{path}[{index}].outside_lock_surface_id must remain outside the aggregation lock")
            _require(surface.get("lock_member_key") is None, f"{path}[{index}].outside_lock_surface_id must not claim a lock member")
            repo_path = _non_empty_string(surface.get("repo_path"), f"surface matrix {surface_id}.repo_path")
            _require(not Path(repo_path).is_absolute() and ".." not in Path(repo_path).parts, f"surface matrix {surface_id}.repo_path is unsafe")
            component_root = (ecosystem_root / repo_path).resolve()
            _require(component_root.is_relative_to(ecosystem_root), f"surface matrix {surface_id}.repo_path escapes ecosystem root")
            try:
                state = release_lock.repo_state(component_root)
            except release_lock.RelError as exc:
                raise CapabilityLedgerError(f"{path}[{index}] outside-lock source is not a readable git checkout: {component_root}") from exc
            _require(state["dirty"] is False, f"{path}[{index}] outside-lock source checkout must be clean")
            _require(state["commit"] == commit, f"{path}[{index}] outside-lock source is not at evidence commit {commit}")
            label = f"{path}[{index}].outside_lock_surface_id"
        try:
            release_lock.require_tracked_source(component_root, source, label)
            source_bytes = release_lock.git_head_file_bytes(component_root, source)
        except release_lock.RelError as exc:
            raise CapabilityLedgerError(f"{label} evidence source cannot be read from tracked HEAD: {source}") from exc
        _require(source_bytes is not None, f"{label} evidence source is absent from tracked HEAD: {source}")
        evidence["_head_source"] = source_bytes.decode("utf-8", errors="replace")
        evidence_rows.append(evidence)
    return evidence_rows


def _validate_runtime_assertions(value: Any, path: str, evidence: list[dict[str, Any]]) -> dict[str, str]:
    assertions = _list(value, path)
    evidence_sources = {item["source"] for item in evidence}
    result: dict[str, str] = {}
    for index, item in enumerate(assertions):
        assertion = _object(item, f"{path}[{index}]")
        _exact_keys(assertion, {"runtime", "availability", "evidence_sources"}, f"{path}[{index}]")
        runtime = _non_empty_string(assertion["runtime"], f"{path}[{index}].runtime")
        _require(runtime not in result, f"{path} has duplicate runtime assertion: {runtime}")
        availability = assertion["availability"]
        _require(availability in RUNTIME_AVAILABILITY, f"{path}[{index}].availability must be one of {sorted(RUNTIME_AVAILABILITY)}")
        sources = _string_list(assertion["evidence_sources"], f"{path}[{index}].evidence_sources")
        _require(set(sources) <= evidence_sources, f"{path}[{index}].evidence_sources must refer to entry evidence")
        result[runtime] = availability
    return result


def _validate_unbound_evidence(value: Any, path: str) -> list[dict[str, Any]]:
    """Validate evidence shape for in-memory resolution; checkout binding is validate_ledger's job."""
    rows = _list(value, path)
    result: list[dict[str, Any]] = []
    for index, item in enumerate(rows):
        evidence = _object(item, f"{path}[{index}]")
        has_component = "component_key" in evidence
        has_outside_surface = "outside_lock_surface_id" in evidence
        has_candidate = "candidate_key" in evidence
        _require(
            sum((has_component, has_outside_surface, has_candidate)) == 1,
            f"{path}[{index}] must bind one lock member, outside-lock surface, or candidate head",
        )
        if has_component:
            expected = {"source", "claim", "component_key"}
        elif has_outside_surface:
            expected = {"source", "claim", "outside_lock_surface_id", "commit"}
        else:
            expected = {"source", "claim", "candidate_key", "commit", "source_sha256"}
        _exact_keys(evidence, expected, f"{path}[{index}]")
        if has_component:
            _non_empty_string(evidence["component_key"], f"{path}[{index}].component_key")
        elif has_outside_surface:
            _non_empty_string(evidence["outside_lock_surface_id"], f"{path}[{index}].outside_lock_surface_id")
            commit = _non_empty_string(evidence["commit"], f"{path}[{index}].commit")
            _require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, f"{path}[{index}].commit must be a full git SHA")
        else:
            _non_empty_string(evidence["candidate_key"], f"{path}[{index}].candidate_key")
            commit = _non_empty_string(evidence["commit"], f"{path}[{index}].commit")
            _require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, f"{path}[{index}].commit must be a full git SHA")
            digest = _non_empty_string(evidence["source_sha256"], f"{path}[{index}].source_sha256")
            _require(
                re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is not None,
                f"{path}[{index}].source_sha256 is invalid",
            )
        _non_empty_string(evidence["source"], f"{path}[{index}].source")
        _non_empty_string(evidence["claim"], f"{path}[{index}].claim")
        result.append(evidence)
    return result


def _validate_required_gates(value: Any, path: str, manifest: dict[str, Any], lock: dict[str, Any]) -> None:
    gates = _validate_v1_required_gates(value, path)
    # Outside-lock surfaces deliberately have no component-local release gate.
    # Their bounded disposition is still checked by evidence and the crosswalk.
    manifest_components = {}
    for index, item in enumerate(_list(manifest.get("components"), "aggregation manifest components")):
        component = _object(item, f"aggregation manifest components[{index}]")
        manifest_components[_non_empty_string(component.get("key"), f"aggregation manifest components[{index}].key")] = component
    lock_members = _object(lock.get("members"), "release lock members")
    for component_key, gate_ids in gates.items():
        _non_empty_string(component_key, f"{path} component key")
        ids = _string_list(gate_ids, f"{path}.{component_key}")
        _require(component_key in manifest_components, f"{path}.{component_key} is not a manifest component")
        _require(component_key in lock_members, f"{path}.{component_key} is not a lock member")
        declared = _string_list(manifest_components[component_key].get("required_gates"), f"manifest component {component_key}.required_gates")
        missing = sorted(set(ids) - set(declared))
        _require(not missing, f"{path}.{component_key} are not manifest required_gates: {missing}")
        lock_member = _object(lock_members[component_key], f"lock member {component_key}")
        lock_declared = _string_list(lock_member.get("required_gates"), f"lock member {component_key}.required_gates")
        _require(set(ids) <= set(lock_declared), f"{path}.{component_key} are absent from lock required_gates")


def _validate_v1_required_gates(value: Any, path: str) -> dict[str, Any]:
    """Close V1 gate maps to the lock/manifest component vocabulary."""
    gates = _object(value, path)
    for component_key, gate_ids in gates.items():
        _non_empty_string(component_key, f"{path} component key")
        _require(
            component_key in V1_REQUIRED_GATE_COMPONENT_KEYS,
            f"{path}.{component_key} is not a V1 release component",
        )
        _string_list(gate_ids, f"{path}.{component_key}")
    return gates


def _validate_preflight(value: Any, disposition: str, path: str) -> None:
    _require(disposition in DISPOSITIONS, f"{path} has an invalid disposition")
    preflight = _object(value, path)
    optional = {"plugin"} if disposition == "plugin" else set()
    _exact_keys(preflight, {"profile", "decision", "before"}, path, optional=optional)
    _require(preflight["profile"] == "strict", f"{path}.profile must be 'strict'")
    _require(preflight["decision"] == PREFLIGHT_DECISIONS[disposition], f"{path}.decision is inconsistent with {disposition!r}")
    _preflight_before(preflight["before"], f"{path}.before")
    if disposition != "plugin":
        return
    plugin = _object(preflight.get("plugin"), f"{path}.plugin")
    _exact_keys(plugin, {"id", "required", "on_missing_plugin"}, f"{path}.plugin")
    _non_empty_string(plugin["id"], f"{path}.plugin.id")
    _require(plugin["required"] is True, f"{path}.plugin.required must be true")
    _require(plugin["on_missing_plugin"] == "refuse", f"{path}.plugin.on_missing_plugin must be 'refuse'")


def _validate_scope(value: Any, path: str, surface_ids: set[str]) -> None:
    scope = _object(value, path)
    _exact_keys(scope, {"profile", "runtime", "surface_ids"}, path)
    _require(scope["profile"] == "strict", f"{path}.profile must be 'strict'")
    _non_empty_string(scope["runtime"], f"{path}.runtime")
    ids = _string_list(scope["surface_ids"], f"{path}.surface_ids")
    unknown = sorted(set(ids) - surface_ids)
    _require(not unknown, f"{path}.surface_ids reference unknown release surfaces: {unknown}")


def _validate_strict_profile(value: Any) -> None:
    profile = _object(value, "strict_profile")
    _exact_keys(profile, {"name", "unknown_entry", "no_implicit_executable_default"}, "strict_profile")
    _require(profile["name"] == "strict", "strict_profile.name must be 'strict'")
    _require(profile["no_implicit_executable_default"] is True, "strict_profile.no_implicit_executable_default must be true")
    unknown_entry = _object(profile["unknown_entry"], "strict_profile.unknown_entry")
    _exact_keys(unknown_entry, {"disposition", "decision", "before", "error_code"}, "strict_profile.unknown_entry")
    _require(unknown_entry["disposition"] == "refused", "strict_profile.unknown_entry.disposition must be 'refused'")
    _require(unknown_entry["decision"] == "refuse", "strict_profile.unknown_entry.decision must be 'refuse'")
    _require(unknown_entry["error_code"] == "unknown", "strict_profile.unknown_entry.error_code must be 'unknown'")
    _preflight_before(unknown_entry["before"], "strict_profile.unknown_entry.before")


def _validate_evolution_policy(value: Any) -> None:
    policy = _object(value, "evolution_policy")
    _exact_keys(policy, {"governed_by", "v1_extension_mode", "unknown_core_fields", "future_major_dual_read", "legacy_prediction_readable_releases"}, "evolution_policy")
    _require(policy["governed_by"] == "ADR-02", "evolution_policy.governed_by must be 'ADR-02'")
    _require(policy["v1_extension_mode"] == "namespaced_optional_reader_ignore", "evolution_policy.v1_extension_mode must preserve additive reader-ignore extensions")
    _require(policy["unknown_core_fields"] == "refuse", "evolution_policy.unknown_core_fields must be 'refuse'")
    _require(policy["future_major_dual_read"] == 1, "evolution_policy.future_major_dual_read must be one release")
    _require(policy["legacy_prediction_readable_releases"] == 2, "evolution_policy.legacy_prediction_readable_releases must be two releases")


def _validate_release_context(value: Any, repository_root: Path, *, verify_inputs: bool) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    context = _object(value, "release_context")
    _exact_keys(context, {"release_train", "inputs"}, "release_context")
    release_train = _non_empty_string(context["release_train"], "release_context.release_train")
    inputs = _object(context["inputs"], "release_context.inputs")
    _require(set(inputs) == set(INPUT_NAMES), "release_context.inputs must name manifest, lock, and surface matrix exactly")
    loaded: dict[str, dict[str, Any]] = {}
    for name, expected_path in INPUT_NAMES.items():
        item = _object(inputs[name], f"release_context.inputs.{name}")
        _exact_keys(item, {"path", "canonical_json_sha256"}, f"release_context.inputs.{name}")
        path_text = _non_empty_string(item["path"], f"release_context.inputs.{name}.path")
        _require(Path(path_text) == expected_path, f"release_context.inputs.{name}.path must be {expected_path}")
        digest = _non_empty_string(item["canonical_json_sha256"], f"release_context.inputs.{name}.canonical_json_sha256")
        _require(re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is not None, f"release_context.inputs.{name}.canonical_json_sha256 must be a sha256 digest")
        if verify_inputs:
            payload = _object(_load_json(repository_root / expected_path, name), name)
            _require(canonical_json_sha256(payload) == digest, f"release_context.inputs.{name} digest does not match {expected_path}")
            _require(payload.get("release_train") == release_train, f"{name}.release_train does not match ledger release_context.release_train")
            loaded[name] = payload
    if not verify_inputs:
        return {}, {}, {}
    manifest, lock, matrix = loaded["aggregation_manifest"], loaded["aggregation_lock"], loaded["surface_matrix"]
    _require(lock.get("manifest_digest") == inputs["aggregation_manifest"]["canonical_json_sha256"], "release lock manifest_digest does not match release_context manifest digest")
    return manifest, lock, matrix


def _validate_crosswalk(value: Any, capabilities: dict[str, dict[str, Any]], matrix: dict[str, Any], lock: dict[str, Any]) -> None:
    rows = value
    _require(isinstance(rows, list) and rows, "release_surface_crosswalk must be a non-empty list")
    surfaces = {
        surface["id"]: surface
        for surface in matrix.get("public_v1_surfaces", [])
        if isinstance(surface, dict) and isinstance(surface.get("id"), str)
    }
    _require(surfaces, "surface matrix has no readable public_v1_surfaces")
    seen: set[str] = set()
    for index, item in enumerate(rows):
        path = f"release_surface_crosswalk[{index}]"
        row = _object(item, path)
        _exact_keys(row, {"capability_id", "surface_ids", "component_keys", "relation", "does_not_imply"}, path)
        capability_id = _non_empty_string(row["capability_id"], f"{path}.capability_id")
        _require(capability_id in capabilities, f"{path}.capability_id is not in capabilities")
        _require(capability_id not in seen, f"duplicate release_surface_crosswalk capability_id: {capability_id}")
        seen.add(capability_id)
        surface_ids = _string_list(row["surface_ids"], f"{path}.surface_ids")
        _require(
            set(surface_ids) == set(capabilities[capability_id]["disposition_scope"]["surface_ids"]),
            f"{path}.surface_ids must equal its capability disposition_scope.surface_ids",
        )
        missing = sorted(set(surface_ids) - set(surfaces))
        _require(not missing, f"{path}.surface_ids reference unknown release surfaces: {missing}")
        component_keys = _string_list(row["component_keys"], f"{path}.component_keys", non_empty=False)
        _require(row["relation"] == "release_accounting_only", f"{path}.relation must keep surfaces distinct from capabilities")
        _require(set(_string_list(row["does_not_imply"], f"{path}.does_not_imply")) == {"execution", "availability", "parity"}, f"{path}.does_not_imply must state execution, availability, and parity")
        expected_components = {
            surfaces[surface_id].get("lock_member_key")
            for surface_id in surface_ids
            if surfaces[surface_id].get("lock_member_key") is not None
        }
        _require(
            set(component_keys) == expected_components,
            f"{path}.component_keys must equal the lock members represented by its covered surfaces",
        )
        _require(set(component_keys) <= set(lock.get("members", {})), f"{path}.component_keys contain unknown lock members")
    _require(seen == set(capabilities), "release_surface_crosswalk must contain one additive row per capability")


def _validate_portable_core_coverage(capabilities: dict[str, dict[str, Any]], selected_members: dict[str, dict[str, Any]]) -> None:
    """Prove all currently portable Core controllers from the locked TOML source."""
    _require("core" in selected_members, "baseline needs the selected core lock member")
    capabilities_toml = selected_members["core"]["root"] / "compat/capabilities.toml"
    try:
        toml = tomllib.loads(capabilities_toml.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise CapabilityLedgerError(f"cannot read locked core capabilities TOML: {exc}") from exc
    controllers = _list(toml.get("controller"), "locked core capabilities TOML controller")
    observed: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(controllers):
        controller = _object(item, f"locked core capabilities TOML controller[{index}]")
        controller_id = _non_empty_string(controller.get("id"), f"locked core capabilities TOML controller[{index}].id")
        observed[controller_id] = controller
    _require(set(observed) == set(PORTABLE_CONTROLLER_KINDS), "ledger coverage must equal every currently proved portable Core controller")
    for controller_id, expected_kind in PORTABLE_CONTROLLER_KINDS.items():
        entry = capabilities.get(controller_id)
        _require(entry is not None, f"baseline must declare portable controller {controller_id}")
        _require(entry["kind"] == expected_kind, f"{controller_id} must have kind {expected_kind}")
        _require(entry["disposition"] == "native", f"{controller_id} must be native")
        controller = observed[controller_id]
        _require(controller.get("execution_path") in {"portable_pipeline", "run_portable_pipeline"}, f"locked Core controller {controller_id} has no portable execution path")
        runtime = _object(controller.get("runtime"), f"locked Core controller {controller_id}.runtime")
        _require(set(runtime) == {"python", "r", "javascript_wasm", "rust", "matlab_octave"}, f"locked Core controller {controller_id} must declare every aggregate runtime")
        _require(all(level == "parity-validated" for level in runtime.values()), f"locked Core controller {controller_id} has unsupported runtime evidence")
        assertions = entry["_runtime_assertions"]
        _require(assertions == {name: "executable" for name in runtime}, f"{controller_id} runtime availability must derive from locked Core assertions")
    pls = capabilities["model.pls_regression"]
    aliases = set(_string_list(pls["aliases"], "model.pls_regression.aliases"))
    _require(aliases == PLS_OPERATOR_ALIASES, "model.pls_regression aliases must exactly match the portable PLS aliases")
    _require(set(observed["model.pls_regression"].get("operator_classes", [])) == PLS_OPERATOR_ALIASES, "locked Core PLS controller aliases do not match the portable aliases")
    _require(any(entry["kind"] == "format" for entry in capabilities.values()), "baseline must declare a source-backed format disposition")


def _validate_baseline_completeness(capabilities: dict[str, dict[str, Any]], crosswalk: Any) -> None:
    """Require the two non-controller boundaries that make the baseline useful."""
    aggregation = capabilities.get("dag-ml.prediction-aggregation")
    _require(aggregation is not None, "baseline must declare native prediction aggregation")
    _require(aggregation["kind"] == "api" and aggregation["disposition"] == "native", "native prediction aggregation must remain a native API capability")
    _require(aggregation["runtime"] == "dag-ml-native", "native prediction aggregation must remain bound to dag-ml-native")

    retained = capabilities.get(LEGACY_ORACLE_CAPABILITY)
    _require(retained is not None, "baseline must declare retained legacy backend availability")
    _require(retained["disposition"] == "refused", "retained legacy backend must not be promoted to native")
    _require("legacy_retention" in retained, "retained legacy backend must carry rollback retention")

    rows = _list(crosswalk, "release_surface_crosswalk")
    by_capability = {
        _non_empty_string(_object(row, "release_surface_crosswalk row").get("capability_id"), "release_surface_crosswalk row.capability_id"): row
        for row in rows
    }
    _require("dag-ml.prediction-aggregation" in by_capability, "baseline must crosswalk native prediction aggregation")
    _require(LEGACY_ORACLE_CAPABILITY in by_capability, "baseline must crosswalk retained legacy backend availability")


def _validate_exhaustive_inventory(
    capabilities: dict[str, dict[str, Any]],
    matrix: dict[str, Any],
) -> None:
    """Require a bijection between public V1 promises and disposition entries."""
    inventory = _object(matrix.get("v1_capability_inventory"), "surface_matrix.v1_capability_inventory")
    _require(inventory.get("exhaustive") is True, "surface matrix capability inventory must be exhaustive")
    promises = _list(inventory.get("promises"), "surface_matrix.v1_capability_inventory.promises")
    promise_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_promise in enumerate(promises):
        promise = _object(raw_promise, f"surface_matrix.v1_capability_inventory.promises[{index}]")
        promise_id = _non_empty_string(
            promise.get("id"),
            f"surface_matrix.v1_capability_inventory.promises[{index}].id",
        )
        _require(promise_id not in promise_by_id, f"duplicate V1 capability promise id: {promise_id}")
        promise_by_id[promise_id] = promise
    missing = sorted(set(promise_by_id) - set(capabilities))
    extra = sorted(set(capabilities) - set(promise_by_id))
    _require(not missing, f"exhaustive capability ledger omits public V1 promises: {missing}")
    _require(not extra, f"capability claims have no public V1 promise evidence: {extra}")

    candidate_heads = {
        candidate.get("key"): candidate
        for candidate in _object(matrix.get("candidate_heads"), "surface_matrix.candidate_heads").get(
            "components", []
        )
        if isinstance(candidate, dict)
    }
    seen_aliases: dict[str, str] = {}
    for capability_id, capability in capabilities.items():
        promise = promise_by_id[capability_id]
        _require(capability["kind"] == promise.get("kind"), f"{capability_id} kind differs from its public promise")
        _require(
            capability["disposition"] == promise.get("disposition"),
            f"{capability_id} disposition differs from its public promise",
        )
        _require(
            set(capability["disposition_scope"]["surface_ids"]) == set(promise.get("surface_ids", [])),
            f"{capability_id} surface scope differs from its public promise",
        )
        for alias in capability["aliases"]:
            previous = seen_aliases.get(alias)
            _require(previous is None, f"duplicate public capability alias {alias!r}: {previous} and {capability_id}")
            seen_aliases[alias] = capability_id

        promised_evidence = {
            (item.get("candidate_key"), item.get("source"), item.get("source_sha256"))
            for item in promise.get("evidence", [])
            if isinstance(item, dict)
        }
        ledger_evidence = {
            (item.get("candidate_key"), item.get("source"), item.get("source_sha256"))
            for item in capability["evidence"]
            if isinstance(item, dict) and "candidate_key" in item
        }
        _require(
            ledger_evidence == promised_evidence,
            f"{capability_id} must cite every and only its exact candidate promise evidence",
        )
        for candidate_key, _source, _digest in ledger_evidence:
            _require(candidate_key in candidate_heads, f"{capability_id} cites an unknown candidate head")


def _validate_v1_surface_scope_extension(extensions: dict[str, Any], matrix: dict[str, Any]) -> None:
    entry = _object(extensions.get(V1_SURFACE_SCOPE_EXTENSION), f"ledger.extensions.{V1_SURFACE_SCOPE_EXTENSION}")
    _exact_keys(
        entry,
        {"matrix_path", "matrix_exhaustive", "required_surface_ids", "omission_semantics"},
        f"ledger.extensions.{V1_SURFACE_SCOPE_EXTENSION}",
    )
    _require(
        entry["matrix_path"] == DEFAULT_SURFACE_MATRIX.as_posix(),
        f"ledger.extensions.{V1_SURFACE_SCOPE_EXTENSION}.matrix_path must identify the release-context surface matrix",
    )
    _require(
        entry["matrix_exhaustive"] is False,
        f"ledger.extensions.{V1_SURFACE_SCOPE_EXTENSION}.matrix_exhaustive must be false",
    )
    omission_semantics = _non_empty_string(
        entry["omission_semantics"],
        f"ledger.extensions.{V1_SURFACE_SCOPE_EXTENSION}.omission_semantics",
    )
    _require(
        "not evidence" in omission_semantics,
        f"ledger.extensions.{V1_SURFACE_SCOPE_EXTENSION}.omission_semantics must distinguish omission from V1 exclusion",
    )
    matrix_scope = _object(matrix.get("scope"), "surface_matrix.scope")
    _require(matrix_scope.get("exhaustive") is False, "surface matrix must explicitly remain non-exhaustive")
    matrix_required = _string_list(
        matrix.get("required_nirs4all_v1_surface_ids"),
        "surface_matrix.required_nirs4all_v1_surface_ids",
    )
    extension_required = _string_list(
        entry["required_surface_ids"],
        f"ledger.extensions.{V1_SURFACE_SCOPE_EXTENSION}.required_surface_ids",
    )
    _require(
        extension_required == matrix_required,
        f"ledger.extensions.{V1_SURFACE_SCOPE_EXTENSION}.required_surface_ids must exactly mirror the surface matrix",
    )
    missing = sorted(ROADMAP_REQUIRED_SURFACE_IDS - set(extension_required))
    _require(not missing, f"native capability ledger omits roadmap-required V1 surface accounting: {missing}")


def validate_ledger(
    ledger_path: Path,
    *,
    workspace_root: Path | None = None,
    ecosystem_root: Path | None = None,
    verify_release_inputs: bool = True,
) -> dict[str, Any]:
    _require(verify_release_inputs is True, "release-input verification cannot be disabled for evidence-bound capability ledgers")
    try:
        raw = ledger_path.read_bytes()
    except OSError as exc:
        raise CapabilityLedgerError(f"cannot read {ledger_path}: {exc}") from exc
    _require(len(raw) <= MAX_LEDGER_BYTES, f"ledger exceeds bounded size of {MAX_LEDGER_BYTES} bytes")
    ledger = _strict_json_loads(raw, str(ledger_path))

    root = _object(ledger, "ledger")
    _exact_keys(root, {"schema_version", "status", "scope", "strict_profile", "rollback_profile", "evolution_policy", "release_context", "capabilities", "release_surface_crosswalk", "extensions"}, "ledger")
    _require(_non_empty_string(root["schema_version"], "ledger.schema_version") == LEDGER_SCHEMA_VERSION, f"unsupported ledger schema_version: {root['schema_version']!r}")
    _require(
        root["status"] == "inventory-complete-candidate",
        "ledger.status must be 'inventory-complete-candidate' for CAP-001 closure",
    )
    scope = _object(root["scope"], "ledger.scope")
    _exact_keys(scope, {"authority", "coverage", "exhaustive"}, "ledger.scope")
    _non_empty_string(scope["authority"], "ledger.scope.authority")
    _non_empty_string(scope["coverage"], "ledger.scope.coverage")
    _require(scope["exhaustive"] is True, "ledger.scope.exhaustive must be true for the closed V1 inventory")
    _validate_strict_profile(root["strict_profile"])
    rollback = _object(root["rollback_profile"], "rollback_profile")
    _exact_keys(rollback, {"name", "backend", "native_default_release", "retention_releases"}, "rollback_profile")
    _require(rollback["name"] == ROLLBACK_PROFILE, f"rollback_profile.name must be {ROLLBACK_PROFILE!r}")
    _require(rollback["backend"] == "legacy", "rollback_profile.backend must be 'legacy'")
    _require(rollback["native_default_release"] is True, "rollback_profile.native_default_release must be true")
    _require(rollback["retention_releases"] == 2, "rollback_profile.retention_releases must preserve ADR-22's two releases")
    _validate_evolution_policy(root["evolution_policy"])
    _require(workspace_root is not None, "workspace_root is required; evidence may not default from the current directory")
    workspace_root = workspace_root.resolve()
    _require(workspace_root.is_dir(), f"workspace_root does not exist: {workspace_root}")
    ecosystem_root = (ecosystem_root or Path(__file__).resolve().parents[1]).resolve()
    _require(ecosystem_root.is_dir(), f"ecosystem_root does not exist: {ecosystem_root}")
    manifest, lock, matrix = _validate_release_context(root["release_context"], ecosystem_root, verify_inputs=verify_release_inputs)
    release_lock = _release_lock_module()
    _validate_release_lock(release_lock, ecosystem_root, workspace_root)
    selected_members = _selected_members(manifest, lock, workspace_root) if verify_release_inputs else {}
    _extensions(root["extensions"], "ledger.extensions")
    _validate_v1_surface_scope_extension(root["extensions"], matrix)

    capabilities = root["capabilities"]
    _require(isinstance(capabilities, list) and capabilities, "ledger.capabilities must be a non-empty list")
    _require(len(capabilities) <= MAX_CAPABILITIES, f"ledger.capabilities exceeds bounded maximum of {MAX_CAPABILITIES}")
    surface_ids = {surface["id"] for surface in matrix.get("public_v1_surfaces", []) if isinstance(surface, dict) and isinstance(surface.get("id"), str)} if verify_release_inputs else set()
    seen_ids: set[str] = set()
    capabilities_by_id: dict[str, dict[str, Any]] = {}
    observed_dispositions: set[str] = set()
    for index, item in enumerate(capabilities):
        path = f"ledger.capabilities[{index}]"
        capability = _object(item, path)
        _exact_keys(capability, {"id", "kind", "aliases", "language", "runtime", "disposition", "owner", "evidence", "runtime_assertions", "required_gates", "preflight", "disposition_scope", "extensions"}, path, optional={"legacy_retention"})
        capability_id = _non_empty_string(capability["id"], f"{path}.id")
        _require(STABLE_CAPABILITY_ID.fullmatch(capability_id) is not None, f"{path}.id must be a stable dotted identifier")
        _require(capability_id not in seen_ids, f"duplicate capability id: {capability_id}")
        seen_ids.add(capability_id)
        capabilities_by_id[capability_id] = capability
        _require(capability["kind"] in KINDS, f"{path}.kind must be one of {sorted(KINDS)}")
        _string_list(capability["aliases"], f"{path}.aliases", non_empty=False)
        _non_empty_string(capability["language"], f"{path}.language")
        runtime = _non_empty_string(capability["runtime"], f"{path}.runtime")
        disposition = capability["disposition"]
        _require(disposition in DISPOSITIONS, f"{path}.disposition must be one of {sorted(DISPOSITIONS)}")
        observed_dispositions.add(disposition)
        owner = _object(capability["owner"], f"{path}.owner")
        _exact_keys(owner, {"repository", "component"}, f"{path}.owner")
        _non_empty_string(owner["repository"], f"{path}.owner.repository")
        _non_empty_string(owner["component"], f"{path}.owner.component")
        evidence = (
            _validate_evidence(
                capability["evidence"],
                f"{path}.evidence",
                selected_members,
                matrix,
                ecosystem_root,
                release_lock,
            )
            if verify_release_inputs
            else _validate_unbound_evidence(capability["evidence"], f"{path}.evidence")
        )
        capability["_runtime_assertions"] = _validate_runtime_assertions(capability["runtime_assertions"], f"{path}.runtime_assertions", evidence)
        if verify_release_inputs:
            _validate_required_gates(capability["required_gates"], f"{path}.required_gates", manifest, lock)
        else:
            _validate_v1_required_gates(capability["required_gates"], f"{path}.required_gates")
        _validate_preflight(capability["preflight"], disposition, f"{path}.preflight")
        _validate_scope(capability["disposition_scope"], f"{path}.disposition_scope", surface_ids) if verify_release_inputs else _object(capability["disposition_scope"], f"{path}.disposition_scope")
        _require(capability["disposition_scope"].get("runtime") == runtime, f"{path}.disposition_scope.runtime must equal capability.runtime")
        _extensions(capability["extensions"], f"{path}.extensions")

        retention = capability.get("legacy_retention")
        if capability_id == "nirs4all.python.oracle.legacy-backend":
            retention = _object(retention, f"{path}.legacy_retention")
            _exact_keys(retention, {"profile", "decision", "runtime", "before", "native"}, f"{path}.legacy_retention")
            _require(retention["profile"] == ROLLBACK_PROFILE, f"{path}.legacy_retention.profile must be {ROLLBACK_PROFILE!r}")
            _require(retention["decision"] == "allow_legacy_retention", f"{path}.legacy_retention.decision must allow the retained legacy path")
            _require(retention["runtime"] == runtime, f"{path}.legacy_retention.runtime must equal capability.runtime")
            _require(retention["native"] is False, f"{path}.legacy_retention.native must be false")
            _preflight_before(retention["before"], f"{path}.legacy_retention.before")
            sources = {item["source"] for item in evidence}
            _require(LEGACY_ENGINE_SOURCES <= sources, f"{path}.evidence must cite executable engine=legacy selection and dispatch code")
        else:
            _require(retention is None, f"{path}.legacy_retention is reserved for the retained legacy backend")

    if verify_release_inputs:
        _validate_portable_core_coverage(capabilities_by_id, selected_members)
        _validate_baseline_completeness(capabilities_by_id, root["release_surface_crosswalk"])
        _validate_exhaustive_inventory(capabilities_by_id, matrix)
        _validate_crosswalk(root["release_surface_crosswalk"], capabilities_by_id, matrix, lock)
    for capability in capabilities_by_id.values():
        capability.pop("_runtime_assertions", None)
        for evidence in capability["evidence"]:
            evidence.pop("_head_source", None)
    if not verify_release_inputs:
        _require(isinstance(root["release_surface_crosswalk"], list), "release_surface_crosswalk must be a list")
    return root


def resolve_capability(ledger: dict[str, Any], capability_id: Any, *, profile: Any = "strict", runtime: Any = None, surface_id: Any = None, installed_plugins: Iterable[str] = ()) -> dict[str, str]:
    """Resolve only runtime evidence; release surfaces remain accounting-only."""
    _non_empty_string(capability_id, "capability_id")
    _require(profile in {"strict", ROLLBACK_PROFILE}, f"profile must be 'strict' or {ROLLBACK_PROFILE!r}")
    runtime = _non_empty_string(runtime, "runtime")
    if surface_id is not None:
        _non_empty_string(surface_id, "surface_id")
    _require(not isinstance(installed_plugins, (str, bytes, dict)) and isinstance(installed_plugins, Iterable), "installed_plugins must be an iterable of plugin ids")
    plugins = {_non_empty_string(plugin, "installed_plugins item") for plugin in installed_plugins}
    entries: dict[str, dict[str, Any]] = {}
    for index, raw_entry in enumerate(_list(_object(ledger, "ledger").get("capabilities"), "ledger.capabilities")):
        entry = _object(raw_entry, f"ledger.capabilities[{index}]")
        _exact_keys(entry, {"id", "kind", "aliases", "language", "runtime", "disposition", "owner", "evidence", "runtime_assertions", "required_gates", "preflight", "disposition_scope", "extensions"}, f"ledger.capabilities[{index}]", optional={"legacy_retention"})
        entry_id = _non_empty_string(entry.get("id"), f"ledger.capabilities[{index}].id")
        _require(entry_id not in entries, f"duplicate capability id: {entry_id}")
        entries[entry_id] = entry
    entry = entries.get(capability_id)
    if entry is None:
        raise CapabilityLedgerError("capability is not declared in the strict baseline", code="unknown")
    _object(entry.get("disposition_scope"), f"capability {capability_id}.disposition_scope")
    assertions = _validate_runtime_assertions(entry.get("runtime_assertions"), f"capability {capability_id}.runtime_assertions", _validate_unbound_evidence(entry.get("evidence"), f"capability {capability_id}.evidence"))
    if assertions.get(runtime) != "executable":
        raise CapabilityLedgerError("capability has no executable assertion for this runtime", code="unknown")
    if profile == ROLLBACK_PROFILE and "legacy_retention" in entry:
        retention = _object(entry["legacy_retention"], f"capability {capability_id}.legacy_retention")
        _require(retention.get("profile") == ROLLBACK_PROFILE and retention.get("runtime") == runtime and retention.get("native") is False, f"capability {capability_id} has an invalid legacy retention profile")
        return {"decision": "allow_legacy_retention", "capability_id": capability_id}
    disposition = entry.get("disposition")
    _require(disposition in DISPOSITIONS, f"capability {capability_id}.disposition is invalid")
    _validate_preflight(entry.get("preflight"), disposition, f"capability {capability_id}.preflight")
    if disposition == "native":
        return {"decision": "allow_native", "capability_id": capability_id}
    if disposition == "plugin":
        plugin = _object(_object(entry["preflight"], f"capability {capability_id}.preflight").get("plugin"), f"capability {capability_id}.plugin")
        if plugin["id"] not in plugins:
            raise CapabilityLedgerError(f"required plugin {plugin['id']!r} is not installed", code="plugin_missing")
        return {"decision": "allow_plugin", "capability_id": capability_id}
    raise CapabilityLedgerError(f"capability disposition is {disposition}", code=disposition)


def read_v1_compatibility_view(payload: Any) -> dict[str, Any]:
    """Read the V1 core while deliberately ignoring namespaced extensions.

    This is the additive-reader half of the ADR-02 policy.  A future major
    version must add a real dual reader; V1 never treats an extension as a new
    required core field.
    """
    if not isinstance(payload, dict):
        raise CapabilityLedgerError("ledger must be an object", code="compatibility_type")
    root = payload
    required = {
        "schema_version", "status", "scope", "strict_profile", "rollback_profile",
        "evolution_policy", "release_context", "capabilities", "release_surface_crosswalk", "extensions",
    }
    missing = sorted(required - set(root))
    if missing:
        raise CapabilityLedgerError(f"ledger is missing V1 core fields: {missing}", code="compatibility_missing_field")
    unknown = sorted(set(root) - required)
    if unknown:
        raise CapabilityLedgerError(f"ledger has unsupported V1 core fields: {unknown}", code="compatibility_unknown_field")
    schema_version = _compat_string(root["schema_version"], "ledger.schema_version")
    if schema_version != LEDGER_SCHEMA_VERSION:
        raise CapabilityLedgerError(
            f"unsupported V1 ledger schema_version: {schema_version!r}",
            code="compatibility_schema_version",
        )
    _compat_string(root["status"], "ledger.status")
    scope = _compat_object(root["scope"], "ledger.scope", {"authority", "coverage", "exhaustive"})
    _compat_string(scope["authority"], "ledger.scope.authority")
    _compat_string(scope["coverage"], "ledger.scope.coverage")
    if not isinstance(scope["exhaustive"], bool):
        raise CapabilityLedgerError("ledger.scope.exhaustive must be a boolean", code="compatibility_type")
    strict = _compat_object(root["strict_profile"], "ledger.strict_profile", {"name", "unknown_entry", "no_implicit_executable_default"})
    _compat_string(strict["name"], "ledger.strict_profile.name")
    unknown_entry = _compat_object(strict["unknown_entry"], "ledger.strict_profile.unknown_entry", {"disposition", "decision", "before", "error_code"})
    for field in {"disposition", "decision", "error_code"}:
        _compat_string(unknown_entry[field], f"ledger.strict_profile.unknown_entry.{field}")
    _compat_string_list(unknown_entry["before"], "ledger.strict_profile.unknown_entry.before")
    if not isinstance(strict["no_implicit_executable_default"], bool):
        raise CapabilityLedgerError("ledger.strict_profile.no_implicit_executable_default must be a boolean", code="compatibility_type")
    rollback = _compat_object(root["rollback_profile"], "ledger.rollback_profile", {"name", "backend", "native_default_release", "retention_releases"})
    _compat_string(rollback["name"], "ledger.rollback_profile.name")
    _compat_string(rollback["backend"], "ledger.rollback_profile.backend")
    if not isinstance(rollback["native_default_release"], bool) or type(rollback["retention_releases"]) is not int:
        raise CapabilityLedgerError("ledger.rollback_profile has invalid field types", code="compatibility_type")
    evolution = _compat_object(root["evolution_policy"], "ledger.evolution_policy", {"governed_by", "v1_extension_mode", "unknown_core_fields", "future_major_dual_read", "legacy_prediction_readable_releases"})
    for field in {"governed_by", "v1_extension_mode", "unknown_core_fields"}:
        _compat_string(evolution[field], f"ledger.evolution_policy.{field}")
    if type(evolution["future_major_dual_read"]) is not int or type(evolution["legacy_prediction_readable_releases"]) is not int:
        raise CapabilityLedgerError("ledger.evolution_policy has invalid field types", code="compatibility_type")
    context = _compat_object(root["release_context"], "ledger.release_context", {"release_train", "inputs"})
    _compat_string(context["release_train"], "ledger.release_context.release_train")
    inputs = _compat_object(context["inputs"], "ledger.release_context.inputs", set(INPUT_NAMES))
    for name in INPUT_NAMES:
        digest = _compat_object(inputs[name], f"ledger.release_context.inputs.{name}", {"path", "canonical_json_sha256"})
        _compat_string(digest["path"], f"ledger.release_context.inputs.{name}.path")
        _compat_string(digest["canonical_json_sha256"], f"ledger.release_context.inputs.{name}.canonical_json_sha256")
    _compat_extensions(root["extensions"], "ledger.extensions")
    capabilities = _compat_list(root["capabilities"], "ledger.capabilities")
    crosswalk = _compat_list(root["release_surface_crosswalk"], "ledger.release_surface_crosswalk")

    capability_fields = {
        "id", "kind", "aliases", "language", "runtime", "disposition", "owner", "evidence",
        "runtime_assertions", "required_gates", "preflight", "disposition_scope", "extensions",
    }
    for index, raw_entry in enumerate(capabilities):
        raw_entry = _compat_object(raw_entry, f"ledger.capabilities[{index}]", capability_fields, optional={"legacy_retention"})
        for field in {"id", "kind", "language", "runtime", "disposition"}:
            _compat_string(raw_entry[field], f"ledger.capabilities[{index}].{field}")
        _compat_string_list(raw_entry["aliases"], f"ledger.capabilities[{index}].aliases")
        owner = _compat_object(raw_entry["owner"], f"ledger.capabilities[{index}].owner", {"repository", "component"})
        _compat_string(owner["repository"], f"ledger.capabilities[{index}].owner.repository")
        _compat_string(owner["component"], f"ledger.capabilities[{index}].owner.component")
        for evidence_index, item in enumerate(_compat_list(raw_entry["evidence"], f"ledger.capabilities[{index}].evidence")):
            evidence_path = f"ledger.capabilities[{index}].evidence[{evidence_index}]"
            if isinstance(item, dict) and "component_key" in item:
                evidence = _compat_object(item, evidence_path, {"component_key", "source", "claim"})
            elif isinstance(item, dict) and "candidate_key" in item:
                evidence = _compat_object(
                    item,
                    evidence_path,
                    {"candidate_key", "commit", "source", "source_sha256", "claim"},
                )
            else:
                evidence = _compat_object(
                    item,
                    evidence_path,
                    {"outside_lock_surface_id", "commit", "source", "claim"},
                )
            for field in evidence:
                _compat_string(evidence[field], f"{evidence_path}.{field}")
        for assertion_index, item in enumerate(_compat_list(raw_entry["runtime_assertions"], f"ledger.capabilities[{index}].runtime_assertions")):
            assertion_path = f"ledger.capabilities[{index}].runtime_assertions[{assertion_index}]"
            assertion = _compat_object(item, assertion_path, {"runtime", "availability", "evidence_sources"})
            _compat_string(assertion["runtime"], f"{assertion_path}.runtime")
            _compat_string(assertion["availability"], f"{assertion_path}.availability")
            _compat_string_list(assertion["evidence_sources"], f"{assertion_path}.evidence_sources")
        required_gates = raw_entry["required_gates"]
        if not isinstance(required_gates, dict):
            raise CapabilityLedgerError(
                f"ledger.capabilities[{index}].required_gates must be an object",
                code="compatibility_type",
            )
        unknown_gate_components = sorted(set(required_gates) - V1_REQUIRED_GATE_COMPONENT_KEYS)
        if unknown_gate_components:
            raise CapabilityLedgerError(
                f"ledger.capabilities[{index}].required_gates has unsupported V1 core fields: {unknown_gate_components}",
                code="compatibility_unknown_field",
            )
        for gate_name, gate_values in required_gates.items():
            _compat_string_list(gate_values, f"ledger.capabilities[{index}].required_gates.{gate_name}")
        preflight_path = f"ledger.capabilities[{index}].preflight"
        preflight = _compat_object(raw_entry["preflight"], preflight_path, {"profile", "decision", "before"}, optional={"plugin"})
        _compat_string(preflight["profile"], f"{preflight_path}.profile")
        _compat_string(preflight["decision"], f"{preflight_path}.decision")
        _compat_string_list(preflight["before"], f"{preflight_path}.before")
        if "plugin" in preflight:
            plugin = _compat_object(preflight["plugin"], f"{preflight_path}.plugin", {"id", "required", "on_missing_plugin"})
            _compat_string(plugin["id"], f"{preflight_path}.plugin.id")
            if not isinstance(plugin["required"], bool):
                raise CapabilityLedgerError(f"{preflight_path}.plugin.required must be a boolean", code="compatibility_type")
            _compat_string(plugin["on_missing_plugin"], f"{preflight_path}.plugin.on_missing_plugin")
        scope_path = f"ledger.capabilities[{index}].disposition_scope"
        disposition_scope = _compat_object(raw_entry["disposition_scope"], scope_path, {"profile", "runtime", "surface_ids"})
        _compat_string(disposition_scope["profile"], f"{scope_path}.profile")
        _compat_string(disposition_scope["runtime"], f"{scope_path}.runtime")
        _compat_string_list(disposition_scope["surface_ids"], f"{scope_path}.surface_ids")
        _compat_extensions(raw_entry["extensions"], f"ledger.capabilities[{index}].extensions")
        if "legacy_retention" in raw_entry:
            retention_path = f"ledger.capabilities[{index}].legacy_retention"
            retention = _compat_object(raw_entry["legacy_retention"], retention_path, {"profile", "decision", "runtime", "before", "native"})
            for field in {"profile", "decision", "runtime"}:
                _compat_string(retention[field], f"{retention_path}.{field}")
            _compat_string_list(retention["before"], f"{retention_path}.before")
            if not isinstance(retention["native"], bool):
                raise CapabilityLedgerError(f"{retention_path}.native must be a boolean", code="compatibility_type")
    for index, row in enumerate(crosswalk):
        row_path = f"ledger.release_surface_crosswalk[{index}]"
        row = _compat_object(row, row_path, {"capability_id", "surface_ids", "component_keys", "relation", "does_not_imply"})
        _compat_string(row["capability_id"], f"ledger.release_surface_crosswalk[{index}].capability_id")
        _compat_string(row["relation"], f"ledger.release_surface_crosswalk[{index}].relation")
        for field in {"surface_ids", "component_keys", "does_not_imply"}:
            _compat_string_list(row[field], f"{row_path}.{field}")
    view = {key: value for key, value in root.items() if key != "extensions"}
    view["capabilities"] = [
        {key: value for key, value in _object(entry, "ledger.capabilities entry").items() if key != "extensions"}
        for entry in root["capabilities"]
    ]
    return view


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path(__file__).resolve().parents[1] / DEFAULT_LEDGER,
        help="Ledger path (default: the ledger in this ecosystem repository).",
    )
    parser.add_argument("--workspace-root", type=Path, required=True, help="Explicit root containing the lock-selected component checkouts.")
    parser.add_argument("command", choices=("validate", "report"), nargs="?", default="validate")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        workspace_root = args.workspace_root.resolve()
        ledger_path = args.ledger if args.ledger.is_absolute() else Path(__file__).resolve().parents[1] / args.ledger
        ledger = validate_ledger(ledger_path.resolve(), workspace_root=workspace_root)
    except CapabilityLedgerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.command == "report":
        print(json.dumps({"capabilities": len(ledger["capabilities"]), "release_train": ledger["release_context"]["release_train"], "status": ledger["status"]}, sort_keys=True))
    else:
        print(f"validated {args.ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
