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
    "CORE-001", "STU-003", "CUT-001", "CUT-002", "CUT-003",
    "DROP-001", "DROP-002", "DROP-003", "DROP-004", "DROP-005", "SUP-001",
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
    assert items["PERF-001"]["state"] == "pending"
    assert items["PERF-001"]["review"] == "pending"


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
    assert evidence["python_strict_profile"]["commit"] == "e227244464983ea2a94ebc01b6af30d474a025df"
    assert evidence["core"]["commit"] == "e0f5d485eae4279f02d58fe82fad3946202e463f"
    assert evidence["io"]["commit"] == "e41bf8f94a92356e98c215d4c41e907a7dfaf6ac"
    assert evidence["canonical_release_lock"]["updated"] is False
    assert all(
        value == "pending" or value.startswith("no_go")
        for value in ledger["locks"].values()
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
