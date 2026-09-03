from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/contracts/governance/ownership-ledger.v1.json"


def _load_validator() -> ModuleType:
    path = ROOT / "scripts/n4a_ownership_ledger.py"
    spec = importlib.util.spec_from_file_location("n4a_ownership_ledger", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _valid_handoff() -> dict:
    return {
        "schema_version": "n4a.ownership-handoff/v1",
        "source_lane": "C",
        "target_lane": "E",
        "repositories": ["dag-ml-data"],
        "from_sha": "1" * 40,
        "to_sha": "2" * 40,
        "tests": ["python3 scripts/validate_contracts.py: passed"],
        "rollback": "Revert the handoff commit and restore the prior schema.",
        "artifact_classes": ["schemas"],
        "arbitration_ids": ["repo.dag-ml-data.lane-overlap"],
    }


def test_ownership_ledger_is_exhaustive_and_assigns_existing_release_authority() -> None:
    validator = _load_validator()

    ledger = validator.validate_ledger(LEDGER)

    assert {lane["id"] for lane in ledger["lanes"]} == set("ABCDEFGH")
    assert {repository["key"] for repository in ledger["repositories"]} == validator._required_repository_keys()
    captain = ledger["release_captain"]
    assert captain["status"] == "assigned-existing-authority"
    assert captain["identity_ref"] == "github:GBeurier"
    assert captain["pending_choice"] is None
    assert ledger["remote_authority"]["team_slugs"] == []


def test_validator_refuses_an_in_scope_repository_without_owner(tmp_path: Path) -> None:
    validator = _load_validator()
    payload = _read_ledger()
    payload["repositories"].pop()
    path = tmp_path / "ledger.json"
    _write(path, payload)

    with pytest.raises(validator.OwnershipLedgerError, match="no owner row"):
        validator.validate_ledger(path)


def test_validator_refuses_unarbitrated_lane_overlap(tmp_path: Path) -> None:
    validator = _load_validator()
    payload = _read_ledger()
    repository = next(
        item for item in payload["repositories"] if item["key"] == "nirs4all-studio"
    )
    repository["arbitration"] = None
    path = tmp_path / "ledger.json"
    _write(path, payload)

    with pytest.raises(validator.OwnershipLedgerError, match="must be an object"):
        validator.validate_ledger(path)


def test_validator_refuses_an_unregistered_approver(tmp_path: Path) -> None:
    validator = _load_validator()
    payload = _read_ledger()
    payload["lanes"][0]["accountable_identity_refs"] = ["github:invented"]
    path = tmp_path / "ledger.json"
    _write(path, payload)

    with pytest.raises(validator.OwnershipLedgerError, match="unknown identities"):
        validator.validate_ledger(path)


def test_handoff_requires_full_shas_tests_and_rollback() -> None:
    validator = _load_validator()
    ledger = validator.validate_ledger(LEDGER)
    validator.validate_handoff(_valid_handoff(), ledger)

    mutations = {
        "from_sha": "short",
        "tests": [],
        "rollback": "too short",
    }
    for field, value in mutations.items():
        payload = copy.deepcopy(_valid_handoff())
        payload[field] = value
        with pytest.raises(validator.OwnershipLedgerError):
            validator.validate_handoff(payload, ledger)


def test_handoff_refuses_missing_sha_tests_or_rollback() -> None:
    validator = _load_validator()
    ledger = validator.validate_ledger(LEDGER)
    for field in ("from_sha", "to_sha", "tests", "rollback"):
        payload = _valid_handoff()
        payload.pop(field)
        with pytest.raises(validator.OwnershipLedgerError, match="missing required fields"):
            validator.validate_handoff(payload, ledger)
