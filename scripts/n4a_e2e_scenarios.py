#!/usr/bin/env python3
"""Validate, plan, and optionally execute NIRS4ALL cross-language E2E scenarios."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = Path("docs/contracts/e2e/cross-language-scenarios.n4a.json")
SCHEMA_VERSION = "n4a.cross-language-e2e/v1"
EXPECTED_SCENARIO_COUNT = 10
MIN_STEPS_PER_SCENARIO = 2
MIN_ARTIFACTS_PER_SCENARIO = 2
ALLOWED_LANGUAGES = {
    "python",
    "r",
    "rust",
    "rust_archive",
    "javascript_wasm",
    "web",
    "matlab_octave",
    "native",
}
REQUIRED_TAGS = {
    "datasets",
    "io",
    "pipeline",
    "repository",
    "papers",
    "predictions",
    "workspace_save",
    "parity",
    "multimodal",
    "multisource",
    "pipeline_generation",
    "web_results",
}
ALLOWED_EVIDENCE_LEVELS = {
    "contract_smoke",
    "hybrid",
    "strict",
}
ALLOWED_CHECK_EVIDENCE_LEVELS = {
    "contract",
    "hybrid",
    "strict",
}
V1_REFACTOR_PHASE_ORDER = (
    "python_open_pipeline",
    "python_rerun_pipeline",
    "python_parity",
    "papers_export",
    "repository_forced_best_refit",
    "wasm_web_reuse",
)
V1_REFACTOR_PHASES = set(V1_REFACTOR_PHASE_ORDER)
ALLOWED_V1_REFACTOR_STATUSES = {
    "strict",
    "contract",
    "gap",
}
TOOL_FALLBACKS = {
    "R": [Path("/home/delete/miniconda3/envs/pls4all_r/bin/R")],
    "Rscript": [Path("/home/delete/miniconda3/envs/pls4all_r/bin/Rscript")],
    "node": [
        Path.home() / ".nvm/versions/node/v24.16.0/bin/node",
        Path.home() / ".nvm/versions/node/v22.21.1/bin/node",
    ],
    "npm": [Path.home() / ".nvm/versions/node/v22.21.1/bin/npm"],
    "google-chrome": [Path("/usr/bin/google-chrome"), Path("/usr/bin/chromium"), Path("/usr/bin/chromium-browser")],
}
ALLOWED_STEP_KINDS = {
    "prepare",
    "execute",
    "verify",
    "export",
    "import",
    "ui",
    "publish",
}
DISALLOWED_COMMAND_FRAGMENTS = {
    "|| true": "shell soft-success masks failed e2e commands",
    "set +e": "shell error ignoring masks failed e2e commands",
    "pytest.skip": "pytest skips are not valid parity evidence",
    "pytest.xfail": "pytest xfails are not valid parity evidence",
    "@pytest.mark.skip": "pytest skip markers are not valid parity evidence",
    "@pytest.mark.xfail": "pytest xfail markers are not valid parity evidence",
    "continue-on-error": "continue-on-error masks failed e2e commands",
    "--allow-failure": "allow-failure masks failed e2e commands",
}
STATUS_FIELD_NAMES = {"status", "parity_status", "result", "verdict"}
DISALLOWED_ARTIFACT_STATUSES = {
    "blocked",
    "error",
    "failed",
    "not_requested",
    "not_run",
    "skip",
    "skipped",
    "xfail",
    "xfailed",
}
DISALLOWED_ARTIFACT_STATUS_TOKENS = {
    "hold",
}
DISALLOWED_ARTIFACT_STATUS_SUBSTRINGS = {
    "not_executed",
}
BOOLEAN_EVIDENCE_FIELDS = {
    "finite_predictions",
    "legacy_python_replay",
    "numeric_oracle_valid",
    "ok",
    "passed",
    "success",
    "valid",
}


class E2EScenarioError(RuntimeError):
    """Invalid scenario contract or execution failure."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_workspace_root() -> Path:
    env_root = os.environ.get("N4A_WORKSPACE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    root = repo_root()
    if root.parent.name == "_worktrees":
        return root.parent.parent.resolve()
    return root.parent.resolve()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise E2EScenarioError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise E2EScenarioError(f"invalid JSON {path}: {exc}") from exc


def _strings(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise E2EScenarioError(f"{field} must be a list of strings")
    if not allow_empty and not value:
        raise E2EScenarioError(f"{field} must not be empty")
    return value


def _unique(values: list[str], field: str) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise E2EScenarioError(f"{field} contains duplicate values: {', '.join(duplicates)}")


def _format_value(value: Any, workspace_root: Path, artifacts_dir: Path) -> Any:
    if isinstance(value, str):
        return value.format(workspace_root=str(workspace_root), artifacts_dir=str(artifacts_dir))
    if isinstance(value, list):
        return [_format_value(item, workspace_root, artifacts_dir) for item in value]
    if isinstance(value, dict):
        return {key: _format_value(item, workspace_root, artifacts_dir) for key, item in value.items()}
    return value


def _tool_available(tool: str) -> bool:
    path = Path(tool).expanduser()
    if path.is_file():
        return True
    if shutil.which(tool) is not None:
        return True
    return any(candidate.is_file() for candidate in TOOL_FALLBACKS.get(tool, []))


def _normal_status(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _json_semantic_failures(value: Any, path: str = "$") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}"
            key_name = str(key).lower()
            if key_name in STATUS_FIELD_NAMES and isinstance(item, str):
                status = _normal_status(item)
                status_tokens = set(status.split("_"))
                if (
                    status in DISALLOWED_ARTIFACT_STATUSES
                    or status_tokens & DISALLOWED_ARTIFACT_STATUS_TOKENS
                    or any(fragment in status for fragment in DISALLOWED_ARTIFACT_STATUS_SUBSTRINGS)
                ):
                    failures.append(f"{child_path}={item!r}")
            if key_name in BOOLEAN_EVIDENCE_FIELDS and item is False:
                failures.append(f"{child_path}=false")
            failures.extend(_json_semantic_failures(item, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            failures.extend(_json_semantic_failures(item, f"{path}[{index}]"))
    return failures


def _produced_snapshot(paths: list[str]) -> dict[str, int | None]:
    snapshot: dict[str, int | None] = {}
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            snapshot[raw_path] = None
            continue
        try:
            snapshot[raw_path] = path.stat().st_mtime_ns
        except OSError:
            snapshot[raw_path] = None
    return snapshot


def _append_step_summary(lines: list[str]) -> None:
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary:
        return
    try:
        with Path(summary).open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    except OSError:
        return


def _parse_allowed_blocked_requirements(values: list[str]) -> dict[str, set[str]]:
    allowed: dict[str, set[str]] = {}
    for value in values:
        scenario_id, separator, fragment = value.partition("=")
        if not separator or not scenario_id or not fragment:
            raise E2EScenarioError(
                "--allowed-blocked-requirement must use SCENARIO_ID=REQUIREMENT_FRAGMENT"
            )
        allowed.setdefault(scenario_id, set()).add(fragment)
    return allowed


def _validate_produced_artifacts(step: dict[str, Any], before: dict[str, int | None]) -> list[str]:
    failures: list[str] = []
    for raw_path in step.get("produces", []):
        path = Path(raw_path)
        structural_failures = _validate_existing_artifact(raw_path)
        if structural_failures:
            failures.extend(structural_failures)
            continue
        previous_mtime = before.get(raw_path)
        if previous_mtime is not None:
            try:
                current_mtime = path.stat().st_mtime_ns
            except OSError as exc:
                failures.append(f"{raw_path}: cannot stat after step: {exc}")
                continue
            if current_mtime <= previous_mtime:
                failures.append(f"{raw_path}: stale artifact was not refreshed by step")
                continue
    return failures


def _validate_existing_artifact(raw_path: str) -> list[str]:
    path = Path(raw_path)
    if not path.exists():
        return [f"{raw_path}: missing"]
    if not path.is_file():
        return [f"{raw_path}: expected file artifact"]
    try:
        if path.stat().st_size <= 0:
            return [f"{raw_path}: empty artifact"]
    except OSError as exc:
        return [f"{raw_path}: cannot stat artifact: {exc}"]
    if path.suffix.lower() != ".json":
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{raw_path}: invalid JSON artifact: {exc}"]
    semantic_failures = _json_semantic_failures(payload)
    if semantic_failures:
        return [f"{raw_path}: non-passing evidence: {', '.join(semantic_failures)}"]
    return []


def _validate_step(scenario_id: str, step: dict[str, Any], step_ids: set[str]) -> None:
    step_id = step.get("id")
    if not isinstance(step_id, str) or not step_id:
        raise E2EScenarioError(f"{scenario_id}: each step needs a non-empty id")
    if step_id in step_ids:
        raise E2EScenarioError(f"{scenario_id}: duplicate step id {step_id!r}")
    step_ids.add(step_id)
    for field in ("title", "repo", "kind"):
        if not isinstance(step.get(field), str) or not step[field]:
            raise E2EScenarioError(f"{scenario_id}.{step_id}: {field} must be a non-empty string")
    if step["kind"] not in ALLOWED_STEP_KINDS:
        raise E2EScenarioError(f"{scenario_id}.{step_id}: unsupported kind {step['kind']!r}")
    command = step.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
        raise E2EScenarioError(f"{scenario_id}.{step_id}: command must be a non-empty list of strings")
    _strings(step.get("requires_tools", []), f"{scenario_id}.{step_id}.requires_tools", allow_empty=True)
    _strings(step.get("requires_env", []), f"{scenario_id}.{step_id}.requires_env", allow_empty=True)
    _strings(step.get("requires_paths", []), f"{scenario_id}.{step_id}.requires_paths", allow_empty=True)
    _strings(step.get("produces", []), f"{scenario_id}.{step_id}.produces", allow_empty=True)
    if not any(step.get(field) for field in ("requires_tools", "requires_env", "requires_paths")):
        raise E2EScenarioError(
            f"{scenario_id}.{step_id}: step must declare dependency gates via "
            "requires_tools, requires_env, or requires_paths"
        )
    normalized_command = " ".join(command).lower()
    for fragment, reason in DISALLOWED_COMMAND_FRAGMENTS.items():
        if fragment in normalized_command:
            raise E2EScenarioError(
                f"{scenario_id}.{step_id}: command contains disallowed fragment "
                f"{fragment!r}: {reason}"
            )


def _contains_smoke_claim(value: str) -> bool:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    return "smoke" in normalized


def _validate_evidence_contract(
    scenario_id: str,
    scenario: dict[str, Any],
    tags: set[str],
    parity_checks: list[Any],
) -> None:
    evidence_level = scenario.get("evidence_level")
    if evidence_level not in ALLOWED_EVIDENCE_LEVELS:
        raise E2EScenarioError(
            f"{scenario_id}.evidence_level must be one of: "
            + ", ".join(sorted(ALLOWED_EVIDENCE_LEVELS))
        )

    strictness_gaps = _strings(
        scenario.get("strictness_gaps", []),
        f"{scenario_id}.strictness_gaps",
        allow_empty=True,
    )
    if evidence_level == "strict" and strictness_gaps:
        raise E2EScenarioError(f"{scenario_id}: strict scenarios must not declare strictness_gaps")
    if evidence_level in {"contract_smoke", "hybrid"} and not strictness_gaps:
        raise E2EScenarioError(f"{scenario_id}: {evidence_level} scenarios must declare strictness_gaps")
    if evidence_level == "contract_smoke" and "parity" in tags:
        raise E2EScenarioError(f"{scenario_id}: contract_smoke scenarios must not use the parity tag")

    strict_check_seen = False
    for index, check in enumerate(parity_checks):
        check_level = check.get("evidence_level")
        if check_level not in ALLOWED_CHECK_EVIDENCE_LEVELS:
            raise E2EScenarioError(
                f"{scenario_id}.parity_checks[{index}].evidence_level must be one of: "
                + ", ".join(sorted(ALLOWED_CHECK_EVIDENCE_LEVELS))
            )
        metric = check.get("metric", "")
        if check_level == "strict":
            strict_check_seen = True
            if _contains_smoke_claim(metric):
                raise E2EScenarioError(
                    f"{scenario_id}.parity_checks[{index}]: strict check metric must not be smoke-only"
                )
            normalized_metric = metric.lower()
            if "schema/array coverage" in normalized_metric or "schema, row count" in normalized_metric:
                raise E2EScenarioError(
                    f"{scenario_id}.parity_checks[{index}]: strict check metric must assert numeric parity, not schema/array coverage"
                )
    if "parity" in tags and not strict_check_seen:
        raise E2EScenarioError(f"{scenario_id}: parity tag requires at least one strict parity_check")


def _validate_v1_refactor_contract(
    value: Any,
    scenario_ids: list[str],
    scenario_artifacts: dict[str, set[str]],
    scenario_evidence_levels: dict[str, str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        raise E2EScenarioError("manifest.v1_refactor_contract must be an object")
    phase_requirements = value.get("phase_requirements")
    if not isinstance(phase_requirements, dict):
        raise E2EScenarioError("manifest.v1_refactor_contract.phase_requirements must be an object")
    phase_names = set(phase_requirements)
    if phase_names != V1_REFACTOR_PHASES:
        missing = V1_REFACTOR_PHASES - phase_names
        extra = phase_names - V1_REFACTOR_PHASES
        detail = []
        if missing:
            detail.append("missing " + ", ".join(sorted(missing)))
        if extra:
            detail.append("unknown " + ", ".join(sorted(extra)))
        raise E2EScenarioError("manifest.v1_refactor_contract.phase_requirements mismatch: " + "; ".join(detail))
    for phase, requirement in phase_requirements.items():
        if not isinstance(requirement, str) or not requirement:
            raise E2EScenarioError(f"manifest.v1_refactor_contract.phase_requirements.{phase} must be a non-empty string")

    coverage = value.get("scenario_coverage")
    if not isinstance(coverage, dict):
        raise E2EScenarioError("manifest.v1_refactor_contract.scenario_coverage must be an object")
    coverage_ids = set(coverage)
    expected_ids = set(scenario_ids)
    if coverage_ids != expected_ids:
        missing = expected_ids - coverage_ids
        extra = coverage_ids - expected_ids
        detail = []
        if missing:
            detail.append("missing " + ", ".join(sorted(missing)))
        if extra:
            detail.append("unknown " + ", ".join(sorted(extra)))
        raise E2EScenarioError("manifest.v1_refactor_contract.scenario_coverage mismatch: " + "; ".join(detail))

    non_gap_phases: set[str] = set()
    validated: dict[str, dict[str, Any]] = {}
    for scenario_id in scenario_ids:
        scenario_coverage = coverage[scenario_id]
        if not isinstance(scenario_coverage, dict):
            raise E2EScenarioError(f"{scenario_id}.v1_refactor_contract must be an object")
        scenario_phases = set(scenario_coverage)
        if scenario_phases != V1_REFACTOR_PHASES:
            missing = V1_REFACTOR_PHASES - scenario_phases
            extra = scenario_phases - V1_REFACTOR_PHASES
            detail = []
            if missing:
                detail.append("missing " + ", ".join(sorted(missing)))
            if extra:
                detail.append("unknown " + ", ".join(sorted(extra)))
            raise E2EScenarioError(f"{scenario_id}.v1_refactor_contract phases mismatch: " + "; ".join(detail))
        validated[scenario_id] = scenario_coverage
        scenario_gap_phases: set[str] = set()
        scenario_strict_phases: set[str] = set()
        for phase, phase_contract in scenario_coverage.items():
            if not isinstance(phase_contract, dict):
                raise E2EScenarioError(f"{scenario_id}.v1_refactor_contract.{phase} must be an object")
            status = phase_contract.get("status")
            if status not in ALLOWED_V1_REFACTOR_STATUSES:
                raise E2EScenarioError(
                    f"{scenario_id}.v1_refactor_contract.{phase}.status must be one of: "
                    + ", ".join(sorted(ALLOWED_V1_REFACTOR_STATUSES))
                )
            evidence = _strings(
                phase_contract.get("evidence"),
                f"{scenario_id}.v1_refactor_contract.{phase}.evidence",
            )
            acceptance = _strings(
                phase_contract.get("acceptance"),
                f"{scenario_id}.v1_refactor_contract.{phase}.acceptance",
            )
            artifacts = _strings(
                phase_contract.get("artifacts", []),
                f"{scenario_id}.v1_refactor_contract.{phase}.artifacts",
                allow_empty=True,
            )
            unknown_artifacts = sorted(set(artifacts) - scenario_artifacts[scenario_id])
            if unknown_artifacts:
                raise E2EScenarioError(
                    f"{scenario_id}.v1_refactor_contract.{phase}: artifact(s) are not scenario artifacts: "
                    + ", ".join(unknown_artifacts)
                )
            gap = phase_contract.get("gap")
            if status == "gap":
                scenario_gap_phases.add(phase)
                if not isinstance(gap, str) or not gap:
                    raise E2EScenarioError(f"{scenario_id}.v1_refactor_contract.{phase}.gap must explain the missing runtime/contract")
            else:
                non_gap_phases.add(phase)
                if status == "strict" and gap is not None:
                    raise E2EScenarioError(f"{scenario_id}.v1_refactor_contract.{phase}: strict phases must not declare a gap")
                if status == "strict":
                    scenario_strict_phases.add(phase)
                if gap is not None and (not isinstance(gap, str) or not gap):
                    raise E2EScenarioError(f"{scenario_id}.v1_refactor_contract.{phase}.gap must be a non-empty string when present")
            if not evidence or not acceptance:
                raise E2EScenarioError(f"{scenario_id}.v1_refactor_contract.{phase} must declare evidence and acceptance")
        if not scenario_strict_phases:
            raise E2EScenarioError(f"{scenario_id}: must declare at least one strict V1 refactor phase")
        if scenario_evidence_levels[scenario_id] == "strict" and scenario_gap_phases:
            raise E2EScenarioError(
                f"{scenario_id}: strict scenarios must not contain gap v1_refactor phases: "
                + ", ".join(sorted(scenario_gap_phases))
            )

    missing_non_gap_phases = V1_REFACTOR_PHASES - non_gap_phases
    if missing_non_gap_phases:
        raise E2EScenarioError(
            "manifest.v1_refactor_contract lacks non-gap coverage for: "
            + ", ".join(sorted(missing_non_gap_phases))
        )
    return validated


def _validate_scenario_semantics(
    scenario_id: str,
    scenario: dict[str, Any],
    *,
    languages: set[str],
    tags: set[str],
    phases: dict[str, dict[str, Any]],
) -> None:
    repos = set(scenario["repos"])
    steps = scenario["steps"]

    if "web" in languages or "web_results" in tags:
        if "web" not in languages or "web_results" not in tags:
            raise E2EScenarioError(
                f"{scenario_id}: web language and web_results tag must be declared together"
            )
        if "nirs4all-web" not in repos:
            raise E2EScenarioError(f"{scenario_id}: web coverage requires nirs4all-web repo")
        if not any(step.get("repo") == "nirs4all-web" for step in steps):
            raise E2EScenarioError(f"{scenario_id}: web coverage requires a nirs4all-web step")
        if phases["wasm_web_reuse"]["status"] == "gap":
            raise E2EScenarioError(f"{scenario_id}: web coverage requires non-gap wasm_web_reuse")

    if "papers" in tags:
        if "nirs4all-papers" not in repos:
            raise E2EScenarioError(f"{scenario_id}: papers tag requires nirs4all-papers repo")
        if phases["papers_export"]["status"] == "gap":
            raise E2EScenarioError(f"{scenario_id}: papers tag requires non-gap papers_export")

    if "repository" in tags:
        if "nirs4all-repository" not in repos:
            raise E2EScenarioError(f"{scenario_id}: repository tag requires nirs4all-repository repo")
        produced = " ".join(
            artifact
            for step in steps
            for artifact in step.get("produces", [])
        )
        if "repository" not in produced:
            raise E2EScenarioError(f"{scenario_id}: repository tag requires a repository artifact")


def validate_scenarios(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    manifest = _read_json(path)
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise E2EScenarioError(f"unsupported schema version: {manifest.get('schema_version')!r}")
    scenarios = manifest.get("scenarios")
    if not isinstance(scenarios, list):
        raise E2EScenarioError("manifest.scenarios must be a list")
    if len(scenarios) != EXPECTED_SCENARIO_COUNT:
        raise E2EScenarioError(f"expected exactly {EXPECTED_SCENARIO_COUNT} scenarios, got {len(scenarios)}")

    scenario_ids: list[str] = []
    scenario_artifacts: dict[str, set[str]] = {}
    scenario_evidence_levels: dict[str, str] = {}
    covered_tags: set[str] = set()
    covered_languages: set[str] = set()
    for scenario in scenarios:
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not scenario_id:
            raise E2EScenarioError("each scenario needs a non-empty id")
        scenario_ids.append(scenario_id)
        for field in ("title", "objective"):
            if not isinstance(scenario.get(field), str) or not scenario[field]:
                raise E2EScenarioError(f"{scenario_id}: {field} must be a non-empty string")
        languages = set(_strings(scenario.get("languages"), f"{scenario_id}.languages"))
        unknown_languages = languages - ALLOWED_LANGUAGES
        if unknown_languages:
            raise E2EScenarioError(f"{scenario_id}: unsupported language(s): {', '.join(sorted(unknown_languages))}")
        if len(languages) < 2:
            raise E2EScenarioError(f"{scenario_id}: must cover at least two language/runtime surfaces")
        covered_languages.update(languages)
        tags = set(_strings(scenario.get("tags"), f"{scenario_id}.tags"))
        covered_tags.update(tags)
        _strings(scenario.get("repos"), f"{scenario_id}.repos")
        _strings(scenario.get("evidence"), f"{scenario_id}.evidence")
        artifacts = set(_strings(scenario.get("artifacts"), f"{scenario_id}.artifacts"))
        if len(artifacts) < MIN_ARTIFACTS_PER_SCENARIO:
            raise E2EScenarioError(
                f"{scenario_id}: must declare at least {MIN_ARTIFACTS_PER_SCENARIO} artifacts"
            )
        scenario_artifacts[scenario_id] = artifacts
        parity_checks = scenario.get("parity_checks", [])
        if not isinstance(parity_checks, list):
            raise E2EScenarioError(f"{scenario_id}.parity_checks must be a list")
        for index, check in enumerate(parity_checks):
            if not isinstance(check, dict):
                raise E2EScenarioError(f"{scenario_id}.parity_checks[{index}] must be an object")
            for field in ("oracle", "candidate", "metric"):
                if not isinstance(check.get(field), str) or not check[field]:
                    raise E2EScenarioError(f"{scenario_id}.parity_checks[{index}].{field} must be non-empty")
        _validate_evidence_contract(scenario_id, scenario, tags, parity_checks)
        scenario_evidence_levels[scenario_id] = scenario["evidence_level"]
        steps = scenario.get("steps")
        if not isinstance(steps, list) or not steps:
            raise E2EScenarioError(f"{scenario_id}.steps must be a non-empty list")
        if len(steps) < MIN_STEPS_PER_SCENARIO:
            raise E2EScenarioError(
                f"{scenario_id}: must declare at least {MIN_STEPS_PER_SCENARIO} executable steps"
            )
        step_ids: set[str] = set()
        produced_artifacts: set[str] = set()
        for step in steps:
            if not isinstance(step, dict):
                raise E2EScenarioError(f"{scenario_id}: each step must be an object")
            _validate_step(scenario_id, step, step_ids)
            produced_artifacts.update(step.get("produces", []))
        missing_artifacts = sorted(artifacts - produced_artifacts)
        if missing_artifacts:
            raise E2EScenarioError(
                f"{scenario_id}: scenario artifact(s) are not produced by any step: "
                + ", ".join(missing_artifacts)
            )

    _unique(scenario_ids, "scenario ids")
    missing_tags = REQUIRED_TAGS - covered_tags
    if missing_tags:
        raise E2EScenarioError(f"required coverage tags missing: {', '.join(sorted(missing_tags))}")
    missing_languages = {"python", "r", "javascript_wasm", "web"} - covered_languages
    if missing_languages:
        raise E2EScenarioError(f"required runtime languages missing: {', '.join(sorted(missing_languages))}")
    v1_refactor_contract = _validate_v1_refactor_contract(
        manifest.get("v1_refactor_contract"),
        scenario_ids,
        scenario_artifacts,
        scenario_evidence_levels,
    )
    for scenario in scenarios:
        scenario["v1_refactor_contract"] = v1_refactor_contract[scenario["id"]]
        _validate_scenario_semantics(
            scenario["id"],
            scenario,
            languages=set(scenario["languages"]),
            tags=set(scenario["tags"]),
            phases=scenario["v1_refactor_contract"],
        )
    return manifest


def _scenario_by_id(manifest: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    for scenario in manifest["scenarios"]:
        if scenario["id"] == scenario_id:
            return scenario
    raise E2EScenarioError(f"unknown scenario id: {scenario_id}")


def _step_status(step: dict[str, Any], workspace_root: Path, artifacts_dir: Path) -> tuple[str, list[str]]:
    missing: list[str] = []
    for tool in step.get("requires_tools", []):
        if not _tool_available(tool):
            missing.append(f"tool:{tool}")
    for env_name in step.get("requires_env", []):
        if not os.environ.get(env_name):
            missing.append(f"env:{env_name}")
    for raw_path in step.get("requires_paths", []):
        formatted = _format_value(raw_path, workspace_root, artifacts_dir)
        path = Path(formatted)
        if not path.is_absolute():
            path = workspace_root / path
        if not path.exists():
            missing.append(f"path:{formatted}")
    return ("blocked" if missing else "ready", missing)


def _v1_refactor_summary(phases: dict[str, dict[str, Any]]) -> dict[str, Any]:
    by_status = {status: 0 for status in ("strict", "contract", "gap")}
    phase_lists = {
        "strict_phases": [],
        "contract_phases": [],
        "gap_phases": [],
    }
    for phase in V1_REFACTOR_PHASE_ORDER:
        status = phases[phase]["status"]
        by_status[status] += 1
        phase_lists[f"{status}_phases"].append(phase)
    return {
        "total": len(V1_REFACTOR_PHASE_ORDER),
        "strict": by_status["strict"],
        "contract": by_status["contract"],
        "gap": by_status["gap"],
        "non_gap": by_status["strict"] + by_status["contract"],
        **phase_lists,
    }


def plan_scenario(
    scenario: dict[str, Any],
    *,
    workspace_root: Path,
    artifacts_dir: Path,
) -> dict[str, Any]:
    planned_steps: list[dict[str, Any]] = []
    for step in scenario["steps"]:
        status, missing = _step_status(step, workspace_root, artifacts_dir)
        planned_steps.append(
            {
                "id": step["id"],
                "title": step["title"],
                "repo": step["repo"],
                "kind": step["kind"],
                "status": status,
                "missing": missing,
                "command": _format_value(step["command"], workspace_root, artifacts_dir),
                "requires_paths": _format_value(step.get("requires_paths", []), workspace_root, artifacts_dir),
                "produces": _format_value(step.get("produces", []), workspace_root, artifacts_dir),
            }
        )
    return {
        "id": scenario["id"],
        "title": scenario["title"],
        "status": "blocked" if any(step["status"] == "blocked" for step in planned_steps) else "ready",
        "languages": scenario["languages"],
        "repos": scenario["repos"],
        "tags": scenario["tags"],
        "evidence_level": scenario["evidence_level"],
        "strictness_gaps": scenario.get("strictness_gaps", []),
        "v1_refactor_contract": scenario.get("v1_refactor_contract", {}),
        "v1_refactor_summary": _v1_refactor_summary(scenario.get("v1_refactor_contract", {})),
        "parity_checks": scenario.get("parity_checks", []),
        "steps": planned_steps,
        "evidence": scenario["evidence"],
        "artifacts": _format_value(scenario["artifacts"], workspace_root, artifacts_dir),
    }


def execute_plan(plan: dict[str, Any], *, stop_on_blocked: bool = True) -> int:
    blocked_seen = False
    if stop_on_blocked and plan["status"] == "blocked":
        blocked = [step for step in plan["steps"] if step["status"] == "blocked"]
        for step in blocked:
            print(f"BLOCKED {plan['id']}.{step['id']}: {', '.join(step['missing'])}", file=sys.stderr)
        return 2
    for step in plan["steps"]:
        if step["status"] == "blocked":
            blocked_seen = True
            print(f"SKIP-BLOCKED {plan['id']}.{step['id']}: {', '.join(step['missing'])}", file=sys.stderr)
            continue
        produced_before = _produced_snapshot(step.get("produces", []))
        proc = subprocess.run(step["command"], text=True, check=False)
        if proc.returncode != 0:
            print(f"FAILED {plan['id']}.{step['id']}: exit {proc.returncode}", file=sys.stderr)
            return proc.returncode
        artifact_failures = _validate_produced_artifacts(step, produced_before)
        if artifact_failures:
            print(
                f"FAILED {plan['id']}.{step['id']}: invalid produced artifact(s): "
                f"{'; '.join(artifact_failures)}",
                file=sys.stderr,
            )
            return 1
    if blocked_seen:
        return 2
    return 0


def execute_ready_plans(
    plans: list[dict[str, Any]],
    *,
    allow_blocked: bool = False,
    allowed_blocked_scenarios: set[str] | None = None,
    allowed_blocked_requirements: dict[str, set[str]] | None = None,
) -> int:
    ready = [plan for plan in plans if plan["status"] == "ready"]
    blocked = [plan for plan in plans if plan["status"] == "blocked"]
    if not ready:
        print("BLOCKED: no ready scenarios to execute", file=sys.stderr)
        return 2
    for plan in ready:
        print(f"RUN {plan['id']}: {plan['title']}")
        returncode = execute_plan(plan)
        if returncode != 0:
            return returncode
    if blocked:
        blocked_ids = {plan["id"] for plan in blocked}
        print(
            "BLOCKED: "
            + ", ".join(sorted(blocked_ids))
            + " still have missing requirements",
            file=sys.stderr,
        )
        for plan in blocked:
            for step in plan["steps"]:
                if step["status"] == "blocked":
                    print(f"BLOCKED {plan['id']}.{step['id']}: {', '.join(step['missing'])}", file=sys.stderr)
        if allow_blocked:
            allowed = allowed_blocked_scenarios or set()
            unexpected = blocked_ids - allowed
            allowed_requirements = allowed_blocked_requirements or {}
            unexpected_requirements: list[str] = []
            for plan in blocked:
                allowed_fragments = allowed_requirements.get(plan["id"], set())
                for step in plan["steps"]:
                    if step["status"] != "blocked":
                        continue
                    for missing in step["missing"]:
                        if not allowed_fragments or not any(
                            fragment in missing for fragment in allowed_fragments
                        ):
                            unexpected_requirements.append(f"{plan['id']}.{step['id']}: {missing}")
            if not unexpected and not unexpected_requirements:
                warning = "Allowlisted blocked E2E scenario(s): " + ", ".join(sorted(blocked_ids))
                print(f"::warning title=NIRS4ALL E2E blocked scenarios::{warning}", file=sys.stderr)
                _append_step_summary(
                    [
                        "## NIRS4ALL E2E ready execution",
                        "",
                        "Ready scenarios passed, but these allowlisted scenarios remain blocked:",
                        *[f"- `{scenario_id}`" for scenario_id in sorted(blocked_ids)],
                    ]
                )
                return 0
            if unexpected:
                print(
                    "BLOCKED: unexpected blocked scenario(s): " + ", ".join(sorted(unexpected)),
                    file=sys.stderr,
                )
            if unexpected_requirements:
                print("BLOCKED: unexpected blocked requirement(s):", file=sys.stderr)
                for requirement in unexpected_requirements:
                    print(f"  {requirement}", file=sys.stderr)
        return 2
    return 0


def _all_plans(manifest: dict[str, Any], workspace_root: Path, artifacts_dir: Path) -> list[dict[str, Any]]:
    return [
        plan_scenario(scenario, workspace_root=workspace_root, artifacts_dir=artifacts_dir)
        for scenario in manifest["scenarios"]
    ]


def coverage_report(
    manifest: dict[str, Any],
    *,
    workspace_root: Path,
    artifacts_dir: Path,
) -> dict[str, Any]:
    """Return a compact readiness and coverage summary for the E2E board."""

    plans = _all_plans(manifest, workspace_root, artifacts_dir)
    scenarios = manifest["scenarios"]
    phase_status_counts = {
        phase: {status: 0 for status in ("strict", "contract", "gap")}
        for phase in V1_REFACTOR_PHASE_ORDER
    }
    scenario_summaries: dict[str, dict[str, Any]] = {}
    tags: dict[str, int] = {}
    languages: dict[str, int] = {}
    repos: dict[str, int] = {}
    evidence_levels: dict[str, int] = {}

    for scenario in scenarios:
        scenario_id = scenario["id"]
        for tag in scenario["tags"]:
            tags[tag] = tags.get(tag, 0) + 1
        for language in scenario["languages"]:
            languages[language] = languages.get(language, 0) + 1
        for repo in scenario["repos"]:
            repos[repo] = repos.get(repo, 0) + 1
        evidence_level = scenario["evidence_level"]
        evidence_levels[evidence_level] = evidence_levels.get(evidence_level, 0) + 1

        v1_summary = _v1_refactor_summary(scenario["v1_refactor_contract"])
        for phase in V1_REFACTOR_PHASE_ORDER:
            phase_status_counts[phase][scenario["v1_refactor_contract"][phase]["status"]] += 1
        scenario_summaries[scenario_id] = {
            "evidence_level": evidence_level,
            "languages": scenario["languages"],
            "repos": scenario["repos"],
            "tags": scenario["tags"],
            "steps": len(scenario["steps"]),
            "artifacts": len(scenario["artifacts"]),
            "strict_parity_checks": sum(
                1
                for check in scenario.get("parity_checks", [])
                if check.get("evidence_level") == "strict"
            ),
            "strictness_gaps": len(scenario.get("strictness_gaps", [])),
            "v1_refactor_summary": v1_summary,
        }

    ready = [plan["id"] for plan in plans if plan["status"] == "ready"]
    blocked = [plan["id"] for plan in plans if plan["status"] == "blocked"]
    blockers = {
        plan["id"]: {
            step["id"]: step["missing"]
            for step in plan["steps"]
            if step["status"] == "blocked"
        }
        for plan in plans
        if plan["status"] == "blocked"
    }
    return {
        "schema_version": manifest["schema_version"],
        "scenario_count": len(scenarios),
        "expected_scenario_count": EXPECTED_SCENARIO_COUNT,
        "ready_count": len(ready),
        "blocked_count": len(blocked),
        "ready": ready,
        "blocked": blocked,
        "blockers": blockers,
        "evidence_levels": dict(sorted(evidence_levels.items())),
        "languages": dict(sorted(languages.items())),
        "tags": dict(sorted(tags.items())),
        "repos": dict(sorted(repos.items())),
        "required_tags": {tag: tags.get(tag, 0) for tag in sorted(REQUIRED_TAGS)},
        "required_languages": {
            language: languages.get(language, 0)
            for language in ("python", "r", "javascript_wasm", "web")
        },
        "v1_refactor_phase_status_counts": phase_status_counts,
        "scenario_summaries": scenario_summaries,
    }


def artifact_evidence_report(plans: list[dict[str, Any]]) -> dict[str, Any]:
    """Verify that expected post-run artifacts exist and contain passing evidence."""

    scenarios: dict[str, dict[str, Any]] = {}
    verified_count = 0
    failed_count = 0
    artifact_count = 0
    failure_count = 0
    for plan in plans:
        artifact_sources: dict[str, set[str]] = {}
        for raw_path in plan["artifacts"]:
            artifact_sources.setdefault(raw_path, set()).add("scenario")
        for step in plan["steps"]:
            for raw_path in step.get("produces", []):
                artifact_sources.setdefault(raw_path, set()).add(step["id"])
        failures: list[str] = []
        verified_artifacts: list[str] = []
        for raw_path in sorted(artifact_sources):
            artifact_failures = _validate_existing_artifact(raw_path)
            if artifact_failures:
                failures.extend(artifact_failures)
            else:
                verified_artifacts.append(raw_path)
        scenario_status = "failed" if failures else "verified"
        if failures:
            failed_count += 1
            failure_count += len(failures)
        else:
            verified_count += 1
        artifact_count += len(artifact_sources)
        scenarios[plan["id"]] = {
            "status": scenario_status,
            "artifact_count": len(artifact_sources),
            "verified_artifacts": verified_artifacts,
            "failures": failures,
        }
    return {
        "scenario_count": len(plans),
        "verified_count": verified_count,
        "failed_count": failed_count,
        "artifact_count": artifact_count,
        "failure_count": failure_count,
        "scenarios": scenarios,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--workspace-root", type=Path, default=default_workspace_root())
    parser.add_argument("--artifacts-dir", type=Path, default=Path(".n4a-e2e-artifacts"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="validate the scenario manifest")

    list_parser = subparsers.add_parser("list", help="list scenario ids")
    list_parser.add_argument("--json", action="store_true")

    plan_parser = subparsers.add_parser("plan", help="render execution plans without running them")
    plan_parser.add_argument("--scenario")
    plan_parser.add_argument("--json", action="store_true")

    coverage_parser = subparsers.add_parser("coverage", help="summarize scenario coverage/readiness")
    coverage_parser.add_argument("--json", action="store_true")

    evidence_parser = subparsers.add_parser("evidence", help="verify expected post-run artifacts")
    evidence_parser.add_argument("--scenario")
    evidence_parser.add_argument("--json", action="store_true")

    run_parser = subparsers.add_parser("run", help="execute one scenario")
    run_parser.add_argument("scenario")
    run_parser.add_argument("--execute", action="store_true", help="actually run commands")
    run_parser.add_argument(
        "--allow-blocked",
        action="store_true",
        help="run ready steps even when other steps are blocked; still exits 2 if any blocker remains",
    )
    run_ready_parser = subparsers.add_parser("run-ready", help="execute every currently ready scenario")
    run_ready_parser.add_argument("--execute", action="store_true", help="actually run commands")
    run_ready_parser.add_argument(
        "--allow-blocked",
        action="store_true",
        help="exit successfully after ready scenarios pass if every blocked scenario is explicitly allowlisted",
    )
    run_ready_parser.add_argument(
        "--allowed-blocked-scenario",
        action="append",
        default=[],
        metavar="SCENARIO_ID",
        help="scenario id allowed to remain blocked when --allow-blocked is set; repeatable",
    )
    run_ready_parser.add_argument(
        "--allowed-blocked-requirement",
        action="append",
        default=[],
        metavar="SCENARIO_ID=REQUIREMENT_FRAGMENT",
        help="missing requirement fragment allowed for an allowlisted blocked scenario; repeatable",
    )

    args = parser.parse_args(argv)
    workspace_root = args.workspace_root.expanduser().resolve()
    artifacts_dir = args.artifacts_dir.expanduser().resolve()

    try:
        manifest = validate_scenarios(args.manifest)
        if args.command == "validate":
            print(f"OK: {len(manifest['scenarios'])} cross-language E2E scenarios")
            return 0
        if args.command == "list":
            ids = [scenario["id"] for scenario in manifest["scenarios"]]
            print(json.dumps(ids, indent=2) if args.json else "\n".join(ids))
            return 0
        if args.command == "plan":
            scenarios = [_scenario_by_id(manifest, args.scenario)] if args.scenario else manifest["scenarios"]
            plans = [
                plan_scenario(scenario, workspace_root=workspace_root, artifacts_dir=artifacts_dir)
                for scenario in scenarios
            ]
            if args.json:
                print(json.dumps(plans, ensure_ascii=True, indent=2, sort_keys=True))
            else:
                for plan in plans:
                    print(f"{plan['id']}: {plan['status']} - {plan['title']}")
                    for step in plan["steps"]:
                        missing = f" ({', '.join(step['missing'])})" if step["missing"] else ""
                        print(f"  {step['id']}: {step['status']}{missing}")
            return 0
        if args.command == "coverage":
            report = coverage_report(
                manifest,
                workspace_root=workspace_root,
                artifacts_dir=artifacts_dir,
            )
            if args.json:
                print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
            else:
                print(
                    f"{report['scenario_count']}/{report['expected_scenario_count']} scenarios; "
                    f"ready={report['ready_count']} blocked={report['blocked_count']}"
                )
                print(
                    "required languages: "
                    + ", ".join(
                        f"{key}={value}" for key, value in report["required_languages"].items()
                    )
                )
                print(
                    "required tags: "
                    + ", ".join(
                        f"{key}={value}" for key, value in report["required_tags"].items()
                    )
                )
                for phase, counts in report["v1_refactor_phase_status_counts"].items():
                    print(
                        f"{phase}: strict={counts['strict']} "
                        f"contract={counts['contract']} gap={counts['gap']}"
                    )
            return 0
        if args.command == "evidence":
            scenarios = [_scenario_by_id(manifest, args.scenario)] if args.scenario else manifest["scenarios"]
            plans = [
                plan_scenario(scenario, workspace_root=workspace_root, artifacts_dir=artifacts_dir)
                for scenario in scenarios
            ]
            report = artifact_evidence_report(plans)
            if args.json:
                print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
            else:
                print(
                    f"{report['verified_count']}/{report['scenario_count']} scenarios verified; "
                    f"artifacts={report['artifact_count']} failures={report['failure_count']}"
                )
                for scenario_id, scenario_report in report["scenarios"].items():
                    if scenario_report["status"] == "verified":
                        print(f"{scenario_id}: verified ({scenario_report['artifact_count']} artifacts)")
                        continue
                    print(f"{scenario_id}: failed")
                    for failure in scenario_report["failures"]:
                        print(f"  {failure}")
            return 0 if report["failed_count"] == 0 else 1
        if args.command == "run":
            plan = plan_scenario(
                _scenario_by_id(manifest, args.scenario),
                workspace_root=workspace_root,
                artifacts_dir=artifacts_dir,
            )
            if not args.execute:
                print(json.dumps(plan, ensure_ascii=True, indent=2, sort_keys=True))
                print("Dry run only. Pass --execute to run commands.", file=sys.stderr)
                return 0
            return execute_plan(plan, stop_on_blocked=not args.allow_blocked)
        if args.command == "run-ready":
            plans = _all_plans(manifest, workspace_root, artifacts_dir)
            if not args.execute:
                summary = {
                    "ready": [plan["id"] for plan in plans if plan["status"] == "ready"],
                    "blocked": [plan["id"] for plan in plans if plan["status"] == "blocked"],
                    "v1_refactor_summary": {
                        plan["id"]: plan["v1_refactor_summary"] for plan in plans
                    },
                }
                print(json.dumps(summary, ensure_ascii=True, indent=2, sort_keys=True))
                print("Dry run only. Pass --execute to run ready scenarios.", file=sys.stderr)
                return 0
            return execute_ready_plans(
                plans,
                allow_blocked=args.allow_blocked,
                allowed_blocked_scenarios=set(args.allowed_blocked_scenario),
                allowed_blocked_requirements=_parse_allowed_blocked_requirements(
                    args.allowed_blocked_requirement
                ),
            )
    except E2EScenarioError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    raise AssertionError(f"unhandled command {args.command!r}")


if __name__ == "__main__":
    raise SystemExit(main())
