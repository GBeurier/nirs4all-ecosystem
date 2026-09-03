from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/contracts/release/migration-work-ledger.yaml"
INVENTORY = ROOT / "docs/contracts/release/r3-rc-triage-inventory.v1.json"
REPORT = ROOT / "docs/contracts/release/r3-rc-triage-report.md"


def _load_validator() -> ModuleType:
    path = ROOT / "scripts/n4a_r3_rc_triage.py"
    spec = importlib.util.spec_from_file_location("n4a_r3_rc_triage", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _inventory() -> dict:
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


def _write_inventory(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def test_committed_inventory_and_report_match_the_ledger() -> None:
    validator = _load_validator()
    inventory = validator.validate_inventory(LEDGER, INVENTORY, REPORT)

    assert inventory["work_item_count"] == 11
    assert [lot["id"] for lot in inventory["lots"]] == list(
        validator._load_migration_validator().ROADMAP_PHASE_WORK_ITEMS["r3"]
    )
    assert inventory["summary"] == {
        "closed_local": 6,
        "advanced_not_closed": 4,
        "pending": 1,
        "release_eligible": False,
        "external_evidence_hold": True,
    }
    assert "not an R3 or RC-001 closure" in REPORT.read_text(encoding="utf-8")


def test_validator_refuses_omitted_and_duplicate_r3_lots(tmp_path: Path) -> None:
    validator = _load_validator()
    inventory = _inventory()

    omitted = copy.deepcopy(inventory)
    omitted["lots"] = omitted["lots"][:-1]
    omitted_path = tmp_path / "omitted.json"
    _write_inventory(omitted_path, omitted)
    with pytest.raises(validator.R3TriageError, match="missing R3 lots"):
        validator.validate_inventory(LEDGER, omitted_path, REPORT)

    duplicated = copy.deepcopy(inventory)
    duplicated["lots"].append(copy.deepcopy(duplicated["lots"][0]))
    duplicate_path = tmp_path / "duplicate.json"
    _write_inventory(duplicate_path, duplicated)
    with pytest.raises(validator.R3TriageError, match="duplicate R3 lots"):
        validator.validate_inventory(LEDGER, duplicate_path, REPORT)


@pytest.mark.parametrize("field", ["state", "input_sha", "disposition"])
def test_validator_refuses_lot_field_drift(tmp_path: Path, field: str) -> None:
    validator = _load_validator()
    inventory = _inventory()
    inventory["lots"][0][field] = "drifted"
    path = tmp_path / f"drift-{field}.json"
    _write_inventory(path, inventory)

    with pytest.raises(validator.R3TriageError, match="drifted from the migration ledger"):
        validator.validate_inventory(LEDGER, path, REPORT)


def test_validator_refuses_non_r3_lot_and_report_drift(tmp_path: Path) -> None:
    validator = _load_validator()
    inventory = _inventory()
    inventory["lots"][-1]["id"] = "RC-001"
    inventory_path = tmp_path / "unexpected.json"
    _write_inventory(inventory_path, inventory)
    with pytest.raises(validator.R3TriageError, match="missing R3 lots"):
        validator.validate_inventory(LEDGER, inventory_path, REPORT)

    report_path = tmp_path / "report.md"
    report_path.write_text(REPORT.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
    with pytest.raises(validator.R3TriageError, match="report drifted"):
        validator.validate_inventory(LEDGER, INVENTORY, report_path)


def test_builder_refuses_to_treat_rc001_as_closed(tmp_path: Path) -> None:
    validator = _load_validator()
    migration = validator._load_migration_validator()
    ledger = migration.validate_ledger(LEDGER)
    next(item for item in ledger["work_items"] if item["id"] == "RC-001")["state"] = "complete"
    ledger_path = tmp_path / "ledger.yaml"

    import yaml

    ledger_path.write_text(yaml.safe_dump(ledger, sort_keys=False), encoding="utf-8")
    with pytest.raises(validator.R3TriageError, match="cannot close it"):
        validator.build_inventory(ledger_path)
