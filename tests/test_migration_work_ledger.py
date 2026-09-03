from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/contracts/release/migration-work-ledger.yaml"
PREVIOUSLY_MISSING_ROADMAP_IDS = {
    "DATA-002", "CORE-001", "STU-003", "REL-003", "WEBREL-001", "DAG-001",
    "PERF-001", "CUT-001", "CUT-002", "CUT-003", "DOC-001", "WEBREL-002",
    "DROP-001", "DROP-002", "DROP-003", "DROP-004", "DROP-005", "SOAK-001",
    "SEC-001", "PERF-002", "INST-001", "SUP-001", "WEBREL-003", "RC-001",
    "RC-002", "DOC-002", "SUP-002", "REL-004", "WEBREL-004",
}
LOCAL_CODE_OR_SUPPORT_CLOSURES = {
    "CORE-001", "STU-003", "REL-003", "DAG-001", "CUT-001", "CUT-002",
    "CUT-003", "DOC-001",
    "DROP-001", "DROP-002", "DROP-003", "DROP-004", "DROP-005", "SUP-001",
}
CAP_SCOPED_LOCAL_CLOSURES = {
    "DATA-003", "SAVE-002", "API-001", "API-002", "API-003", "API-004",
    "API-005", "PAR-002",
}


def _load_validator() -> ModuleType:
    path = ROOT / "scripts/n4a_migration_work_ledger.py"
    spec = importlib.util.spec_from_file_location("n4a_migration_work_ledger", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_ledger() -> dict:
    payload = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _write_ledger(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_ledger_covers_every_reviewed_phase_0_to_r4_roadmap_lot() -> None:
    validator = _load_validator()

    ledger = validator.validate_ledger(LEDGER)
    items = {item["id"]: item for item in ledger["work_items"]}

    assert len(validator.ROADMAP_WORK_ITEMS) == 66
    assert {phase: len(ids) for phase, ids in validator.ROADMAP_PHASE_WORK_ITEMS.items()} == {
        "phase_0": 7,
        "r1": 24,
        "r2": 18,
        "r3": 11,
        "r4": 6,
    }
    assert set(validator.ROADMAP_WORK_ITEMS) <= set(items)
    assert len(PREVIOUSLY_MISSING_ROADMAP_IDS) == 29
    assert PREVIOUSLY_MISSING_ROADMAP_IDS <= set(items)
    assert all(
        isinstance(items[work_item_id]["state"], str)
        for work_item_id in PREVIOUSLY_MISSING_ROADMAP_IDS
    )
    assert all(
        isinstance(items[work_item_id]["review"], str)
        for work_item_id in PREVIOUSLY_MISSING_ROADMAP_IDS
    )
    assert items["DATA-002"]["state"] == "complete_local_code_release_hold"
    assert all(items[work_item_id]["state"].startswith("complete_local") for work_item_id in LOCAL_CODE_OR_SUPPORT_CLOSURES)
    assert all(
        items[work_item_id]["state"].startswith("complete_local")
        for work_item_id in CAP_SCOPED_LOCAL_CLOSURES
    )
    assert items["PERF-001"]["state"] == "complete_local_measurement_release_hold"
    assert items["DOC-002"]["state"] == "prepared_local_docs_release_hold"
    assert all(
        items[work_item_id]["state"] == "advanced_local_evidence_not_closed"
        for work_item_id in {"SOAK-001", "PERF-002"}
    )
    assert items["SEC-001"]["state"] == "prepared_local_native_fuzz_harnesses_campaign_not_closed"


def test_coverage_is_inventory_only_and_does_not_claim_release_readiness() -> None:
    ledger = _read_ledger()
    items = {item["id"]: item for item in ledger["work_items"]}

    assert ledger["roadmap_coverage"]["exhaustive_for_source_work_lots"] is True
    semantics = ledger["roadmap_coverage"]["status_semantics"]
    assert "does not mean" in semantics
    assert "completion" in semantics
    assert "publication" in semantics
    assert items["CAP-001"]["state"] == "complete"
    assert "bijectively mapped" in items["CAP-001"]["review"]
    assert items["GOV-001"]["state"] == "complete"
    assert items["DOC-WEB-001"]["state"] == "complete_local_staging_publication_hold"
    assert items["DOC-WEB-001B"]["state"] == "complete_local_staging_publication_hold"
    evidence = ledger["current_candidate_evidence"]
    assert evidence["methods"]["commit"] == "e0bee1ce160cd805d3060185fd151c09230c3381"
    assert evidence["dag_ml_data"]["commit"] == "7d9b9fed04c135ed4c2bba472c782aca7ef85807"
    assert evidence["dag_ml"]["commit"] == "1caa26dc9b90f33bc3f53b15b4d85e18f3f67381"
    assert evidence["python_strict_profile"]["commit"] == "53a0acb964bff86dc67002763d8e9b850336731f"
    assert evidence["python_strict_profile"]["r3_direct_parent"] == "1de9dcb50fcdcc6273113f54a7c7235528c31ed8"
    assert evidence["core"]["commit"] == "89787477bd7883ceb26b51fa3228bca13db85f6e"
    assert evidence["core"]["version"] == "0.3.27"
    assert evidence["io"]["commit"] == "df7f2198862c71a24aeeba08ba09ee118524b55d"
    assert evidence["io"]["publication_repair_commit"] == "a5f7eac50126d445f745f945ff5c770ed470254c"
    assert evidence["datasets"]["commit"] == "007d7aafe50e6e4148d5a5cefe0ad96d9da37e7b"
    assert evidence["datasets"]["product_commit"] == "285d8df2a6701e870566f66c931438b8fdf04ffb"
    assert evidence["datasets"]["release_tag_move_count"] == 1
    assert evidence["tools"]["commit"] == "88c2bc1e29603049cdbf1a1080a35845edf2f3c9"
    assert evidence["tools"]["support_matrix_sha256"] == "85031fd02b89c16f7adc90e1faad4843cd654f0279c48332d58af3ad6b37a65b"
    assert evidence["ui"]["commit"] == "406d94d70004f27459ef12347af1e6f0079ab6ac"
    assert evidence["ui"]["tarball_sha256"] == "44ba22aef663548f426518ada8478a5c461e96dd5592cf2691b68776c42b9a67"
    assert evidence["studio"]["candidate_commit"] == "f8e9da2ecc71a1207f92a19a1aec0535a69c02d7"
    assert evidence["studio"]["published"] is False
    assert evidence["studio"]["signed"] is False
    assert evidence["web"]["candidate_commit"] == "051bf636d7c1729087e5d40061b18bd690cd33b7"
    assert evidence["web"]["published"] is True
    assert evidence["web"]["pages_published"] is True
    assert evidence["benchmarks"]["commit"] == "9ff889a5be1bbc48a16d69a27ab743c23598f7da"
    assert evidence["security_harnesses"]["formats"]["commit"] == "892a48b38f6c94697f805524f6efd4e8ff7323b0"
    assert evidence["security_harnesses"]["core"]["commit"] == "0218bfc8b9d9193f771d27470e7cf9d5cf578823"
    assert evidence["security_harnesses"]["methods"]["commit"] == "530b11c632ac467e6bf54022c7241d27cd72d73c"
    assert evidence["security_harnesses"]["studio_store"]["commit"] == "6d53f301830947ff85767c53c800829741af75ff"
    assert evidence["org"]["commit"] == "b09f2768f264269d72be351d0c6282b769ec8f85"
    assert evidence["cockpit"]["commit"] == "0abde191e91629d4d54d111f93805508de9a6639"
    assert evidence["remote_candidate_staging"]["status"] == "components_r1_and_web_published_r2_r3_and_studio_unpublished"
    assert evidence["remote_candidate_staging"]["tag_or_registry_publication"] is True
    assert evidence["remote_candidate_staging"]["all_product_milestones_published"] is False
    assert len(evidence["remote_candidate_staging"]["heads"]) == 15
    assert evidence["product_release_sequence"]["status"] == "r1_r2_r3_distinct_remote_candidates_r4_held"
    assert evidence["product_release_sequence"]["milestones"]["r1"]["default_engine"] == "legacy"
    assert evidence["product_release_sequence"]["milestones"]["r1"]["publication_repair_commit"] == "e76c834c75157f0c74fcbba7383a69a818ed6b34"
    assert evidence["product_release_sequence"]["milestones"]["r1"]["pypi_published"] is True
    assert evidence["product_release_sequence"]["milestones"]["r1"]["ghcr_published"] is True
    assert evidence["product_release_sequence"]["milestones"]["r2"]["studio_commit"] == "54350c688ae576bbbb393c5a24dae8d106f77322"
    assert evidence["product_release_sequence"]["milestones"]["r3"]["version"] == "1.0.0rc2"
    assert items["UI-001"]["state"] == "complete_registry_publication_downstream_product_hold"
    assert items["STU-006"]["state"] == "complete_local_code_external_release_hold"
    assert items["GATE-001"]["state"] == "complete_local_linux_functional_release_hold"
    assert items["STORE-002"]["state"] == "complete_local_code_release_hold"
    assert items["STU-005"]["state"] == "complete_local_code_release_hold"
    assert items["WEBREL-002"]["state"] == "prepared_local_docs_installer_publication_hold"
    assert items["WEBREL-003"]["state"] == "prepared_local_docs_installer_publication_hold"
    assert items["WEBREL-001"]["state"] == "complete_local_staging_publication_hold"
    assert items["INST-001"]["state"] == "prepared_local_linux_harness_external_matrix_hold"
    assert items["SUP-002"]["state"] == "complete_local_support_matrix_external_publication_hold"
    assert evidence["canonical_release_lock"]["updated"] is False
    assert ledger["locks"]["LOCK-ARCH"].startswith("closed_")
    assert all(
        value == "pending" or value.startswith("no_go")
        for key, value in ledger["locks"].items()
        if key != "LOCK-ARCH"
    )
    assert ledger["locks"]["LOCK-RELEASE"].startswith("no_go")


def test_validator_refuses_a_missing_roadmap_lot(tmp_path: Path) -> None:
    validator = _load_validator()
    ledger = _read_ledger()
    ledger["work_items"] = [item for item in ledger["work_items"] if item["id"] != "WEBREL-004"]
    path = tmp_path / "ledger.yaml"
    _write_ledger(path, ledger)

    with pytest.raises(validator.MigrationWorkLedgerError, match="missing roadmap work lots"):
        validator.validate_ledger(path)


def test_validator_refuses_an_unclassified_supplemental_lot(tmp_path: Path) -> None:
    validator = _load_validator()
    ledger = _read_ledger()
    ledger["roadmap_coverage"]["supplemental_work_items"] = [
        entry
        for entry in ledger["roadmap_coverage"]["supplemental_work_items"]
        if entry["id"] != "CORE-002"
    ]
    path = tmp_path / "ledger.yaml"
    _write_ledger(path, ledger)

    with pytest.raises(validator.MigrationWorkLedgerError, match="unclassified supplemental work items"):
        validator.validate_ledger(path)


def test_validator_refuses_dangling_and_cyclic_dependencies(tmp_path: Path) -> None:
    validator = _load_validator()
    dangling = _read_ledger()
    next(item for item in dangling["work_items"] if item["id"] == "RC-002")["dependencies"] = ["MISSING-001"]
    path = tmp_path / "dangling.yaml"
    _write_ledger(path, dangling)
    with pytest.raises(validator.MigrationWorkLedgerError, match="unknown dependencies"):
        validator.validate_ledger(path)

    cyclic = _read_ledger()
    next(item for item in cyclic["work_items"] if item["id"] == "ARCH-001")["dependencies"] = ["WEBREL-004"]
    cycle_path = tmp_path / "cycle.yaml"
    _write_ledger(cycle_path, cyclic)
    with pytest.raises(validator.MigrationWorkLedgerError, match="dependency cycle"):
        validator.validate_ledger(cycle_path)


def test_validator_refuses_ambiguous_done_without_reclassifying_existing_evidence(tmp_path: Path) -> None:
    validator = _load_validator()
    ledger = copy.deepcopy(_read_ledger())
    next(item for item in ledger["work_items"] if item["id"] == "RC-001")["state"] = "done"
    path = tmp_path / "ledger.yaml"
    _write_ledger(path, ledger)

    with pytest.raises(validator.MigrationWorkLedgerError, match="ambiguous done"):
        validator.validate_ledger(path)
