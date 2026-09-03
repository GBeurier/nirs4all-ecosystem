#!/usr/bin/env python3
"""Build and validate the bounded R3 inventory used to prepare RC-001 triage."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "docs/contracts/release/migration-work-ledger.yaml"
DEFAULT_INVENTORY = ROOT / "docs/contracts/release/r3-rc-triage-inventory.v1.json"
DEFAULT_REPORT = ROOT / "docs/contracts/release/r3-rc-triage-report.md"
SCHEMA_VERSION = "n4a.r3-rc-triage-inventory/v1"
DISPOSITIONS = ("closed_local", "advanced_not_closed", "pending")
PREPARED_RC001_STATE = "prepared_local_triage_external_evidence_hold"


class R3TriageError(RuntimeError):
    """Raised when the R3 triage inventory is incomplete or stale."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise R3TriageError(message)


def _load_migration_validator() -> ModuleType:
    path = ROOT / "scripts/n4a_migration_work_ledger.py"
    spec = importlib.util.spec_from_file_location("n4a_migration_work_ledger", path)
    _require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _disposition(state: str) -> str:
    if state.startswith("complete_local"):
        return "closed_local"
    if state.startswith("advanced_local") or state.startswith("prepared_local"):
        return "advanced_not_closed"
    if state == "pending":
        return "pending"
    raise R3TriageError(f"R3 state has no triage disposition: {state!r}")


def _projection_digest(lots: list[dict[str, str]]) -> str:
    payload = json.dumps(lots, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_inventory(ledger_path: Path) -> tuple[dict[str, Any], str]:
    validator = _load_migration_validator()
    ledger = validator.validate_ledger(ledger_path)
    r3_ids = tuple(validator.ROADMAP_PHASE_WORK_ITEMS["r3"])
    _require(len(r3_ids) == 11, "the reviewed roadmap must contain exactly 11 R3 lots")
    _require(len(r3_ids) == len(set(r3_ids)), "the reviewed R3 lot list contains duplicates")

    items = {item["id"]: item for item in ledger["work_items"]}
    missing = [work_item_id for work_item_id in r3_ids if work_item_id not in items]
    _require(not missing, f"ledger is missing R3 lots: {missing}")

    lots = [
        {
            "id": work_item_id,
            "state": items[work_item_id]["state"],
            "input_sha": items[work_item_id]["input_sha"],
            "disposition": _disposition(items[work_item_id]["state"]),
        }
        for work_item_id in r3_ids
    ]
    counts = Counter(lot["disposition"] for lot in lots)
    inventory = {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "ledger": "docs/contracts/release/migration-work-ledger.yaml",
            "roadmap_source_sha256": ledger["roadmap_coverage"]["source_sha256"],
        },
        "release": "R3",
        "work_item_count": len(lots),
        "projection_sha256": _projection_digest(lots),
        "lots": lots,
        "summary": {
            disposition: counts.get(disposition, 0)
            for disposition in DISPOSITIONS
        }
        | {
            "release_eligible": False,
            "external_evidence_hold": True,
        },
    }
    rc001 = items["RC-001"]
    _require(
        rc001["state"] in {"pending", PREPARED_RC001_STATE},
        "RC-001 must remain pending or prepared; this inventory cannot close it",
    )
    return inventory, rc001["state"]


def render_markdown(inventory: dict[str, Any], rc001_state: str) -> str:
    summary = inventory["summary"]
    lines = [
        "# R3 inventory for RC-001 triage",
        "",
        "This report is a local triage input, not an R3 or RC-001 closure.",
        "",
        f"- RC-001 state: `{rc001_state}`",
        f"- R3 lots: {inventory['work_item_count']}",
        f"- Closed locally: {summary['closed_local']}",
        f"- Advanced but not closed: {summary['advanced_not_closed']}",
        f"- Pending: {summary['pending']}",
        "- Release eligibility: **NO-GO** — external evidence remains required.",
        "",
        "| Lot | State | Input SHA | Disposition |",
        "|---|---|---|---|",
    ]
    lines.extend(
        f"| `{lot['id']}` | `{lot['state']}` | `{lot['input_sha']}` | `{lot['disposition']}` |"
        for lot in inventory["lots"]
    )
    return "\n".join(lines) + "\n"


def _read_inventory(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise R3TriageError(f"cannot read inventory {path}: {exc}") from exc
    _require(isinstance(value, dict), "inventory root must be an object")
    return value


def validate_inventory(ledger_path: Path, inventory_path: Path, report_path: Path) -> dict[str, Any]:
    expected, rc001_state = build_inventory(ledger_path)
    actual = _read_inventory(inventory_path)

    lots = actual.get("lots")
    _require(isinstance(lots, list), "inventory.lots must be a list")
    ids = [lot.get("id") for lot in lots if isinstance(lot, dict)]
    _require(len(ids) == len(lots), "every inventory lot must be an object with an id")
    duplicates = sorted(work_item_id for work_item_id, count in Counter(ids).items() if count > 1)
    _require(not duplicates, f"duplicate R3 lots: {duplicates}")
    expected_ids = [lot["id"] for lot in expected["lots"]]
    missing = [work_item_id for work_item_id in expected_ids if work_item_id not in ids]
    unexpected = [work_item_id for work_item_id in ids if work_item_id not in expected_ids]
    _require(not missing, f"inventory is missing R3 lots: {missing}")
    _require(not unexpected, f"inventory has non-R3 lots: {unexpected}")
    _require(actual == expected, "R3 inventory drifted from the migration ledger")

    try:
        report = report_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise R3TriageError(f"cannot read report {report_path}: {exc}") from exc
    _require(report == render_markdown(expected, rc001_state), "R3 triage report drifted from the inventory")
    return expected


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "validate"))
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.command == "build":
            inventory, rc001_state = build_inventory(args.ledger.resolve())
            args.inventory.parent.mkdir(parents=True, exist_ok=True)
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.inventory.write_text(
                json.dumps(inventory, indent=2, sort_keys=False) + "\n",
                encoding="utf-8",
            )
            args.report.write_text(render_markdown(inventory, rc001_state), encoding="utf-8")
            print(f"wrote {args.inventory} and {args.report}")
        else:
            inventory = validate_inventory(
                args.ledger.resolve(), args.inventory.resolve(), args.report.resolve()
            )
            print(f"validated {len(inventory['lots'])} R3 lots")
    except R3TriageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
