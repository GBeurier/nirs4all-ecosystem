from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "contracts" / "release" / "public-v1-surface-matrix.n4a.json"
MANIFEST = ROOT / "docs" / "contracts" / "release" / "aggregation-manifest.n4a.json"
LOCK = ROOT / "docs" / "contracts" / "release" / "aggregation-lock.n4a.lock.json"


def _load_surface_matrix() -> ModuleType:
    path = ROOT / "scripts" / "n4a_release_surface_matrix.py"
    spec = importlib.util.spec_from_file_location("n4a_release_surface_matrix", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_matrix() -> dict:
    return json.loads(MATRIX.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _surface(matrix: dict, surface_id: str) -> dict:
    for surface in matrix["public_v1_surfaces"]:
        if surface["id"] == surface_id:
            return surface
    raise AssertionError(f"missing fixture surface {surface_id}")


def test_public_v1_surface_matrix_validates_current_contracts() -> None:
    surface_matrix = _load_surface_matrix()

    validated = surface_matrix.validate_surface_matrix(MATRIX, MANIFEST, LOCK)

    assert validated["matrix"]["required_nirs4all_v1_surface_ids"] == [
        "nirs4all.python.oracle",
        "nirs4all.python.core",
        "nirs4all.r.aggregate",
        "nirs4all.javascript_wasm.aggregate",
        "nirs4all.javascript_wasm.methods_scoped",
        "nirs4all.javascript_wasm.datasets_scoped",
        "nirs4all.rust.aggregate",
        "nirs4all.matlab_octave.aggregate",
        "nirs4all.studio.product",
        "nirs4all.ui.package",
        "nirs4all.web.product",
        "nirs4all.providers.contracts",
        "nirs4all.cockpit.product",
        "nirs4all.org.site",
        "nirs4all.tools.migration",
    ]


def test_public_v1_surface_matrix_is_explicitly_non_exhaustive() -> None:
    matrix = _read_matrix()

    assert matrix["scope"]["exhaustive"] is False
    assert "does not prove" in matrix["scope"]["omission_semantics"]


def test_surface_matrix_rejects_a_false_exhaustivity_claim(tmp_path: Path) -> None:
    surface_matrix = _load_surface_matrix()
    matrix = _read_matrix()
    matrix["scope"]["exhaustive"] = True
    matrix_path = tmp_path / "matrix.json"
    _write_json(matrix_path, matrix)

    with pytest.raises(surface_matrix.SurfaceMatrixError, match="exhaustive must be false"):
        surface_matrix.validate_surface_matrix(matrix_path, MANIFEST, LOCK)


def test_public_v1_surface_matrix_requires_r_aggregate_surface(tmp_path: Path) -> None:
    surface_matrix = _load_surface_matrix()
    matrix = _read_matrix()
    matrix["public_v1_surfaces"] = [
        surface
        for surface in matrix["public_v1_surfaces"]
        if surface["id"] != "nirs4all.r.aggregate"
    ]
    matrix_path = tmp_path / "matrix.json"
    _write_json(matrix_path, matrix)

    with pytest.raises(surface_matrix.SurfaceMatrixError, match="required nirs4all V1 surface ids are missing"):
        surface_matrix.validate_surface_matrix(matrix_path, MANIFEST, LOCK)


def test_outside_lock_surface_cannot_point_to_locked_repo(tmp_path: Path) -> None:
    surface_matrix = _load_surface_matrix()
    matrix = _read_matrix()
    _surface(matrix, "nirs4all.python.oracle")["repo_path"] = "nirs4all-core"
    matrix_path = tmp_path / "matrix.json"
    _write_json(matrix_path, matrix)

    with pytest.raises(surface_matrix.SurfaceMatrixError, match="is a lock member"):
        surface_matrix.validate_surface_matrix(matrix_path, MANIFEST, LOCK)


def test_covered_surface_distribution_must_be_declared_by_lock_member(tmp_path: Path) -> None:
    surface_matrix = _load_surface_matrix()
    matrix = copy.deepcopy(_read_matrix())
    _surface(matrix, "nirs4all.javascript_wasm.aggregate")["distribution"] = "not-nirs4all"
    matrix_path = tmp_path / "matrix.json"
    _write_json(matrix_path, matrix)

    with pytest.raises(surface_matrix.SurfaceMatrixError, match="is not declared by lock member core"):
        surface_matrix.validate_surface_matrix(matrix_path, MANIFEST, LOCK)


def test_required_surfaces_include_core_rust_and_matlab_accounting(tmp_path: Path) -> None:
    surface_matrix = _load_surface_matrix()
    matrix = _read_matrix()
    matrix["public_v1_surfaces"] = [
        surface
        for surface in matrix["public_v1_surfaces"]
        if surface["id"] != "nirs4all.rust.aggregate"
    ]
    matrix["required_nirs4all_v1_surface_ids"] = [
        surface_id
        for surface_id in matrix["required_nirs4all_v1_surface_ids"]
        if surface_id != "nirs4all.rust.aggregate"
    ]
    matrix_path = tmp_path / "matrix.json"
    _write_json(matrix_path, matrix)

    with pytest.raises(surface_matrix.SurfaceMatrixError, match="missing rust:nirs4all"):
        surface_matrix.validate_surface_matrix(matrix_path, MANIFEST, LOCK)


def test_public_surface_matrix_accounts_for_web_providers_and_sites() -> None:
    matrix = _read_matrix()
    by_id = {surface["id"]: surface for surface in matrix["public_v1_surfaces"]}

    ui = by_id["nirs4all.ui.package"]
    assert ui["distribution"] == "nirs4all-ui"
    assert ui["ecosystem"] == "javascript_ui"
    assert ui["repo_path"] == "nirs4all-ui"
    assert ui["lock_relation"] == "outside_aggregation_lock"
    assert ui["required_for_nirs4all_v1"] is True
    assert "pure TypeScript view-model helpers" in ui["proof_boundary"]
    assert "not a backend" in ui["proof_boundary"]

    web = by_id["nirs4all.web.product"]
    assert web["required_for_nirs4all_v1"] is True
    assert "browser" in web["display_name"]
    assert "client-side-only" in web["proof_boundary"]
    assert "Python server" in web["proof_boundary"]

    quality = by_id["nirs4all.quality.product"]
    assert quality["distribution"] == "nirs4all-quality"
    assert quality["repo_path"] == "nirs4all-quality"
    assert quality["lock_relation"] == "outside_aggregation_lock"
    assert quality["required_for_nirs4all_v1"] is False
    assert "client-side-only" in quality["proof_boundary"]
    assert "cockpit links and monitors" in quality["proof_boundary"]

    providers = by_id["nirs4all.providers.contracts"]
    assert providers["distribution"] == "nirs4all-providers"
    assert providers["lock_relation"] == "outside_aggregation_lock"
    assert providers["required_for_nirs4all_v1"] is True
    assert "neutral schemas" in providers["proof_boundary"]
    assert "R/WASM/native" in providers["proof_boundary"]

    cockpit = by_id["nirs4all.cockpit.product"]
    assert cockpit["distribution"] == "nirs4all-cockpit"
    assert cockpit["required_for_nirs4all_v1"] is True

    org = by_id["nirs4all.org.site"]
    assert org["distribution"] == "nirs4all-org"
    assert org["repo_path"] == "nirs4all-org"
    assert org["lock_relation"] == "outside_aggregation_lock"
    assert org["required_for_nirs4all_v1"] is True

    studio = by_id["nirs4all.studio.product"]
    assert studio["required_for_nirs4all_v1"] is True
    assert studio["release_batch_role"] == "required_product_held"

    tools = by_id["nirs4all.tools.migration"]
    assert tools["required_for_nirs4all_v1"] is True
    assert tools["repo_path"] == "nirs4all-tools"


@pytest.mark.parametrize(
    "surface_id",
    [
        "nirs4all.studio.product",
        "nirs4all.ui.package",
        "nirs4all.web.product",
        "nirs4all.tools.migration",
        "nirs4all.providers.contracts",
        "nirs4all.cockpit.product",
        "nirs4all.org.site",
    ],
)
def test_roadmap_v1_surface_cannot_be_removed_from_required_scope(
    tmp_path: Path, surface_id: str
) -> None:
    surface_matrix = _load_surface_matrix()
    matrix = _read_matrix()
    matrix["required_nirs4all_v1_surface_ids"].remove(surface_id)
    _surface(matrix, surface_id)["required_for_nirs4all_v1"] = False
    matrix_path = tmp_path / "matrix.json"
    _write_json(matrix_path, matrix)

    with pytest.raises(surface_matrix.SurfaceMatrixError, match="roadmap-required V1 surfaces"):
        surface_matrix.validate_surface_matrix(matrix_path, MANIFEST, LOCK)


def test_release_batch_semantics_keep_oracle_and_shipped_surfaces_distinct() -> None:
    matrix = _read_matrix()
    semantics = matrix["release_batch_semantics"]
    by_id = {surface["id"]: surface for surface in matrix["public_v1_surfaces"]}

    oracle = by_id["nirs4all.python.oracle"]
    assert oracle["required_for_nirs4all_v1"] is True
    assert oracle["release_batch_role"] == "required_parity_oracle_held"
    assert oracle["lock_relation"] == "outside_aggregation_lock"
    assert "nirs4all.python.oracle" in semantics["held_surface_ids"]

    studio = by_id["nirs4all.studio.product"]
    assert studio["required_for_nirs4all_v1"] is True
    assert studio["release_batch_role"] == "required_product_held"
    assert "nirs4all.studio.product" in semantics["held_surface_ids"]

    assert semantics["custom_app_host_surface_ids"] == [
        "nirs4all.javascript_wasm.aggregate",
        "nirs4all.ui.package",
        "nirs4all.web.product",
        "nirs4all.quality.product",
    ]
    assert (
        by_id["nirs4all.javascript_wasm.aggregate"]["release_batch_role"]
        == "custom_app_host_runtime"
    )
    assert by_id["nirs4all.ui.package"]["release_batch_role"] == "custom_app_host_ui"
    assert by_id["nirs4all.web.product"]["release_batch_role"] == "custom_app_host_product"
    assert "bare Python/PyPI nirs4all" in semantics["python_name_policy"]
    assert "nirs4all-core" in semantics["python_name_policy"]


def test_release_batch_semantics_reject_oracle_as_shipped_product(tmp_path: Path) -> None:
    surface_matrix = _load_surface_matrix()
    matrix = _read_matrix()
    _surface(matrix, "nirs4all.python.oracle")["release_batch_role"] = "portable_aggregate_python"
    matrix_path = tmp_path / "matrix.json"
    _write_json(matrix_path, matrix)

    with pytest.raises(surface_matrix.SurfaceMatrixError, match="required_parity_oracle_held"):
        surface_matrix.validate_surface_matrix(matrix_path, MANIFEST, LOCK)


def test_release_batch_semantics_require_custom_host_path(tmp_path: Path) -> None:
    surface_matrix = _load_surface_matrix()
    matrix = _read_matrix()
    matrix["release_batch_semantics"]["custom_app_host_surface_ids"].remove("nirs4all.ui.package")
    matrix_path = tmp_path / "matrix.json"
    _write_json(matrix_path, matrix)

    with pytest.raises(surface_matrix.SurfaceMatrixError, match="custom app host surface missing"):
        surface_matrix.validate_surface_matrix(matrix_path, MANIFEST, LOCK)
