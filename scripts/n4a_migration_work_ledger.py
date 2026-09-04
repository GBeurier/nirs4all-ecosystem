#!/usr/bin/env python3
"""Validate roadmap coverage and dependency integrity of the V1 work ledger.

The source roadmap is maintained at the ecosystem workspace root rather than
inside this repository.  This validator therefore freezes both its reviewed
SHA-256 and its 66 Phase-0/R1/R2/R3/R4 work-lot identifiers.  Coverage is an
inventory assertion only: it never promotes a pending lot or a release gate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


LEDGER_SCHEMA_VERSION = "n4a.migration-work-ledger/v1"
DEFAULT_LEDGER = Path("docs/contracts/release/migration-work-ledger.yaml")
ROADMAP_SOURCE_LABEL = "ROADMAP_BACKEND_NATIF_V1.md"
ROADMAP_SOURCE_SHA256 = "cd63adb6a915f851d947ab471c8abbbdd51c5c9f4312e53fcd8906901c083e79"
ROADMAP_PHASE_WORK_ITEMS = {
    "phase_0": (
        "ARCH-001", "ARCH-002", "REL-001", "REL-002", "PAR-001",
        "CAP-001", "GOV-001",
    ),
    "r1": (
        "SAVE-001", "PAR-002", "STU-001", "DATA-001", "MTH-001",
        "MTH-002", "MTH-003", "MTH-DOC-001", "MTH-DOC-002", "DATA-002",
        "DATA-003", "IO-XLG-001", "CONF-001", "FMT-001", "CORE-001",
        "STU-002", "GATE-001", "SAVE-002", "SAVE-003", "SAVE-004",
        "STU-003", "REL-003", "MTH-DOC-003", "WEBREL-001",
    ),
    "r2": (
        "API-001", "API-002", "API-003", "API-004", "API-005", "DAG-001",
        "HPO-001", "STU-004", "STU-005", "STU-006", "UI-001", "WEB-001",
        "PERF-001", "CUT-001", "CUT-002", "CUT-003", "DOC-001",
        "WEBREL-002",
    ),
    "r3": (
        "DROP-001", "DROP-002", "DROP-003", "DROP-004", "DROP-005",
        "SOAK-001", "ROB-001", "PERF-002", "INST-001", "SUP-001",
        "WEBREL-003",
    ),
    "r4": (
        "RC-001", "RC-002", "DOC-002", "SUP-002", "REL-004",
        "WEBREL-004",
    ),
}
ROADMAP_WORK_ITEMS = tuple(
    work_item
    for phase_items in ROADMAP_PHASE_WORK_ITEMS.values()
    for work_item in phase_items
)
WORK_ITEM_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
SHA = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
WORK_ITEM_FIELDS = {
    "id", "owner", "dependencies", "state", "input_sha", "owned_files",
    "acceptance_tests", "review", "rollback",
}


class MigrationWorkLedgerError(RuntimeError):
    """Migration work ledger validation error."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MigrationWorkLedgerError(message)


def _mapping(value: Any, path: str) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{path} must be an object")
    return value


def _non_empty_string(value: Any, path: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), f"{path} must be a non-empty string")
    return value


def _string_list(value: Any, path: str, *, allow_empty: bool = True) -> list[str]:
    _require(isinstance(value, list), f"{path} must be a list")
    if not allow_empty:
        _require(bool(value), f"{path} must not be empty")
    for index, item in enumerate(value):
        _non_empty_string(item, f"{path}[{index}]")
    _require(len(value) == len(set(value)), f"{path} must not contain duplicates")
    return value


def _validate_roadmap_coverage(value: Any) -> tuple[set[str], set[str]]:
    coverage = _mapping(value, "roadmap_coverage")
    expected_fields = {
        "source_label", "source_sha256", "exhaustive_for_source_work_lots",
        "total_required_work_lots", "phases", "supplemental_work_items",
        "status_semantics",
    }
    _require(set(coverage) == expected_fields, "roadmap_coverage fields must match the frozen V1 contract")
    _require(coverage["source_label"] == ROADMAP_SOURCE_LABEL, "roadmap_coverage.source_label does not match the reviewed roadmap")
    _require(coverage["source_sha256"] == ROADMAP_SOURCE_SHA256, "roadmap_coverage.source_sha256 does not match the reviewed roadmap")
    _require(coverage["exhaustive_for_source_work_lots"] is True, "roadmap work-lot coverage must be exhaustive")
    _require(coverage["total_required_work_lots"] == len(ROADMAP_WORK_ITEMS), f"roadmap_coverage.total_required_work_lots must be {len(ROADMAP_WORK_ITEMS)}")
    _non_empty_string(coverage["status_semantics"], "roadmap_coverage.status_semantics")

    phases = _mapping(coverage["phases"], "roadmap_coverage.phases")
    _require(set(phases) == set(ROADMAP_PHASE_WORK_ITEMS), "roadmap_coverage.phases must contain exactly Phase 0 and R1-R4")
    for phase, expected in ROADMAP_PHASE_WORK_ITEMS.items():
        actual = _string_list(phases[phase], f"roadmap_coverage.phases.{phase}", allow_empty=False)
        _require(tuple(actual) == expected, f"roadmap_coverage.phases.{phase} differs from the reviewed roadmap")

    supplemental = coverage["supplemental_work_items"]
    _require(isinstance(supplemental, list), "roadmap_coverage.supplemental_work_items must be a list")
    supplemental_ids: list[str] = []
    for index, raw_entry in enumerate(supplemental):
        path = f"roadmap_coverage.supplemental_work_items[{index}]"
        entry = _mapping(raw_entry, path)
        _require(set(entry) == {"id", "source", "reason"}, f"{path} must contain id, source and reason")
        supplemental_id = _non_empty_string(entry["id"], f"{path}.id")
        _require(WORK_ITEM_ID.fullmatch(supplemental_id) is not None, f"{path}.id is invalid")
        _non_empty_string(entry["source"], f"{path}.source")
        _non_empty_string(entry["reason"], f"{path}.reason")
        supplemental_ids.append(supplemental_id)
    _require(len(supplemental_ids) == len(set(supplemental_ids)), "supplemental work-item ids must be unique")
    _require(not set(supplemental_ids) & set(ROADMAP_WORK_ITEMS), "roadmap work lots must not be classified as supplemental")
    return set(ROADMAP_WORK_ITEMS), set(supplemental_ids)


def _validate_acyclic_dependencies(items: dict[str, dict[str, Any]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(work_item_id: str, trail: tuple[str, ...]) -> None:
        if work_item_id in visiting:
            raise MigrationWorkLedgerError(
                "work-item dependency cycle: " + " -> ".join((*trail, work_item_id))
            )
        if work_item_id in visited:
            return
        visiting.add(work_item_id)
        for dependency in items[work_item_id]["dependencies"]:
            visit(dependency, (*trail, work_item_id))
        visiting.remove(work_item_id)
        visited.add(work_item_id)

    for work_item_id in items:
        visit(work_item_id, ())


def validate_ledger(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MigrationWorkLedgerError(f"cannot read {path}: {exc}") from exc
    try:
        root = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise MigrationWorkLedgerError(f"invalid YAML {path}: {exc}") from exc
    root = _mapping(root, "ledger")
    _require(root.get("schema_version") == LEDGER_SCHEMA_VERSION, f"unsupported schema_version: {root.get('schema_version')!r}")
    _require(root.get("program") == "nirs4all-native-backend-v1", "ledger.program must identify the native-backend V1 program")
    required_ids, supplemental_ids = _validate_roadmap_coverage(root.get("roadmap_coverage"))

    raw_items = root.get("work_items")
    _require(isinstance(raw_items, list) and bool(raw_items), "ledger.work_items must be a non-empty list")
    items: dict[str, dict[str, Any]] = {}
    for index, raw_item in enumerate(raw_items):
        path_prefix = f"work_items[{index}]"
        item = _mapping(raw_item, path_prefix)
        _require(set(item) == WORK_ITEM_FIELDS, f"{path_prefix} fields must match the work-item contract")
        work_item_id = _non_empty_string(item["id"], f"{path_prefix}.id")
        _require(WORK_ITEM_ID.fullmatch(work_item_id) is not None, f"{path_prefix}.id is invalid")
        _require(work_item_id not in items, f"duplicate work-item id: {work_item_id}")
        _non_empty_string(item["owner"], f"{path_prefix}.owner")
        _non_empty_string(item["state"], f"{path_prefix}.state")
        _require(item["state"] != "done", f"{work_item_id}: use evidence-bearing complete or pending/hold state, never ambiguous done")
        input_sha = _non_empty_string(item["input_sha"], f"{path_prefix}.input_sha")
        _require(SHA.fullmatch(input_sha) is not None, f"{work_item_id}: input_sha must be a Git SHA-1 or SHA-256")
        _string_list(item["dependencies"], f"{path_prefix}.dependencies")
        _string_list(item["owned_files"], f"{path_prefix}.owned_files")
        _string_list(item["acceptance_tests"], f"{path_prefix}.acceptance_tests")
        _non_empty_string(item["review"], f"{path_prefix}.review")
        _non_empty_string(item["rollback"], f"{path_prefix}.rollback")
        if item["state"] == "complete":
            _require(bool(item["acceptance_tests"]), f"{work_item_id}: complete state requires acceptance evidence")
            _require(item["review"].strip().lower() != "pending", f"{work_item_id}: complete state requires independent review")
        items[work_item_id] = item

    item_ids = set(items)
    missing = sorted(required_ids - item_ids)
    _require(not missing, f"ledger is missing roadmap work lots: {missing}")
    unexpected = sorted(item_ids - required_ids - supplemental_ids)
    _require(not unexpected, f"unclassified supplemental work items: {unexpected}")
    missing_supplemental = sorted(supplemental_ids - item_ids)
    _require(not missing_supplemental, f"declared supplemental work items are missing records: {missing_supplemental}")
    for work_item_id, item in items.items():
        dangling = sorted(set(item["dependencies"]) - item_ids)
        _require(not dangling, f"{work_item_id}: unknown dependencies: {dangling}")
        _require(work_item_id not in item["dependencies"], f"{work_item_id}: self dependency is forbidden")
    _validate_acyclic_dependencies(items)
    return root


def render_report(ledger: dict[str, Any]) -> dict[str, Any]:
    items = {item["id"]: item for item in ledger["work_items"]}
    return {
        "roadmap_source_sha256": ledger["roadmap_coverage"]["source_sha256"],
        "roadmap_work_lots": len(ROADMAP_WORK_ITEMS),
        "roadmap_work_lots_by_phase": {
            phase: len(work_items)
            for phase, work_items in ROADMAP_PHASE_WORK_ITEMS.items()
        },
        "supplemental_work_lots": len(items) - len(ROADMAP_WORK_ITEMS),
        "states": dict(sorted(Counter(item["state"] for item in items.values()).items())),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("command", choices=("validate", "report"), nargs="?", default="validate")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        ledger = validate_ledger(args.ledger.resolve())
    except MigrationWorkLedgerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.command == "report":
        print(json.dumps(render_report(ledger), sort_keys=True))
    else:
        print(f"validated {args.ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
