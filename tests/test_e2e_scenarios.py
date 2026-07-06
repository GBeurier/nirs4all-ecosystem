from __future__ import annotations

import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "contracts" / "e2e" / "cross-language-scenarios.n4a.json"
ALLOWED_PUBLIC_CHECKOUT_DATA_BLOCKERS = {
    "nirs4all-datasets/datasets/malaria_anopheles_gambiae_sporozoite_nir/canonical/dataset.json",
    "nirs4all-data/regression/GRAPEVINE_LeafTraits/PSI_spxyG70_30_byCultivar_MicroNIR_NeoSpectra",
}
ALLOWED_PUBLIC_CHECKOUT_BLOCKED_SCENARIOS = {
    "e2e-r-dataset-io-pipeline-save",
    "e2e-cluster-dag-rights-client-core",
}


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


def _assert_ready_or_only_public_checkout_data_blockers(plans: list[dict]) -> None:
    blocked = {plan["id"] for plan in plans if plan["status"] == "blocked"}
    unexpected: list[str] = []
    for plan in plans:
        for step in plan["steps"]:
            for missing in step["missing"]:
                if not missing.startswith("path:"):
                    unexpected.append(f"{plan['id']}.{step['id']}: {missing}")
                    continue
                if not any(fragment in missing for fragment in ALLOWED_PUBLIC_CHECKOUT_DATA_BLOCKERS):
                    unexpected.append(f"{plan['id']}.{step['id']}: {missing}")

    assert not unexpected
    assert blocked <= ALLOWED_PUBLIC_CHECKOUT_BLOCKED_SCENARIOS
    if not blocked:
        assert {plan["status"] for plan in plans} == {"ready"}


def test_cross_language_e2e_manifest_validates_current_contract() -> None:
    e2e = _load_e2e_module()

    manifest = e2e.validate_scenarios(MANIFEST)

    assert len(manifest["scenarios"]) == 10
    tags = {tag for scenario in manifest["scenarios"] for tag in scenario["tags"]}
    assert "multimodal" in tags
    assert "multisource" in tags
    assert "web_results" in tags
    assert set(manifest["v1_refactor_contract"]["scenario_coverage"]) == {
        scenario["id"] for scenario in manifest["scenarios"]
    }
    assert set(manifest["v1_refactor_contract"]["phase_requirements"]) == {
        "python_open_pipeline",
        "python_rerun_pipeline",
        "python_parity",
        "papers_export",
        "repository_forced_best_refit",
        "wasm_web_reuse",
    }


def test_cross_language_e2e_declares_requested_complex_workflows() -> None:
    manifest = _read_manifest()
    scenarios = {scenario["id"]: scenario for scenario in manifest["scenarios"]}

    expected = {
        "e2e-r-dataset-io-pipeline-save": {
            "languages": {"r", "python", "native"},
            "repos": {"nirs4all-core", "nirs4all-providers", "nirs4all-datasets", "nirs4all-io", "nirs4all-methods"},
            "tags": {"datasets", "io", "pipeline", "workspace_save", "parity"},
        },
        "e2e-python-reopen-paper-repository-refit": {
            "languages": {"python", "native"},
            "repos": {"nirs4all", "nirs4all-repository", "nirs4all-papers", "dag-ml"},
            "tags": {"pipeline", "repository", "papers", "workspace_save", "parity"},
        },
        "e2e-wasm-open-repo-pipeline-alt-dataset": {
            "languages": {"javascript_wasm", "web", "python"},
            "repos": {"nirs4all-web", "nirs4all-core", "nirs4all-repository", "nirs4all-datasets", "nirs4all-ui"},
            "tags": {"pipeline", "repository", "predictions", "web_results"},
        },
        "e2e-multimodal-python-r-wasm-roundtrip": {
            "languages": {"python", "r", "javascript_wasm"},
            "repos": {"nirs4all", "nirs4all-core"},
            "tags": {"multimodal", "pipeline", "parity", "predictions"},
        },
        "e2e-multisource-branching-stacking-replay": {
            "languages": {"python", "native"},
            "repos": {"nirs4all", "nirs4all-core", "dag-ml"},
            "tags": {"multisource", "pipeline", "parity", "pipeline_generation"},
        },
        "e2e-converter-legacy-save-predictions-web": {
            "languages": {"python", "web"},
            "repos": {"nirs4all-tools", "nirs4all-web"},
            "tags": {"workspace_save", "predictions", "web_results"},
        },
        "e2e-dataset-provider-repository-roundtrip": {
            "languages": {"python", "javascript_wasm"},
            "repos": {"nirs4all-core", "nirs4all-providers", "nirs4all-datasets", "nirs4all-repository"},
            "tags": {"datasets", "repository", "pipeline", "parity"},
        },
        "e2e-pipeline-generation-performance-compare": {
            "languages": {"python", "javascript_wasm", "web", "native"},
            "repos": {"nirs4all", "dag-ml", "nirs4all-core", "nirs4all-web"},
            "tags": {"pipeline_generation", "pipeline", "parity", "predictions", "web_results"},
        },
        "e2e-cluster-dag-rights-client-core": {
            "languages": {"python", "native"},
            "repos": {"nirs4all-cluster", "nirs4all-core", "dag-ml"},
            "tags": {"pipeline", "workspace_save", "parity"},
        },
        "e2e-formats-io-datasets-methods-language-bindings": {
            "languages": {"python", "r", "javascript_wasm", "rust_archive", "native"},
            "repos": {"nirs4all-formats", "nirs4all-io", "nirs4all-datasets", "nirs4all-methods", "nirs4all-core"},
            "tags": {"datasets", "io", "predictions", "parity", "pipeline"},
        },
    }

    assert set(scenarios) == set(expected)
    for scenario_id, requirements in expected.items():
        scenario = scenarios[scenario_id]
        assert requirements["languages"].issubset(set(scenario["languages"])), scenario_id
        assert requirements["repos"].issubset(set(scenario["repos"])), scenario_id
        assert requirements["tags"].issubset(set(scenario["tags"])), scenario_id
        assert len(scenario["steps"]) >= 2, scenario_id
        assert len(scenario["artifacts"]) >= 2, scenario_id
        assert any(check["evidence_level"] == "strict" for check in scenario["parity_checks"]), scenario_id
        phases = manifest["v1_refactor_contract"]["scenario_coverage"][scenario_id]
        assert any(phase["status"] == "strict" for phase in phases.values()), scenario_id


@pytest.mark.parametrize(
    ("scenario_id", "contract"),
    [
        (
            "e2e-r-dataset-io-pipeline-save",
            {
                "steps": ["r-load-reshape", "r-run-save"],
                "languages": {"r", "python", "native"},
                "tags": {"datasets", "io", "pipeline", "workspace_save", "parity"},
                "tools": {"Rscript"},
                "produces": {"dataset-card.json", "workspace.n4a.json", "roundtrip-checks.json"},
                "commands": {"e2e_dataset_io_pipeline.R", "make test-r-parity"},
                "evidence": {"Python portable oracle", "Native methods parity"},
                "phase_statuses": {"python_parity": "strict", "papers_export": "gap"},
            },
        ),
        (
            "e2e-python-reopen-paper-repository-refit",
            {
                "steps": [
                    "python-reopen-rerun",
                    "papers-export-repository-refit",
                    "web-import-repository-best-pipeline",
                ],
                "languages": {"python", "native", "javascript_wasm", "web"},
                "tags": {"pipeline", "repository", "papers", "workspace_save", "parity", "web_results"},
                "tools": {"python3.11", "node", "npm"},
                "produces": {"paper-export.zip", "repository-best-pipeline.json", "web-repository-best-pipeline.json"},
                "commands": {
                    "test_pipeline_reopen_paper_repository.py",
                    "test_repository_refit_export.py",
                    "smoke:repository-best-pipeline",
                },
                "evidence": {"force_best_refit", "Web/WASM import"},
                "phase_statuses": {
                    "python_open_pipeline": "strict",
                    "papers_export": "strict",
                    "repository_forced_best_refit": "contract",
                    "wasm_web_reuse": "contract",
                },
            },
        ),
        (
            "e2e-wasm-open-repo-pipeline-alt-dataset",
            {
                "steps": ["wasm-run-repository-pipeline", "web-render-results"],
                "languages": {"javascript_wasm", "web", "python"},
                "tags": {"datasets", "pipeline", "repository", "predictions", "web_results"},
                "tools": {"npm"},
                "produces": {"pipeline-repository-smoke.json", "predict-artifact-smoke.json", "web-results.png"},
                "commands": {"smoke:pipeline-repository", "smoke:predict-artifact"},
                "evidence": {"Python nirs4all/sklearn oracle", "fresh Web/WASM session"},
                "phase_statuses": {"python_parity": "strict", "wasm_web_reuse": "strict"},
            },
        ),
        (
            "e2e-multimodal-python-r-wasm-roundtrip",
            {
                "steps": ["python-generate-multimodal", "r-wasm-roundtrip"],
                "languages": {"python", "r", "javascript_wasm"},
                "tags": {"multimodal", "datasets", "io", "pipeline", "predictions", "workspace_save", "parity"},
                "tools": {"python3.11", "Rscript", "node"},
                "produces": {"multimodal-pipeline.n4a.json", "r-predictions.parquet", "wasm-predictions.json"},
                "commands": {"test_multimodal_roundtrip.py", "run_multimodal_roundtrip.py"},
                "evidence": {"dense-fused multimodal", "roundtrip manifest hashes"},
                "phase_statuses": {"python_parity": "strict", "wasm_web_reuse": "contract"},
            },
        ),
        (
            "e2e-multisource-branching-stacking-replay",
            {
                "steps": ["python-build-stacking", "native-replay"],
                "languages": {"python", "native", "rust"},
                "tags": {"multisource", "pipeline_generation", "pipeline", "workspace_save", "parity"},
                "tools": {"python3", "python3.11", "cargo"},
                "produces": {"stacking-replay.n4a.json", "oof-ledger.json", "native-replay.json"},
                "commands": {"test_multisource_stacking_replay.py", "run_multisource_stacking_replay.py"},
                "evidence": {"OOF", "native prediction-table schema/array coverage"},
                "phase_statuses": {"python_parity": "strict", "python_rerun_pipeline": "contract"},
            },
        ),
        (
            "e2e-converter-legacy-save-predictions-web",
            {
                "steps": ["convert-legacy-save", "web-open-predictions"],
                "languages": {"python", "javascript_wasm", "web"},
                "tags": {"workspace_save", "predictions", "web_results", "pipeline", "parity"},
                "tools": {"python3.11", "npm"},
                "produces": {"converted-workspace.n4a.json", "predictions.rt_result.json", "web-results-panels.json"},
                "commands": {"test_legacy_save_predictions_web.py", "smoke:converted-predictions"},
                "evidence": {"legacy fixture values", "Web opens converted predictions"},
                "phase_statuses": {"python_parity": "strict", "wasm_web_reuse": "strict"},
            },
        ),
        (
            "e2e-dataset-provider-repository-roundtrip",
            {
                "steps": ["provider-materialize", "core-consume-repository"],
                "languages": {"python", "javascript_wasm"},
                "tags": {"datasets", "io", "repository", "pipeline", "parity"},
                "tools": {"python3.11", "npm"},
                "produces": {"provider-resolution.json", "repository-pipeline.n4a.json", "cross-language-consumption.json"},
                "commands": {"test_dataset_provider_repository_roundtrip.py", "consume_repository_descriptor.py"},
                "evidence": {"provider materialization", "Python/WASM RMSE"},
                "phase_statuses": {"python_open_pipeline": "strict", "wasm_web_reuse": "strict"},
            },
        ),
        (
            "e2e-pipeline-generation-performance-compare",
            {
                "steps": ["generate-family", "compare-runtimes"],
                "languages": {"python", "javascript_wasm", "web", "native"},
                "tags": {"pipeline_generation", "pipeline", "parity", "predictions", "web_results"},
                "tools": {"python3.11", "node", "npm", "google-chrome"},
                "produces": {"pipeline-family.json", "python-vs-dagml.json", "web-runtime.json"},
                "commands": {"test_pipeline_generation_performance.py", "smoke:performance-compare"},
                "evidence": {"generated candidates", "performance ratio ledger"},
                "phase_statuses": {"python_rerun_pipeline": "strict", "wasm_web_reuse": "contract"},
            },
        ),
        (
            "e2e-cluster-dag-rights-client-core",
            {
                "steps": ["cluster-run-dag", "core-client-handoff"],
                "languages": {"python", "native"},
                "tags": {"pipeline", "workspace_save", "parity"},
                "tools": {"python3.11"},
                "produces": {"scheduler-run.json", "local-vs-cluster-numeric.json", "core-client-result.json"},
                "commands": {"test_cluster_dag_rights_core_client.py", "verify_cluster_handoff.py"},
                "evidence": {"N4A_CLUSTER_NUMERIC_ORACLE=1", "Local-vs-cluster"},
                "phase_statuses": {"python_rerun_pipeline": "strict", "python_parity": "strict"},
            },
        ),
        (
            "e2e-formats-io-datasets-methods-language-bindings",
            {
                "steps": ["assemble-reference-datasets", "cross-binding-methods-parity"],
                "languages": {"python", "r", "javascript_wasm", "rust_archive", "native"},
                "tags": {"datasets", "io", "predictions", "parity", "pipeline"},
                "tools": {"python3.11", "cmake", "ninja"},
                "produces": {"assembled-datasets.json", "binding-parity.json", "predictions-by-language.json"},
                "commands": {"test_formats_io_datasets_methods.py", "cross_binding_methods_parity.py"},
                "evidence": {"Native methods ABI", "WASM fixture output"},
                "phase_statuses": {"python_parity": "strict", "wasm_web_reuse": "contract"},
            },
        ),
    ],
)
def test_cross_language_e2e_orchestrates_each_complex_workflow(
    scenario_id: str,
    contract: dict,
) -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)
    scenario = _scenario_by_id(manifest, scenario_id)

    assert [step["id"] for step in scenario["steps"]] == contract["steps"]
    assert contract["languages"].issubset(set(scenario["languages"]))
    assert contract["tags"].issubset(set(scenario["tags"]))

    tools = {tool for step in scenario["steps"] for tool in step.get("requires_tools", [])}
    assert contract["tools"].issubset(tools), scenario_id

    produced = "\n".join(path for step in scenario["steps"] for path in step.get("produces", []))
    for fragment in contract["produces"]:
        assert fragment in produced, scenario_id

    commands = " ".join(part for step in scenario["steps"] for part in step["command"])
    for fragment in contract["commands"]:
        assert fragment in commands, scenario_id

    evidence_text = json.dumps(scenario, sort_keys=True)
    for fragment in contract["evidence"]:
        assert fragment in evidence_text, scenario_id

    for phase, status in contract["phase_statuses"].items():
        assert scenario["v1_refactor_contract"][phase]["status"] == status, scenario_id


def test_cross_language_e2e_current_workspace_plans_all_complex_workflows_ready(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    workspace_root = e2e.default_workspace_root()
    plans = [
        e2e.plan_scenario(scenario, workspace_root=workspace_root, artifacts_dir=tmp_path / "artifacts")
        for scenario in manifest["scenarios"]
    ]

    assert [plan["id"] for plan in plans] == [scenario["id"] for scenario in manifest["scenarios"]]
    _assert_ready_or_only_public_checkout_data_blockers(plans)
    for plan in plans:
        assert len(plan["steps"]) >= 2, plan["id"]
        summary = plan["v1_refactor_summary"]
        assert summary["total"] == len(e2e.V1_REFACTOR_PHASE_ORDER), plan["id"]
        assert summary["strict"] + summary["contract"] + summary["gap"] == summary["total"], plan["id"]
        assert summary["non_gap"] == summary["strict"] + summary["contract"], plan["id"]


def test_cross_language_e2e_plan_summarizes_v1_refactor_gaps(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)
    scenario = next(
        scenario
        for scenario in manifest["scenarios"]
        if scenario["id"] == "e2e-wasm-open-repo-pipeline-alt-dataset"
    )

    plan = e2e.plan_scenario(
        scenario,
        workspace_root=e2e.default_workspace_root(),
        artifacts_dir=tmp_path / "artifacts",
    )

    assert plan["evidence_level"] == "hybrid"
    assert plan["v1_refactor_summary"] == {
        "total": 6,
        "strict": 2,
        "contract": 1,
        "gap": 3,
        "non_gap": 3,
        "strict_phases": ["python_parity", "wasm_web_reuse"],
        "contract_phases": ["repository_forced_best_refit"],
        "gap_phases": ["python_open_pipeline", "python_rerun_pipeline", "papers_export"],
    }


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


def test_cross_language_e2e_manifest_requires_explicit_dependency_gates(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    step = manifest["scenarios"][0]["steps"][0]
    step["requires_tools"] = []
    step["requires_env"] = []
    step["requires_paths"] = []
    manifest_path = tmp_path / "no-dependency-gate.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="step must declare dependency gates"):
        e2e.validate_scenarios(manifest_path)


@pytest.mark.parametrize(
    "fragment",
    [
        "|| true",
        "set +e",
        "pytest.skip",
        "pytest.xfail",
        "@pytest.mark.skip",
        "@pytest.mark.xfail",
        "continue-on-error",
        "--allow-failure",
    ],
)
def test_cross_language_e2e_manifest_rejects_commands_that_mask_divergence(
    tmp_path: Path,
    fragment: str,
) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    manifest["scenarios"][0]["steps"][0]["command"] = ["bash", "-lc", f"python real_gate.py {fragment}"]
    manifest_path = tmp_path / "soft-success-command.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="command contains disallowed fragment"):
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


def test_cross_language_e2e_strict_check_rejects_schema_only_metric(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-multisource-branching-stacking-replay")
    scenario["parity_checks"][0]["metric"] = (
        "score deltas pass but native prediction table schema/array coverage is only audited"
    )
    manifest_path = tmp_path / "schema-only-strict.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="numeric parity, not schema/array coverage"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_requires_artifacts_to_be_produced(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    manifest["scenarios"][0]["artifacts"].append("{artifacts_dir}/never-produced.json")
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="not produced by any step"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_requires_minimum_complexity(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    manifest["scenarios"][0]["steps"] = manifest["scenarios"][0]["steps"][:1]
    manifest_path = tmp_path / "too-few-steps.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="at least 2 executable steps"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    manifest["scenarios"][0]["artifacts"] = manifest["scenarios"][0]["artifacts"][:1]
    manifest_path = tmp_path / "too-few-artifacts.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="at least 2 artifacts"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_requires_v1_refactor_phase_coverage(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario_id = manifest["scenarios"][0]["id"]
    del manifest["v1_refactor_contract"]["scenario_coverage"][scenario_id]["wasm_web_reuse"]
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="v1_refactor_contract phases mismatch"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_rejects_strict_v1_refactor_gap(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    phase = manifest["v1_refactor_contract"]["scenario_coverage"]["e2e-python-reopen-paper-repository-refit"]["python_open_pipeline"]
    phase["gap"] = "should not be allowed on strict coverage"
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="strict phases must not declare a gap"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_requires_one_strict_v1_phase_per_scenario(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario_id = manifest["scenarios"][0]["id"]
    coverage = manifest["v1_refactor_contract"]["scenario_coverage"][scenario_id]
    for phase_contract in coverage.values():
        phase_contract["status"] = "contract"
        phase_contract.pop("gap", None)
    manifest_path = tmp_path / "no-strict-v1-phase.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="at least one strict V1 refactor phase"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_strict_scenario_cannot_contain_gap_phases(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario_id = "e2e-r-dataset-io-pipeline-save"
    scenario = _scenario_by_id(manifest, scenario_id)
    scenario["evidence_level"] = "strict"
    scenario["strictness_gaps"] = []
    coverage = manifest["v1_refactor_contract"]["scenario_coverage"][scenario_id]
    for phase_contract in coverage.values():
        phase_contract["status"] = "contract"
        phase_contract.pop("gap", None)
    coverage["python_parity"]["status"] = "strict"
    coverage["python_rerun_pipeline"]["status"] = "gap"
    coverage["python_rerun_pipeline"]["gap"] = "forced gap for strict scenario regression coverage"
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="strict scenarios must not contain gap v1_refactor phases"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_rejects_unknown_v1_refactor_artifact(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    phase = manifest["v1_refactor_contract"]["scenario_coverage"]["e2e-python-reopen-paper-repository-refit"]["papers_export"]
    phase["artifacts"].append("{artifacts_dir}/python-paper-repository/not-a-scenario-artifact.json")
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="artifact\\(s\\) are not scenario artifacts"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_plan_formats_paths_and_reports_blockers(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)
    scenario = copy.deepcopy(manifest["scenarios"][0])
    scenario["steps"][0]["requires_tools"] = ["definitely-missing-n4a-e2e-tool"]

    plan = e2e.plan_scenario(
        scenario,
        workspace_root=Path("/tmp/n4a-workspace"),
        artifacts_dir=tmp_path / "artifacts",
    )

    assert plan["status"] == "blocked"
    assert "tool:definitely-missing-n4a-e2e-tool" in plan["steps"][0]["missing"]
    assert str(tmp_path / "artifacts") in plan["steps"][0]["command"][-1]


def test_cross_language_e2e_plan_reports_missing_entrypoint_paths(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)
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
    assert set(plan["v1_refactor_contract"]) == {
        "python_open_pipeline",
        "python_rerun_pipeline",
        "python_parity",
        "papers_export",
        "repository_forced_best_refit",
        "wasm_web_reuse",
    }
    assert plan["steps"]
    assert "requires_paths" in plan["steps"][0]


def test_cross_language_e2e_cli_coverage_json_exposes_readiness_and_gaps() -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"

    covered = subprocess.run(
        [sys.executable, str(script), "coverage", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    report = json.loads(covered.stdout)

    assert report["scenario_count"] == 10
    assert report["expected_scenario_count"] == 10
    assert report["evidence_levels"] == {"hybrid": 10}
    assert set(report["required_languages"]) == {"python", "r", "javascript_wasm", "web"}
    assert all(count > 0 for count in report["required_languages"].values())
    assert all(count > 0 for count in report["required_tags"].values())
    assert report["ready_count"] + report["blocked_count"] == 10
    assert set(report["v1_refactor_phase_status_counts"]) == {
        "python_open_pipeline",
        "python_rerun_pipeline",
        "python_parity",
        "papers_export",
        "repository_forced_best_refit",
        "wasm_web_reuse",
    }
    expected_phase_counts = {
        "python_open_pipeline": {"strict": 2, "contract": 2, "gap": 6},
        "python_rerun_pipeline": {"strict": 4, "contract": 3, "gap": 3},
        "python_parity": {"strict": 10, "contract": 0, "gap": 0},
        "papers_export": {"strict": 1, "contract": 0, "gap": 9},
        "repository_forced_best_refit": {"strict": 0, "contract": 2, "gap": 8},
        "wasm_web_reuse": {"strict": 3, "contract": 4, "gap": 3},
    }
    assert report["v1_refactor_phase_status_counts"] == expected_phase_counts
    scenario_ids_by_phase = report["v1_refactor_phase_scenario_ids"]
    assert scenario_ids_by_phase["repository_forced_best_refit"]["strict"] == []
    assert set(scenario_ids_by_phase["repository_forced_best_refit"]["contract"]) == {
        "e2e-python-reopen-paper-repository-refit",
        "e2e-wasm-open-repo-pipeline-alt-dataset",
    }
    assert set(scenario_ids_by_phase["papers_export"]["gap"]) == {
        scenario_id
        for scenario_id in report["scenario_summaries"]
        if scenario_id != "e2e-python-reopen-paper-repository-refit"
    }
    assert set(scenario_ids_by_phase["wasm_web_reuse"]["strict"]) == {
        "e2e-converter-legacy-save-predictions-web",
        "e2e-dataset-provider-repository-roundtrip",
        "e2e-wasm-open-repo-pipeline-alt-dataset",
    }
    for counts in expected_phase_counts.values():
        assert counts["strict"] + counts["contract"] + counts["gap"] == 10
        assert counts["strict"] + counts["contract"] >= 1
    for summary in report["scenario_summaries"].values():
        assert summary["steps"] >= 2
        assert summary["artifacts"] >= 2
        assert summary["strict_parity_checks"] >= 1
        assert summary["v1_refactor_summary"]["strict"] >= 1


def test_cross_language_e2e_semantic_tags_require_matching_runtime_steps(tmp_path: Path) -> None:
    e2e = _load_e2e_module()

    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-multimodal-python-r-wasm-roundtrip")
    scenario["languages"].append("web")
    scenario["repos"].append("nirs4all-web")
    scenario["tags"].append("web_results")
    manifest_path = tmp_path / "false-web.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="web coverage requires a nirs4all-web step"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-python-reopen-paper-repository-refit")
    scenario["repos"] = [repo for repo in scenario["repos"] if repo != "nirs4all-papers"]
    manifest_path = tmp_path / "papers-without-repo.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="papers tag requires nirs4all-papers repo"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-dataset-provider-repository-roundtrip")
    for step in scenario["steps"]:
        step["produces"] = [path.replace("repository", "repo") for path in step.get("produces", [])]
    scenario["artifacts"] = [path.replace("repository", "repo") for path in scenario["artifacts"]]
    for phase in manifest["v1_refactor_contract"]["scenario_coverage"][scenario["id"]].values():
        phase["artifacts"] = [path.replace("repository", "repo") for path in phase.get("artifacts", [])]
    manifest_path = tmp_path / "repository-without-artifact.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="repository tag requires a repository artifact"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_declares_known_semantic_gaps() -> None:
    manifest = _read_manifest()
    flow = manifest["v1_refactor_contract"]["scenario_coverage"]

    repository_refit = _scenario_by_id(manifest, "e2e-python-reopen-paper-repository-refit")
    assert repository_refit["evidence_level"] == "hybrid"
    assert any("does not execute a repository best-pipeline refit yet" in gap for gap in repository_refit["strictness_gaps"])
    assert any("refit.executed=true" in check["metric"] for check in repository_refit["parity_checks"])
    repository_flow = flow["e2e-python-reopen-paper-repository-refit"]
    assert repository_flow["python_open_pipeline"]["status"] == "strict"
    assert repository_flow["papers_export"]["status"] == "strict"
    assert repository_flow["repository_forced_best_refit"]["status"] == "contract"
    assert "force_best_refit=true" in repository_flow["repository_forced_best_refit"]["acceptance"][0]
    assert repository_flow["wasm_web_reuse"]["status"] == "contract"
    assert "alternative uploadable dataset" in repository_flow["wasm_web_reuse"]["gap"]

    wasm_alt_dataset = _scenario_by_id(manifest, "e2e-wasm-open-repo-pipeline-alt-dataset")
    assert wasm_alt_dataset["evidence_level"] == "hybrid"
    assert any("non-demo uploaded fixture dataset" in gap for gap in wasm_alt_dataset["strictness_gaps"])
    assert any("external provider/catalog dataset" in gap for gap in wasm_alt_dataset["strictness_gaps"])
    wasm_flow = flow["e2e-wasm-open-repo-pipeline-alt-dataset"]
    assert wasm_flow["python_parity"]["status"] == "strict"
    assert wasm_flow["wasm_web_reuse"]["status"] == "strict"

    multimodal = _scenario_by_id(manifest, "e2e-multimodal-python-r-wasm-roundtrip")
    assert multimodal["evidence_level"] == "hybrid"
    assert any("dense fused-matrix multimodal proxy" in gap for gap in multimodal["strictness_gaps"])
    assert any("proxy representation" in check["metric"] for check in multimodal["parity_checks"])
    assert flow["e2e-multimodal-python-r-wasm-roundtrip"]["wasm_web_reuse"]["status"] == "contract"

    multisource = _scenario_by_id(manifest, "e2e-multisource-branching-stacking-replay")
    assert multisource["evidence_level"] == "hybrid"
    assert any("schema/array coverage" in gap for gap in multisource["strictness_gaps"])
    assert flow["e2e-multisource-branching-stacking-replay"]["repository_forced_best_refit"]["status"] == "gap"
    assert "not contractualized" in flow["e2e-multisource-branching-stacking-replay"]["repository_forced_best_refit"]["gap"]

    dataset_roundtrip = _scenario_by_id(manifest, "e2e-dataset-provider-repository-roundtrip")
    assert dataset_roundtrip["evidence_level"] == "hybrid"
    assert any("does not execute R" in gap for gap in dataset_roundtrip["strictness_gaps"])
    assert flow["e2e-dataset-provider-repository-roundtrip"]["wasm_web_reuse"]["status"] == "strict"
    assert flow["e2e-dataset-provider-repository-roundtrip"]["repository_forced_best_refit"]["status"] == "gap"

    formats_bindings = _scenario_by_id(manifest, "e2e-formats-io-datasets-methods-language-bindings")
    assert formats_bindings["evidence_level"] == "hybrid"
    assert any("WASM remains fixture-scoped" in gap for gap in formats_bindings["strictness_gaps"])
    assert flow["e2e-formats-io-datasets-methods-language-bindings"]["wasm_web_reuse"]["status"] == "contract"

    cluster = _scenario_by_id(manifest, "e2e-cluster-dag-rights-client-core")
    assert cluster["evidence_level"] == "hybrid"
    assert any("public checkout remains data-blocked" in gap for gap in cluster["strictness_gaps"])
    assert flow["e2e-cluster-dag-rights-client-core"]["python_parity"]["status"] == "strict"
    assert flow["e2e-cluster-dag-rights-client-core"]["wasm_web_reuse"]["status"] == "gap"


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
    assert plan["v1_refactor_contract"]["python_parity"]["status"] == "strict"
    assert plan["v1_refactor_contract"]["wasm_web_reuse"]["status"] == "strict"


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


def test_cross_language_e2e_runtime_artifacts_are_gitignored() -> None:
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", ".n4a-e2e-artifacts/probe.json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert ignored.returncode == 0


def test_cross_language_e2e_required_paths_stay_in_declared_repos_or_allowlisted_data_blockers() -> None:
    manifest = _read_manifest()

    for scenario in manifest["scenarios"]:
        declared_repos = set(scenario["repos"])
        for step in scenario["steps"]:
            for raw_path in step.get("requires_paths", []):
                prefix = "{workspace_root}/"
                if not raw_path.startswith(prefix):
                    continue
                relative = raw_path[len(prefix) :]
                top_level = relative.split("/", 1)[0]
                if top_level in declared_repos:
                    continue
                assert scenario["id"] in ALLOWED_PUBLIC_CHECKOUT_BLOCKED_SCENARIOS, (
                    f"{scenario['id']}.{step['id']} requires {raw_path}, but {top_level!r} "
                    "is not a declared repo and the scenario is not explicitly allowed as data-blocked"
                )
                assert any(fragment in relative for fragment in ALLOWED_PUBLIC_CHECKOUT_DATA_BLOCKERS), (
                    f"{scenario['id']}.{step['id']} requires undeclared workspace path {raw_path!r} "
                    "without a public-checkout data blocker allowlist entry"
                )


def test_cross_language_e2e_python311_steps_use_python311_command() -> None:
    manifest = _read_manifest()

    for scenario in manifest["scenarios"]:
        for step in scenario["steps"]:
            if "python3.11" in step.get("requires_tools", []):
                assert any("python3.11" in part for part in step["command"]), f"{scenario['id']}.{step['id']}"


def test_cross_language_e2e_workflow_checks_out_declared_repos() -> None:
    workflow = (ROOT / ".github" / "workflows" / "cross-language-e2e.yml").read_text(encoding="utf-8")
    gitmodules = (ROOT / ".gitmodules").read_text(encoding="utf-8")
    manifest = _read_manifest()
    declared_repos = {repo for scenario in manifest["scenarios"] for repo in scenario["repos"]}

    assert "N4A_WORKSPACE_ROOT: ${{ github.workspace }}/nirs4all-ecosystem" in workflow
    assert "allow_blocked:" in workflow
    assert "run-ready --execute" in workflow
    assert "--allow-blocked" in workflow
    assert set(re.findall(r"--allowed-blocked-scenario ([a-z0-9-]+)", workflow)) == (
        ALLOWED_PUBLIC_CHECKOUT_BLOCKED_SCENARIOS
    )
    assert workflow.count("--allowed-blocked-scenario ") == len(ALLOWED_PUBLIC_CHECKOUT_BLOCKED_SCENARIOS)
    expected_blocked_requirements = {
        "e2e-r-dataset-io-pipeline-save="
        "nirs4all-datasets/datasets/malaria_anopheles_gambiae_sporozoite_nir/canonical/dataset.json",
        "e2e-cluster-dag-rights-client-core="
        "nirs4all-data/regression/GRAPEVINE_LeafTraits/PSI_spxyG70_30_byCultivar_MicroNIR_NeoSpectra",
    }
    assert set(re.findall(r"--allowed-blocked-requirement ([^\s]+)", workflow)) == (
        expected_blocked_requirements
    )
    assert workflow.count("--allowed-blocked-requirement ") == len(expected_blocked_requirements)
    assert "N4A_E2E_SCENARIO: ${{ github.event.inputs.scenario }}" in workflow
    assert "N4A_ALLOW_BLOCKED: ${{ github.event.inputs.allow_blocked }}" in workflow
    assert '[[ "$N4A_ALLOW_BLOCKED" == "true" ]]' in workflow
    assert 'plan --scenario "$N4A_E2E_SCENARIO"' in workflow
    assert 'args=(run "$N4A_E2E_SCENARIO" --execute)' in workflow
    assert 'args=(run "${{ github.event.inputs.scenario }}" --execute)' not in workflow
    assert '[[ "${{ github.event.inputs.allow_blocked }}" == "true" ]]' not in workflow
    assert "path: nirs4all-ecosystem" in workflow
    assert "submodules: recursive" in workflow
    assert "nirs4all-drafts" not in workflow
    assert "nirs4all-lab" not in workflow
    for repo in sorted(declared_repos):
        assert f'path = {repo}' in gitmodules
        assert f"url = https://github.com/GBeurier/{repo}.git" in gitmodules


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


def test_cross_language_e2e_run_ready_can_allow_declared_blockers(
    tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "ready-result.json"
    ready_plan = {
        "id": "ready-scenario",
        "title": "Ready scenario",
        "status": "ready",
        "steps": [
            {
                "id": "ready-step",
                "status": "ready",
                "missing": [],
                "command": [
                    sys.executable,
                    "-c",
                    f"from pathlib import Path; Path({str(artifact)!r}).write_text('{{\"status\":\"passed\"}}\\n')",
                ],
                "produces": [str(artifact)],
            }
        ],
    }
    blocked_plan = {
        "id": "blocked-scenario",
        "title": "Blocked scenario",
        "status": "blocked",
        "steps": [
            {
                "id": "blocked-step",
                "status": "blocked",
                "missing": ["path:/missing/public-dataset"],
                "command": [sys.executable, "-c", "raise SystemExit(99)"],
                "produces": [],
            }
        ],
    }

    assert e2e.execute_ready_plans([ready_plan, blocked_plan]) == 2
    artifact.unlink()
    assert e2e.execute_ready_plans([ready_plan, blocked_plan], allow_blocked=True) == 2
    artifact.unlink()
    assert (
        e2e.execute_ready_plans(
            [ready_plan, blocked_plan],
            allow_blocked=True,
            allowed_blocked_scenarios={"blocked-scenario"},
        )
        == 2
    )
    artifact.unlink()
    summary = tmp_path / "step-summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    assert (
        e2e.execute_ready_plans(
            [ready_plan, blocked_plan],
            allow_blocked=True,
            allowed_blocked_scenarios={"blocked-scenario"},
            allowed_blocked_requirements={"blocked-scenario": {"other-dataset"}},
        )
        == 2
    )
    artifact.unlink()
    assert (
        e2e.execute_ready_plans(
            [ready_plan, blocked_plan],
            allow_blocked=True,
            allowed_blocked_scenarios={"blocked-scenario"},
            allowed_blocked_requirements={"blocked-scenario": {"public-dataset"}},
        )
        == 0
    )
    captured = capsys.readouterr()
    assert "BLOCKED: blocked-scenario still have missing requirements" in captured.err
    assert "BLOCKED blocked-scenario.blocked-step: path:/missing/public-dataset" in captured.err
    assert "unexpected blocked scenario(s): blocked-scenario" in captured.err
    assert "unexpected blocked requirement(s):" in captured.err
    assert "::warning title=NIRS4ALL E2E blocked scenarios::" in captured.err
    assert "Ready scenarios passed" in summary.read_text(encoding="utf-8")
    assert "- `blocked-scenario`" in summary.read_text(encoding="utf-8")


def test_cross_language_e2e_run_ready_requires_complete_blocker_allowlist(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "ready-result.json"
    ready_plan = {
        "id": "ready-scenario",
        "title": "Ready scenario",
        "status": "ready",
        "steps": [
            {
                "id": "ready-step",
                "status": "ready",
                "missing": [],
                "command": [
                    sys.executable,
                    "-c",
                    f"from pathlib import Path; Path({str(artifact)!r}).write_text('{{}}\\n')",
                ],
                "produces": [str(artifact)],
            }
        ],
    }
    blocked_a = {
        "id": "blocked-a",
        "title": "Blocked A",
        "status": "blocked",
        "steps": [
            {
                "id": "blocked-step",
                "status": "blocked",
                "missing": ["path:/missing/public-dataset-a"],
                "command": [sys.executable, "-c", "raise SystemExit(99)"],
                "produces": [],
            }
        ],
    }
    blocked_b = {
        "id": "blocked-b",
        "title": "Blocked B",
        "status": "blocked",
        "steps": [
            {
                "id": "blocked-step",
                "status": "blocked",
                "missing": ["path:/missing/public-dataset-b"],
                "command": [sys.executable, "-c", "raise SystemExit(99)"],
                "produces": [],
            }
        ],
    }

    assert (
        e2e.execute_ready_plans(
            [ready_plan, blocked_a, blocked_b],
            allow_blocked=True,
            allowed_blocked_scenarios={"blocked-a"},
            allowed_blocked_requirements={"blocked-a": {"public-dataset-a"}},
        )
        == 2
    )


def test_cross_language_e2e_run_ready_allowlist_does_not_mask_ready_failure(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "never-written.json"
    failing_ready_plan = {
        "id": "ready-scenario",
        "title": "Ready scenario",
        "status": "ready",
        "steps": [
            {
                "id": "failing-step",
                "status": "ready",
                "missing": [],
                "command": [sys.executable, "-c", "raise SystemExit(7)"],
                "produces": [str(artifact)],
            }
        ],
    }
    blocked_plan = {
        "id": "blocked-scenario",
        "title": "Blocked scenario",
        "status": "blocked",
        "steps": [
            {
                "id": "blocked-step",
                "status": "blocked",
                "missing": ["path:/missing/public-dataset"],
                "command": [sys.executable, "-c", "raise SystemExit(99)"],
                "produces": [],
            }
        ],
    }

    assert (
        e2e.execute_ready_plans(
            [failing_ready_plan, blocked_plan],
            allow_blocked=True,
            allowed_blocked_scenarios={"blocked-scenario"},
            allowed_blocked_requirements={"blocked-scenario": {"public-dataset"}},
        )
        == 7
    )


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


def test_cross_language_e2e_artifact_evidence_report_verifies_existing_artifacts(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    json_artifact = tmp_path / "passing-result.json"
    png_artifact = tmp_path / "web-results.png"
    json_artifact.write_text('{"status": "passed", "ok": true}\n', encoding="utf-8")
    png_artifact.write_bytes(b"\x89PNG\r\n\x1a\n")

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "synthetic",
                "artifacts": [str(json_artifact), str(png_artifact)],
                "steps": [
                    {
                        "id": "write-evidence",
                        "produces": [str(json_artifact), str(png_artifact)],
                    }
                ],
            }
        ]
    )

    assert report["verified_count"] == 1
    assert report["failed_count"] == 0
    assert report["artifact_count"] == 2
    assert report["scenarios"]["synthetic"]["status"] == "verified"


def test_cross_language_e2e_artifact_evidence_report_rejects_missing_and_nonpassing(
    tmp_path: Path,
) -> None:
    e2e = _load_e2e_module()
    missing_artifact = tmp_path / "missing-result.json"
    nonpassing_artifact = tmp_path / "nonpassing-result.json"
    nonpassing_artifact.write_text('{"status": "skipped"}\n', encoding="utf-8")

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "synthetic",
                "artifacts": [str(missing_artifact), str(nonpassing_artifact)],
                "steps": [
                    {
                        "id": "write-evidence",
                        "produces": [str(nonpassing_artifact)],
                    }
                ],
            }
        ]
    )

    assert report["verified_count"] == 0
    assert report["failed_count"] == 1
    assert report["failure_count"] == 2
    failures = "\n".join(report["scenarios"]["synthetic"]["failures"])
    assert "missing" in failures
    assert "non-passing evidence" in failures


def test_cross_language_e2e_cli_evidence_json_selected_scenario(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)
    scenario = _scenario_by_id(manifest, "e2e-r-dataset-io-pipeline-save")
    artifacts_dir = tmp_path / "artifacts"

    for raw_path in scenario["artifacts"]:
        path = Path(raw_path.format(workspace_root=tmp_path, artifacts_dir=artifacts_dir))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"status": "passed", "ok": true}\n', encoding="utf-8")

    verified = subprocess.run(
        [
            sys.executable,
            str(script),
            "--workspace-root",
            str(tmp_path),
            "--artifacts-dir",
            str(artifacts_dir),
            "evidence",
            "--scenario",
            scenario["id"],
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    report = json.loads(verified.stdout)

    assert report["verified_count"] == 1
    assert report["failed_count"] == 0
    assert report["scenarios"][scenario["id"]]["artifact_count"] == len(scenario["artifacts"])

    missing = subprocess.run(
        [
            sys.executable,
            str(script),
            "--workspace-root",
            str(tmp_path),
            "--artifacts-dir",
            str(tmp_path / "missing-artifacts"),
            "evidence",
            "--scenario",
            scenario["id"],
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert missing.returncode == 1
    assert "failed" in missing.stdout
    assert "missing" in missing.stdout


def test_cross_language_e2e_cli_fails_when_declared_artifact_is_missing(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    manifest = _read_manifest()
    scenario_id = manifest["scenarios"][0]["id"]
    ok_artifact = tmp_path / "ok-cli-result.json"
    missing_artifact = tmp_path / "missing-cli-result.json"
    manifest["scenarios"][0]["artifacts"] = [str(ok_artifact), str(missing_artifact)]
    for phase in manifest["v1_refactor_contract"]["scenario_coverage"][scenario_id].values():
        phase["artifacts"] = []
    manifest["scenarios"][0]["steps"] = [
        {
            "id": "write-cli-step",
            "title": "Command writes one declared artifact",
            "kind": "verify",
            "repo": "nirs4all-ecosystem",
            "requires_tools": [sys.executable],
            "requires_paths": [],
            "command": [
                sys.executable,
                "-c",
                f"from pathlib import Path; Path({str(ok_artifact)!r}).write_text('{{{{\"status\":\"passed\"}}}}\\n')",
            ],
            "produces": [str(ok_artifact)],
        },
        {
            "id": "forgetful-cli-step",
            "title": "Command exits zero but omits its artifact",
            "kind": "verify",
            "repo": "nirs4all-ecosystem",
            "requires_tools": [sys.executable],
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


def test_cross_language_e2e_evidence_can_require_fresh_artifacts(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "archived-result.json"
    artifact.write_text('{"status":"passed"}\n', encoding="utf-8")
    os.utime(artifact, (1, 1))
    plan = {
        "id": "archived-scenario",
        "artifacts": [str(artifact)],
        "steps": [{"id": "write-artifact", "produces": [str(artifact)]}],
    }

    archived_report = e2e.artifact_evidence_report([plan])
    fresh_report = e2e.artifact_evidence_report([plan], max_age_seconds=60)

    assert archived_report["verified_count"] == 1
    assert archived_report["failed_count"] == 0
    assert fresh_report["verified_count"] == 0
    assert fresh_report["failed_count"] == 1
    assert "stale artifact age=" in fresh_report["scenarios"]["archived-scenario"]["failures"][0]


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
    assert summary["v1_refactor_summary"]["e2e-wasm-open-repo-pipeline-alt-dataset"]["gap"] == 3
    assert (
        summary["v1_refactor_summary"]["e2e-python-reopen-paper-repository-refit"]["strict"]
        == 4
    )
    assert "Dry run only" in planned.stderr
