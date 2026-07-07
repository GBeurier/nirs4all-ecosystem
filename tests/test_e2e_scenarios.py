from __future__ import annotations

import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
import zipfile
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
LANGUAGE_EVIDENCE_FRAGMENTS = {
    "python": ("python", "python3", "nirs4all"),
    "r": ("rscript", "r-predictions", "python/r", "r and wasm", "python/r bindings"),
    "rust": ("cargo", "rust"),
    "rust_archive": ("archived rust", "rust status"),
    "javascript_wasm": ("wasm", "javascript/wasm", "node", "npm"),
    "web": ("web", "nirs4all-web", "screenshot", ".png"),
    "native": ("native", "dag-ml", "nirs4all-methods", "cluster worker", "libn4m"),
}
TAG_EVIDENCE_FRAGMENTS = {
    "datasets": ("dataset", "provider", "assembled"),
    "io": ("io", "reshape", "roundtrip", "manifest hash"),
    "pipeline": ("pipeline", "descriptor", "dag"),
    "repository": ("repository", "best-refit", "descriptor"),
    "papers": ("paper", "papers", "publisher"),
    "predictions": ("prediction", "predictions", "predict"),
    "workspace_save": ("workspace", "save", "saved", ".n4a.json", "persist", "handoff"),
    "parity": ("parity", "match", "delta", "tolerance", "oracle"),
    "multimodal": ("multimodal", "dense-fused"),
    "multisource": ("multisource", "branch", "stacking"),
    "pipeline_generation": ("generated", "generate", "pipeline-family", "stacking"),
    "web_results": ("web-results", "web results", "web-runtime", "result panel", "screenshot", ".png"),
}
STRICT_PARITY_METRIC_FRAGMENTS = (
    "prediction",
    "rmse",
    "score",
    "metric",
    "method output",
    "fixture gate",
    "parity",
)
PHASE_ACCEPTANCE_ACTION_FRAGMENTS = (
    "add ",
    "assert",
    "compare",
    "consume",
    "declare",
    "define",
    "emit",
    "execute",
    "export",
    "include",
    "import",
    "keep",
    "match",
    "must",
    "open",
    "persist",
    "preserve",
    "promote",
    "prove",
    "publish",
    "record",
    "replace",
    "rerun",
    "verify",
)
DISALLOWED_PLACEHOLDER_FRAGMENTS = (
    "coming soon",
    "dummy",
    "lorem ipsum",
    "not implemented",
    "placeholder",
    "stub",
    "tbd",
    "todo",
)


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


def _synthetic_evidence_payload(path: Path) -> dict:
    key = "/".join(path.parts[-2:])
    if key == "r-dataset-io-pipeline/roundtrip-checks.json":
        return {
            "status": "passed",
            "workspace_reopened": True,
            "pipeline_reopened": True,
            "predictions_reopened": True,
            "reproduced_split_targets_rmse_predictions": True,
        }
    if key == "r-dataset-io-pipeline/python-reopen-ledger.json":
        return {
            "status": "passed",
            "tolerance": 1e-6,
            "checks": {
                "workspace_reopened": True,
                "pipeline_reopened": True,
                "python_rerun_executed": True,
                "finite_predictions": True,
                "dataset_hash_match": True,
                "selected_prediction_max_abs_delta": 0,
                "selected_rmse_delta": 0,
                "r_prediction_artifact_max_abs_delta": 0,
            },
        }
    if key == "python-paper-repository/reopened-result.json":
        return {
            "status": "passed",
            "parity": {
                "final_prediction_rows": 1,
                "best_prediction_rows": 1,
                "best_prediction_abs_max": 0,
                "best_rmse_abs": 0,
                "final_prediction_abs_max": 0,
                "bundle_reopen_prediction_abs_max": 0,
                "tolerance": 1e-6,
            },
        }
    if key == "python-paper-repository/repository-best-pipeline.json":
        return {
            "scenario": "e2e-python-reopen-paper-repository-refit",
            "refit": {
                "status": "passed",
                "executed": True,
                "force_best_refit": True,
                "prediction_count": 1,
                "selected_pipeline_id": "synthetic",
            },
            "repository_handoff": {
                "pipeline_id": "synthetic",
                "catalog_index": "catalog/index.json",
                "descriptor": {"id": "synthetic"},
            },
        }
    if key == "wasm-repo-alt-dataset/pipeline-repository-smoke.json":
        return {
            "status": "passed",
            "repository_pipeline_id": "synthetic-repository-pipeline",
            "repository_dataset_id": "synthetic-non-demo-dataset",
            "repository_descriptor_sha256": "0" * 64,
            "repository_descriptor_verified": True,
            "repository_dataset_id_non_demo_sample": True,
            "repository_dataset_files_sha256": "1" * 64,
            "provider_runtime_assertions": {
                "original_folds": {
                    "assignment_sha256": "2" * 64,
                },
            },
            "python_open_pipeline": {
                "status": "passed",
                "pipeline_reopened": True,
                "descriptor_hash_match": True,
                "repository_pipeline_id": "synthetic-repository-pipeline",
                "repository_dataset_id": "synthetic-non-demo-dataset",
                "descriptor_sha256": "0" * 64,
            },
            "python_rerun_pipeline": {
                "status": "passed",
                "executed": True,
                "finite_predictions": True,
                "repository_pipeline_id": "synthetic-repository-pipeline",
                "repository_dataset_id": "synthetic-non-demo-dataset",
                "dataset_files_sha256": "1" * 64,
                "dataset_hash_match": True,
                "fold_assignment_sha256": "2" * 64,
                "python_fold_assignment_sha256": "2" * 64,
                "fold_assignment_hash_match": True,
                "prediction_rows": 4,
                "rmse": 0.1,
            },
            "executed_imported_pipeline": True,
            "console_error_count": 0,
            "prediction_comparison": {
                "compared_rows": 4,
                "max_abs_delta": 0,
                "tolerance": 1e-6,
            },
            "python_oracle_comparison": {
                "max_abs_delta": 0,
                "predictions_tolerance": 1e-6,
            },
            "imported_python_oracle_comparison": {
                "max_abs_delta": 0,
                "predictions_tolerance": 1e-6,
            },
        }
    if key == "legacy-converter/python-open-pipeline.json":
        return {
            "schema_version": "n4a.e2e.python_open_pipeline.v1",
            "scenario_id": "e2e-converter-legacy-save-predictions-web",
            "status": "passed",
            "legacy_workspace_opened": True,
            "converted_workspace_reopened": True,
            "store_reopened_read_only": True,
            "sqlite_integrity_ok": True,
            "sqlite_foreign_key_check_ok": True,
            "required_tables_present": True,
            "runtime_result_reopened": True,
            "pipeline_metadata_reopened": True,
            "chain_metadata_reopened": True,
            "prediction_metadata_reopened": True,
            "store_hash_match": True,
            "array_hash_match": True,
            "manifest_source_fingerprint_match": True,
            "report_verification_summary_match": True,
            "store_user_version": 2,
            "expected_store_user_version": 2,
            "store_user_version_match": True,
            "row_counts_match_report": True,
            "workspace_artifact_counts_match_store": True,
            "run_pipeline_fk_match": True,
            "chain_pipeline_fk_match": True,
            "prediction_pipeline_fk_match": True,
            "prediction_chain_fk_match": True,
            "pipeline_dataset_match": True,
            "chain_dataset_match": True,
            "chain_model_class_match": True,
            "chain_model_name_match": True,
            "runtime_result_pipeline_id_match": True,
            "runtime_result_prediction_id_match": True,
            "runtime_result_rows_match": True,
            "array_prediction_id_match": True,
            "array_rows_match": True,
            "pipeline_step_count": 2,
            "pipeline_classes": ["sklearn.cross_decomposition.PLSRegression"],
            "prediction_rows": 3,
            "workspace_row_counts": {"runs": 1, "pipelines": 1, "chains": 1, "predictions": 1, "arrays": 1},
            "store_row_counts": {"chains": 1, "pipelines": 1, "predictions": 1, "runs": 1},
            "fingerprints": {
                "store_sha256": "sha256:" + "3" * 64,
                "runtime_array_sha256": "sha256:" + "4" * 64,
            },
            "converted": {
                "run_id": "run-2024-legacy",
                "pipeline_id": "pipeline-pls",
                "chain_id": "chain-1",
                "prediction_id": "pred-loose-001",
                "dataset_name": "cassava-drymatter-2024",
                "model_name": "PLSRegression",
                "model_class": "sklearn.cross_decomposition.PLSRegression",
                "metric": "rmse",
                "task_type": "regression",
                "prediction_scope": "loose-predictions",
                "prediction_level": "prediction-row",
                "run_datasets": ["cassava-drymatter-2024"],
                "pipeline_config": {"source_kind": "loose-predictions"},
                "pipeline_generator_choices": [],
            },
        }
    if key == "legacy-converter/python-rerun-pipeline.json":
        return {
            "schema_version": "n4a.e2e.python_rerun_pipeline.v1",
            "scenario_id": "e2e-converter-legacy-save-predictions-web",
            "status": "passed",
            "converted_workspace_reopened": True,
            "pipeline_reopened": True,
            "python_rerun_executed": True,
            "finite_predictions": True,
            "prediction_rows": 3,
            "prediction_max_abs_delta": 0,
            "prediction_tolerance": 1e-6,
            "rmse_delta": 0,
            "rmse_tolerance": 1e-6,
        }
    if key == "custom-app-host/custom-host-python-open.json":
        return {
            "schema_version": "n4a.e2e.python_open_pipeline.v1",
            "scenario_id": "e2e-core-ui-custom-app-host",
            "status": "passed",
            "oracle_reopened": True,
            "pipeline_reopened": True,
            "dataset_reopened": True,
            "fixture_path_match": True,
            "pipeline_name_match": True,
            "case_name_match": True,
            "pipeline_classes": [
                "nirs4all.operators.splitters.KennardStoneSplitter",
                "nirs4all.operators.transforms.StandardNormalVariate",
                "nirs4all.operators.transforms.SavitzkyGolay",
                "sklearn.cross_decomposition.PLSRegression",
            ],
            "plan_step_count": 4,
            "selected_n_components_expected": 6,
            "dataset": {"rows": 40, "cols": 28},
            "fingerprints": {
                "oracle_sha256": "sha256:" + "5" * 64,
                "pipeline_descriptor_sha256": "sha256:" + "6" * 64,
            },
        }
    if key == "custom-app-host/custom-host-python-rerun.json":
        return {
            "schema_version": "n4a.e2e.python_rerun_pipeline.v1",
            "scenario_id": "e2e-core-ui-custom-app-host",
            "status": "passed",
            "oracle_reopened": True,
            "pipeline_reopened": True,
            "python_rerun_executed": True,
            "finite_predictions": True,
            "prediction_rows": 12,
            "split_match": True,
            "variant_count_match": True,
            "selected_n_components_match": True,
            "target_max_abs_delta": 0,
            "target_tolerance": 1e-12,
            "prediction_max_abs_delta": 0,
            "prediction_tolerance": 1e-5,
            "rmse_delta": 0,
            "rmse_tolerance": 1e-6,
            "variant_rmse_max_abs_delta": 0,
            "variant_prediction_max_abs_delta": 0,
        }
    if key == "multimodal-roundtrip/python-rerun-ledger.json":
        return {
            "schema_version": "n4a.e2e.python_rerun_pipeline.v1",
            "scenario_id": "e2e-multimodal-python-r-wasm-roundtrip",
            "status": "passed",
            "pipeline_reopened": True,
            "dataset_reopened": True,
            "python_rerun_executed": True,
            "finite_predictions": True,
            "prediction_rows": 12,
            "pipeline_hash_match": True,
            "dataset_hash_match": True,
            "split_hash_match": True,
            "selected_n_components_match": True,
            "prediction_shape_match": True,
            "prediction_max_abs_delta": 0,
            "prediction_tolerance": 1e-8,
            "target_shape_match": True,
            "target_max_abs_delta": 0,
            "target_tolerance": 1e-8,
            "rmse_delta": 0,
            "rmse_tolerance": 1e-8,
        }
    if key == "multisource-stacking/python-rerun-ledger.json":
        return {
            "schema_version": "n4a.e2e.python_rerun_pipeline.v1",
            "scenario_id": "e2e-multisource-branching-stacking-replay",
            "status": "passed",
            "pipeline_reopened": True,
            "replay_manifest_reopened": True,
            "python_rerun_executed": True,
            "finite_predictions": True,
            "prediction_rows": 4,
            "pipeline_hash_match": True,
            "branch_hash_match": True,
            "fold_hash_match": True,
            "prediction_shape_match": True,
            "prediction_max_abs_delta": 0,
            "prediction_tolerance": 1e-8,
            "target_shape_match": True,
            "target_max_abs_delta": 0,
            "target_tolerance": 1e-8,
            "cv_best_score_delta": 0,
            "best_rmse_delta": 0,
            "score_tolerance": 1e-8,
        }
    return {
        "status": "passed",
        "ok": True,
        "prediction_rows": 1,
        "prediction_max_abs_delta": 0,
        "prediction_tolerance": 1e-6,
    }


def _scenario_by_id(manifest: dict, scenario_id: str) -> dict:
    for scenario in manifest["scenarios"]:
        if scenario["id"] == scenario_id:
            return scenario
    raise AssertionError(f"missing scenario: {scenario_id}")


def _contract_text(*values: object) -> str:
    return json.dumps(values, sort_keys=True).lower()


def _placeholder_hits(value: object, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, str):
        normalized = value.lower()
        for fragment in DISALLOWED_PLACEHOLDER_FRAGMENTS:
            if fragment in normalized:
                hits.append(f"{path}: {fragment!r}")
        return hits
    if isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(_placeholder_hits(item, f"{path}[{index}]"))
        return hits
    if isinstance(value, dict):
        for key, item in value.items():
            hits.extend(_placeholder_hits(item, f"{path}.{key}"))
    return hits


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

    assert len(manifest["scenarios"]) == 11
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


def test_cross_language_e2e_docs_list_every_orchestrated_scenario() -> None:
    manifest = _read_manifest()
    docs = (ROOT / "docs" / "CROSS_LANGUAGE_E2E.md").read_text(encoding="utf-8")

    documented_ids = re.findall(r"\| `(e2e-[^`]+)` \|", docs)

    assert documented_ids == [scenario["id"] for scenario in manifest["scenarios"]]
    assert len(documented_ids) == 11


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
        "e2e-core-ui-custom-app-host": {
            "languages": {"python", "r", "javascript_wasm", "web"},
            "repos": {"nirs4all-core", "nirs4all-ui", "nirs4all-web"},
            "tags": {"pipeline", "predictions", "parity", "web_results"},
        },
        "e2e-multimodal-python-r-wasm-roundtrip": {
            "languages": {"python", "r", "javascript_wasm"},
            "repos": {"nirs4all", "nirs4all-core"},
            "tags": {"multimodal", "pipeline", "predictions", "parity"},
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
        if "parity" in scenario["tags"]:
            assert any(check["evidence_level"] == "strict" for check in scenario["parity_checks"]), scenario_id
        phases = manifest["v1_refactor_contract"]["scenario_coverage"][scenario_id]
        assert any(phase["status"] != "gap" for phase in phases.values()), scenario_id


def test_cross_language_e2e_suite_spans_requested_surface_families() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    def _match(*, languages: set[str], tags: set[str], repos: set[str]) -> str:
        for scenario in manifest["scenarios"]:
            if (
                languages.issubset(set(scenario["languages"]))
                and tags.issubset(set(scenario["tags"]))
                and repos.issubset(set(scenario["repos"]))
            ):
                return scenario["id"]
        raise AssertionError(
            f"no scenario covers languages={sorted(languages)} tags={sorted(tags)} repos={sorted(repos)}"
        )

    matched_ids = {
        "r_python_dataset_io_save": _match(
            languages={"r", "python"},
            tags={"datasets", "io", "workspace_save"},
            repos={"nirs4all-datasets", "nirs4all-io"},
        ),
        "papers_repository_refit": _match(
            languages={"python"},
            tags={"papers", "repository", "workspace_save"},
            repos={"nirs4all-papers", "nirs4all-repository"},
        ),
        "wasm_web_repository_predictions": _match(
            languages={"javascript_wasm", "web", "python"},
            tags={"repository", "predictions", "web_results"},
            repos={"nirs4all-web"},
        ),
        "custom_app_host_python_r_wasm_web": _match(
            languages={"python", "r", "javascript_wasm", "web"},
            tags={"pipeline", "predictions", "web_results"},
            repos={"nirs4all-core", "nirs4all-ui", "nirs4all-web"},
        ),
        "converter_save_predictions": _match(
            languages={"python", "web"},
            tags={"workspace_save", "predictions", "web_results"},
            repos={"nirs4all-tools", "nirs4all-web"},
        ),
        "multimodal_roundtrip": _match(
            languages={"python", "r", "javascript_wasm"},
            tags={"multimodal", "predictions"},
            repos={"nirs4all"},
        ),
        "multisource_generation": _match(
            languages={"python", "native"},
            tags={"multisource", "pipeline_generation"},
            repos={"dag-ml", "nirs4all-core"},
        ),
        "formats_io_bindings": _match(
            languages={"python", "r", "javascript_wasm", "native"},
            tags={"datasets", "io", "predictions"},
            repos={"nirs4all-formats", "nirs4all-methods"},
        ),
    }

    assert len(set(matched_ids.values())) == len(matched_ids)


def test_cross_language_e2e_declared_languages_are_backed_by_runtime_evidence() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    for scenario in manifest["scenarios"]:
        text = _contract_text(
            scenario["objective"],
            scenario["repos"],
            scenario["artifacts"],
            scenario["evidence"],
            scenario["parity_checks"],
            scenario["steps"],
            scenario["strictness_gaps"],
        )
        for language in scenario["languages"]:
            fragments = LANGUAGE_EVIDENCE_FRAGMENTS.get(language)
            assert fragments is not None, f"{scenario['id']}: no test fragments for language {language!r}"
            assert any(fragment in text for fragment in fragments), f"{scenario['id']}: {language}"


def test_cross_language_e2e_step_repos_and_path_gates_stay_on_declared_public_surfaces() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    for scenario in manifest["scenarios"]:
        repos = set(scenario["repos"])
        for step in scenario["steps"]:
            step_id = f"{scenario['id']}.{step['id']}"
            step_repo = step["repo"]
            assert step_repo in repos, step_id

            command = " ".join(step["command"])
            assert f"cd {{workspace_root}}/{step_repo}" in command, step_id

            for raw_path in step.get("requires_paths", []):
                if any(fragment in raw_path for fragment in ALLOWED_PUBLIC_CHECKOUT_DATA_BLOCKERS):
                    continue
                assert raw_path.startswith("{workspace_root}/"), f"{step_id}: {raw_path}"
                gated_repo = raw_path.removeprefix("{workspace_root}/").split("/", 1)[0]
                assert gated_repo in repos, f"{step_id}: {raw_path}"


def test_cross_language_e2e_tags_are_backed_by_domain_artifacts_or_evidence() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    for scenario in manifest["scenarios"]:
        text = _contract_text(
            scenario["title"],
            scenario["objective"],
            scenario["artifacts"],
            scenario["evidence"],
            scenario["parity_checks"],
            scenario["strictness_gaps"],
            scenario["v1_refactor_contract"],
        )
        for tag in scenario["tags"]:
            fragments = TAG_EVIDENCE_FRAGMENTS.get(tag)
            assert fragments is not None, f"{scenario['id']}: no test fragments for tag {tag!r}"
            assert any(fragment in text for fragment in fragments), f"{scenario['id']}: {tag}"


def test_cross_language_e2e_strict_parity_checks_assert_real_oracle_comparisons() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    for scenario in manifest["scenarios"]:
        scenario_artifacts = set(scenario["artifacts"])
        produced_artifacts = {
            artifact
            for step in scenario["steps"]
            for artifact in step.get("produces", [])
        }
        strict_checks = [
            check for check in scenario["parity_checks"] if check["evidence_level"] == "strict"
        ]
        assert strict_checks, scenario["id"]
        for check in strict_checks:
            metric = check["metric"].lower()
            assert any(fragment in metric for fragment in STRICT_PARITY_METRIC_FRAGMENTS), (
                f"{scenario['id']}: {check['metric']}"
            )
            assert "schema/array coverage" not in metric, scenario["id"]
            assert "smoke-only" not in metric, scenario["id"]
            artifacts = set(check["artifacts"])
            assert artifacts, scenario["id"]
            assert artifacts <= scenario_artifacts, scenario["id"]
            assert artifacts <= produced_artifacts, scenario["id"]
            assert all(Path(artifact).suffix == ".json" for artifact in artifacts), scenario["id"]


def test_cross_language_e2e_all_parity_checks_link_declared_artifacts() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    for scenario in manifest["scenarios"]:
        scenario_artifacts = set(scenario["artifacts"])
        produced_artifacts = {
            artifact
            for step in scenario["steps"]
            for artifact in step.get("produces", [])
        }
        for index, check in enumerate(scenario["parity_checks"]):
            artifacts = set(check["artifacts"])
            assert artifacts, f"{scenario['id']}.parity_checks[{index}]"
            assert artifacts <= scenario_artifacts, f"{scenario['id']}.parity_checks[{index}]"
            assert artifacts <= produced_artifacts, f"{scenario['id']}.parity_checks[{index}]"


def test_cross_language_e2e_non_gap_v1_phases_are_artifact_backed() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    for scenario in manifest["scenarios"]:
        scenario_artifacts = set(scenario["artifacts"])
        produced_artifacts = {
            artifact
            for step in scenario["steps"]
            for artifact in step.get("produces", [])
        }
        for phase, contract in scenario["v1_refactor_contract"].items():
            acceptance = _contract_text(contract["acceptance"])
            assert any(fragment in acceptance for fragment in PHASE_ACCEPTANCE_ACTION_FRAGMENTS), (
                f"{scenario['id']}.{phase}: acceptance must name an actionable condition"
            )
            if contract["status"] == "gap":
                assert contract.get("gap"), f"{scenario['id']}.{phase}"
                continue
            if contract["status"] == "not_applicable":
                assert contract.get("applicability"), f"{scenario['id']}.{phase}"
                assert "gap" not in contract, f"{scenario['id']}.{phase}"
                assert not contract.get("artifacts"), f"{scenario['id']}.{phase}"
                continue

            artifacts = set(contract.get("artifacts", []))
            assert artifacts, f"{scenario['id']}.{phase}: non-gap phases need evidence artifacts"
            assert artifacts <= scenario_artifacts, f"{scenario['id']}.{phase}"
            assert artifacts <= produced_artifacts, f"{scenario['id']}.{phase}"


def test_cross_language_e2e_repository_scenarios_document_repository_invocation() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    repository_scenarios = [
        scenario for scenario in manifest["scenarios"] if "repository" in scenario["tags"]
    ]
    assert {scenario["id"] for scenario in repository_scenarios} == {
        "e2e-python-reopen-paper-repository-refit",
        "e2e-wasm-open-repo-pipeline-alt-dataset",
        "e2e-dataset-provider-repository-roundtrip",
    }

    for scenario in repository_scenarios:
        produced_artifacts = {
            artifact
            for step in scenario["steps"]
            for artifact in step.get("produces", [])
        }
        repository_steps = [
            step for step in scenario["steps"] if step["repo"] == "nirs4all-repository"
        ]
        repository_delegations = [
            delegated
            for step in scenario["steps"]
            for delegated in step.get("delegated_invocations", [])
            if delegated["repo"] == "nirs4all-repository"
        ]
        assert repository_steps or repository_delegations, scenario["id"]
        for delegated in repository_delegations:
            assert delegated["mode"], scenario["id"]
            assert delegated["calls"], scenario["id"]
            assert delegated["evidence"], scenario["id"]
            assert set(delegated["artifacts"]) <= produced_artifacts, scenario["id"]


def test_cross_language_e2e_repository_forced_refit_has_strict_artifact_evidence() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    strict = [
        (scenario["id"], scenario["v1_refactor_contract"]["repository_forced_best_refit"])
        for scenario in manifest["scenarios"]
        if scenario["v1_refactor_contract"]["repository_forced_best_refit"]["status"] == "strict"
    ]

    assert [scenario_id for scenario_id, _contract in strict] == [
        "e2e-python-reopen-paper-repository-refit"
    ]
    assert strict[0][1]["artifacts"] == [
        "{artifacts_dir}/python-paper-repository/repository-best-pipeline.json"
    ]


@pytest.mark.parametrize(
    ("scenario_id", "contract"),
    [
        (
            "e2e-r-dataset-io-pipeline-save",
            {
                "steps": ["r-load-reshape", "r-run-save", "python-reopen-r-workspace"],
                "languages": {"r", "python", "native"},
                "tags": {"datasets", "io", "pipeline", "workspace_save", "parity"},
                "tools": {"Rscript", "python3.11"},
                "produces": {
                    "dataset-card.json",
                    "workspace.n4a.json",
                    "roundtrip-checks.json",
                    "python-reopen-ledger.json",
                },
                "commands": {"e2e_dataset_io_pipeline.R", "make test-r-parity", "reopen_r_dataset_io_pipeline.py"},
                "evidence": {"Python reopen/rerun ledger", "Python portable oracle", "Native methods parity"},
                "phase_statuses": {
                    "python_open_pipeline": "strict",
                    "python_rerun_pipeline": "strict",
                    "python_parity": "strict",
                    "papers_export": "not_applicable",
                    "repository_forced_best_refit": "not_applicable",
                    "wasm_web_reuse": "not_applicable",
                },
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
                "evidence": {"force_best_refit", "repository_reopen", "Web/WASM import"},
                "phase_statuses": {
                    "python_open_pipeline": "strict",
                    "papers_export": "strict",
                    "repository_forced_best_refit": "strict",
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
                "tools": {"npm", "python3.11"},
                "produces": {"pipeline-repository-smoke.json", "predict-artifact-smoke.json", "web-results.png"},
                "commands": {"smoke:pipeline-repository", "smoke:predict-artifact"},
                "evidence": {"Python nirs4all/sklearn oracle", "fresh Web/WASM session", "python_rerun_pipeline"},
                "phase_statuses": {
                    "python_open_pipeline": "strict",
                    "python_rerun_pipeline": "strict",
                    "python_parity": "strict",
                    "wasm_web_reuse": "strict",
                },
            },
        ),
        (
            "e2e-core-ui-custom-app-host",
            {
                "steps": [
                    "core-r-surface-probe",
                    "core-python-open-rerun",
                    "core-ui-runtime-host",
                    "shared-ui-host-render",
                ],
                "languages": {"python", "r", "javascript_wasm", "web"},
                "tags": {"pipeline", "predictions", "parity", "web_results"},
                "tools": {"python3.11", "Rscript", "npm"},
                "produces": {
                    "custom-host-r-surface.json",
                    "custom-host-python-open.json",
                    "custom-host-python-rerun.json",
                    "custom-host-run.json",
                    "custom-host-predictions.json",
                    "custom-host-runtime-contracts.json",
                    "custom-host-ui.json",
                },
                "commands": {"run_custom_app_host.py", "smoke:custom-app-host", "check:ui-shim", "Rscript"},
                "evidence": {
                    "R binding surface",
                    "Standalone nirs4all-core Python oracle fixture open ledger",
                    "Standalone nirs4all-core Python rerun parity ledger",
                    "nirs4all-core WASM",
                    "runtimeContracts",
                    "nirs4all-ui",
                },
                "phase_statuses": {
                    "python_open_pipeline": "strict",
                    "python_rerun_pipeline": "strict",
                    "python_parity": "strict",
                    "wasm_web_reuse": "strict",
                },
            },
        ),
        (
            "e2e-multimodal-python-r-wasm-roundtrip",
            {
                "steps": ["python-generate-multimodal", "r-wasm-roundtrip"],
                "languages": {"python", "r", "javascript_wasm"},
                "tags": {"multimodal", "datasets", "io", "pipeline", "predictions", "workspace_save", "parity"},
                "tools": {"python3.11", "Rscript", "node"},
                "produces": {
                    "multimodal-pipeline.n4a.json",
                    "python-open-ledger.json",
                    "python-rerun-ledger.json",
                    "r-predictions.parquet",
                    "wasm-predictions.json",
                },
                "commands": {"test_multimodal_roundtrip.py", "run_multimodal_roundtrip.py"},
                "evidence": {"dense-fused multimodal", "Python saved artifact rerun ledger", "Roundtrip manifest hash equality"},
                "phase_statuses": {
                    "python_open_pipeline": "strict",
                    "python_rerun_pipeline": "strict",
                    "python_parity": "strict",
                    "wasm_web_reuse": "contract",
                },
            },
        ),
        (
            "e2e-multisource-branching-stacking-replay",
            {
                "steps": ["python-build-stacking", "native-replay"],
                "languages": {"python", "native", "rust"},
                "tags": {"multisource", "pipeline_generation", "pipeline", "workspace_save", "parity"},
                "tools": {"python3", "python3.11", "cargo"},
                "produces": {
                    "stacking-replay.n4a.json",
                    "python-open-ledger.json",
                    "python-rerun-ledger.json",
                    "oof-ledger.json",
                    "native-replay.json",
                },
                "commands": {"test_multisource_stacking_replay.py", "run_multisource_stacking_replay.py"},
                "evidence": {"OOF", "Python saved stacking replay rerun ledger", "native prediction-table schema/array coverage"},
                "phase_statuses": {
                    "python_open_pipeline": "strict",
                    "python_parity": "strict",
                    "python_rerun_pipeline": "strict",
                },
            },
        ),
        (
            "e2e-converter-legacy-save-predictions-web",
            {
                "steps": ["convert-legacy-save", "python-rerun-converted-pipeline", "web-open-predictions"],
                "languages": {"python", "javascript_wasm", "web"},
                "tags": {"workspace_save", "predictions", "web_results", "pipeline", "parity"},
                "tools": {"python3.11", "npm"},
                "produces": {
                    "converted-workspace.n4a.json",
                    "predictions.rt_result.json",
                    "python-open-pipeline.json",
                    "python-rerun-pipeline.json",
                    "web-results-panels.json",
                },
                "commands": {
                    "test_legacy_save_predictions_web.py",
                    "test_python_rerun_converted_pipeline",
                    "smoke:converted-predictions",
                },
                "evidence": {
                    "legacy fixture values",
                    "Python reopened converted workspace/pipeline metadata ledger",
                    "Python rerun converted workspace",
                    "Web opens converted predictions",
                },
                "phase_statuses": {
                    "python_open_pipeline": "strict",
                    "python_rerun_pipeline": "strict",
                    "python_parity": "strict",
                    "wasm_web_reuse": "strict",
                },
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
                "produces": {
                    "pipeline-candidate.n4a.json",
                    "pipeline-family.json",
                    "python-vs-dagml.json",
                    "web-runtime.json",
                },
                "commands": {"test_pipeline_generation_performance.py", "smoke:performance-compare"},
                "evidence": {"generated candidates", "performance ratio ledger"},
                "phase_statuses": {
                    "python_open_pipeline": "strict",
                    "python_rerun_pipeline": "strict",
                    "wasm_web_reuse": "contract",
                },
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
                "tools": {"python3.11", "Rscript", "cmake", "ninja"},
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


def test_cross_language_e2e_each_scenario_keeps_complex_cross_runtime_shape() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    for scenario in manifest["scenarios"]:
        scenario_id = scenario["id"]
        languages = set(scenario["languages"])
        repos = set(scenario["repos"])
        produced_artifacts = {path for step in scenario["steps"] for path in step.get("produces", [])}
        assert e2e.REQUIRED_SCENARIO_LANGUAGE in languages, scenario_id
        assert len(languages) >= 2, scenario_id
        assert len(repos) >= e2e.MIN_REPOS_PER_SCENARIO, scenario_id
        assert len({step["kind"] for step in scenario["steps"]}) >= e2e.MIN_STEP_KINDS_PER_SCENARIO, scenario_id
        assert len(produced_artifacts) >= e2e.MIN_PRODUCED_ARTIFACTS_PER_SCENARIO, scenario_id
        if "javascript_wasm" in languages:
            assert {"nirs4all-core", "nirs4all-web"} & repos, scenario_id


def test_cross_language_e2e_manifest_rejects_flat_runtime_claims(tmp_path: Path) -> None:
    e2e = _load_e2e_module()

    manifest = _read_manifest()
    scenario = manifest["scenarios"][0]
    scenario["languages"] = [language for language in scenario["languages"] if language != "python"]
    manifest_path = tmp_path / "missing-python-oracle.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="portable oracle runtime"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    scenario = manifest["scenarios"][0]
    for step in scenario["steps"]:
        step["kind"] = "execute"
    manifest_path = tmp_path / "one-step-kind.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="mix at least 2 step kinds"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    scenario = manifest["scenarios"][0]
    scenario["artifacts"] = [
        "{artifacts_dir}/flat/a.json",
        "{artifacts_dir}/flat/b.json",
    ]
    for step in scenario["steps"]:
        step["produces"] = []
    scenario["steps"][0]["produces"] = [scenario["artifacts"][0]]
    scenario["steps"][1]["produces"] = [scenario["artifacts"][1]]
    for phase in manifest["v1_refactor_contract"]["scenario_coverage"][scenario["id"]].values():
        phase["artifacts"] = [scenario["artifacts"][0]]
    manifest_path = tmp_path / "too-few-produced-artifacts.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="at least 3 unique artifacts"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_requires_core_ui_web_custom_app_surface(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    for scenario in manifest["scenarios"]:
        scenario["repos"] = [repo for repo in scenario["repos"] if repo != "nirs4all-ui"]
    manifest_path = tmp_path / "missing-core-ui-web-surface.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="required suite workflow missing: core_ui_web_custom_app"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-core-ui-custom-app-host")
    scenario["languages"] = [language for language in scenario["languages"] if language != "r"]
    manifest_path = tmp_path / "missing-custom-app-r-surface.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="required suite workflow missing: core_ui_web_custom_app"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_custom_app_host_declares_python_r_wasm_web_artifact_flow() -> None:
    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-core-ui-custom-app-host")
    phases = manifest["v1_refactor_contract"]["scenario_coverage"][scenario["id"]]

    assert {"python", "r", "javascript_wasm", "web"}.issubset(set(scenario["languages"]))
    assert {"nirs4all-core", "nirs4all-ui", "nirs4all-web"}.issubset(set(scenario["repos"]))
    assert [step["id"] for step in scenario["steps"]] == [
        "core-r-surface-probe",
        "core-python-open-rerun",
        "core-ui-runtime-host",
        "shared-ui-host-render",
    ]
    assert {step["repo"] for step in scenario["steps"][:2]} == {"nirs4all-core"}
    assert {step["repo"] for step in scenario["steps"][2:]} == {"nirs4all-web"}
    assert phases["python_open_pipeline"]["status"] == "strict"
    assert phases["python_rerun_pipeline"]["status"] == "strict"
    assert phases["python_parity"]["status"] == "strict"
    assert phases["wasm_web_reuse"]["status"] == "strict"

    text = _contract_text(scenario, phases)
    for fragment in (
        "custom-host-r-surface.json",
        "custom-host-python-open.json",
        "custom-host-python-rerun.json",
        "custom-host-run.json",
        "custom-host-predictions.json",
        "custom-host-runtime-contracts.json",
        "custom-host-ui.json",
        "r binding surface",
        "python_open_pipeline",
        "python_rerun_pipeline",
        "nirs4all-core wasm",
        "serialized_model_predict_surfaces",
        "predictportablepipeline",
        "nirs4all-ui",
        "dataset title",
        "selected pipeline",
        "prediction count",
        "result panel",
    ):
        assert fragment in text

    checks_by_artifact = {
        tuple(check["artifacts"]): check
        for check in scenario["parity_checks"]
    }
    runtime_check = checks_by_artifact[
        ("{artifacts_dir}/custom-app-host/custom-host-runtime-contracts.json",)
    ]
    assert runtime_check["evidence_level"] == "strict"
    assert "serialized_model_predict_surfaces" in runtime_check["metric"]
    assert "predictPortablePipeline" in runtime_check["metric"]


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (
            "drop-runtime-contract-check",
            "custom app host requires strict runtime contract artifact evidence",
        ),
        (
            "drop-shared-ui-check",
            "custom app host requires shared UI render artifact evidence",
        ),
        (
            "weaken-shared-ui-flow",
            "custom app host shared UI evidence must mention dataset",
        ),
        (
            "weaken-python-parity-phase",
            "python_parity must stay strict",
        ),
    ],
)
def test_cross_language_e2e_manifest_enforces_custom_app_host_contract(
    tmp_path: Path,
    mutation: str,
    match: str,
) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-core-ui-custom-app-host")

    if mutation == "drop-runtime-contract-check":
        scenario["parity_checks"] = [
            check
            for check in scenario["parity_checks"]
            if "{artifacts_dir}/custom-app-host/custom-host-runtime-contracts.json"
            not in check["artifacts"]
        ]
    elif mutation == "drop-shared-ui-check":
        scenario["parity_checks"] = [
            check
            for check in scenario["parity_checks"]
            if "{artifacts_dir}/custom-app-host/custom-host-ui.json" not in check["artifacts"]
        ]
    elif mutation == "weaken-shared-ui-flow":
        for check in scenario["parity_checks"]:
            if "{artifacts_dir}/custom-app-host/custom-host-ui.json" in check["artifacts"]:
                check["metric"] = "component tags and engine label render from shared UI components"
                break
    elif mutation == "weaken-python-parity-phase":
        manifest["v1_refactor_contract"]["scenario_coverage"][scenario["id"]]["python_parity"]["status"] = "contract"
    else:
        raise AssertionError(mutation)

    manifest_path = tmp_path / f"{mutation}.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match=match):
        e2e.validate_scenarios(manifest_path)


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
        assert (
            summary["strict"] + summary["contract"] + summary["gap"] + summary["not_applicable"]
            == summary["total"]
        ), plan["id"]
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
        "strict": 4,
        "contract": 1,
        "gap": 0,
        "not_applicable": 1,
        "non_gap": 5,
        "strict_phases": [
            "python_open_pipeline",
            "python_rerun_pipeline",
            "python_parity",
            "wasm_web_reuse",
        ],
        "contract_phases": ["repository_forced_best_refit"],
        "gap_phases": [],
        "not_applicable_phases": ["papers_export"],
    }


def test_cross_language_e2e_manifest_requires_exact_scenario_count(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    manifest["scenarios"] = manifest["scenarios"][:-1]
    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="expected exactly 11 scenarios"):
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


def test_cross_language_e2e_manifest_contract_text_is_non_placeholder() -> None:
    manifest = _read_manifest()
    contract_payload = {
        "scenarios": manifest["scenarios"],
        "v1_refactor_contract": manifest["v1_refactor_contract"],
    }

    assert _placeholder_hits(contract_payload) == []


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

    with pytest.raises(e2e.E2EScenarioError, match="numeric parity"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_strict_check_rejects_proxy_representation_metric(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-multimodal-python-r-wasm-roundtrip")
    scenario["tags"].append("parity")
    scenario["parity_checks"][0]["evidence_level"] = "strict"
    scenario["parity_checks"][0]["metric"] = (
        "per-output prediction_abs_max <= 1e-8 within the current proxy representation"
    )
    manifest_path = tmp_path / "proxy-strict.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="proxy-only evidence"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_strict_check_requires_json_artifact_evidence(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-python-reopen-paper-repository-refit")

    scenario["parity_checks"][0]["artifacts"] = []
    manifest_path = tmp_path / "strict-check-without-artifacts.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="strict parity_check requires artifact evidence"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-python-reopen-paper-repository-refit")
    scenario["parity_checks"][0]["artifacts"] = [
        "{artifacts_dir}/python-paper-repository/paper-export.zip"
    ]
    manifest_path = tmp_path / "strict-check-with-zip-artifact.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="strict parity_check artifacts must be JSON"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_strict_artifacts_have_scenario_field_requirements() -> None:
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)

    for scenario in manifest["scenarios"]:
        requirements = e2e.SCENARIO_ARTIFACT_REQUIREMENTS.get(scenario["id"], {})
        strict_artifacts = {
            artifact
            for check in scenario["parity_checks"]
            if check["evidence_level"] == "strict"
            for artifact in check["artifacts"]
        }
        assert strict_artifacts, scenario["id"]
        for artifact in strict_artifacts:
            requirement_key = e2e._artifact_requirement_key(artifact)
            assert requirement_key in requirements, f"{scenario['id']}: {artifact}"
            assert requirements[requirement_key], f"{scenario['id']}: {artifact}"


def test_cross_language_e2e_evidence_rejects_passed_artifact_missing_required_fields(
    tmp_path: Path,
) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "custom-app-host" / "custom-host-predictions.json"
    artifact.parent.mkdir(parents=True)
    _write_json(artifact, {"status": "passed", "ok": True})

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "e2e-core-ui-custom-app-host",
                "artifacts": [str(artifact)],
                "steps": [],
                "parity_checks": [],
            }
        ]
    )

    assert report["failed_count"] == 1
    failures = report["scenarios"]["e2e-core-ui-custom-app-host"]["failures"]
    assert any("missing required evidence field prediction_rows" in failure for failure in failures)


def test_cross_language_e2e_evidence_rejects_wrong_scenario_artifact_shape(
    tmp_path: Path,
) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "custom-app-host" / "custom-host-predictions.json"
    artifact.parent.mkdir(parents=True)
    _write_json(
        artifact,
        {
            "status": "passed",
            "prediction_rows": 12,
            "max_abs_delta": 0.1,
            "tolerance": 0.001,
        },
    )

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "e2e-core-ui-custom-app-host",
                "artifacts": [str(artifact)],
                "steps": [],
                "parity_checks": [],
            }
        ]
    )

    assert report["failed_count"] == 1
    failures = report["scenarios"]["e2e-core-ui-custom-app-host"]["failures"]
    assert any("max_abs_delta" in failure and "exceeds tolerance" in failure for failure in failures)


def test_cross_language_e2e_evidence_accepts_required_scenario_artifact_shape(
    tmp_path: Path,
) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "custom-app-host" / "custom-host-predictions.json"
    artifact.parent.mkdir(parents=True)
    _write_json(
        artifact,
        {
            "status": "passed",
            "prediction_rows": 12,
            "max_abs_delta": 1e-12,
            "tolerance": 1e-6,
        },
    )

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "e2e-core-ui-custom-app-host",
                "artifacts": [str(artifact)],
                "steps": [],
                "parity_checks": [],
            }
        ]
    )

    assert report["verified_count"] == 1
    assert report["failed_count"] == 0


def test_cross_language_e2e_wasm_repository_evidence_requires_python_reopen_rerun(
    tmp_path: Path,
) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "wasm-repo-alt-dataset" / "pipeline-repository-smoke.json"
    artifact.parent.mkdir(parents=True)
    _write_json(
        artifact,
        {
            "status": "passed",
            "repository_descriptor_verified": True,
            "repository_dataset_id_non_demo_sample": True,
            "executed_imported_pipeline": True,
            "console_error_count": 0,
            "prediction_comparison": {
                "compared_rows": 4,
                "max_abs_delta": 0,
                "tolerance": 1e-6,
            },
            "python_oracle_comparison": {
                "max_abs_delta": 0,
                "predictions_tolerance": 1e-6,
            },
            "imported_python_oracle_comparison": {
                "max_abs_delta": 0,
                "predictions_tolerance": 1e-6,
            },
        },
    )

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "e2e-wasm-open-repo-pipeline-alt-dataset",
                "artifacts": [str(artifact)],
                "steps": [],
                "parity_checks": [],
            }
        ]
    )

    assert report["failed_count"] == 1
    failures = "\n".join(report["scenarios"]["e2e-wasm-open-repo-pipeline-alt-dataset"]["failures"])
    assert "missing required evidence field python_open_pipeline.status" in failures
    assert "missing required evidence field python_rerun_pipeline.status" in failures


def test_cross_language_e2e_wasm_repository_evidence_rejects_hash_mismatches(
    tmp_path: Path,
) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "wasm-repo-alt-dataset" / "pipeline-repository-smoke.json"
    artifact.parent.mkdir(parents=True)
    payload = _synthetic_evidence_payload(artifact)
    payload["python_open_pipeline"]["descriptor_sha256"] = "a" * 64
    payload["python_rerun_pipeline"]["dataset_files_sha256"] = "b" * 64
    payload["python_rerun_pipeline"]["fold_assignment_sha256"] = "c" * 64
    payload["python_rerun_pipeline"]["python_fold_assignment_sha256"] = "c" * 64
    _write_json(artifact, payload)

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "e2e-wasm-open-repo-pipeline-alt-dataset",
                "artifacts": [str(artifact)],
                "steps": [],
                "parity_checks": [],
            }
        ]
    )

    assert report["failed_count"] == 1
    failures = "\n".join(report["scenarios"]["e2e-wasm-open-repo-pipeline-alt-dataset"]["failures"])
    assert "python_open_pipeline.descriptor_sha256" in failures
    assert "python_rerun_pipeline.dataset_files_sha256" in failures
    assert "python_rerun_pipeline.fold_assignment_sha256" in failures


def test_cross_language_e2e_parity_check_artifacts_must_be_scenario_artifacts(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-dataset-provider-repository-roundtrip")
    scenario["steps"][0]["produces"].append("{artifacts_dir}/provider-repository-roundtrip/outside-check.json")
    scenario["parity_checks"][1]["artifacts"].append(
        "{artifacts_dir}/provider-repository-roundtrip/outside-check.json"
    )
    manifest_path = tmp_path / "parity-check-outside-scenario-artifacts.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="artifact\\(s\\) are not scenario artifacts"):
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


def test_cross_language_e2e_manifest_requires_one_non_gap_v1_phase_per_scenario(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    scenario_id = manifest["scenarios"][0]["id"]
    coverage = manifest["v1_refactor_contract"]["scenario_coverage"][scenario_id]
    for phase_contract in coverage.values():
        phase_contract["status"] = "gap"
        phase_contract["gap"] = "forced all-gap contract for regression coverage"
        phase_contract.pop("applicability", None)
    manifest_path = tmp_path / "no-non-gap-v1-phase.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="at least one non-gap V1 refactor phase"):
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
        phase_contract.pop("applicability", None)
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


def test_cross_language_e2e_web_surface_cannot_mark_wasm_reuse_not_applicable(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    phase = manifest["v1_refactor_contract"]["scenario_coverage"]["e2e-core-ui-custom-app-host"]["wasm_web_reuse"]
    phase["status"] = "not_applicable"
    phase.pop("artifacts", None)
    phase.pop("gap", None)
    phase["applicability"] = "forced n/a for regression coverage"
    manifest_path = tmp_path / "web-wasm-not-applicable.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="web coverage requires applicable wasm_web_reuse"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_papers_surface_cannot_mark_export_not_applicable(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    phase = manifest["v1_refactor_contract"]["scenario_coverage"]["e2e-python-reopen-paper-repository-refit"]["papers_export"]
    phase["status"] = "not_applicable"
    phase.pop("artifacts", None)
    phase.pop("gap", None)
    phase["applicability"] = "forced n/a for regression coverage"
    manifest_path = tmp_path / "papers-export-not-applicable.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="lacks non-gap coverage for: papers_export"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_requires_strict_repository_forced_refit_coverage(
    tmp_path: Path,
) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    phase = manifest["v1_refactor_contract"]["scenario_coverage"]["e2e-python-reopen-paper-repository-refit"]["repository_forced_best_refit"]
    phase["status"] = "contract"
    manifest_path = tmp_path / "no-strict-repository-forced-refit.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(
        e2e.E2EScenarioError,
        match="at least one strict repository_forced_best_refit",
    ):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_requires_strict_repository_forced_refit_artifacts(
    tmp_path: Path,
) -> None:
    e2e = _load_e2e_module()
    manifest = _read_manifest()
    phase = manifest["v1_refactor_contract"]["scenario_coverage"]["e2e-python-reopen-paper-repository-refit"]["repository_forced_best_refit"]
    phase["artifacts"] = []
    manifest_path = tmp_path / "strict-repository-forced-refit-without-artifacts.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="strict repository forced-refit coverage requires artifact evidence"):
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
    assert len(scenario_ids) == 11
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

    assert report["scenario_count"] == 11
    assert report["expected_scenario_count"] == 11
    assert report["evidence_levels"] == {"hybrid": 11}
    assert report["required_languages"] == {
        "javascript_wasm": 8,
        "python": 11,
        "r": 4,
        "web": 5,
    }
    assert report["languages"] == {
        "javascript_wasm": 8,
        "native": 6,
        "python": 11,
        "r": 4,
        "rust": 1,
        "rust_archive": 1,
        "web": 5,
    }
    assert report["required_tags"] == {
        "datasets": 5,
        "io": 4,
        "multimodal": 1,
        "multisource": 1,
        "papers": 1,
        "parity": 11,
        "pipeline": 11,
        "pipeline_generation": 2,
        "predictions": 6,
        "repository": 3,
        "web_results": 5,
        "workspace_save": 6,
    }
    assert report["debt_summary"]["strictness_gap_count"] == 12
    assert report["debt_summary"]["parity_check_evidence_levels"] == {
        "contract": 7,
        "strict": 18,
    }
    assert report["debt_summary"]["scenarios_without_strict_parity_check"] == []
    assert report["debt_summary"]["v1_contract_phase_count"] == 5
    assert report["debt_summary"]["v1_gap_phase_count"] == 0
    assert report["debt_summary"]["v1_not_applicable_phase_count"] == 25
    assert report["debt_summary"]["scenario_phase_debt"]["e2e-core-ui-custom-app-host"] == {
        "strictness_gaps": 2,
        "contract_phases": [],
        "gap_phases": [],
        "not_applicable_phases": ["papers_export", "repository_forced_best_refit"],
        "contract_parity_checks": 1,
        "strict_parity_checks": 3,
    }
    assert report["debt_summary"]["scenario_phase_debt"]["e2e-wasm-open-repo-pipeline-alt-dataset"] == {
        "strictness_gaps": 1,
        "contract_phases": ["repository_forced_best_refit"],
        "gap_phases": [],
        "not_applicable_phases": ["papers_export"],
        "contract_parity_checks": 1,
        "strict_parity_checks": 3,
    }
    assert report["debt_summary"]["scenario_phase_debt"]["e2e-multimodal-python-r-wasm-roundtrip"] == {
        "strictness_gaps": 1,
        "contract_phases": ["wasm_web_reuse"],
        "gap_phases": [],
        "not_applicable_phases": ["papers_export", "repository_forced_best_refit"],
        "contract_parity_checks": 0,
        "strict_parity_checks": 1,
    }
    assert report["repos"] == {
        "dag-ml": 4,
        "dag-ml-data": 2,
        "nirs4all": 6,
        "nirs4all-cluster": 1,
        "nirs4all-core": 9,
        "nirs4all-datasets": 4,
        "nirs4all-formats": 1,
        "nirs4all-io": 3,
        "nirs4all-methods": 6,
        "nirs4all-papers": 1,
        "nirs4all-providers": 2,
        "nirs4all-repository": 3,
        "nirs4all-tools": 1,
        "nirs4all-ui": 3,
        "nirs4all-web": 5,
    }
    assert report["ready_count"] + report["blocked_count"] == 11
    assert set(report["v1_refactor_phase_status_counts"]) == {
        "python_open_pipeline",
        "python_rerun_pipeline",
        "python_parity",
        "papers_export",
        "repository_forced_best_refit",
        "wasm_web_reuse",
    }
    expected_phase_counts = {
        "python_open_pipeline": {"strict": 9, "contract": 0, "gap": 0, "not_applicable": 2},
        "python_rerun_pipeline": {"strict": 10, "contract": 0, "gap": 0, "not_applicable": 1},
        "python_parity": {"strict": 11, "contract": 0, "gap": 0, "not_applicable": 0},
        "papers_export": {"strict": 1, "contract": 0, "gap": 0, "not_applicable": 10},
        "repository_forced_best_refit": {"strict": 1, "contract": 1, "gap": 0, "not_applicable": 9},
        "wasm_web_reuse": {"strict": 4, "contract": 4, "gap": 0, "not_applicable": 3},
    }
    assert report["v1_refactor_phase_status_counts"] == expected_phase_counts
    scenario_ids_by_phase = report["v1_refactor_phase_scenario_ids"]
    assert scenario_ids_by_phase["repository_forced_best_refit"]["strict"] == [
        "e2e-python-reopen-paper-repository-refit",
    ]
    assert set(scenario_ids_by_phase["repository_forced_best_refit"]["contract"]) == {
        "e2e-wasm-open-repo-pipeline-alt-dataset",
    }
    assert scenario_ids_by_phase["papers_export"]["gap"] == []
    assert set(scenario_ids_by_phase["papers_export"]["not_applicable"]) == {
        scenario_id
        for scenario_id in report["scenario_summaries"]
        if scenario_id != "e2e-python-reopen-paper-repository-refit"
    }
    assert set(scenario_ids_by_phase["wasm_web_reuse"]["strict"]) == {
        "e2e-core-ui-custom-app-host",
        "e2e-converter-legacy-save-predictions-web",
        "e2e-dataset-provider-repository-roundtrip",
        "e2e-wasm-open-repo-pipeline-alt-dataset",
    }
    for counts in expected_phase_counts.values():
        assert counts["strict"] + counts["contract"] + counts["gap"] + counts["not_applicable"] == 11
        assert counts["strict"] + counts["contract"] >= 1
    for scenario_id, summary in report["scenario_summaries"].items():
        assert summary["steps"] >= 2
        assert summary["artifacts"] >= 2
        assert summary["strict_parity_checks"] >= 1
        assert summary["v1_refactor_summary"]["non_gap"] >= 1


def test_cross_language_e2e_cli_coverage_text_prints_debt_summary() -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"

    covered = subprocess.run(
        [sys.executable, str(script), "coverage"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    assert (
        "debt: strictness_gaps=12 v1_contract_phases=5 "
        "v1_gap_phases=0 v1_not_applicable_phases=25"
    ) in covered.stdout
    assert "without_strict_parity=" in covered.stdout
    assert "without_strict_parity=e2e-multimodal-python-r-wasm-roundtrip" not in covered.stdout


def test_cross_language_e2e_cli_coverage_json_out_writes_report(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    report_path = tmp_path / "coverage-summary.json"

    covered = subprocess.run(
        [sys.executable, str(script), "coverage", "--json-out", str(report_path)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert "11/11 scenarios" in covered.stdout
    assert report["scenario_count"] == 11
    assert report["debt_summary"]["strictness_gap_count"] == 12


def test_cross_language_e2e_cli_coverage_markdown_out_writes_debt_board(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    report_path = tmp_path / "coverage-debt.md"

    subprocess.run(
        [sys.executable, str(script), "coverage", "--markdown-out", str(report_path)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    report = report_path.read_text(encoding="utf-8")

    assert "# NIRS4ALL Cross-language E2E Coverage" in report
    assert "| strictness gaps | 12 |" in report
    assert "| V1 gap phases | 0 |" in report
    assert "| V1 not applicable phases | 25 |" in report
    assert "e2e-core-ui-custom-app-host" in report
    assert "repository_forced_best_refit" in report
    assert "javascript_wasm" in report


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
    for check in scenario["parity_checks"]:
        check["artifacts"] = [path.replace("repository", "repo") for path in check.get("artifacts", [])]
    manifest_path = tmp_path / "repository-without-artifact.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="repository tag requires a repository artifact"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-dataset-provider-repository-roundtrip")
    for step in scenario["steps"]:
        step.pop("delegated_invocations", None)
        step.pop("delegates_to_repos", None)
    manifest_path = tmp_path / "repository-without-delegate.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="nirs4all-repository step or documented delegated invocation"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-core-ui-custom-app-host")
    for step in scenario["steps"]:
        step["requires_tools"] = [tool for tool in step.get("requires_tools", []) if tool != "Rscript"]
    manifest_path = tmp_path / "r-without-rscript.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="r coverage requires an Rscript-gated step"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-formats-io-datasets-methods-language-bindings")
    for step in scenario["steps"]:
        if "Rscript" in step.get("requires_tools", []):
            step["command"] = [
                part.replace("Rscript --version >/dev/null && ", "")
                for part in step["command"]
            ]
    manifest_path = tmp_path / "rscript-without-probe.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="must invoke or probe Rscript"):
        e2e.validate_scenarios(manifest_path)

    manifest = _read_manifest()
    scenario = _scenario_by_id(manifest, "e2e-core-ui-custom-app-host")
    scenario["strictness_gaps"] = [
        gap for gap in scenario["strictness_gaps"] if "full R numeric rerun" not in gap
    ]
    manifest_path = tmp_path / "structural-r-without-gap.json"
    _write_json(manifest_path, manifest)

    with pytest.raises(e2e.E2EScenarioError, match="without numeric R evidence"):
        e2e.validate_scenarios(manifest_path)


def test_cross_language_e2e_manifest_declares_known_semantic_gaps() -> None:
    manifest = _read_manifest()
    flow = manifest["v1_refactor_contract"]["scenario_coverage"]

    repository_refit = _scenario_by_id(manifest, "e2e-python-reopen-paper-repository-refit")
    assert repository_refit["evidence_level"] == "hybrid"
    assert not any("does not execute a repository best-pipeline refit yet" in gap for gap in repository_refit["strictness_gaps"])
    assert any("refit.executed=true" in check["metric"] for check in repository_refit["parity_checks"])
    repository_flow = flow["e2e-python-reopen-paper-repository-refit"]
    assert repository_flow["python_open_pipeline"]["status"] == "strict"
    assert repository_flow["papers_export"]["status"] == "strict"
    assert repository_flow["repository_forced_best_refit"]["status"] == "strict"
    repository_refit_contract = json.dumps(repository_flow["repository_forced_best_refit"], sort_keys=True)
    assert "force_best_refit=true" in repository_refit_contract
    assert "selected artificial best pipeline id" in repository_refit_contract
    assert "descriptor/manifest/catalog fingerprints" in repository_refit_contract
    assert "repository_reopen_validated=true" in repository_refit_contract
    assert "repository-owned forced_best_refit_contract" in repository_refit_contract
    assert repository_flow["wasm_web_reuse"]["status"] == "contract"
    assert "alternative uploadable dataset" in repository_flow["wasm_web_reuse"]["gap"]

    wasm_alt_dataset = _scenario_by_id(manifest, "e2e-wasm-open-repo-pipeline-alt-dataset")
    assert wasm_alt_dataset["evidence_level"] == "hybrid"
    assert any("non-demo uploaded fixture dataset" in gap for gap in wasm_alt_dataset["strictness_gaps"])
    assert any("external provider/catalog dataset" in gap for gap in wasm_alt_dataset["strictness_gaps"])
    wasm_flow = flow["e2e-wasm-open-repo-pipeline-alt-dataset"]
    assert wasm_flow["python_open_pipeline"]["status"] == "strict"
    assert wasm_flow["python_rerun_pipeline"]["status"] == "strict"
    assert "python_open_pipeline.status=passed" in json.dumps(wasm_flow["python_open_pipeline"], sort_keys=True)
    assert "python_rerun_pipeline.status=passed" in json.dumps(wasm_flow["python_rerun_pipeline"], sort_keys=True)
    assert wasm_flow["python_parity"]["status"] == "strict"
    assert wasm_flow["wasm_web_reuse"]["status"] == "strict"

    multimodal = _scenario_by_id(manifest, "e2e-multimodal-python-r-wasm-roundtrip")
    assert multimodal["evidence_level"] == "hybrid"
    assert any("dense fused-matrix multimodal proxy" in gap for gap in multimodal["strictness_gaps"])
    assert not any("proxy representation" in check["metric"] for check in multimodal["parity_checks"])
    assert any("dense-fused feature representation" in check["metric"] for check in multimodal["parity_checks"])
    assert flow["e2e-multimodal-python-r-wasm-roundtrip"]["python_open_pipeline"]["status"] == "strict"
    assert "python-open-ledger.json" in json.dumps(
        flow["e2e-multimodal-python-r-wasm-roundtrip"]["python_open_pipeline"],
        sort_keys=True,
    )
    assert flow["e2e-multimodal-python-r-wasm-roundtrip"]["python_rerun_pipeline"]["status"] == "strict"
    assert "python-rerun-ledger.json" in json.dumps(
        flow["e2e-multimodal-python-r-wasm-roundtrip"]["python_rerun_pipeline"],
        sort_keys=True,
    )
    assert flow["e2e-multimodal-python-r-wasm-roundtrip"]["python_parity"]["status"] == "strict"
    assert flow["e2e-multimodal-python-r-wasm-roundtrip"]["wasm_web_reuse"]["status"] == "contract"

    multisource = _scenario_by_id(manifest, "e2e-multisource-branching-stacking-replay")
    assert multisource["evidence_level"] == "hybrid"
    assert any("schema/array coverage" in gap for gap in multisource["strictness_gaps"])
    assert flow["e2e-multisource-branching-stacking-replay"]["python_open_pipeline"]["status"] == "strict"
    assert "branch/source/pipeline identity" in json.dumps(
        flow["e2e-multisource-branching-stacking-replay"]["python_open_pipeline"],
        sort_keys=True,
    )
    assert flow["e2e-multisource-branching-stacking-replay"]["python_rerun_pipeline"]["status"] == "strict"
    assert "python-rerun-ledger.json" in json.dumps(
        flow["e2e-multisource-branching-stacking-replay"]["python_rerun_pipeline"],
        sort_keys=True,
    )
    assert (
        flow["e2e-multisource-branching-stacking-replay"]["repository_forced_best_refit"]["status"]
        == "not_applicable"
    )
    assert (
        "does not publish a repository recipe"
        in flow["e2e-multisource-branching-stacking-replay"]["repository_forced_best_refit"]["applicability"]
    )

    dataset_roundtrip = _scenario_by_id(manifest, "e2e-dataset-provider-repository-roundtrip")
    assert dataset_roundtrip["evidence_level"] == "hybrid"
    assert any("does not execute R" in gap for gap in dataset_roundtrip["strictness_gaps"])
    assert flow["e2e-dataset-provider-repository-roundtrip"]["wasm_web_reuse"]["status"] == "strict"
    assert (
        flow["e2e-dataset-provider-repository-roundtrip"]["repository_forced_best_refit"]["status"]
        == "not_applicable"
    )
    assert (
        "descriptor consumption"
        in flow["e2e-dataset-provider-repository-roundtrip"]["repository_forced_best_refit"]["applicability"]
    )

    performance = _scenario_by_id(manifest, "e2e-pipeline-generation-performance-compare")
    assert performance["evidence_level"] == "hybrid"
    assert any("Studio is explicitly outside this Web-only gate" in gap for gap in performance["strictness_gaps"])
    assert flow["e2e-pipeline-generation-performance-compare"]["python_open_pipeline"]["status"] == "strict"
    assert "pipeline-candidate.n4a.json" in json.dumps(
        flow["e2e-pipeline-generation-performance-compare"]["python_open_pipeline"],
        sort_keys=True,
    )

    formats_bindings = _scenario_by_id(manifest, "e2e-formats-io-datasets-methods-language-bindings")
    assert formats_bindings["evidence_level"] == "hybrid"
    assert any("WASM remains fixture-scoped" in gap for gap in formats_bindings["strictness_gaps"])
    assert flow["e2e-formats-io-datasets-methods-language-bindings"]["wasm_web_reuse"]["status"] == "contract"

    cluster = _scenario_by_id(manifest, "e2e-cluster-dag-rights-client-core")
    assert cluster["evidence_level"] == "hybrid"
    assert any("public checkout remains data-blocked" in gap for gap in cluster["strictness_gaps"])
    assert flow["e2e-cluster-dag-rights-client-core"]["python_parity"]["status"] == "strict"
    assert flow["e2e-cluster-dag-rights-client-core"]["wasm_web_reuse"]["status"] == "not_applicable"
    assert (
        "no Web or JavaScript/WASM runtime surface"
        in flow["e2e-cluster-dag-rights-client-core"]["wasm_web_reuse"]["applicability"]
    )


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
    assert "parity" in plan["tags"]
    assert [check["evidence_level"] for check in plan["parity_checks"]].count("strict") >= 2
    assert plan["v1_refactor_contract"]["python_parity"]["status"] == "strict"
    assert plan["v1_refactor_contract"]["wasm_web_reuse"]["status"] == "strict"
    assert plan["steps"][0]["delegates_to_repos"] == ["nirs4all-repository"]
    assert plan["steps"][0]["delegated_invocations"][0]["repo"] == "nirs4all-repository"
    assert plan["steps"][0]["delegated_invocations"][0]["artifacts"]


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
    assert 'N4A_E2E_MAX_ARTIFACT_AGE_SECONDS: "14400"' in workflow
    assert "allow_blocked:" in workflow
    assert "run-ready --execute" in workflow
    assert "Verify ready scenario artifacts" in workflow
    assert "Write coverage debt board" in workflow
    assert "Upload coverage debt board" in workflow
    assert "--json-out .n4a-e2e-artifacts/coverage/coverage-summary.json" in workflow
    assert "--markdown-out .n4a-e2e-artifacts/coverage/coverage-debt.md" in workflow
    assert "python3 scripts/n4a_e2e_scenarios.py evidence" in workflow
    assert "--ready-only" in workflow
    assert '--max-age-seconds "$N4A_E2E_MAX_ARTIFACT_AGE_SECONDS"' in workflow
    assert "--json-out .n4a-e2e-artifacts/evidence-summary.json" in workflow
    assert workflow.count("--json-out .n4a-e2e-artifacts/evidence-summary.json") == 2
    assert "actions/upload-artifact@v4" in workflow
    assert "n4a-e2e-coverage-debt-${{ github.run_id }}" in workflow
    assert "n4a-e2e-ready-runtime-evidence-${{ github.run_id }}" in workflow
    assert "n4a-e2e-${{ github.event.inputs.scenario }}-runtime-evidence-${{ github.run_id }}" in workflow
    assert workflow.count("path: nirs4all-ecosystem/.n4a-e2e-artifacts/coverage/**") == 1
    assert workflow.count("path: nirs4all-ecosystem/.n4a-e2e-artifacts/**") == 2
    assert workflow.count("if-no-files-found: warn") == 3
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
    assert "Verify selected scenario artifacts" in workflow
    assert '--scenario "$N4A_E2E_SCENARIO"' in workflow
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
        step["requires_tools"] = ["Rscript", "definitely-missing-n4a-e2e-tool"]
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
                    f"from pathlib import Path; Path({str(artifact)!r}).write_text('{{\"status\":\"passed\"}}\\n')",
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
        {},
        [],
        None,
        {"note": "command exited zero"},
        [{"note": "nested list without evidence"}],
    ],
)
def test_cross_language_e2e_rejects_non_passing_json_artifacts(tmp_path: Path, payload: object) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "non-passing-result.json"

    returncode = e2e.execute_plan(
        {
            "id": "synthetic",
            "status": "ready",
            "parity_checks": [{"artifacts": [str(artifact)]}],
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


def test_cross_language_e2e_allows_structural_json_without_positive_signal(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "pipeline.n4a.json"
    artifact.write_text('{"nodes": [], "edges": []}\n', encoding="utf-8")

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "synthetic",
                "artifacts": [str(artifact)],
                "steps": [{"id": "write-structure", "produces": [str(artifact)]}],
            }
        ]
    )

    assert report["verified_count"] == 1
    assert report["failed_count"] == 0


def test_cross_language_e2e_parity_artifacts_require_positive_signal(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "parity-ledger.json"
    artifact.write_text('{"note": "command exited zero"}\n', encoding="utf-8")

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "synthetic",
                "artifacts": [str(artifact)],
                "parity_checks": [{"artifacts": [str(artifact)]}],
                "steps": [{"id": "write-evidence", "produces": [str(artifact)]}],
            }
        ]
    )

    assert report["verified_count"] == 0
    assert report["failed_count"] == 1
    assert "no positive passing signal" in "\n".join(report["scenarios"]["synthetic"]["failures"])


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            {
                "status": "passed",
                "prediction_rows": "12",
            },
            "prediction_rows='12' must be numeric",
        ),
        (
            {
                "status": "passed",
                "prediction_rows": 0,
            },
            "prediction_rows=0 must be > 0",
        ),
        (
            {
                "status": "passed",
                "prediction_rows": 12,
                "duration_ms": -5,
            },
            "duration_ms=-5 must be non-negative",
        ),
        (
            {
                "status": "passed",
                "prediction_rows": 12,
                "prediction_max_abs_delta": 0.002,
                "prediction_tolerance": 0.001,
            },
            "prediction_max_abs_delta=0.002 exceeds prediction_tolerance=0.001",
        ),
        (
            {
                "status": "passed",
                "prediction_rows": 12,
                "rmse": float("nan"),
            },
            "rmse=nan is not finite",
        ),
        (
            {
                "status": "passed",
                "prediction_rows": 12,
                "parity_ok": False,
            },
            "parity_ok=false",
        ),
        (
            {
                "status": "passed",
                "prediction_rows": 12,
                "within_tolerance": False,
            },
            "within_tolerance=false",
        ),
    ],
)
def test_cross_language_e2e_rejects_semantically_weak_numeric_artifacts(
    tmp_path: Path,
    payload: dict,
    expected: str,
) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "weak-numeric-result.json"
    artifact.write_text(json.dumps(payload), encoding="utf-8")

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "synthetic",
                "artifacts": [str(artifact)],
                "steps": [
                    {
                        "id": "write-evidence",
                        "produces": [str(artifact)],
                    }
                ],
            }
        ]
    )

    assert report["verified_count"] == 0
    assert report["failed_count"] == 1
    assert expected in "\n".join(report["scenarios"]["synthetic"]["failures"])


def test_cross_language_e2e_accepts_signed_delta_within_tolerance(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / "signed-delta-result.json"
    artifact.write_text(
        json.dumps(
            {
                "status": "passed",
                "prediction_rows": 12,
                "rmse_delta": -0.001,
                "rmse_tolerance": 0.01,
            }
        ),
        encoding="utf-8",
    )

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "synthetic",
                "artifacts": [str(artifact)],
                "steps": [{"id": "write-evidence", "produces": [str(artifact)]}],
            }
        ]
    )

    assert report["verified_count"] == 1
    assert report["failed_count"] == 0


def test_cross_language_e2e_artifact_evidence_report_verifies_existing_artifacts(tmp_path: Path) -> None:
    e2e = _load_e2e_module()
    json_artifact = tmp_path / "passing-result.json"
    png_artifact = tmp_path / "web-results.png"
    zip_artifact = tmp_path / "paper-export.zip"
    parquet_artifact = tmp_path / "predictions.parquet"
    json_artifact.write_text(
        json.dumps(
            {
                "status": "passed",
                "ok": True,
                "prediction_rows": 4,
                "prediction_max_abs_delta": 1e-9,
                "prediction_tolerance": 1e-6,
                "within_tolerance": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    png_artifact.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xe2A\xb5"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    with zipfile.ZipFile(zip_artifact, "w") as archive:
        archive.writestr("manifest.json", '{"status": "passed"}\n')
    parquet_artifact.write_bytes(b"PAR1minimal-footerPAR1")

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "synthetic",
                "artifacts": [
                    str(json_artifact),
                    str(png_artifact),
                    str(zip_artifact),
                    str(parquet_artifact),
                ],
                "steps": [
                    {
                        "id": "write-evidence",
                        "produces": [
                            str(json_artifact),
                            str(png_artifact),
                            str(zip_artifact),
                            str(parquet_artifact),
                        ],
                    }
                ],
            }
        ]
    )

    assert report["verified_count"] == 1
    assert report["failed_count"] == 0
    assert report["artifact_count"] == 4
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


@pytest.mark.parametrize(
    ("filename", "payload", "expected"),
    [
        ("web-results.png", b"\x89PNG\r\n\x1a\n", "missing PNG IHDR chunk"),
        ("paper-export.zip", b"not a zip", "invalid ZIP archive"),
        ("predictions.parquet", b"not parquet", "invalid Parquet magic bytes"),
    ],
)
def test_cross_language_e2e_artifact_evidence_report_rejects_invalid_typed_artifacts(
    tmp_path: Path,
    filename: str,
    payload: bytes,
    expected: str,
) -> None:
    e2e = _load_e2e_module()
    artifact = tmp_path / filename
    artifact.write_bytes(payload)

    report = e2e.artifact_evidence_report(
        [
            {
                "id": "synthetic",
                "artifacts": [str(artifact)],
                "steps": [
                    {
                        "id": "write-evidence",
                        "produces": [str(artifact)],
                    }
                ],
            }
        ]
    )

    assert report["verified_count"] == 0
    assert report["failed_count"] == 1
    assert expected in "\n".join(report["scenarios"]["synthetic"]["failures"])


def test_cross_language_e2e_cli_evidence_json_selected_scenario(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    e2e = _load_e2e_module()
    manifest = e2e.validate_scenarios(MANIFEST)
    scenario = _scenario_by_id(manifest, "e2e-r-dataset-io-pipeline-save")
    artifacts_dir = tmp_path / "artifacts"
    report_path = tmp_path / "evidence-summary.json"

    for raw_path in scenario["artifacts"]:
        path = Path(raw_path.format(workspace_root=tmp_path, artifacts_dir=artifacts_dir))
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(path, _synthetic_evidence_payload(path))

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
            "--json-out",
            str(report_path),
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
    assert json.loads(report_path.read_text(encoding="utf-8")) == report

    archived_artifact = Path(
        scenario["artifacts"][0].format(workspace_root=tmp_path, artifacts_dir=artifacts_dir)
    )
    os.utime(archived_artifact, (1, 1))
    stale = subprocess.run(
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
            "--max-age-seconds",
            "60",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert stale.returncode == 1
    assert "failed" in stale.stdout
    assert "stale artifact age=" in stale.stdout

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


def test_cross_language_e2e_cli_evidence_ready_only_skips_blocked_scenarios(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    manifest = _read_manifest()
    ready_scenario = manifest["scenarios"][1]
    ready_id = ready_scenario["id"]
    blocked_ids = {scenario["id"] for scenario in manifest["scenarios"] if scenario["id"] != ready_id}
    workspace_root = tmp_path / "workspace"
    artifacts_dir = tmp_path / "artifacts"
    missing_path = tmp_path / "missing-public-dataset.json"
    workspace_root.mkdir()
    artifacts_dir.mkdir()

    for step in ready_scenario["steps"]:
        step["requires_tools"] = [sys.executable]
        step["requires_env"] = []
        step["requires_paths"] = []
    for scenario in manifest["scenarios"]:
        if scenario["id"] == ready_id:
            continue
        for step in scenario["steps"]:
            step["requires_paths"] = [*step.get("requires_paths", []), str(missing_path)]

    for raw_path in ready_scenario["artifacts"]:
        artifact = Path(raw_path.format(workspace_root=workspace_root, artifacts_dir=artifacts_dir))
        artifact.parent.mkdir(parents=True, exist_ok=True)
        payload = _synthetic_evidence_payload(artifact)
        if artifact.suffix == ".zip":
            with zipfile.ZipFile(artifact, "w") as archive:
                archive.writestr("evidence.json", json.dumps(payload))
            continue
        if artifact.suffix == ".png":
            artifact.write_bytes(
                b"\x89PNG\r\n\x1a\n"
                b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                b"\x08\x02\x00\x00\x00\x90wS\xde"
                b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00"
                b"\x18\xdd\x8d\xb0"
                b"\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            continue
        artifact.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    verified = subprocess.run(
        [
            sys.executable,
            str(script),
            "--manifest",
            str(manifest_path),
            "--workspace-root",
            str(workspace_root),
            "--artifacts-dir",
            str(artifacts_dir),
            "evidence",
            "--ready-only",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    report = json.loads(verified.stdout)

    assert report["scenario_count"] == 1
    assert report["verified_count"] == 1
    assert set(report["scenarios"]) == {ready_id}
    assert blocked_ids.isdisjoint(report["scenarios"])

    incompatible = subprocess.run(
        [
            sys.executable,
            str(script),
            "--manifest",
            str(manifest_path),
            "evidence",
            "--scenario",
            ready_id,
            "--ready-only",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert incompatible.returncode == 1
    assert "--ready-only cannot be combined with --scenario" in incompatible.stderr


def test_cross_language_e2e_cli_evidence_ready_only_rejects_empty_ready_set(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    manifest = _read_manifest()
    workspace_root = tmp_path / "workspace"
    artifacts_dir = tmp_path / "artifacts"
    missing_path = tmp_path / "missing-public-dataset.json"
    workspace_root.mkdir()
    artifacts_dir.mkdir()

    for scenario in manifest["scenarios"]:
        for step in scenario["steps"]:
            step["requires_paths"] = [*step.get("requires_paths", []), str(missing_path)]

    manifest_path = tmp_path / "scenarios.json"
    _write_json(manifest_path, manifest)

    empty = subprocess.run(
        [
            sys.executable,
            str(script),
            "--manifest",
            str(manifest_path),
            "--workspace-root",
            str(workspace_root),
            "--artifacts-dir",
            str(artifacts_dir),
            "evidence",
            "--ready-only",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert empty.returncode == 1
    assert "--ready-only matched no ready scenarios" in empty.stderr


def test_cross_language_e2e_cli_fails_when_declared_artifact_is_missing(tmp_path: Path) -> None:
    script = ROOT / "scripts" / "n4a_e2e_scenarios.py"
    manifest = _read_manifest()
    scenario_id = manifest["scenarios"][0]["id"]
    manifest["scenarios"][0]["languages"] = ["python", "native"]
    manifest["scenarios"][0]["tags"] = [
        tag for tag in manifest["scenarios"][0]["tags"] if tag != "parity"
    ]
    ok_artifact = tmp_path / "ok-cli-result.json"
    extra_artifact = tmp_path / "extra-cli-result.json"
    missing_artifact = tmp_path / "missing-cli-result.json"
    manifest["scenarios"][0]["artifacts"] = [str(ok_artifact), str(missing_artifact)]
    for check in manifest["scenarios"][0]["parity_checks"]:
        check["evidence_level"] = "contract"
        check["artifacts"] = [str(ok_artifact)]
    for phase in manifest["v1_refactor_contract"]["scenario_coverage"][scenario_id].values():
        phase["artifacts"] = []
    manifest["scenarios"][0]["steps"] = [
        {
                "id": "write-cli-step",
                "title": "Command writes one declared artifact",
                "kind": "prepare",
                "repo": "nirs4all-ecosystem",
                "requires_tools": [sys.executable],
                "requires_paths": [],
                "command": [
                    sys.executable,
                    "-c",
                        (
                            "import json; "
                            "from pathlib import Path; "
                            "payload=json.dumps(dict(status='passed', ok=True))+'\\n'; "
                            f"Path({str(ok_artifact)!r}).write_text(payload); "
                            f"Path({str(extra_artifact)!r}).write_text(payload)"
                        ),
                    ],
                "produces": [str(ok_artifact), str(extra_artifact)],
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
            step["requires_tools"] = (
                ["Rscript"] if "Rscript" in step.get("requires_tools", []) else []
            )
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
    assert summary["v1_refactor_summary"]["e2e-wasm-open-repo-pipeline-alt-dataset"]["gap"] == 0
    assert summary["v1_refactor_summary"]["e2e-wasm-open-repo-pipeline-alt-dataset"]["not_applicable"] == 1
    assert (
        summary["v1_refactor_summary"]["e2e-python-reopen-paper-repository-refit"]["strict"]
        == 5
    )
    assert "Dry run only" in planned.stderr
