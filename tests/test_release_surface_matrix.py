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
    ]


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

    with pytest.raises(surface_matrix.SurfaceMatrixError, match="is not declared by lock member lite"):
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
