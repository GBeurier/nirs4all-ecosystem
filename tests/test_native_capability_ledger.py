from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/contracts/release/native-capability-ledger.v1.json"
SCHEMA = ROOT / "docs/contracts/release/native-capability-ledger/v1.schema.json"
FIXTURES = ROOT / "tests/fixtures/native-capability-ledger"
RELEASE_WORKFLOW = ROOT / ".github/workflows/native-capability-ledger.yml"


def _load_validator() -> ModuleType:
    path = ROOT / "scripts" / "n4a_native_capability_ledger.py"
    spec = importlib.util.spec_from_file_location("n4a_native_capability_ledger", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_ledger() -> dict[str, Any]:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _write_ledger(path: Path, ledger: Any) -> None:
    path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


def _fixture(name: str) -> dict[str, Any]:
    fixture = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    assert fixture["base"] == "docs/contracts/release/native-capability-ledger.v1.json"
    ledger: dict[str, Any] = copy.deepcopy(_read_ledger())
    for operation in fixture["patch"]:
        target: Any = ledger
        for part in operation["path"][:-1]:
            target = target[part]
        key = operation["path"][-1]
        if operation["op"] == "add":
            target[key] = operation["value"]
        elif operation["op"] == "replace":
            assert key in target
            target[key] = operation["value"]
        else:  # Fixture vocabulary stays deliberately small and reviewable.
            raise AssertionError(operation)
    return ledger


def _selected_workspace_root() -> Path:
    """Return CI's selected-member checkout, or this checkout for structural tests."""
    configured = os.environ.get("N4A_RELEASE_WORKSPACE_ROOT")
    return Path(configured).resolve() if configured else ROOT


def _validate_structural_semantics(validator: ModuleType, path: Path) -> dict[str, Any]:
    """Exercise isolated ledger semantics; never use this helper as the release gate.

    Structural mutation tests need to alter the ledger while retaining the checked-in
    release inputs.  They deliberately stub only the selected-workspace comparison.
    The workflow's CLI command and the integration test below exercise the real,
    non-bypassable release-lock validation against N4A_RELEASE_WORKSPACE_ROOT.
    """
    original = validator._validate_release_lock
    validator._validate_release_lock = lambda *_args: None
    try:
        return validator.validate_ledger(path, workspace_root=_selected_workspace_root())
    finally:
        validator._validate_release_lock = original


def test_native_capability_ledger_validates_baseline_and_release_inputs() -> None:
    validator = _load_validator()

    ledger = _validate_structural_semantics(validator, LEDGER)

    assert ledger["scope"]["exhaustive"] is False
    assert ledger["release_context"]["release_train"] == "2026.07-refactor"
    assert {entry["id"] for entry in ledger["capabilities"]} >= set(validator.PORTABLE_CONTROLLER_KINDS)
    assert {entry["kind"] for entry in ledger["capabilities"]} >= {"api", "model", "operator", "format"}


def test_schema_is_json_schema_for_the_contract_core() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["schema_version"]["const"] == "n4a.native-capability-ledger/v1"
    assert schema["additionalProperties"] is False
    assert schema["$defs"]["extensions"]["additionalProperties"] == {"type": "object"}
    assert schema["$defs"]["preflight"]["additionalProperties"] is False


def test_schema_validates_the_baseline() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator.check_schema(json.loads(SCHEMA.read_text(encoding="utf-8")))
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(_read_ledger())


def test_schema_and_runtime_validator_close_preflight_and_runtime_assertions(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    validator = _load_validator()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    ledger = _read_ledger()
    ledger["capabilities"][0]["preflight"]["unreviewed"] = True
    ledger["capabilities"][0]["runtime_assertions"][0]["availability"] = "runs-maybe"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(ledger)
    path = tmp_path / "ledger.json"
    _write_ledger(path, ledger)
    with pytest.raises(validator.CapabilityLedgerError):
        _validate_structural_semantics(validator, path)


def test_positive_fixture_validates_and_keeps_the_baseline_non_artificial(tmp_path: Path) -> None:
    validator = _load_validator()
    path = tmp_path / "ledger.json"
    _write_ledger(path, _fixture("positive-v1-extension.json"))

    _validate_structural_semantics(validator, path)


@pytest.mark.parametrize(
    ("fixture_name", "message"),
    [
        ("negative-unknown-core-field.json", "unsupported fields"),
        ("negative-stale-manifest-digest.json", "digest does not match"),
    ],
)
def test_negative_fixtures_fail_closed(tmp_path: Path, fixture_name: str, message: str) -> None:
    validator = _load_validator()
    path = tmp_path / "ledger.json"
    _write_ledger(path, _fixture(fixture_name))

    with pytest.raises(validator.CapabilityLedgerError, match=message):
        _validate_structural_semantics(validator, path)


def test_v1_and_current_readers_interoperate_on_additive_extensions(tmp_path: Path) -> None:
    validator = _load_validator()
    baseline = _read_ledger()
    extension_fixture = _fixture("reader-v1-additive-extension.json")
    path = tmp_path / "ledger.json"
    _write_ledger(path, extension_fixture)

    _validate_structural_semantics(validator, path)
    assert validator.read_v1_compatibility_view(extension_fixture) == validator.read_v1_compatibility_view(baseline)


@pytest.mark.parametrize(
    ("capability_id", "installed_plugins", "expected"),
    [
        ("model.pls_regression", (), {"decision": "allow_native", "capability_id": "model.pls_regression"}),
    ],
)
def test_native_and_installed_plugin_dispositions_from_positive_fixture(capability_id: str, installed_plugins: tuple[str, ...], expected: dict[str, str]) -> None:
    validator = _load_validator()
    ledger = _fixture("positive-v1-extension.json")

    assert validator.resolve_capability(ledger, capability_id, runtime="python", installed_plugins=installed_plugins) == expected


@pytest.mark.parametrize(
    ("capability_id", "installed_plugins", "code"),
    [
        ("missing.capability", (), "unknown"),
        ("nirs4all.python.oracle.legacy-backend", (), "refused"),
        ("format.nirs4all-core.lazy-upstream", (), "unknown"),
    ],
)
def test_strict_profile_exposes_all_typed_refusals_from_fixture(capability_id: str, installed_plugins: tuple[str, ...], code: str) -> None:
    validator = _load_validator()

    with pytest.raises(validator.CapabilityLedgerError) as raised:
        validator.resolve_capability(_fixture("positive-v1-extension.json"), capability_id, runtime="legacy-python" if capability_id.endswith("legacy-backend") else "python", installed_plugins=installed_plugins)

    assert raised.value.code == code


@pytest.mark.parametrize("invalid", [[], {}, None, False])
def test_resolver_rejects_non_string_capability_ids_with_capability_ledger_error(invalid: object) -> None:
    validator = _load_validator()

    with pytest.raises(validator.CapabilityLedgerError):
        validator.resolve_capability(_fixture("positive-v1-extension.json"), invalid, runtime="python")


def test_native_capability_ledger_rejects_duplicate_ids(tmp_path: Path) -> None:
    validator = _load_validator()
    ledger = _read_ledger()
    ledger["capabilities"].append(copy.deepcopy(ledger["capabilities"][0]))
    path = tmp_path / "ledger.json"
    _write_ledger(path, ledger)

    with pytest.raises(validator.CapabilityLedgerError, match="duplicate capability id"):
        _validate_structural_semantics(validator, path)


def test_native_pls_claim_requires_the_proven_portable_alias_crosswalk(tmp_path: Path) -> None:
    validator = _load_validator()
    ledger = _read_ledger()
    pls = next(entry for entry in ledger["capabilities"] if entry["id"] == "model.pls_regression")
    pls["aliases"] = ["sklearn.cross_decomposition.NotPLS"]
    path = tmp_path / "ledger.json"
    _write_ledger(path, ledger)

    with pytest.raises(validator.CapabilityLedgerError, match="portable PLS aliases"):
        _validate_structural_semantics(validator, path)


def test_native_capability_ledger_rejects_unbounded_entry_list(tmp_path: Path) -> None:
    validator = _load_validator()
    validator.MAX_LEDGER_BYTES = 1024 * 1024
    ledger = _read_ledger()
    template = copy.deepcopy(ledger["capabilities"][0])
    ledger["capabilities"] = [
        {**copy.deepcopy(template), "id": f"test.capability.{index}"}
        for index in range(validator.MAX_CAPABILITIES + 1)
    ]
    path = tmp_path / "ledger.json"
    _write_ledger(path, ledger)

    with pytest.raises(validator.CapabilityLedgerError, match="exceeds bounded maximum"):
        _validate_structural_semantics(validator, path)


@pytest.mark.parametrize("invalid_document", [[], None, False, "not an object"])
def test_validator_rejects_non_object_documents(tmp_path: Path, invalid_document: object) -> None:
    validator = _load_validator()
    path = tmp_path / "ledger.json"
    _write_ledger(path, invalid_document)

    with pytest.raises(validator.CapabilityLedgerError, match="ledger must be an object"):
        validator.validate_ledger(path, workspace_root=ROOT)


def test_release_surface_never_authorizes_runtime_and_metadata_never_executes() -> None:
    validator = _load_validator()
    ledger = _read_ledger()
    with pytest.raises(validator.CapabilityLedgerError, match="executable assertion"):
        validator.resolve_capability(ledger, "dag-ml.prediction-aggregation", runtime="rust", surface_id="nirs4all.rust.aggregate")
    with pytest.raises(validator.CapabilityLedgerError, match="executable assertion"):
        validator.resolve_capability(ledger, "format.nirs4all-core.lazy-upstream", runtime="python", surface_id="nirs4all.python.core")
    assert validator.resolve_capability(ledger, "dag-ml.prediction-aggregation", runtime="native") == {"decision": "allow_native", "capability_id": "dag-ml.prediction-aggregation"}


def test_adr22_retention_profile_allows_legacy_without_calling_it_native() -> None:
    validator = _load_validator()
    ledger = _read_ledger()
    assert validator.resolve_capability(ledger, "nirs4all.python.oracle.legacy-backend", profile="rollback-capable", runtime="legacy-python") == {"decision": "allow_legacy_retention", "capability_id": "nirs4all.python.oracle.legacy-backend"}


@pytest.mark.parametrize(
    ("mutate", "code"),
    [
        (lambda payload: payload.pop("rollback_profile"), "compatibility_missing_field"),
        (lambda payload: payload.__setitem__("unreviewed", True), "compatibility_unknown_field"),
        (lambda payload: payload.__setitem__("capabilities", {}), "compatibility_type"),
    ],
)
def test_v1_compatibility_reader_refuses_missing_unknown_and_wrongly_typed_core(
    mutate: Any, code: str
) -> None:
    validator = _load_validator()
    payload = _read_ledger()
    mutate(payload)

    with pytest.raises(validator.CapabilityLedgerError) as raised:
        validator.read_v1_compatibility_view(payload)

    assert raised.value.code == code


@pytest.mark.parametrize(
    "fixture_name",
    ["negative-duplicate-core-key.json", "negative-nan-extension.json"],
)
def test_strict_json_parser_rejects_ambiguous_or_non_finite_values_for_all_inputs(
    tmp_path: Path, fixture_name: str
) -> None:
    validator = _load_validator()
    path = tmp_path / "input.json"
    path.write_bytes((FIXTURES / fixture_name).read_bytes())

    with pytest.raises(validator.CapabilityLedgerError) as ledger_error:
        validator.validate_ledger(path, workspace_root=ROOT)
    assert ledger_error.value.code == "invalid_json"

    with pytest.raises(validator.CapabilityLedgerError) as release_input_error:
        validator._load_json(path, "release input")
    assert release_input_error.value.code == "invalid_json"


def test_v1_compatibility_reader_requires_the_exact_v1_schema_version() -> None:
    validator = _load_validator()

    with pytest.raises(validator.CapabilityLedgerError) as raised:
        validator.read_v1_compatibility_view(_fixture("negative-v1-schema-version.json"))

    assert raised.value.code == "compatibility_schema_version"


def test_v1_compatibility_reader_closes_nested_owner_core_fields() -> None:
    validator = _load_validator()

    with pytest.raises(validator.CapabilityLedgerError) as raised:
        validator.read_v1_compatibility_view(_fixture("negative-owner-unreviewed.json"))

    assert raised.value.code == "compatibility_unknown_field"
    assert "owner" in str(raised.value)


def test_v1_compatibility_reader_closes_required_gates_to_the_v1_release_vocabulary() -> None:
    validator = _load_validator()
    payload = _read_ledger()
    payload["capabilities"][0]["required_gates"]["unreviewed.core"] = ["unreviewed_gate"]

    with pytest.raises(validator.CapabilityLedgerError) as raised:
        validator.read_v1_compatibility_view(payload)

    assert raised.value.code == "compatibility_unknown_field"
    assert "required_gates" in str(raised.value)


def test_schema_closes_required_gates_to_the_v1_release_vocabulary() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = _read_ledger()
    payload["capabilities"][0]["required_gates"]["unreviewed.core"] = ["unreviewed_gate"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_release_ci_gate_validates_only_a_lock_pinned_selected_workspace() -> None:
    workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")

    assert workflow.count('- ".gitmodules"') == 2
    assert workflow.count('- "nirs4all"') == 2
    assert "checkout-members" in workflow
    assert "--output \"$N4A_RELEASE_WORKSPACE_ROOT\"" in workflow
    assert workflow.count("--workspace-root \"$N4A_RELEASE_WORKSPACE_ROOT\"") == 2
    assert "scripts/n4a_native_capability_ledger.py" in workflow
    assert "tests/test_release_lock.py tests/test_native_capability_ledger.py" in workflow
    assert "--workspace-root \"$GITHUB_WORKSPACE\"" not in workflow
    assert "git submodule update --init --checkout nirs4all" in workflow
    assert 'git -C nirs4all fetch --depth=1 origin "$oracle_commit"' in workflow
    assert 'git -C nirs4all checkout --detach "$oracle_commit"' in workflow
    assert 'test "$oracle_head" = "$oracle_commit"' in workflow
    assert "N4A_RELEASE_WORKSPACE_ROOT: ${{ runner.temp }}/n4a-selected-release-members" in workflow


def test_outside_lock_oracle_ledger_commit_is_immutable() -> None:
    """The current aggregate pin may move, but evidence must select one exact commit."""
    ledger = _read_ledger()
    commits = {
        evidence["commit"]
        for capability in ledger["capabilities"]
        for evidence in capability["evidence"]
        if evidence.get("outside_lock_surface_id") == "nirs4all.python.oracle"
    }
    assert len(commits) == 1
    [commit] = commits
    assert len(commit) == 40
    assert all(character in "0123456789abcdef" for character in commit)


def test_selected_workspace_integration_uses_the_real_release_lock_gate() -> None:
    """CI supplies a lock-pinned checkout; local structural runs do not pretend to."""
    configured = os.environ.get("N4A_RELEASE_WORKSPACE_ROOT")
    if not configured:
        pytest.skip("requires CI's lock-pinned selected-member workspace")

    validator = _load_validator()
    ledger = validator.validate_ledger(LEDGER, workspace_root=Path(configured).resolve())
    assert ledger["release_context"]["release_train"] == "2026.07-refactor"


@pytest.mark.parametrize(
    ("capability_id", "expected"),
    [
        ("dag-ml.prediction-aggregation", "baseline must declare native prediction aggregation"),
        ("nirs4all.python.oracle.legacy-backend", "baseline must declare retained legacy backend availability"),
    ],
)
def test_baseline_requires_native_aggregation_and_rollback_retention_entries(
    tmp_path: Path, capability_id: str, expected: str
) -> None:
    validator = _load_validator()
    payload = _read_ledger()
    payload["capabilities"] = [entry for entry in payload["capabilities"] if entry["id"] != capability_id]
    payload["release_surface_crosswalk"] = [row for row in payload["release_surface_crosswalk"] if row["capability_id"] != capability_id]
    path = tmp_path / "ledger.json"
    _write_ledger(path, payload)

    with pytest.raises(validator.CapabilityLedgerError, match=expected):
        _validate_structural_semantics(validator, path)


def test_baseline_requires_crosswalks_for_native_aggregation_and_rollback_retention(
    tmp_path: Path
) -> None:
    validator = _load_validator()
    payload = _read_ledger()
    payload["release_surface_crosswalk"] = [
        row for row in payload["release_surface_crosswalk"]
        if row["capability_id"] != "nirs4all.python.oracle.legacy-backend"
    ]
    path = tmp_path / "ledger.json"
    _write_ledger(path, payload)

    with pytest.raises(validator.CapabilityLedgerError, match="baseline must crosswalk retained legacy backend availability"):
        _validate_structural_semantics(validator, path)


def test_legacy_retention_evidence_is_pinned_to_the_outside_lock_python_oracle(
    tmp_path: Path
) -> None:
    validator = _load_validator()
    payload = _read_ledger()
    legacy = next(entry for entry in payload["capabilities"] if entry["id"] == "nirs4all.python.oracle.legacy-backend")
    legacy["evidence"][0]["outside_lock_surface_id"] = "nirs4all.python.core"
    path = tmp_path / "ledger.json"
    _write_ledger(path, payload)

    with pytest.raises(validator.CapabilityLedgerError, match="must remain outside the aggregation lock"):
        _validate_structural_semantics(validator, path)


def test_release_lock_validation_is_the_production_selected_workspace_gate() -> None:
    validator = _load_validator()
    with pytest.raises(validator.CapabilityLedgerError, match="release-lock validation failed"):
        validator.validate_ledger(LEDGER, workspace_root=ROOT)


def test_evidence_is_read_from_tracked_head_not_a_mutable_worktree(tmp_path: Path) -> None:
    validator = _load_validator()
    repo = tmp_path / "selected-member"
    repo.mkdir()
    for command in (
        ["git", "init"],
        ["git", "config", "user.email", "capability-ledger@example.invalid"],
        ["git", "config", "user.name", "Capability Ledger"],
    ):
        subprocess.run(command, cwd=repo, check=True, capture_output=True, text=True)
    source = repo / "evidence.txt"
    source.write_text("locked proof\n", encoding="utf-8")
    subprocess.run(["git", "add", "evidence.txt"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "proof"], cwd=repo, check=True, capture_output=True, text=True)
    source.write_text("mutable worktree replacement\n", encoding="utf-8")

    release_lock = validator._release_lock_module()
    evidence = validator._validate_evidence(
        [{"component_key": "core", "source": "evidence.txt", "claim": "tracked only"}],
        "evidence",
        {"core": {"root": repo, "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()}},
        {"public_v1_surfaces": []},
        ROOT,
        release_lock,
    )

    assert evidence[0]["_head_source"] == "locked proof\n"


@pytest.mark.parametrize("path", [("runtime_assertions", 0, "availability"), ("evidence", 0, "component_key"), ("preflight", "before")])
def test_nested_invalid_values_raise_capability_ledger_error(tmp_path: Path, path: tuple[object, ...]) -> None:
    validator = _load_validator()
    ledger = _read_ledger()
    target: Any = ledger["capabilities"][0]
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = False
    output = tmp_path / "ledger.json"
    _write_ledger(output, ledger)
    with pytest.raises(validator.CapabilityLedgerError):
        _validate_structural_semantics(validator, output)


def test_cli_defaults_ledger_from_its_repository_and_needs_explicit_workspace_root(tmp_path: Path) -> None:
    script = ROOT / "scripts/n4a_native_capability_ledger.py"
    missing = subprocess.run([sys.executable, str(script)], cwd=tmp_path, capture_output=True, text=True)
    assert missing.returncode == 2
    validator = _load_validator()
    args = validator.parse_args(["--workspace-root", str(ROOT), "report"])
    assert args.ledger == LEDGER
