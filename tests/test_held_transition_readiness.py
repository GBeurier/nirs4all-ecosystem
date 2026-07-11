from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "docs" / "contracts" / "release" / "held-transition-readiness.n4a.json"


def _readiness() -> dict:
    return json.loads(READINESS.read_text(encoding="utf-8"))


def test_held_transition_readiness_schema_and_projects() -> None:
    data = _readiness()

    assert data["schema_version"] == "n4a.held-transition-readiness/v1"
    assert data["policy"]["production_switch_allowed"] is False
    assert set(data["policy"]["held_projects"]) == {"nirs4all", "nirs4all-studio"}

    projects = {project["id"]: project for project in data["projects"]}
    assert projects["nirs4all"]["production_status"] == "held"
    assert projects["nirs4all"]["current_production_version"] == "0.10.3"
    assert projects["nirs4all"]["transition_branch"] == "refactor/L17-pyref"
    assert projects["nirs4all"]["transition_head"] == "f6c201153b3921c0f214cd63a992beb29e10b7bc"

    assert projects["nirs4all-studio"]["production_status"] == "held"
    assert projects["nirs4all-studio"]["current_production_version"] == "0.9.1"
    assert projects["nirs4all-studio"]["current_main_head"] == "8654e4d24c22553717e08d6f646f423c02bf4667"
    assert projects["nirs4all-studio"]["current_rc_installer_version"] == "1.0.0-rc.4"


def test_automated_gates_are_green_but_manual_gates_block_prod_switch() -> None:
    data = _readiness()

    automated = {gate["id"]: gate for gate in data["automated_gates"]}
    assert {gate["status"] for gate in automated.values()} == {"passed"}
    assert automated["PYTHON-PREPUBLISH-TRANSITION"]["run_id"] == 29146982675
    assert automated["PYTHON-PREPUBLISH-TRANSITION"]["head"]["sha"] == "f6c201153b3921c0f214cd63a992beb29e10b7bc"
    assert automated["STUDIO-RC4-INSTALLERS"]["run_id"] == 29145157945
    assert automated["STUDIO-RC4-INSTALLERS"]["release_created"] is False
    assert automated["STUDIO-RC4-INSTALLERS"]["inputs"] == {
        "tag": "1.0.0-rc.4",
        "skip_all_in_one": True,
        "skip_docker": True,
    }
    assert {artifact["name"] for artifact in automated["STUDIO-RC4-INSTALLERS"]["artifacts"]} == {
        "installer-windows-x64",
        "installer-linux-x64",
        "installer-macos-x64",
        "installer-macos-arm64",
    }

    manual = {gate["id"]: gate for gate in data["manual_gates"]}
    assert manual["STUDIO-WINDOWS-RC4-SMOKE"]["status"] == "pending"
    assert manual["HELD-PROJECT-PUBLISH-DECISION"]["status"] == "pending"
    assert all(gate["required_before_production_switch"] for gate in manual.values())

    completion = data["completion_state"]
    assert completion["automated_readiness"] == "passed"
    assert completion["manual_readiness"] == "pending"
    assert completion["production_switch_allowed"] is False
