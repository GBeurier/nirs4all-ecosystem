from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "contracts" / "e2e" / "cross-language-scenarios.n4a.json"


def _load_e2e_module():
    path = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    spec = importlib.util.spec_from_file_location("n4a_e2e_scenarios", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_cross_language_e2e_manifest_validates_current_contract() -> None:
    e2e = _load_e2e_module()

    manifest = e2e.validate_scenarios(MANIFEST)

    assert len(manifest["scenarios"]) == 10
    tags = {tag for scenario in manifest["scenarios"] for tag in scenario["tags"]}
    assert "multimodal" in tags
    assert "multisource" in tags
    assert "web_results" in tags


def test_cross_language_e2e_manifest_requires_exact_scenario_count(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    manifest["scenarios"] = manifest["scenarios"][:-1]
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="expected exactly 10 scenarios"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_rejects_missing_required_coverage(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    for scenario in manifest["scenarios"]:
        scenario["tags"] = [tag for tag in scenario["tags"] if tag != "web_results"]
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="required coverage tags missing: web_results"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_rejects_duplicate_step_ids(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = manifest["scenarios"][0]
    duplicate = copy.deepcopy(scenario["steps"][0])
    scenario["steps"].append(duplicate)
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="duplicate step id"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_requires_artifacts_to_be_produced(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    manifest["scenarios"][0]["artifacts"].append("{artifacts_dir}/never-produced.json")
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="not produced by any step"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_plan_formats_paths_and_reports_blockers(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = copy.deepcopy(manifest["scenarios"][0])
    scenario["steps"][0]["requires_tools"] = ["definitely-missing-n4a-e2e-tool"]
    validated = {"scenarios": [scenario]}

    plan = e2e.plan_scenario(
        validated["scenarios"][0],
        workspace_root=Path("/tmp/n4a-workspace"),
        artifacts_dir=tmp_path / "artifacts",
    )

    assert plan["status"] == "blocked"
    assert "tool:definitely-missing-n4a-e2e-tool" in plan["steps"][0]["missing"]
    assert str(tmp_path / "artifacts") in plan["steps"][0]["command"][-1]


def test_cross_language_e2e_plan_reports_missing_entrypoint_paths(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = copy.deepcopy(manifest["scenarios"][0])
    scenario["steps"][0]["requires_tools"] = []
    scenario["steps"][0]["requires_paths"] = ["{workspace_root}/missing/e2e-entrypoint.py"]

    plan = e2e.plan_scenario(
        scenario,
        workspace_root=Path("/tmp/n4a-workspace"),
        artifacts_dir=tmp_path / "artifacts",
    )

    assert plan["status"] == "blocked"
    assert "path:/tmp/n4a-workspace/missing/e2e-entrypoint.py" in plan["steps"][0]["missing"]


def test_cross_language_e2e_cli_list_and_plan_json() -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"

    listed = subprocess.run(
        [sys.executable, str(script), "list", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    scenario_ids = json.loads(listed.stdout)
    assert len(scenario_ids) == 10
    assert "e2e-wasm-open-repo-pipeline-parity-alt-dataset" in scenario_ids

    planned = subprocess.run(
        [sys.executable, str(script), "plan", "--scenario", scenario_ids[0], "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    plan = json.loads(planned.stdout)[0]
    assert plan["id"] == scenario_ids[0]
    assert plan["steps"]
    assert "requires_paths" in plan["steps"][0]


def test_cross_language_e2e_manifest_is_not_gitignored() -> None:
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", str(MANIFEST.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert ignored.returncode == 1


def test_cross_language_e2e_allow_blocked_never_returns_green(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    manifest = _read_manifest()
    scenario_id = manifest["scenarios"][0]["id"]
    for step in manifest["scenarios"][0]["steps"]:
        step["requires_tools"] = ["definitely-missing-n4a-e2e-tool"]
        step["requires_paths"] = []
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    executed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--manifest",
            str(manifest_path),
            "run",
            scenario_id,
            "--execute",
            "--allow-blocked",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert executed.returncode == 2
    assert f"SKIP-BLOCKED {scenario_id}" in executed.stderr


def test_cross_language_e2e_successful_step_must_produce_declared_artifacts(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    missing_artifact = tmp_path / "missing-result.json"

    returncode = e2e.execute_plan(
        {
            "id": "synthetic",
            "status": "ready",
            "steps": [
                {
                    "id": "forgetful-step",
                    "status": "ready",
                    "missing": [],
                    "command": [sys.executable, "-c", "pass"],
                    "produces": [str(missing_artifact)],
                }
            ],
        }
    )

    assert returncode == 1
    assert not missing_artifact.exists()


def test_cross_language_e2e_cli_fails_when_declared_artifact_is_missing(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    manifest = _read_manifest()
    scenario_id = manifest["scenarios"][0]["id"]
    missing_artifact = tmp_path / "missing-cli-result.json"
    manifest["scenarios"][0]["artifacts"] = [str(missing_artifact)]
    manifest["scenarios"][0]["steps"] = [
        {
            "id": "forgetful-cli-step",
            "title": "Command exits zero but omits its artifact",
            "kind": "verify",
            "repo": "nirs4all-ecosystem",
            "requires_tools": [],
            "requires_paths": [],
            "command": [sys.executable, "-c", "pass"],
            "produces": [str(missing_artifact)],
        }
    ]
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    executed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--manifest",
            str(manifest_path),
            "run",
            scenario_id,
            "--execute",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert executed.returncode == 1
    assert "missing produced artifact(s)" in executed.stderr
    assert str(missing_artifact) in executed.stderr
