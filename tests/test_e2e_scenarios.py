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


def _scenario_by_id(manifest: dict, scenario_id: str) -> dict:
    for scenario in manifest["scenarios"]:
        if scenario["id"] == scenario_id:
            return scenario
    raise AssertionError(f"missing scenario: {scenario_id}")


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


def test_cross_language_e2e_manifest_requires_evidence_levels(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    del manifest["scenarios"][0]["evidence_level"]
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="evidence_level must be one of"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_contract_smoke_cannot_claim_parity_tag(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = manifest["scenarios"][0]
    scenario["evidence_level"] = "contract_smoke"
    scenario["strictness_gaps"] = ["numeric oracle pending"]
    scenario["tags"] = sorted(set(scenario["tags"]) | {"parity"})
    for check in scenario["parity_checks"]:
        check["evidence_level"] = "contract"
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="contract_smoke scenarios must not use the parity tag"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_hybrid_scenarios_declare_strictness_gaps(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = manifest["scenarios"][0]
    scenario["evidence_level"] = "hybrid"
    scenario["strictness_gaps"] = []
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="hybrid scenarios must declare strictness_gaps"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_parity_tag_requires_strict_check(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = manifest["scenarios"][0]
    scenario["tags"] = sorted(set(scenario["tags"]) | {"parity"})
    for check in scenario["parity_checks"]:
        check["evidence_level"] = "contract"
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="parity tag requires at least one strict parity_check"):
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
    assert "e2e-wasm-open-repo-pipeline-alt-dataset" in scenario_ids

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
    assert plan["evidence_level"] in {"contract_smoke", "hybrid", "strict"}
    assert "parity_checks" in plan
    assert "strictness_gaps" in plan
    assert plan["steps"]
    assert "requires_paths" in plan["steps"][0]


def test_cross_language_e2e_manifest_declares_known_semantic_gaps() -> None:
    manifest = _read_manifest()

    repository_refit = _scenario_by_id(manifest, "e2e-python-reopen-paper-repository-refit")
    assert repository_refit["evidence_level"] == "hybrid"
    assert any("does not execute a repository best-pipeline refit yet" in gap for gap in repository_refit["strictness_gaps"])
    assert any("executed=false" in check["metric"] for check in repository_refit["parity_checks"])

    wasm_alt_dataset = _scenario_by_id(manifest, "e2e-wasm-open-repo-pipeline-alt-dataset")
    assert wasm_alt_dataset["evidence_level"] == "hybrid"
    assert any("no Python-vs-WASM numeric oracle" in gap for gap in wasm_alt_dataset["strictness_gaps"])
    assert any("alternative catalog dataset" in gap for gap in wasm_alt_dataset["strictness_gaps"])

    multimodal = _scenario_by_id(manifest, "e2e-multimodal-python-r-wasm-roundtrip")
    assert multimodal["evidence_level"] == "hybrid"
    assert any("dense fused-matrix multimodal proxy" in gap for gap in multimodal["strictness_gaps"])
    assert any("proxy representation" in check["metric"] for check in multimodal["parity_checks"])


def test_cross_language_e2e_plan_exposes_hybrid_web_gaps_and_strict_checks() -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"

    planned = subprocess.run(
        [
            sys.executable,
            str(script),
            "plan",
            "--scenario",
            "e2e-wasm-open-repo-pipeline-alt-dataset",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    plan = json.loads(planned.stdout)[0]

    assert plan["evidence_level"] == "hybrid"
    assert plan["strictness_gaps"]
    assert "parity" not in plan["tags"]
    assert [check["evidence_level"] for check in plan["parity_checks"]].count("strict") >= 2


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


def test_cross_language_e2e_python311_steps_use_python311_command() -> None:
    manifest = _read_manifest()

    for scenario in manifest["scenarios"]:
        for step in scenario["steps"]:
            if "python3.11" in step.get("requires_tools", []):
                assert any("python3.11" in part for part in step["command"]), f"{scenario['id']}.{step['id']}"


def test_cross_language_e2e_workflow_checks_out_declared_repos() -> None:
    workflow = (ROOT / ".github" / "workflows" / "cross-language-e2e.yml").read_text(encoding="utf-8")
    manifest = _read_manifest()
    declared_repos = {repo for scenario in manifest["scenarios"] for repo in scenario["repos"]}

    assert "N4A_WORKSPACE_ROOT: ${{ github.workspace }}" in workflow
    assert "path: nirs4all-ecosystem" in workflow
    assert "nirs4all-drafts" not in workflow
    assert "nirs4all-lab" not in workflow
    for repo in sorted(declared_repos):
        assert f"repository: GBeurier/{repo}" in workflow
        assert f"path: {repo}" in workflow


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


def test_cross_language_e2e_successful_step_must_refresh_existing_artifacts(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    stale_artifact = tmp_path / "stale-result.json"
    stale_artifact.write_text('{"status": "passed"}\n', encoding="utf-8")

    returncode = e2e.execute_plan(
        {
            "id": "synthetic",
            "status": "ready",
            "steps": [
                {
                    "id": "stale-step",
                    "status": "ready",
                    "missing": [],
                    "command": [sys.executable, "-c", "pass"],
                    "produces": [str(stale_artifact)],
                }
            ],
        }
    )

    assert returncode == 1


@pytest.mark.parametrize(
    "payload",
    [
        {"parity": {"status": "not_run"}},
        {"numeric_oracle": {"status": "not_requested"}},
        {"web_runtime": {"status": "passed_web_with_studio_hold"}},
        {"studio_runtime": {"status": "not_executed_prod_hold"}},
        {"repository_runtime": {"result": "not_executed_in_this_gate"}},
        {"legacy_python_replay": False},
    ],
)
def test_cross_language_e2e_rejects_non_passing_json_artifacts(tmp_path: Path, payload: dict) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "non-passing-result.json"

    returncode = e2e.execute_plan(
        {
            "id": "synthetic",
            "status": "ready",
            "steps": [
                {
                    "id": "non-passing-step",
                    "status": "ready",
                    "missing": [],
                    "command": [
                        sys.executable,
                        "-c",
                        (
                            "import json, pathlib; "
                            f"pathlib.Path({str(artifact)!r}).write_text(json.dumps({payload!r}), encoding='utf-8')"
                        ),
                    ],
                    "produces": [str(artifact)],
                }
            ],
        }
    )

    assert returncode == 1


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
    assert "invalid produced artifact(s)" in executed.stderr
    assert "missing" in executed.stderr
    assert str(missing_artifact) in executed.stderr


def test_cross_language_e2e_run_ready_executes_ready_but_reports_blocked(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    produced = tmp_path / "ready-result.json"

    returncode = e2e.execute_ready_plans(
        [
            {
                "id": "ready-scenario",
                "title": "Ready synthetic scenario",
                "status": "ready",
                "steps": [
                    {
                        "id": "write-artifact",
                        "status": "ready",
                        "missing": [],
                        "command": [
                            sys.executable,
                            "-c",
                            f"from pathlib import Path; Path({str(produced)!r}).write_text('{{\"status\":\"passed\"}}')",
                        ],
                        "produces": [str(produced)],
                    }
                ],
            },
            {
                "id": "blocked-scenario",
                "title": "Blocked synthetic scenario",
                "status": "blocked",
                "steps": [
                    {
                        "id": "missing-tool",
                        "status": "blocked",
                        "missing": ["tool:definitely-missing"],
                        "command": [sys.executable, "-c", "raise SystemExit(99)"],
                        "produces": [],
                    }
                ],
            },
        ]
    )

    assert json.loads(produced.read_text(encoding="utf-8")) == {"status": "passed"}
    assert returncode == 2


def test_cross_language_e2e_cli_run_ready_dry_run_lists_ready_and_blocked(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    manifest = _read_manifest()
    workspace_root = tmp_path / "workspace"
    artifacts_dir = tmp_path / "artifacts"
    workspace_root.mkdir()
    artifacts_dir.mkdir()
    for scenario in manifest["scenarios"]:
        for step in scenario["steps"]:
            step["requires_tools"] = []
            step["requires_env"] = []
            for raw_path in step.get("requires_paths", []):
                path = Path(raw_path.format(workspace_root=workspace_root, artifacts_dir=artifacts_dir))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("e2e entrypoint placeholder\n", encoding="utf-8")
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    planned = subprocess.run(
        [
            sys.executable,
            str(script),
            "--manifest",
            str(manifest_path),
            "--workspace-root",
            str(workspace_root),
            "--artifacts-dir",
            str(artifacts_dir),
            "run-ready",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    summary = json.loads(planned.stdout)

    assert "e2e-r-dataset-io-pipeline-save" in summary["ready"]
    assert "e2e-python-reopen-paper-repository-refit" in summary["ready"]
    assert "e2e-multimodal-python-r-wasm-roundtrip" in summary["ready"]
    assert "e2e-multisource-branching-stacking-replay" in summary["ready"]
    assert summary["blocked"] == []
    assert "Dry run only" in planned.stderr
